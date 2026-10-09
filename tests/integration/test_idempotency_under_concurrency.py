"""Step 19 §2 -- idempotency under REAL concurrency, against real Postgres
and real Redis. A single-request idempotency test (fire it once, fire it
again, assert the same result) cannot catch a check-then-act race; only
genuinely concurrent requests can.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.tables import FinancialEvent, User

pytestmark = pytest.mark.integration

STRONG_PASSWORD = "Str0ngPassw0rd123"
CONCURRENCY = 50


async def _register_and_login(client: AsyncClient, email: str) -> dict:
    resp = await client.post(
        "/auth/register", json={"email": email, "password": STRONG_PASSWORD, "display_name": "Concurrency Test"}
    )
    assert resp.status_code == 201, resp.text
    resp = await client.post("/auth/login", json={"email": email, "password": STRONG_PASSWORD})
    assert resp.status_code == 200, resp.text
    return resp.json()


async def test_fifty_concurrent_identical_manual_ingests_produce_one_event(
    client: AsyncClient, real_db, monkeypatch
) -> None:
    email = f"idempotency-{uuid4().hex[:8]}@example.com"
    tokens = await _register_and_login(client, email)
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Idempotency-Key": f"concurrency-test-{uuid4().hex}",
    }
    payload = {
        "event_type": "expense",
        "amount": "500.00",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "counterparty": "Concurrency Test Merchant",
        "category": "test",
    }

    # Instrument the actual write function -- a shared counter proves the
    # handler logic ran exactly once, not just that the HTTP responses
    # happened to look the same (which the old check-then-act
    # implementation could still get wrong while creating N rows).
    call_count = 0
    import app.modules.ingestion.repository as repository_module

    original_write_event = repository_module.write_event

    async def counting_write_event(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return await original_write_event(*args, **kwargs)

    monkeypatch.setattr(repository_module, "write_event", counting_write_event)
    import app.api.routers.ingestion as ingestion_router_module

    monkeypatch.setattr(ingestion_router_module, "write_event", counting_write_event)

    async def fire_one():
        return await client.post("/ingest/manual", json=payload, headers=headers)

    responses = await asyncio.gather(*(fire_one() for _ in range(CONCURRENCY)))

    statuses = {r.status_code for r in responses}
    assert statuses == {201}, [r.text for r in responses if r.status_code != 201]

    bodies = [r.json() for r in responses]
    first = bodies[0]
    assert all(body == first for body in bodies), "all 50 responses must be byte-identical"

    assert call_count == 1, f"write_event ran {call_count} times, expected exactly 1"

    user_result = await real_db.execute(select(User).where(User.email == email))
    user = user_result.scalar_one()
    # Scoped to THIS test's own freshly-registered user -- "Concurrency
    # Test Merchant" is a literal shared across every run of this test
    # file, so an unscoped query here would accumulate matches from every
    # prior run against the same (never-cleared) real Postgres database,
    # not just this run's 50 concurrent requests.
    result = await real_db.execute(
        select(FinancialEvent).where(
            FinancialEvent.user_id == user.id,
            FinancialEvent.description.is_(None),
            FinancialEvent.counterparty == "Concurrency Test Merchant",
        )
    )
    rows = list(result.scalars())
    assert len(rows) == 1, f"expected exactly one financial_events row, found {len(rows)}"


async def test_redis_streams_redelivery_of_the_same_message_id_is_a_no_op(real_redis, real_db, monkeypatch) -> None:
    from app.modules.confidence.service import ConfidenceService
    from app.modules.pipeline.handlers import PipelineContext, handle_financial_event
    from app.platform.eventbus import BusMessage, EventBus, Topic
    from app.platform.database import AsyncSessionLocal

    call_count = 0
    original_process_event = ConfidenceService.process_event

    async def counting_process_event(self, session, event_id):
        nonlocal call_count
        call_count += 1
        return await original_process_event(self, session, event_id)

    monkeypatch.setattr(ConfidenceService, "process_event", counting_process_event)

    # A real FinancialEvent row for the handler to act on.
    from app.models.tables import User

    result = await real_db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user is None:
        pytest.skip("no user in the database to attach a test event to")

    event = FinancialEvent(
        user_id=user.id,
        event_type="expense",
        amount="42.00",
        currency="INR",
        occurred_at=datetime.now(timezone.utc),
        data_source="manual",
        confidence_score=0.9,
    )
    real_db.add(event)
    await real_db.commit()

    bus = EventBus(real_redis)
    ctx = PipelineContext(
        session_factory=AsyncSessionLocal,
        redis=real_redis,
        event_bus=bus,
        group="idempotency-test-group",
        consumer="idempotency-test-consumer",
    )
    message_id = f"redelivery-test-{uuid4().hex}"
    message = BusMessage(
        id=message_id,
        topic=Topic.FINANCIAL_EVENT,
        payload={"event_id": str(event.id)},
        trace_id="redelivery-test-trace",
        delivery_count=1,
    )

    # First delivery, then a SECOND delivery of the identical message id
    # -- exactly what an at-least-once Streams redelivery looks like
    # (a crashed consumer, a missed ack, claim_stale recovering it).
    await handle_financial_event(ctx, message)
    await handle_financial_event(ctx, message)

    assert call_count == 1, f"ConfidenceService.process_event ran {call_count} times, expected exactly 1"
