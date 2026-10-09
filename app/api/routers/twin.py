from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.twin import (
    GoalCreateRequest,
    GoalResponse,
    GoalUpdateRequest,
    IncomeSourceCreateRequest,
    IncomeSourceResponse,
    ObligationCreateRequest,
    ObligationResponse,
    ObligationUpdateRequest,
    RecurringCandidateResponse,
    StateResponse,
)
from app.contracts.events import FinancialStateSnapshot, Goal, Obligation
from app.models.tables import User
from app.modules.twin.service import TwinService
from app.platform.audit import write_audit
from app.platform.database import get_session
from app.platform.deps import get_client_ip, get_current_user

router = APIRouter(prefix="/twin", tags=["twin"])


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


def _service() -> TwinService:
    return TwinService()


@router.get("/snapshot", response_model=FinancialStateSnapshot)
async def get_snapshot(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FinancialStateSnapshot:
    return await _service().get_snapshot(session, current_user.id)


@router.get("/state", response_model=StateResponse)
async def get_state(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> StateResponse:
    snapshot = await _service().get_snapshot(session, current_user.id)
    return StateResponse(
        cash_available=snapshot.cash_available,
        weather=snapshot.weather,
        state_confidence=snapshot.state_confidence,
    )


@router.post("/rebuild", response_model=FinancialStateSnapshot)
async def rebuild_twin(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FinancialStateSnapshot:
    snapshot = await _service().rebuild(session, current_user.id)
    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="twin.rebuilt",
        resource_type="twin_state",
        resource_id=str(current_user.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"events_applied": snapshot.events_applied},
    )
    return snapshot


# -- Obligations ------------------------------------------------------------


@router.get("/obligations", response_model=list[Obligation])
async def list_obligations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Obligation]:
    return await _service().list_obligations(session, current_user.id)


@router.post("/obligations", response_model=ObligationResponse, status_code=status.HTTP_201_CREATED)
async def create_obligation(
    payload: ObligationCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ObligationResponse:
    row = await _service().add_obligation(
        session,
        current_user.id,
        label=payload.label,
        amount=payload.amount,
        due_date=payload.due_date,
        category=payload.category,
        is_fixed=payload.is_fixed,
        is_recurring=payload.is_recurring,
        recurrence_rule=payload.recurrence_rule,
    )
    return ObligationResponse.model_validate(row)


@router.patch("/obligations/{obligation_id}", response_model=ObligationResponse)
async def update_obligation(
    obligation_id: UUID,
    payload: ObligationUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ObligationResponse:
    row = await _service().update_obligation(
        session, current_user.id, obligation_id, **payload.model_dump(exclude_unset=True)
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation not found")
    return ObligationResponse.model_validate(row)


@router.delete("/obligations/{obligation_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_obligation(
    obligation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    deleted = await _service().delete_obligation(session, current_user.id, obligation_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation not found")


# -- Goals --------------------------------------------------------------------


@router.get("/goals", response_model=list[Goal])
async def list_goals(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Goal]:
    return await _service().list_goals(session, current_user.id)


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> GoalResponse:
    row = await _service().add_goal(
        session,
        current_user.id,
        label=payload.label,
        target_amount=payload.target_amount,
        saved_amount=payload.saved_amount,
        target_date=payload.target_date,
        priority=payload.priority,
        is_flexible=payload.is_flexible,
    )
    return GoalResponse.model_validate(row)


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    payload: GoalUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> GoalResponse:
    row = await _service().update_goal(
        session, current_user.id, goal_id, **payload.model_dump(exclude_unset=True)
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return GoalResponse.model_validate(row)


# -- Income sources -------------------------------------------------------------


@router.get("/income-sources", response_model=list[IncomeSourceResponse])
async def list_income_sources(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[IncomeSourceResponse]:
    rows = await _service().list_income_sources(session, current_user.id)
    return [IncomeSourceResponse.model_validate(row) for row in rows]


@router.post(
    "/income-sources", response_model=IncomeSourceResponse, status_code=status.HTTP_201_CREATED
)
async def create_income_source(
    payload: IncomeSourceCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> IncomeSourceResponse:
    row = await _service().add_income_source(
        session,
        current_user.id,
        label=payload.label,
        counterparty=payload.counterparty,
        declared_min=payload.declared_min,
        declared_max=payload.declared_max,
        declared_frequency_days=payload.declared_frequency_days,
    )
    return IncomeSourceResponse.model_validate(row)


# -- Recurring detection ---------------------------------------------------------


@router.get("/recurring", response_model=list[RecurringCandidateResponse])
async def list_recurring(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[RecurringCandidateResponse]:
    service = _service()
    await service.detect_and_store_recurring(session, current_user.id)
    rows = await service.list_recurring_candidates(session, current_user.id)
    return [RecurringCandidateResponse.model_validate(row) for row in rows]


@router.post("/recurring/{candidate_id}/confirm", response_model=ObligationResponse)
async def confirm_recurring(
    candidate_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ObligationResponse:
    obligation = await _service().confirm_recurring(session, current_user.id, candidate_id)
    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recurring candidate not found"
        )
    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="twin.recurring_confirmed",
        resource_type="obligation",
        resource_id=str(obligation.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"recurring_candidate_id": str(candidate_id)},
    )
    return ObligationResponse.model_validate(obligation)
