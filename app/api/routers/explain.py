from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.explain import ExplainHealthResponse, NarrationResponse, TraceStepNarrationResponse
from app.models.tables import User
from app.modules.explain.narrator import NarrationResult
from app.modules.explain.service import ExplainService
from app.platform.config import get_settings
from app.platform.database import get_session
from app.platform.deps import get_current_user
from app.platform.llm_client import call_groq_json

router = APIRouter(prefix="/explain", tags=["explain"])


def _to_response(result: NarrationResult) -> NarrationResponse:
    return NarrationResponse(
        text=result.text,
        source=result.source,
        validation_passed=result.validation_passed,
        violations=result.violations,
        cached=result.cached,
        duration_ms=result.duration_ms,
    )


@router.get("/health", response_model=ExplainHealthResponse)
async def explain_health(current_user: User = Depends(get_current_user)) -> ExplainHealthResponse:
    settings = get_settings()
    configured = bool(settings.GROQ_API_KEY)
    if not configured:
        return ExplainHealthResponse(llm_configured=False, llm_reachable=None)

    content = await call_groq_json(
        "Respond with valid JSON and nothing else.",
        '{"ping": "pong"}',
        settings,
        timeout_seconds=5.0,
        retries=0,
    )
    return ExplainHealthResponse(llm_configured=True, llm_reachable=content is not None)


@router.get("/snapshot", response_model=NarrationResponse)
async def explain_snapshot(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> NarrationResponse:
    result = await ExplainService().explain_snapshot(session, current_user.id)
    return _to_response(result)


@router.get("/intervention/{intervention_id}", response_model=NarrationResponse)
async def explain_intervention(
    intervention_id: UUID,
    style: str = Query("concise", pattern="^(concise|detailed)$"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> NarrationResponse:
    result = await ExplainService().explain_intervention(session, current_user.id, intervention_id, style=style)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found")
    return _to_response(result)


@router.get("/intervention/{intervention_id}/steps", response_model=list[TraceStepNarrationResponse])
async def explain_intervention_steps(
    intervention_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[TraceStepNarrationResponse]:
    explain_service = ExplainService()
    trace = await explain_service.get_trace_steps(session, current_user.id, intervention_id)
    if trace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found")

    responses: list[TraceStepNarrationResponse] = []
    for step in trace:
        result = await explain_service.explain_trace_step(session, current_user.id, intervention_id, step.order)
        if result is None:
            continue
        responses.append(TraceStepNarrationResponse(order=step.order, stage=step.stage, narration=_to_response(result)))
    return responses
