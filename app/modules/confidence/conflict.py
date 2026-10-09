"""Detects and resolves value disagreements between independent sources
that describe what looks like the same transaction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import DataSource
from app.models.tables import FinancialEvent
from app.modules.confidence.authority import resolve_authority
from app.modules.confidence.counterparty import CounterpartyResolver

CONFLICT_LOWER_BOUND_PCT = Decimal("0.005")  # 0.5% — below this, dedup's job
# Beyond 20% two amounts are very unlikely to be describing the same
# transaction with a data-quality problem — a ₹500 coffee and a ₹5,000
# dinner sharing a counterparty and rough timing are just two different,
# genuinely real transactions. Treating that as "a conflict to resolve"
# would mean picking a winner between two things that are both simply
# true, and silently discarding the "loser" — there is nothing to
# resolve here, so we deliberately leave both events alone.
CONFLICT_UPPER_BOUND_PCT = Decimal("0.20")

# Agreement between independent sources should raise trust; the inverse
# holds too — disagreement should lower it, even for the side that
# ultimately wins. A winner that was contradicted by another source is
# less certain than one nobody ever disputed, so it pays this penalty too.
WINNER_CONFIDENCE_PENALTY = 0.10


@dataclass
class Conflict:
    event_a_id: UUID
    event_b_id: UUID
    field: str
    value_a: str
    value_b: str
    winner_id: UUID
    winner_reason: str
    confidence_penalty: float


@dataclass
class ConflictResolution:
    winner_id: UUID
    loser_id: UUID
    winner_reason: str
    winner_new_confidence: float


async def detect_conflicts(
    session: AsyncSession,
    event: FinancialEvent,
    window_hours: int = 48,
    resolver: CounterpartyResolver | None = None,
) -> list[Conflict]:
    if event.amount is None:
        return []

    resolver = resolver or CounterpartyResolver()
    window = timedelta(hours=window_hours)
    event_amount = Decimal(str(event.amount))
    if event_amount == 0:
        return []

    stmt = select(FinancialEvent).where(
        FinancialEvent.user_id == event.user_id,
        FinancialEvent.event_type == event.event_type,
        FinancialEvent.id != event.id,
        FinancialEvent.occurred_at >= event.occurred_at - window,
        FinancialEvent.occurred_at <= event.occurred_at + window,
        FinancialEvent.duplicate_of.is_(None),
        FinancialEvent.superseded_by.is_(None),
    )
    result = await session.execute(stmt)

    conflicts: list[Conflict] = []
    for row in result.scalars():
        if row.amount is None:
            continue

        match = await resolver.resolve(event.counterparty, row.counterparty)
        if not match.is_same:
            continue

        row_amount = Decimal(str(row.amount))
        diff_pct = abs(row_amount - event_amount) / event_amount

        if diff_pct <= CONFLICT_LOWER_BOUND_PCT or diff_pct >= CONFLICT_UPPER_BOUND_PCT:
            continue  # either "same" (dedup's job) or genuinely different transactions

        resolution = resolve_conflict(event, row)
        conflicts.append(
            Conflict(
                event_a_id=event.id,
                event_b_id=row.id,
                field="amount",
                value_a=str(event_amount),
                value_b=str(row_amount),
                winner_id=resolution.winner_id,
                winner_reason=resolution.winner_reason,
                confidence_penalty=WINNER_CONFIDENCE_PENALTY,
            )
        )

    return conflicts


def resolve_conflict(event_a: FinancialEvent, event_b: FinancialEvent) -> ConflictResolution:
    source_a = DataSource(event_a.data_source)
    source_b = DataSource(event_b.data_source)

    a_contradicted_by_bank = source_b == DataSource.bank_csv and source_a != DataSource.bank_csv
    b_contradicted_by_bank = source_a == DataSource.bank_csv and source_b != DataSource.bank_csv

    authority_a = resolve_authority(source_a, a_contradicted_by_bank)
    authority_b = resolve_authority(source_b, b_contradicted_by_bank)

    if authority_a > authority_b:
        winner, loser = event_a, event_b
        reason = (
            f"{source_a.value} (authority {authority_a:.2f}) outranks "
            f"{source_b.value} (authority {authority_b:.2f})"
        )
    elif authority_b > authority_a:
        winner, loser = event_b, event_a
        reason = (
            f"{source_b.value} (authority {authority_b:.2f}) outranks "
            f"{source_a.value} (authority {authority_a:.2f})"
        )
    else:
        # Tie: the more recently ingested record wins — it's the most
        # up-to-date view we have.
        if event_a.ingested_at >= event_b.ingested_at:
            winner, loser = event_a, event_b
            reason = f"tied authority ({authority_a:.2f}); {source_a.value} ingested more recently"
        else:
            winner, loser = event_b, event_a
            reason = f"tied authority ({authority_b:.2f}); {source_b.value} ingested more recently"

    winner_confidence = float(winner.confidence_score)
    new_confidence = max(0.0, winner_confidence - WINNER_CONFIDENCE_PENALTY)

    return ConflictResolution(
        winner_id=winner.id,
        loser_id=loser.id,
        winner_reason=reason,
        winner_new_confidence=new_confidence,
    )


async def apply_resolution(
    session: AsyncSession,
    resolution: ConflictResolution,
    event_a: FinancialEvent,
    event_b: FinancialEvent,
) -> None:
    winner = event_a if event_a.id == resolution.winner_id else event_b
    loser = event_b if winner is event_a else event_a

    loser.superseded_by = winner.id
    winner.confidence_score = resolution.winner_new_confidence

    # The frozen Pydantic contract types conflicts_with as list[UUID] for
    # a freshly-normalized event, but at the DB layer this JSONB column
    # can hold a richer record — we deliberately store both disputed
    # values here (not just an id) so the disagreement itself, not just
    # the fact that one occurred, is never lost. This only ever happens
    # through this function, never through app.contracts.events, so it
    # doesn't touch or violate the frozen contract.
    existing = list(winner.conflicts_with or [])
    existing.append(
        {
            "event_id": str(loser.id),
            "field": "amount",
            "winner_value": str(winner.amount),
            "loser_value": str(loser.amount),
            "loser_source": loser.data_source,
        }
    )
    winner.conflicts_with = existing
