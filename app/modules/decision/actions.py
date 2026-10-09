"""Maps an ArbitrationResult to RecommendedAction contract objects.

CRITICAL: projected_risk_after on every action below is result.prob_after
— the VERIFIED value arbitration.py obtained by actually re-running the
simulation (see arbitration.arbitrate's VERIFICATION step). It is never
estimated, interpolated, or guessed at here; this module only formats
numbers arbitration.py already measured.
"""

from __future__ import annotations

from app.contracts.events import RecommendedAction
from app.modules.decision.arbitration import ArbitrationResult, Claim
from app.modules.decision.policy import ClaimTier


def _action_type_for(claim: Claim) -> str:
    if claim.source == "goal":
        return "reduce_sip" if claim.tier == ClaimTier.GROWTH else "defer_goal_contribution"
    if claim.source == "buffer":
        # A reduced TOP-UP contribution (less new money going in this
        # period) -- distinct from move_from_emergency_fund, which is
        # money coming OUT of the already-existing balance.
        return "defer_goal_contribution"
    # obligation
    if claim.tier == ClaimTier.DISCRETIONARY:
        return "delay_purchase"
    if claim.tier in (ClaimTier.CONTRACTUAL, ClaimTier.SURVIVAL):
        # A protected-tier obligation only ends up here as an absolute
        # last resort (see policy.reduction_order) -- a partial payment
        # now with the remainder deferred, not a full cut.
        return "split_obligation"
    return "reduce_discretionary"


def build_recommended_actions(result: ArbitrationResult) -> list[RecommendedAction]:
    claims_by_id = {claim.claim_id: claim for claim in result.claims}
    actions: list[RecommendedAction] = []

    for claim_id, amount in result.reductions.items():
        if amount <= 0:
            continue

        if claim_id == "buffer:emergency_fund_drawdown":
            actions.append(
                RecommendedAction(
                    action_type="move_from_emergency_fund",
                    label="Draw from your emergency fund",
                    amount=amount,
                    expected_effect=f"Frees Rs.{amount:,.2f} to cover an upcoming obligation without missing it.",
                    projected_risk_after=result.prob_after,
                )
            )
            continue

        claim = claims_by_id.get(claim_id)
        if claim is None:
            continue
        actions.append(
            RecommendedAction(
                action_type=_action_type_for(claim),
                label=f"Reduce {claim.label} by Rs.{amount:,.2f}",
                amount=amount,
                expected_effect=f"Frees Rs.{amount:,.2f} this period, verified to reduce shortfall risk.",
                projected_risk_after=result.prob_after,
            )
        )

    return actions
