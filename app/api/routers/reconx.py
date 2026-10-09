from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.reconx import (
    ReconResultResponse,
    ReconRunDetailResponse,
    ReconRunRequest,
    ReconRunSummaryResponse,
    ResolveRequest,
)
from app.models.tables import User
from app.modules.org.reconx.ingest import ingest_bank, ingest_gateway, ingest_internal
from app.modules.org.reconx.matcher import MatchConfig
from app.modules.org.reconx.service import ReconResultDetail, ReconRunDetail, ReconRunSummary, ReconService
from app.platform.database import get_session
from app.platform.deps import require_roles

router = APIRouter(prefix="/org/{org_id}/recon", tags=["reconx"])

_READ_ROLES = ("owner", "ops_engineer", "recon_analyst", "viewer")
_WRITE_ROLES = ("owner", "ops_engineer", "recon_analyst")


def _to_summary_response(summary: ReconRunSummary) -> ReconRunSummaryResponse:
    return ReconRunSummaryResponse(
        run_id=summary.run_id,
        period_start=summary.period_start,
        period_end=summary.period_end,
        total_records=summary.total_records,
        matched=summary.matched,
        missing=summary.missing,
        duplicates=summary.duplicates,
        amount_mismatches=summary.amount_mismatches,
        timing_differences=summary.timing_differences,
        unresolved=summary.unresolved,
        status=summary.status,
        duration_ms=summary.duration_ms,
        created_at=summary.created_at,
    )


def _to_result_response(r: ReconResultDetail) -> ReconResultResponse:
    return ReconResultResponse(
        result_id=r.result_id,
        run_id=r.run_id,
        transaction_ref=r.transaction_ref,
        status=r.status.value,
        internal_amount=r.internal_amount,
        gateway_amount=r.gateway_amount,
        bank_amount=r.bank_amount,
        probable_cause=r.probable_cause,
        cause_confidence=r.cause_confidence,
        evidence=r.evidence,
        resolved=r.resolved,
        resolved_by=r.resolved_by,
        resolution_note=r.resolution_note,
    )


def _to_detail_response(detail: ReconRunDetail) -> ReconRunDetailResponse:
    return ReconRunDetailResponse(
        summary=_to_summary_response(detail.summary),
        results=[_to_result_response(r) for r in detail.results],
    )


@router.post("/runs", response_model=ReconRunSummaryResponse)
async def create_run(
    org_id: UUID,
    payload: ReconRunRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> ReconRunSummaryResponse:
    internal = await ingest_internal(session, org_id, payload.internal)
    gateway = await ingest_gateway(session, org_id, payload.gateway)
    bank = await ingest_bank(session, org_id, payload.bank)

    config = MatchConfig(
        amount_tolerance_pct=payload.amount_tolerance_pct,
        amount_tolerance_abs=payload.amount_tolerance_abs,
        time_window_hours=payload.time_window_hours,
        ref_similarity_threshold=payload.ref_similarity_threshold,
    )

    run_result = await ReconService().create_run(
        session, org_id, internal, gateway, bank, config=config, started_by=current_user.id
    )
    detail = await ReconService().get_run(session, org_id, run_result.run_id)
    assert detail is not None, "just-created run must be readable back"
    return _to_summary_response(detail.summary)


@router.get("/runs", response_model=list[ReconRunSummaryResponse])
async def list_runs(
    org_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[ReconRunSummaryResponse]:
    runs = await ReconService().get_runs(session, org_id)
    return [_to_summary_response(r) for r in runs]


@router.get("/runs/{run_id}", response_model=ReconRunDetailResponse)
async def get_run(
    org_id: UUID,
    run_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> ReconRunDetailResponse:
    detail = await ReconService().get_run(session, org_id, run_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reconciliation run not found")
    return _to_detail_response(detail)


@router.get("/runs/{run_id}/mismatches", response_model=list[ReconResultResponse])
async def get_mismatches(
    org_id: UUID,
    run_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[ReconResultResponse]:
    results = await ReconService().get_mismatches(session, org_id, run_id)
    if results is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reconciliation run not found")
    return [_to_result_response(r) for r in results]


@router.post("/runs/{run_id}/results/{result_id}/resolve", response_model=ReconResultResponse)
async def resolve_result(
    org_id: UUID,
    run_id: UUID,
    result_id: UUID,
    payload: ResolveRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> ReconResultResponse:
    resolved = await ReconService().resolve_manually(
        session, org_id, result_id, payload.resolution_note, current_user.id
    )
    if resolved is None or resolved.run_id != run_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reconciliation result not found")
    return _to_result_response(resolved)


@router.get("/runs/{run_id}/export")
async def export_run(
    org_id: UUID,
    run_id: UUID,
    format: str = Query("csv"),
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> Response:
    try:
        content = await ReconService().export_results(session, org_id, run_id, format=format)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(content=content, media_type="text/csv")
