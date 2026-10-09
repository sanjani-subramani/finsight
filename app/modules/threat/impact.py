"""Threat x Twin — THE DIFFERENTIATOR.

A generic scam-detection tool says "suspicious link." This says what it
would actually cost you: the same counterfactual-simulation technique
Step 7's collision detector uses (re-simulate with the SAME seed, change
exactly one thing, measure the delta) applied here to "what if I actually
paid what this scammer is asking for" instead of "what if this risk
factor weren't present."
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ThreatEvent
from app.modules.simulation.builder import build_simulation_input
from app.modules.simulation.engine import SimulationResult, simulate
from app.modules.simulation.service import SimulationService
from app.modules.twin.service import TwinService

# A payment that pushes the median simulated scenario into a shortfall
# more than half the time is "more likely than not" to cause real harm —
# the same threshold framing used throughout the risk pipeline (Step 7).
WOULD_CAUSE_SHORTFALL_PROBABILITY_THRESHOLD = 0.5
# Above this POST-payment probability, this isn't just "a bit worse" —
# it's dangerous enough to warrant amplifying the threat's own severity.
# See app.modules.threat.service, which is where this multiplier is
# actually applied to the threat's risk_score (ThreatImpact itself only
# reports the probabilities; combining them into a score is the
# service's job, matching how Step 7's scoring stays separate from
# collision detection).
SEVERITY_MULTIPLIER_THRESHOLD = 0.60
SEVERITY_MULTIPLIER = 1.5


@dataclass(frozen=True)
class ThreatImpact:
    would_cause_shortfall: bool
    prob_before: float
    prob_after: float
    obligations_at_risk: list[str] = field(default_factory=list)
    days_until_first_impact: int | None = None
    human_statement: str = ""


def _first_impact_days(result: SimulationResult) -> int | None:
    percentiles = (result.first_breach_day_distribution or {}).get("percentiles")
    if not percentiles:
        return None
    p50 = percentiles.get("p50")
    return round(p50) if p50 is not None else None


def _build_human_statement(
    requested_amount: Decimal,
    cash_available: Decimal,
    at_risk_detail: list[tuple[str, Decimal, int]],
    prob_before: float,
    prob_after: float,
) -> str:
    remaining = cash_available - requested_amount
    statement = f"Paying Rs.{requested_amount:,.2f} would leave Rs.{remaining:,.2f}"
    if at_risk_detail:
        label, amount, days = at_risk_detail[0]
        statement += f", but {label} of Rs.{amount:,.2f} is due in {days} day(s)"
    statement += f". Shortfall risk would rise from {prob_before:.0%} to {prob_after:.0%}."
    return statement


async def assess_financial_impact(
    session: AsyncSession, user_id: UUID, threat: ThreatEvent
) -> ThreatImpact | None:
    """None when the threat has no requested_amount — there is nothing to
    run a "what if I paid this" counterfactual against."""
    if threat.requested_amount is None:
        return None

    snapshot = await TwinService().get_base_snapshot(session, user_id)
    sim_outcome = await SimulationService().run(session, user_id)
    result_before = sim_outcome.result
    horizon = max(result_before.shortfall_probability_by_horizon)
    prob_before = result_before.shortfall_probability_by_horizon[horizon]

    # SAME SEED as the baseline run: the only thing that should change
    # between "before" and "after" is the one amount this threat would
    # cost. A different seed would mean part of the measured probability
    # delta is just random Monte Carlo noise between two independent
    # draws, not the threat's actual financial impact — identical
    # reasoning to Step 7's collision counterfactuals.
    baseline_input = await build_simulation_input(
        session, snapshot, horizon, result_before.scenarios_run, seed=result_before.seed
    )
    reduced_cash = baseline_input.starting_cash - threat.requested_amount
    counterfactual_input = dataclasses.replace(baseline_input, starting_cash=reduced_cash)
    result_after = simulate(counterfactual_input)
    prob_after = result_after.shortfall_probability_by_horizon.get(horizon, 0.0)

    today = date.today()
    at_risk_detail: list[tuple[str, Decimal, int]] = []
    cumulative = Decimal("0")
    unpaid_obligations = sorted(
        (o for o in snapshot.obligations if not o.is_paid), key=lambda o: o.due_date
    )
    for obligation in unpaid_obligations:
        cumulative += obligation.amount
        if cumulative > reduced_cash:
            at_risk_detail.append((obligation.label, obligation.amount, (obligation.due_date - today).days))

    return ThreatImpact(
        would_cause_shortfall=prob_after >= WOULD_CAUSE_SHORTFALL_PROBABILITY_THRESHOLD,
        prob_before=prob_before,
        prob_after=prob_after,
        obligations_at_risk=[label for label, _amount, _days in at_risk_detail],
        days_until_first_impact=_first_impact_days(result_after),
        human_statement=_build_human_statement(
            threat.requested_amount, snapshot.cash_available, at_risk_detail, prob_before, prob_after
        ),
    )
