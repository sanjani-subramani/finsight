"""Temporal trust decay for unconfirmed events.

Only events that no independent second source has corroborated lose
confidence over time — a confirmed event already has independent
agreement, so there's nothing further eroding it as it ages.
"""

from __future__ import annotations

import math

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import DataSource
from app.models.tables import FinancialEvent
from app.modules.confidence.counterparty import CounterpartyResolver
from app.modules.confidence.dedup import find_duplicates

# exp(-1) at 180 days => half-life of roughly 125 days.
DECAY_HALF_LIFE_DAYS = 180.0

# Never decay to zero: the event genuinely happened — we are not saying
# "this probably didn't occur," only that we're less sure of its exact
# details (amount, counterparty, date) the longer it goes uncorroborated.
# A floor keeps very old unconfirmed events visibly present and weighted
# rather than effectively erased from the Twin's view of the past.
CONFIDENCE_FLOOR = 0.30


def apply_decay(base_confidence: float, age_days: float, is_confirmed: bool) -> float:
    if is_confirmed:
        return base_confidence

    decayed = base_confidence * math.exp(-age_days / DECAY_HALF_LIFE_DAYS)
    return max(CONFIDENCE_FLOOR, decayed)


def effective_age_days(age_days: float, data_source: DataSource) -> float:
    """Manual entries decay more slowly: a user asserting their own
    finances stays relevant longer than an unconfirmed automated read, so
    halve the effective age before it's handed to apply_decay."""
    if data_source == DataSource.manual:
        return age_days / 2
    return age_days


async def is_confirmed(
    session: AsyncSession,
    event: FinancialEvent,
    resolver: CounterpartyResolver | None = None,
) -> bool:
    """True when another event from a DIFFERENT data_source matches this
    one (same dedup criteria as app.modules.confidence.dedup) and was not
    itself marked as a conflict loser (superseded_by is excluded by
    find_duplicates)."""
    candidates = await find_duplicates(session, event, resolver=resolver)
    return len(candidates) > 0
