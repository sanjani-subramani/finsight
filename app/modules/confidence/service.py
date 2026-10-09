"""Orchestrates the confidence pipeline for one newly-ingested event, and
supports a full state recompute after a user manually overrides a
resolution.

Note on "is_confirmed": there is no stored is_confirmed column anywhere —
it is always computed live (see decay.is_confirmed) from whatever
corroborating events currently exist. That means an older event is
automatically promoted to "confirmed" the next time state confidence is
computed, as soon as a corroborating second-source event exists, with no
separate recompute step needed for it here.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import ConflictRecord, FinancialEvent
from app.modules.confidence.aggregator import StateConfidence, compute_state_confidence
from app.modules.confidence.conflict import apply_resolution, detect_conflicts, resolve_conflict
from app.modules.confidence.counterparty import CounterpartyResolver
from app.modules.confidence.dedup import find_duplicates, mark_duplicate
from app.platform.audit import write_audit
from app.platform.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConfidenceOutcome:
    event_id: UUID
    was_marked_duplicate: bool
    duplicate_of: UUID | None
    conflicts_resolved: int
    state_confidence: StateConfidence | None


class ConfidenceService:
    def __init__(self, resolver: CounterpartyResolver | None = None) -> None:
        self._resolver = resolver or CounterpartyResolver()

    async def process_event(self, session: AsyncSession, event_id: UUID) -> ConfidenceOutcome:
        event = await self._load_event(session, event_id)
        if event is None:
            raise ValueError(f"no financial_events row with id {event_id}")

        duplicates = await find_duplicates(session, event, resolver=self._resolver)
        if duplicates:
            best = max(duplicates, key=lambda d: d.similarity)
            await mark_duplicate(session, event.id, best.existing_event_id)
            await write_audit(
                session,
                actor_user_id=event.user_id,
                action="confidence.duplicate_marked",
                resource_type="financial_event",
                resource_id=str(event.id),
                payload={
                    "canonical_event_id": str(best.existing_event_id),
                    "similarity": best.similarity,
                    "reasons": best.reasons,
                },
            )
            return ConfidenceOutcome(
                event_id=event.id,
                was_marked_duplicate=True,
                duplicate_of=best.existing_event_id,
                conflicts_resolved=0,
                state_confidence=None,
            )

        conflicts = await detect_conflicts(session, event, resolver=self._resolver)
        conflicts_resolved = 0
        for conflict in conflicts:
            other = await self._load_event(session, conflict.event_b_id)
            if other is None:
                continue

            resolution = resolve_conflict(event, other)
            await apply_resolution(session, resolution, event, other)

            session.add(
                ConflictRecord(
                    user_id=event.user_id,
                    event_a_id=event.id,
                    event_b_id=other.id,
                    field_name=conflict.field,
                    value_a=conflict.value_a,
                    value_b=conflict.value_b,
                    winner_event_id=resolution.winner_id,
                    winner_reason=resolution.winner_reason,
                )
            )
            conflicts_resolved += 1

            await write_audit(
                session,
                actor_user_id=event.user_id,
                action="confidence.conflict_resolved",
                resource_type="financial_event",
                resource_id=str(conflict.event_a_id),
                payload={
                    "event_b_id": str(conflict.event_b_id),
                    "field": conflict.field,
                    "winner_id": str(resolution.winner_id),
                    "reason": resolution.winner_reason,
                },
            )

        await session.flush()

        state_confidence = await compute_state_confidence(
            session, event.user_id, resolver=self._resolver
        )

        return ConfidenceOutcome(
            event_id=event.id,
            was_marked_duplicate=False,
            duplicate_of=None,
            conflicts_resolved=conflicts_resolved,
            state_confidence=state_confidence,
        )

    async def recompute_all(self, session: AsyncSession, user_id: UUID) -> StateConfidence:
        # Deliberately just the aggregate, not a full re-run of dedup/
        # conflict detection: re-running those after a user override
        # could re-detect and re-resolve the very conflict they just
        # corrected, silently undoing their decision.
        return await compute_state_confidence(session, user_id, resolver=self._resolver)

    @staticmethod
    async def _load_event(session: AsyncSession, event_id: UUID) -> FinancialEvent | None:
        result = await session.execute(
            select(FinancialEvent).where(FinancialEvent.id == event_id)
        )
        return result.scalar_one_or_none()
