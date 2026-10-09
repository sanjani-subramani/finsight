import dataclasses
import json
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
from hypothesis import given
from hypothesis import settings as hyp_settings
from hypothesis import strategies as st

from app.modules.simulation.distributions import DistributionSpec, fit_income_distribution
from app.modules.simulation.engine import (
    IncomeSpec,
    ObligationSpec,
    SimulationInput,
    compute_time_to_danger,
    simulate,
)
from app.modules.simulation.safe_to_spend import compute_safe_to_spend, evaluate_purchase
from app.modules.simulation.sensitivity import analyse_sensitivity
from app.modules.simulation.service import SimulationService, _serialize_input
from app.models.tables import SimulationRun
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


def _make_input(
    *,
    starting_cash=Decimal("10000.00"),
    income_mean=5000.0,
    income_std=500.0,
    expected_day=15,
    day_uncertainty_std=2.0,
    obligation_amount=Decimal("8000.00"),
    obligation_day=5,
    discretionary_mean=Decimal("100"),
    discretionary_std=Decimal("30"),
    horizon_days=30,
    scenarios=200,
    seed=42,
) -> SimulationInput:
    return SimulationInput(
        starting_cash=starting_cash,
        income_events=[
            IncomeSpec(
                label="Job",
                distribution=DistributionSpec(family="normal", params={"mean": income_mean, "std": income_std}),
                expected_day=expected_day,
                day_uncertainty_std=day_uncertainty_std,
            )
        ],
        obligations=[ObligationSpec(label="Rent", amount=obligation_amount, day_offset=obligation_day)],
        discretionary_daily_mean=discretionary_mean,
        discretionary_daily_std=discretionary_std,
        horizon_days=horizon_days,
        scenarios=scenarios,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# CORRECTNESS
# ---------------------------------------------------------------------------


def test_zero_uncertainty_produces_deterministic_hand_computed_result():
    inp = SimulationInput(
        starting_cash=Decimal("1000.00"),
        income_events=[
            IncomeSpec(
                label="Job",
                distribution=DistributionSpec(family="empirical", params={"values": [500.0]}),
                expected_day=10,
                day_uncertainty_std=0.0,
            )
        ],
        obligations=[ObligationSpec(label="Rent", amount=Decimal("800.00"), day_offset=5)],
        discretionary_daily_mean=Decimal("0"),
        discretionary_daily_std=Decimal("0"),
        horizon_days=30,
        scenarios=50,
        seed=1,
    )
    result = simulate(inp)
    # Hand calc: cash 1000; day5: -800 -> 200; day10: +500 -> 700; flat to day30.
    assert result.min_balance_p5 == Decimal("200.00")
    assert result.min_balance_p50 == Decimal("200.00")
    assert result.shortfall_probability_by_horizon[30] == 0.0


def test_more_obligations_than_cash_and_income_near_certain_shortfall():
    inp = SimulationInput(
        starting_cash=Decimal("100.00"),
        income_events=[
            IncomeSpec(
                label="Job",
                distribution=DistributionSpec(family="empirical", params={"values": [50.0]}),
                expected_day=20,
                day_uncertainty_std=1.0,
            )
        ],
        obligations=[ObligationSpec(label="Rent", amount=Decimal("5000.00"), day_offset=5)],
        discretionary_daily_mean=Decimal("0"),
        discretionary_daily_std=Decimal("0"),
        horizon_days=30,
        scenarios=500,
        seed=1,
    )
    result = simulate(inp)
    assert result.shortfall_probability_by_horizon[30] > 0.95


def test_huge_cash_buffer_near_zero_shortfall():
    inp = SimulationInput(
        starting_cash=Decimal("10000000.00"),
        income_events=[
            IncomeSpec(
                label="Job",
                distribution=DistributionSpec(family="normal", params={"mean": 5000.0, "std": 1000.0}),
                expected_day=15,
                day_uncertainty_std=3.0,
            )
        ],
        obligations=[ObligationSpec(label="Rent", amount=Decimal("8000.00"), day_offset=5)],
        discretionary_daily_mean=Decimal("300"),
        discretionary_daily_std=Decimal("100"),
        horizon_days=90,
        scenarios=500,
        seed=1,
    )
    result = simulate(inp)
    assert result.shortfall_probability_by_horizon[90] < 0.01


def test_shortfall_probability_always_in_unit_interval():
    inp = _make_input(scenarios=500)
    result = simulate(inp)
    for p in result.shortfall_probability_by_horizon.values():
        assert 0.0 <= p <= 1.0


def test_shortfall_probability_monotonic_in_horizon():
    inp = SimulationInput(
        starting_cash=Decimal("3000.00"),
        income_events=[
            IncomeSpec(
                label="Job",
                distribution=DistributionSpec(family="normal", params={"mean": 8000.0, "std": 1500.0}),
                expected_day=10,
                day_uncertainty_std=5.0,
            )
        ],
        obligations=[
            ObligationSpec(label="Rent1", amount=Decimal("7000.00"), day_offset=5),
            ObligationSpec(label="Rent2", amount=Decimal("7000.00"), day_offset=35),
            ObligationSpec(label="Rent3", amount=Decimal("7000.00"), day_offset=65),
        ],
        discretionary_daily_mean=Decimal("50"),
        discretionary_daily_std=Decimal("20"),
        horizon_days=90,
        scenarios=1000,
        seed=1,
    )
    result = simulate(inp)
    assert result.shortfall_probability_by_horizon[30] <= result.shortfall_probability_by_horizon[90]


# ---------------------------------------------------------------------------
# REPRODUCIBILITY
# ---------------------------------------------------------------------------


def test_same_seed_same_input_produces_identical_result():
    inp = _make_input(seed=99)
    r1 = simulate(inp)
    r2 = simulate(inp)
    assert r1.shortfall_probability_by_horizon == r2.shortfall_probability_by_horizon
    assert r1.min_balance_p5 == r2.min_balance_p5
    assert r1.min_balance_p50 == r2.min_balance_p50
    assert r1.balance_matrix_summary == r2.balance_matrix_summary


def test_different_seed_similar_but_not_identical():
    inp1 = _make_input(seed=1, scenarios=1000, day_uncertainty_std=3.0)
    inp2 = dataclasses.replace(inp1, seed=2)
    r1 = simulate(inp1)
    r2 = simulate(inp2)
    p1 = r1.shortfall_probability_by_horizon[30]
    p2 = r2.shortfall_probability_by_horizon[30]
    assert r1.balance_matrix_summary != r2.balance_matrix_summary
    assert abs(p1 - p2) <= 0.05  # within 5 percentage points at 1000 scenarios


async def test_replay_run_reproduces_stored_result_exactly(db_session):
    user_id = uuid4()
    inp = _make_input(seed=123, scenarios=500)
    result = simulate(inp)

    row = SimulationRun(
        user_id=user_id,
        scenarios=result.scenarios_run,
        horizon_days=inp.horizon_days,
        random_seed=inp.seed,
        shortfall_probability=result.shortfall_probability_by_horizon[inp.horizon_days],
        first_breach_date=None,
        worst_case_balance=result.min_balance_p5,
        time_to_danger_days=result.time_to_danger_days,
        safe_to_spend=Decimal("0.00"),
        inputs_snapshot=_serialize_input(inp),
        percentile_curve={
            "balance_matrix_summary": result.balance_matrix_summary,
            "shortfall_probability_by_horizon": {
                str(k): v for k, v in result.shortfall_probability_by_horizon.items()
            },
            "min_balance_p50": str(result.min_balance_p50),
            "first_breach_day_distribution": result.first_breach_day_distribution,
            "safe_to_spend_detail": {
                "amount": "0.00",
                "threshold_used": 0.15,
                "risk_tolerance": "balanced",
                "iterations": 12,
                "final_shortfall_probability": 0.0,
            },
            "sensitivity": [],
        },
        duration_ms=result.duration_ms,
    )
    db_session.add(row)
    await db_session.flush()

    replay = await SimulationService().replay_run(db_session, row.id)
    assert replay is not None
    assert replay.matches is True
    assert replay.original_probability == replay.replayed_probability


# ---------------------------------------------------------------------------
# MINIMUM VS ENDING BALANCE
# ---------------------------------------------------------------------------


def test_minimum_balance_dip_counted_even_if_ends_positive():
    inp = SimulationInput(
        starting_cash=Decimal("1000.00"),
        income_events=[
            IncomeSpec(
                label="Job",
                distribution=DistributionSpec(family="empirical", params={"values": [2000.0]}),
                expected_day=20,
                day_uncertainty_std=0.0,
            )
        ],
        obligations=[ObligationSpec(label="BigBill", amount=Decimal("1500.00"), day_offset=5)],
        discretionary_daily_mean=Decimal("0"),
        discretionary_daily_std=Decimal("0"),
        horizon_days=30,
        scenarios=10,
        seed=1,
    )
    result = simulate(inp)
    # day5: 1000-1500=-500 (negative dip); day20: -500+2000=1500 (ends positive).
    assert result.min_balance_p50 == Decimal("-500.00")
    assert result.shortfall_probability_by_horizon[30] == 1.0


# ---------------------------------------------------------------------------
# TIME TO DANGER
# ---------------------------------------------------------------------------


def test_time_to_danger_returns_known_crossing_day():
    inp = SimulationInput(
        starting_cash=Decimal("100.00"),
        income_events=[],
        obligations=[ObligationSpec(label="Bill", amount=Decimal("500.00"), day_offset=4)],
        discretionary_daily_mean=Decimal("0"),
        discretionary_daily_std=Decimal("0"),
        horizon_days=30,
        scenarios=50,
        seed=1,
    )
    result = simulate(inp)
    # day_offset=4 (0-indexed) is calendar day 5; compute_time_to_danger is 1-indexed.
    assert result.time_to_danger_days == 5


def test_safe_case_returns_none_time_to_danger():
    inp = SimulationInput(
        starting_cash=Decimal("10000000.00"),
        income_events=[
            IncomeSpec(
                label="Job",
                distribution=DistributionSpec(family="normal", params={"mean": 5000.0, "std": 500.0}),
                expected_day=15,
                day_uncertainty_std=2.0,
            )
        ],
        obligations=[ObligationSpec(label="Rent", amount=Decimal("8000.00"), day_offset=5)],
        discretionary_daily_mean=Decimal("200"),
        discretionary_daily_std=Decimal("50"),
        horizon_days=90,
        scenarios=500,
        seed=1,
    )
    result = simulate(inp)
    assert result.time_to_danger_days is None


def test_compute_time_to_danger_directly_on_known_matrix():
    import numpy as np

    balances = np.array([[10.0, -5.0, -5.0], [10.0, 10.0, -5.0], [10.0, 10.0, 10.0], [10.0, -5.0, -5.0]])
    # day0: 0/4 negative; day1: 2/4 negative (0.5, crosses threshold); day2: 3/4 negative.
    assert compute_time_to_danger(balances, threshold=0.5) == 2


# ---------------------------------------------------------------------------
# SAFE TO SPEND
# ---------------------------------------------------------------------------


def _rich_input(seed=5, scenarios=1000, horizon_days=90) -> SimulationInput:
    inp = _make_input(
        starting_cash=Decimal("50000.00"),
        income_mean=20000.0,
        income_std=2000.0,
        obligation_amount=Decimal("15000.00"),
        discretionary_mean=Decimal("300"),
        discretionary_std=Decimal("100"),
        horizon_days=horizon_days,
        scenarios=scenarios,
        seed=seed,
    )
    return inp


def test_safe_to_spend_binary_search_converges():
    inp = _rich_input()
    result = compute_safe_to_spend(inp, "balanced")
    assert Decimal("0") <= result.amount <= inp.starting_cash
    assert result.iterations == 12


def test_spending_exactly_safe_to_spend_keeps_probability_at_or_under_threshold():
    inp = _rich_input()
    sts = compute_safe_to_spend(inp, "balanced")
    trial = dataclasses.replace(inp, starting_cash=inp.starting_cash - sts.amount)
    result = simulate(trial)
    prob = result.shortfall_probability_by_horizon.get(30, result.shortfall_probability_by_horizon[inp.horizon_days])
    # Small tolerance: binary search converges to *near* the threshold,
    # not exactly at it, in finitely many iterations over noisy scenarios.
    assert prob <= sts.threshold_used + 0.03


def test_spending_more_than_safe_to_spend_pushes_probability_over():
    inp = _rich_input()
    sts = compute_safe_to_spend(inp, "balanced")
    over_amount = sts.amount + (inp.starting_cash - sts.amount) * Decimal("0.5")
    trial = dataclasses.replace(inp, starting_cash=inp.starting_cash - over_amount)
    result = simulate(trial)
    prob = result.shortfall_probability_by_horizon.get(30, result.shortfall_probability_by_horizon[inp.horizon_days])
    assert prob > sts.threshold_used


def test_conservative_yields_lower_safe_to_spend_than_aggressive():
    inp = _rich_input()
    conservative = compute_safe_to_spend(inp, "conservative")
    aggressive = compute_safe_to_spend(inp, "aggressive")
    assert conservative.amount <= aggressive.amount


# ---------------------------------------------------------------------------
# PURCHASE
# ---------------------------------------------------------------------------


def test_affordable_purchase_returns_true():
    inp = _rich_input(scenarios=500)
    inp = dataclasses.replace(inp, starting_cash=Decimal("100000.00"))
    verdict = evaluate_purchase(inp, Decimal("500"), "balanced")
    assert verdict.affordable is True
    assert verdict.wait_days_recommended is None


def test_unaffordable_purchase_returns_sensible_wait_days():
    inp = _rich_input(scenarios=500)
    inp = dataclasses.replace(inp, starting_cash=Decimal("9000.00"))
    verdict = evaluate_purchase(inp, Decimal("8500"), "conservative")
    assert verdict.affordable is False
    assert verdict.wait_days_recommended is not None
    assert 0 <= verdict.wait_days_recommended <= inp.horizon_days


# ---------------------------------------------------------------------------
# SENSITIVITY
# ---------------------------------------------------------------------------


def test_top_sensitivity_factor_has_largest_delta():
    inp = SimulationInput(
        starting_cash=Decimal("2000.00"),
        income_events=[
            IncomeSpec(
                label="ACME",
                distribution=DistributionSpec(family="normal", params={"mean": 20000.0, "std": 1000.0}),
                expected_day=10,
                day_uncertainty_std=15.0,
            )
        ],
        obligations=[
            ObligationSpec(label="Rent", amount=Decimal("15000.00"), day_offset=25, is_flexible=False),
            ObligationSpec(label="Gym", amount=Decimal("2000.00"), day_offset=10, is_flexible=True),
        ],
        discretionary_daily_mean=Decimal("200"),
        discretionary_daily_std=Decimal("50"),
        horizon_days=60,
        scenarios=1000,
        seed=3,
    )
    result = simulate(inp)
    factors = analyse_sensitivity(inp, result)
    assert len(factors) >= 2
    deltas = [f.delta for f in factors]
    assert deltas == sorted(deltas, reverse=True)


def test_on_time_income_reduces_probability_in_late_payment_scenario():
    # Obligation due AFTER the expected income day, with high timing
    # uncertainty, so late arrivals commonly miss it — making "on time"
    # unambiguously helpful (as opposed to a case where the obligation
    # precedes the expected day, where removing timing spread can also
    # remove lucky early arrivals).
    inp = SimulationInput(
        starting_cash=Decimal("2000.00"),
        income_events=[
            IncomeSpec(
                label="ACME",
                distribution=DistributionSpec(family="normal", params={"mean": 20000.0, "std": 1000.0}),
                expected_day=10,
                day_uncertainty_std=15.0,
            )
        ],
        obligations=[ObligationSpec(label="Rent", amount=Decimal("15000.00"), day_offset=25, is_flexible=False)],
        discretionary_daily_mean=Decimal("0"),
        discretionary_daily_std=Decimal("0"),
        horizon_days=60,
        scenarios=1000,
        seed=3,
    )
    result = simulate(inp)
    factors = analyse_sensitivity(inp, result)
    on_time_factor = next(f for f in factors if f.name == "ACME_on_time")
    assert on_time_factor.delta > 0
    assert on_time_factor.prob_after < on_time_factor.prob_before


# ---------------------------------------------------------------------------
# DISTRIBUTIONS
# ---------------------------------------------------------------------------


async def test_three_observations_empirical_no_llm_called():
    mock_client = AsyncMock()
    spec = await fit_income_distribution(
        [Decimal("20000"), Decimal("21000"), Decimal("19500")],
        settings=_llm_settings_with_key(),
        http_client=mock_client,
    )
    assert spec.family == "empirical"
    assert spec.method == "insufficient_data"
    mock_client.post.assert_not_called()


async def test_clearly_skewed_data_fits_lognormal():
    skewed = [Decimal(str(v)) for v in [18000, 19000, 18500, 20000, 17500, 19200, 95000, 18800]]
    spec = await fit_income_distribution(skewed)
    assert spec.family == "lognormal"


async def test_clearly_normal_data_fits_normal():
    normal_vals = [Decimal(str(v)) for v in [20000, 20500, 19800, 20200, 19900, 20100, 20300, 19700]]
    spec = await fit_income_distribution(normal_vals)
    assert spec.family == "normal"


async def test_ambiguous_band_uses_llm_when_configured():
    fake_client = _FakeGroqClient(json.dumps({"family": "lognormal", "reasoning": "slightly skewed"}))
    ambiguous_vals = [Decimal(str(v)) for v in [21594, 21490, 21158, 22710, 22899, 20742]]
    spec = await fit_income_distribution(
        ambiguous_vals, settings=_llm_settings_with_key(), http_client=fake_client
    )
    assert spec.method == "llm"
    assert spec.family == "lognormal"


async def test_no_llm_key_ambiguous_band_falls_back_to_empirical_without_error():
    ambiguous_vals = [Decimal(str(v)) for v in [21594, 21490, 21158, 22710, 22899, 20742]]
    spec = await fit_income_distribution(ambiguous_vals)  # default settings -> no GROQ key here
    assert spec.family == "empirical"
    assert spec.method == "llm_unavailable"


# ---------------------------------------------------------------------------
# PERFORMANCE
# ---------------------------------------------------------------------------


def test_1000_scenarios_90_days_completes_under_100ms():
    inp = _make_input(scenarios=1000, horizon_days=90)
    result = simulate(inp)
    assert result.duration_ms < 100


# ---------------------------------------------------------------------------
# PROPERTY (hypothesis)
# ---------------------------------------------------------------------------


@given(
    starting_cash=st.decimals(min_value=Decimal("0"), max_value=Decimal("1000000"), places=2, allow_nan=False),
    income_mean=st.floats(min_value=0, max_value=100_000, allow_nan=False),
    obligation_amount=st.decimals(min_value=Decimal("0"), max_value=Decimal("50000"), places=2, allow_nan=False),
    scenarios=st.integers(min_value=50, max_value=300),
    horizon_days=st.integers(min_value=7, max_value=90),
    seed=st.integers(min_value=0, max_value=2**31 - 1),
)
@hyp_settings(deadline=None, max_examples=30)
def test_property_probability_bounds_and_result_metadata(
    starting_cash, income_mean, obligation_amount, scenarios, horizon_days, seed
):
    inp = SimulationInput(
        starting_cash=starting_cash,
        income_events=[
            IncomeSpec(
                label="Job",
                distribution=DistributionSpec(
                    family="normal", params={"mean": income_mean, "std": max(income_mean * 0.1, 1.0)}
                ),
                expected_day=horizon_days // 2,
                day_uncertainty_std=2.0,
            )
        ],
        obligations=[ObligationSpec(label="Bill", amount=obligation_amount, day_offset=min(5, horizon_days - 1))],
        discretionary_daily_mean=Decimal("10"),
        discretionary_daily_std=Decimal("5"),
        horizon_days=horizon_days,
        scenarios=scenarios,
        seed=seed,
    )
    result = simulate(inp)

    for p in result.shortfall_probability_by_horizon.values():
        assert 0.0 <= p <= 1.0
    assert result.duration_ms > 0
    assert result.scenarios_run == scenarios
