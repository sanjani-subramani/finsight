"""API request/response DTOs for the Scam Shield (Step 10)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SmsThreatRequest(BaseModel):
    body: str
    sender: str = ""


class UrlThreatRequest(BaseModel):
    url: str


class QrThreatRequest(BaseModel):
    qr_payload: str
    claimed_merchant_name: str | None = None


class CallThreatRequest(BaseModel):
    transcript: str


class ThreatSignalResponse(BaseModel):
    name: str
    category: str
    weight: float
    evidence: str | None
    detector: str


class ThreatImpactResponse(BaseModel):
    would_cause_shortfall: bool
    prob_before: float
    prob_after: float
    obligations_at_risk: list[str]
    days_until_first_impact: int | None
    human_statement: str


class ThreatEventResponse(BaseModel):
    threat_id: UUID
    channel: str
    risk_score: float
    primary_category: str
    signals: list[ThreatSignalResponse]
    requested_amount: Decimal | None
    payee_identifier: str | None
    detected_at: datetime
    impact: ThreatImpactResponse | None = None


class ThreatEventSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    channel: str
    risk_score: float
    primary_category: str
    detected_at: datetime


class ThreatEventDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    channel: str
    risk_score: float
    primary_category: str
    signals: list[ThreatSignalResponse]
    requested_amount: Decimal | None
    payee_identifier: str | None
    raw_reference: str | None
    transcript_excerpt: str | None
    data_source: str
    detection_confidence: float
    financial_impact: ThreatImpactResponse | None
    detected_at: datetime
