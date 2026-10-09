"""Claim priority ordering. Fully deterministic — no LLM, no randomness.

CLAIM_TIERS, highest to lowest priority:
  1 SURVIVAL      rent, food, utilities, medical -- missing these has
                  immediate, severe consequences (eviction, going hungry,
                  power cut). Always funded; see HARD CONSTRAINTS below.
  2 CONTRACTUAL   EMI, insurance premium, taxes -- sits ABOVE buffer
                  deliberately: a missed EMI or premium has COMPOUNDING
                  consequences (credit score damage that lasts years,
                  policy lapse, penalty interest), whereas a thin buffer
                  is recoverable by saving again next month. The pain of
                  tier 2 outlasts the pain of tier 3.
  3 BUFFER        topping up (or not raiding) the emergency fund, up to
                  a 1-month-of-fixed-obligations floor.
  4 GROWTH        SIP, investments -- committed but genuinely deferrable
                  without immediate penalty.
  5 DISCRETIONARY vacation, upgrades, wants -- the first and easiest
                  thing to cut.
"""

from __future__ import annotations

from decimal import Decimal
from enum import IntEnum

from app.contracts.events import Goal, Obligation

# The ABSOLUTE floor the emergency fund may never cross, regardless of
# risk tolerance or how severe the shortfall is -- a HARD constraint.
# 1-month-of-fixed-obligations is the *target* (see arbitration.py's
# buffer claim), this is the much lower line under which the fund stops
# being a safety net at all.
EMERGENCY_FUND_ABSOLUTE_FLOOR = Decimal("5000")


class ClaimTier(IntEnum):
    SURVIVAL = 1
    CONTRACTUAL = 2
    BUFFER = 3
    GROWTH = 4
    DISCRETIONARY = 5


_SURVIVAL_CATEGORIES = {"rent", "food_delivery", "groceries", "utilities", "health"}
_CONTRACTUAL_CATEGORIES = {"emi", "insurance", "tax"}
_GROWTH_CATEGORIES = {"investment", "education"}
# Everything else (entertainment, shopping, subscriptions, transport,
# fuel, uncategorized, ...) falls through to DISCRETIONARY.

_BUFFER_GOAL_KEYWORDS = ("emergency fund", "emergency")
_GROWTH_GOAL_KEYWORDS = ("sip", "invest", "retirement", "mutual fund", "stocks", "stock")
_DISCRETIONARY_GOAL_KEYWORDS = ("vacation", "trip", "travel", "upgrade", "gadget", "phone", "shopping")


def classify_claim(obligation_or_goal: Obligation | Goal) -> ClaimTier:
    if isinstance(obligation_or_goal, Obligation):
        return _classify_obligation(obligation_or_goal)
    return _classify_goal(obligation_or_goal)


def _classify_obligation(obligation: Obligation) -> ClaimTier:
    category = (obligation.category or "").lower()
    if category in _SURVIVAL_CATEGORIES:
        return ClaimTier.SURVIVAL
    if category in _CONTRACTUAL_CATEGORIES:
        return ClaimTier.CONTRACTUAL
    if category in _GROWTH_CATEGORIES:
        return ClaimTier.GROWTH
    # An unrecognized but FIXED obligation (a recurring bill we simply
    # don't have a merchant category for) is more likely a genuine
    # commitment than a want -- default it to CONTRACTUAL rather than
    # DISCRETIONARY. A flexible/uncategorized one has no such signal.
    return ClaimTier.CONTRACTUAL if obligation.is_fixed else ClaimTier.DISCRETIONARY


def _classify_goal(goal: Goal) -> ClaimTier:
    label = goal.label.lower()
    if any(keyword in label for keyword in _BUFFER_GOAL_KEYWORDS):
        return ClaimTier.BUFFER
    if any(keyword in label for keyword in _GROWTH_GOAL_KEYWORDS):
        return ClaimTier.GROWTH
    if any(keyword in label for keyword in _DISCRETIONARY_GOAL_KEYWORDS):
        return ClaimTier.DISCRETIONARY
    # No recognizable keyword: a non-flexible goal reads more like a
    # committed plan (GROWTH); a flexible one reads more like a want
    # that can be skipped (DISCRETIONARY).
    return ClaimTier.DISCRETIONARY if goal.is_flexible else ClaimTier.GROWTH


def reduction_order(risk_tolerance: str) -> list[ClaimTier]:
    """The order in which tiers are considered as a SOURCE of cash when
    covering a shortfall -- earlier in the list means "sacrifice this
    first." SURVIVAL is deliberately never included: it is a hard
    constraint, not a preference to trade off (see HARD CONSTRAINTS in
    the module docstring). CONTRACTUAL is included only as an absolute
    last resort, consistent with it sitting above BUFFER in the tier
    ordering.

    SOFT PREFERENCE, adjustable by risk_tolerance:
    - conservative prefers keeping the buffer intact, sacrificing growth
      first (buffer drawn from only after growth is exhausted).
    - aggressive prefers keeping growth contributions intact, accepting
      a thinner buffer instead (buffer drawn from before growth).
    - balanced sits at the same default ordering as conservative -- growth
      before buffer -- since protecting the safety net is the more
      broadly defensible default absent an explicit preference.
    """
    if risk_tolerance == "aggressive":
        return [ClaimTier.DISCRETIONARY, ClaimTier.BUFFER, ClaimTier.GROWTH, ClaimTier.CONTRACTUAL]
    return [ClaimTier.DISCRETIONARY, ClaimTier.GROWTH, ClaimTier.BUFFER, ClaimTier.CONTRACTUAL]
