"""The real Safe-to-Spend: how much can be spent right now while keeping
30-day shortfall risk under a risk-tolerance-specific threshold.

Replaces the naive Step 5 version (cash - obligations - emergency_fund,
floored at zero), which had no notion of probability at all.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from decimal import Decimal

from app.modules.simulation.engine import ObligationSpec, SimulationInput, simulate

RISK_TOLERANCE_THRESHOLDS: dict[str, float] = {
    "conservative": 0.05,
    "balanced": 0.15,
    "aggressive": 0.30,
}
DEFAULT_THRESHOLD = RISK_TOLERANCE_THRESHOLDS["balanced"]

BINARY_SEARCH_ITERATIONS = 12
EVALUATION_HORIZON_DAYS = 30


def _threshold_for(risk_tolerance: str) -> float:
    return RISK_TOLERANCE_THRESHOLDS.get(risk_tolerance, DEFAULT_THRESHOLD)


def _probability_at(result_probs: dict[int, float], horizon: int) -> float:
    if horizon in result_probs:
        return result_probs[horizon]
    nearest = min(result_probs, key=lambda h: abs(h - horizon))
    return result_probs[nearest]


@dataclass(frozen=True)
class SafeToSpendResult:
    amount: Decimal
    threshold_used: float
    risk_tolerance: str
    iterations: int
    final_shortfall_probability: float


def compute_safe_to_spend(base_input: SimulationInput, risk_tolerance: str) -> SafeToSpendResult:
    threshold = _threshold_for(risk_tolerance)

    lo = Decimal("0")
    hi = base_input.starting_cash
    last_prob = 0.0

    # CRITICAL: reuse the SAME seed (carried through unchanged by
    # dataclasses.replace) across every iteration. If each iteration drew
    # a fresh seed, we'd be comparing runs that differ by both the spend
    # amount AND independent random noise — the shortfall probability
    # could jump around non-monotonically even as spend increases, and
    # the binary search would never converge on a stable answer. Fixing
    # the seed makes spend amount the ONLY thing that changes between
    # iterations, which is what binary search requires to work at all.
    for _ in range(BINARY_SEARCH_ITERATIONS):
        mid = (lo + hi) / 2
        trial_input = dataclasses.replace(base_input, starting_cash=base_input.starting_cash - mid)
        result = simulate(trial_input)
        prob = _probability_at(result.shortfall_probability_by_horizon, EVALUATION_HORIZON_DAYS)
        last_prob = prob
        if prob <= threshold:
            lo = mid
        else:
            hi = mid

    return SafeToSpendResult(
        amount=lo,
        threshold_used=threshold,
        risk_tolerance=risk_tolerance,
        iterations=BINARY_SEARCH_ITERATIONS,
        final_shortfall_probability=last_prob,
    )


@dataclass(frozen=True)
class PurchaseVerdict:
    affordable: bool
    prob_before: float
    prob_after: float
    wait_days_recommended: int | None
    reasoning_values: dict[str, str | float]


def _find_earliest_affordable_day(
    base_input: SimulationInput, amount: Decimal, threshold: float, step_days: int = 7
) -> int:
    for day in range(0, base_input.horizon_days, step_days):
        deferred_purchase = ObligationSpec(label="deferred_purchase", amount=amount, day_offset=day)
        trial_input = dataclasses.replace(
            base_input, obligations=[*base_input.obligations, deferred_purchase]
        )
        result = simulate(trial_input)
        # Worst case across all reported checkpoints — deferring the
        # purchase shouldn't just look safe at 30 days while quietly
        # blowing the 90-day picture.
        worst_prob = max(result.shortfall_probability_by_horizon.values())
        if worst_prob <= threshold:
            return day
    return base_input.horizon_days


def evaluate_purchase(
    base_input: SimulationInput, amount: Decimal, risk_tolerance: str
) -> PurchaseVerdict:
    threshold = _threshold_for(risk_tolerance)

    before_result = simulate(base_input)
    prob_before = _probability_at(before_result.shortfall_probability_by_horizon, EVALUATION_HORIZON_DAYS)

    after_input = dataclasses.replace(base_input, starting_cash=base_input.starting_cash - amount)
    after_result = simulate(after_input)
    prob_after = _probability_at(after_result.shortfall_probability_by_horizon, EVALUATION_HORIZON_DAYS)

    affordable = prob_after <= threshold

    wait_days_recommended = None
    if not affordable:
        wait_days_recommended = _find_earliest_affordable_day(base_input, amount, threshold)

    return PurchaseVerdict(
        affordable=affordable,
        prob_before=prob_before,
        prob_after=prob_after,
        wait_days_recommended=wait_days_recommended,
        reasoning_values={"threshold": threshold, "amount": str(amount)},
    )
