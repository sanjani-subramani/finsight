"""Redis Streams wrapper — the event bus that moves heavy processing off
the request path (Step 9).

Redis Streams gives consumer groups, acknowledgement, replay and
pending-message recovery in one container (XADD/XREADGROUP/XACK/
XAUTOCLAIM). Kafka would give the same guarantees at millions of
events/sec, which this system does not have — revisit only above roughly
50k events/sec.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import redis.asyncio as redis
from redis.exceptions import ResponseError

from app.platform.cache import RedisLike
from app.platform.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

# Same lazy-singleton-with-injection-override pattern used throughout
# app.platform/app.modules for redis clients (see e.g.
# app.modules.simulation.service._get_redis) — kept local rather than
# shared, consistent with how every prior step has done this.
_default_redis_client: RedisLike | None = None


def get_redis_client(injected: RedisLike | None = None) -> RedisLike:
    if injected is not None:
        return injected
    global _default_redis_client
    if _default_redis_client is None:
        _default_redis_client = redis.from_url(get_settings().REDIS_URL, decode_responses=True)
    return _default_redis_client


class Topic(str, Enum):
    FINANCIAL_EVENT = "financial_event"
    STATE_CHANGED = "state.changed"
    SNAPSHOT_UPDATED = "snapshot.updated"
    RISK_ASSESSED = "risk.assessed"
    INTERVENTION_CREATED = "intervention.created"
    THREAT_EVENT = "threat_event"
    DEAD_LETTER = "dead_letter"


SCHEMA_VERSION = 1
_STREAM_KEY_PREFIX = "stream:"


def stream_key(topic: Topic) -> str:
    return f"{_STREAM_KEY_PREFIX}{topic.value}"


@dataclass(frozen=True)
class BusMessage:
    id: str
    topic: Topic
    payload: dict[str, Any]
    trace_id: str
    delivery_count: int


class EventBus:
    def __init__(self, redis_client: RedisLike | None = None) -> None:
        self._redis = get_redis_client(redis_client)

    async def publish(self, topic: Topic, payload: dict[str, Any], trace_id: str) -> str:
        envelope = {
            "schema_version": str(SCHEMA_VERSION),
            "trace_id": trace_id,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "payload": json.dumps(payload, default=str),
        }
        message_id = await self._redis.xadd(stream_key(topic), envelope)
        return str(message_id)

    async def _ensure_group(self, key: str, group: str) -> None:
        try:
            # id="0" (not "$"): a lazily-created group must still see
            # messages already sitting on the stream from before the
            # group existed — starting at "$" would silently skip them.
            await self._redis.xgroup_create(key, group, id="0", mkstream=True)
        except ResponseError as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    async def subscribe(
        self, topic: Topic, group: str, consumer: str, *, block_ms: int = 5000, count: int = 10
    ) -> AsyncIterator[BusMessage]:
        key = stream_key(topic)
        await self._ensure_group(key, group)
        while True:
            response = await self._redis.xreadgroup(group, consumer, {key: ">"}, count=count, block=block_ms)
            if not response:
                continue
            for _stream_name, entries in response:
                for message_id, fields in entries:
                    delivery_count = await self._delivery_count(key, group, message_id)
                    yield self._to_bus_message(topic, message_id, fields, delivery_count)

    async def _delivery_count(self, key: str, group: str, message_id: str) -> int:
        pending = await self._redis.xpending_range(key, group, min=message_id, max=message_id, count=1)
        if not pending:
            return 1
        entry = pending[0]
        times_delivered = entry.get("times_delivered", 1) if isinstance(entry, dict) else 1
        return int(times_delivered)

    def _to_bus_message(
        self, topic: Topic, message_id: str, fields: dict[str, Any], delivery_count: int
    ) -> BusMessage:
        payload = json.loads(fields.get("payload", "{}"))
        trace_id = fields.get("trace_id", "")
        return BusMessage(
            id=str(message_id), topic=topic, payload=payload, trace_id=trace_id, delivery_count=delivery_count
        )

    async def ack(self, topic: Topic, group: str, message_id: str) -> None:
        await self._redis.xack(stream_key(topic), group, message_id)

    async def claim_stale(
        self, topic: Topic, group: str, consumer: str, *, min_idle_ms: int = 60000
    ) -> list[BusMessage]:
        """XAUTOCLAIM: recovers messages that were delivered to a consumer
        which then crashed (or is simply taking too long) before acking —
        without this, a dead consumer's in-flight messages would sit
        pending forever and never be retried.
        """
        key = stream_key(topic)
        # Memurai Developer is based on Redis 5, which lacks the XAUTOCLAIM command (added in 6.2).
        # We degrade gracefully to the Redis 5 two-step equivalent: XPENDING + XCLAIM.
        pending_messages = await self._redis.xpending_range(key, group, min="-", max="+", count=100)
        
        stale_ids = [
            msg["message_id"] 
            for msg in pending_messages 
            if msg["time_since_delivered"] >= min_idle_ms
        ]
        
        claimed = []
        if stale_ids:
            claimed = await self._redis.xclaim(
                key, group, consumer, min_idle_time=min_idle_ms, message_ids=stale_ids
            )
            
        messages = []
        for message_id, fields in claimed:
            delivery_count = await self._delivery_count(key, group, message_id)
            messages.append(self._to_bus_message(topic, message_id, fields, delivery_count))
        return messages

    async def dead_letter(self, topic: Topic, message: BusMessage, reason: str) -> str:
        dlq_payload = {
            "original_topic": topic.value,
            "original_message_id": message.id,
            "payload": message.payload,
            "reason": reason,
        }
        logger.warning("dead_letter", topic=topic.value, message_id=message.id, reason=reason)
        return await self.publish(Topic.DEAD_LETTER, dlq_payload, message.trace_id)
