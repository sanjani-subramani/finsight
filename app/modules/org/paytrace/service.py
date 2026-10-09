"""PayTraceService -- ingestion, lookup, search, health, and alerts for the
org-side payment-lifecycle-reconstruction feature (Step 14).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import TransactionEvent, TxnStage
from app.models.tables import TransactionEvent as TransactionEventRow
from app.modules.org.paytrace.analytics import (
    PaymentHealth,
    ProviderAlert,
    compute_health,
    detect_provider_degradation,
)
from app.modules.org.paytrace.classifier import FailureClassification, FailureClassifier, FailureMode
from app.modules.org.paytrace.state_machine import TransactionState, derive_state
from app.platform.timeutils import as_aware_utc

DEFAULT_SEARCH_LIMIT = 50
MAX_SEARCH_LIMIT = 500

_EPOCH_AWARE = datetime.min.replace(tzinfo=timezone.utc)


def _row_to_event(row: TransactionEventRow) -> TransactionEvent:
    return TransactionEvent(
        event_id=row.id,
        org_id=row.org_id,
        transaction_ref=row.transaction_ref,
        stage=TxnStage(row.stage),
        occurred_at=as_aware_utc(row.occurred_at),
        amount=Decimal(str(row.amount)),
        provider=row.provider,
        provider_ref=row.provider_ref,
        error_code=row.error_code,
        latency_ms=row.latency_ms,
        idempotency_key=row.idempotency_key,
        raw_payload=row.raw_payload or {},
    )


@dataclass(frozen=True)
class TransactionSearchFilters:
    status: TxnStage | None = None
    provider: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    failure_mode: FailureMode | None = None


@dataclass(frozen=True)
class TransactionSummary:
    transaction_ref: str
    current_stage: TxnStage | None
    provider: str | None
    last_event_at: datetime | None
    is_terminal: bool
    classification: FailureClassification


@dataclass(frozen=True)
class TransactionSearchResult:
    items: list[TransactionSummary]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class TransactionDetail:
    state: TransactionState
    classification: FailureClassification


class PayTraceService:
    async def ingest_event(self, session: AsyncSession, org_id: UUID, event: TransactionEvent) -> TransactionState:
        """Validate nothing up front and reject nothing -- an invalid
        transition is exactly the kind of anomaly PayTrace exists to
        surface, not something to silently refuse. The event is always
        appended; derive_state() is what flags it.

        `(org_id, idempotency_key)` is unique at the DB level (redelivery
        of the exact same event -- e.g. an at-least-once queue retry -- is
        a no-op, not a new fact to fold in and not a DUPLICATE_ATTEMPT,
        which is about two DIFFERENT idempotency keys for what looks like
        the same purchase).
        """
        existing_rows = await self._load_rows(session, org_id, event.transaction_ref)
        existing_events = [_row_to_event(r) for r in existing_rows]

        if any(row.idempotency_key == event.idempotency_key for row in existing_rows):
            return derive_state(existing_events)

        session.add(
            TransactionEventRow(
                id=event.event_id,
                org_id=org_id,
                transaction_ref=event.transaction_ref,
                stage=event.stage.value,
                occurred_at=event.occurred_at,
                amount=event.amount,
                provider=event.provider,
                provider_ref=event.provider_ref,
                error_code=event.error_code,
                latency_ms=event.latency_ms,
                idempotency_key=event.idempotency_key,
                raw_payload=event.raw_payload,
            )
        )
        await session.flush()

        return derive_state([*existing_events, event])

    async def ingest_batch(
        self, session: AsyncSession, org_id: UUID, events: list[TransactionEvent]
    ) -> dict[str, TransactionState]:
        results: dict[str, TransactionState] = {}
        for event in events:
            results[event.transaction_ref] = await self.ingest_event(session, org_id, event)
        return results

    async def get_transaction(
        self, session: AsyncSession, org_id: UUID, transaction_ref: str
    ) -> TransactionDetail | None:
        rows = await self._load_rows(session, org_id, transaction_ref)
        if not rows:
            return None
        state = derive_state([_row_to_event(r) for r in rows])
        classification = FailureClassifier().classify(state)
        return TransactionDetail(state=state, classification=classification)

    async def get_health(self, session: AsyncSession, org_id: UUID, window_hours: int = 24) -> PaymentHealth:
        return await compute_health(session, org_id, window_hours)

    async def get_provider_alerts(self, session: AsyncSession, org_id: UUID) -> list[ProviderAlert]:
        return await detect_provider_degradation(session, org_id)

    async def search_transactions(
        self,
        session: AsyncSession,
        org_id: UUID,
        filters: TransactionSearchFilters,
        limit: int = DEFAULT_SEARCH_LIMIT,
        offset: int = 0,
    ) -> TransactionSearchResult:
        # Filters that narrow which transaction_refs are even candidates can
        # be pushed into SQL; status and failure_mode can't (they depend on
        # the folded state / classification), so those are applied after
        # loading each candidate's full history.
        conditions = [TransactionEventRow.org_id == org_id]
        if filters.provider is not None:
            conditions.append(TransactionEventRow.provider == filters.provider)
        if filters.date_from is not None:
            conditions.append(TransactionEventRow.occurred_at >= filters.date_from)
        if filters.date_to is not None:
            conditions.append(TransactionEventRow.occurred_at <= filters.date_to)

        ref_result = await session.execute(
            select(TransactionEventRow.transaction_ref).where(*conditions).distinct()
        )
        candidate_refs = [row[0] for row in ref_result.all()]
        if not candidate_refs:
            return TransactionSearchResult(items=[], total=0, limit=limit, offset=offset)

        rows_result = await session.execute(
            select(TransactionEventRow).where(
                TransactionEventRow.org_id == org_id,
                TransactionEventRow.transaction_ref.in_(candidate_refs),
            )
        )
        by_ref: dict[str, list[TransactionEventRow]] = {}
        for row in rows_result.scalars():
            by_ref.setdefault(row.transaction_ref, []).append(row)

        classifier = FailureClassifier()
        summaries: list[TransactionSummary] = []
        for ref, rows in by_ref.items():
            state = derive_state([_row_to_event(r) for r in rows])
            classification = classifier.classify(state)

            if filters.status is not None and state.current_stage != filters.status:
                continue
            if filters.failure_mode is not None and classification.mode != filters.failure_mode:
                continue

            last_entry = state.timeline[-1] if state.timeline else None
            summaries.append(
                TransactionSummary(
                    transaction_ref=ref,
                    current_stage=state.current_stage,
                    provider=last_entry.provider if last_entry else None,
                    last_event_at=last_entry.occurred_at if last_entry else None,
                    is_terminal=state.is_terminal,
                    classification=classification,
                )
            )

        summaries.sort(key=lambda s: s.last_event_at or _EPOCH_AWARE, reverse=True)
        total = len(summaries)
        page = summaries[offset : offset + limit]
        return TransactionSearchResult(items=page, total=total, limit=limit, offset=offset)

    async def _load_rows(
        self, session: AsyncSession, org_id: UUID, transaction_ref: str
    ) -> list[TransactionEventRow]:
        result = await session.execute(
            select(TransactionEventRow).where(
                TransactionEventRow.org_id == org_id,
                TransactionEventRow.transaction_ref == transaction_ref,
            )
        )
        return list(result.scalars())
