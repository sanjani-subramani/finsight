from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.contracts.events import TransactionEvent, TxnStage
from app.models.tables import Organization, OrgMembership, TransactionEvent as TransactionEventRow, User
from app.modules.org.paytrace.analytics import compute_health, detect_provider_degradation
from app.modules.org.paytrace.classifier import FailureClassifier, FailureMode
from app.modules.org.paytrace.state_machine import derive_state, validate_transition

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------

_BASE = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _event(
    *,
    org_id: UUID,
    ref: str = "TX83921",
    stage: TxnStage,
    occurred_at: datetime,
    amount: Decimal = Decimal("1000.00"),
    provider: str = "razorpay",
    idempotency_key: str,
    error_code: str | None = None,
    latency_ms: int | None = None,
) -> TransactionEvent:
    return TransactionEvent(
        org_id=org_id,
        transaction_ref=ref,
        stage=stage,
        occurred_at=occurred_at,
        amount=amount,
        provider=provider,
        error_code=error_code,
        latency_ms=latency_ms,
        idempotency_key=idempotency_key,
    )


def _add_row(
    session,
    *,
    org_id: UUID,
    ref: str,
    stage: TxnStage,
    occurred_at: datetime,
    provider: str = "razorpay",
    amount: Decimal = Decimal("100.00"),
    error_code: str | None = None,
    idempotency_key: str | None = None,
) -> None:
    session.add(
        TransactionEventRow(
            org_id=org_id,
            transaction_ref=ref,
            stage=stage.value,
            occurred_at=occurred_at,
            amount=amount,
            provider=provider,
            error_code=error_code,
            idempotency_key=idempotency_key or f"{ref}-{stage.value}",
        )
    )


def _add_valid_txn(session, *, org_id: UUID, ref: str, provider: str, occurred_at: datetime, success: bool) -> None:
    """Seeds a transaction along an actually-valid path through
    VALID_TRANSITIONS (initiated -> gateway_accepted -> bank_accepted ->
    settled, or initiated -> gateway_accepted -> bank_failed) -- a shortcut
    straight from initiated to settled/bank_failed would itself be an
    invalid-transition anomaly and would never classify as SUCCESSFUL.
    """
    _add_row(session, org_id=org_id, ref=ref, stage=TxnStage.initiated, occurred_at=occurred_at, provider=provider)
    _add_row(
        session,
        org_id=org_id,
        ref=ref,
        stage=TxnStage.gateway_accepted,
        occurred_at=occurred_at + timedelta(seconds=1),
        provider=provider,
    )
    if success:
        _add_row(
            session,
            org_id=org_id,
            ref=ref,
            stage=TxnStage.bank_accepted,
            occurred_at=occurred_at + timedelta(seconds=2),
            provider=provider,
        )
        _add_row(
            session,
            org_id=org_id,
            ref=ref,
            stage=TxnStage.settled,
            occurred_at=occurred_at + timedelta(seconds=3),
            provider=provider,
        )
    else:
        _add_row(
            session,
            org_id=org_id,
            ref=ref,
            stage=TxnStage.bank_failed,
            occurred_at=occurred_at + timedelta(seconds=2),
            provider=provider,
            error_code="INSUFFICIENT_FUNDS",
        )


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------


def test_valid_transition_is_allowed():
    assert validate_transition(TxnStage.initiated, TxnStage.gateway_accepted) is True
    assert validate_transition(TxnStage.bank_accepted, TxnStage.settled) is True
    assert validate_transition(TxnStage.webhook_failed, TxnStage.settled) is True


def test_invalid_transition_is_rejected():
    assert validate_transition(TxnStage.initiated, TxnStage.settled) is False
    assert validate_transition(TxnStage.refunded, TxnStage.settled) is False


def test_invalid_transition_between_events_is_flagged_as_anomaly():
    org_id = uuid4()
    events = [
        _event(org_id=org_id, stage=TxnStage.initiated, occurred_at=_BASE, idempotency_key="i1"),
        _event(
            org_id=org_id,
            stage=TxnStage.settled,
            occurred_at=_BASE + timedelta(seconds=5),
            idempotency_key="i2",
        ),
    ]
    state = derive_state(events)
    assert any(a.kind == "invalid_transition" for a in state.anomalies)


def test_missing_initiated_stage_is_flagged_as_anomaly():
    org_id = uuid4()
    events = [_event(org_id=org_id, stage=TxnStage.bank_accepted, occurred_at=_BASE, idempotency_key="i1")]
    state = derive_state(events)
    assert any(a.kind == "missing_stage" for a in state.anomalies)


def test_events_are_folded_by_occurred_at_not_insertion_order():
    org_id = uuid4()
    first = _event(org_id=org_id, stage=TxnStage.initiated, occurred_at=_BASE, idempotency_key="i1")
    second = _event(
        org_id=org_id,
        stage=TxnStage.gateway_accepted,
        occurred_at=_BASE + timedelta(seconds=5),
        idempotency_key="i2",
    )

    # Insert out of chronological order -- the fold must still order by
    # occurred_at, not by list position.
    state = derive_state([second, first])

    assert [e.stage for e in state.timeline] == [TxnStage.initiated, TxnStage.gateway_accepted]
    assert state.current_stage == TxnStage.gateway_accepted


def test_point_in_time_fold_shows_state_as_of_that_moment():
    org_id = uuid4()
    ref = "TX83921"
    events = [
        _event(org_id=org_id, ref=ref, stage=TxnStage.initiated, occurred_at=_BASE, idempotency_key="i1"),
        _event(
            org_id=org_id,
            ref=ref,
            stage=TxnStage.gateway_accepted,
            occurred_at=_BASE + timedelta(seconds=5),
            idempotency_key="i2",
        ),
        _event(
            org_id=org_id,
            ref=ref,
            stage=TxnStage.bank_accepted,
            occurred_at=_BASE + timedelta(seconds=10),
            idempotency_key="i3",
        ),
        _event(
            org_id=org_id,
            ref=ref,
            stage=TxnStage.webhook_sent,
            occurred_at=_BASE + timedelta(minutes=35),
            idempotency_key="i4",
        ),
        _event(
            org_id=org_id,
            ref=ref,
            stage=TxnStage.settled,
            occurred_at=_BASE + timedelta(minutes=36),
            idempotency_key="i5",
        ),
    ]

    cutoff = _BASE + timedelta(minutes=30, seconds=6)
    state = derive_state(events, up_to=cutoff)

    assert state.current_stage == TxnStage.bank_accepted
    assert TxnStage.webhook_sent not in [e.stage for e in state.timeline]


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def test_webhook_lost_is_classified_correctly():
    org_id = uuid4()
    events = [
        _event(org_id=org_id, stage=TxnStage.initiated, occurred_at=_BASE, idempotency_key="i1"),
        _event(
            org_id=org_id,
            stage=TxnStage.gateway_accepted,
            occurred_at=_BASE + timedelta(seconds=2),
            idempotency_key="i2",
        ),
        _event(
            org_id=org_id,
            stage=TxnStage.bank_accepted,
            occurred_at=_BASE + timedelta(seconds=5),
            idempotency_key="i3",
        ),
        _event(
            org_id=org_id,
            stage=TxnStage.webhook_failed,
            occurred_at=_BASE + timedelta(seconds=8),
            idempotency_key="i4",
        ),
        _event(
            org_id=org_id,
            stage=TxnStage.settled,
            occurred_at=_BASE + timedelta(seconds=20),
            idempotency_key="i5",
        ),
    ]
    state = derive_state(events)
    classification = FailureClassifier().classify(state)

    assert classification.mode == FailureMode.WEBHOOK_LOST
    assert classification.recommended_action == "Re-send notification to merchant"
    assert "webhook_failed_at" in classification.evidence


def test_fully_successful_transaction_is_not_a_false_alarm():
    org_id = uuid4()
    events = [
        _event(org_id=org_id, stage=TxnStage.initiated, occurred_at=_BASE, idempotency_key="i1"),
        _event(
            org_id=org_id,
            stage=TxnStage.gateway_accepted,
            occurred_at=_BASE + timedelta(seconds=2),
            idempotency_key="i2",
        ),
        _event(
            org_id=org_id,
            stage=TxnStage.bank_accepted,
            occurred_at=_BASE + timedelta(seconds=5),
            idempotency_key="i3",
        ),
        _event(
            org_id=org_id,
            stage=TxnStage.webhook_sent,
            occurred_at=_BASE + timedelta(seconds=8),
            idempotency_key="i4",
        ),
        _event(
            org_id=org_id,
            stage=TxnStage.settled,
            occurred_at=_BASE + timedelta(seconds=10),
            idempotency_key="i5",
        ),
    ]
    state = derive_state(events)
    assert state.anomalies == []

    classification = FailureClassifier().classify(state)
    assert classification.mode == FailureMode.SUCCESSFUL


def test_stuck_transaction_is_detected():
    org_id = uuid4()
    # initiated's SLA is 30s; more than 2x that with no follow-up event.
    stale_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    events = [_event(org_id=org_id, stage=TxnStage.initiated, occurred_at=stale_time, idempotency_key="i1")]

    state = derive_state(events)
    classification = FailureClassifier().classify(state)

    assert classification.mode == FailureMode.STUCK
    assert classification.recommended_action == "Query gateway for status update"
    assert classification.evidence["elapsed_ms"] > classification.evidence["threshold_ms"]


def test_duplicate_attempt_is_caught():
    org_id = uuid4()
    events = [
        _event(
            org_id=org_id,
            stage=TxnStage.initiated,
            occurred_at=_BASE,
            amount=Decimal("500.00"),
            idempotency_key="attempt-1",
        ),
        _event(
            org_id=org_id,
            stage=TxnStage.initiated,
            occurred_at=_BASE + timedelta(seconds=30),
            amount=Decimal("500.00"),
            idempotency_key="attempt-2",
        ),
    ]
    state = derive_state(events)
    classification = FailureClassifier().classify(state)

    assert classification.mode == FailureMode.DUPLICATE_ATTEMPT
    assert classification.recommended_action == "Refund the duplicate"
    assert classification.evidence["first_idempotency_key"] == "attempt-1"
    assert classification.evidence["second_idempotency_key"] == "attempt-2"


def test_classification_confidence_and_evidence_contain_real_values():
    org_id = uuid4()
    events = [
        _event(
            org_id=org_id,
            stage=TxnStage.initiated,
            occurred_at=_BASE,
            idempotency_key="i1",
            latency_ms=None,
        ),
        _event(
            org_id=org_id,
            stage=TxnStage.gateway_failed,
            occurred_at=_BASE + timedelta(seconds=15),
            idempotency_key="i2",
            latency_ms=15_000,
        ),
    ]
    state = derive_state(events)
    classification = FailureClassifier().classify(state)

    assert classification.mode == FailureMode.GATEWAY_TIMEOUT
    assert 0.0 < classification.confidence <= 1.0
    assert classification.evidence["latency_ms"] == 15_000
    assert classification.evidence["threshold_ms"] > 0
    assert "GATEWAY_TIMEOUT" not in classification.human_summary  # human-readable, not the enum name
    assert "timed out" in classification.human_summary


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_stats_sum_correctly_across_a_batch_of_transactions(db_session):
    org_id = uuid4()
    now = datetime.now(timezone.utc) - timedelta(minutes=10)

    for i in range(3):
        _add_valid_txn(db_session, org_id=org_id, ref=f"OK-{i}", provider="razorpay", occurred_at=now, success=True)
    _add_valid_txn(db_session, org_id=org_id, ref="FAIL-1", provider="razorpay", occurred_at=now, success=False)

    await db_session.commit()

    health = await compute_health(db_session, org_id, window_hours=24)

    assert health.total_transactions == 4
    assert health.success_rate == pytest.approx(3 / 4)
    assert health.failure_breakdown[FailureMode.SUCCESSFUL] == 3
    assert health.failure_breakdown[FailureMode.BANK_DECLINED] == 1
    assert health.anomaly_count == 0


@pytest.mark.asyncio
async def test_per_provider_breakdown_shows_correct_per_provider_stats(db_session):
    org_id = uuid4()
    now = datetime.now(timezone.utc) - timedelta(minutes=10)

    for i in range(4):
        _add_valid_txn(db_session, org_id=org_id, ref=f"A-OK-{i}", provider="gateway_a", occurred_at=now, success=True)
    _add_valid_txn(db_session, org_id=org_id, ref="A-FAIL", provider="gateway_a", occurred_at=now, success=False)

    for i in range(3):
        _add_valid_txn(db_session, org_id=org_id, ref=f"B-OK-{i}", provider="gateway_b", occurred_at=now, success=True)

    await db_session.commit()

    health = await compute_health(db_session, org_id, window_hours=24)
    by_provider = {p.provider: p for p in health.providers}

    assert by_provider["gateway_a"].total_transactions == 5
    assert by_provider["gateway_a"].success_rate == pytest.approx(0.8)
    assert by_provider["gateway_b"].total_transactions == 3
    assert by_provider["gateway_b"].success_rate == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_provider_degradation_alert_fires_on_a_spike(db_session):
    org_id = uuid4()
    provider = "razorpay"
    now = datetime.now(timezone.utc)

    # 7-day baseline: 50 transactions, 1 failure -> 2%.
    baseline_start = now - timedelta(days=2)
    for i in range(50):
        _add_valid_txn(
            db_session,
            org_id=org_id,
            ref=f"BASE-{i}",
            provider=provider,
            occurred_at=baseline_start + timedelta(seconds=i),
            success=(i != 0),
        )

    # Current 1h window: 5 transactions, 1 failure -> 20%.
    current_start = now - timedelta(minutes=30)
    for i in range(5):
        _add_valid_txn(
            db_session,
            org_id=org_id,
            ref=f"CUR-{i}",
            provider=provider,
            occurred_at=current_start + timedelta(seconds=i),
            success=(i != 0),
        )

    await db_session.commit()

    alerts = await detect_provider_degradation(db_session, org_id, window_hours=1)

    assert len(alerts) == 1
    assert alerts[0].provider == provider
    assert alerts[0].current_failure_rate == pytest.approx(0.2)
    assert alerts[0].baseline_failure_rate == pytest.approx(0.02)
    assert alerts[0].ratio == pytest.approx(10.0)


@pytest.mark.asyncio
async def test_provider_degradation_does_not_fire_on_low_volume(db_session):
    org_id = uuid4()
    provider = "razorpay"
    now = datetime.now(timezone.utc)

    # A single failed transaction in the current window is a 100% failure
    # rate, but with a sample size below MIN_TRANSACTIONS_FOR_ALERT this
    # must NOT page anyone -- one unlucky transaction isn't an outage.
    _add_valid_txn(
        db_session, org_id=org_id, ref="LONE-FAIL", provider=provider, occurred_at=now - timedelta(minutes=10), success=False
    )
    await db_session.commit()

    alerts = await detect_provider_degradation(db_session, org_id, window_hours=1)
    assert alerts == []


# ---------------------------------------------------------------------------
# End-to-end through the API
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ingest_and_fetch_transaction_through_the_api(client: AsyncClient, auth_headers: dict, db_session):
    result = await db_session.execute(select(User).where(User.email == "ingest_user@example.com"))
    user = result.scalar_one()

    org = Organization(name="Acme Payments", slug="acme-payments")
    db_session.add(org)
    await db_session.flush()
    db_session.add(OrgMembership(user_id=user.id, org_id=org.id, role="owner"))
    await db_session.commit()

    ref = "TX-API-1"
    # Recent (not _BASE) -- the STUCK rule compares against real wall-clock
    # time, and this transaction is meant to still be genuinely in flight.
    recent = datetime.now(timezone.utc) - timedelta(seconds=5)
    resp = await client.post(
        f"/org/{org.id}/paytrace/events",
        json={
            "transaction_ref": ref,
            "stage": "initiated",
            "occurred_at": recent.isoformat(),
            "amount": "250.00",
            "provider": "razorpay",
            "idempotency_key": "api-idem-1",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["current_stage"] == "initiated"

    resp = await client.post(
        f"/org/{org.id}/paytrace/events",
        json={
            "transaction_ref": ref,
            "stage": "gateway_accepted",
            "occurred_at": (recent + timedelta(seconds=2)).isoformat(),
            "amount": "250.00",
            "provider": "razorpay",
            "idempotency_key": "api-idem-2",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    resp = await client.get(f"/org/{org.id}/paytrace/transactions/{ref}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["state"]["current_stage"] == "gateway_accepted"
    assert body["classification"]["mode"] == "in_progress"


@pytest.mark.asyncio
async def test_paytrace_endpoints_require_org_membership(client: AsyncClient, auth_headers: dict):
    other_org_id = uuid4()
    resp = await client.get(f"/org/{other_org_id}/paytrace/health", headers=auth_headers)
    assert resp.status_code == 403
