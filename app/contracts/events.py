"""
Event and state contracts for FinSentinel.

These contracts are FROZEN. Once a contract ships, its fields never change:
no renaming, no retyping, no adding/removing required fields. If a contract
needs to evolve, add a new versioned class (e.g. NormalizedFinancialEventV2)
rather than editing this one in place. Every consumer across every module
and every historical event/row on disk depends on the shape staying exactly
as declared here.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

SCHEMA_VERSION = 1


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class DataSource(str, Enum):
    sms = "sms"
    bank_csv = "bank_csv"
    manual = "manual"
    receipt_ocr = "receipt_ocr"
    simulated = "simulated"
    system = "system"


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class FinancialEventType(str, Enum):
    income_received = "income_received"
    income_expected = "income_expected"
    income_delayed = "income_delayed"
    expense = "expense"
    bill_due = "bill_due"
    bill_paid = "bill_paid"
    emi_due = "emi_due"
    emi_paid = "emi_paid"
    transfer_in = "transfer_in"
    transfer_out = "transfer_out"
    balance_snapshot = "balance_snapshot"
    goal_created = "goal_created"
    goal_updated = "goal_updated"


class FinancialWeather(str, Enum):
    stable = "stable"
    pressure = "pressure"
    risk = "risk"
    critical = "critical"


class ThreatChannel(str, Enum):
    call = "call"
    sms = "sms"
    qr = "qr"
    link = "link"


class ThreatCategory(str, Enum):
    bank_impersonation = "bank_impersonation"
    otp_request = "otp_request"
    kyc_scam = "kyc_scam"
    upi_scam = "upi_scam"
    phishing_link = "phishing_link"
    malicious_qr = "malicious_qr"
    social_engineering = "social_engineering"
    urgency_manipulation = "urgency_manipulation"
    credential_request = "credential_request"
    unknown = "unknown"


class Severity(str, Enum):
    ignore = "ignore"
    monitor = "monitor"
    notify = "notify"
    critical = "critical"


class TxnStage(str, Enum):
    initiated = "initiated"
    gateway_accepted = "gateway_accepted"
    gateway_failed = "gateway_failed"
    bank_accepted = "bank_accepted"
    bank_failed = "bank_failed"
    webhook_sent = "webhook_sent"
    webhook_failed = "webhook_failed"
    settled = "settled"
    settlement_failed = "settlement_failed"
    refunded = "refunded"


class ReconStatus(str, Enum):
    matched = "matched"
    missing_in_bank = "missing_in_bank"
    missing_in_gateway = "missing_in_gateway"
    missing_in_internal = "missing_in_internal"
    duplicate = "duplicate"
    amount_mismatch = "amount_mismatch"
    timing_difference = "timing_difference"
    unresolved = "unresolved"


class Topic(str, Enum):
    financial_events = "financial.events"
    threat_events = "threat.events"
    state_snapshots = "state.snapshots"
    decision_interventions = "decision.interventions"
    org_transactions = "org.transactions"
    org_recon = "org.recon"
    system_dlq = "system.dlq"


# ---------------------------------------------------------------------------
# Contract 1 — NormalizedFinancialEvent
# ---------------------------------------------------------------------------


class NormalizedFinancialEvent(FrozenModel):
    schema_version: int = SCHEMA_VERSION
    event_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    event_type: FinancialEventType
    amount: Decimal | None = None
    currency: Literal["INR"] = "INR"
    occurred_at: datetime
    ingested_at: datetime = Field(default_factory=_utcnow)
    effective_date: date | None = None
    counterparty: str | None = None
    category: str | None = None
    description: str | None = None
    data_source: DataSource
    source_ref: str | None = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    duplicate_of: UUID | None = None
    conflicts_with: list[UUID] = Field(default_factory=list)
    raw_payload: dict = Field(default_factory=dict)

    @field_validator("amount")
    @classmethod
    def amount_must_be_non_negative(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v < 0:
            raise ValueError(
                "amount must be >= 0; direction is encoded in event_type, "
                "not in the sign of amount"
            )
        return v

    @property
    def confidence_band(self) -> Confidence:
        if self.confidence_score >= 0.75:
            return Confidence.high
        if self.confidence_score >= 0.50:
            return Confidence.medium
        return Confidence.low


# ---------------------------------------------------------------------------
# Contract 2 — FinancialStateSnapshot and supporting models
# ---------------------------------------------------------------------------


class Obligation(FrozenModel):
    obligation_id: UUID = Field(default_factory=uuid4)
    label: str
    amount: Decimal
    due_date: date
    category: str | None = None
    is_fixed: bool
    is_paid: bool
    confidence_score: float = Field(ge=0.0, le=1.0)


class IncomeForecast(FrozenModel):
    expected_min: Decimal | None = None
    expected_max: Decimal | None = None
    p10: Decimal | None = None
    p50: Decimal | None = None
    p90: Decimal | None = None
    expected_arrival: date | None = None
    arrival_uncertainty_days: int | None = None
    source: Literal["declared", "observed", "hybrid"]
    sample_size: int = 0
    confidence_score: float = Field(ge=0.0, le=1.0)


class Goal(FrozenModel):
    goal_id: UUID = Field(default_factory=uuid4)
    label: str
    target_amount: Decimal
    saved_amount: Decimal
    target_date: date | None = None
    priority: int = Field(ge=1, le=5)
    is_flexible: bool


class ShortfallRisk(FrozenModel):
    horizon_days: int
    probability: float = Field(ge=0.0, le=1.0)
    first_breach_date: date | None = None
    worst_case_balance: Decimal
    scenarios_run: int


class FinancialStateSnapshot(FrozenModel):
    schema_version: int = SCHEMA_VERSION
    snapshot_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    generated_at: datetime = Field(default_factory=_utcnow)
    cash_available: Decimal
    emergency_fund: Decimal
    income_forecast: IncomeForecast
    obligations: list[Obligation] = Field(default_factory=list)
    goals: list[Goal] = Field(default_factory=list)
    weather: FinancialWeather
    shortfall_risks: list[ShortfallRisk] = Field(default_factory=list)
    time_to_danger_days: int | None = None
    safe_to_spend: Decimal
    state_confidence: float = Field(ge=0.0, le=1.0)
    unconfirmed_event_count: int = 0
    contains_simulated_data: bool = False
    last_event_id: UUID | None = None
    events_applied: int = 0

    @property
    def total_fixed_obligations(self) -> Decimal:
        return sum(
            (o.amount for o in self.obligations if o.is_fixed and not o.is_paid),
            Decimal("0"),
        )


# ---------------------------------------------------------------------------
# Contract 3 — ThreatSignal / ThreatEvent
# ---------------------------------------------------------------------------


class ThreatSignal(FrozenModel):
    name: str
    category: ThreatCategory
    weight: float = Field(ge=0.0, le=100.0)
    evidence: str | None = None
    detector: Literal["rule", "model", "hybrid"]


class ThreatEvent(FrozenModel):
    schema_version: int = SCHEMA_VERSION
    threat_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    detected_at: datetime = Field(default_factory=_utcnow)
    channel: ThreatChannel
    risk_score: float = Field(ge=0.0, le=1.0)
    signals: list[ThreatSignal] = Field(default_factory=list)
    primary_category: ThreatCategory
    requested_amount: Decimal | None = None
    payee_identifier: str | None = None
    raw_reference: str | None = None
    transcript_excerpt: str | None = None
    data_source: DataSource
    detection_confidence: float = Field(ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Contract 4 — ContextualIntervention and supporting models
# ---------------------------------------------------------------------------


class TraceStep(FrozenModel):
    order: int
    stage: str
    statement: str
    values: dict = Field(default_factory=dict)


class RecommendedAction(FrozenModel):
    action_type: str
    label: str
    amount: Decimal | None = None
    expected_effect: str | None = None
    projected_risk_after: float | None = Field(default=None, ge=0.0, le=1.0)


class ContextualIntervention(FrozenModel):
    schema_version: int = SCHEMA_VERSION
    intervention_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    created_at: datetime = Field(default_factory=_utcnow)
    severity: Severity
    headline: str
    body: str
    triggered_by_event_id: UUID | None = None
    triggered_by_threat_id: UUID | None = None
    snapshot_id: UUID | None = None
    severity_raw: float = Field(ge=0.0, le=1.0)
    confidence_ceiling_applied: bool = False
    probability: float = Field(ge=0.0, le=1.0)
    urgency_score: float = Field(ge=0.0, le=1.0)
    data_confidence: float = Field(ge=0.0, le=1.0)
    decision_trace: list[TraceStep] = Field(default_factory=list)
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)
    shadow_mode: bool = True
    delivered: bool = False


# ---------------------------------------------------------------------------
# Contract 5 — Org/platform transaction, reconciliation, and impact models
# ---------------------------------------------------------------------------


class TransactionEvent(FrozenModel):
    schema_version: int = SCHEMA_VERSION
    event_id: UUID = Field(default_factory=uuid4)
    org_id: UUID
    transaction_ref: str
    stage: TxnStage
    occurred_at: datetime
    amount: Decimal
    provider: str
    provider_ref: str | None = None
    error_code: str | None = None
    latency_ms: int | None = None
    idempotency_key: str
    raw_payload: dict = Field(default_factory=dict)


class ReconciliationResult(FrozenModel):
    result_id: UUID = Field(default_factory=uuid4)
    org_id: UUID
    run_id: UUID
    transaction_ref: str
    status: ReconStatus
    internal_amount: Decimal | None = None
    gateway_amount: Decimal | None = None
    bank_amount: Decimal | None = None
    probable_cause: str | None = None
    cause_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class ImpactResult(FrozenModel):
    impact_id: UUID = Field(default_factory=uuid4)
    org_id: UUID
    failed_node: str
    affected_services: list[str] = Field(default_factory=list)
    affected_workflows: list[str] = Field(default_factory=list)
    estimated_transactions: int = 0
    critical_paths: list[list[str]] = Field(default_factory=list)
    alternative_providers: list[str] = Field(default_factory=list)
