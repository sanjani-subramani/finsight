"""One handler per pipeline stage, wiring the event bus to the domain
services built in Steps 3-8.

CRITICAL — IDEMPOTENCY: Redis Streams delivers AT LEAST ONCE. A crashed
consumer, a slow handler that misses its ack, or claim_stale() recovering
a stale message can all cause the SAME message id to reach a handler
twice. Every handler here MUST tolerate that: _run_stage() checks a
"processed" marker in Redis (24h TTL) before doing any work, and the
underlying domain services (write_event's source_ref uniqueness,
ConfidenceService's cross-source dedup, the Twin's event-sourced fold,
RiskService's dismissal-respecting collision persistence) are each
independently idempotent too — belt and suspenders, since the processed
marker alone cannot make an already-published downstream message
un-publish itself (see the design note in _run_stage below).

CRITICAL — ERROR HANDLING: on an exception, we log it (with trace_id) and
do NOT ack — the message stays pending so a future read/claim_stale
retries it. Only after MAX_DELIVERY_ATTEMPTS do we give up: dead_letter
the message and ack it, so one permanently-broken ("poison") message
cannot wedge the stream for every message behind it forever.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypedDict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.tables import FinancialEvent, NotificationDelivery
from app.modules.confidence.service import ConfidenceService
from app.modules.decision.service import DecisionService
from app.modules.notification.delivery import deliver
from app.modules.risk.service import RiskService
from app.modules.twin.service import TwinService
from app.platform.cache import RedisLike
from app.platform.eventbus import BusMessage, EventBus, Topic
from app.platform.logging import get_logger

logger = get_logger(__name__)

MAX_DELIVERY_ATTEMPTS = 3
PROCESSED_ID_TTL_SECONDS = 24 * 3600
_PROCESSED_KEY_PREFIX = "pipeline:processed:"
_STATUS_KEY_PREFIX = "pipeline:status:"
PIPELINE_STATUS_TTL_SECONDS = 24 * 3600


class PipelineContext(TypedDict):
    session_factory: async_sessionmaker[AsyncSession]
    redis: RedisLike
    event_bus: EventBus
    group: str
    consumer: str


async def _already_processed(redis: RedisLike, message_id: str) -> bool:
    return bool(await redis.exists(f"{_PROCESSED_KEY_PREFIX}{message_id}"))


async def _mark_processed(redis: RedisLike, message_id: str) -> None:
    await redis.setex(f"{_PROCESSED_KEY_PREFIX}{message_id}", PROCESSED_ID_TTL_SECONDS, "1")


async def set_pipeline_status(redis: RedisLike, trace_id: str, stage: str) -> None:
    if not trace_id:
        return
    await redis.setex(f"{_STATUS_KEY_PREFIX}{trace_id}", PIPELINE_STATUS_TTL_SECONDS, stage)


async def get_pipeline_status(redis: RedisLike, trace_id: str) -> str | None:
    value = await redis.get(f"{_STATUS_KEY_PREFIX}{trace_id}")
    return value if isinstance(value, str) or value is None else str(value)


async def _run_stage(
    ctx: PipelineContext,
    message: BusMessage,
    stage_name: str,
    work: Callable[[AsyncSession], Awaitable[None]],
) -> None:
    """Shared idempotency + commit + ack + error-handling wrapper every
    handler below uses, so that behavior isn't duplicated five times.

    DESIGN NOTE on the at-least-once / duplicate-publish tradeoff: work()
    may itself publish a downstream message before this stage's own
    commit+ack complete. If the process crashes in that exact window (work
    succeeded, ack didn't happen), a retry will re-run work() and publish
    a SECOND downstream message. We accept this — it's the well-known
    cost of choreography over Redis Streams without a full transactional
    outbox — and rely on each downstream domain service's own idempotency
    (see module docstring) to make the eventual duplicate a no-op rather
    than a duplicated side effect. A true outbox pattern would close this
    gap entirely but is out of scope here.
    """
    redis = ctx["redis"]
    event_bus = ctx["event_bus"]
    group = ctx["group"]

    if await _already_processed(redis, message.id):
        await event_bus.ack(message.topic, group, message.id)
        return

    try:
        async with ctx["session_factory"]() as session:
            await work(session)
            await session.commit()
        await set_pipeline_status(redis, message.trace_id, stage_name)
        await _mark_processed(redis, message.id)
        await event_bus.ack(message.topic, group, message.id)
    except Exception:
        logger.error(
            "pipeline_stage_failed",
            stage=stage_name,
            trace_id=message.trace_id,
            message_id=message.id,
            delivery_count=message.delivery_count,
            exc_info=True,
        )
        if message.delivery_count >= MAX_DELIVERY_ATTEMPTS:
            await event_bus.dead_letter(
                message.topic, message, reason=f"{stage_name} failed after {message.delivery_count} attempts"
            )
            await set_pipeline_status(redis, message.trace_id, "dead_letter")
            await event_bus.ack(message.topic, group, message.id)
        # else: leave unacked so XREADGROUP/claim_stale redelivers it.


async def handle_financial_event(ctx: PipelineContext, message: BusMessage) -> None:
    """IDEMPOTENT — see module docstring. Runs the confidence engine over
    a newly-ingested event, then hands off to the Twin fold.
    """

    async def work(session: AsyncSession) -> None:
        event_id = UUID(message.payload["event_id"])
        await ConfidenceService().process_event(session, event_id)
        row = await session.get(FinancialEvent, event_id)
        if row is None:
            return
        await ctx["event_bus"].publish(
            Topic.STATE_CHANGED,
            {"event_id": str(event_id), "user_id": str(row.user_id)},
            message.trace_id,
        )

    await _run_stage(ctx, message, "state_changed", work)


async def handle_state_changed(ctx: PipelineContext, message: BusMessage) -> None:
    """IDEMPOTENT — see module docstring. Folds the event into the Twin.
    TwinService.on_event_ingested() already invalidates the cached
    snapshot itself (see its docstring), so there is nothing further to
    invalidate here.
    """

    async def work(session: AsyncSession) -> None:
        event_id = UUID(message.payload["event_id"])
        user_id = UUID(message.payload["user_id"])
        row = await session.get(FinancialEvent, event_id)
        if row is None:
            return
        await TwinService().on_event_ingested(session, row)
        await ctx["event_bus"].publish(
            Topic.SNAPSHOT_UPDATED,
            {"user_id": str(user_id), "event_id": str(event_id)},
            message.trace_id,
        )

    await _run_stage(ctx, message, "snapshot_updated", work)


async def handle_snapshot_updated(ctx: PipelineContext, message: BusMessage) -> None:
    """IDEMPOTENT — see module docstring. RiskService.assess() already
    runs SimulationService.run() as its own first step (see
    app.modules.risk.service.RiskService.assess), so there is no separate
    simulation call to make here.
    """

    async def work(session: AsyncSession) -> None:
        user_id = UUID(message.payload["user_id"])
        await RiskService().assess(session, user_id)
        await ctx["event_bus"].publish(
            Topic.RISK_ASSESSED,
            {"user_id": str(user_id), "trigger_event_id": message.payload.get("event_id")},
            message.trace_id,
        )

    await _run_stage(ctx, message, "risk_assessed", work)


async def handle_risk_assessed(ctx: PipelineContext, message: BusMessage) -> None:
    """IDEMPOTENT — see module docstring. Re-running decide() for a
    message seen twice would, in the worst case, create a second
    intervention for the same underlying risk state; the processed-id
    check in _run_stage is the primary guard against that for this
    handler specifically (DecisionService itself has no additional
    dedup of its own).
    """

    async def work(session: AsyncSession) -> None:
        user_id = UUID(message.payload["user_id"])
        trigger_event_id_raw = message.payload.get("trigger_event_id")
        trigger_event_id = UUID(trigger_event_id_raw) if trigger_event_id_raw else None
        intervention = await DecisionService().decide(session, user_id, trigger_event_id=trigger_event_id)
        if intervention is not None:
            await ctx["event_bus"].publish(
                Topic.INTERVENTION_CREATED,
                {"intervention_id": str(intervention.intervention_id), "user_id": str(user_id)},
                message.trace_id,
            )

    await _run_stage(ctx, message, "risk_assessed_complete", work)


async def handle_intervention_created(ctx: PipelineContext, message: BusMessage) -> None:
    """IDEMPOTENT — see module docstring. DecisionService.decide()
    already creates any warranted NotificationDelivery row (status
    "pending") inline when it builds the intervention — see Step 8. This
    handler's job is the actual delivery ATTEMPT, moved off the request
    path: it picks up whatever pending delivery rows exist for this
    intervention and runs deliver() on each. If decide() decided no
    delivery was warranted (shadow mode, or severity below NOTIFY), there
    is nothing pending and this is a no-op — which is correct, not a bug.
    """

    async def work(session: AsyncSession) -> None:
        intervention_id = UUID(message.payload["intervention_id"])
        result = await session.execute(
            select(NotificationDelivery).where(
                NotificationDelivery.intervention_id == intervention_id,
                NotificationDelivery.status == "pending",
            )
        )
        for delivery_row in result.scalars():
            await deliver(session, delivery_row.id)

    await _run_stage(ctx, message, "intervention_delivered", work)


async def handle_threat_event(ctx: PipelineContext, message: BusMessage) -> None:
    """IDEMPOTENT — see module docstring. This is the single place that
    turns a detected threat into a decision: app.modules.threat.service
    deliberately does NOT call DecisionService itself, precisely so a
    threat can never produce two interventions from two call sites
    racing each other.
    """

    async def work(session: AsyncSession) -> None:
        user_id = UUID(message.payload["user_id"])
        threat_id = UUID(message.payload["threat_id"])
        await DecisionService().decide(session, user_id, trigger_threat_id=threat_id)

    await _run_stage(ctx, message, "threat_event_routed", work)


HANDLERS: dict[Topic, Callable[[PipelineContext, BusMessage], Awaitable[None]]] = {
    Topic.FINANCIAL_EVENT: handle_financial_event,
    Topic.STATE_CHANGED: handle_state_changed,
    Topic.SNAPSHOT_UPDATED: handle_snapshot_updated,
    Topic.RISK_ASSESSED: handle_risk_assessed,
    Topic.INTERVENTION_CREATED: handle_intervention_created,
    Topic.THREAT_EVENT: handle_threat_event,
}
