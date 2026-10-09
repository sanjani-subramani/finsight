"""Cross-source duplicate detection.

Step 3's ingestion-level idempotency (see app.modules.ingestion.repository
.write_event) already catches the EASY case: the exact same SMS/CSV row
re-ingested, which produces an identical source_ref for the same source.
This module catches the HARDER case: the same real-world transaction
arriving through two DIFFERENT channels — e.g. a bank SMS and a CSV bank
statement both describing the same ₹18,000 payment from the same client
on the same day.

PRECISION VS RECALL — read before touching any threshold below. A FALSE
MERGE (deciding two genuinely different payments are the same
transaction) silently makes real money disappear from the user's
financial Twin: if a freelancer was paid ₹18,000 twice by the same
client in one week and we merge those into one event, their actual cash
position is now wrong and nothing will ever alert them, because as far
as the system is concerned nothing is unusual. A FALSE SPLIT (failing to
recognize a real duplicate) just leaves one extra visible row the user
can notice and correct — annoying, but self-correcting, and never
silently wrong. Because these two failure modes are not equally bad,
every threshold in this module is deliberately conservative: when a
match is ambiguous, we do NOT merge.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import FinancialEvent
from app.modules.confidence.counterparty import CounterpartyResolver

# 0.5% or exact — anything looser risks a false merge on two unrelated
# transactions that merely happen to be similarly sized.
AMOUNT_TOLERANCE_PCT = Decimal("0.005")


@dataclass
class DuplicateCandidate:
    existing_event_id: UUID
    similarity: float
    reasons: list[str]


async def find_duplicates(
    session: AsyncSession,
    event: FinancialEvent,
    window_hours: int = 48,
    resolver: CounterpartyResolver | None = None,
) -> list[DuplicateCandidate]:
    if event.amount is None:
        return []

    resolver = resolver or CounterpartyResolver()
    window = timedelta(hours=window_hours)
    event_amount = Decimal(str(event.amount))

    stmt = select(FinancialEvent).where(
        FinancialEvent.user_id == event.user_id,
        FinancialEvent.event_type == event.event_type,
        # Same source + same source_ref is Step 3's job (exact
        # re-ingestion); this module exists specifically for the
        # different-source case.
        FinancialEvent.data_source != event.data_source,
        FinancialEvent.occurred_at >= event.occurred_at - window,
        FinancialEvent.occurred_at <= event.occurred_at + window,
        FinancialEvent.id != event.id,
        FinancialEvent.duplicate_of.is_(None),
        FinancialEvent.superseded_by.is_(None),
    )
    result = await session.execute(stmt)

    candidates: list[DuplicateCandidate] = []
    for row in result.scalars():
        if row.amount is None:
            continue

        row_amount = Decimal(str(row.amount))
        if event_amount == 0:
            amount_matches = row_amount == 0
            diff_pct = Decimal("0") if amount_matches else Decimal("1")
        else:
            diff_pct = abs(row_amount - event_amount) / event_amount
            amount_matches = row_amount == event_amount or diff_pct <= AMOUNT_TOLERANCE_PCT

        if not amount_matches:
            continue

        match = await resolver.resolve(event.counterparty, row.counterparty)
        if not match.is_same:
            continue

        reasons = [
            "amount exactly equal" if row_amount == event_amount else "amount within 0.5% tolerance",
            f"counterparty resolved as same entity ({match.method})",
            f"different data_source ({event.data_source} vs {row.data_source})",
            f"occurred_at within {window_hours}h window",
        ]
        # Blend how close the amounts are with how confident the entity
        # match was — either signal being weak should pull this down.
        amount_closeness = float(1 - min(diff_pct, Decimal("1")))
        similarity = (amount_closeness * 0.5) + (match.similarity * 0.5)

        candidates.append(
            DuplicateCandidate(
                existing_event_id=row.id, similarity=round(similarity, 4), reasons=reasons
            )
        )

    return candidates


async def mark_duplicate(
    session: AsyncSession, duplicate_event_id: UUID, canonical_event_id: UUID
) -> None:
    # financial_events is append-only: we NEVER delete the duplicate row.
    # Setting duplicate_of preserves the full raw history — useful for
    # audit, and for undoing a wrong merge via the unmerge endpoint —
    # while telling every downstream reader (the aggregator, the Twin,
    # ...) to treat this row as non-authoritative.
    result = await session.execute(
        select(FinancialEvent).where(FinancialEvent.id == duplicate_event_id)
    )
    row = result.scalar_one_or_none()
    if row is not None:
        row.duplicate_of = canonical_event_id
