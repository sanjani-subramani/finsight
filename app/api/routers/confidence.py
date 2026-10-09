from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.confidence import (
    ConflictOverrideRequest,
    ConflictResponse,
    DuplicateResponse,
    StateConfidenceResponse,
    UnmergeResponse,
)
from app.models.tables import ConflictRecord, FinancialEvent, User
from app.modules.confidence.aggregator import compute_state_confidence
from app.modules.confidence.counterparty import CounterpartyResolver
from app.modules.confidence.service import ConfidenceService
from app.platform.audit import write_audit
from app.platform.database import get_session
from app.platform.deps import get_client_ip, get_current_user

router = APIRouter(prefix="/confidence", tags=["confidence"])


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


@router.get("/state", response_model=StateConfidenceResponse)
async def get_state_confidence(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> StateConfidenceResponse:
    state = await compute_state_confidence(session, current_user.id)
    return StateConfidenceResponse(
        score=state.score,
        unconfirmed_count=state.unconfirmed_count,
        conflicted_count=state.conflicted_count,
        simulated_count=state.simulated_count,
        contributing_events=state.contributing_events,
        breakdown=state.breakdown,
    )


@router.get("/conflicts", response_model=list[ConflictResponse])
async def list_conflicts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ConflictRecord]:
    result = await session.execute(
        select(ConflictRecord)
        .where(
            ConflictRecord.user_id == current_user.id,
            ConflictRecord.user_overridden.is_(False),
        )
        .order_by(ConflictRecord.resolved_at.desc())
    )
    return list(result.scalars())


@router.post("/conflicts/{conflict_id}/override", response_model=ConflictResponse)
async def override_conflict(
    conflict_id: UUID,
    payload: ConflictOverrideRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConflictRecord:
    result = await session.execute(
        select(ConflictRecord).where(
            ConflictRecord.id == conflict_id,
            ConflictRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conflict not found"
        )

    if payload.correct_event_id not in (record.event_a_id, record.event_b_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="correct_event_id must be one of this conflict's two events",
        )

    events_result = await session.execute(
        select(FinancialEvent).where(
            FinancialEvent.id.in_([record.event_a_id, record.event_b_id])
        )
    )
    events_by_id = {e.id: e for e in events_result.scalars()}
    correct = events_by_id.get(payload.correct_event_id)
    if correct is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conflicting event not found"
        )
    other_id = (
        record.event_a_id if payload.correct_event_id == record.event_b_id else record.event_b_id
    )
    other = events_by_id.get(other_id)

    # The user's word about their own transaction is final: full
    # confidence, and this row is no longer treated as superseded even if
    # the automatic resolution had picked the other side.
    correct.confidence_score = 1.0
    correct.superseded_by = None
    if other is not None:
        other.superseded_by = correct.id

    record.winner_event_id = correct.id
    record.user_overridden = True

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="confidence.conflict_overridden",
        resource_type="conflict_record",
        resource_id=str(record.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"correct_event_id": str(correct.id)},
    )

    await ConfidenceService().recompute_all(session, current_user.id)

    return record


@router.get("/duplicates", response_model=list[DuplicateResponse])
async def list_duplicates(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[DuplicateResponse]:
    result = await session.execute(
        select(FinancialEvent).where(
            FinancialEvent.user_id == current_user.id,
            FinancialEvent.duplicate_of.isnot(None),
        )
    )
    rows = list(result.scalars())

    resolver = CounterpartyResolver()
    responses: list[DuplicateResponse] = []

    for row in rows:
        canonical_result = await session.execute(
            select(FinancialEvent).where(FinancialEvent.id == row.duplicate_of)
        )
        canonical = canonical_result.scalar_one_or_none()

        similarity = 0.0
        reasons: list[str] = []
        if canonical is not None:
            match = await resolver.resolve(row.counterparty, canonical.counterparty)
            similarity = match.similarity
            reasons = [
                f"counterparty match via {match.method}",
                "amount within tolerance",
                f"different data_source ({row.data_source} vs {canonical.data_source})",
            ]

        responses.append(
            DuplicateResponse(
                id=row.id,
                duplicate_of=row.duplicate_of,
                event_type=row.event_type,
                amount=row.amount,
                occurred_at=row.occurred_at,
                counterparty=row.counterparty,
                data_source=row.data_source,
                similarity=similarity,
                reasons=reasons,
            )
        )

    return responses


@router.post("/duplicates/{event_id}/unmerge", response_model=UnmergeResponse)
async def unmerge_duplicate(
    event_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UnmergeResponse:
    result = await session.execute(
        select(FinancialEvent).where(
            FinancialEvent.id == event_id,
            FinancialEvent.user_id == current_user.id,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    if row.duplicate_of is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Event is not marked as a duplicate"
        )

    previous_canonical = row.duplicate_of
    row.duplicate_of = None

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="confidence.duplicate_unmerged",
        resource_type="financial_event",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"previous_canonical_event_id": str(previous_canonical)},
    )

    state = await ConfidenceService().recompute_all(session, current_user.id)

    return UnmergeResponse(event_id=row.id, unmerged=True, state_confidence=state.score)
