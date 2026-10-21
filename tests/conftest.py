"""Shared test fixtures.

FinSentinel's real target database is Postgres (see docker-compose.yml).
This test suite runs against an in-memory SQLite database instead, so it
can execute without a live Postgres/Docker instance. The one production
type SQLite can't render is Postgres's JSONB — the @compiles hook below
teaches SQLite's DDL compiler to treat it as a plain JSON column. This is
purely a test-time shim; app/models/tables.py is untouched and still
declares JSONB for the real Postgres schema.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest_asyncio
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool

import fakeredis.aioredis

from app.main import app
from app.models.tables import Base
from app.platform.database import get_session


@compiles(JSONB, "sqlite")
def _compile_jsonb_as_json_on_sqlite(element, compiler, **kw):  # type: ignore[no-untyped-def]
    return "JSON"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(test_engine):
    return async_sessionmaker(bind=test_engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_session() -> AsyncGenerator[AsyncSession, None]:
        # Mirrors app.platform.database.get_session exactly (see the
        # comment there): an HTTPException still commits, since it signals
        # a deliberate error response rather than a DB failure.
        async with session_factory() as session:
            try:
                yield session
            except HTTPException:
                await session.commit()
                raise
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def _fake_redis(monkeypatch):
    """Replace the real Redis client with fakeredis for every test so
    endpoints that touch Redis (admin, reports) work without a live server."""
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    import app.platform.eventbus as _eb

    monkeypatch.setattr(_eb, "_default_redis_client", fake)
    yield fake
    await fake.aclose()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    await client.post(
        "/auth/register",
        json={
            "email": "ingest_user@example.com",
            "password": "Str0ngPassw0rd",
            "display_name": "Ingest Tester",
        },
    )
    resp = await client.post(
        "/auth/login",
        json={"email": "ingest_user@example.com", "password": "Str0ngPassw0rd"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
