"""Persistence for ingested events and quarantined input.

Owns the only code paths allowed to write to financial_events and
quarantined_inputs from the ingestion module.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import NormalizedFinancialEvent
from app.models.tables import FinancialEvent, QuarantinedInput


async def write_event(
    session: AsyncSession,
    event: NormalizedFinancialEvent,
    source_ref: str | None,
) -> tuple[FinancialEvent, bool]:
    """Insert `event`, or return the existing row if (user_id, source_ref)
    was already ingested. Returns (row, was_duplicate)."""

    if source_ref is not None:
        existing = await _find_by_source_ref(session, event.user_id, source_ref)
        if existing is not None:
            return existing, True

    row = FinancialEvent(
        id=event.event_id,
        user_id=event.user_id,
        schema_version=event.schema_version,
        event_type=event.event_type.value,
        amount=event.amount,
        currency=event.currency,
        occurred_at=event.occurred_at,
        ingested_at=event.ingested_at,
        effective_date=event.effective_date,
        counterparty=event.counterparty,
        category=event.category,
        description=event.description,
        data_source=event.data_source.value,
        source_ref=source_ref,
        confidence_score=event.confidence_score,
        duplicate_of=event.duplicate_of,
        conflicts_with=[str(u) for u in event.conflicts_with] or None,
        raw_payload=event.raw_payload or None,
    )

    # financial_events is append-only: we never UPDATE an existing row. A
    # correction to a past event is modeled as a brand-new event row, with
    # the OLD row's superseded_by pointing at the new one — never as an
    # in-place mutation of financial history.
    try:
        async with session.begin_nested():
            session.add(row)
            await session.flush()
    except IntegrityError:
        if source_ref is None:
            raise
        # Lost a race with a concurrent identical ingestion (same
        # user_id + source_ref) — the other insert already committed the
        # canonical row under our partial unique index, so fetch and
        # return it instead of failing the request.
        existing = await _find_by_source_ref(session, event.user_id, source_ref)
        if existing is not None:
            return existing, True
        raise

    return row, False


async def _find_by_source_ref(
    session: AsyncSession, user_id: UUID, source_ref: str
) -> FinancialEvent | None:
    result = await session.execute(
        select(FinancialEvent).where(
            FinancialEvent.user_id == user_id,
            FinancialEvent.source_ref == source_ref,
        )
    )
    return result.scalar_one_or_none()


async def quarantine_raw(
    session: AsyncSession,
    *,
    user_id: UUID,
    raw_input: str,
    sender: str | None,
    reason: str,
    attempted_methods: list[str] | None = None,
) -> QuarantinedInput:
    row = QuarantinedInput(
        user_id=user_id,
        raw_text=raw_input,
        sender=sender,
        reason=reason,
        attempted_methods=attempted_methods or [],
    )
    session.add(row)
    await session.flush()
    return row
