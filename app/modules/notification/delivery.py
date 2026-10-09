"""Reliable notification delivery: pluggable channels, retry with
exponential backoff + jitter, and a dead-letter path after repeated
failure so a permanently-broken delivery doesn't retry forever.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import NotificationDelivery
from app.platform.logging import get_logger

logger = get_logger(__name__)

BACKOFF_BASE_SECONDS = 30
BACKOFF_FACTOR = 2
BACKOFF_MAX_SECONDS = 3600
# +/-20% jitter: without it, every delivery that failed during the same
# outage would retry at EXACTLY the same moment once the backoff elapses
# — a thundering herd that hammers the channel the instant it recovers,
# likely knocking it right back down.
BACKOFF_JITTER_FRACTION = 0.20
MAX_ATTEMPTS_BEFORE_DEAD_LETTER = 5


class DeliveryChannel(Protocol):
    async def send(self, delivery: NotificationDelivery) -> None:
        """Raises on failure; returns normally on success."""
        ...


class LogChannel:
    """The only channel actually wired up right now — it just logs.
    Real push/email/SMS channels are pluggable later behind the same
    DeliveryChannel protocol; nothing else in this module changes when
    they're added.
    """

    async def send(self, delivery: NotificationDelivery) -> None:
        logger.info(
            "notification_delivered_log_channel",
            delivery_id=str(delivery.id),
            user_id=str(delivery.user_id),
            intervention_id=str(delivery.intervention_id),
        )


class PushChannel:
    """Stub: not yet wired to a real push provider (FCM/APNs/...).
    Deliberately always fails so a delivery routed here goes through the
    real retry/backoff/dead-letter path rather than silently pretending
    to succeed.
    """

    async def send(self, delivery: NotificationDelivery) -> None:
        raise NotImplementedError("PushChannel is a stub; not yet wired to a real provider")


_CHANNELS: dict[str, DeliveryChannel] = {
    "log": LogChannel(),
    "push": PushChannel(),
}


@dataclass(frozen=True)
class DeliveryResult:
    delivery_id: UUID
    status: str
    attempt_count: int
    next_retry_at: datetime | None


def _compute_backoff(attempt_count: int) -> datetime:
    raw_delay = min(BACKOFF_BASE_SECONDS * (BACKOFF_FACTOR ** (attempt_count - 1)), BACKOFF_MAX_SECONDS)
    jitter = raw_delay * BACKOFF_JITTER_FRACTION
    delay = max(0.0, raw_delay + random.uniform(-jitter, jitter))
    return datetime.now(timezone.utc) + timedelta(seconds=delay)


async def deliver(session: AsyncSession, delivery_id: UUID) -> DeliveryResult:
    row = await session.get(NotificationDelivery, delivery_id)
    if row is None:
        raise ValueError(f"NotificationDelivery {delivery_id} not found")

    channel = _CHANNELS.get(row.channel, _CHANNELS["log"])
    row.attempt_count += 1

    try:
        await channel.send(row)
    except Exception as exc:
        row.last_error = str(exc)[:2000]
        if row.attempt_count >= MAX_ATTEMPTS_BEFORE_DEAD_LETTER:
            row.status = "dead_letter"
            row.next_retry_at = None
            # A real admin-alert channel doesn't exist yet (Step 9+) — a
            # loud log is the interim signal that something needs human
            # attention.
            logger.error(
                "notification_dead_lettered",
                delivery_id=str(delivery_id),
                attempt_count=row.attempt_count,
                last_error=row.last_error,
            )
        else:
            row.status = "failed"
            row.next_retry_at = _compute_backoff(row.attempt_count)
        await session.flush()
        return DeliveryResult(
            delivery_id=delivery_id,
            status=row.status,
            attempt_count=row.attempt_count,
            next_retry_at=row.next_retry_at,
        )

    row.status = "delivered"
    row.delivered_at = datetime.now(timezone.utc)
    row.next_retry_at = None
    await session.flush()
    return DeliveryResult(delivery_id=delivery_id, status=row.status, attempt_count=row.attempt_count, next_retry_at=None)


async def retry_failed(session: AsyncSession) -> int:
    """Cron job: pick up rows due for retry (status failed, next_retry_at
    has passed) and attempt them again. Returns the count attempted."""
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(NotificationDelivery).where(
            NotificationDelivery.status == "failed", NotificationDelivery.next_retry_at <= now
        )
    )
    rows = list(result.scalars())
    for row in rows:
        await deliver(session, row.id)
    return len(rows)
