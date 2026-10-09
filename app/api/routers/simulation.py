from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.simulation import (
    PurchaseRequest,
    PurchaseVerdictResponse,
    ReplayResponse,
    RunResponse,
    SensitivityFactorResponse,
    SimulationRunDetail,
    SimulationRunSummary,
)
from app.models.tables import User
from app.modules.simulation.service import SimulationOutcome, SimulationService
from app.platform.database import get_session
from app.platform.deps import get_current_user

router = APIRouter(prefix="/simulation", tags=["simulation"])

DEFAULT_HORIZON_DAYS = 90
DEFAULT_SCENARIOS = 1000


def _service() -> SimulationService:
    return SimulationService()


def _to_run_response(outcome: SimulationOutcome) -> RunResponse:
    return RunResponse(
        run_id=outcome.run_id,
        scenarios_run=outcome.result.scenarios_run,
        horizon_days=max(outcome.result.shortfall_probability_by_horizon),
        seed=outcome.result.seed,
        shortfall_probability_by_horizon=outcome.result.shortfall_probability_by_horizon,
        min_balance_p5=outcome.result.min_balance_p5,
        min_balance_p50=outcome.result.min_balance_p50,
        time_to_danger_days=outcome.result.time_to_danger_days,
        safe_to_spend=outcome.safe_to_spend.amount,
        duration_ms=outcome.result.duration_ms,
        from_cache=outcome.from_cache,
        balance_matrix_summary=outcome.result.balance_matrix_summary,
        sensitivity=[
            SensitivityFactorResponse(
                name=f.name,
                description=f.description,
                prob_before=f.prob_before,
                prob_after=f.prob_after,
                delta=f.delta,
                actionable=f.actionable,
            )
            for f in outcome.sensitivity
        ],
    )


@router.get("/run", response_model=RunResponse)
async def run_simulation(
    horizon: int = Query(DEFAULT_HORIZON_DAYS, ge=7, le=365),
    scenarios: int = Query(DEFAULT_SCENARIOS, ge=100, le=10_000),
    force_refresh: bool = Query(False),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RunResponse:
    outcome = await _service().run(
        session, current_user.id, horizon_days=horizon, scenarios=scenarios, force_refresh=force_refresh
    )
    return _to_run_response(outcome)


@router.post("/afford", response_model=PurchaseVerdictResponse)
async def evaluate_purchase(
    payload: PurchaseRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PurchaseVerdictResponse:
    verdict = await _service().evaluate_purchase(
        session, current_user.id, payload.amount, payload.description
    )
    return PurchaseVerdictResponse(
        affordable=verdict.affordable,
        prob_before=verdict.prob_before,
        prob_after=verdict.prob_after,
        wait_days_recommended=verdict.wait_days_recommended,
        reasoning_values=verdict.reasoning_values,
    )


@router.get("/sensitivity", response_model=list[SensitivityFactorResponse])
async def get_sensitivity(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[SensitivityFactorResponse]:
    outcome = await _service().run(session, current_user.id)
    return [
        SensitivityFactorResponse(
            name=f.name,
            description=f.description,
            prob_before=f.prob_before,
            prob_after=f.prob_after,
            delta=f.delta,
            actionable=f.actionable,
        )
        for f in outcome.sensitivity
    ]


@router.get("/runs", response_model=list[SimulationRunSummary])
async def list_runs(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[SimulationRunSummary]:
    rows = await _service().list_runs(session, current_user.id, limit=limit)
    return [SimulationRunSummary.model_validate(row) for row in rows]


@router.get("/runs/{run_id}", response_model=SimulationRunDetail)
async def get_run(
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SimulationRunDetail:
    row = await _service().get_run(session, current_user.id, run_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation run not found")
    return SimulationRunDetail.model_validate(row)


@router.post("/runs/{run_id}/replay", response_model=ReplayResponse)
async def replay_run(
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ReplayResponse:
    service = _service()
    owned = await service.get_run(session, current_user.id, run_id)
    if owned is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Simulation run not found")

    replay = await service.replay_run(session, run_id)
    if replay is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Run has no stored inputs to replay"
        )

    return ReplayResponse(
        run_id=replay.run_id,
        matches=replay.matches,
        original_probability=replay.original_probability,
        replayed_probability=replay.replayed_probability,
    )
