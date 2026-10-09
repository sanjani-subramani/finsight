from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID, uuid4

import fakeredis.aioredis as fakeredis
import pytest
from httpx import AsyncClient
from sqlalchemy import select

import app.modules.simulation.service as simulation_service_module
import app.modules.twin.snapshot as twin_snapshot_module
import app.platform.eventbus as eventbus_module
from app.models.tables import FinancialEvent, Intervention, NotificationDelivery, Obligation, User
from app.modules.confidence.service import ConfidenceService
from app.modules.notification.delivery import (
    BACKOFF_BASE_SECONDS,
    BACKOFF_FACTOR,
    BACKOFF_JITTER_FRACTION,
    MAX_ATTEMPTS_BEFORE_DEAD_LETTER,
    deliver,
)
from app.modules.pipeline.handlers import (
    PipelineContext,
    get_pipeline_status,
    handle_financial_event,
    handle_intervention_created,
    handle_risk_assessed,
    handle_snapshot_updated,
    handle_state_changed,
)
from app.platform.eventbus import BusMessage, EventBus, Topic, stream_key

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_redis():
    return fakeredis.FakeRedis(decode_responses=True)


def _make_ctx(session_factory, redis_client, bus, *, consumer: str = "test-consumer") -> PipelineContext:
    return PipelineContext(
        session_factory=session_factory,
        redis=redis_client,
        event_bus=bus,
        group="pipeline",
        consumer=consumer,
    )


def _reset_redis_singletons() -> None:
    # Several domain services (Twin, Simulation, ...) lazily cache their
    # OWN default redis.asyncio client in a module-level global the first
    # time nothing is injected -- and once cached, it stays cached for
    # the rest of the process. If an EARLIER test in this same pytest
    # session already triggered that (e.g. test_ingestion.py's sync path
    # calling TwinService directly), that stale real (unreachable) client
    # sticks around and patching redis.asyncio.from_url alone can't
    # undo it -- only resetting the cache to None forces a fresh
    # construction that the from_url patch can actually intercept.
    eventbus_module._default_redis_client = None
    twin_snapshot_module._default_redis_client = None
    simulation_service_module._default_redis_client = None


async def _read_one(bus: EventBus, topic: Topic, group: str, consumer: str, *, block_ms: int = 300) -> BusMessage:
    gen = bus.subscribe(topic, group, consumer, block_ms=block_ms)
    return await gen.__anext__()


# ---------------------------------------------------------------------------
# EVENT BUS primitives
# ---------------------------------------------------------------------------


async def test_publish_and_consume_returns_same_payload(fake_redis):
    bus = EventBus(fake_redis)
    await bus.publish(Topic.FINANCIAL_EVENT, {"event_id": "abc123"}, trace_id="trace-1")

    message = await _read_one(bus, Topic.FINANCIAL_EVENT, "grp", "c1")
    assert message.payload == {"event_id": "abc123"}
    assert message.trace_id == "trace-1"
    assert message.delivery_count == 1


async def test_ack_removes_message_from_pending(fake_redis):
    bus = EventBus(fake_redis)
    await bus.publish(Topic.FINANCIAL_EVENT, {"x": 1}, trace_id="t")
    message = await _read_one(bus, Topic.FINANCIAL_EVENT, "grp", "c1")

    pending_before = await fake_redis.xpending(stream_key(Topic.FINANCIAL_EVENT), "grp")
    assert pending_before["pending"] == 1

    await bus.ack(Topic.FINANCIAL_EVENT, "grp", message.id)

    pending_after = await fake_redis.xpending(stream_key(Topic.FINANCIAL_EVENT), "grp")
    assert pending_after["pending"] == 0


async def test_unacked_message_reclaimable_via_claim_stale(fake_redis):
    bus = EventBus(fake_redis)
    await bus.publish(Topic.FINANCIAL_EVENT, {"x": 1}, trace_id="t")
    message = await _read_one(bus, Topic.FINANCIAL_EVENT, "grp", "c1")  # read, never acked

    claimed = await bus.claim_stale(Topic.FINANCIAL_EVENT, "grp", "c2", min_idle_ms=0)
    assert len(claimed) == 1
    assert claimed[0].id == message.id
    assert claimed[0].delivery_count == 2  # first XREADGROUP delivery + this claim


# ---------------------------------------------------------------------------
# IDEMPOTENCY (the critical test)
# ---------------------------------------------------------------------------


async def test_handler_receiving_same_message_twice_produces_one_side_effect(
    fake_redis, session_factory, db_session
):
    user_id = uuid4()
    event = FinancialEvent(
        id=uuid4(),
        user_id=user_id,
        schema_version=1,
        event_type="expense",
        amount=Decimal("100.00"),
        currency="INR",
        occurred_at=datetime.now(timezone.utc),
        data_source="manual",
        confidence_score=0.9,
    )
    db_session.add(event)
    await db_session.commit()

    bus = EventBus(fake_redis)
    ctx = _make_ctx(session_factory, fake_redis, bus)
    message = BusMessage(
        id="1-1", topic=Topic.FINANCIAL_EVENT, payload={"event_id": str(event.id)}, trace_id="trace-x", delivery_count=1
    )

    call_count = 0
    original = ConfidenceService.process_event

    async def counting_process_event(self, session, event_id):
        nonlocal call_count
        call_count += 1
        return await original(self, session, event_id)

    with patch.object(ConfidenceService, "process_event", counting_process_event):
        await handle_financial_event(ctx, message)
        await handle_financial_event(ctx, message)  # same message id again

    assert call_count == 1


# ---------------------------------------------------------------------------
# DEAD LETTER after MAX_DELIVERY_ATTEMPTS
# ---------------------------------------------------------------------------


async def test_handler_failing_three_times_sends_to_dlq_and_acks(fake_redis, session_factory):
    bus = EventBus(fake_redis)
    ctx = _make_ctx(session_factory, fake_redis, bus)

    # An event_id that isn't a valid UUID makes handle_financial_event's
    # work() raise deterministically, every attempt.
    for delivery_count in (1, 2, 3):
        message = BusMessage(
            id="poison-1",
            topic=Topic.FINANCIAL_EVENT,
            payload={"event_id": "not-a-uuid"},
            trace_id="trace-poison",
            delivery_count=delivery_count,
        )
        await handle_financial_event(ctx, message)

    dlq_message = await _read_one(bus, Topic.DEAD_LETTER, "grp", "c1")
    assert dlq_message.payload["original_message_id"] == "poison-1"
    assert dlq_message.payload["original_topic"] == "financial_event"
    assert "failed after 3 attempts" in dlq_message.payload["reason"]

    status = await get_pipeline_status(fake_redis, "trace-poison")
    assert status == "dead_letter"


# ---------------------------------------------------------------------------
# TRACE ID PROPAGATION
# ---------------------------------------------------------------------------


async def test_trace_id_propagates_through_every_stage_unchanged(fake_redis, session_factory, db_session):
    _reset_redis_singletons()
    user_id = uuid4()
    trace_id = "trace-propagation-check"

    event = FinancialEvent(
        id=uuid4(),
        user_id=user_id,
        schema_version=1,
        event_type="expense",
        amount=Decimal("50.00"),
        currency="INR",
        occurred_at=datetime.now(timezone.utc),
        data_source="manual",
        confidence_score=0.9,
    )
    db_session.add(event)
    await db_session.commit()

    bus = EventBus(fake_redis)
    ctx = _make_ctx(session_factory, fake_redis, bus)

    # TwinService/SimulationService/CounterpartyResolver etc. each fall
    # back to their OWN real redis.asyncio client when nothing is
    # injected, and none of that is reachable through the public service
    # methods these handlers call -- patching redis.asyncio.from_url
    # process-wide (rather than chasing every module's private default)
    # is what keeps this test from spending tens of seconds timing out
    # against a Redis server that doesn't exist in this dev environment.
    with patch("redis.asyncio.from_url", return_value=fake_redis):
        financial_event_msg = BusMessage(
            id="te-1",
            topic=Topic.FINANCIAL_EVENT,
            payload={"event_id": str(event.id)},
            trace_id=trace_id,
            delivery_count=1,
        )
        await handle_financial_event(ctx, financial_event_msg)
        state_changed_msg = await _read_one(bus, Topic.STATE_CHANGED, "pipeline", "c1")
        assert state_changed_msg.trace_id == trace_id

        await handle_state_changed(ctx, state_changed_msg)
        snapshot_updated_msg = await _read_one(bus, Topic.SNAPSHOT_UPDATED, "pipeline", "c1")
        assert snapshot_updated_msg.trace_id == trace_id

        await handle_snapshot_updated(ctx, snapshot_updated_msg)
        risk_assessed_msg = await _read_one(bus, Topic.RISK_ASSESSED, "pipeline", "c1")
        assert risk_assessed_msg.trace_id == trace_id


# ---------------------------------------------------------------------------
# FULL PIPELINE END TO END
# ---------------------------------------------------------------------------


async def test_full_pipeline_end_to_end_produces_an_intervention(
    fake_redis, client: AsyncClient, auth_headers: dict, session_factory, db_session
):
    # The router (and everything downstream) reaches for the module-level
    # default redis client via get_redis_client() -- there's no FastAPI
    # dependency-injection seam for it (services are instantiated
    # directly throughout this codebase, not injected), so the test
    # points that singleton (and the others -- see _reset_redis_singletons)
    # at the same fake redis this test itself uses.
    _reset_redis_singletons()
    eventbus_module._default_redis_client = fake_redis

    result = await db_session.execute(select(User).where(User.email == "ingest_user@example.com"))
    user = result.scalar_one()

    # A large, soon-due obligation against near-zero cash guarantees the
    # risk/gate pipeline actually produces something above IGNORE.
    db_session.add(
        Obligation(
            user_id=user.id,
            label="Rent",
            amount=Decimal("50000"),
            due_date=date.today() + timedelta(days=3),
            is_fixed=True,
            is_paid=False,
            data_source="manual",
            confidence_score=0.9,
        )
    )
    await db_session.commit()

    response = await client.post(
        "/ingest/sms",
        json={
            "raw_sms": "Rs.100.00 credited to A/c XX4417 on 12-01-26 from ACME SOLUTIONS. Avl Bal Rs.100.00",
            "sender": "HDFCBK",
        },
        headers=auth_headers,
    )
    assert response.status_code == 202
    body = response.json()
    trace_id = body["trace_id"]
    event_id = body["event_id"]
    assert event_id is not None

    bus = EventBus(fake_redis)
    ctx = _make_ctx(session_factory, fake_redis, bus)

    # See the identical comment in test_trace_id_propagates_... -- several
    # domain services fall back to their own real redis.asyncio client
    # when nothing is injected, with no seam to inject one through their
    # public methods.
    with patch("redis.asyncio.from_url", return_value=fake_redis):
        financial_event_msg = await _read_one(bus, Topic.FINANCIAL_EVENT, "pipeline", "worker")
        assert financial_event_msg.trace_id == trace_id
        await handle_financial_event(ctx, financial_event_msg)

        state_changed_msg = await _read_one(bus, Topic.STATE_CHANGED, "pipeline", "worker")
        await handle_state_changed(ctx, state_changed_msg)

        snapshot_updated_msg = await _read_one(bus, Topic.SNAPSHOT_UPDATED, "pipeline", "worker")
        await handle_snapshot_updated(ctx, snapshot_updated_msg)

        risk_assessed_msg = await _read_one(bus, Topic.RISK_ASSESSED, "pipeline", "worker")
        await handle_risk_assessed(ctx, risk_assessed_msg)

        intervention_created_msg = await _read_one(bus, Topic.INTERVENTION_CREATED, "pipeline", "worker")
        assert intervention_created_msg.trace_id == trace_id
        await handle_intervention_created(ctx, intervention_created_msg)

    result = await db_session.execute(select(Intervention).where(Intervention.user_id == user.id))
    interventions = list(result.scalars())
    assert len(interventions) == 1
    assert interventions[0].triggered_by_event_id == UUID(event_id)

    status = await get_pipeline_status(fake_redis, trace_id)
    assert status is not None


# ---------------------------------------------------------------------------
# NOTIFICATION DELIVERY: retry backoff + dead letter
# ---------------------------------------------------------------------------


async def test_notification_retry_uses_exponential_backoff_with_jitter(db_session):
    delivery = NotificationDelivery(
        intervention_id=uuid4(), user_id=uuid4(), channel="push", status="pending"
    )
    db_session.add(delivery)
    await db_session.flush()

    result_1 = await deliver(db_session, delivery.id)
    assert result_1.status == "failed"
    assert result_1.attempt_count == 1
    delay_1 = (result_1.next_retry_at - datetime.now(timezone.utc)).total_seconds()
    lo_1 = BACKOFF_BASE_SECONDS * (1 - BACKOFF_JITTER_FRACTION)
    hi_1 = BACKOFF_BASE_SECONDS * (1 + BACKOFF_JITTER_FRACTION)
    assert lo_1 <= delay_1 <= hi_1 + 1  # +1s slack for wall-clock drift during the test

    result_2 = await deliver(db_session, delivery.id)
    assert result_2.attempt_count == 2
    expected_base_2 = BACKOFF_BASE_SECONDS * (BACKOFF_FACTOR**1)
    delay_2 = (result_2.next_retry_at - datetime.now(timezone.utc)).total_seconds()
    lo_2 = expected_base_2 * (1 - BACKOFF_JITTER_FRACTION)
    hi_2 = expected_base_2 * (1 + BACKOFF_JITTER_FRACTION)
    assert lo_2 <= delay_2 <= hi_2 + 1


async def test_five_failed_attempts_move_delivery_to_dead_letter(db_session):
    delivery = NotificationDelivery(
        intervention_id=uuid4(), user_id=uuid4(), channel="push", status="pending"
    )
    db_session.add(delivery)
    await db_session.flush()

    result = None
    for _ in range(MAX_ATTEMPTS_BEFORE_DEAD_LETTER):
        result = await deliver(db_session, delivery.id)

    assert result is not None
    assert result.status == "dead_letter"
    assert result.attempt_count == MAX_ATTEMPTS_BEFORE_DEAD_LETTER
    assert result.next_retry_at is None
