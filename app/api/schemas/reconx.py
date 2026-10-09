"""API request/response DTOs for ReconX (Step 15).

Plain Pydantic models, not the frozen event/state contracts in
app/contracts — these describe HTTP wire shapes for this router only.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ReconRunRequest(BaseModel):
    internal: list[dict[str, Any]] = Field(default_factory=list)
    gateway: list[dict[str, Any]] = Field(default_factory=list)
    # Bank data can arrive as parsed records OR raw CSV text (the one
    # source that commonly shows up as a statement export rather than an
    # API response/ledger dump).
    bank: list[dict[str, Any]] | str = Field(default_factory=list)

    amount_tolerance_pct: float = 0.01
    amount_tolerance_abs: Decimal = Decimal("1.00")
    time_window_hours: int = 72
    ref_similarity_threshold: float = 0.85


class ResolveRequest(BaseModel):
    resolution_note: str = Field(min_length=1, max_length=2000)


class ReconResultResponse(BaseModel):
    result_id: UUID
    run_id: UUID
    transaction_ref: str
    status: str
    internal_amount: Decimal | None
    gateway_amount: Decimal | None
    bank_amount: Decimal | None
    probable_cause: str | None
    cause_confidence: float | None
    evidence: list[str]
    resolved: bool
    resolved_by: UUID | None
    resolution_note: str | None


class ReconRunSummaryResponse(BaseModel):
    run_id: UUID
    period_start: datetime
    period_end: datetime
    total_records: int
    matched: int
    missing: int
    duplicates: int
    amount_mismatches: int
    timing_differences: int
    unresolved: int
    status: str
    duration_ms: int | None
    created_at: datetime


class ReconRunDetailResponse(BaseModel):
    summary: ReconRunSummaryResponse
    results: list[ReconResultResponse]
