"""ReconX ingestion — parse and normalize internal, gateway, and bank
records into a single common shape before matching.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from io import BytesIO, StringIO
from typing import Any, Literal
from uuid import UUID

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import FrozenModel

SourceName = Literal["internal", "gateway", "bank"]


class ReconRecord(FrozenModel):
    source: SourceName
    transaction_ref: str
    amount: Decimal
    currency: str = "INR"
    occurred_at: datetime
    counterparty: str | None = None
    status: str | None = None
    raw_fields: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Reference normalization
# ---------------------------------------------------------------------------

_TOKEN_SPLIT_RE = re.compile(r"[-\s]+")
_HAS_LETTER_RE = re.compile(r"[A-Z]")
_HAS_DIGIT_RE = re.compile(r"\d")


def normalize_ref(ref: str) -> str:
    """Banks and gateways format references differently ("ACME-TX8921-0112"
    vs "TX8921") -- normalization is the first step to matching them.

    Split on hyphens/spaces, uppercase, then keep the token(s) that mix
    letters AND digits (the actual transaction id, e.g. "TX8921") while
    dropping pure-alpha tokens (merchant/prefix codes like "ACME") and
    pure-numeric tokens (sequence numbers / date suffixes like "0112").
    If no token is a letter+digit mix (e.g. a purely numeric ref), fall
    back to the whole cleaned string.
    """
    cleaned = ref.strip().upper()
    tokens = [t for t in _TOKEN_SPLIT_RE.split(cleaned) if t]
    mixed = [t for t in tokens if _HAS_LETTER_RE.search(t) and _HAS_DIGIT_RE.search(t)]
    if mixed:
        return "".join(mixed)
    return "".join(tokens)


# ---------------------------------------------------------------------------
# Field normalization
# ---------------------------------------------------------------------------

_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "transaction_ref": ("transaction_ref", "ref", "reference", "txn_ref", "transaction_id"),
    "amount": ("amount", "amt", "value"),
    "occurred_at": ("occurred_at", "date", "txn_date", "transaction_date", "timestamp"),
    "counterparty": ("counterparty", "payee", "merchant", "counter_party"),
    "status": ("status", "state"),
    "currency": ("currency", "curr"),
}


def _pick(lower_row: dict[str, Any], field_name: str) -> Any | None:
    for alias in _FIELD_ALIASES[field_name]:
        value = lower_row.get(alias)
        if value not in (None, ""):
            return value
    return None


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            import pandas as pd  # deferred: only needed for odd date formats

            parsed = pd.Timestamp(text).to_pydatetime()
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _parse_amount(value: Any) -> Decimal:
    text = str(value).replace(",", "").replace("₹", "").strip()
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Could not parse amount: {value!r}") from exc


def _to_recon_record(source: SourceName, row: dict[str, Any]) -> ReconRecord:
    lower_row = {str(k).strip().lower(): v for k, v in row.items()}

    ref = _pick(lower_row, "transaction_ref")
    amount_raw = _pick(lower_row, "amount")
    occurred_raw = _pick(lower_row, "occurred_at")
    if ref is None or amount_raw is None or occurred_raw is None:
        raise ValueError(
            f"{source} record missing a required field (transaction_ref/amount/occurred_at): {row}"
        )

    status_raw = _pick(lower_row, "status")
    return ReconRecord(
        source=source,
        transaction_ref=str(ref),
        amount=_parse_amount(amount_raw),
        currency=str(_pick(lower_row, "currency") or "INR"),
        occurred_at=_parse_datetime(occurred_raw),
        counterparty=(
            str(counterparty) if (counterparty := _pick(lower_row, "counterparty")) is not None else None
        ),
        status=str(status_raw) if status_raw is not None else None,
        raw_fields=dict(row),
    )


def _parse_csv(content: str | bytes) -> list[dict[str, Any]]:
    import pandas as pd

    buffer = BytesIO(content) if isinstance(content, bytes) else StringIO(content)
    df = pd.read_csv(buffer)
    # Replace NaN with None so downstream normalization sees a real
    # missing value rather than pandas' float NaN sentinel.
    return df.astype(object).where(df.notna(), None).to_dict(orient="records")  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Public ingestion entrypoints
# ---------------------------------------------------------------------------


async def ingest_internal(
    session: AsyncSession, org_id: UUID, records: list[dict[str, Any]]
) -> list[ReconRecord]:
    return [_to_recon_record("internal", r) for r in records]


async def ingest_gateway(
    session: AsyncSession, org_id: UUID, records: list[dict[str, Any]]
) -> list[ReconRecord]:
    return [_to_recon_record("gateway", r) for r in records]


async def ingest_bank(
    session: AsyncSession, org_id: UUID, file_or_records: list[dict[str, Any]] | str | bytes
) -> list[ReconRecord]:
    """Bank statements commonly arrive as a CSV export, unlike internal
    ledger dumps or gateway API responses -- this is the one source that
    also accepts raw CSV content directly.
    """
    rows = file_or_records if isinstance(file_or_records, list) else _parse_csv(file_or_records)
    return [_to_recon_record("bank", r) for r in rows]
