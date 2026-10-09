from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.regimpact import (
    CreateProductRequest,
    CreateWorkflowRequest,
    ImpactReportResponse,
    IngestRegulationRequest,
    ProductResponse,
    RegulationResponse,
    RegulatoryRuleResponse,
    ReviewRuleRequest,
    WorkflowResponse,
)
from app.models.tables import ImpactReport as ImpactReportRow
from app.models.tables import Product as ProductRow
from app.models.tables import Regulation as RegulationRow
from app.models.tables import RegulatoryRule as RegulatoryRuleRow
from app.models.tables import User
from app.models.tables import Workflow as WorkflowRow
from app.modules.org.regimpact.impact import ImpactReportResult
from app.modules.org.regimpact.service import RegImpactService, RuleNotConfirmedError
from app.platform.database import get_session
from app.platform.deps import require_roles

router = APIRouter(prefix="/org/{org_id}/regimpact", tags=["regimpact"])

_READ_ROLES = ("owner", "ops_engineer", "recon_analyst", "viewer")
_WRITE_ROLES = ("owner", "ops_engineer")
# Reviewing (confirming/rejecting) an extracted rule is the human
# accountability checkpoint before it can drive any analysis -- gated to
# the same elevated roles as writing to the graph, per the spec.
_REVIEW_ROLES = ("owner", "ops_engineer")


def _to_product_response(row: ProductRow) -> ProductResponse:
    return ProductResponse(id=row.id, name=row.name, description=row.description, category=row.category)


def _to_workflow_response(row: WorkflowRow) -> WorkflowResponse:
    return WorkflowResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        uses_service_node_ids=[str(i) for i in (row.uses_service_node_ids or [])],
        uses_product_ids=[str(i) for i in (row.uses_product_ids or [])],
    )


def _to_regulation_response(row: RegulationRow) -> RegulationResponse:
    return RegulationResponse(
        id=row.id,
        title=row.title,
        source_url=row.source_url,
        effective_date=row.effective_date,
        ingested_at=row.ingested_at,
    )


def _to_rule_response(row: RegulatoryRuleRow) -> RegulatoryRuleResponse:
    return RegulatoryRuleResponse(
        id=row.id,
        regulation_id=row.regulation_id,
        rule_text=row.rule_text,
        trigger_condition=row.trigger_condition,
        threshold_json=row.threshold_json,
        required_action=row.required_action,
        deadline_days=row.deadline_days,
        applies_to_product_categories=list(row.applies_to_product_categories or []),
        extraction_confidence=row.extraction_confidence,
        ambiguities=list(row.ambiguities or []),
        status=row.status,
        reviewed_by=row.reviewed_by,
        reviewed_at=row.reviewed_at,
        review_note=row.review_note,
    )


def _to_report_response(result: ImpactReportResult) -> ImpactReportResponse:
    return ImpactReportResponse(
        id=result.id,
        regulation_id=result.regulation_id,
        rule_id=result.rule_id,
        affected_products=result.affected_products,
        affected_workflows=result.affected_workflows,
        affected_service_nodes=result.affected_service_nodes,
        estimated_transactions=result.estimated_transactions,
        required_changes=result.required_changes,
        generated_at=result.generated_at,
    )


def _row_to_report_response(row: ImpactReportRow) -> ImpactReportResponse:
    return ImpactReportResponse(
        id=row.id,
        regulation_id=row.regulation_id,
        rule_id=row.rule_id,
        affected_products=list(row.affected_products or []),
        affected_workflows=list(row.affected_workflows or []),
        affected_service_nodes=list(row.affected_service_nodes or []),
        estimated_transactions=row.estimated_transactions,
        required_changes=list(row.required_changes or []),
        generated_at=row.generated_at,
    )


@router.post("/products", response_model=ProductResponse)
async def create_product(
    org_id: UUID,
    payload: CreateProductRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    row = await RegImpactService().create_product(session, org_id, payload.name, payload.description, payload.category)
    return _to_product_response(row)


@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    org_id: UUID,
    payload: CreateWorkflowRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> WorkflowResponse:
    row = await RegImpactService().create_workflow(
        session,
        org_id,
        payload.name,
        payload.description,
        payload.uses_service_node_ids,
        payload.uses_product_ids,
    )
    return _to_workflow_response(row)


@router.post("/regulations", response_model=RegulationResponse)
async def ingest_regulation(
    org_id: UUID,
    payload: IngestRegulationRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> RegulationResponse:
    regulation = await RegImpactService().ingest_regulation(
        session,
        org_id,
        payload.title,
        payload.source_text,
        payload.source_url,
        payload.effective_date,
        current_user.id,
    )
    return _to_regulation_response(regulation)


@router.get("/regulations/{regulation_id}/rules", response_model=list[RegulatoryRuleResponse])
async def get_regulation_rules(
    org_id: UUID,
    regulation_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[RegulatoryRuleResponse]:
    result = await session.execute(
        select(RegulatoryRuleRow).where(
            RegulatoryRuleRow.org_id == org_id, RegulatoryRuleRow.regulation_id == regulation_id
        )
    )
    return [_to_rule_response(r) for r in result.scalars()]


@router.get("/rules/pending", response_model=list[RegulatoryRuleResponse])
async def get_pending_rules(
    org_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[RegulatoryRuleResponse]:
    # Org-wide, not scoped to one regulation -- the dashboard's Overview
    # page (Step 18) needs a single pending-review count across every
    # regulation ingested for this org, which GET .../regulations/{id}/rules
    # can't give without already knowing every regulation_id up front.
    rules = await RegImpactService().get_pending_review(session, org_id)
    return [_to_rule_response(r) for r in rules]


@router.get("/rules/confirmed", response_model=list[RegulatoryRuleResponse])
async def get_confirmed_rules(
    org_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[RegulatoryRuleResponse]:
    rules = await RegImpactService().get_confirmed_rules(session, org_id)
    return [_to_rule_response(r) for r in rules]


@router.post("/rules/{rule_id}/review", response_model=RegulatoryRuleResponse)
async def review_rule(
    org_id: UUID,
    rule_id: UUID,
    payload: ReviewRuleRequest,
    current_user: User = Depends(require_roles(*_REVIEW_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> RegulatoryRuleResponse:
    rule = await RegImpactService().review_rule(
        session, org_id, rule_id, payload.decision, current_user.id, payload.note
    )
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulatory rule not found")
    return _to_rule_response(rule)


@router.post("/rules/{rule_id}/analyze", response_model=ImpactReportResponse)
async def analyze_rule(
    org_id: UUID,
    rule_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> ImpactReportResponse:
    try:
        result = await RegImpactService().run_impact_analysis(session, org_id, rule_id)
    except RuleNotConfirmedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_report_response(result)


@router.get("/reports", response_model=list[ImpactReportResponse])
async def list_reports(
    org_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[ImpactReportResponse]:
    rows = await RegImpactService().get_impact_history(session, org_id)
    return [_row_to_report_response(r) for r in rows]


@router.get("/reports/{report_id}", response_model=ImpactReportResponse)
async def get_report(
    org_id: UUID,
    report_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> ImpactReportResponse:
    result = await session.execute(
        select(ImpactReportRow).where(ImpactReportRow.id == report_id, ImpactReportRow.org_id == org_id)
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Impact report not found")
    return _row_to_report_response(row)
