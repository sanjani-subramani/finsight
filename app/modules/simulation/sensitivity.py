"""Sensitivity analysis: which single input matters most to the current
shortfall risk?

This is what turns a probability into an action. "14% shortfall risk" is
just a number a user can't do anything with; "your ACME payment arriving
by day 8 removes this risk entirely" tells them exactly what to watch
for or chase up.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from decimal import Decimal

import numpy as np

from app.modules.simulation.distributions import DistributionSpec
from app.modules.simulation.engine import SimulationInput, SimulationResult, simulate

EVALUATION_HORIZON_DAYS = 30
DISCRETIONARY_REDUCTION_FACTOR = 0.75  # 25% cut
# When probing "what if this income arrived at its optimistic (p90)
# level," we also shrink its spread so the probe genuinely represents
# "consistently getting the good outcome," not just a wider distribution
# recentred — otherwise the probe wouldn't isolate the effect of amount
# from the effect of remaining uncertainty.
P90_PROBE_SPREAD_FACTOR = 0.1
Z_SCORE_90TH_PERCENTILE = 1.2816


def _probability_at(result: SimulationResult, horizon: int = EVALUATION_HORIZON_DAYS) -> float:
    probs = result.shortfall_probability_by_horizon
    if horizon in probs:
        return probs[horizon]
    nearest = min(probs, key=lambda h: abs(h - horizon))
    return probs[nearest]


@dataclass(frozen=True)
class SensitivityFactor:
    name: str
    description: str
    prob_before: float
    prob_after: float
    delta: float
    actionable: bool


def _boost_to_p90(spec: DistributionSpec) -> DistributionSpec | None:
    if spec.family == "lognormal":
        p90_mu = spec.params["mu"] + Z_SCORE_90TH_PERCENTILE * spec.params["sigma"]
        return DistributionSpec(
            family="lognormal",
            params={"mu": p90_mu, "sigma": spec.params["sigma"] * P90_PROBE_SPREAD_FACTOR},
            method="sensitivity_probe",
            confidence=spec.confidence,
        )
    if spec.family == "normal":
        p90_mean = spec.params["mean"] + Z_SCORE_90TH_PERCENTILE * spec.params["std"]
        return DistributionSpec(
            family="normal",
            params={"mean": p90_mean, "std": spec.params["std"] * P90_PROBE_SPREAD_FACTOR},
            method="sensitivity_probe",
            confidence=spec.confidence,
        )
    if spec.family == "empirical":
        values = spec.params.get("values", [])
        if not values:
            return None
        p90_value = float(np.percentile(values, 90))
        return DistributionSpec(
            family="empirical", params={"values": [p90_value]}, method="sensitivity_probe", confidence=spec.confidence
        )
    return None


def analyse_sensitivity(
    base_input: SimulationInput, base_result: SimulationResult
) -> list[SensitivityFactor]:
    prob_before = _probability_at(base_result)
    factors: list[SensitivityFactor] = []

    # Each income source arriving ON TIME instead of with its usual
    # uncertainty.
    for i, income in enumerate(base_input.income_events):
        if income.day_uncertainty_std <= 0:
            continue  # already certain — nothing to improve
        improved = list(base_input.income_events)
        improved[i] = dataclasses.replace(income, day_uncertainty_std=0.0)
        result = simulate(dataclasses.replace(base_input, income_events=improved))
        prob_after = _probability_at(result)
        factors.append(
            SensitivityFactor(
                name=f"{income.label}_on_time",
                description=f"{income.label} arriving exactly when expected, with no delay",
                prob_before=prob_before,
                prob_after=prob_after,
                delta=prob_before - prob_after,
                actionable=True,
            )
        )

    # Each income source paying at its optimistic (p90) level.
    for i, income in enumerate(base_input.income_events):
        boosted = _boost_to_p90(income.distribution)
        if boosted is None:
            continue
        improved = list(base_input.income_events)
        improved[i] = dataclasses.replace(income, distribution=boosted)
        result = simulate(dataclasses.replace(base_input, income_events=improved))
        prob_after = _probability_at(result)
        factors.append(
            SensitivityFactor(
                name=f"{income.label}_at_p90",
                description=f"{income.label} paying at its optimistic level instead of typical",
                prob_before=prob_before,
                prob_after=prob_after,
                delta=prob_before - prob_after,
                # Not actionable: the user can't make a client pay more
                # than agreed — this quantifies upside, not a lever.
                actionable=False,
            )
        )

    # Each flexible obligation removed (skipped/deferred this period).
    for i, obligation in enumerate(base_input.obligations):
        if not obligation.is_flexible:
            continue
        remaining = [o for j, o in enumerate(base_input.obligations) if j != i]
        result = simulate(dataclasses.replace(base_input, obligations=remaining))
        prob_after = _probability_at(result)
        factors.append(
            SensitivityFactor(
                name=f"skip_{obligation.label}",
                description=f"Skipping or deferring {obligation.label} this period",
                prob_before=prob_before,
                prob_after=prob_after,
                delta=prob_before - prob_after,
                actionable=True,
            )
        )

    # Discretionary spending reduced 25%.
    reduced_mean = base_input.discretionary_daily_mean * Decimal(str(DISCRETIONARY_REDUCTION_FACTOR))
    result = simulate(dataclasses.replace(base_input, discretionary_daily_mean=reduced_mean))
    prob_after = _probability_at(result)
    factors.append(
        SensitivityFactor(
            name="reduce_discretionary_spending",
            description="Cutting discretionary spending by 25%",
            prob_before=prob_before,
            prob_after=prob_after,
            delta=prob_before - prob_after,
            actionable=True,
        )
    )

    # The top factor is what the user should be told first: sorting by
    # delta descending surfaces the single lever with the biggest impact
    # on risk, rather than an undifferentiated list.
    factors.sort(key=lambda f: f.delta, reverse=True)
    return factors
