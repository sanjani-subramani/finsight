from __future__ import annotations

import json
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import httpx
import pytest

from app.contracts.events import FinancialStateSnapshot, FinancialWeather, Goal, IncomeForecast, Obligation
from app.models.tables import CollisionRecord as CollisionRecordRow
from app.models.tables import FinancialEvent, Obligation as ObligationRow, ProposedRuleRecord as ProposedRuleRecordRow
from app.modules.risk import collision as collision_module
from app.modules.risk.collision import Collision, detect_collisions
from app.modules.risk.discovery import approve_proposed_rule, propose_rules
from app.modules.risk.rules import RULE_REGISTRY, RuleContext, RuleFinding, evaluate_all_rules
from app.modules.risk.scoring import compute_risk_score
from app.modules.risk.service import RiskService
from app.modules.simulation.engine import SimulationResult
from app.platform.config import get_settings

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------


class _FakeGroqClient:
    def __init__(self, content: str) -> None:
        self.content = content

    async def post(self, url, json=None, headers=None):
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": self.content}}]},
            request=httpx.Request("POST", url),
        )

    async def aclose(self) -> None:
        pass


def _llm_settings_with_key():
    return get_settings().model_copy(update={"GROQ_API_KEY": "test-key-not-real"})


def _make_forecast(expected_arrival: date | None = None) -> IncomeForecast:
    return IncomeForecast(source="declared", confidence_score=0.7, expected_arrival=expected_arrival)


def _make_snapshot(
    *,
    user_id: UUID | None = None,
    cash: Decimal = Decimal("100000"),
    emergency_fund: Decimal = Decimal("50000"),
    obligations: list[Obligation] | None = None,
    goals: list[Goal] | None = None,
    income_forecast: IncomeForecast | None = None,
    state_confidence: float = 0.9,
) -> FinancialStateSnapshot:
    return FinancialStateSnapshot(
        user_id=user_id or uuid4(),
        cash_available=cash,
        emergency_fund=emergency_fund,
        income_forecast=income_forecast or _make_forecast(),
        obligations=obligations or [],
        goals=goals or [],
        weather=FinancialWeather.stable,
        safe_to_spend=Decimal("0"),
        state_confidence=state_confidence,
    )


def _obligation(label: str, amount: str, due_in_days: int, *, is_fixed: bool = True, is_paid: bool = False) -> Obligation:
    return Obligation(
        label=label,
        amount=Decimal(amount),
        due_date=date.today() + timedelta(days=due_in_days),
        is_fixed=is_fixed,
        is_paid=is_paid,
        confidence_score=0.9,
    )


def _make_event(
    user_id, *, event_type: str = "expense", amount: Decimal | None = Decimal("100.00"), counterparty: str | None = None
) -> FinancialEvent:
    return FinancialEvent(
        id=uuid4(),
        user_id=user_id,
        schema_version=1,
        event_type=event_type,
        amount=amount,
        currency="INR",
        occurred_at=datetime.now(timezone.utc),
        counterparty=counterparty,
        data_source="manual",
        confidence_score=0.9,
    )


def _make_sim_result(
    shortfall_probability: float,
    *,
    horizon: int = 90,
    seed: int = 12345,
    scenarios_run: int = 200,
    p50_breach_day: float | None = 5.0,
) -> SimulationResult:
    return SimulationResult(
        balance_matrix_summary={},
        shortfall_probability_by_horizon={horizon: shortfall_probability},
        min_balance_p5=Decimal("-100"),
        min_balance_p50=Decimal("500"),
        first_breach_day_distribution={"percentiles": {"p50": p50_breach_day}} if p50_breach_day else {},
        time_to_danger_days=None,
        scenarios_run=scenarios_run,
        seed=seed,
        duration_ms=1,
    )


def _finding(rule_id: str, severity: int, evidence: dict, statement: str) -> RuleFinding:
    return RuleFinding(rule_id=rule_id, triggered=True, severity=severity, evidence=evidence, human_statement=statement)


# ---------------------------------------------------------------------------
# RULES
# ---------------------------------------------------------------------------


def test_low_buffer_triggers_when_cash_below_threshold():
    snapshot = _make_snapshot(cash=Decimal("10000"), obligations=[_obligation("Rent", "10000", 20)])
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    finding = RULE_REGISTRY["low_buffer"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["cash_available"] == "10000"
    assert finding.evidence["obligations_due_30d"] == "10000"
    assert finding.evidence["threshold"] == "15000.0"


def test_low_buffer_does_not_trigger_when_cash_sufficient():
    snapshot = _make_snapshot(cash=Decimal("50000"), obligations=[_obligation("Rent", "10000", 20)])
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert RULE_REGISTRY["low_buffer"].evaluate(ctx) is None


def test_critical_buffer_triggers_when_cash_below_14d_obligations():
    snapshot = _make_snapshot(cash=Decimal("5000"), obligations=[_obligation("Rent", "10000", 10)])
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    finding = RULE_REGISTRY["critical_buffer"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["obligations_due_14d"] == "10000"


def test_critical_buffer_does_not_trigger_with_sufficient_cash():
    snapshot = _make_snapshot(cash=Decimal("20000"), obligations=[_obligation("Rent", "10000", 10)])
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert RULE_REGISTRY["critical_buffer"].evaluate(ctx) is None


def test_emergency_fund_depleted_triggers_below_one_month_fixed():
    snapshot = _make_snapshot(
        emergency_fund=Decimal("1000"), obligations=[_obligation("Rent", "8000", 90, is_fixed=True)]
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    finding = RULE_REGISTRY["emergency_fund_depleted"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["monthly_fixed_obligations"] == "8000"


def test_emergency_fund_depleted_does_not_trigger_when_covered():
    snapshot = _make_snapshot(
        emergency_fund=Decimal("20000"), obligations=[_obligation("Rent", "8000", 90, is_fixed=True)]
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert RULE_REGISTRY["emergency_fund_depleted"].evaluate(ctx) is None


def test_negative_projection_triggers_on_negative_median():
    snapshot = _make_snapshot()
    sim_result = _make_sim_result(0.5)
    sim_result = replace(sim_result, min_balance_p50=Decimal("-500"))
    ctx = RuleContext(snapshot=snapshot, simulation_result=sim_result, recent_events=[])
    finding = RULE_REGISTRY["negative_projection"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["min_balance_p50"] == "-500"


def test_negative_projection_does_not_trigger_on_positive_median_or_missing_result():
    snapshot = _make_snapshot()
    sim_result = replace(_make_sim_result(0.5), min_balance_p50=Decimal("1000"))
    ctx = RuleContext(snapshot=snapshot, simulation_result=sim_result, recent_events=[])
    assert RULE_REGISTRY["negative_projection"].evaluate(ctx) is None

    ctx_no_sim = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert RULE_REGISTRY["negative_projection"].evaluate(ctx_no_sim) is None


def test_income_delayed_triggers_when_expected_after_baseline():
    snapshot = _make_snapshot()
    ctx = RuleContext(
        snapshot=snapshot,
        simulation_result=None,
        recent_events=[],
        historical_averages={
            "income_sources": [
                {"label": "ACME Freelance", "expected_arrival": "2026-09-20", "baseline_arrival": "2026-09-13"}
            ]
        },
    )
    finding = RULE_REGISTRY["income_delayed"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["days_late"] == 7
    assert finding.evidence["income_source"] == "ACME Freelance"


def test_income_delayed_does_not_trigger_when_on_time():
    snapshot = _make_snapshot()
    ctx = RuleContext(
        snapshot=snapshot,
        simulation_result=None,
        recent_events=[],
        historical_averages={
            "income_sources": [
                {"label": "ACME Freelance", "expected_arrival": "2026-09-13", "baseline_arrival": "2026-09-13"}
            ]
        },
    )
    assert RULE_REGISTRY["income_delayed"].evaluate(ctx) is None


def test_obligation_cluster_triggers_for_two_fixed_within_window():
    snapshot = _make_snapshot(
        obligations=[_obligation("Rent", "15000", 5), _obligation("EMI", "6800", 9)]
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    finding = RULE_REGISTRY["obligation_cluster"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["total_amount"] == "21800"
    assert {o["label"] for o in finding.evidence["obligations"]} == {"Rent", "EMI"}


def test_obligation_cluster_does_not_trigger_when_spread_apart():
    snapshot = _make_snapshot(
        obligations=[_obligation("Rent", "15000", 1), _obligation("EMI", "6800", 25)]
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert RULE_REGISTRY["obligation_cluster"].evaluate(ctx) is None


def test_income_after_obligation_classic_freelancer_trap():
    obligation_due = date.today() + timedelta(days=5)
    snapshot = _make_snapshot(
        obligations=[_obligation("Rent", "15000", 5)],
        income_forecast=_make_forecast(expected_arrival=obligation_due + timedelta(days=3)),
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    finding = RULE_REGISTRY["income_after_obligation"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["gap_days"] == 3
    assert finding.evidence["next_obligation"] == "Rent"


def test_income_after_obligation_does_not_trigger_when_income_arrives_first():
    obligation_due = date.today() + timedelta(days=5)
    snapshot = _make_snapshot(
        obligations=[_obligation("Rent", "15000", 5)],
        income_forecast=_make_forecast(expected_arrival=obligation_due - timedelta(days=2)),
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert RULE_REGISTRY["income_after_obligation"].evaluate(ctx) is None


def test_high_burn_triggers_on_40pct_spike():
    snapshot = _make_snapshot()
    ctx = RuleContext(
        snapshot=snapshot,
        simulation_result=None,
        recent_events=[],
        historical_averages={"discretionary_7d_total": 980.0, "discretionary_60d_daily_mean": 100.0},
    )
    finding = RULE_REGISTRY["high_burn"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["baseline_60d_daily_mean"] == 100.0


def test_high_burn_does_not_trigger_on_normal_spend():
    snapshot = _make_snapshot()
    ctx = RuleContext(
        snapshot=snapshot,
        simulation_result=None,
        recent_events=[],
        historical_averages={"discretionary_7d_total": 700.0, "discretionary_60d_daily_mean": 100.0},
    )
    assert RULE_REGISTRY["high_burn"].evaluate(ctx) is None


def test_unusual_large_expense_triggers_over_3x_p95():
    snapshot = _make_snapshot()
    event = _make_event(snapshot.user_id, event_type="expense", amount=Decimal("50000"), counterparty="Big Store")
    ctx = RuleContext(
        snapshot=snapshot, simulation_result=None, recent_events=[event], historical_averages={"expense_p95": 5000.0}
    )
    finding = RULE_REGISTRY["unusual_large_expense"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["amount"] == 50000.0
    assert finding.evidence["historical_p95"] == 5000.0


def test_unusual_large_expense_does_not_trigger_for_typical_expense():
    snapshot = _make_snapshot()
    event = _make_event(snapshot.user_id, event_type="expense", amount=Decimal("2000"))
    ctx = RuleContext(
        snapshot=snapshot, simulation_result=None, recent_events=[event], historical_averages={"expense_p95": 5000.0}
    )
    assert RULE_REGISTRY["unusual_large_expense"].evaluate(ctx) is None


def test_goal_at_risk_triggers_when_underfunded_near_deadline():
    goal = Goal(
        label="Emergency Trip",
        target_amount=Decimal("50000"),
        saved_amount=Decimal("10000"),
        target_date=date.today() + timedelta(days=15),
        priority=2,
        is_flexible=False,
    )
    snapshot = _make_snapshot(goals=[goal])
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    finding = RULE_REGISTRY["goal_at_risk"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["target_amount"] == "50000"
    assert finding.evidence["saved_amount"] == "10000"


def test_goal_at_risk_does_not_trigger_when_well_funded():
    goal = Goal(
        label="Emergency Trip",
        target_amount=Decimal("50000"),
        saved_amount=Decimal("45000"),
        target_date=date.today() + timedelta(days=15),
        priority=2,
        is_flexible=False,
    )
    snapshot = _make_snapshot(goals=[goal])
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert RULE_REGISTRY["goal_at_risk"].evaluate(ctx) is None


def test_goal_conflicts_obligation_triggers_when_contribution_breaches_obligations():
    goal = Goal(
        label="New Laptop",
        target_amount=Decimal("90000"),
        saved_amount=Decimal("0"),
        target_date=date.today() + timedelta(days=30),
        priority=3,
        is_flexible=True,
    )
    snapshot = _make_snapshot(
        cash=Decimal("95000"), obligations=[_obligation("Rent", "15000", 20)], goals=[goal]
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    finding = RULE_REGISTRY["goal_conflicts_obligation"].evaluate(ctx)
    assert finding is not None
    assert finding.evidence["obligations_due_30d"] == "15000"


def test_goal_conflicts_obligation_does_not_trigger_with_ample_cash():
    goal = Goal(
        label="New Laptop",
        target_amount=Decimal("90000"),
        saved_amount=Decimal("0"),
        target_date=date.today() + timedelta(days=30),
        priority=3,
        is_flexible=True,
    )
    snapshot = _make_snapshot(
        cash=Decimal("500000"), obligations=[_obligation("Rent", "15000", 20)], goals=[goal]
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert RULE_REGISTRY["goal_conflicts_obligation"].evaluate(ctx) is None


def test_evaluate_all_rules_returns_empty_on_safe_state():
    snapshot = _make_snapshot(
        obligations=[_obligation("Rent", "10000", 25)],
        income_forecast=_make_forecast(expected_arrival=date.today() + timedelta(days=10)),
    )
    ctx = RuleContext(snapshot=snapshot, simulation_result=None, recent_events=[])
    assert evaluate_all_rules(ctx) == []


# ---------------------------------------------------------------------------
# COLLISIONS
# ---------------------------------------------------------------------------


def _canonical_findings() -> list[RuleFinding]:
    return [
        _finding(
            "low_buffer",
            3,
            {"cash_available": "5000", "obligations_due_30d": "21800", "threshold": "32700.0"},
            "Your available cash (Rs.5,000.00) is below 1.5x your obligations due in the next 30 days (Rs.21,800.00).",
        ),
        _finding(
            "income_delayed",
            3,
            {"income_source": "ACME Freelance", "expected_arrival": "2026-09-27", "baseline_arrival": "2026-09-20", "days_late": 7},
            "ACME Freelance is now expected on 2026-09-27, 7 day(s) later than its usual pattern (2026-09-20).",
        ),
        _finding(
            "obligation_cluster",
            3,
            {"obligations": [{"label": "Rent", "amount": "15000"}, {"label": "EMI", "amount": "6800"}], "total_amount": "21800"},
            "2 fixed obligations totalling Rs.21,800.00 are due within 10 days of each other: Rent, EMI.",
        ),
    ]


async def _run_detect_with_canned_probabilities(
    db_session, snapshot, sim_result, findings, canned_probabilities: list[float]
):
    """Patches app.modules.risk.collision.simulate so the counterfactual
    probability for each successive call (one per simulatable finding, in
    order, plus one final "all removed" call) is fully controlled — this
    isolates detect_collisions' ALGORITHM (thresholds, deltas,
    amplification) from the real Monte Carlo engine's numeric behaviour,
    which is already covered by tests/test_simulation.py.
    """
    seen_seeds: list[int] = []
    canned_iter = iter(canned_probabilities)

    def _fake_simulate(inp):
        seen_seeds.append(inp.seed)
        prob = next(canned_iter)
        return _make_sim_result(prob, seed=inp.seed)

    original = collision_module.simulate
    collision_module.simulate = _fake_simulate
    try:
        collisions = await detect_collisions(db_session, snapshot.user_id, snapshot, sim_result, findings)
    finally:
        collision_module.simulate = original
    return collisions, seen_seeds


async def test_canonical_scenario_detected_as_collision(db_session):
    snapshot = _make_snapshot(
        cash=Decimal("5000"), obligations=[_obligation("Rent", "15000", 5), _obligation("EMI", "6800", 9)]
    )
    sim_result = _make_sim_result(0.45, seed=777)
    findings = _canonical_findings()

    # Call order matches findings order: low_buffer, income_delayed,
    # obligation_cluster, then one final "all removed" call.
    collisions, seen_seeds = await _run_detect_with_canned_probabilities(
        db_session, snapshot, sim_result, findings, [0.15, 0.40, 0.42, 0.05]
    )

    assert len(collisions) == 1
    collision = collisions[0]
    assert collision.condition_ids == sorted(["low_buffer", "income_delayed", "obligation_cluster"])
    assert collision.joint_probability == 0.45
    assert collision.amplification_factor > 1.0
    assert all(seed == 777 for seed in seen_seeds)


async def test_single_condition_is_not_a_collision(db_session):
    snapshot = _make_snapshot(cash=Decimal("5000"), obligations=[_obligation("Rent", "15000", 5)])
    sim_result = _make_sim_result(0.45)
    findings = [_canonical_findings()[0]]  # only low_buffer

    collisions, _ = await _run_detect_with_canned_probabilities(
        db_session, snapshot, sim_result, findings, [0.05]
    )
    assert collisions == []


async def test_joint_probability_below_threshold_is_not_a_collision(db_session):
    snapshot = _make_snapshot(
        cash=Decimal("5000"), obligations=[_obligation("Rent", "15000", 5), _obligation("EMI", "6800", 9)]
    )
    sim_result = _make_sim_result(0.20)  # below COLLISION_MIN_JOINT_PROBABILITY
    findings = _canonical_findings()

    collisions, _ = await _run_detect_with_canned_probabilities(
        db_session, snapshot, sim_result, findings, [0.05, 0.15, 0.18, 0.02]
    )
    assert collisions == []


async def test_margin_over_largest_individual_not_met_is_not_a_collision(db_session):
    snapshot = _make_snapshot(
        cash=Decimal("5000"), obligations=[_obligation("Rent", "15000", 5), _obligation("EMI", "6800", 9)]
    )
    sim_result = _make_sim_result(0.45)
    findings = _canonical_findings()

    # low_buffer alone (removed prob 0.05) nearly explains everything:
    # delta=0.40, margin = 0.45 - 0.40 = 0.05 < COLLISION_MIN_MARGIN_OVER_LARGEST.
    collisions, _ = await _run_detect_with_canned_probabilities(
        db_session, snapshot, sim_result, findings, [0.05, 0.44, 0.44, 0.05]
    )
    assert collisions == []


async def test_dominant_condition_produces_largest_probability_drop(db_session):
    snapshot = _make_snapshot(
        cash=Decimal("5000"), obligations=[_obligation("Rent", "15000", 5), _obligation("EMI", "6800", 9)]
    )
    sim_result = _make_sim_result(0.45)
    findings = _canonical_findings()

    collisions, _ = await _run_detect_with_canned_probabilities(
        db_session, snapshot, sim_result, findings, [0.15, 0.40, 0.42, 0.05]
    )
    assert len(collisions) == 1
    deltas = collisions[0].evidence["deltas"]
    assert max(deltas, key=lambda k: deltas[k]) == "low_buffer"


async def test_human_statement_contains_real_numbers_not_placeholders(db_session):
    snapshot = _make_snapshot(
        cash=Decimal("5000"), obligations=[_obligation("Rent", "15000", 5), _obligation("EMI", "6800", 9)]
    )
    sim_result = _make_sim_result(0.45)
    findings = _canonical_findings()

    collisions, _ = await _run_detect_with_canned_probabilities(
        db_session, snapshot, sim_result, findings, [0.15, 0.40, 0.42, 0.05]
    )
    statement = collisions[0].human_statement
    assert "21,800.00" in statement
    assert "ACME Freelance" in statement
    assert "45%" in statement
    assert "5%" in statement
    assert "{" not in statement and "}" not in statement


# ---------------------------------------------------------------------------
# SCORING
# ---------------------------------------------------------------------------


def test_confidence_acts_as_a_proportional_multiplier():
    kwargs = dict(
        probability=0.6, severity=4, urgency=5, amount_at_risk=Decimal("20000"), monthly_obligations=Decimal("40000")
    )
    high_conf = compute_risk_score(confidence=0.9, **kwargs)
    low_conf = compute_risk_score(confidence=0.5, **kwargs)
    assert high_conf.breakdown["raw_score_before_confidence"] == pytest.approx(
        low_conf.breakdown["raw_score_before_confidence"]
    )
    assert high_conf.score == pytest.approx(low_conf.score * (0.9 / 0.5))


def test_breakdown_allows_hand_reconstruction():
    result = compute_risk_score(
        probability=0.4,
        severity=3,
        urgency=7,
        confidence=0.8,
        amount_at_risk=Decimal("10000"),
        monthly_obligations=Decimal("30000"),
    )
    reconstructed_raw = (
        result.breakdown["probability_contribution"]
        + result.breakdown["severity_contribution"]
        + result.breakdown["urgency_contribution"]
        + result.breakdown["magnitude_contribution"]
    )
    assert reconstructed_raw == pytest.approx(result.breakdown["raw_score_before_confidence"])
    assert result.breakdown["raw_score_before_confidence"] * result.breakdown["confidence"] == pytest.approx(
        result.score
    )


def test_higher_probability_severity_urgency_magnitude_each_raise_score():
    base = compute_risk_score(
        probability=0.3, severity=2, urgency=20, confidence=1.0, amount_at_risk=Decimal("1000"), monthly_obligations=Decimal("50000")
    )
    higher_prob = compute_risk_score(
        probability=0.8, severity=2, urgency=20, confidence=1.0, amount_at_risk=Decimal("1000"), monthly_obligations=Decimal("50000")
    )
    higher_severity = compute_risk_score(
        probability=0.3, severity=5, urgency=20, confidence=1.0, amount_at_risk=Decimal("1000"), monthly_obligations=Decimal("50000")
    )
    higher_urgency = compute_risk_score(
        probability=0.3, severity=2, urgency=1, confidence=1.0, amount_at_risk=Decimal("1000"), monthly_obligations=Decimal("50000")
    )
    higher_magnitude = compute_risk_score(
        probability=0.3, severity=2, urgency=20, confidence=1.0, amount_at_risk=Decimal("40000"), monthly_obligations=Decimal("50000")
    )
    assert higher_prob.score > base.score
    assert higher_severity.score > base.score
    assert higher_urgency.score > base.score
    assert higher_magnitude.score > base.score


# ---------------------------------------------------------------------------
# LIFECYCLE
# ---------------------------------------------------------------------------


async def test_stale_collision_is_auto_resolved(db_session):
    user_id = uuid4()
    row = CollisionRecordRow(
        user_id=user_id,
        condition_ids=["low_buffer", "obligation_cluster"],
        joint_probability=0.4,
        individual_probabilities={"low_buffer": 0.1},
        amplification_factor=1.2,
        severity="high",
        urgency="medium",
        first_impact_date=None,
        evidence={},
        human_statement="stale",
    )
    db_session.add(row)
    await db_session.flush()

    await RiskService()._auto_resolve_stale_collisions(db_session, user_id, current_collisions=[])

    await db_session.refresh(row)
    assert row.resolved_at is not None
    assert row.resolution_reason == "conditions no longer hold"


async def test_dismissed_collision_does_not_reappear(db_session):
    user_id = uuid4()
    condition_ids = ["low_buffer", "income_delayed"]
    dismissed = CollisionRecordRow(
        user_id=user_id,
        condition_ids=condition_ids,
        joint_probability=0.4,
        individual_probabilities={},
        amplification_factor=1.1,
        severity="high",
        urgency="medium",
        first_impact_date=None,
        evidence={},
        human_statement="dismissed",
        resolved_at=datetime.now(timezone.utc),
        resolution_reason="user_dismissed: not applicable",
    )
    db_session.add(dismissed)
    await db_session.flush()

    new_collision = Collision(
        collision_id=uuid4(),
        condition_ids=condition_ids,
        joint_probability=0.5,
        individual_probabilities={},
        amplification_factor=1.3,
        severity="high",
        urgency="high",
        first_impact_date=None,
        evidence={},
        human_statement="recomputed",
    )
    await RiskService()._persist_new_collisions(db_session, user_id, [new_collision], simulation_run_id=None)

    from sqlalchemy import select

    result = await db_session.execute(select(CollisionRecordRow).where(CollisionRecordRow.user_id == user_id))
    rows = list(result.scalars())
    assert len(rows) == 1
    assert rows[0].id == dismissed.id
    assert rows[0].resolved_at is not None


# ---------------------------------------------------------------------------
# DISCOVERY
# ---------------------------------------------------------------------------


async def _seed_discovery_data(db_session, *, hit_count: int = 10, control_count: int = 6):
    hit_combo = ["low_buffer", "obligation_cluster"]
    now = datetime.now(timezone.utc)

    for _ in range(hit_count):
        user_id = uuid4()
        detected_at = now - timedelta(days=10)
        db_session.add(
            CollisionRecordRow(
                user_id=user_id,
                condition_ids=hit_combo,
                joint_probability=0.4,
                individual_probabilities={},
                amplification_factor=1.2,
                severity="high",
                urgency="medium",
                first_impact_date=None,
                evidence={},
                human_statement="x",
                detected_at=detected_at,
            )
        )
        db_session.add(
            ObligationRow(
                user_id=user_id,
                label="Rent",
                amount=Decimal("10000"),
                due_date=date.today() - timedelta(days=5),
                is_fixed=True,
                is_paid=False,
                data_source="manual",
                confidence_score=0.9,
            )
        )

    for _ in range(control_count):
        user_id = uuid4()
        db_session.add(
            CollisionRecordRow(
                user_id=user_id,
                condition_ids=["high_burn"],
                joint_probability=0.3,
                individual_probabilities={},
                amplification_factor=1.0,
                severity="medium",
                urgency="low",
                first_impact_date=None,
                evidence={},
                human_statement="x",
                detected_at=now - timedelta(days=10),
            )
        )

    await db_session.flush()
    return hit_combo


async def test_proposed_rules_always_created_with_pending_review_status(db_session):
    await _seed_discovery_data(db_session)

    proposed = await propose_rules(db_session, lookback_days=180)

    assert len(proposed) >= 1
    assert all(p.status == "pending_review" for p in proposed)

    from sqlalchemy import select

    result = await db_session.execute(select(ProposedRuleRecordRow))
    rows = list(result.scalars())
    assert len(rows) >= 1
    assert all(row.status == "pending_review" for row in rows)


async def test_proposed_rule_never_active_without_approval(db_session):
    await _seed_discovery_data(db_session)
    proposed = await propose_rules(db_session, lookback_days=180)
    assert len(proposed) >= 1

    for p in proposed:
        assert p.name not in RULE_REGISTRY

    from sqlalchemy import select

    result = await db_session.execute(
        select(ProposedRuleRecordRow).where(ProposedRuleRecordRow.status == "pending_review")
    )
    row = result.scalars().first()
    assert row is not None
    assert row.approved is False

    approved_row = await approve_proposed_rule(db_session, row.id, uuid4())
    assert approved_row is not None
    assert approved_row.status == "approved"
    assert approved_row.name not in RULE_REGISTRY  # approval is a DB flag, never a code deploy


async def test_discovery_without_llm_key_returns_statistical_candidates_without_crashing(db_session):
    combo = await _seed_discovery_data(db_session)

    settings = get_settings().model_copy(update={"GROQ_API_KEY": ""})
    proposed = await propose_rules(db_session, lookback_days=180, settings=settings)

    assert len(proposed) >= 1
    match = next(p for p in proposed if sorted(p.suggested_conditions) == sorted(combo))
    assert match.llm_rationale is None
    assert match.support >= 10
    assert match.lift >= 1.5


async def test_discovery_with_llm_key_phrases_candidate_via_mocked_llm(db_session):
    combo = await _seed_discovery_data(db_session)
    fake_response = json.dumps(
        {
            "name": "Rent Shortfall Combo",
            "description": "Low buffer plus a clustered obligation historically preceded a missed rent payment.",
            "proposed_threshold": {"min_joint_probability": 0.3},
            "rationale": "Support and lift both clear the statistical bar for a new rule.",
        }
    )
    proposed = await propose_rules(
        db_session, lookback_days=180, settings=_llm_settings_with_key(), http_client=_FakeGroqClient(fake_response)
    )

    match = next(p for p in proposed if sorted(p.suggested_conditions) == sorted(combo))
    assert match.name == "Rent Shortfall Combo"
    assert match.llm_rationale == "Support and lift both clear the statistical bar for a new rule."
    assert match.proposed_threshold == {"min_joint_probability": 0.3}
