"""
SQLAlchemy 2.0 declarative tables for FinSentinel.

Money columns use NUMERIC(14, 2) rather than FLOAT: floating point binary
representation cannot exactly represent most decimal fractions, which is
unacceptable for anything that touches money (balances, amounts owed,
reconciliation deltas). NUMERIC stores an exact decimal value.

Tables marked APPEND-ONLY (financial_events, transaction_events) are never
updated or deleted in place. Corrections are modeled as new rows that
reference the row they supersede/duplicate (see superseded_by / duplicate_of
and idempotency_key). This preserves a full audit trail and lets the system
reconstruct state as of any point in time.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

MONEY = Numeric(14, 2)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


# ---------------------------------------------------------------------------
# Identity / access
# ---------------------------------------------------------------------------


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "account_type IN ('person', 'org_member')", name="ck_users_account_type"
        ),
        CheckConstraint(
            "risk_tolerance IN ('conservative', 'balanced', 'aggressive')",
            name="ck_users_risk_tolerance",
        ),
        CheckConstraint(
            "onboarding_stage IN ('declared', 'learning', 'observed')",
            name="ck_users_onboarding_stage",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    account_type: Mapped[str] = mapped_column(String(32), default="person")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    # Global admin flag — no org-scoped role fits app.modules.risk's
    # proposed-rules review endpoints (they aren't org-scoped at all), so
    # this is the minimal addition needed rather than building out a
    # full permissions system. See app.platform.deps.require_admin.
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    risk_tolerance: Mapped[str] = mapped_column(String(32), default="balanced")
    onboarding_stage: Mapped[str] = mapped_column(String(32), default="declared")
    # Per-user override of settings.SHADOW_MODE, for gradual rollout of
    # live interventions to a subset of users before flipping the global
    # default. NULL means "use the global default." See
    # app.modules.decision.shadow.is_shadow_mode.
    shadow_mode_override: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class OrgMembership(Base, TimestampMixin):
    __tablename__ = "org_memberships"
    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'ops_engineer', 'recon_analyst', 'viewer')",
            name="ck_org_memberships_role",
        ),
        UniqueConstraint("user_id", "org_id", name="uq_org_memberships_user_org"),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(32))


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    user_agent: Mapped[str | None] = mapped_column(String(512))


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = _uuid_pk()
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String(255))
    resource_type: Mapped[str | None] = mapped_column(String(255))
    resource_id: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    trace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    endpoint: Mapped[str] = mapped_column(String(255))
    request_hash: Mapped[str] = mapped_column(String(255))
    response_body: Mapped[dict | None] = mapped_column(JSONB)
    status_code: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


# ---------------------------------------------------------------------------
# Financial events (APPEND-ONLY — see module docstring)
# ---------------------------------------------------------------------------


class FinancialEvent(Base):
    __tablename__ = "financial_events"
    __table_args__ = (
        CheckConstraint(
            "amount IS NULL OR amount >= 0", name="ck_financial_events_amount_nonneg"
        ),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="ck_financial_events_confidence_range",
        ),
        Index("ix_financial_events_user_occurred", "user_id", "occurred_at"),
        # Ingestion-level idempotency: re-ingesting the same SMS/CSV row
        # (same user, same computed source_ref) must resolve to the one
        # existing row, never a second insert. NULL source_ref values
        # (e.g. manual entries, which dedupe via Idempotency-Key instead)
        # are intentionally excluded from this constraint.
        Index(
            "uq_financial_events_user_source_ref",
            "user_id",
            "source_ref",
            unique=True,
            postgresql_where=text("source_ref IS NOT NULL"),
            sqlite_where=text("source_ref IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    amount: Mapped[float | None] = mapped_column(MONEY)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    effective_date: Mapped[date | None] = mapped_column(Date)
    counterparty: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(128), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    data_source: Mapped[str] = mapped_column(String(32), index=True)
    source_ref: Mapped[str | None] = mapped_column(String(255))
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3))
    duplicate_of: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    conflicts_with: Mapped[list | None] = mapped_column(JSONB)
    superseded_by: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    raw_payload: Mapped[dict | None] = mapped_column(JSONB)


# ---------------------------------------------------------------------------
# Digital twin state
# ---------------------------------------------------------------------------


class TwinState(Base, TimestampMixin):
    __tablename__ = "twin_states"
    __table_args__ = (
        CheckConstraint(
            "weather IN ('stable', 'pressure', 'risk', 'critical')",
            name="ck_twin_states_weather",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    cash_available: Mapped[float] = mapped_column(MONEY)
    emergency_fund: Mapped[float] = mapped_column(MONEY)
    weather: Mapped[str] = mapped_column(String(32))
    state_confidence: Mapped[float] = mapped_column(Numeric(4, 3))
    unconfirmed_event_count: Mapped[int] = mapped_column(Integer, default=0)
    contains_simulated_data: Mapped[bool] = mapped_column(Boolean, default=False)
    last_event_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    events_applied: Mapped[int] = mapped_column(Integer, default=0)
    # Serialized TwinAccumulator working state (pending_income,
    # obligations_seen, goals, reconciliation_deltas) — everything the
    # fold needs to resume from *without* a full event replay. See
    # app.modules.twin.fold: this is what makes incremental_update a real
    # O(1) update instead of secretly replaying the whole history.
    fold_state: Mapped[dict | None] = mapped_column(JSONB)


class Obligation(Base, TimestampMixin):
    __tablename__ = "obligations"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(MONEY)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    category: Mapped[str | None] = mapped_column(String(128))
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(255))
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    data_source: Mapped[str] = mapped_column(String(32))
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IncomeSource(Base, TimestampMixin):
    """Cold-start income model: starts on declared values, graduates to
    observed statistics (hybrid, then observed) as real events accumulate."""

    __tablename__ = "income_sources"
    __table_args__ = (
        CheckConstraint(
            "forecast_mode IN ('declared', 'hybrid', 'observed')",
            name="ck_income_sources_forecast_mode",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255))
    counterparty: Mapped[str | None] = mapped_column(String(255))
    declared_min: Mapped[float | None] = mapped_column(MONEY)
    declared_max: Mapped[float | None] = mapped_column(MONEY)
    declared_frequency_days: Mapped[int | None] = mapped_column(Integer)
    observed_p10: Mapped[float | None] = mapped_column(MONEY)
    observed_p50: Mapped[float | None] = mapped_column(MONEY)
    observed_p90: Mapped[float | None] = mapped_column(MONEY)
    observed_delay_mean_days: Mapped[float | None] = mapped_column(Numeric(6, 2))
    observed_delay_std_days: Mapped[float | None] = mapped_column(Numeric(6, 2))
    last_received_date: Mapped[date | None] = mapped_column(Date)
    observation_count: Mapped[int] = mapped_column(Integer, default=0)
    forecast_mode: Mapped[str] = mapped_column(String(16), default="declared")
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Goal(Base, TimestampMixin):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("priority >= 1 AND priority <= 5", name="ck_goals_priority"),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255))
    target_amount: Mapped[float] = mapped_column(MONEY)
    saved_amount: Mapped[float] = mapped_column(MONEY, default=0)
    target_date: Mapped[date | None] = mapped_column(Date)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    is_flexible: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    scenarios: Mapped[int] = mapped_column(Integer)
    horizon_days: Mapped[int] = mapped_column(Integer)
    # BigInteger, not Integer: the seed is deliberately a ~63-bit value
    # (app.modules.simulation.builder._seed_from_state hashes user_id +
    # snapshot_id into numpy default_rng's full 64-bit seed range for
    # proper entropy) -- Postgres int32 overflows on the very first real
    # run. SQLite's dynamic typing silently accepted the oversized value
    # in every unit test, which is exactly why this bug was invisible
    # until Step 19 ran against real Postgres.
    random_seed: Mapped[int | None] = mapped_column(BigInteger)
    shortfall_probability: Mapped[float] = mapped_column(Numeric(5, 4))
    first_breach_date: Mapped[date | None] = mapped_column(Date)
    worst_case_balance: Mapped[float] = mapped_column(MONEY)
    time_to_danger_days: Mapped[int | None] = mapped_column(Integer)
    safe_to_spend: Mapped[float] = mapped_column(MONEY)
    inputs_snapshot: Mapped[dict | None] = mapped_column(JSONB)
    percentile_curve: Mapped[dict | None] = mapped_column(JSONB)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


# ---------------------------------------------------------------------------
# Threat detection
# ---------------------------------------------------------------------------


class ThreatEvent(Base):
    __tablename__ = "threat_events"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(16))
    risk_score: Mapped[float] = mapped_column(Numeric(4, 3))
    primary_category: Mapped[str] = mapped_column(String(64))
    signals: Mapped[list | None] = mapped_column(JSONB)
    requested_amount: Mapped[float | None] = mapped_column(MONEY)
    payee_identifier: Mapped[str | None] = mapped_column(String(255))
    raw_reference: Mapped[str | None] = mapped_column(Text)
    transcript_excerpt: Mapped[str | None] = mapped_column(Text)
    data_source: Mapped[str] = mapped_column(String(32))
    detection_confidence: Mapped[float] = mapped_column(Numeric(4, 3))
    # The persisted ThreatImpact (see app.modules.threat.impact) so
    # GET /threat/events/{id} can return the financial-impact assessment
    # without re-running a Monte Carlo simulation on every read.
    financial_impact: Mapped[dict | None] = mapped_column(JSONB)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


# ---------------------------------------------------------------------------
# Decisions / interventions / delivery
# ---------------------------------------------------------------------------


class Intervention(Base):
    __tablename__ = "interventions"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('ignore', 'monitor', 'notify', 'critical')",
            name="ck_interventions_severity",
        ),
        Index(
            "ix_interventions_shadow_severity_outcome",
            "shadow_mode",
            "severity",
            "outcome_materialized",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    severity: Mapped[str] = mapped_column(String(16), index=True)
    severity_raw: Mapped[float] = mapped_column(Numeric(4, 3))
    confidence_ceiling_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    headline: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    triggered_by_event_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True)
    )
    triggered_by_threat_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True)
    )
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    simulation_run_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    probability: Mapped[float] = mapped_column(Numeric(4, 3))
    urgency_score: Mapped[float] = mapped_column(Numeric(4, 3))
    data_confidence: Mapped[float] = mapped_column(Numeric(4, 3))
    decision_trace: Mapped[list | None] = mapped_column(JSONB)
    recommended_actions: Mapped[list | None] = mapped_column(JSONB)
    shadow_mode: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    # Not set anywhere before Step 19: DecisionService.acknowledge() only
    # ever flipped the boolean. shadow_report.generate_shadow_report needs
    # avg_time_to_acknowledge (delivered_at -> acknowledged_at), which is
    # unmeasurable without recording WHEN, not just whether.
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_acted: Mapped[bool] = mapped_column(Boolean, default=False)
    outcome_materialized: Mapped[bool | None] = mapped_column(Boolean)
    outcome_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'sent', 'delivered', 'failed', 'dead_letter')",
            name="ck_notification_deliveries_status",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    intervention_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("interventions.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ---------------------------------------------------------------------------
# Org platform: transactions, reconciliation, dependency graph
# (APPEND-ONLY — see module docstring)
# ---------------------------------------------------------------------------


class TransactionEvent(Base):
    __tablename__ = "transaction_events"
    __table_args__ = (
        UniqueConstraint(
            "org_id", "idempotency_key", name="uq_transaction_events_org_idem"
        ),
        Index(
            "ix_transaction_events_ref_occurred", "transaction_ref", "occurred_at"
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    transaction_ref: Mapped[str] = mapped_column(String(255), index=True)
    stage: Mapped[str] = mapped_column(String(32))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    amount: Mapped[float] = mapped_column(MONEY)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    provider_ref: Mapped[str | None] = mapped_column(String(255))
    error_code: Mapped[str | None] = mapped_column(String(64))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    idempotency_key: Mapped[str] = mapped_column(String(255))
    raw_payload: Mapped[dict | None] = mapped_column(JSONB)


class ReconRun(Base):
    __tablename__ = "recon_runs"

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    started_by: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    matched: Mapped[int] = mapped_column(Integer, default=0)
    missing: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    amount_mismatch: Mapped[int] = mapped_column(Integer, default=0)
    # ReconX (Step 15) classifies TIMING_DIFFERENCE as its own ReconStatus
    # (ref+amount agree, dates differ by >24h) distinct from an unresolved
    # amount mismatch -- this table predates that step and had no column
    # for it.
    timing_differences: Mapped[int] = mapped_column(Integer, default=0)
    unresolved: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="running")
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ReconResult(Base):
    __tablename__ = "recon_results"

    id: Mapped[uuid.UUID] = _uuid_pk()
    run_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("recon_runs.id"), nullable=False
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    transaction_ref: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    internal_amount: Mapped[float | None] = mapped_column(MONEY)
    gateway_amount: Mapped[float | None] = mapped_column(MONEY)
    bank_amount: Mapped[float | None] = mapped_column(MONEY)
    probable_cause: Mapped[str | None] = mapped_column(String(255))
    cause_confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))
    evidence: Mapped[list | None] = mapped_column(JSONB)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    resolution_note: Mapped[str | None] = mapped_column(Text)


class DependencyNode(Base):
    __tablename__ = "dependency_nodes"
    __table_args__ = (
        UniqueConstraint("org_id", "name", name="uq_dependency_nodes_org_name"),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255))
    node_type: Mapped[str] = mapped_column(String(64))
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    alternative_for: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    metadata_json: Mapped[dict | None] = mapped_column(JSONB)


class DependencyEdge(Base):
    __tablename__ = "dependency_edges"
    __table_args__ = (
        UniqueConstraint(
            "from_node_id",
            "to_node_id",
            "edge_type",
            name="uq_dependency_edges_from_to_type",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    from_node_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("dependency_nodes.id"), nullable=False
    )
    to_node_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("dependency_nodes.id"), nullable=False
    )
    edge_type: Mapped[str] = mapped_column(String(64))
    weight: Mapped[float | None] = mapped_column(Numeric(6, 3))


class FailureSimulation(Base):
    """History of "what if X fails?" runs (FinGraph, Step 16) -- kept so
    an org can look back at a past blast-radius estimate rather than only
    ever seeing the current one."""

    __tablename__ = "failure_simulations"

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    failed_node: Mapped[str] = mapped_column(String(255))
    duration_hours: Mapped[float | None] = mapped_column(Numeric(8, 2))
    result: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ---------------------------------------------------------------------------
# RegImpact (Step 17): products, workflows, and regulatory rule tracking
# ---------------------------------------------------------------------------


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("org_id", "name", name="uq_products_org_name"),)

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(128), index=True)


class Workflow(Base, TimestampMixin):
    """A business process (e.g. "new customer onboarding") that uses one
    or more Products and, transitively via FinGraph, one or more
    DependencyNode service nodes.
    """

    __tablename__ = "workflows"
    __table_args__ = (UniqueConstraint("org_id", "name", name="uq_workflows_org_name"),)

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    # Lists of UUIDs (DependencyNode.id / Product.id) as JSON rather than
    # join tables -- this membership changes rarely and is always read as
    # a whole list for one workflow, never queried by individual member.
    uses_service_node_ids: Mapped[list] = mapped_column(JSONB, default=list)
    uses_product_ids: Mapped[list] = mapped_column(JSONB, default=list)


class Regulation(Base):
    __tablename__ = "regulations"

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500))
    source_text: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(1000))
    effective_date: Mapped[date | None] = mapped_column(Date)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ingested_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id")
    )


class RegulatoryRule(Base):
    """One extracted obligation from a Regulation. NEVER auto-activated:
    status starts at 'pending_review' and app.modules.org.regimpact.service
    hard-refuses to run impact analysis on anything but 'confirmed' -- a
    human is accountable for every rule that goes on to affect mapping.
    """

    __tablename__ = "regulatory_rules"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending_review', 'confirmed', 'rejected')",
            name="ck_regulatory_rules_status",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("regulations.id"), nullable=False
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    rule_text: Mapped[str] = mapped_column(Text)
    trigger_condition: Mapped[str] = mapped_column(Text)
    threshold_json: Mapped[dict | None] = mapped_column(JSONB)
    required_action: Mapped[str] = mapped_column(Text)
    deadline_days: Mapped[int | None] = mapped_column(Integer)
    applies_to_product_categories: Mapped[list] = mapped_column(JSONB, default=list)
    extraction_confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))
    # Not in Step 17's original column list, but dropping it silently
    # discards exactly the signal the extractor was told to be careful
    # about: ExtractedRule.ambiguities (app.modules.org.regimpact.extractor)
    # is populated whenever the model was unsure of something, and the
    # Step 18 review queue is REQUIRED to show it prominently alongside
    # low confidence -- there is nowhere else for that list to live.
    ambiguities: Mapped[list] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(16), default="pending_review", index=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id")
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ImpactReport(Base):
    __tablename__ = "impact_reports"

    id: Mapped[uuid.UUID] = _uuid_pk()
    org_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    regulation_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("regulations.id"), nullable=False
    )
    # Not in the spec's literal field list, but required in practice: a
    # regulation commonly yields multiple RegulatoryRule rows, and without
    # this a report can't say WHICH rule it's the impact of.
    rule_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("regulatory_rules.id"), nullable=False
    )
    affected_products: Mapped[list] = mapped_column(JSONB, default=list)
    affected_workflows: Mapped[list] = mapped_column(JSONB, default=list)
    affected_service_nodes: Mapped[list] = mapped_column(JSONB, default=list)
    estimated_transactions: Mapped[int] = mapped_column(Integer, default=0)
    required_changes: Mapped[list] = mapped_column(JSONB, default=list)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ---------------------------------------------------------------------------
# Ingestion quarantine
# ---------------------------------------------------------------------------


class QuarantinedInput(Base):
    """Raw input (SMS, CSV row, ...) that no ingestion method could turn
    into a NormalizedFinancialEvent, kept for the user to resolve
    manually rather than silently dropped."""

    __tablename__ = "quarantined_inputs"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    raw_text: Mapped[str] = mapped_column(Text)
    sender: Mapped[str | None] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(String(255))
    attempted_methods: Mapped[list | None] = mapped_column(JSONB)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


# ---------------------------------------------------------------------------
# Confidence engine: cross-source conflict resolution
# ---------------------------------------------------------------------------


class ConflictRecord(Base):
    """A recorded disagreement between two independent sources describing
    what resolves to the same transaction (e.g. an SMS and a bank CSV row
    reporting different amounts for what is otherwise the same payment).
    The system picks a winner automatically (see
    app.modules.confidence.conflict.resolve_conflict); user_overridden
    tracks whether a human later confirmed or corrected that pick."""

    __tablename__ = "conflict_records"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    event_a_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("financial_events.id"), nullable=False
    )
    event_b_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("financial_events.id"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(64))
    value_a: Mapped[str] = mapped_column(String(255))
    value_b: Mapped[str] = mapped_column(String(255))
    winner_event_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("financial_events.id"), nullable=False
    )
    winner_reason: Mapped[str] = mapped_column(Text)
    resolved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    user_overridden: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


# ---------------------------------------------------------------------------
# Twin: detected recurring obligation candidates awaiting user confirmation
# ---------------------------------------------------------------------------


class RecurringCandidate(Base, TimestampMixin):
    """A pattern app.modules.twin.obligations.detect_recurring found in a
    user's event history that looks like a recurring bill, but hasn't
    been turned into a real Obligation yet — that only happens once the
    user confirms it via POST /twin/recurring/{id}/confirm."""

    __tablename__ = "recurring_candidates"
    __table_args__ = (
        CheckConstraint(
            "detection_method IN ('statistical', 'llm')",
            name="ck_recurring_candidates_detection_method",
        ),
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'dismissed')",
            name="ck_recurring_candidates_status",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    counterparty: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(128))
    suggested_amount: Mapped[float] = mapped_column(MONEY)
    interval_days: Mapped[int] = mapped_column(Integer)
    day_of_month: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3))
    detection_method: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    evidence_event_ids: Mapped[list | None] = mapped_column(JSONB)


# ---------------------------------------------------------------------------
# Risk: collision detection and offline rule discovery
# ---------------------------------------------------------------------------


class CollisionRecord(Base):
    """A detected combination of individually-normal conditions whose
    joint shortfall probability substantially exceeds their individual
    contributions — see app.modules.risk.collision.detect_collisions.
    resolved_at/resolution_reason track BOTH auto-resolution (the
    underlying conditions stopped holding on a later assessment) and a
    user's explicit dismissal."""

    __tablename__ = "collision_records"
    __table_args__ = (
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')", name="ck_collision_records_severity"
        ),
        CheckConstraint(
            "urgency IN ('low', 'medium', 'high', 'critical')", name="ck_collision_records_urgency"
        ),
        Index("ix_collision_records_user_resolved", "user_id", "resolved_at"),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    condition_ids: Mapped[list] = mapped_column(JSONB)
    joint_probability: Mapped[float] = mapped_column(Numeric(5, 4))
    individual_probabilities: Mapped[dict] = mapped_column(JSONB)
    amplification_factor: Mapped[float] = mapped_column(Numeric(8, 4))
    severity: Mapped[str] = mapped_column(String(16), index=True)
    urgency: Mapped[str] = mapped_column(String(16))
    first_impact_date: Mapped[date | None] = mapped_column(Date)
    evidence: Mapped[dict] = mapped_column(JSONB)
    human_statement: Mapped[str] = mapped_column(Text)
    simulation_run_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("simulation_runs.id")
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_reason: Mapped[str | None] = mapped_column(String(255))


class ProposedRuleRecord(Base):
    """An OFFLINE-discovered candidate rule (see
    app.modules.risk.discovery.propose_rules) — statistically derived
    from historical CollisionRecords, optionally phrased by an LLM.

    HARD REQUIREMENT, enforced by construction, not just convention:
    nothing anywhere reads status='pending_review' rows into
    RULE_REGISTRY. A proposed rule only affects the runtime risk path
    once a human explicitly approves it (POST
    /risk/proposed-rules/{id}/approve), which is a separate, audited
    action — never automatic. The LLM proposes; a human activates.
    """

    __tablename__ = "proposed_rule_records"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending_review', 'approved', 'rejected')",
            name="ck_proposed_rule_records_status",
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    suggested_conditions: Mapped[list] = mapped_column(JSONB)
    support: Mapped[int] = mapped_column(Integer)
    lift: Mapped[float] = mapped_column(Numeric(8, 4))
    proposed_threshold: Mapped[dict | None] = mapped_column(JSONB)
    llm_rationale: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="pending_review", index=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
