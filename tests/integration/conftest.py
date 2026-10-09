"""Fixtures for full-system integration tests (Step 19).

These point at the SAME DATABASE_URL/REDIS_URL the real app uses
(app/platform/config.py, read from .env) -- real Postgres, real Redis,
real event bus. No SQLite shim, no fakeredis: this is deliberately the
opposite of every other test module in this repo (see tests/conftest.py's
own docstring for why unit tests use SQLite) because the entire point of
this suite is proving the seams between modules hold with nothing mocked.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
import redis.asyncio as aioredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.platform import worker as worker_module
from app.platform.config import get_settings
from app.platform.database import AsyncSessionLocal, engine


@pytest_asyncio.fixture(autouse=True)
async def _reset_module_level_async_singletons() -> AsyncGenerator[None, None]:
    """pytest-asyncio gives each test function its OWN event loop by
    default. Two categories of module-level, loop-bound resource don't
    survive that:

    1. Three app modules (app.platform.eventbus,
       app.modules.simulation.service, app.modules.twin.snapshot) each
       keep a lazily-created, module-level asyncio Redis client.
    2. app.platform.database.engine's connection pool holds pooled
       asyncpg connections, each opened against whatever event loop was
       current at checkout time.

    Both are entirely correct for a real deployment, which runs exactly
    one event loop for the process's whole lifetime -- the resource only
    ever needs to be created once. Under pytest, a resource created
    against test A's loop is unusable once that loop closes; reusing it
    from test B's (different) loop raises "Event loop is closed" (Redis)
    or fails the pool's checkout ping (Postgres). Clearing the Redis
    singletons and disposing the engine's pool before each test forces
    fresh connections bound to the CURRENT loop, exactly as a fresh
    production process would create on its first call.
    """
    import app.modules.simulation.service as simulation_service_module
    import app.modules.twin.snapshot as snapshot_module
    import app.platform.eventbus as eventbus_module

    eventbus_module._default_redis_client = None
    simulation_service_module._default_redis_client = None
    snapshot_module._default_redis_client = None
    await engine.dispose()
    yield


@pytest_asyncio.fixture
async def real_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def real_redis() -> AsyncGenerator[aioredis.Redis, None]:
    client = aioredis.from_url(get_settings().REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # No dependency_overrides at all -- app.platform.database.get_session
    # and every module's lazy get_redis_client() singleton already resolve
    # to the real DATABASE_URL/REDIS_URL from settings, exactly as they
    # would in a real deployment.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def pipeline_worker() -> AsyncGenerator[None, None]:
    """Starts the REAL background consumer loops (app.platform.worker,
    one asyncio task per pipeline topic) against real Redis/Postgres for
    the duration of a test. Nothing in the FastAPI app's own startup
    consumes the event bus (confirmed by reading app/main.py) -- in
    production this runs as a separate `arq` worker process. Without
    this fixture, POST /ingest/sms would publish to a real Redis Stream
    that nothing ever reads, and GET /ingest/status/{trace_id} would sit
    at "queued" forever.
    """
    ctx: dict = {}
    await worker_module.startup(ctx)
    try:
        yield
    finally:
        await worker_module.shutdown(ctx)
