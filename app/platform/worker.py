"""ARQ worker process: background Redis Streams consumer loops (one per
pipeline topic) plus the four scheduled cron jobs.

Pipeline handlers (app.modules.pipeline.handlers.HANDLERS) are NOT
dispatched through ARQ's own job queue in normal operation — they run
directly from the consumer loops started in on_startup, so that each
handler's own ack/redelivery/dead-letter bookkeeping (via EventBus) stays
the single source of truth for retry state, instead of running two
independent retry systems (ARQ's job retries and the Streams-based one)
at once. They're still registered in WorkerSettings.functions (via a thin
ctx-adapting wrapper) so they can be manually enqueued too — e.g. an
admin DLQ replay.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast

import redis.asyncio as redis
from arq import cron
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.modules.decision.shadow import evaluate_outcomes
from app.modules.notification.delivery import retry_failed
from app.modules.pipeline.handlers import HANDLERS, PipelineContext
from app.platform.config import get_settings
from app.platform.eventbus import BusMessage, EventBus, Topic
from app.platform.logging import get_logger

logger = get_logger(__name__)

CONSUMER_GROUP = "pipeline"
JOB_TIMEOUT_SECONDS = 120
MAX_JOBS = 10
CLAIM_STALE_MIN_IDLE_MS = 60_000
RETRY_NOTIFICATIONS_CRON_MINUTES = set(range(0, 60, 5))  # every 5 minutes


CONSUME_RESTART_BACKOFF_SECONDS = 2.0


async def _consume_topic(ctx: dict[str, Any], topic: Topic) -> None:
    event_bus: EventBus = ctx["event_bus"]
    pipeline_ctx: PipelineContext = ctx["pipeline_ctx"]
    handler = HANDLERS[topic]
    # The try/except around the handler call below only protects against a
    # bad MESSAGE (one handler's own exception) -- it does nothing for a
    # failure in the subscription itself (a dropped Redis connection, or
    # the consumer group disappearing out from under a long-running
    # process, e.g. an operator flushing Redis without restarting
    # consumers). EventBus.subscribe() only calls _ensure_group() ONCE,
    # before its internal `while True`, so a group lost after that point
    # raises NOGROUP on the next xreadgroup call, which propagates out of
    # the `async for` itself -- outside the inner try/except entirely.
    # Uncaught, that silently and permanently kills this topic's consumer
    # task: create_task()'s result is never awaited, so nothing surfaces
    # the failure, and the topic just stops being processed forever with
    # no further log output. The outer loop here makes that recoverable
    # instead of fatal: log it, back off briefly, and resubscribe (which
    # recreates the group via _ensure_group's mkstream=True).
    while True:
        try:
            async for message in event_bus.subscribe(topic, CONSUMER_GROUP, f"worker-{topic.value}"):
                try:
                    await handler(pipeline_ctx, message)
                except Exception:
                    # Each handler's own _run_stage already logs/dead-letters
                    # on failure -- this inner guard exists only so one
                    # unexpected error can't kill the whole consumer loop.
                    logger.error("consumer_loop_handler_error", topic=topic.value, exc_info=True)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.error("consumer_loop_subscription_error", topic=topic.value, exc_info=True)
            await asyncio.sleep(CONSUME_RESTART_BACKOFF_SECONDS)


async def startup(ctx: dict[str, Any]) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    # A separate client from arq's own ctx['redis'] pool — mixing the two
    # would overwrite arq's internal job-queue connection.
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    event_bus = EventBus(redis_client)

    ctx["engine"] = engine
    ctx["session_factory"] = session_factory
    ctx["redis_client"] = redis_client
    ctx["event_bus"] = event_bus
    ctx["pipeline_ctx"] = PipelineContext(
        session_factory=session_factory,
        redis=redis_client,
        event_bus=event_bus,
        group=CONSUMER_GROUP,
        consumer="worker",
    )
    ctx["consumer_tasks"] = [asyncio.create_task(_consume_topic(ctx, topic)) for topic in HANDLERS]
    logger.info("worker_started", topics=[t.value for t in HANDLERS])


async def shutdown(ctx: dict[str, Any]) -> None:
    for task in ctx.get("consumer_tasks", []):
        task.cancel()
    await asyncio.gather(*ctx.get("consumer_tasks", []), return_exceptions=True)
    if "redis_client" in ctx:
        await ctx["redis_client"].aclose()
    if "engine" in ctx:
        await ctx["engine"].dispose()
    logger.info("worker_stopped")


async def evaluate_shadow_outcomes(ctx: dict[str, Any]) -> int:
    async with ctx["session_factory"]() as session:
        count = await evaluate_outcomes(session)
        await session.commit()
    return count


async def retry_failed_notifications(ctx: dict[str, Any]) -> int:
    async with ctx["session_factory"]() as session:
        count = await retry_failed(session)
        await session.commit()
    return count


async def recompute_stale_snapshots(ctx: dict[str, Any]) -> int:
    """Rebuilds the Twin snapshot for every active user — a safety net
    catching drift from any event that, for whatever reason, never
    triggered an explicit cache invalidation."""
    from sqlalchemy import select

    from app.models.tables import User
    from app.modules.twin.service import TwinService

    count = 0
    async with ctx["session_factory"]() as session:
        result = await session.execute(select(User.id).where(User.deleted_at.is_(None)))
        for (user_id,) in result.all():
            await TwinService().rebuild(session, user_id)
            count += 1
        await session.commit()
    return count


async def claim_stale_messages(ctx: dict[str, Any]) -> int:
    """Recovers messages left pending by a crashed consumer via
    XAUTOCLAIM and runs them through the normal handler — their
    delivery_count already reflects the earlier attempt(s), so a message
    already at MAX_DELIVERY_ATTEMPTS still gets dead-lettered rather than
    retried forever."""
    event_bus: EventBus = ctx["event_bus"]
    pipeline_ctx: PipelineContext = ctx["pipeline_ctx"]
    reclaimed = 0
    for topic, handler in HANDLERS.items():
        messages = await event_bus.claim_stale(
            topic, CONSUMER_GROUP, "claim-stale-cron", min_idle_ms=CLAIM_STALE_MIN_IDLE_MS
        )
        for message in messages:
            await handler(pipeline_ctx, message)
            reclaimed += 1
    return reclaimed


def _adapt_for_arq(handler: Any) -> Any:
    """Wraps a (PipelineContext, BusMessage) handler so it can also be
    registered as a plain ARQ task function, invoked with ARQ's own raw
    ctx (which carries our PipelineContext nested under ctx['pipeline_ctx'],
    set up in startup())."""

    async def _wrapper(ctx: dict[str, Any], message: BusMessage) -> None:
        await handler(cast(PipelineContext, ctx["pipeline_ctx"]), message)

    _wrapper.__name__ = handler.__name__
    return _wrapper


class WorkerSettings:
    functions = [_adapt_for_arq(handler) for handler in HANDLERS.values()] + [
        evaluate_shadow_outcomes,
        retry_failed_notifications,
        recompute_stale_snapshots,
        claim_stale_messages,
    ]
    cron_jobs = [
        # Daily, off-peak: checks whether predicted shortfalls actually
        # materialized for interventions whose horizon has passed.
        cron(evaluate_shadow_outcomes, hour=3, minute=0),
        # Every 5 minutes: picks up failed deliveries whose backoff has elapsed.
        cron(retry_failed_notifications, minute=RETRY_NOTIFICATIONS_CRON_MINUTES),
        # Hourly: safety-net snapshot rebuild.
        cron(recompute_stale_snapshots, minute=0),
        # Every minute: recovers messages orphaned by a crashed consumer.
        cron(claim_stale_messages, second=0),
    ]
    redis_settings = RedisSettings.from_dsn(get_settings().REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = MAX_JOBS
    job_timeout = JOB_TIMEOUT_SECONDS
