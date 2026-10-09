"""API request/response DTOs for confidence endpoints.

Plain Pydantic models, not the frozen event/state contracts in
app/contracts — these describe HTTP wire shapes for this router only.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StateConfidenceResponse(BaseModel):
    score: float
    unconfirmed_count: int
    conflicted_count: int
    simulated_count: int
    contributing_events: int
    breakdown: dict[str, Any]


class ConflictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_a_id: UUID
    event_b_id: UUID
    field_name: str
    value_a: str
    value_b: str
    winner_event_id: UUID
    winner_reason: str
    resolved_at: datetime
    user_overridden: bool


class ConflictOverrideRequest(BaseModel):
    correct_event_id: UUID


class DuplicateResponse(BaseModel):
    id: UUID
    duplicate_of: UUID
    event_type: str
    amount: Decimal | None
    occurred_at: datetime
    counterparty: str | None
    data_source: str
    similarity: float
    reasons: list[str]


class UnmergeResponse(BaseModel):
    event_id: UUID
    unmerged: bool
    state_confidence: float
