from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.fingraph import (
    AddEdgeRequest,
    AddNodeRequest,
    BulkImportRequest,
    CentralityResponse,
    GraphEdgeResponse,
    GraphNodeResponse,
    GraphResponse,
    ImpactResultResponse,
    SimulateMultiRequest,
    SimulateRequest,
    SimulationHistoryResponse,
)
from app.contracts.events import ImpactResult
from app.models.tables import FailureSimulation as FailureSimulationRow
from app.models.tables import User
from app.modules.org.fingraph.graph_builder import validate_and_build
from app.modules.org.fingraph.graph_management import CycleError, add_edge, add_node, bulk_import
from app.modules.org.fingraph.impact import CentralityScore
from app.modules.org.fingraph.service import FinGraphService
from app.platform.database import get_session
from app.platform.deps import require_roles

router = APIRouter(prefix="/org/{org_id}/fingraph", tags=["fingraph"])

_READ_ROLES = ("owner", "ops_engineer", "recon_analyst", "viewer")
_WRITE_ROLES = ("owner", "ops_engineer")


def _to_impact_response(result: ImpactResult) -> ImpactResultResponse:
    return ImpactResultResponse(
        impact_id=result.impact_id,
        failed_node=result.failed_node,
        affected_services=result.affected_services,
        affected_workflows=result.affected_workflows,
        estimated_transactions=result.estimated_transactions,
        critical_paths=result.critical_paths,
        alternative_providers=result.alternative_providers,
    )


def _to_centrality_response(score: CentralityScore) -> CentralityResponse:
    return CentralityResponse(
        node_name=score.node_name,
        betweenness=score.betweenness,
        is_critical=score.is_critical,
        node_type=score.node_type,
    )


def _to_history_response(row: FailureSimulationRow) -> SimulationHistoryResponse:
    return SimulationHistoryResponse(
        id=row.id,
        failed_node=row.failed_node,
        duration_hours=row.duration_hours,
        result=row.result,
        created_at=row.created_at,
    )


@router.post("/nodes", response_model=GraphNodeResponse)
async def create_node(
    org_id: UUID,
    payload: AddNodeRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> GraphNodeResponse:
    row = await add_node(
        session,
        org_id,
        payload.name,
        payload.node_type,
        is_critical=payload.is_critical,
        alternative_for=payload.alternative_for,
        metadata=payload.metadata,
    )
    return GraphNodeResponse(
        id=row.id,
        name=row.name,
        node_type=row.node_type,
        is_critical=row.is_critical,
        alternative_for=row.alternative_for,
        metadata=row.metadata_json or {},
    )


@router.post("/edges", response_model=GraphEdgeResponse)
async def create_edge(
    org_id: UUID,
    payload: AddEdgeRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> GraphEdgeResponse:
    try:
        row = await add_edge(
            session, org_id, payload.from_name, payload.to_name, edge_type=payload.edge_type, weight=payload.weight
        )
    except CycleError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return GraphEdgeResponse(
        from_name=payload.from_name, to_name=payload.to_name, edge_type=row.edge_type, weight=float(row.weight or 1.0)
    )


@router.post("/bulk-import", response_model=GraphResponse)
async def bulk_import_graph(
    org_id: UUID,
    payload: BulkImportRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> GraphResponse:
    try:
        await bulk_import(
            session,
            org_id,
            [n.model_dump() for n in payload.nodes],
            [e.model_dump() for e in payload.edges],
        )
    except CycleError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return await _get_graph_response(session, org_id)


async def _get_graph_response(session: AsyncSession, org_id: UUID) -> GraphResponse:
    build_result = await validate_and_build(session, org_id)
    graph = build_result.graph
    nodes = [
        GraphNodeResponse(
            id=graph.nodes[n]["node_id"],
            name=n,
            node_type=graph.nodes[n]["node_type"],
            is_critical=graph.nodes[n]["is_critical"],
            alternative_for=graph.nodes[n]["alternative_for"],
            metadata=graph.nodes[n]["metadata"],
        )
        for n in graph.nodes
    ]
    edges = [
        GraphEdgeResponse(from_name=u, to_name=v, edge_type=data["edge_type"], weight=data["weight"])
        for u, v, data in graph.edges(data=True)
    ]
    return GraphResponse(nodes=nodes, edges=edges, cycle_warnings=build_result.warnings)


@router.get("/graph", response_model=GraphResponse)
async def get_graph(
    org_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> GraphResponse:
    return await _get_graph_response(session, org_id)


@router.get("/critical-nodes", response_model=list[CentralityResponse])
async def get_critical_nodes(
    org_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[CentralityResponse]:
    scores = await FinGraphService().get_critical_nodes(session, org_id)
    return [_to_centrality_response(s) for s in scores]


@router.post("/simulate", response_model=ImpactResultResponse)
async def simulate(
    org_id: UUID,
    payload: SimulateRequest,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> ImpactResultResponse:
    try:
        result = await FinGraphService().simulate_failure(session, org_id, payload.node_name, payload.duration_hours)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_impact_response(result)


@router.post("/simulate-multi", response_model=ImpactResultResponse)
async def simulate_multi(
    org_id: UUID,
    payload: SimulateMultiRequest,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> ImpactResultResponse:
    try:
        result = await FinGraphService().simulate_multi_failure(
            session, org_id, payload.node_names, payload.duration_hours
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_impact_response(result)


@router.get("/history", response_model=list[SimulationHistoryResponse])
async def get_history(
    org_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[SimulationHistoryResponse]:
    rows = await FinGraphService().get_simulation_history(session, org_id)
    return [_to_history_response(r) for r in rows]
