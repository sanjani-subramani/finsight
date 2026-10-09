"""TwinService — the public face of app.modules.twin.

Nothing outside this module should call anything else in here: every
other module (routers, decision, risk, ...) that needs Digital Twin state
goes through TwinService, never straight at fold.py / snapshot.py /
obligations.py directly.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import FinancialStateSnapshot
from app.contracts.events import Goal as GoalContract
from app.contracts.events import Obligation as ObligationContract
from app.models.tables import FinancialEvent
from app.models.tables import Goal as GoalRow
from app.models.tables import IncomeSource
from app.models.tables import Obligation as ObligationRow
from app.models.tables import RecurringCandidate as RecurringCandidateRow
from app.modules.confidence.counterparty import CounterpartyResolver
from app.modules.twin import fold, snapshot
from app.modules.twin.obligations import detect_recurring, get_active_obligations
from app.modules.twin.snapshot import build_snapshot, invalidate_snapshot
from app.platform.logging import get_logger

logger = get_logger(__name__)


class TwinService:
    async def get_base_snapshot(self, session: AsyncSession, user_id: UUID) -> FinancialStateSnapshot:
        """The snapshot with only Twin-owned fields populated — cash,
        obligations, goals, income forecast, weather, confidence — and
        NONE of the simulation-derived ones (shortfall_risks,
        time_to_danger_days, a real safe_to_spend). app.modules.simulation
        uses exactly this to build its own SimulationInput, so that
        get_snapshot()'s enrichment step below (which runs a simulation)
        can never recursively trigger another simulation run.
        """
        return await build_snapshot(session, user_id, use_cache=True)

    async def get_snapshot(self, session: AsyncSession, user_id: UUID) -> FinancialStateSnapshot:
        base = await self.get_base_snapshot(session, user_id)

        # Deferred import: app.modules.simulation itself depends on
        # get_base_snapshot() above to build its own input, so importing
        # SimulationService at module load time would create a genuine
        # circular import between the twin and simulation modules.
        # Deferring to call time breaks the cycle safely — by the time
        # this line actually runs, both modules are fully loaded.
        from app.modules.simulation.service import SimulationService

        try:
            outcome = await SimulationService().run(session, user_id)
        except Exception:
            # The simulation that enriches the snapshot must never be
            # able to take the snapshot itself down — a user should still
            # see their cash/obligations/weather even on a day the Monte
            # Carlo engine has a problem.
            logger.warning("snapshot_simulation_enrichment_failed", user_id=str(user_id), exc_info=True)
            return base

        return base.model_copy(
            update={
                "shortfall_risks": outcome.shortfall_risks,
                "time_to_danger_days": outcome.result.time_to_danger_days,
                "safe_to_spend": outcome.safe_to_spend.amount,
            }
        )

    async def get_pending_income(self, session: AsyncSession, user_id: UUID) -> dict[str, dict[str, Any]]:
        """Read-only view of the fold's currently pending income entries
        (reflects any real INCOME_DELAYED event already folded in) —
        exposed for app.modules.risk's income_delayed rule, which needs
        to compare this against the statistical baseline arrival. Uses
        the persisted fold row directly (O(1)) rather than a full replay.
        """
        row = await fold._load_twin_state_row(session, user_id)
        if row is None:
            return {}
        accumulator = fold._accumulator_from_row(row)
        return accumulator.pending_income

    async def on_event_ingested(self, session: AsyncSession, event: FinancialEvent) -> None:
        """Wired into the Step 3/4 ingestion pipeline so the Twin updates
        automatically as events arrive — an incremental fold step, then
        an immediate cache invalidation (see snapshot.invalidate_snapshot
        for why this must never be lazy or batched)."""
        await fold.incremental_update(session, event.user_id, event)
        await invalidate_snapshot(event.user_id)

    async def rebuild(self, session: AsyncSession, user_id: UUID) -> FinancialStateSnapshot:
        state = await fold.rebuild_state(session, user_id)
        await fold._persist_fold_columns(session, user_id, state)
        await invalidate_snapshot(user_id)
        return await self.get_snapshot(session, user_id)

    async def list_obligations(
        self, session: AsyncSession, user_id: UUID, horizon_days: int = 90
    ) -> list[ObligationContract]:
        return await get_active_obligations(session, user_id, horizon_days=horizon_days)

    # -- Obligations ---------------------------------------------------

    async def add_obligation(
        self,
        session: AsyncSession,
        user_id: UUID,
        *,
        label: str,
        amount: Decimal,
        due_date: date,
        category: str | None = None,
        is_fixed: bool = True,
        is_recurring: bool = False,
        recurrence_rule: str | None = None,
        data_source: str = "manual",
        confidence_score: float = 1.0,
    ) -> ObligationRow:
        row = ObligationRow(
            user_id=user_id,
            label=label,
            amount=amount,
            due_date=due_date,
            category=category,
            is_fixed=is_fixed,
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule,
            is_paid=False,
            data_source=data_source,
            confidence_score=confidence_score,
        )
        session.add(row)
        await session.flush()
        await invalidate_snapshot(user_id)
        return row

    async def update_obligation(
        self, session: AsyncSession, user_id: UUID, obligation_id: UUID, **fields: Any
    ) -> ObligationRow | None:
        result = await session.execute(
            select(ObligationRow).where(
                ObligationRow.id == obligation_id, ObligationRow.user_id == user_id
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(row, key):
                setattr(row, key, value)
        await session.flush()
        await invalidate_snapshot(user_id)
        return row

    async def delete_obligation(self, session: AsyncSession, user_id: UUID, obligation_id: UUID) -> bool:
        result = await session.execute(
            select(ObligationRow).where(
                ObligationRow.id == obligation_id, ObligationRow.user_id == user_id
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return False
        row.deleted_at = datetime.now(timezone.utc)  # soft delete — never hard-remove financial records
        await session.flush()
        await invalidate_snapshot(user_id)
        return True

    # -- Goals -----------------------------------------------------------

    async def add_goal(
        self,
        session: AsyncSession,
        user_id: UUID,
        *,
        label: str,
        target_amount: Decimal,
        saved_amount: Decimal = Decimal("0"),
        target_date: date | None = None,
        priority: int = 3,
        is_flexible: bool = True,
    ) -> GoalRow:
        row = GoalRow(
            user_id=user_id,
            label=label,
            target_amount=target_amount,
            saved_amount=saved_amount,
            target_date=target_date,
            priority=priority,
            is_flexible=is_flexible,
        )
        session.add(row)
        await session.flush()
        await invalidate_snapshot(user_id)
        return row

    async def update_goal(
        self, session: AsyncSession, user_id: UUID, goal_id: UUID, **fields: Any
    ) -> GoalRow | None:
        result = await session.execute(
            select(GoalRow).where(GoalRow.id == goal_id, GoalRow.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(row, key):
                setattr(row, key, value)
        await session.flush()
        await invalidate_snapshot(user_id)
        return row

    async def delete_goal(self, session: AsyncSession, user_id: UUID, goal_id: UUID) -> bool:
        result = await session.execute(
            select(GoalRow).where(GoalRow.id == goal_id, GoalRow.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return False
        row.deleted_at = datetime.now(timezone.utc)
        await session.flush()
        await invalidate_snapshot(user_id)
        return True

    async def list_goals(self, session: AsyncSession, user_id: UUID) -> list[GoalContract]:
        return await snapshot._load_goals(session, user_id)

    # -- Income sources ---------------------------------------------------

    async def add_income_source(
        self,
        session: AsyncSession,
        user_id: UUID,
        *,
        label: str,
        counterparty: str | None = None,
        declared_min: Decimal | None = None,
        declared_max: Decimal | None = None,
        declared_frequency_days: int | None = None,
    ) -> IncomeSource:
        row = IncomeSource(
            user_id=user_id,
            label=label,
            counterparty=counterparty,
            declared_min=declared_min,
            declared_max=declared_max,
            declared_frequency_days=declared_frequency_days,
            observation_count=0,
            forecast_mode="declared",
            confidence_score=0.30,
            is_active=True,
        )
        session.add(row)
        await session.flush()
        await invalidate_snapshot(user_id)
        return row

    async def update_income_source(
        self, session: AsyncSession, user_id: UUID, income_source_id: UUID, **fields: Any
    ) -> IncomeSource | None:
        result = await session.execute(
            select(IncomeSource).where(
                IncomeSource.id == income_source_id, IncomeSource.user_id == user_id
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(row, key):
                setattr(row, key, value)
        await session.flush()
        await invalidate_snapshot(user_id)
        return row

    async def list_income_sources(self, session: AsyncSession, user_id: UUID) -> list[IncomeSource]:
        result = await session.execute(
            select(IncomeSource).where(IncomeSource.user_id == user_id, IncomeSource.is_active.is_(True))
        )
        return list(result.scalars())

    # -- Recurring detection ----------------------------------------------

    async def detect_and_store_recurring(
        self, session: AsyncSession, user_id: UUID, resolver: CounterpartyResolver | None = None
    ) -> list[RecurringCandidateRow]:
        candidates = await detect_recurring(session, user_id, resolver=resolver)

        stored: list[RecurringCandidateRow] = []
        for candidate in candidates:
            existing_result = await session.execute(
                select(RecurringCandidateRow).where(
                    RecurringCandidateRow.user_id == user_id,
                    RecurringCandidateRow.counterparty == candidate.counterparty,
                    RecurringCandidateRow.status == "pending",
                )
            )
            row = existing_result.scalar_one_or_none()
            evidence_ids = [str(e) for e in candidate.evidence_event_ids]
            if row is None:
                row = RecurringCandidateRow(
                    user_id=user_id,
                    counterparty=candidate.counterparty,
                    category=candidate.category,
                    suggested_amount=candidate.suggested_amount,
                    interval_days=candidate.interval_days,
                    day_of_month=candidate.day_of_month,
                    confidence=candidate.confidence,
                    detection_method=candidate.detection_method,
                    status="pending",
                    evidence_event_ids=evidence_ids,
                )
                session.add(row)
            else:
                row.suggested_amount = float(candidate.suggested_amount)
                row.confidence = candidate.confidence
                row.evidence_event_ids = evidence_ids
            stored.append(row)

        await session.flush()
        return stored

    async def list_recurring_candidates(
        self, session: AsyncSession, user_id: UUID
    ) -> list[RecurringCandidateRow]:
        result = await session.execute(
            select(RecurringCandidateRow).where(
                RecurringCandidateRow.user_id == user_id, RecurringCandidateRow.status == "pending"
            )
        )
        return list(result.scalars())

    async def confirm_recurring(
        self, session: AsyncSession, user_id: UUID, candidate_id: UUID
    ) -> ObligationRow | None:
        result = await session.execute(
            select(RecurringCandidateRow).where(
                RecurringCandidateRow.id == candidate_id, RecurringCandidateRow.user_id == user_id
            )
        )
        candidate = result.scalar_one_or_none()
        if candidate is None or candidate.status != "pending":
            return None

        today = date.today()
        day = min(candidate.day_of_month or today.day, 28)
        due_date = today.replace(day=day)

        obligation = await self.add_obligation(
            session,
            user_id,
            label=candidate.counterparty,
            amount=Decimal(str(candidate.suggested_amount)),
            due_date=due_date,
            category=candidate.category,
            is_fixed=True,
            is_recurring=True,
            recurrence_rule=f"MONTHLY:{day}",
            data_source="system",
            confidence_score=float(candidate.confidence),
        )
        candidate.status = "confirmed"
        await session.flush()
        return obligation
