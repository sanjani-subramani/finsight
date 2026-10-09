"""Shared structural type for an injectable cache/redis client.

Lives in app.platform (not inside any one module) because more than one
module needs it — per the module boundary rule (see README), a module may
depend on app.platform but never reach into another module's internals.
"""

from __future__ import annotations

from typing import Any, Protocol


class RedisLike(Protocol):
    """Just enough of redis.asyncio.Redis's interface to be usable, so
    tests can pass a lightweight in-memory fake (fakeredis) without it
    needing to subclass Redis.

    Extended beyond simple get/set for app.platform.eventbus (Redis
    Streams) and app.modules.pipeline's idempotency tracking — both
    redis.asyncio.Redis and fakeredis's async client already implement
    this surface structurally, so nothing needs to explicitly subclass
    this Protocol.
    """

    async def get(self, name: str) -> str | None: ...
    async def set(self, name: str, value: str) -> object: ...
    async def setex(self, name: str, time: int, value: str) -> object: ...
    async def exists(self, *names: str) -> int: ...
    async def delete(self, *names: str) -> int: ...

    # Streams
    async def xadd(self, name: str, fields: dict[str, Any], id: str = "*") -> Any: ...
    async def xgroup_create(
        self, name: str, groupname: str, id: str = "$", mkstream: bool = False
    ) -> object: ...
    async def xreadgroup(
        self,
        groupname: str,
        consumername: str,
        streams: dict[str, str],
        count: int | None = None,
        block: int | None = None,
    ) -> Any: ...
    async def xack(self, name: str, groupname: str, *ids: str) -> int: ...
    async def xautoclaim(
        self,
        name: str,
        groupname: str,
        consumername: str,
        min_idle_time: int,
        start_id: str = "0-0",
        count: int | None = None,
    ) -> Any: ...
    async def xpending_range(
        self,
        name: str,
        groupname: str,
        min: str,
        max: str,
        count: int,
        consumername: str | None = None,
    ) -> Any: ...
    async def xpending(self, name: str, groupname: str) -> Any: ...
    async def xlen(self, name: str) -> int: ...
    async def xrange(self, name: str, min: str = "-", max: str = "+", count: int | None = None) -> Any: ...
