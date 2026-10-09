"""API request/response DTOs for PayTrace (Step 14).

Plain Pydantic models, not the frozen event/state contracts in
app/contracts — these describe HTTP wire shapes for this router only.
org_id is always taken from the URL path (and checked via require_roles),
never from the request body, so a caller can't ingest an event under a
different org than the one they're authorized against.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.contracts.events import TxnStage


class TransactionEventRequest(BaseModel):
    transaction_ref: str = Field(min_length=1, max_length=255)
    stage: TxnStage
    occurred_at: datetime
    amount: Decimal
    provider: str = Field(min_length=1, max_length=64)
    provider_ref: str | None = None
    error_code: str | None = None
    latency_ms: int | None = None
    idempotency_key: str = Field(min_length=1, max_length=255)
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class TransactionEventBatchRequest(BaseModel):
    events: list[TransactionEventRequest] = Field(min_length=1, max_length=500)


class TimelineEntryResponse(BaseModel):
    stage: str
    occurred_at: datetime
    amount: Decimal
    provider: str
    provider_ref: str | None
    error_code: str | None
    latency_ms: int | None


class AnomalyResponse(BaseModel):
    kind: str
    description: str
    from_stage: str | None
    to_stage: str | None
    occurred_at: datetime | None
    gap_ms: int | None


class ClassificationResponse(BaseModel):
    mode: str
    confidence: float
    evidence: dict[str, Any]
    recommended_action: str | None
    human_summary: str


class TransactionStateResponse(BaseModel):
    transaction_ref: str | None
    current_stage: str | None
    timeline: list[TimelineEntryResponse]
    anomalies: list[AnomalyResponse]
    duration_by_stage: dict[str, int]
    total_duration_ms: int | None
    is_terminal: bool


class TransactionDetailResponse(BaseModel):
    state: TransactionStateResponse
    classification: ClassificationResponse


class TransactionSummaryResponse(BaseModel):
    transaction_ref: str
    current_stage: str | None
    provider: str | None
    last_event_at: datetime | None
    is_terminal: bool
    failure_mode: str
    confidence: float
    recommended_action: str | None


class TransactionSearchResponse(BaseModel):
    items: list[TransactionSummaryResponse]
    total: int
    limit: int
    offset: int


class ProviderStatsResponse(BaseModel):
    provider: str
    total_transactions: int
    success_rate: float
    avg_latency_ms: float | None
    failure_breakdown: dict[str, int]


class PaymentHealthResponse(BaseModel):
    total_transactions: int
    success_rate: float
    failure_breakdown: dict[str, int]
    avg_latency_by_stage: dict[str, float]
    p95_latency_by_stage: dict[str, float]
    webhook_success_rate: float | None
    settlement_success_rate: float
    providers: list[ProviderStatsResponse]
    anomaly_count: int
    computed_at: datetime


class ProviderAlertResponse(BaseModel):
    provider: str
    current_failure_rate: float
    baseline_failure_rate: float
    ratio: float | None
    current_transaction_count: int
    message: str
