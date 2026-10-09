"""The ingestion cascade orchestrator.

normalize_sms tries, in order: the deterministic regex templates, then an
LLM fallback, then gives up and asks the caller to quarantine the input
for a human to resolve. Manual entry and CSV rows skip the cascade
entirely — they carry their own confidence, set by how authoritative the
source is.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from app.contracts.events import DataSource, FinancialEventType, NormalizedFinancialEvent
from app.modules.ingestion.llm_extractor import LlmExtractor
from app.modules.ingestion.sms_parser import SmsParser

MANUAL_CONFIDENCE = 1.0
CSV_CONFIDENCE = 0.95


@dataclass
class IngestionOutcome:
    event: NormalizedFinancialEvent | None
    method: str  # "template" | "llm" | "manual" | "csv" | "quarantined"
    confidence: float
    reason: str
    raw_input: str
    quarantined: bool = False


def compute_source_ref(raw_sms: str, sender: str, occurred_at: datetime) -> str:
    """Stable hash used for ingestion-level duplicate detection.

    Deliberately built only from the raw SMS text, the sender, and the
    *parsed* occurred_at (derived from content inside the message, not
    wall-clock receive time) — so re-ingesting a byte-identical SMS always
    produces the same source_ref, no matter when it's re-ingested.
    """
    basis = f"{sender}|{raw_sms.strip()}|{occurred_at.isoformat()}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def _hash_payload(payload: dict[str, Any]) -> str:
    canonical = "|".join(f"{k}={payload[k]}" for k in sorted(payload))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class Normalizer:
    def __init__(
        self,
        sms_parser: SmsParser | None = None,
        llm_extractor: LlmExtractor | None = None,
    ) -> None:
        self._sms_parser = sms_parser or SmsParser()
        self._llm_extractor = llm_extractor or LlmExtractor()

    async def normalize_sms(
        self,
        raw_sms: str,
        sender: str,
        user_id: UUID,
        received_at: datetime | None = None,
    ) -> IngestionOutcome:
        parse_result = self._sms_parser.parse(raw_sms, sender, user_id, received_at)

        if parse_result.event is not None:
            event = self._with_source_ref(parse_result.event, raw_sms, sender)
            return IngestionOutcome(
                event=event,
                method="template",
                confidence=parse_result.confidence,
                reason=parse_result.reason,
                raw_input=raw_sms,
                quarantined=False,
            )

        llm_event = await self._llm_extractor.extract(
            raw_sms, sender, user_id, received_at
        )
        if llm_event is not None:
            event = self._with_source_ref(llm_event, raw_sms, sender)
            return IngestionOutcome(
                event=event,
                method="llm",
                confidence=event.confidence_score,
                reason="llm extraction",
                raw_input=raw_sms,
                quarantined=False,
            )

        return IngestionOutcome(
            event=None,
            method="quarantined",
            confidence=0.0,
            reason=parse_result.reason,
            raw_input=raw_sms,
            quarantined=True,
        )

    @staticmethod
    def _with_source_ref(
        event: NormalizedFinancialEvent, raw_sms: str, sender: str
    ) -> NormalizedFinancialEvent:
        source_ref = compute_source_ref(raw_sms, sender, event.occurred_at)
        # NormalizedFinancialEvent is frozen — model_copy is the only way
        # to attach the source_ref computed after construction.
        return event.model_copy(update={"source_ref": source_ref})


def normalize_manual(payload: dict[str, Any], user_id: UUID) -> NormalizedFinancialEvent:
    occurred_at = payload["occurred_at"]
    effective_date = occurred_at.date() if isinstance(occurred_at, datetime) else None

    return NormalizedFinancialEvent(
        user_id=user_id,
        event_type=payload["event_type"],
        amount=payload.get("amount"),
        occurred_at=occurred_at,
        effective_date=effective_date,
        counterparty=payload.get("counterparty"),
        category=payload.get("category"),
        description=payload.get("description"),
        data_source=DataSource.manual,
        # The user asserted this event about their own finances directly
        # — nothing in the system is more authoritative about a person's
        # own money than the person themselves.
        confidence_score=MANUAL_CONFIDENCE,
    )


def normalize_csv_row(
    row: dict[str, Any], mapping: dict[str, str], user_id: UUID
) -> NormalizedFinancialEvent:
    """mapping maps our canonical field names to the CSV's own column
    names, e.g. {"amount": "Amount", "occurred_at": "Transaction Date"}."""

    def _get(field: str) -> Any:
        column = mapping.get(field)
        return row.get(column) if column else None

    amount_raw = _get("amount")
    amount: Decimal | None = None
    if amount_raw is not None and str(amount_raw).strip() != "":
        try:
            amount = Decimal(str(amount_raw).replace(",", "").strip())
        except InvalidOperation as exc:
            raise ValueError(f"unparseable amount: {amount_raw!r}") from exc

    occurred_raw = _get("occurred_at")
    if occurred_raw is None or str(occurred_raw).strip() == "":
        raise ValueError("row is missing a value for the mapped occurred_at column")
    occurred_at = _parse_csv_datetime(str(occurred_raw))

    event_type_raw = _get("event_type")
    if not event_type_raw:
        raise ValueError("row is missing a value for the mapped event_type column")
    try:
        event_type = FinancialEventType(str(event_type_raw).strip())
    except ValueError as exc:
        raise ValueError(f"unrecognized event_type: {event_type_raw!r}") from exc

    event = NormalizedFinancialEvent(
        user_id=user_id,
        event_type=event_type,
        amount=amount,
        occurred_at=occurred_at,
        effective_date=occurred_at.date(),
        counterparty=_get("counterparty"),
        category=_get("category"),
        description=_get("description"),
        data_source=DataSource.bank_csv,
        confidence_score=CSV_CONFIDENCE,
        raw_payload={"csv_row": {str(k): str(v) for k, v in row.items()}},
    )

    source_ref = _hash_payload(
        {
            "user_id": str(user_id),
            "amount": str(amount),
            "occurred_at": occurred_at.isoformat(),
            "counterparty": _get("counterparty"),
        }
    )
    return event.model_copy(update={"source_ref": source_ref})


def _parse_csv_datetime(raw: str) -> datetime:
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y"):
        try:
            parsed = datetime.strptime(raw, fmt)
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        parsed_date = date.fromisoformat(raw)
        return datetime.combine(parsed_date, datetime.min.time(), tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError(f"unrecognized date format in CSV row: {raw!r}") from exc
