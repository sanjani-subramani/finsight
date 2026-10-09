"""class ExplainService — the public face of app.modules.explain.

Every method here goes through the SAME grounding validation, via
Narrator.narrate, whether narrating a whole intervention, a single trace
step, or the current snapshot. This module reads already-computed state
via app.modules.decision/twin's public service classes; it never
recomputes risk or decision logic itself.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ContextualIntervention, RecommendedAction, Severity, TraceStep
from app.models.tables import Intervention
from app.modules.decision.trace import TraceBuilder
from app.modules.explain.narrator import NarrationResult, Narrator
from app.platform.eventbus import get_redis_client
from app.platform.logging import get_logger
from app.platform.timeutils import as_aware_utc

logger = get_logger(__name__)


def _intervention_and_trace_from_row(row: Intervention) -> tuple[ContextualIntervention, list[TraceStep]]:
    trace = [TraceStep.model_validate(step) for step in (row.decision_trace or [])]
    recommended_actions = [RecommendedAction.model_validate(action) for action in (row.recommended_actions or [])]
    intervention = ContextualIntervention(
        intervention_id=row.id,
        user_id=row.user_id,
        created_at=as_aware_utc(row.created_at),
        severity=Severity(row.severity),
        headline=row.headline,
        body=row.body,
        triggered_by_event_id=row.triggered_by_event_id,
        triggered_by_threat_id=row.triggered_by_threat_id,
        snapshot_id=row.snapshot_id,
        severity_raw=float(row.severity_raw),
        confidence_ceiling_applied=row.confidence_ceiling_applied,
        probability=float(row.probability),
        urgency_score=float(row.urgency_score),
        data_confidence=float(row.data_confidence),
        decision_trace=trace,
        recommended_actions=recommended_actions,
        shadow_mode=row.shadow_mode,
        delivered=row.delivered,
    )
    return intervention, trace


def _snapshot_trace_and_intervention(snapshot: object, user_id: UUID) -> tuple[list[TraceStep], ContextualIntervention]:
    # snapshot is a FinancialStateSnapshot; typed as object in the
    # signature purely to keep the import local to the function body
    # (deferred, matching the rest of this file's lazy-import-of-siblings
    # pattern) without upsetting a type checker that hasn't seen it yet.
    from app.contracts.events import FinancialStateSnapshot

    assert isinstance(snapshot, FinancialStateSnapshot)

    builder = TraceBuilder()
    builder.add(
        "state_change",
        f"Cash available Rs.{snapshot.cash_available:,.2f}; emergency fund Rs.{snapshot.emergency_fund:,.2f}; "
        f"total fixed obligations Rs.{snapshot.total_fixed_obligations:,.2f}.",
        {
            "cash_available": str(snapshot.cash_available),
            "emergency_fund": str(snapshot.emergency_fund),
            "total_fixed_obligations": str(snapshot.total_fixed_obligations),
        },
    )
    if snapshot.shortfall_risks:
        top_risk = snapshot.shortfall_risks[0]
        prob_pct = round(top_risk.probability * 100)
        builder.add(
            "simulation",
            f"Shortfall probability over {top_risk.horizon_days} days: {prob_pct}%.",
            {"shortfall_probability_pct": prob_pct, "horizon_days": top_risk.horizon_days},
        )
    builder.add(
        "recommendation",
        f"Rs.{snapshot.safe_to_spend:,.2f} is currently safe to spend.",
        {"safe_to_spend": str(snapshot.safe_to_spend)},
    )
    trace = builder.build()

    body = (
        f"Financial weather: {snapshot.weather.value}. You have Rs.{snapshot.cash_available:,.2f} available, "
        f"with Rs.{snapshot.safe_to_spend:,.2f} safe to spend."
    )
    intervention = ContextualIntervention(
        user_id=user_id,
        severity=Severity.ignore,  # informational only, not an alert
        headline="Current financial state",
        body=body,
        snapshot_id=snapshot.snapshot_id,
        severity_raw=0.0,
        probability=0.0,
        urgency_score=0.0,
        data_confidence=snapshot.state_confidence,
        decision_trace=trace,
    )
    return trace, intervention


class ExplainService:
    def __init__(self, narrator: Narrator | None = None) -> None:
        self._narrator = narrator or Narrator(redis_client=get_redis_client())

    async def get_trace_steps(
        self, session: AsyncSession, user_id: UUID, intervention_id: UUID
    ) -> list[TraceStep] | None:
        """Public accessor for a persisted intervention's trace steps —
        e.g. so a caller can list step order/stage before narrating each
        one via explain_trace_step, without reaching into this module's
        row-conversion internals."""
        from app.modules.decision.service import DecisionService

        row = await DecisionService().get_intervention(session, user_id, intervention_id)
        if row is None:
            return None
        _intervention, trace = _intervention_and_trace_from_row(row)
        return trace

    async def explain_intervention(
        self, session: AsyncSession, user_id: UUID, intervention_id: UUID, style: str = "concise"
    ) -> NarrationResult | None:
        from app.modules.decision.service import DecisionService

        row = await DecisionService().get_intervention(session, user_id, intervention_id)
        if row is None:
            return None
        intervention, trace = _intervention_and_trace_from_row(row)
        return await self._narrator.narrate(trace, intervention, style=style)

    async def explain_trace_step(
        self, session: AsyncSession, user_id: UUID, intervention_id: UUID, step_order: int
    ) -> NarrationResult | None:
        from app.modules.decision.service import DecisionService

        row = await DecisionService().get_intervention(session, user_id, intervention_id)
        if row is None:
            return None
        intervention, trace = _intervention_and_trace_from_row(row)
        matching = [step for step in trace if step.order == step_order]
        if not matching:
            return None
        # Narrate just this one step as its own miniature trace -- the
        # SAME grounding validation applies (a number must come from THIS
        # step's own values), giving a per-step "how did you work this
        # out?" explanation with the identical anti-hallucination guarantee
        # as the full intervention narration.
        return await self._narrator.narrate(matching, intervention, style="concise")

    async def explain_snapshot(self, session: AsyncSession, user_id: UUID) -> NarrationResult:
        from app.modules.twin.service import TwinService

        snapshot = await TwinService().get_snapshot(session, user_id)
        trace, intervention = _snapshot_trace_and_intervention(snapshot, user_id)
        return await self._narrator.narrate(trace, intervention, style="concise")
