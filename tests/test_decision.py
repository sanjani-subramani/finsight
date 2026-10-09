from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.contracts.events import (
    ContextualIntervention,
    FinancialStateSnapshot,
    FinancialWeather,
    IncomeForecast,
    Obligation,
    Severity,
)
from app.models.tables import Intervention, NotificationDelivery, User
from app.modules.decision.gate import GateInput, evaluate_gate
from app.modules.decision.service import DecisionService
from app.modules.decision.shadow import compute_precision
from app.modules.decision.trace import TRACE_STAGE_ORDER, TraceBuilder, validate_trace_completeness
from app.modules.risk.rules import RuleFinding
from app.modules.risk.scoring import RiskScore
from app.modules.risk.service import RiskAssessment, RiskService

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------


def _make_gate_input(
    *,
    probability: float = 0.9,
    severity_signal: float = 0.9,
    urgency_score: float = 0.9,
    data_confidence: float = 0.9,
    financial_magnitude: float = 0.9,
    user_risk_tolerance: str = "balanced",
    recent_intervention_count: int = 0,
    hours_since_last_intervention: float | None = None,
) -> GateInput:
    return GateInput(
        probability=probability,
        severity_signal=severity_signal,
        urgency_score=urgency_score,
        data_confidence=data_confidence,
        financial_magnitude=financial_magnitude,
        user_risk_tolerance=user_risk_tolerance,
        recent_intervention_count=recent_intervention_count,
        hours_since_last_intervention=hours_since_last_intervention,
    )


def _make_snapshot(user_id, cash: Decimal = Decimal("5000")) -> FinancialStateSnapshot:
    return FinancialStateSnapshot(
        user_id=user_id,
        cash_available=cash,
        emergency_fund=Decimal("1000"),
        income_forecast=IncomeForecast(source="declared", confidence_score=0.7),
        obligations=[
            Obligation(
                label="Rent",
                amount=Decimal("15000"),
                due_date=date.today() + timedelta(days=5),
                is_fixed=True,
                is_paid=False,
                confidence_score=0.9,
            )
        ],
        weather=FinancialWeather.risk,
        safe_to_spend=Decimal("0"),
        state_confidence=0.9,
    )


def _make_finding() -> RuleFinding:
    return RuleFinding(
        rule_id="low_buffer",
        triggered=True,
        severity=3,
        evidence={
            "cash_available": "5000",
            "obligations_due_30d": "15000",
            "threshold": "22500.0",
            "multiplier": "1.5",
            "window_days": "30",
        },
        human_statement=(
            "Your available cash (Rs.5,000.00) is below 1.5x your obligations due in the "
            "next 30 days (Rs.15,000.00)."
        ),
    )


def _make_score(**breakdown_overrides) -> RiskScore:
    breakdown = {
        "probability": 0.9,
        "severity_normalized": 0.9,
        "urgency_normalized": 0.9,
        "magnitude_normalized": 0.9,
        "confidence": 0.9,
    }
    breakdown.update(breakdown_overrides)
    return RiskScore(score=0.9, breakdown=breakdown)


def _make_assessment(user_id, *, finding: RuleFinding | None = None, score: RiskScore | None = None) -> RiskAssessment:
    snapshot = _make_snapshot(user_id)
    finding = finding or _make_finding()
    score = score or _make_score()
    return RiskAssessment(
        snapshot_id=snapshot.snapshot_id,
        simulation_run_id=uuid4(),
        findings=[finding],
        collisions=[],
        overall_risk_score=score.score,
        top_collision=None,
        assessed_at=snapshot.generated_at,
        finding_scores={finding.rule_id: score},
        collision_scores={},
        snapshot=snapshot,
    )


# ---------------------------------------------------------------------------
# GATE
# ---------------------------------------------------------------------------


def test_high_probability_high_confidence_is_critical():
    decision = evaluate_gate(_make_gate_input(probability=0.9, data_confidence=0.9))
    assert decision.severity == Severity.critical


def test_high_probability_confidence_0_4_capped_at_monitor():
    decision = evaluate_gate(_make_gate_input(probability=0.9, data_confidence=0.4))
    assert decision.severity == Severity.monitor
    assert decision.severity_raw == Severity.critical
    assert decision.confidence_ceiling_applied is True


def test_high_probability_confidence_0_6_capped_at_notify():
    decision = evaluate_gate(_make_gate_input(probability=0.9, data_confidence=0.6))
    assert decision.severity == Severity.notify
    assert decision.severity_raw == Severity.critical
    assert decision.confidence_ceiling_applied is True


def test_fatigue_damping_demotes_notify_to_monitor_after_4_interventions():
    inp = _make_gate_input(
        probability=0.55, severity_signal=0.5, urgency_score=0.5, financial_magnitude=0.5,
        data_confidence=0.9, recent_intervention_count=4,
    )
    decision = evaluate_gate(inp)
    assert decision.stage_results[0]["severity"] == "notify"  # sanity: base stage was NOTIFY
    assert decision.fatigue_damped is True
    assert decision.severity == Severity.monitor


def test_fatigue_damping_never_demotes_critical():
    inp = _make_gate_input(probability=0.95, data_confidence=0.95, recent_intervention_count=10)
    decision = evaluate_gate(inp)
    assert decision.severity == Severity.critical
    assert decision.fatigue_damped is False


def test_conservative_tolerance_promotes_monitor_to_notify_at_probability_0_35():
    inp = _make_gate_input(
        probability=0.35, severity_signal=0.3, urgency_score=0.3, financial_magnitude=0.3,
        data_confidence=0.9, user_risk_tolerance="conservative",
    )
    decision = evaluate_gate(inp)
    assert decision.stage_results[2]["severity"] == "monitor"  # pre-tolerance-stage severity
    assert decision.tolerance_adjusted is True
    assert decision.severity == Severity.notify


def test_stage_results_records_severity_after_every_stage():
    decision = evaluate_gate(_make_gate_input())
    assert len(decision.stage_results) == 4
    stage_names = [s["stage"] for s in decision.stage_results]
    assert stage_names == ["base_severity", "confidence_ceiling", "fatigue_damping", "user_tolerance"]
    for stage in decision.stage_results:
        assert "severity" in stage


# ---------------------------------------------------------------------------
# TRACE
# ---------------------------------------------------------------------------


def _build_sample_trace_and_intervention():
    builder = TraceBuilder()
    builder.add("event", "Risk assessment triggered.", {})
    builder.add(
        "state_change",
        "Cash available Rs.5,000.00; obligations Rs.15,000.00.",
        {"cash_available": "5000", "obligations": "15000"},
    )
    builder.add(
        "risk_score",
        "Risk score 0.720 computed.",
        {"probability": 0.72, "severity_normalized": 0.5},
    )
    trace = builder.build()
    intervention = ContextualIntervention(
        user_id=uuid4(),
        severity=Severity.notify,
        headline="NOTIFY: shortfall risk at 72%",
        body="Cash available Rs.5,000.00 is below what's needed for obligations of Rs.15,000.00.",
        severity_raw=0.72,
        probability=0.72,
        urgency_score=0.5,
        data_confidence=0.9,
        decision_trace=trace,
    )
    return trace, intervention


def test_every_number_in_headline_appears_in_some_trace_step_values():
    # 72 (from "72%") must be found as 0.72*100 -- but validate_trace_completeness
    # compares numbers as literally written, so store the pct form explicitly.
    builder = TraceBuilder()
    builder.add("event", "x", {})
    builder.add("state_change", "Cash Rs.5,000.00; obligations Rs.15,000.00.", {"cash_available": "5000", "obligations": "15000"})
    builder.add("simulation", "Shortfall probability 72%.", {"shortfall_probability_pct": 72})
    trace = builder.build()
    intervention = ContextualIntervention(
        user_id=uuid4(),
        severity=Severity.notify,
        headline="NOTIFY: shortfall risk at 72%",
        body="Cash available Rs.5,000.00 is below what's needed for obligations of Rs.15,000.00.",
        severity_raw=0.72,
        probability=0.72,
        urgency_score=0.5,
        data_confidence=0.9,
        decision_trace=trace,
    )
    validate_trace_completeness(trace, intervention)  # must not raise


def test_validate_trace_completeness_raises_on_unsupported_number():
    trace, intervention = _build_sample_trace_and_intervention()
    broken = intervention.model_copy(update={"headline": "NOTIFY: shortfall risk at 99%"})
    with pytest.raises(ValueError, match="unsupported number"):
        validate_trace_completeness(trace, broken)


def test_trace_stages_are_in_correct_order():
    builder = TraceBuilder()
    builder.add("event", "e", {})
    builder.add("simulation", "s", {})
    builder.add("gate_stage_1", "g1", {})
    builder.add("recommendation", "r", {})
    trace = builder.build()
    stages = [step.stage for step in trace]
    indices = [TRACE_STAGE_ORDER.index(s) for s in stages]
    assert indices == sorted(indices)
    assert [step.order for step in trace] == [0, 1, 2, 3]

    with pytest.raises(ValueError):
        builder.add("event", "out of order", {})


def test_same_inputs_produce_identical_trace():
    user_id = uuid4()
    assessment = _make_assessment(user_id)
    finding = assessment.findings[0]
    score = assessment.finding_scores[finding.rule_id]
    gate_input = _make_gate_input()
    gate_decision = evaluate_gate(gate_input)

    service = DecisionService()
    trace_1 = service._build_trace(assessment, "finding", finding, score, gate_input, gate_decision)
    trace_2 = service._build_trace(assessment, "finding", finding, score, gate_input, gate_decision)
    assert trace_1 == trace_2


# ---------------------------------------------------------------------------
# SHADOW MODE
# ---------------------------------------------------------------------------


async def _make_user(db_session, *, shadow_override: bool | None) -> User:
    user = User(
        id=uuid4(),
        email=f"{uuid4()}@example.com",
        password_hash="hash",
        risk_tolerance="balanced",
        shadow_mode_override=shadow_override,
    )
    db_session.add(user)
    await db_session.flush()
    return user


async def test_shadow_mode_true_persists_without_delivery(db_session):
    user = await _make_user(db_session, shadow_override=True)
    assessment = _make_assessment(user.id)

    with patch.object(RiskService, "assess", AsyncMock(return_value=assessment)):
        result = await DecisionService().decide(db_session, user.id)

    from sqlalchemy import select

    rows = list((await db_session.execute(select(Intervention).where(Intervention.user_id == user.id))).scalars())
    assert len(rows) == 1
    assert rows[0].shadow_mode is True
    assert rows[0].delivered is False

    deliveries = list(
        (await db_session.execute(select(NotificationDelivery).where(NotificationDelivery.user_id == user.id))).scalars()
    )
    assert deliveries == []
    assert result is not None  # shadowed but still returned to the caller


async def test_shadow_mode_false_critical_creates_delivery_row(db_session):
    user = await _make_user(db_session, shadow_override=False)
    # severity_signal/urgency/magnitude all high + high probability -> CRITICAL via Stage 1.
    score = _make_score(probability=0.95, severity_normalized=0.95, urgency_normalized=0.95, magnitude_normalized=0.95, confidence=0.95)
    assessment = _make_assessment(user.id, score=score)

    with patch.object(RiskService, "assess", AsyncMock(return_value=assessment)):
        result = await DecisionService().decide(db_session, user.id)

    assert result is not None
    assert result.severity == Severity.critical

    from sqlalchemy import select

    rows = list((await db_session.execute(select(Intervention).where(Intervention.user_id == user.id))).scalars())
    assert len(rows) == 1
    assert rows[0].shadow_mode is False

    deliveries = list(
        (await db_session.execute(select(NotificationDelivery).where(NotificationDelivery.user_id == user.id))).scalars()
    )
    assert len(deliveries) == 1
    assert deliveries[0].status == "pending"


async def test_compute_precision_correct_arithmetic_on_seeded_data(db_session):
    user_id = uuid4()
    since = datetime.now(timezone.utc) - timedelta(days=1)

    # 3 NOTIFY: 2 materialized, 1 did not.
    for materialized in (True, True, False):
        db_session.add(
            Intervention(
                user_id=user_id,
                severity="notify",
                severity_raw=0.5,
                confidence_ceiling_applied=False,
                headline="h",
                body="b",
                probability=0.5,
                urgency_score=0.5,
                data_confidence=0.9,
                shadow_mode=False,
                delivered=True,
                outcome_materialized=materialized,
                outcome_checked_at=datetime.now(timezone.utc),
            )
        )
    # 1 CRITICAL, confidence-ceiling-applied, checked, did NOT materialize (a ceiling save).
    db_session.add(
        Intervention(
            user_id=user_id,
            severity="critical",
            severity_raw=0.9,
            confidence_ceiling_applied=True,
            headline="h",
            body="b",
            probability=0.9,
            urgency_score=0.9,
            data_confidence=0.4,
            shadow_mode=False,
            delivered=True,
            outcome_materialized=False,
            outcome_checked_at=datetime.now(timezone.utc),
        )
    )
    await db_session.flush()

    report = await compute_precision(db_session, since)
    notify = report.by_severity["notify"]
    assert notify.total_fired == 3
    assert notify.total_checked == 3
    assert notify.materialized == 2
    assert notify.precision == pytest.approx(2 / 3)
    assert notify.false_alarm_rate == pytest.approx(1 / 3)

    assert report.confidence_ceiling_total == 1
    assert report.confidence_ceiling_checked == 1
    assert report.confidence_ceiling_saves == 1
    assert report.confidence_ceiling_save_rate == pytest.approx(1.0)


async def test_compute_precision_zero_fired_does_not_divide_by_zero(db_session):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    report = await compute_precision(db_session, since)
    assert report.by_severity == {}
    assert report.confidence_ceiling_save_rate is None
