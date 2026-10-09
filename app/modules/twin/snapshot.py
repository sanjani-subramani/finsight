"""Assembles the frozen FinancialStateSnapshot contract — the one object
every downstream module (risk, decision, org) reads instead of touching
raw events or the fold directly.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import FinancialStateSnapshot
from app.contracts.events import Goal as GoalContract
from app.models.tables import Goal as GoalRow
from app.modules.confidence.aggregator import compute_state_confidence
from app.modules.twin import fold
from app.modules.twin.forecast import IncomeForecaster
from app.modules.twin.obligations import get_active_obligations
from app.modules.twin.weather import compute_weather
from app.platform.cache import RedisLike
from app.platform.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

SNAPSHOT_CACHE_PREFIX = "snapshot"
SNAPSHOT_CACHE_TTL_SECONDS = 300
OBLIGATIONS_HORIZON_DAYS = 90
WEATHER_WINDOW_DAYS = 30

_default_redis_client: RedisLike | None = None


def _get_redis(injected: RedisLike | None) -> RedisLike:
    if injected is not None:
        return injected
    global _default_redis_client
    if _default_redis_client is None:
        _default_redis_client = redis.from_url(get_settings().REDIS_URL, decode_responses=True)
    return _default_redis_client


def _cache_key(user_id: UUID) -> str:
    return f"{SNAPSHOT_CACHE_PREFIX}:{user_id}"


async def _load_or_build_accumulator(session: AsyncSession, user_id: UUID) -> fold.TwinAccumulator:
    row = await fold._load_twin_state_row(session, user_id)
    if row is not None:
        return fold._accumulator_from_row(row)
    state = await fold.rebuild_state(session, user_id)
    await fold._persist_fold_columns(session, user_id, state)
    return state


async def _load_goals(session: AsyncSession, user_id: UUID) -> list[GoalContract]:
    result = await session.execute(
        select(GoalRow).where(GoalRow.user_id == user_id, GoalRow.deleted_at.is_(None))
    )
    return [
        GoalContract(
            goal_id=row.id,
            label=row.label,
            target_amount=Decimal(str(row.target_amount)),
            saved_amount=Decimal(str(row.saved_amount)),
            target_date=row.target_date,
            priority=row.priority,
            is_flexible=row.is_flexible,
        )
        for row in result.scalars()
    ]


async def _read_cache(user_id: UUID, redis_client: RedisLike | None) -> FinancialStateSnapshot | None:
    try:
        raw = await _get_redis(redis_client).get(_cache_key(user_id))
    except Exception:
        logger.warning("snapshot_cache_read_failed", user_id=str(user_id), exc_info=True)
        return None
    if not raw:  # missing or invalidated (empty-string sentinel)
        return None
    try:
        return FinancialStateSnapshot.model_validate_json(raw)
    except Exception:
        logger.warning("snapshot_cache_corrupt", user_id=str(user_id), exc_info=True)
        return None


async def _write_cache(
    user_id: UUID, snapshot: FinancialStateSnapshot, redis_client: RedisLike | None
) -> None:
    try:
        await _get_redis(redis_client).set(_cache_key(user_id), snapshot.model_dump_json())
    except Exception:
        logger.warning("snapshot_cache_write_failed", user_id=str(user_id), exc_info=True)


async def invalidate_snapshot(user_id: UUID, redis_client: RedisLike | None = None) -> None:
    """Called immediately on any new event, obligation change, or goal
    change (see TwinService) — never lazily, never batched.

    INVALIDATION STRATEGY: a stale snapshot in a financial product is
    worse than a slow one. Showing someone a cash position or a weather
    severity that's already wrong can lead them to spend money they
    don't actually have, or miss a warning that would have changed their
    decision. We would always rather pay the cost of an extra rebuild on
    the next read than risk serving stale financial state — so
    invalidation overwrites the cache entry with an empty sentinel
    (treated as a miss by _read_cache) rather than waiting out the TTL.
    """
    try:
        await _get_redis(redis_client).set(_cache_key(user_id), "")
    except Exception:
        logger.warning("snapshot_cache_invalidate_failed", user_id=str(user_id), exc_info=True)


async def build_snapshot(
    session: AsyncSession,
    user_id: UUID,
    use_cache: bool = True,
    redis_client: RedisLike | None = None,
) -> FinancialStateSnapshot:
    if use_cache:
        cached = await _read_cache(user_id, redis_client)
        if cached is not None:
            return cached

    accumulator = await _load_or_build_accumulator(session, user_id)
    income_forecast = await IncomeForecaster().forecast(session, user_id)
    obligations = await get_active_obligations(session, user_id, horizon_days=OBLIGATIONS_HORIZON_DAYS)
    goals = await _load_goals(session, user_id)
    state_confidence = await compute_state_confidence(session, user_id)

    window_end = date.today() + timedelta(days=WEATHER_WINDOW_DAYS)
    obligations_30d = sum(
        (o.amount for o in obligations if o.due_date <= window_end and not o.is_paid),
        Decimal("0"),
    )

    weather_result = compute_weather(
        cash=accumulator.cash,
        obligations_30d=obligations_30d,
        income_p10=income_forecast.p10,
        confidence=state_confidence.score,
    )

    # NAIVE INTERIM VERSION: the real simulation-based safe-to-spend
    # (Monte Carlo across scenarios) arrives in Step 6. This is just
    # "what's left after this month's known obligations and the
    # emergency-fund reserve," floored at zero.
    safe_to_spend = max(Decimal("0"), accumulator.cash - obligations_30d - accumulator.emergency_fund)

    snapshot = FinancialStateSnapshot(
        user_id=user_id,
        cash_available=accumulator.cash,
        emergency_fund=accumulator.emergency_fund,
        income_forecast=income_forecast,
        obligations=obligations,
        goals=goals,
        weather=weather_result.weather,
        shortfall_risks=[],
        # Step 6 (Monte Carlo simulation) computes this properly; None
        # here means "not yet modelled," not "no danger."
        time_to_danger_days=None,
        safe_to_spend=safe_to_spend,
        state_confidence=state_confidence.score,
        unconfirmed_event_count=state_confidence.unconfirmed_count,
        contains_simulated_data=accumulator.simulated_seen,
        last_event_id=accumulator.last_event_id,
        events_applied=accumulator.events_applied,
    )

    if use_cache:
        await _write_cache(user_id, snapshot, redis_client)

    return snapshot
