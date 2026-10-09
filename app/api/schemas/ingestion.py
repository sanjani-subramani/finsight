"""API request/response DTOs for ingestion endpoints.

Plain Pydantic models, not the frozen event/state contracts in
app/contracts — these describe HTTP wire shapes for this router only.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.events import FinancialEventType


class SmsIngestRequest(BaseModel):
    raw_sms: str = Field(min_length=1, max_length=2000)
    sender: str = Field(default="", max_length=64)
    received_at: datetime | None = None


class ManualEventRequest(BaseModel):
    event_type: FinancialEventType
    amount: Decimal | None = None
    occurred_at: datetime
    counterparty: str | None = None
    category: str | None = None
    description: str | None = None


class CsvImportRequest(BaseModel):
    # Canonical field name -> CSV column name, e.g.
    # {"amount": "Amount", "occurred_at": "Txn Date", "event_type": "Type"}
    column_mapping: dict[str, str]


class IngestionResponse(BaseModel):
    event_id: UUID | None
    method: str
    confidence: float
    was_duplicate: bool
    quarantined: bool
    reason: str | None = None


class IngestAcceptedResponse(BaseModel):
    trace_id: str
    event_id: UUID | None
    quarantined: bool
    reason: str | None = None
    status: str


class IngestionStatusResponse(BaseModel):
    trace_id: str
    status: str


class BatchIngestionResponse(BaseModel):
    processed: int
    created: int
    duplicates: int
    quarantined: int
    results: list[IngestionResponse]


class QuarantinedInputResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    raw_text: str
    sender: str | None
    reason: str
    attempted_methods: list[str] | None
    resolved: bool
    created_at: datetime


class FinancialEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: str
    amount: Decimal | None
    currency: str
    occurred_at: datetime
    effective_date: date | None
    counterparty: str | None
    category: str | None
    description: str | None
    data_source: str
    source_ref: str | None
    confidence_score: Decimal
