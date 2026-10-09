from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.decision import (
    ActedRequest,
    InterventionDetailResponse,
    InterventionSummaryResponse,
    PrecisionReportResponse,
    SeverityPrecisionResponse,
    TraceStepResponse,
)
from app.models.tables import Intervention, User
from app.modules.decision.service import DecisionService
from app.modules.decision.shadow import compute_precision
from app.platform.audit import write_audit
from app.platform.database import get_session
from app.platform.deps import get_client_ip, get_current_user, require_admin

router = APIRouter(prefix="/decisions", tags=["decisions"])

DEFAULT_PRECISION_LOOKBACK_DAYS = 30
DEFAULT_SHADOW_LIST_LIMIT = 50


def _service() -> DecisionService:
    return DecisionService()


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


def _to_detail_response(row: Intervention) -> InterventionDetailResponse:
    return InterventionDetailResponse.model_validate(row)


@router.get("/precision", response_model=PrecisionReportResponse)
async def get_precision(
    since: datetime | None = Query(None),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> PrecisionReportResponse:
    resolved_since = since or (datetime.now(timezone.utc) - timedelta(days=DEFAULT_PRECISION_LOOKBACK_DAYS))
    report = await compute_precision(session, resolved_since)
    return PrecisionReportResponse(
        since=report.since,
        by_severity={
            severity: SeverityPrecisionResponse(
                severity=p.severity,
                total_fired=p.total_fired,
                total_checked=p.total_checked,
                materialized=p.materialized,
                precision=p.precision,
                false_alarm_rate=p.false_alarm_rate,
            )
            for severity, p in report.by_severity.items()
        },
        confidence_ceiling_total=report.confidence_ceiling_total,
        confidence_ceiling_checked=report.confidence_ceiling_checked,
        confidence_ceiling_saves=report.confidence_ceiling_saves,
        confidence_ceiling_save_rate=report.confidence_ceiling_save_rate,
    )


@router.get("/shadow", response_model=list[InterventionSummaryResponse])
async def list_shadow_decisions(
    limit: int = Query(DEFAULT_SHADOW_LIST_LIMIT, ge=1, le=200),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[InterventionSummaryResponse]:
    result = await session.execute(
        select(Intervention)
        .where(Intervention.shadow_mode.is_(True))
        .order_by(Intervention.created_at.desc())
        .limit(limit)
    )
    rows = list(result.scalars())
    return [InterventionSummaryResponse.model_validate(row) for row in rows]


@router.get("", response_model=list[InterventionSummaryResponse])
async def list_decisions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[InterventionSummaryResponse]:
    rows = await _service().get_interventions(session, current_user.id, include_shadow=False)
    return [InterventionSummaryResponse.model_validate(row) for row in rows]


@router.get("/{intervention_id}", response_model=InterventionDetailResponse)
async def get_decision(
    intervention_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> InterventionDetailResponse:
    row = await _service().get_intervention(session, current_user.id, intervention_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found")
    return _to_detail_response(row)


@router.get("/{intervention_id}/trace", response_model=list[TraceStepResponse])
async def get_decision_trace(
    intervention_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[TraceStepResponse]:
    row = await _service().get_intervention(session, current_user.id, intervention_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found")
    return [TraceStepResponse.model_validate(step) for step in (row.decision_trace or [])]


@router.post("/{intervention_id}/acknowledge", response_model=InterventionDetailResponse)
async def acknowledge_decision(
    intervention_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> InterventionDetailResponse:
    row = await _service().acknowledge(session, current_user.id, intervention_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found")

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="decision.acknowledged",
        resource_type="intervention",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
    )
    return _to_detail_response(row)


@router.post("/{intervention_id}/acted", response_model=InterventionDetailResponse)
async def report_acted(
    intervention_id: UUID,
    payload: ActedRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> InterventionDetailResponse:
    row = await _service().mark_acted(session, current_user.id, intervention_id, payload.acted)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found")

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="decision.acted",
        resource_type="intervention",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"acted": payload.acted},
    )
    return _to_detail_response(row)
