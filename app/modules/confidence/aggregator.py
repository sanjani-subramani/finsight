"""Produces one state-level confidence number: how much the system
actually believes its own picture of a user's finances right now."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import DataSource
from app.models.tables import ConflictRecord, FinancialEvent
from app.modules.confidence.counterparty import CounterpartyResolver
from app.modules.confidence.decay import apply_decay, effective_age_days, is_confirmed
from app.platform.timeutils import as_aware_utc

LOOKBACK_DAYS = 90
CONFLICT_PENALTY_PER_ITEM = 0.05
CONFLICT_PENALTY_MAX = 0.20
SIMULATED_DATA_PENALTY = 0.10


@dataclass
class StateConfidence:
    score: float
    unconfirmed_count: int
    conflicted_count: int
    simulated_count: int
    contributing_events: int
    breakdown: dict[str, Any] = field(default_factory=dict)


async def compute_state_confidence(
    session: AsyncSession,
    user_id: UUID,
    resolver: CounterpartyResolver | None = None,
) -> StateConfidence:
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    stmt = select(FinancialEvent).where(
        FinancialEvent.user_id == user_id,
        FinancialEvent.occurred_at >= cutoff,
        FinancialEvent.duplicate_of.is_(None),
        FinancialEvent.superseded_by.is_(None),
    )
    result = await session.execute(stmt)
    events = list(result.scalars())

    conflicted_count = await _count_unresolved_conflicts(session, user_id)

    if not events:
        return StateConfidence(
            score=0.0,
            unconfirmed_count=0,
            conflicted_count=conflicted_count,
            simulated_count=0,
            contributing_events=0,
            breakdown={
                "reason": "no contributing events in lookback window",
                "lookback_days": LOOKBACK_DAYS,
            },
        )

    now = datetime.now(timezone.utc)
    weighted_sum = 0.0
    total_weight = 0.0
    unconfirmed_count = 0
    simulated_count = 0
    per_event: list[dict[str, Any]] = []

    for row in events:
        source = DataSource(row.data_source)
        if source == DataSource.simulated:
            simulated_count += 1

        confirmed = await is_confirmed(session, row, resolver=resolver)
        if not confirmed:
            unconfirmed_count += 1

        raw_age_days = max(0.0, (now - as_aware_utc(row.occurred_at)).total_seconds() / 86400.0)
        age_days = effective_age_days(raw_age_days, source)
        base_confidence = float(row.confidence_score)
        effective_confidence = apply_decay(base_confidence, age_days, confirmed)

        amount = float(row.amount) if row.amount is not None else 0.0
        # WEIGHT BY FINANCIAL MAGNITUDE: log1p(amount), not amount itself.
        # Without magnitude weighting, twenty confident ₹50 coffee runs
        # would statistically drown out one uncertain ₹18,000 payment in
        # a plain average — but that ₹18,000 event is the one that
        # actually determines whether rent gets paid this month. log1p
        # still lets bigger amounts matter more without letting them
        # dominate absolutely (a ₹1,000,000 event shouldn't erase every
        # other signal outright).
        weight = math.log1p(amount)

        weighted_sum += effective_confidence * weight
        total_weight += weight

        per_event.append(
            {
                "event_id": str(row.id),
                "data_source": source.value,
                "base_confidence": base_confidence,
                "age_days": round(raw_age_days, 1),
                "effective_age_days": round(age_days, 1),
                "is_confirmed": confirmed,
                "effective_confidence": round(effective_confidence, 4),
                "amount": amount,
                "weight": round(weight, 4),
            }
        )

    weighted_mean = weighted_sum / total_weight if total_weight > 0 else 0.0

    conflict_penalty = min(CONFLICT_PENALTY_MAX, conflicted_count * CONFLICT_PENALTY_PER_ITEM)
    simulated_penalty = SIMULATED_DATA_PENALTY if simulated_count > 0 else 0.0

    raw_score = weighted_mean - conflict_penalty - simulated_penalty
    score = max(0.0, min(1.0, raw_score))

    breakdown: dict[str, Any] = {
        "lookback_days": LOOKBACK_DAYS,
        "weighted_mean_confidence": round(weighted_mean, 4),
        "total_weight": round(total_weight, 4),
        "conflict_penalty": conflict_penalty,
        "conflict_penalty_per_item": CONFLICT_PENALTY_PER_ITEM,
        "conflict_penalty_max": CONFLICT_PENALTY_MAX,
        "simulated_penalty": simulated_penalty,
        "raw_score_before_clamp": round(raw_score, 4),
        "final_score": round(score, 4),
        "per_event": per_event,
    }

    return StateConfidence(
        score=score,
        unconfirmed_count=unconfirmed_count,
        conflicted_count=conflicted_count,
        simulated_count=simulated_count,
        contributing_events=len(events),
        breakdown=breakdown,
    )


async def _count_unresolved_conflicts(session: AsyncSession, user_id: UUID) -> int:
    stmt = select(ConflictRecord).where(
        ConflictRecord.user_id == user_id,
        ConflictRecord.user_overridden.is_(False),
    )
    result = await session.execute(stmt)
    return len(list(result.scalars()))
