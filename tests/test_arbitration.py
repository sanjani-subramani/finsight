from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

from app.contracts.events import FinancialStateSnapshot, FinancialWeather, Goal, IncomeForecast, Obligation
from app.models.tables import User
from app.modules.decision.actions import build_recommended_actions
from app.modules.decision.arbitration import ArbitrationResult, Claim, arbitrate
from app.modules.decision.policy import EMERGENCY_FUND_ABSOLUTE_FLOOR, ClaimTier, reduction_order
from app.modules.simulation.engine import SimulationResult

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------


def _obligation(label: str, amount: str, due_in_days: int, *, category: str | None, is_fixed: bool = True) -> Obligation:
    return Obligation(
        obligation_id=uuid4(),
        label=label,
        amount=Decimal(amount),
        due_date=date.today() + timedelta(days=due_in_days),
        category=category,
        is_fixed=is_fixed,
        is_paid=False,
        confidence_score=0.9,
    )


def _goal(label: str, target_amount: str, *, saved_amount: str = "0", is_flexible: bool = True) -> Goal:
    return Goal(
        goal_id=uuid4(),
        label=label,
        target_amount=Decimal(target_amount),
        saved_amount=Decimal(saved_amount),
        target_date=date.today() + timedelta(days=30),
        priority=3,
        is_flexible=is_flexible,
    )


def _snapshot(
    *,
    cash: Decimal,
    obligations: list[Obligation] | None = None,
    goals: list[Goal] | None = None,
    emergency_fund: Decimal = Decimal("999999"),  # high by default: no synthetic buffer claim unless a test wants one
) -> FinancialStateSnapshot:
    return FinancialStateSnapshot(
        user_id=uuid4(),
        cash_available=cash,
        emergency_fund=emergency_fund,
        income_forecast=IncomeForecast(source="declared", confidence_score=0.7),
        obligations=obligations or [],
        goals=goals or [],
        weather=FinancialWeather.risk,
        safe_to_spend=Decimal("0"),
        state_confidence=0.9,
    )


def _sim_result(probability: float, *, horizon: int = 90, seed: int = 777, scenarios_run: int = 200) -> SimulationResult:
    return SimulationResult(
        balance_matrix_summary={},
        shortfall_probability_by_horizon={horizon: probability},
        min_balance_p5=Decimal("0"),
        min_balance_p50=Decimal("0"),
        first_breach_day_distribution={},
        time_to_danger_days=None,
        scenarios_run=scenarios_run,
        seed=seed,
        duration_ms=1,
    )


async def _make_user(db_session, *, risk_tolerance: str = "balanced") -> User:
    user = User(id=uuid4(), email=f"{uuid4()}@example.com", password_hash="hash", risk_tolerance=risk_tolerance)
    db_session.add(user)
    await db_session.flush()
    return user


def _canned_simulate(probability: float, horizon: int = 90):
    def _fake(inp):
        return _sim_result(probability, horizon=horizon, seed=inp.seed, scenarios_run=inp.scenarios)

    return _fake


# ---------------------------------------------------------------------------
# TIER ORDERING
# ---------------------------------------------------------------------------


async def test_rent_tier1_always_funded_before_sip_tier4(db_session):
    user = await _make_user(db_session)
    rent = _obligation("Rent", "8000", 5, category="rent")
    sip = _goal("SIP contribution", "4000")
    snapshot = _snapshot(cash=Decimal("9000"), obligations=[rent], goals=[sip])
    sim_result = _sim_result(0.5)

    with patch("app.modules.decision.arbitration.simulate", side_effect=_canned_simulate(0.5)):
        result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert result.allocations[f"obligation:{rent.obligation_id}"] == Decimal("8000")
    assert result.allocations[f"goal:{sip.goal_id}"] < Decimal("4000")


async def test_emi_tier2_funded_before_emergency_topup_tier3(db_session):
    user = await _make_user(db_session)
    emi = _obligation("Car EMI", "6000", 5, category="emi")
    snapshot = _snapshot(cash=Decimal("7000"), obligations=[emi], emergency_fund=Decimal("0"))
    sim_result = _sim_result(0.5)

    with patch("app.modules.decision.arbitration.simulate", side_effect=_canned_simulate(0.5)):
        result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert result.allocations[f"obligation:{emi.obligation_id}"] == Decimal("6000")
    assert result.allocations["buffer:topup"] < Decimal("2000")


async def test_emergency_fund_never_taken_below_absolute_floor(db_session):
    user = await _make_user(db_session, risk_tolerance="aggressive")
    rent = _obligation("Rent", "12000", 3, category="rent")
    snapshot = _snapshot(cash=Decimal("1000"), obligations=[rent], emergency_fund=Decimal("20000"))
    sim_result = _sim_result(0.8)

    with patch("app.modules.decision.arbitration.simulate", side_effect=_canned_simulate(0.1)):
        result = await arbitrate(db_session, user.id, snapshot, sim_result)

    drawn = result.reductions.get("buffer:emergency_fund_drawdown", Decimal("0"))
    assert snapshot.emergency_fund - drawn >= EMERGENCY_FUND_ABSOLUTE_FLOOR


async def test_no_reductions_when_cash_covers_everything(db_session):
    user = await _make_user(db_session)
    rent = _obligation("Rent", "8000", 5, category="rent")
    sip = _goal("SIP contribution", "4000")
    snapshot = _snapshot(cash=Decimal("50000"), obligations=[rent], goals=[sip])
    sim_result = _sim_result(0.1)

    result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert result.reductions == {}
    assert result.unfunded == []
    assert result.prob_after == result.prob_before


async def test_lowest_tier_reduced_first_when_cash_is_short(db_session):
    user = await _make_user(db_session)
    rent = _obligation("Rent", "8000", 5, category="rent")
    sip = _goal("SIP contribution", "4000")
    vacation = _goal("Vacation fund", "10000")
    snapshot = _snapshot(cash=Decimal("10000"), obligations=[rent], goals=[sip, vacation])
    sim_result = _sim_result(0.5)

    with patch("app.modules.decision.arbitration.simulate", side_effect=_canned_simulate(0.5)):
        result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert result.allocations[f"obligation:{rent.obligation_id}"] == Decimal("8000")
    assert result.allocations[f"goal:{vacation.goal_id}"] == Decimal("0")  # DISCRETIONARY: cut first


async def test_canonical_case_vacation_deferred_sip_reduced_rent_intact(db_session):
    user = await _make_user(db_session)
    rent = _obligation("Rent", "8000", 5, category="rent")
    sip = _goal("SIP contribution", "4000")
    vacation = _goal("Vacation fund", "10000")
    snapshot = _snapshot(cash=Decimal("10000"), obligations=[rent], goals=[sip, vacation])
    sim_result = _sim_result(0.5)

    result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert result.allocations[f"obligation:{rent.obligation_id}"] == Decimal("8000")
    assert result.allocations[f"goal:{sip.goal_id}"] == Decimal("2000")
    assert result.allocations[f"goal:{vacation.goal_id}"] == Decimal("0")
    assert sip.label in result.unfunded


# ---------------------------------------------------------------------------
# VERIFICATION
# ---------------------------------------------------------------------------


async def test_non_improving_proposal_is_discarded(db_session):
    user = await _make_user(db_session, risk_tolerance="aggressive")
    rent = _obligation("Rent", "12000", 3, category="rent")
    snapshot = _snapshot(cash=Decimal("1000"), obligations=[rent], emergency_fund=Decimal("20000"))
    sim_result = _sim_result(0.5)

    # simulate() always reports the SAME (not-improved) probability no
    # matter the proposed allocation -- every candidate must be discarded.
    with patch("app.modules.decision.arbitration.simulate", side_effect=_canned_simulate(0.5)):
        result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert result.alternatives == []
    assert result.reductions == {}
    assert result.prob_after == result.prob_before


async def test_projected_risk_after_comes_from_a_real_resimulation(db_session):
    user = await _make_user(db_session, risk_tolerance="aggressive")
    rent = _obligation("Rent", "12000", 3, category="rent")
    snapshot = _snapshot(cash=Decimal("1000"), obligations=[rent], emergency_fund=Decimal("20000"))
    sim_result = _sim_result(0.8)

    call_count = 0

    def _spy(inp):
        nonlocal call_count
        call_count += 1
        return _sim_result(0.1, seed=inp.seed, scenarios_run=inp.scenarios)

    with patch("app.modules.decision.arbitration.simulate", side_effect=_spy):
        result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert call_count > 0
    assert result.prob_after == 0.1  # the actual value the (mocked) simulation returned, not an estimate


async def test_alternatives_have_distinct_allocations_and_verified_outcomes(db_session):
    user = await _make_user(db_session)
    rent = _obligation("Rent", "12000", 3, category="rent")
    snapshot = _snapshot(cash=Decimal("1000"), obligations=[rent], emergency_fund=Decimal("15000"))
    sim_result = _sim_result(0.8)

    with patch("app.modules.decision.arbitration.simulate", side_effect=_canned_simulate(0.1)):
        result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert len(result.alternatives) >= 2
    seen_allocations = [tuple(sorted(alt.allocations.items())) for alt in result.alternatives]
    assert len(set(seen_allocations)) == len(seen_allocations)  # all distinct
    for alt in result.alternatives:
        assert alt.prob_after < result.prob_before


# ---------------------------------------------------------------------------
# RISK TOLERANCE
# ---------------------------------------------------------------------------


def test_conservative_prefers_buffer_over_growth_aggressive_reverses():
    conservative = reduction_order("conservative")
    aggressive = reduction_order("aggressive")

    assert conservative.index(ClaimTier.GROWTH) < conservative.index(ClaimTier.BUFFER)
    assert aggressive.index(ClaimTier.BUFFER) < aggressive.index(ClaimTier.GROWTH)


# ---------------------------------------------------------------------------
# TRADE-OFF STATEMENT
# ---------------------------------------------------------------------------


async def test_trade_off_statement_contains_real_numbers_no_placeholders(db_session):
    user = await _make_user(db_session, risk_tolerance="aggressive")
    rent = _obligation("Rent", "12000", 3, category="rent")
    snapshot = _snapshot(cash=Decimal("1000"), obligations=[rent], emergency_fund=Decimal("20000"))
    sim_result = _sim_result(0.8)

    with patch("app.modules.decision.arbitration.simulate", side_effect=_canned_simulate(0.1)):
        result = await arbitrate(db_session, user.id, snapshot, sim_result)

    assert "{" not in result.trade_off_statement and "}" not in result.trade_off_statement
    assert "80%" in result.trade_off_statement
    assert "10%" in result.trade_off_statement


# ---------------------------------------------------------------------------
# ACTIONS MAPPING
# ---------------------------------------------------------------------------


def test_build_recommended_actions_uses_verified_projected_risk():
    sip_claim = Claim(
        claim_id="goal:sip-1", label="SIP contribution", tier=ClaimTier.GROWTH,
        amount=Decimal("4000"), due_date=None, source="goal",
    )
    result = ArbitrationResult(
        claims=[sip_claim],
        allocations={"goal:sip-1": Decimal("2000")},
        reductions={"goal:sip-1": Decimal("2000"), "buffer:emergency_fund_drawdown": Decimal("1500")},
        unfunded=[],
        prob_before=0.4,
        prob_after=0.11,
        trade_off_statement="x",
    )

    actions = build_recommended_actions(result)

    assert len(actions) == 2
    sip_action = next(a for a in actions if a.action_type == "reduce_sip")
    assert sip_action.amount == Decimal("2000")
    assert sip_action.projected_risk_after == 0.11
    assert "2,000" in sip_action.label

    buffer_action = next(a for a in actions if a.action_type == "move_from_emergency_fund")
    assert buffer_action.amount == Decimal("1500")
    assert buffer_action.projected_risk_after == 0.11
