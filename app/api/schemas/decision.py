"""API request/response DTOs for decision (intervention) endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TraceStepResponse(BaseModel):
    order: int
    stage: str
    statement: str
    values: dict[str, Any]


class InterventionSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    severity: str
    severity_raw: float
    confidence_ceiling_applied: bool
    headline: str
    body: str
    probability: float
    urgency_score: float
    data_confidence: float
    shadow_mode: bool
    delivered: bool
    user_acknowledged: bool
    user_acted: bool
    outcome_materialized: bool | None
    created_at: datetime


class RecommendedActionResponse(BaseModel):
    action_type: str
    label: str
    amount: Decimal | None
    expected_effect: str | None
    projected_risk_after: float | None


class InterventionDetailResponse(InterventionSummaryResponse):
    triggered_by_event_id: UUID | None
    triggered_by_threat_id: UUID | None
    snapshot_id: UUID | None
    simulation_run_id: UUID | None
    outcome_checked_at: datetime | None
    decision_trace: list[TraceStepResponse]
    # Step 11 populates this on the ORM row (Intervention.recommended_actions,
    # JSONB) but the response schema never exposed it until now — clients
    # (the Flutter alerts screen) need projected_risk_after per action.
    recommended_actions: list[RecommendedActionResponse]


class ActedRequest(BaseModel):
    acted: bool


class SeverityPrecisionResponse(BaseModel):
    severity: str
    total_fired: int
    total_checked: int
    materialized: int
    precision: float | None
    false_alarm_rate: float | None


class PrecisionReportResponse(BaseModel):
    since: datetime
    by_severity: dict[str, SeverityPrecisionResponse]
    confidence_ceiling_total: int
    confidence_ceiling_checked: int
    confidence_ceiling_saves: int
    confidence_ceiling_save_rate: float | None
