"""DecisionService — turns a RiskAssessment into (at most) one
ContextualIntervention: decides whether to interrupt the user via the
Gate, builds a fully-supported Decision Trace, and persists the result
(shadowed or delivered) for later measurement.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ContextualIntervention, RecommendedAction, Severity, TraceStep
from app.models.tables import Intervention, NotificationDelivery, User
from app.modules.decision.actions import build_recommended_actions
from app.modules.decision.arbitration import ArbitrationResult, arbitrate
from app.modules.decision.gate import GateDecision, GateInput, evaluate_gate
from app.modules.decision.shadow import is_shadow_mode
from app.modules.decision.trace import TraceBuilder, validate_trace_completeness
from app.modules.risk.collision import Collision
from app.modules.risk.rules import RuleFinding
from app.modules.risk.scoring import RiskScore
from app.modules.risk.service import RiskAssessment
from app.platform.audit import write_audit
from app.platform.config import get_settings
from app.platform.logging import get_logger
from app.platform.timeutils import as_aware_utc

logger = get_logger(__name__)

RECENT_INTERVENTION_WINDOW_HOURS = 24
# app.modules.notification.delivery is the only channel actually wired up
# right now (LogChannel) — real channel selection (push/email/SMS) is a
# later concern, so every delivery defaults to the one that works today.
DEFAULT_NOTIFICATION_CHANNEL = "log"

_SEVERITY_LABELS: dict[Severity, str] = {
    Severity.ignore: "IGNORE",
    Severity.monitor: "MONITOR",
    Severity.notify: "NOTIFY",
    Severity.critical: "CRITICAL",
}


def _pct(fraction: float) -> int:
    # The single conversion point from a 0-1 probability to the whole
    # percent number shown in text — every caller uses this so a
    # percentage appearing in headline/body text always numerically
    # matches the same figure recorded in a TraceStep's values (see
    # app.modules.decision.trace's convention comment).
    return round(fraction * 100)


class DecisionService:
    async def decide(
        self,
        session: AsyncSession,
        user_id: UUID,
        trigger_event_id: UUID | None = None,
        trigger_threat_id: UUID | None = None,
    ) -> ContextualIntervention | None:
        from app.modules.risk.service import RiskService

        assessment = await RiskService().assess(session, user_id)
        if not assessment.findings and not assessment.collisions:
            return None  # nothing to say

        assert assessment.snapshot is not None, "RiskService.assess always populates snapshot"
        snapshot = assessment.snapshot

        kind, item, score = self._select_top_item(assessment)
        user = await session.get(User, user_id)

        gate_input = await self._build_gate_input(session, user_id, user, assessment, score)
        gate_decision = evaluate_gate(gate_input)

        arbitration_result: ArbitrationResult | None = None
        recommended_actions: list[RecommendedAction] = []
        if gate_decision.severity in (Severity.notify, Severity.critical) and assessment.sim_result is not None:
            arbitration_result = await arbitrate(session, user_id, snapshot, assessment.sim_result)
            recommended_actions = build_recommended_actions(arbitration_result)

        trace = self._build_trace(assessment, kind, item, score, gate_input, gate_decision, arbitration_result)

        intervention_id = uuid4()
        headline = f"{_SEVERITY_LABELS[gate_decision.severity]}: shortfall risk at {_pct(gate_input.probability)}%"
        body = item.human_statement

        settings = get_settings()
        shadow_mode = is_shadow_mode(settings, user) if user is not None else settings.SHADOW_MODE

        intervention = ContextualIntervention(
            intervention_id=intervention_id,
            user_id=user_id,
            severity=gate_decision.severity,
            headline=headline,
            body=body,
            triggered_by_event_id=trigger_event_id,
            triggered_by_threat_id=trigger_threat_id,
            snapshot_id=snapshot.snapshot_id,
            severity_raw=gate_decision.base_score,
            confidence_ceiling_applied=gate_decision.confidence_ceiling_applied,
            probability=gate_input.probability,
            urgency_score=gate_input.urgency_score,
            data_confidence=gate_input.data_confidence,
            decision_trace=trace,
            recommended_actions=recommended_actions,
            shadow_mode=shadow_mode,
            delivered=False,
        )

        # Every number this intervention asserts must be traceable — this
        # runs BEFORE persistence so a broken trace fails loudly instead
        # of silently reaching a user.
        validate_trace_completeness(trace, intervention)

        row = await self._persist(session, intervention, assessment.simulation_run_id)

        await write_audit(
            session,
            actor_user_id=None,
            action="decision.intervention_created",
            resource_type="intervention",
            resource_id=str(row.id),
            payload={"severity": gate_decision.severity.value, "shadow_mode": shadow_mode},
        )

        if gate_decision.severity == Severity.ignore:
            return None  # persisted above for analytics; nothing to say to the user

        if not shadow_mode and gate_decision.severity in (Severity.notify, Severity.critical):
            await self._enqueue_delivery(session, row)

        return intervention

    async def get_interventions(
        self, session: AsyncSession, user_id: UUID, include_shadow: bool = False
    ) -> list[Intervention]:
        conditions = [Intervention.user_id == user_id]
        if not include_shadow:
            conditions.append(Intervention.shadow_mode.is_(False))
        result = await session.execute(
            select(Intervention).where(*conditions).order_by(Intervention.created_at.desc())
        )
        return list(result.scalars())

    async def get_intervention(self, session: AsyncSession, user_id: UUID, intervention_id: UUID) -> Intervention | None:
        result = await session.execute(
            select(Intervention).where(Intervention.id == intervention_id, Intervention.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def acknowledge(self, session: AsyncSession, user_id: UUID, intervention_id: UUID) -> Intervention | None:
        row = await self.get_intervention(session, user_id, intervention_id)
        if row is None:
            return None
        row.user_acknowledged = True
        if row.acknowledged_at is None:
            row.acknowledged_at = datetime.now(timezone.utc)
        await session.flush()
        return row

    async def mark_acted(
        self, session: AsyncSession, user_id: UUID, intervention_id: UUID, acted: bool
    ) -> Intervention | None:
        row = await self.get_intervention(session, user_id, intervention_id)
        if row is None:
            return None
        row.user_acted = acted
        await session.flush()
        return row

    # -- selection / gate input ------------------------------------------

    def _select_top_item(
        self, assessment: RiskAssessment
    ) -> tuple[str, RuleFinding | Collision, RiskScore]:
        # Prefer the top collision when one exists — it represents
        # amplified, compounding risk (the whole point of Step 7's
        # differentiator), which is a stronger basis for an intervention
        # than any single finding alone.
        if assessment.top_collision is not None:
            collision = assessment.top_collision
            score = assessment.collision_scores.get(collision.collision_id)
            if score is None:
                score = RiskScore(score=0.0, breakdown={})
            return "collision", collision, score

        finding = max(assessment.findings, key=lambda f: assessment.finding_scores[f.rule_id].score)
        return "finding", finding, assessment.finding_scores[finding.rule_id]

    async def _build_gate_input(
        self,
        session: AsyncSession,
        user_id: UUID,
        user: User | None,
        assessment: RiskAssessment,
        score: RiskScore,
    ) -> GateInput:
        assert assessment.snapshot is not None
        breakdown = score.breakdown
        probability = float(breakdown.get("probability", 0.0))
        severity_signal = float(breakdown.get("severity_normalized", 0.0))
        urgency_score = float(breakdown.get("urgency_normalized", 0.5))
        financial_magnitude = float(breakdown.get("magnitude_normalized", 0.0))
        data_confidence = assessment.snapshot.state_confidence

        cutoff = datetime.now(timezone.utc) - timedelta(hours=RECENT_INTERVENTION_WINDOW_HOURS)
        result = await session.execute(
            select(Intervention.created_at)
            .where(Intervention.user_id == user_id, Intervention.created_at >= cutoff)
            .order_by(Intervention.created_at.desc())
        )
        recent_created_ats = [as_aware_utc(row) for row in result.scalars()]

        hours_since_last = (
            (datetime.now(timezone.utc) - recent_created_ats[0]).total_seconds() / 3600
            if recent_created_ats
            else None
        )

        return GateInput(
            probability=probability,
            severity_signal=severity_signal,
            urgency_score=urgency_score,
            data_confidence=data_confidence,
            financial_magnitude=financial_magnitude,
            user_risk_tolerance=user.risk_tolerance if user is not None else "balanced",
            recent_intervention_count=len(recent_created_ats),
            hours_since_last_intervention=hours_since_last,
        )

    def _base_simulation_probability(self, assessment: RiskAssessment, gate_input: GateInput) -> float:
        # The "simulation" trace stage always describes the base Monte
        # Carlo shortfall probability, which is distinct from
        # gate_input.probability when the top item is a collision (whose
        # joint_probability is its own, usually higher, figure). Every
        # finding's RiskScore was built from the same single simulation
        # run in RiskService.assess(), so any one of them carries it.
        if assessment.finding_scores:
            return float(next(iter(assessment.finding_scores.values())).breakdown.get("probability", gate_input.probability))
        return gate_input.probability

    # -- trace ------------------------------------------------------------

    def _build_trace(
        self,
        assessment: RiskAssessment,
        kind: str,
        item: RuleFinding | Collision,
        score: RiskScore,
        gate_input: GateInput,
        gate_decision: GateDecision,
        arbitration_result: ArbitrationResult | None = None,
    ) -> list[TraceStep]:
        assert assessment.snapshot is not None
        snapshot = assessment.snapshot
        builder = TraceBuilder()

        builder.add(
            "event",
            "Risk assessment triggered for this user.",
            {},
        )
        builder.add(
            "state_change",
            f"Cash available Rs.{snapshot.cash_available:,.2f}; total fixed obligations "
            f"Rs.{snapshot.total_fixed_obligations:,.2f}.",
            {
                "cash_available": str(snapshot.cash_available),
                "total_fixed_obligations": str(snapshot.total_fixed_obligations),
            },
        )
        base_probability = self._base_simulation_probability(assessment, gate_input)
        builder.add(
            "simulation",
            f"Simulated shortfall probability: {_pct(base_probability)}%.",
            {"shortfall_probability_pct": _pct(base_probability)},
        )
        builder.add(
            "rule_findings",
            f"{len(assessment.findings)} risk rule(s) triggered.",
            {"finding_count": len(assessment.findings), **_flatten_evidence(assessment.findings)},
        )
        if kind == "collision":
            collision = item
            assert isinstance(collision, Collision)
            baseline_probability = collision.evidence.get("baseline_probability_all_removed", 0.0)
            builder.add(
                "collision",
                f"Collision combining {len(collision.condition_ids)} condition(s); joint probability "
                f"{_pct(collision.joint_probability)}%, amplification {collision.amplification_factor:.2f}x. "
                f"Shortfall risk rose from {_pct(baseline_probability)}% to {_pct(collision.joint_probability)}%.",
                {
                    "joint_probability_pct": _pct(collision.joint_probability),
                    # Matches the ":.0%" figure collision.human_statement's
                    # own closing sentence quotes — must be recorded in
                    # percentage form, not the raw 0-1 fraction, per
                    # trace.py's convention.
                    "baseline_probability_pct": _pct(baseline_probability),
                    "amplification_factor": collision.amplification_factor,
                    **collision.evidence,
                },
            )
        builder.add(
            "risk_score",
            f"Risk score {score.score:.3f} for the top item.",
            dict(score.breakdown),
        )
        # GateDecision.stage_results uses short internal names
        # (base_severity, confidence_ceiling, ...); TraceBuilder's fixed
        # slots are the positional gate_stage_1..4 — map onto those in
        # the same order the Gate produced them.
        for index, stage_result in enumerate(gate_decision.stage_results, start=1):
            builder.add(
                f"gate_stage_{index}",
                gate_decision.reasoning[index - 1] if index - 1 < len(gate_decision.reasoning) else stage_result["stage"],
                dict(stage_result),
            )
        arbitration_statement = (
            f"Final severity: {gate_decision.severity.value.upper()} "
            f"(stage 1 raw: {gate_decision.severity_raw.value.upper()})."
        )
        arbitration_values: dict[str, Any] = {"base_score": gate_decision.base_score}

        if arbitration_result is not None:
            arbitration_values["claim_count"] = len(arbitration_result.claims)
            arbitration_values["reduction_count"] = len(arbitration_result.reductions)
            arbitration_values["prob_before_pct"] = _pct(arbitration_result.prob_before)
            arbitration_values["prob_after_pct"] = _pct(arbitration_result.prob_after)
            arbitration_values["trade_off_statement"] = arbitration_result.trade_off_statement
            for claim in arbitration_result.claims:
                arbitration_values[f"claim.{claim.claim_id}.amount"] = str(claim.amount)
            for claim_id, amount in arbitration_result.reductions.items():
                arbitration_values[f"reduction.{claim_id}"] = str(amount)

            reduction_summary = (
                "no reductions were needed"
                if not arbitration_result.reductions
                else f"{len(arbitration_result.reductions)} claim(s) reduced"
            )
            arbitration_statement += (
                f" Considered {len(arbitration_result.claims)} claim(s) across tiers; {reduction_summary}. "
                f"Verified shortfall risk {_pct(arbitration_result.prob_before)}% before, "
                f"{_pct(arbitration_result.prob_after)}% after."
            )

        builder.add("arbitration", arbitration_statement, arbitration_values)

        if arbitration_result is not None and arbitration_result.reductions:
            claim_labels = {claim.claim_id: claim.label for claim in arbitration_result.claims}
            claim_labels["buffer:emergency_fund_drawdown"] = "emergency fund"
            recommendation_statement = "Recommended: " + "; ".join(
                f"reduce {claim_labels.get(claim_id, claim_id)} by Rs.{amount:,.2f}"
                for claim_id, amount in arbitration_result.reductions.items()
            ) + "."
            recommendation_values = {
                f"recommendation.{claim_id}": str(amount) for claim_id, amount in arbitration_result.reductions.items()
            }
        else:
            recommendation_statement = "No recommended actions."
            recommendation_values = {}

        builder.add("recommendation", recommendation_statement, recommendation_values)
        return builder.build()

    # -- persistence --------------------------------------------------------

    async def _persist(
        self, session: AsyncSession, intervention: ContextualIntervention, simulation_run_id: UUID
    ) -> Intervention:
        row = Intervention(
            id=intervention.intervention_id,
            user_id=intervention.user_id,
            severity=intervention.severity.value,
            severity_raw=intervention.severity_raw,
            confidence_ceiling_applied=intervention.confidence_ceiling_applied,
            headline=intervention.headline,
            body=intervention.body,
            triggered_by_event_id=intervention.triggered_by_event_id,
            triggered_by_threat_id=intervention.triggered_by_threat_id,
            snapshot_id=intervention.snapshot_id,
            simulation_run_id=simulation_run_id,
            probability=intervention.probability,
            urgency_score=intervention.urgency_score,
            data_confidence=intervention.data_confidence,
            decision_trace=[step.model_dump(mode="json") for step in intervention.decision_trace],
            recommended_actions=[a.model_dump(mode="json") for a in intervention.recommended_actions],
            shadow_mode=intervention.shadow_mode,
            delivered=False,
        )
        session.add(row)
        await session.flush()
        return row

    async def _enqueue_delivery(self, session: AsyncSession, row: Intervention) -> NotificationDelivery:
        delivery = NotificationDelivery(
            intervention_id=row.id,
            user_id=row.user_id,
            channel=DEFAULT_NOTIFICATION_CHANNEL,
            status="pending",
        )
        session.add(delivery)
        await session.flush()
        return delivery


def _flatten_evidence(findings: list[RuleFinding]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for finding in findings:
        for key, value in finding.evidence.items():
            flattened[f"{finding.rule_id}.{key}"] = value
    return flattened
