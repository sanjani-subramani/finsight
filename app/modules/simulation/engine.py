"""The Monte Carlo simulation core.

PURE FUNCTION, NO I/O: simulate() touches nothing but numpy arrays
derived from its own input. No DB, no network, no clock (the caller
supplies the seed). This is what makes it trivially testable — same
input always produces the same output — and safe to call from a hot
request path without worrying about side effects.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import numpy as np

from app.modules.simulation.distributions import DistributionSpec, sample_income

# Fixed checkpoints we always report shortfall probability at, filtered
# to whatever fits inside the actual horizon (plus the horizon itself).
_STANDARD_HORIZON_CHECKPOINTS = (7, 14, 30, 60, 90)


@dataclass(frozen=True)
class IncomeSpec:
    label: str
    distribution: DistributionSpec
    expected_day: int  # day offset from simulation start (0-indexed)
    day_uncertainty_std: float  # std dev of the arrival day, in days


@dataclass(frozen=True)
class ObligationSpec:
    label: str
    amount: Decimal
    day_offset: int  # deterministic due day, same in every scenario
    is_flexible: bool = False  # can this obligation realistically be skipped/deferred?


@dataclass(frozen=True)
class SimulationInput:
    starting_cash: Decimal
    income_events: list[IncomeSpec]
    obligations: list[ObligationSpec]
    discretionary_daily_mean: Decimal
    discretionary_daily_std: Decimal
    horizon_days: int
    scenarios: int
    seed: int


@dataclass(frozen=True)
class SimulationResult:
    balance_matrix_summary: dict[str, Any]  # percentile curves, NOT the full matrix
    shortfall_probability_by_horizon: dict[int, float]
    min_balance_p5: Decimal
    min_balance_p50: Decimal
    first_breach_day_distribution: dict[str, Any]
    time_to_danger_days: int | None
    scenarios_run: int
    seed: int
    duration_ms: int


def _horizon_checkpoints(horizon_days: int) -> list[int]:
    checkpoints = {d for d in _STANDARD_HORIZON_CHECKPOINTS if d <= horizon_days}
    checkpoints.add(horizon_days)
    return sorted(checkpoints)


def compute_time_to_danger(balances: np.ndarray, threshold: float = 0.5) -> int | None:
    """TIME-TO-DANGER: for each day d, P(minimum balance from day 0
    through day d < 0) across all scenarios. Returns the first day that
    probability crosses `threshold`, or None if it never does.

    This converts an abstract probability ("14% shortfall risk") into a
    deadline ("by day 23 you have a coin-flip chance of going negative")
    — which is what people actually act on. A percentage is easy to
    shrug off; a date is not.
    """
    running_min = np.minimum.accumulate(balances, axis=1)
    prob_breached_by_day = (running_min < 0).mean(axis=0)
    crossing = np.where(prob_breached_by_day >= threshold)[0]
    if crossing.size == 0:
        return None
    return int(crossing[0]) + 1  # 1-indexed: "day 1" is tomorrow, not today


def _first_breach_day(balances: np.ndarray) -> np.ndarray:
    negative = balances < 0
    has_breach = negative.any(axis=1)
    first_day = np.argmax(negative, axis=1)  # 0 for rows with no True at all
    return np.where(has_breach, first_day, -1)


def simulate(inp: SimulationInput) -> SimulationResult:
    start = time.perf_counter()
    rng = np.random.default_rng(inp.seed)  # modern Generator API, fully seeded/reproducible

    scenarios, days = inp.scenarios, inp.horizon_days
    net_flow = np.zeros((scenarios, days), dtype=np.float64)

    # --- Income: amount AND arrival day sampled independently ---------
    # A client's PAYMENT AMOUNT and how LATE they run are different,
    # largely unrelated risks — someone who always pays the full amount
    # but is erratic about timing needs a different response than someone
    # reliable on timing but unpredictable on amount. Modelling them with
    # two independent draws (rather than one combined "risk score")
    # keeps that distinction visible all the way through the simulation.
    for income in inp.income_events:
        amounts = sample_income(rng, income.distribution, scenarios)
        arrival_days = np.round(
            rng.normal(income.expected_day, max(income.day_uncertainty_std, 0.0), size=scenarios)
        ).astype(np.int64)
        arrival_days = np.clip(arrival_days, 0, days - 1)
        # Scatter each scenario's income into ITS OWN arrival day without
        # a Python loop over scenarios: fancy-index the (scenario, day)
        # coordinate pairs directly. np.add.at is required (not `+=`)
        # because multiple scenarios can land on the same day, and a
        # plain indexed `+=` would silently drop all but one of them.
        np.add.at(net_flow, (np.arange(scenarios), arrival_days), amounts)

    # --- Obligations: deterministic, same day and amount in every scenario ---
    for obligation in inp.obligations:
        day = min(max(obligation.day_offset, 0), days - 1)
        net_flow[:, day] -= float(obligation.amount)

    # --- Discretionary spending: random per scenario per day, clipped at 0 ---
    discretionary = rng.normal(
        float(inp.discretionary_daily_mean),
        max(float(inp.discretionary_daily_std), 0.0),
        size=(scenarios, days),
    )
    discretionary = np.clip(discretionary, 0, None)  # spending cannot be negative
    net_flow -= discretionary

    # PERFORMANCE: everything above and below is array math over the
    # whole (scenarios, days) matrix at once. A nested Python loop —
    # `for s in range(scenarios): for d in range(days): ...` — over 1000
    # scenarios x 90 days would run ~90,000 iterations of interpreted
    # Python and take seconds; the vectorized numpy version below does
    # the equivalent work in compiled C loops and takes on the order of
    # 10ms. That difference is what makes GET /simulation/run feel like a
    # normal API call instead of a "please wait" spinner.
    balances = float(inp.starting_cash) + np.cumsum(net_flow, axis=1)

    # We test the MINIMUM balance across each window, not the ending
    # balance: bouncing rent on day 12 is a real failure even if the
    # month ends positive again by day 30. An ending-balance check would
    # miss exactly the failure mode this simulation exists to catch.
    shortfall_by_horizon: dict[int, float] = {}
    for h in _horizon_checkpoints(days):
        shortfall_by_horizon[h] = float((balances[:, :h].min(axis=1) < 0).mean())

    min_balances = balances.min(axis=1)
    percentiles = np.percentile(balances, [5, 25, 50, 75, 95], axis=0)

    time_to_danger = compute_time_to_danger(balances)

    first_breach = _first_breach_day(balances)
    breached = first_breach[first_breach >= 0]
    first_breach_distribution: dict[str, Any] = {
        "count_breached": int(breached.size),
        "count_never_breached": int(scenarios - breached.size),
    }
    if breached.size > 0:
        breach_percentiles = np.percentile(breached, [10, 25, 50, 75, 90])
        first_breach_distribution["percentiles"] = {
            "p10": float(breach_percentiles[0]),
            "p25": float(breach_percentiles[1]),
            "p50": float(breach_percentiles[2]),
            "p75": float(breach_percentiles[3]),
            "p90": float(breach_percentiles[4]),
        }

    # Floored at 1: a duration metric reading literally "0" is misleading
    # even for a genuinely sub-millisecond run — round up rather than
    # imply the work took no measurable time at all.
    duration_ms = max(1, int((time.perf_counter() - start) * 1000))

    return SimulationResult(
        balance_matrix_summary={
            "days": list(range(days)),
            "p5": percentiles[0].round(2).tolist(),
            "p25": percentiles[1].round(2).tolist(),
            "p50": percentiles[2].round(2).tolist(),
            "p75": percentiles[3].round(2).tolist(),
            "p95": percentiles[4].round(2).tolist(),
        },
        shortfall_probability_by_horizon=shortfall_by_horizon,
        min_balance_p5=Decimal(str(round(float(np.percentile(min_balances, 5)), 2))),
        min_balance_p50=Decimal(str(round(float(np.percentile(min_balances, 50)), 2))),
        first_breach_day_distribution=first_breach_distribution,
        time_to_danger_days=time_to_danger,
        scenarios_run=scenarios,
        seed=inp.seed,
        duration_ms=duration_ms,
    )
