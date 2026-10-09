"""Goal Arbitration: when money cannot cover everything, decide what
gives -- and PROVE the recommendation actually improves the outcome
rather than just sounding reasonable.

ALGORITHM: greedy allocation down the tiers, with verification.

Greedy is acceptable here (rather than, say, an LP solver) because: the
claim set for one user in one period is small (a handful of obligations
and goals), ClaimTier gives a clean total order so there's no ambiguity
about what "priority" means, and — critically — we do not TRUST the
greedy heuristic's output blindly. Every proposal is checked by
re-running the Monte Carlo simulation with the proposed allocation
(SAME SEED as the baseline) and confirming the shortfall probability
actually went down. A proposal that doesn't verifiably help is discarded.
This is what separates a recommendation from a guess.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import FinancialStateSnapshot
from app.models.tables import User
from app.modules.decision.policy import (
    EMERGENCY_FUND_ABSOLUTE_FLOOR,
    ClaimTier,
    classify_claim,
    reduction_order,
)
from app.modules.simulation.builder import build_simulation_input
from app.modules.simulation.engine import SimulationResult, simulate

# Reductions move in Rs.500 steps -- coarse enough to produce a
# recommendation a person can actually act on ("cut SIP by Rs.1,500"),
# never all the way below zero.
REDUCTION_INCREMENT = Decimal("500")
# The default monthly contribution proposed toward rebuilding an
# under-target emergency fund, when nothing more specific is known.
BUFFER_MONTHLY_TOPUP = Decimal("2000")
# Tolerance profiles tried when generating alternatives -- see
# _effective_buffer_floor for how each one changes how much of the
# emergency fund is considered drawable.
_TOLERANCE_PROFILES = ("conservative", "balanced", "aggressive")


@dataclass(frozen=True)
class Claim:
    claim_id: str
    label: str
    tier: ClaimTier
    amount: Decimal
    due_date: date | None
    source: str  # "obligation" | "goal" | "buffer"


@dataclass(frozen=True)
class ArbitrationAlternative:
    profile: str  # "conservative" | "balanced" | "aggressive"
    allocations: dict[str, Decimal]
    reductions: dict[str, Decimal]
    prob_after: float


@dataclass(frozen=True)
class ArbitrationResult:
    claims: list[Claim]
    allocations: dict[str, Decimal]
    reductions: dict[str, Decimal]
    unfunded: list[str]
    prob_before: float
    prob_after: float
    trade_off_statement: str
    alternatives: list[ArbitrationAlternative] = field(default_factory=list)


def _collect_claims(snapshot: FinancialStateSnapshot, horizon_end: date) -> list[Claim]:
    claims: list[Claim] = []

    for obligation in snapshot.obligations:
        if obligation.is_paid or obligation.due_date > horizon_end:
            continue
        claims.append(
            Claim(
                claim_id=f"obligation:{obligation.obligation_id}",
                label=obligation.label,
                tier=classify_claim(obligation),
                amount=obligation.amount,
                due_date=obligation.due_date,
                source="obligation",
            )
        )

    today = date.today()
    for goal in snapshot.goals:
        if goal.target_date is not None and goal.target_date < today:
            continue
        remaining = max(Decimal("0"), goal.target_amount - goal.saved_amount)
        if remaining <= 0:
            continue
        months_left = 1
        if goal.target_date is not None:
            months_left = max(1, (goal.target_date - today).days // 30)
        monthly_contribution = (remaining / months_left).quantize(Decimal("1"))
        if monthly_contribution <= 0:
            continue
        claims.append(
            Claim(
                claim_id=f"goal:{goal.goal_id}",
                label=goal.label,
                tier=classify_claim(goal),
                amount=monthly_contribution,
                due_date=goal.target_date,
                source="goal",
            )
        )

    # A synthetic BUFFER claim: new money going INTO the emergency fund
    # this period, competing for cash on equal footing with everything
    # else at tier 3 -- distinct from _attempt_cover_shortfall's
    # emergency-fund DRAWDOWN, which is money coming OUT of the
    # already-existing balance. Both are real, separate cash flows.
    monthly_target = snapshot.total_fixed_obligations
    if monthly_target > 0 and snapshot.emergency_fund < monthly_target:
        claims.append(
            Claim(
                claim_id="buffer:topup",
                label="Emergency fund top-up",
                tier=ClaimTier.BUFFER,
                amount=BUFFER_MONTHLY_TOPUP,
                due_date=None,
                source="buffer",
            )
        )

    return claims


def _greedy_allocate(claims: list[Claim], available_cash: Decimal) -> tuple[dict[str, Decimal], Claim | None]:
    ordered = sorted(claims, key=lambda c: (c.tier, c.due_date or date.max, c.claim_id))
    allocations: dict[str, Decimal] = {}
    remaining = available_cash
    first_unfunded: Claim | None = None

    for claim in ordered:
        if remaining >= claim.amount:
            allocations[claim.claim_id] = claim.amount
            remaining -= claim.amount
        else:
            allocations[claim.claim_id] = max(Decimal("0"), remaining)
            remaining = Decimal("0")
            if first_unfunded is None:
                first_unfunded = claim

    return allocations, first_unfunded


def _effective_buffer_floor(snapshot: FinancialStateSnapshot, risk_tolerance: str) -> Decimal:
    monthly_target = snapshot.total_fixed_obligations  # the BUFFER tier's "1-month" target
    if risk_tolerance == "conservative":
        # Very protective: barely drawable, keeps the buffer close to a
        # full month of cover.
        return max(EMERGENCY_FUND_ABSOLUTE_FLOOR, monthly_target)
    if risk_tolerance == "aggressive":
        # Only the hard floor protects it.
        return EMERGENCY_FUND_ABSOLUTE_FLOOR
    return max(EMERGENCY_FUND_ABSOLUTE_FLOOR, monthly_target / 2)  # balanced: halfway


def _attempt_cover_shortfall(
    claims: list[Claim],
    allocations: dict[str, Decimal],
    first_unfunded: Claim,
    snapshot: FinancialStateSnapshot,
    risk_tolerance: str,
) -> tuple[dict[str, Decimal], Decimal, dict[str, Decimal]]:
    """Tries to free enough cash (from lower-priority claims and/or the
    emergency fund) to cover first_unfunded's shortfall. Returns
    (updated_allocations, total_freed, reductions)."""
    shortfall = first_unfunded.amount - allocations.get(first_unfunded.claim_id, Decimal("0"))
    if shortfall <= 0:
        return allocations, Decimal("0"), {}

    allocations = dict(allocations)
    reductions: dict[str, Decimal] = {}
    freed = Decimal("0")

    for tier in reduction_order(risk_tolerance):
        if freed >= shortfall:
            break

        if tier == ClaimTier.BUFFER:
            # Never raid the buffer to fund something LOWER priority than
            # the buffer itself (e.g. topping up a SIP) -- that defeats
            # the point of having a safety net.
            if first_unfunded.tier > ClaimTier.BUFFER:
                continue
            floor = _effective_buffer_floor(snapshot, risk_tolerance)
            drawable = max(Decimal("0"), snapshot.emergency_fund - floor)
            draw = min(drawable, shortfall - freed)
            if draw > 0:
                freed += draw
                reductions["buffer:emergency_fund_drawdown"] = draw
            continue

        # Claims in this tier other than the unfunded one itself. In a
        # strict tier-then-date greedy pass, anything strictly below
        # first_unfunded already received Rs.0 (cash ran out before
        # reaching it), so this is frequently a no-op for THIS specific
        # allocation -- it stays general (not special-cased away) so a
        # richer multi-claim mix is still handled correctly rather than
        # silently doing nothing.
        candidates = sorted(
            (c for c in claims if c.tier == tier and c.claim_id != first_unfunded.claim_id),
            key=lambda c: c.claim_id,
        )
        for claim in candidates:
            current = allocations.get(claim.claim_id, Decimal("0"))
            reduced_by = Decimal("0")
            while current > 0 and freed < shortfall:
                step = min(REDUCTION_INCREMENT, current)
                current -= step
                freed += step
                reduced_by += step
            if reduced_by > 0:
                allocations[claim.claim_id] = current
                reductions[claim.claim_id] = reductions.get(claim.claim_id, Decimal("0")) + reduced_by
            if freed >= shortfall:
                break

    new_amount = min(first_unfunded.amount, allocations.get(first_unfunded.claim_id, Decimal("0")) + freed)
    allocations[first_unfunded.claim_id] = new_amount
    return allocations, freed, reductions


def _build_trade_off_statement(
    reductions: dict[str, Decimal],
    claims_by_id: dict[str, Claim],
    first_unfunded: Claim | None,
    prob_before: float,
    prob_after: float,
) -> str:
    if not reductions:
        if first_unfunded is not None:
            return (
                f"Cash on hand cannot fully cover {first_unfunded.label} this period; "
                f"no further reduction was available to close the gap."
            )
        return "Cash on hand covers all claims this period; no reductions needed."

    parts = []
    for claim_id, amount in reductions.items():
        if claim_id == "buffer:emergency_fund_drawdown":
            parts.append(f"draw Rs.{amount:,.2f} from your emergency fund")
        else:
            label = claims_by_id[claim_id].label
            parts.append(f"reduce {label} by Rs.{amount:,.2f}")

    target = f" to preserve {first_unfunded.label}" if first_unfunded is not None else ""
    statement = f"{', '.join(parts).capitalize()}{target}."
    statement += f" Shortfall risk drops from {prob_before:.0%} to {prob_after:.0%}."

    annual_projection = sum(reductions.get(cid, Decimal("0")) for cid in reductions if cid != "buffer:emergency_fund_drawdown")
    if annual_projection > 0:
        statement += (
            f" You would move Rs.{annual_projection * 12:,.2f} less over a year if this pattern repeated monthly."
        )
    return statement


async def verify_allocation(
    session: AsyncSession,
    snapshot: FinancialStateSnapshot,
    horizon: int,
    baseline_seed: int,
    scenarios_run: int,
    freed: Decimal,
) -> float:
    """Re-runs the simulation with the SAME SEED as the baseline, with
    starting_cash increased by the amount this proposal frees up --
    money that would have gone to a lower-priority claim stays in the
    account instead. Same-seed reasoning is identical to Step 7's
    collision counterfactuals and Step 10's threat impact assessment: a
    different seed would mix random Monte Carlo noise into the measured
    delta instead of isolating the proposal's actual effect.
    """
    baseline_input = await build_simulation_input(session, snapshot, horizon, scenarios_run, seed=baseline_seed)
    counterfactual_input = dataclasses.replace(baseline_input, starting_cash=baseline_input.starting_cash + freed)
    result = simulate(counterfactual_input)
    return result.shortfall_probability_by_horizon.get(horizon, 1.0)


async def arbitrate(
    session: AsyncSession,
    user_id: UUID,
    snapshot: FinancialStateSnapshot,
    sim_result: SimulationResult,
) -> ArbitrationResult:
    horizon = max(sim_result.shortfall_probability_by_horizon)
    prob_before = sim_result.shortfall_probability_by_horizon[horizon]
    horizon_end = date.today() + timedelta(days=horizon)

    claims = _collect_claims(snapshot, horizon_end)
    claims_by_id = {c.claim_id: c for c in claims}

    if not claims:
        return ArbitrationResult(
            claims=[], allocations={}, reductions={}, unfunded=[],
            prob_before=prob_before, prob_after=prob_before,
            trade_off_statement="No claims to arbitrate this period.",
        )

    base_allocations, first_unfunded = _greedy_allocate(claims, snapshot.cash_available)

    if first_unfunded is None:
        return ArbitrationResult(
            claims=claims, allocations=base_allocations, reductions={}, unfunded=[],
            prob_before=prob_before, prob_after=prob_before,
            trade_off_statement="Cash on hand covers all claims this period; no reductions needed.",
        )

    user = await session.get(User, user_id)
    primary_tolerance = user.risk_tolerance if user is not None else "balanced"

    verified: dict[str, tuple[dict[str, Decimal], dict[str, Decimal], float]] = {}
    for profile in _TOLERANCE_PROFILES:
        allocations, freed, reductions = _attempt_cover_shortfall(
            claims, base_allocations, first_unfunded, snapshot, profile
        )
        if freed <= 0:
            continue  # nothing to propose for this profile
        prob_after = await verify_allocation(session, snapshot, horizon, sim_result.seed, sim_result.scenarios_run, freed)
        # VERIFICATION: only a proposal that measurably improves the
        # outcome is kept. This is what separates a recommendation from
        # a guess -- we measure the effect before suggesting it.
        if prob_after < prob_before:
            verified[profile] = (allocations, reductions, prob_after)

    if not verified:
        return ArbitrationResult(
            claims=claims, allocations=base_allocations, reductions={},
            unfunded=[first_unfunded.label] if base_allocations[first_unfunded.claim_id] < first_unfunded.amount else [],
            prob_before=prob_before, prob_after=prob_before,
            trade_off_statement=_build_trade_off_statement({}, claims_by_id, first_unfunded, prob_before, prob_before),
        )

    primary = verified.get(primary_tolerance) or min(verified.values(), key=lambda v: v[2])
    primary_allocations, primary_reductions, primary_prob_after = primary
    primary_unfunded = (
        [] if primary_allocations[first_unfunded.claim_id] >= first_unfunded.amount else [first_unfunded.label]
    )

    alternatives = [
        ArbitrationAlternative(profile=profile, allocations=allocations, reductions=reductions, prob_after=prob_after)
        for profile, (allocations, reductions, prob_after) in verified.items()
    ]

    return ArbitrationResult(
        claims=claims,
        allocations=primary_allocations,
        reductions=primary_reductions,
        unfunded=primary_unfunded,
        prob_before=prob_before,
        prob_after=primary_prob_after,
        trade_off_statement=_build_trade_off_statement(
            primary_reductions, claims_by_id, first_unfunded, prob_before, primary_prob_after
        ),
        alternatives=alternatives,
    )
