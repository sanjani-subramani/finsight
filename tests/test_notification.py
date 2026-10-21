"""Tests for the notification delivery module (retry, backoff, dead-letter)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import (
    FinancialEvent,
    Intervention,
    NotificationDelivery,
    Organization,
    OrgMembership,
    User,
)
from app.modules.notification.delivery import (
    MAX_ATTEMPTS_BEFORE_DEAD_LETTER,
    PushChannel,
    _compute_backoff,
    deliver,
    retry_failed,
)


async def _create_user_and_delivery(
    session: AsyncSession, channel: str = "log"
) -> NotificationDelivery:
    """Helper: create a user, org, dummy intervention, and a delivery row."""
    user = User(
        email=f"notify-{uuid4().hex[:8]}@example.com",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$fakehash",
        display_name="Notify Test",
    )
    session.add(user)
    await session.flush()

    org = Organization(name="Test Org", slug=f"org-{uuid4().hex}")
    session.add(org)
    await session.flush()

    session.add(OrgMembership(user_id=user.id, org_id=org.id, role="owner"))
    await session.flush()

    # Create a minimal financial event (required FK chain)
    event = FinancialEvent(
        user_id=user.id,
        event_type="income",
        amount=Decimal("100.00"),
        currency="INR",
        description="test income",
        data_source="manual",
        confidence_score=Decimal("0.90"),
        occurred_at=datetime.now(timezone.utc),
    )
    session.add(event)
    await session.flush()

    intervention = Intervention(
        user_id=user.id,
        triggered_by_event_id=event.id,
        severity="notify",
        severity_raw=Decimal("0.500"),
        headline="Test intervention",
        body="Test intervention body",
        probability=Decimal("0.500"),
        urgency_score=Decimal("0.500"),
        data_confidence=Decimal("0.800"),
        shadow_mode=False,
    )
    session.add(intervention)
    await session.flush()

    delivery = NotificationDelivery(
        user_id=user.id,
        intervention_id=intervention.id,
        channel=channel,
        status="pending",
        attempt_count=0,
    )
    session.add(delivery)
    await session.flush()
    return delivery


# --- LogChannel (always succeeds) ---


async def test_log_channel_delivers_successfully(db_session: AsyncSession) -> None:
    delivery = await _create_user_and_delivery(db_session, channel="log")
    result = await deliver(db_session, delivery.id)
    assert result.status == "delivered"
    assert result.attempt_count == 1


async def test_log_channel_sets_delivered_at(db_session: AsyncSession) -> None:
    delivery = await _create_user_and_delivery(db_session, channel="log")
    await deliver(db_session, delivery.id)
    await db_session.refresh(delivery)
    assert delivery.delivered_at is not None
    assert delivery.status == "delivered"


# --- PushChannel (always fails — stub) ---


async def test_push_channel_fails_and_retries(db_session: AsyncSession) -> None:
    delivery = await _create_user_and_delivery(db_session, channel="push")
    result = await deliver(db_session, delivery.id)
    assert result.status == "failed"
    assert result.attempt_count == 1
    assert result.next_retry_at is not None


async def test_push_channel_dead_letters_after_max_attempts(
    db_session: AsyncSession,
) -> None:
    delivery = await _create_user_and_delivery(db_session, channel="push")

    for i in range(MAX_ATTEMPTS_BEFORE_DEAD_LETTER):
        result = await deliver(db_session, delivery.id)

    assert result.status == "dead_letter"
    assert result.attempt_count == MAX_ATTEMPTS_BEFORE_DEAD_LETTER
    assert result.next_retry_at is None


# --- Backoff ---


def test_backoff_increases_with_attempt_count() -> None:
    t1 = _compute_backoff(1)
    t2 = _compute_backoff(3)
    # The third attempt's backoff should be later than the first's
    assert t2 > t1


def test_backoff_is_bounded() -> None:
    # Even at a very high attempt count, backoff shouldn't exceed the max
    now = datetime.now(timezone.utc)
    t = _compute_backoff(100)
    # Max delay is BACKOFF_MAX_SECONDS (3600) + 20% jitter = 4320s
    assert t < now + timedelta(seconds=4400)


# --- retry_failed ---


async def test_retry_failed_picks_up_due_deliveries(db_session: AsyncSession) -> None:
    delivery = await _create_user_and_delivery(db_session, channel="push")
    # First attempt fails
    await deliver(db_session, delivery.id)
    # Force next_retry_at into the past so retry_failed picks it up
    delivery.next_retry_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    await db_session.flush()

    retried = await retry_failed(db_session)
    assert retried >= 1


async def test_retry_failed_ignores_future_retry(db_session: AsyncSession) -> None:
    delivery = await _create_user_and_delivery(db_session, channel="push")
    await deliver(db_session, delivery.id)
    # next_retry_at is in the future by default, so retry_failed should skip it
    retried = await retry_failed(db_session)
    assert retried == 0


# --- Edge cases ---


async def test_deliver_nonexistent_id_raises(db_session: AsyncSession) -> None:
    with pytest.raises(ValueError, match="not found"):
        await deliver(db_session, uuid4())


async def test_push_channel_always_raises() -> None:
    ch = PushChannel()
    with pytest.raises(NotImplementedError):
        await ch.send(None)  # type: ignore[arg-type]
