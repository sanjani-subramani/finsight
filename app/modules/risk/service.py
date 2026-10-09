"""RiskService — the public face of app.modules.risk.

Orchestrates: get a Twin snapshot + simulation -> evaluate every active
rule -> detect collisions -> score and rank everything -> persist
collisions (and auto-resolve stale ones) -> return one RiskAssessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import FinancialEventType, FinancialStateSnapshot
from app.models.tables import CollisionRecord as CollisionRecordRow
from app.models.tables import FinancialEvent, IncomeSource
from app.modules.risk.collision import Collision, detect_collisions
from app.modules.risk.rules import RuleContext, RuleFinding, evaluate_all_rules
from app.modules.risk.scoring import RiskScore, compute_risk_score
from app.modules.simulation.engine import SimulationResult
from app.platform.logging import get_logger
from app.platform.timeutils import as_aware_utc

logger = get_logger(__name__)

RECENT_EVENTS_LOOKBACK_DAYS = 14
DISCRETIONARY_LOOKBACK_DAYS = 60
EXPENSE_PERCENTILE_LOOKBACK_DAYS = 90
OBLIGATION_CATEGORIES = {"rent", "emi"}
USER_DISMISSAL_REASON_PREFIX = "user_dismissed"
AUTO_RESOLUTION_REASON = "conditions no longer hold"


@dataclass(frozen=True)
class RiskAssessment:
    snapshot_id: UUID
    simulation_run_id: UUID
    findings: list[RuleFinding]
    collisions: list[Collision]
    overall_risk_score: float
    top_collision: Collision | None
    assessed_at: datetime
    finding_scores: dict[str, RiskScore] = field(default_factory=dict)
    # Keyed by collision_id, mirroring finding_scores — exposed so
    # app.modules.decision (Step 8) can build a GateInput from whichever
    # item (finding or collision) actually drove overall_risk_score,
    # without recomputing scores itself or reaching into this module's
    # internals.
    collision_scores: dict[UUID, RiskScore] = field(default_factory=dict)
    # The full snapshot, not just its id — app.modules.decision (Step 8)
    # needs real figures (cash_available, obligations, ...) to build a
    # trace and compose headline/body text, and re-fetching it would mean
    # a second, redundant Twin query for every decide() call.
    snapshot: FinancialStateSnapshot | None = None
    # The raw simulation result, not just probabilities baked into scores
    # — app.modules.decision.arbitration (Step 11) needs it to run its own
    # verification re-simulations (same seed, same scenario count) without
    # a second, redundant SimulationService.run() call.
    sim_result: SimulationResult | None = None


class RiskService:
    async def assess(self, session: AsyncSession, user_id: UUID) -> RiskAssessment:
        # Deferred imports: both twin and simulation sit "below" risk in
        # the dependency chain, but simulation.service.SimulationService
        # already imports TwinService lazily too — importing either at
        # module load time here is safe (no cycle back to this module),
        # kept deferred anyway for consistency with that established
        # pattern.
        from app.modules.simulation.service import SimulationService
        from app.modules.twin.service import TwinService

        snapshot = await TwinService().get_base_snapshot(session, user_id)
        sim_outcome = await SimulationService().run(session, user_id)
        sim_result = sim_outcome.result

        recent_events = await self._load_recent_events(session, user_id)
        historical_averages = await self._build_context(session, user_id, snapshot)

        ctx = RuleContext(
            snapshot=snapshot,
            simulation_result=sim_result,
            recent_events=recent_events,
            historical_averages=historical_averages,
        )
        findings = evaluate_all_rules(ctx)

        collisions = await detect_collisions(session, user_id, snapshot, sim_result, findings)

        monthly_obligations = snapshot.total_fixed_obligations
        if monthly_obligations <= 0:
            monthly_obligations = Decimal("1")  # avoid division by zero in magnitude normalization

        horizon = max(sim_result.shortfall_probability_by_horizon)
        probability = sim_result.shortfall_probability_by_horizon[horizon]

        finding_scores: dict[str, RiskScore] = {}
        for finding in findings:
            amount_at_risk = self._amount_at_risk(finding, snapshot)
            urgency_days = self._urgency_days(finding)
            finding_scores[finding.rule_id] = compute_risk_score(
                probability=probability,
                severity=finding.severity,
                urgency=urgency_days,
                confidence=snapshot.state_confidence,
                amount_at_risk=amount_at_risk,
                monthly_obligations=monthly_obligations,
            )

        collision_scores: dict[UUID, RiskScore] = {
            collision.collision_id: compute_risk_score(
                probability=collision.joint_probability,
                severity=collision.severity,
                urgency=collision.urgency,
                confidence=snapshot.state_confidence,
                amount_at_risk=monthly_obligations,
                monthly_obligations=monthly_obligations,
            )
            for collision in collisions
        }

        overall_risk_score = max(
            [s.score for s in finding_scores.values()] + [s.score for s in collision_scores.values()], default=0.0
        )
        top_collision = max(collisions, key=lambda c: c.joint_probability, default=None)

        await self._persist_new_collisions(session, user_id, collisions, sim_outcome.run_id)
        await self._auto_resolve_stale_collisions(session, user_id, collisions)

        return RiskAssessment(
            snapshot_id=snapshot.snapshot_id,
            simulation_run_id=sim_outcome.run_id,
            findings=findings,
            collisions=collisions,
            overall_risk_score=overall_risk_score,
            top_collision=top_collision,
            assessed_at=datetime.now(timezone.utc),
            finding_scores=finding_scores,
            collision_scores=collision_scores,
            snapshot=snapshot,
            sim_result=sim_result,
        )

    async def get_active_collisions(self, session: AsyncSession, user_id: UUID) -> list[CollisionRecordRow]:
        result = await session.execute(
            select(CollisionRecordRow)
            .where(CollisionRecordRow.user_id == user_id, CollisionRecordRow.resolved_at.is_(None))
            .order_by(CollisionRecordRow.detected_at.desc())
        )
        return list(result.scalars())

    async def get_collision(
        self, session: AsyncSession, user_id: UUID, collision_id: UUID
    ) -> CollisionRecordRow | None:
        result = await session.execute(
            select(CollisionRecordRow).where(
                CollisionRecordRow.id == collision_id, CollisionRecordRow.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def resolve_collision(
        self, session: AsyncSession, user_id: UUID, collision_id: UUID, reason: str
    ) -> CollisionRecordRow | None:
        row = await self.get_collision(session, user_id, collision_id)
        if row is None or row.resolved_at is not None:
            return None
        row.resolved_at = datetime.now(timezone.utc)
        row.resolution_reason = f"{USER_DISMISSAL_REASON_PREFIX}: {reason}"
        await session.flush()
        return row

    # -- context building --------------------------------------------------

    async def _load_recent_events(self, session: AsyncSession, user_id: UUID) -> list[FinancialEvent]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_EVENTS_LOOKBACK_DAYS)
        result = await session.execute(
            select(FinancialEvent).where(
                FinancialEvent.user_id == user_id,
                FinancialEvent.occurred_at >= cutoff,
                FinancialEvent.duplicate_of.is_(None),
                FinancialEvent.superseded_by.is_(None),
            )
        )
        return list(result.scalars())

    async def _build_context(
        self, session: AsyncSession, user_id: UUID, snapshot: FinancialStateSnapshot
    ) -> dict[str, Any]:
        today = date.today()
        cutoff_60 = datetime.now(timezone.utc) - timedelta(days=DISCRETIONARY_LOOKBACK_DAYS)
        cutoff_90 = datetime.now(timezone.utc) - timedelta(days=EXPENSE_PERCENTILE_LOOKBACK_DAYS)
        cutoff_7 = datetime.now(timezone.utc) - timedelta(days=7)

        result = await session.execute(
            select(FinancialEvent).where(
                FinancialEvent.user_id == user_id,
                FinancialEvent.event_type == FinancialEventType.expense.value,
                FinancialEvent.occurred_at >= cutoff_90,
                FinancialEvent.duplicate_of.is_(None),
                FinancialEvent.superseded_by.is_(None),
            )
        )
        events = list(result.scalars())
        # Exclude anything already accounted for as an obligation payment
        # — same reasoning as simulation.builder's discretionary
        # estimate: counting rent/EMI again here would double-count the
        # same rupee as both "an obligation" and "discretionary burn."
        discretionary = [
            e for e in events if (e.category or "").lower() not in OBLIGATION_CATEGORIES and e.amount is not None
        ]

        daily_totals: dict[date, float] = {}
        for e in discretionary:
            if e.amount is None or as_aware_utc(e.occurred_at) < cutoff_60:
                continue
            day = as_aware_utc(e.occurred_at).date()
            daily_totals[day] = daily_totals.get(day, 0.0) + float(e.amount)

        discretionary_60d_daily_mean = float(np.mean(list(daily_totals.values()))) if daily_totals else None
        discretionary_7d_total = sum(
            v
            for d, v in daily_totals.items()
            if datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc) >= cutoff_7
        )

        all_amounts = [float(e.amount) for e in discretionary if e.amount is not None]
        expense_p95 = float(np.percentile(all_amounts, 95)) if all_amounts else None

        income_sources = await self._income_source_timing(session, user_id, today)

        return {
            "discretionary_7d_total": discretionary_7d_total,
            "discretionary_60d_daily_mean": discretionary_60d_daily_mean,
            "expense_p95": expense_p95,
            "income_sources": income_sources,
        }

    async def _income_source_timing(
        self, session: AsyncSession, user_id: UUID, today: date
    ) -> list[dict[str, Any]]:
        from app.modules.twin.service import TwinService

        result = await session.execute(
            select(IncomeSource).where(IncomeSource.user_id == user_id, IncomeSource.is_active.is_(True))
        )
        sources = list(result.scalars())
        pending_income = await TwinService().get_pending_income(session, user_id)

        entries: list[dict[str, Any]] = []
        for source in sources:
            if source.last_received_date is None or source.declared_frequency_days is None:
                continue
            delay_mean = source.observed_delay_mean_days or 0.0
            baseline_arrival = (
                source.last_received_date
                + timedelta(days=source.declared_frequency_days)
                + timedelta(days=round(delay_mean))
            )

            key = (source.counterparty or "").strip().upper()
            pending_entry = pending_income.get(key)
            expected_arrival = (
                pending_entry["expected_arrival"]
                if pending_entry and pending_entry.get("expected_arrival")
                else baseline_arrival.isoformat()
            )

            entries.append(
                {
                    "label": source.label,
                    "expected_arrival": expected_arrival,
                    "baseline_arrival": baseline_arrival.isoformat(),
                }
            )
        return entries

    # -- scoring helpers --------------------------------------------------

    def _amount_at_risk(self, finding: RuleFinding, snapshot: FinancialStateSnapshot) -> Decimal:
        for key in (
            "obligations_due_14d",
            "obligations_due_30d",
            "total_amount",
            "obligation_amount",
            "amount",
            "target_amount",
        ):
            value = finding.evidence.get(key)
            if value is None:
                continue
            try:
                return Decimal(str(value))
            except (ValueError, TypeError):
                continue
        return snapshot.total_fixed_obligations

    def _urgency_days(self, finding: RuleFinding) -> int | None:
        for key in ("obligation_due_date", "target_date", "expected_arrival", "baseline_arrival"):
            value = finding.evidence.get(key)
            if not value:
                continue
            try:
                parsed = date.fromisoformat(value)
            except (ValueError, TypeError):
                continue
            return max(0, (parsed - date.today()).days)
        return None

    # -- persistence --------------------------------------------------------

    async def _persist_new_collisions(
        self,
        session: AsyncSession,
        user_id: UUID,
        collisions: list[Collision],
        simulation_run_id: UUID,
    ) -> None:
        for collision in collisions:
            existing_result = await session.execute(
                select(CollisionRecordRow)
                .where(
                    CollisionRecordRow.user_id == user_id,
                    CollisionRecordRow.condition_ids == collision.condition_ids,
                )
                .order_by(CollisionRecordRow.detected_at.desc())
            )
            existing_rows = list(existing_result.scalars())
            active = next((r for r in existing_rows if r.resolved_at is None), None)
            dismissed = next(
                (
                    r
                    for r in existing_rows
                    if r.resolved_at is not None
                    and (r.resolution_reason or "").startswith(USER_DISMISSAL_REASON_PREFIX)
                ),
                None,
            )

            if active is not None:
                active.joint_probability = collision.joint_probability
                active.individual_probabilities = collision.individual_probabilities
                active.amplification_factor = collision.amplification_factor
                active.severity = collision.severity
                active.urgency = collision.urgency
                active.first_impact_date = collision.first_impact_date
                active.evidence = collision.evidence
                active.human_statement = collision.human_statement
                active.simulation_run_id = simulation_run_id
                continue

            if dismissed is not None:
                # A user explicitly said "not this" for exactly this
                # condition combination — it must not silently reappear
                # on the very next assessment. A genuinely new
                # combination (different condition_ids) is unaffected.
                continue

            session.add(
                CollisionRecordRow(
                    id=collision.collision_id,
                    user_id=user_id,
                    condition_ids=collision.condition_ids,
                    joint_probability=collision.joint_probability,
                    individual_probabilities=collision.individual_probabilities,
                    amplification_factor=collision.amplification_factor,
                    severity=collision.severity,
                    urgency=collision.urgency,
                    first_impact_date=collision.first_impact_date,
                    evidence=collision.evidence,
                    human_statement=collision.human_statement,
                    simulation_run_id=simulation_run_id,
                )
            )
        await session.flush()

    async def _auto_resolve_stale_collisions(
        self, session: AsyncSession, user_id: UUID, current_collisions: list[Collision]
    ) -> None:
        current_condition_sets = {tuple(c.condition_ids) for c in current_collisions}
        result = await session.execute(
            select(CollisionRecordRow).where(
                CollisionRecordRow.user_id == user_id, CollisionRecordRow.resolved_at.is_(None)
            )
        )
        for row in result.scalars():
            if tuple(row.condition_ids) not in current_condition_sets:
                row.resolved_at = datetime.now(timezone.utc)
                row.resolution_reason = AUTO_RESOLUTION_REASON
        await session.flush()
