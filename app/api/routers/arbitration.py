from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.arbitration import (
    AcceptActionResponse,
    AllocationResponse,
    AlternativeResponse,
    ClaimResponse,
    SimulateProposalRequest,
    SimulateProposalResponse,
)
from app.contracts.events import FinancialStateSnapshot
from app.models.tables import User
from app.modules.decision.arbitration import ArbitrationResult, arbitrate, verify_allocation
from app.modules.decision.service import DecisionService
from app.modules.simulation.engine import SimulationResult
from app.platform.audit import write_audit
from app.platform.database import get_session
from app.platform.deps import get_client_ip, get_current_user

router = APIRouter(prefix="/arbitration", tags=["arbitration"])


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


async def _current_snapshot_and_sim(
    session: AsyncSession, user_id: UUID
) -> tuple[FinancialStateSnapshot, SimulationResult]:
    # Deferred imports: same reasoning as everywhere else this pairing
    # shows up (e.g. app.modules.risk.service.RiskService.assess) -- twin
    # and simulation sit below decision in the dependency chain, but
    # importing either at module load time here risks a cycle.
    from app.modules.simulation.service import SimulationService
    from app.modules.twin.service import TwinService

    snapshot = await TwinService().get_base_snapshot(session, user_id)
    sim_outcome = await SimulationService().run(session, user_id)
    return snapshot, sim_outcome.result


def _to_allocation_response(result: ArbitrationResult) -> AllocationResponse:
    return AllocationResponse(
        claims=[
            ClaimResponse(
                claim_id=claim.claim_id,
                label=claim.label,
                tier=int(claim.tier),
                amount=claim.amount,
                due_date=claim.due_date,
                source=claim.source,
            )
            for claim in result.claims
        ],
        allocations=result.allocations,
        reductions=result.reductions,
        unfunded=result.unfunded,
        prob_before=result.prob_before,
        prob_after=result.prob_after,
        trade_off_statement=result.trade_off_statement,
    )


@router.get("/current", response_model=AllocationResponse)
async def get_current_allocation(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AllocationResponse:
    snapshot, sim_result = await _current_snapshot_and_sim(session, current_user.id)
    result = await arbitrate(session, current_user.id, snapshot, sim_result)
    return _to_allocation_response(result)


@router.get("/alternatives", response_model=list[AlternativeResponse])
async def get_alternatives(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[AlternativeResponse]:
    snapshot, sim_result = await _current_snapshot_and_sim(session, current_user.id)
    result = await arbitrate(session, current_user.id, snapshot, sim_result)
    return [
        AlternativeResponse(
            profile=alt.profile, allocations=alt.allocations, reductions=alt.reductions, prob_after=alt.prob_after
        )
        for alt in result.alternatives
    ]


@router.post("/simulate", response_model=SimulateProposalResponse)
async def simulate_proposal(
    payload: SimulateProposalRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SimulateProposalResponse:
    snapshot, sim_result = await _current_snapshot_and_sim(session, current_user.id)
    horizon = max(sim_result.shortfall_probability_by_horizon)
    prob_before = sim_result.shortfall_probability_by_horizon[horizon]
    freed = sum(payload.reductions.values(), Decimal("0"))
    prob_after = await verify_allocation(session, snapshot, horizon, sim_result.seed, sim_result.scenarios_run, freed)
    return SimulateProposalResponse(prob_before=prob_before, prob_after=prob_after, improved=prob_after < prob_before)


@router.post("/accept/{action_id}", response_model=AcceptActionResponse)
async def accept_action(
    action_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AcceptActionResponse:
    # action_id is "<intervention_id>:<index into recommended_actions>" --
    # RecommendedAction (a frozen contract) carries no id of its own, so
    # this is the only stable way to address one specific action.
    try:
        intervention_id_str, index_str = action_id.rsplit(":", 1)
        intervention_id = UUID(intervention_id_str)
        action_index = int(index_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="action_id must be '<intervention_id>:<action_index>'",
        ) from exc

    row = await DecisionService().get_intervention(session, current_user.id, intervention_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found")

    actions = row.recommended_actions or []
    if action_index < 0 or action_index >= len(actions):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommended action not found")
    action = actions[action_index]

    # Recording the acceptance (and auditing it) is fully implemented.
    # Automatically adjusting the underlying obligation/goal is NOT: a
    # RecommendedAction carries no reference back to the specific
    # Obligation/Goal row it came from (the frozen contract has no such
    # field), so there is nothing reliable to apply the change to here
    # without guessing. That mapping would need a new field or a
    # dedicated table — out of scope for this step.
    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="arbitration.action_accepted",
        resource_type="intervention",
        resource_id=str(intervention_id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"action_index": action_index, "action_type": action.get("action_type")},
    )

    return AcceptActionResponse(
        intervention_id=intervention_id,
        action_index=action_index,
        action_type=action.get("action_type", ""),
        accepted=True,
    )
