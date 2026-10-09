"""Shadow Mode (Innovation 1): FinSentinel can decide an intervention is
warranted WITHOUT actually delivering it, so its calls can be measured
against reality before users are ever interrupted. This module answers
"should this user's interventions be shadowed?" and, separately, "how
good were our shadowed/delivered calls, really?" — using only plain
measured counts, never an estimate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import FinancialEvent, Intervention
from app.models.tables import Obligation as ObligationRow
from app.models.tables import SimulationRun, User
from app.platform.config import Settings
from app.platform.timeutils import as_aware_utc

OUTCOME_LOOKFORWARD_FALLBACK_DAYS = 30


def is_shadow_mode(settings: Settings, user: User) -> bool:
    if user.shadow_mode_override is not None:
        return user.shadow_mode_override
    return settings.SHADOW_MODE


async def record_outcome(
    session: AsyncSession, intervention_id: UUID, materialized: bool, checked_at: datetime
) -> None:
    row = await session.get(Intervention, intervention_id)
    if row is None:
        return
    row.outcome_materialized = materialized
    row.outcome_checked_at = checked_at
    await session.flush()


async def _had_shortfall_between(session: AsyncSession, user_id: UUID, start: datetime, end: datetime) -> bool:
    # Duplicated from app.modules.risk.discovery._had_shortfall_after
    # rather than imported — it's a private, few-line helper, and per the
    # module boundary rule a private symbol must never cross a module
    # boundary (see app.modules.risk.collision._representative_breach_date
    # for the same precedent).
    negative_balance = await session.execute(
        select(FinancialEvent.id).where(
            FinancialEvent.user_id == user_id,
            FinancialEvent.event_type == "balance_snapshot",
            FinancialEvent.amount < 0,
            FinancialEvent.occurred_at >= start,
            FinancialEvent.occurred_at <= end,
        )
    )
    if negative_balance.first() is not None:
        return True

    missed_obligation = await session.execute(
        select(ObligationRow.id).where(
            ObligationRow.user_id == user_id,
            ObligationRow.is_paid.is_(False),
            ObligationRow.due_date >= start.date(),
            ObligationRow.due_date <= end.date(),
            ObligationRow.due_date < datetime.now(timezone.utc).date(),
        )
    )
    return missed_obligation.first() is not None


async def evaluate_outcomes(session: AsyncSession, lookback_days: int = 30) -> int:
    """Background job: for every intervention whose predicted horizon has
    now passed and whose outcome hasn't been checked yet, determine
    whether the predicted risk actually materialized. Returns the count
    evaluated.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=lookback_days)

    result = await session.execute(
        select(Intervention, SimulationRun)
        .join(SimulationRun, Intervention.simulation_run_id == SimulationRun.id)
        .where(Intervention.outcome_materialized.is_(None), Intervention.created_at >= cutoff)
    )
    rows = result.all()

    evaluated = 0
    for intervention, sim_run in rows:
        created_at = as_aware_utc(intervention.created_at)
        horizon_days = sim_run.horizon_days or OUTCOME_LOOKFORWARD_FALLBACK_DAYS
        window_end = created_at + timedelta(days=horizon_days)
        if now < window_end:
            continue  # the predicted horizon hasn't passed yet — nothing to check

        materialized = await _had_shortfall_between(session, intervention.user_id, created_at, window_end)
        intervention.outcome_materialized = materialized
        intervention.outcome_checked_at = now
        evaluated += 1

    if evaluated:
        await session.flush()
    return evaluated


@dataclass(frozen=True)
class SeverityPrecision:
    severity: str
    total_fired: int
    total_checked: int  # outcome_materialized is not None
    materialized: int
    # None (not 0.0) when total_checked == 0 — there is no measurement to
    # report yet, and reporting 0.0 would falsely claim "measured zero
    # precision" rather than "nothing measured." See PrecisionReport.
    precision: float | None
    false_alarm_rate: float | None


@dataclass(frozen=True)
class PrecisionReport:
    """Plain measured counts only. Every rate here is computed directly
    from Intervention.outcome_materialized rows — nothing here is
    fabricated, estimated, or backfilled. These are the only precision
    numbers this system is allowed to quote, and only after this real
    measurement has actually happened.
    """

    since: datetime
    by_severity: dict[str, SeverityPrecision] = field(default_factory=dict)
    confidence_ceiling_total: int = 0
    confidence_ceiling_checked: int = 0
    confidence_ceiling_saves: int = 0  # ceiling downgraded it, and it then did NOT materialize
    confidence_ceiling_save_rate: float | None = None


async def compute_precision(session: AsyncSession, since: datetime) -> PrecisionReport:
    result = await session.execute(select(Intervention).where(Intervention.created_at >= since))
    interventions = list(result.scalars())

    by_severity: dict[str, SeverityPrecision] = {}
    grouped: dict[str, list[Intervention]] = {}
    for row in interventions:
        grouped.setdefault(row.severity, []).append(row)

    for severity, rows in grouped.items():
        checked = [r for r in rows if r.outcome_materialized is not None]
        materialized = [r for r in checked if r.outcome_materialized]
        precision = len(materialized) / len(checked) if checked else None
        false_alarm_rate = (1 - precision) if precision is not None else None
        by_severity[severity] = SeverityPrecision(
            severity=severity,
            total_fired=len(rows),
            total_checked=len(checked),
            materialized=len(materialized),
            precision=precision,
            false_alarm_rate=false_alarm_rate,
        )

    ceiling_rows = [r for r in interventions if r.confidence_ceiling_applied]
    ceiling_checked = [r for r in ceiling_rows if r.outcome_materialized is not None]
    ceiling_saves = [r for r in ceiling_checked if not r.outcome_materialized]
    ceiling_save_rate = len(ceiling_saves) / len(ceiling_checked) if ceiling_checked else None

    return PrecisionReport(
        since=since,
        by_severity=by_severity,
        confidence_ceiling_total=len(ceiling_rows),
        confidence_ceiling_checked=len(ceiling_checked),
        confidence_ceiling_saves=len(ceiling_saves),
        confidence_ceiling_save_rate=ceiling_save_rate,
    )
