"""Aggregate PayTrace analysis across many transactions for one org.

This is the data behind the ops dashboard: overall health, per-provider
comparison ("Provider A is failing 17% while Provider B is at 2% --
switch."), and early-warning alerts when a provider's failure rate spikes
well above its own recent normal.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import TransactionEvent, TxnStage
from app.models.tables import TransactionEvent as TransactionEventRow
from app.modules.org.paytrace.classifier import FailureClassification, FailureClassifier, FailureMode
from app.modules.org.paytrace.state_machine import TransactionState, derive_state
from app.platform.timeutils import as_aware_utc

# A provider's current failure rate must be based on at least this many
# transactions before it's eligible for a degradation alert -- otherwise
# one or two unlucky transactions on a low-volume provider would trigger a
# false alarm every hour.
MIN_TRANSACTIONS_FOR_ALERT = 5

# When a provider has NO failures at all in its 7-day baseline, a ratio
# against zero is undefined; fall back to an absolute threshold instead.
NO_BASELINE_FAILURE_RATE_THRESHOLD = 0.10

DEGRADATION_RATIO_THRESHOLD = 3.0
BASELINE_WINDOW_DAYS = 7


def _row_to_event(row: TransactionEventRow) -> TransactionEvent:
    return TransactionEvent(
        event_id=row.id,
        org_id=row.org_id,
        transaction_ref=row.transaction_ref,
        stage=TxnStage(row.stage),
        occurred_at=as_aware_utc(row.occurred_at),
        amount=Decimal(str(row.amount)),
        provider=row.provider,
        provider_ref=row.provider_ref,
        error_code=row.error_code,
        latency_ms=row.latency_ms,
        idempotency_key=row.idempotency_key,
        raw_payload=row.raw_payload or {},
    )


async def _load_states(
    session: AsyncSession, org_id: UUID, window_start: datetime, window_end: datetime | None = None
) -> dict[str, TransactionState]:
    conditions = [TransactionEventRow.org_id == org_id, TransactionEventRow.occurred_at >= window_start]
    if window_end is not None:
        conditions.append(TransactionEventRow.occurred_at < window_end)

    result = await session.execute(select(TransactionEventRow).where(*conditions))
    rows = list(result.scalars())

    by_ref: dict[str, list[TransactionEvent]] = defaultdict(list)
    for row in rows:
        by_ref[row.transaction_ref].append(_row_to_event(row))

    return {ref: derive_state(events) for ref, events in by_ref.items()}


def _settlement_latency_ms(state: TransactionState) -> int | None:
    for candidate in (TxnStage.webhook_sent, TxnStage.webhook_failed, TxnStage.bank_accepted):
        latency = state.duration_by_stage.get(candidate)
        if latency is not None:
            return latency
    return None


def _provider_of(state: TransactionState) -> str | None:
    if not state.timeline:
        return None
    return state.timeline[-1].provider


def _p95_settlement_by_provider(states: list[TransactionState]) -> dict[str, float]:
    latencies_by_provider: dict[str, list[int]] = defaultdict(list)
    for state in states:
        if state.current_stage != TxnStage.settled:
            continue
        latency = _settlement_latency_ms(state)
        provider = _provider_of(state)
        if latency is not None and provider is not None:
            latencies_by_provider[provider].append(latency)

    return {
        provider: float(np.percentile(values, 95))
        for provider, values in latencies_by_provider.items()
        if values
    }


@dataclass(frozen=True)
class ProviderStats:
    provider: str
    total_transactions: int
    success_rate: float
    avg_latency_ms: float | None
    failure_breakdown: dict[FailureMode, int] = field(default_factory=dict)


@dataclass(frozen=True)
class PaymentHealth:
    org_id: UUID
    window_hours: int
    total_transactions: int
    success_rate: float
    failure_breakdown: dict[FailureMode, int]
    avg_latency_by_stage: dict[TxnStage, float]
    p95_latency_by_stage: dict[TxnStage, float]
    webhook_success_rate: float | None
    settlement_success_rate: float
    providers: list[ProviderStats]
    anomaly_count: int
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ProviderAlert:
    provider: str
    current_failure_rate: float
    baseline_failure_rate: float
    ratio: float | None
    current_transaction_count: int
    message: str


async def compute_health(session: AsyncSession, org_id: UUID, window_hours: int = 24) -> PaymentHealth:
    window_start = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    states = list((await _load_states(session, org_id, window_start)).values())

    total = len(states)
    provider_p95 = _p95_settlement_by_provider(states)
    classifier = FailureClassifier(provider_p95_settlement_ms=provider_p95)
    classifications = [classifier.classify(state) for state in states]

    successful = sum(1 for c in classifications if c.mode == FailureMode.SUCCESSFUL)
    success_rate = successful / total if total else 0.0
    failure_breakdown = dict(Counter(c.mode for c in classifications))

    stage_durations: dict[TxnStage, list[int]] = defaultdict(list)
    for state in states:
        for stage, duration_ms in state.duration_by_stage.items():
            stage_durations[stage].append(duration_ms)
    avg_latency_by_stage = {stage: float(np.mean(values)) for stage, values in stage_durations.items()}
    p95_latency_by_stage = {stage: float(np.percentile(values, 95)) for stage, values in stage_durations.items()}

    webhook_attempted = [
        state
        for state in states
        if any(e.stage in (TxnStage.webhook_sent, TxnStage.webhook_failed) for e in state.timeline)
    ]
    webhook_succeeded = [
        state for state in webhook_attempted if any(e.stage == TxnStage.webhook_sent for e in state.timeline)
    ]
    webhook_success_rate = len(webhook_succeeded) / len(webhook_attempted) if webhook_attempted else None

    settled_count = sum(1 for state in states if any(e.stage == TxnStage.settled for e in state.timeline))
    settlement_success_rate = settled_count / total if total else 0.0

    anomaly_count = sum(len(state.anomalies) for state in states)

    providers = _provider_breakdown(states, classifications)

    return PaymentHealth(
        org_id=org_id,
        window_hours=window_hours,
        total_transactions=total,
        success_rate=success_rate,
        failure_breakdown=failure_breakdown,
        avg_latency_by_stage=avg_latency_by_stage,
        p95_latency_by_stage=p95_latency_by_stage,
        webhook_success_rate=webhook_success_rate,
        settlement_success_rate=settlement_success_rate,
        providers=providers,
        anomaly_count=anomaly_count,
    )


def _provider_breakdown(
    states: list[TransactionState], classifications: list[FailureClassification]
) -> list[ProviderStats]:
    by_provider: dict[str, list[tuple[TransactionState, FailureClassification]]] = defaultdict(list)
    for state, classification in zip(states, classifications):
        provider = _provider_of(state)
        if provider is not None:
            by_provider[provider].append((state, classification))

    stats: list[ProviderStats] = []
    for provider, pairs in sorted(by_provider.items()):
        total = len(pairs)
        successful = sum(1 for _, c in pairs if c.mode == FailureMode.SUCCESSFUL)
        latencies = [
            duration_ms
            for state, _ in pairs
            for duration_ms in state.duration_by_stage.values()
        ]
        stats.append(
            ProviderStats(
                provider=provider,
                total_transactions=total,
                success_rate=successful / total if total else 0.0,
                avg_latency_ms=float(np.mean(latencies)) if latencies else None,
                failure_breakdown=dict(Counter(c.mode for _, c in pairs)),
            )
        )
    return stats


async def detect_provider_degradation(
    session: AsyncSession, org_id: UUID, window_hours: int = 1
) -> list[ProviderAlert]:
    now = datetime.now(timezone.utc)
    current_start = now - timedelta(hours=window_hours)
    baseline_start = now - timedelta(days=BASELINE_WINDOW_DAYS)

    current_states = list((await _load_states(session, org_id, current_start)).values())
    baseline_states = list((await _load_states(session, org_id, baseline_start, current_start)).values())

    classifier = FailureClassifier()

    def _failure_rate_by_provider(states: list[TransactionState]) -> dict[str, tuple[float, int]]:
        by_provider: dict[str, list[TransactionState]] = defaultdict(list)
        for state in states:
            provider = _provider_of(state)
            if provider is not None:
                by_provider[provider].append(state)

        rates: dict[str, tuple[float, int]] = {}
        for provider, provider_states in by_provider.items():
            total = len(provider_states)
            failed = sum(
                1 for s in provider_states if classifier.classify(s).mode != FailureMode.SUCCESSFUL
            )
            rates[provider] = (failed / total if total else 0.0, total)
        return rates

    current_rates = _failure_rate_by_provider(current_states)
    baseline_rates = _failure_rate_by_provider(baseline_states)

    alerts: list[ProviderAlert] = []
    for provider, (current_rate, current_count) in current_rates.items():
        if current_count < MIN_TRANSACTIONS_FOR_ALERT:
            continue

        baseline_rate, _baseline_count = baseline_rates.get(provider, (0.0, 0))

        if baseline_rate > 0:
            ratio = current_rate / baseline_rate
            triggered = ratio > DEGRADATION_RATIO_THRESHOLD
        else:
            ratio = None
            triggered = current_rate > NO_BASELINE_FAILURE_RATE_THRESHOLD

        if not triggered:
            continue

        ratio_text = f"{ratio:.1f}x" if ratio is not None else "with no prior failures to compare against"
        alerts.append(
            ProviderAlert(
                provider=provider,
                current_failure_rate=current_rate,
                baseline_failure_rate=baseline_rate,
                ratio=ratio,
                current_transaction_count=current_count,
                message=(
                    f"{provider}'s failure rate over the last {window_hours}h is "
                    f"{current_rate:.1%} ({ratio_text} its {BASELINE_WINDOW_DAYS}-day baseline of "
                    f"{baseline_rate:.1%})."
                ),
            )
        )

    return alerts
