"""A minimal Redis-backed fixed-window rate limiter."""

from __future__ import annotations

import redis.asyncio as redis

from app.platform.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(get_settings().REDIS_URL, decode_responses=True)
    return _client


async def check_rate_limit(key: str, *, limit: int, window_seconds: int) -> bool:
    """True if the caller is within the limit.

    Fails OPEN (allows the request) if Redis itself is unreachable — a
    rate limiter must never become a way to take the whole product down
    when an infrastructure dependency hiccups. The endpoint's own auth
    and validation still apply regardless.
    """
    try:
        client = _get_client()
        current = await client.incr(key)
        if current == 1:
            await client.expire(key, window_seconds)
        return current <= limit
    except Exception:
        logger.warning("rate_limit_check_failed", key=key, exc_info=True)
        return True
