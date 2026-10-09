"""Collision detection: combinations of individually-normal conditions
whose JOINT risk substantially exceeds their individual risks.

Everything here is deterministic — no LLM, no randomness beyond the
seeded Monte Carlo engine itself (and every re-simulation reuses the
SAME seed as the baseline run, which is what makes the measured deltas
mean something rather than being noise between independent draws).
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import FinancialStateSnapshot
from app.modules.risk.rules import RuleFinding
from app.modules.simulation.builder import build_simulation_input
from app.modules.simulation.engine import SimulationInput, SimulationResult, simulate

# joint_probability below this is small enough in absolute terms that
# "amplification" is academic — a 5% shortfall chance isn't worth calling
# a crisis even if it's technically higher than any single factor alone.
COLLISION_MIN_JOINT_PROBABILITY = 0.25
# The actual test for amplification (superadditivity), not just "multiple
# bad things are true at once": a 0.10 margin over the single largest
# individual contribution filters out cases where one dominant factor
# already explains nearly everything on its own.
COLLISION_MIN_MARGIN_OVER_LARGEST = 0.10
COLLISION_MIN_CONDITIONS = 2


@dataclass(frozen=True)
class Collision:
    collision_id: UUID
    condition_ids: list[str]
    joint_probability: float
    individual_probabilities: dict[str, float]
    amplification_factor: float
    severity: str  # low | medium | high | critical
    urgency: str  # low | medium | high | critical
    first_impact_date: date | None
    evidence: dict[str, Any] = field(default_factory=dict)
    human_statement: str = ""


# ---------------------------------------------------------------------------
# Counterfactual mutators: "what would the input look like if this ONE
# condition simply weren't true?" Only findings with a registered mutator
# here can participate in collision detection — a finding like
# unusual_large_expense (about a past event) or goal_at_risk (goals
# aren't part of SimulationInput at all) has no meaningful simulatable
# counterfactual, so it's excluded from collision candidates entirely
# rather than faked.
# ---------------------------------------------------------------------------


def _remove_income_delayed(inp: SimulationInput, finding: RuleFinding) -> SimulationInput:
    days_late = finding.evidence.get("days_late", 0)
    label = finding.evidence.get("income_source")
    updated = [
        dataclasses.replace(income, expected_day=max(0, income.expected_day - days_late), day_uncertainty_std=0.0)
        if income.label == label
        else income
        for income in inp.income_events
    ]
    return dataclasses.replace(inp, income_events=updated)


def _remove_income_after_obligation(inp: SimulationInput, finding: RuleFinding) -> SimulationInput:
    gap_days = finding.evidence.get("gap_days", 0)
    updated = [
        dataclasses.replace(income, expected_day=max(0, income.expected_day - gap_days), day_uncertainty_std=0.0)
        for income in inp.income_events
    ]
    return dataclasses.replace(inp, income_events=updated)


def _remove_obligation_cluster(inp: SimulationInput, finding: RuleFinding) -> SimulationInput:
    cluster_labels = {o["label"] for o in finding.evidence.get("obligations", [])}
    involved = sorted((o for o in inp.obligations if o.label in cluster_labels), key=lambda o: o.day_offset)
    others = [o for o in inp.obligations if o.label not in cluster_labels]
    if not involved:
        return inp
    spacing_days = 15  # well outside the 10-day cluster window
    base_day = involved[0].day_offset
    spaced = [dataclasses.replace(o, day_offset=base_day + i * spacing_days) for i, o in enumerate(involved)]
    return dataclasses.replace(inp, obligations=others + spaced)


def _remove_low_buffer(inp: SimulationInput, finding: RuleFinding) -> SimulationInput:
    threshold = Decimal(str(finding.evidence.get("threshold", "0")))
    if threshold <= inp.starting_cash:
        return inp
    return dataclasses.replace(inp, starting_cash=threshold)


def _remove_critical_buffer(inp: SimulationInput, finding: RuleFinding) -> SimulationInput:
    threshold = Decimal(str(finding.evidence.get("obligations_due_14d", "0")))
    if threshold <= inp.starting_cash:
        return inp
    return dataclasses.replace(inp, starting_cash=threshold)


def _remove_high_burn(inp: SimulationInput, finding: RuleFinding) -> SimulationInput:
    baseline = finding.evidence.get("baseline_60d_daily_mean")
    if baseline is None:
        return inp
    return dataclasses.replace(inp, discretionary_daily_mean=Decimal(str(round(baseline, 2))))


_COUNTERFACTUAL_MUTATORS: dict[str, Callable[[SimulationInput, RuleFinding], SimulationInput]] = {
    "income_delayed": _remove_income_delayed,
    "income_after_obligation": _remove_income_after_obligation,
    "obligation_cluster": _remove_obligation_cluster,
    "low_buffer": _remove_low_buffer,
    "critical_buffer": _remove_critical_buffer,
    "high_burn": _remove_high_burn,
}


def _representative_breach_date(sim_result: SimulationResult) -> date | None:
    percentiles = sim_result.first_breach_day_distribution.get("percentiles")
    if not percentiles:
        return None
    median_day = percentiles.get("p50")
    if median_day is None:
        return None
    return date.today() + timedelta(days=round(median_day))


def _severity_from_probability(probability: float) -> str:
    if probability >= 0.6:
        return "critical"
    if probability >= 0.4:
        return "high"
    if probability >= 0.25:
        return "medium"
    return "low"


def _urgency_from_days(days_until: int | None) -> str:
    if days_until is None:
        return "low"
    if days_until <= 3:
        return "critical"
    if days_until <= 7:
        return "high"
    if days_until <= 14:
        return "medium"
    return "low"


def _build_human_statement(
    findings_involved: list[RuleFinding], joint_probability: float, baseline_probability: float
) -> str:
    # Deterministic TEMPLATE substitution, no LLM: each finding already
    # carries a well-formed sentence with its own real numbers, so the
    # collision statement just stitches those together with the joint
    # risk delta — e.g. "Your ACME payment is 7 days late while rent
    # (Rs.15,000) and EMI (Rs.6,800) are both due within 9 days.
    # Shortfall risk rose from 8% to 41%."
    condition_summaries = " ".join(f.human_statement.rstrip(".") + "." for f in findings_involved)
    return (
        f"{condition_summaries} Shortfall risk rose from {baseline_probability:.0%} to {joint_probability:.0%}."
    )


async def detect_collisions(
    session: AsyncSession,
    user_id: UUID,
    snapshot: FinancialStateSnapshot,
    sim_result: SimulationResult,
    findings: list[RuleFinding],
) -> list[Collision]:
    simulatable = [f for f in findings if f.rule_id in _COUNTERFACTUAL_MUTATORS]
    if len(simulatable) < COLLISION_MIN_CONDITIONS:
        return []

    horizon_days = max(sim_result.shortfall_probability_by_horizon)
    joint_probability = sim_result.shortfall_probability_by_horizon[horizon_days]

    # Rebuild the exact input the baseline run used, with the SAME SEED —
    # essential. Without it, the delta measured below would be partly
    # random noise between two independent Monte Carlo draws rather than
    # the condition's actual contribution: a controlled counterfactual
    # changes exactly one thing, and randomness must not be that thing.
    baseline_input = await build_simulation_input(
        session, snapshot, horizon_days, sim_result.scenarios_run, seed=sim_result.seed
    )

    individual_probabilities: dict[str, float] = {}
    deltas: dict[str, float] = {}
    for finding in simulatable:
        counterfactual_input = _COUNTERFACTUAL_MUTATORS[finding.rule_id](baseline_input, finding)
        counterfactual_result = simulate(counterfactual_input)  # same seed, carried through unchanged
        probability_without_c = counterfactual_result.shortfall_probability_by_horizon.get(horizon_days, 0.0)
        individual_probabilities[finding.rule_id] = probability_without_c
        deltas[finding.rule_id] = max(0.0, joint_probability - probability_without_c)

    total_individual_delta = sum(deltas.values())
    amplification_factor = (
        joint_probability / total_individual_delta if total_individual_delta > 1e-9 else 0.0
    )

    largest_individual_delta = max(deltas.values(), default=0.0)
    condition_ids = sorted(individual_probabilities.keys())

    # A COLLISION exists only when ALL of these hold — see the module
    # docstring / constant comments for why each threshold is where it is.
    if (
        len(condition_ids) < COLLISION_MIN_CONDITIONS
        or joint_probability < COLLISION_MIN_JOINT_PROBABILITY
        or (joint_probability - largest_individual_delta) < COLLISION_MIN_MARGIN_OVER_LARGEST
    ):
        return []

    # "All conditions removed together" gives the genuinely meaningful
    # "before" figure for the human statement — distinct from any single
    # condition's individual_probabilities entry.
    all_removed_input = baseline_input
    for finding in simulatable:
        all_removed_input = _COUNTERFACTUAL_MUTATORS[finding.rule_id](all_removed_input, finding)
    all_removed_result = simulate(all_removed_input)
    baseline_probability = all_removed_result.shortfall_probability_by_horizon.get(horizon_days, 0.0)

    first_impact_date = _representative_breach_date(sim_result)
    days_until = (first_impact_date - date.today()).days if first_impact_date is not None else None

    collision = Collision(
        collision_id=uuid4(),
        condition_ids=condition_ids,
        joint_probability=joint_probability,
        individual_probabilities=individual_probabilities,
        amplification_factor=amplification_factor,
        severity=_severity_from_probability(joint_probability),
        urgency=_urgency_from_days(days_until),
        first_impact_date=first_impact_date,
        evidence={
            "findings": [{"rule_id": f.rule_id, "evidence": f.evidence} for f in simulatable],
            "baseline_probability_all_removed": baseline_probability,
            "deltas": deltas,
            "horizon_days": horizon_days,
            "seed": sim_result.seed,
        },
        human_statement=_build_human_statement(simulatable, joint_probability, baseline_probability),
    )
    return [collision]
