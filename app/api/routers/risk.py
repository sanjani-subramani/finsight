from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.risk import (
    ActiveCollisionResponse,
    CollisionDetailResponse,
    CollisionResponse,
    DismissCollisionRequest,
    ProposedRuleResponse,
    RiskAssessmentResponse,
    RiskScoreResponse,
    RuleFindingResponse,
    RuleInfoResponse,
)
from app.models.tables import ProposedRuleRecord as ProposedRuleRecordRow
from app.models.tables import User
from app.modules.risk.collision import Collision
from app.modules.risk.discovery import approve_proposed_rule
from app.modules.risk.rules import RULE_REGISTRY
from app.modules.risk.service import RiskAssessment, RiskService
from app.platform.audit import write_audit
from app.platform.database import get_session
from app.platform.deps import get_client_ip, get_current_user, require_admin

router = APIRouter(prefix="/risk", tags=["risk"])


def _service() -> RiskService:
    return RiskService()


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


def _to_collision_response(collision: Collision) -> CollisionResponse:
    return CollisionResponse(
        collision_id=collision.collision_id,
        condition_ids=collision.condition_ids,
        joint_probability=collision.joint_probability,
        individual_probabilities=collision.individual_probabilities,
        amplification_factor=collision.amplification_factor,
        severity=collision.severity,
        urgency=collision.urgency,
        first_impact_date=collision.first_impact_date,
        evidence=collision.evidence,
        human_statement=collision.human_statement,
    )


def _to_assessment_response(assessment: RiskAssessment) -> RiskAssessmentResponse:
    return RiskAssessmentResponse(
        snapshot_id=assessment.snapshot_id,
        simulation_run_id=assessment.simulation_run_id,
        findings=[
            RuleFindingResponse(
                rule_id=f.rule_id, severity=f.severity, evidence=f.evidence, human_statement=f.human_statement
            )
            for f in assessment.findings
        ],
        collisions=[_to_collision_response(c) for c in assessment.collisions],
        overall_risk_score=assessment.overall_risk_score,
        top_collision=_to_collision_response(assessment.top_collision) if assessment.top_collision else None,
        assessed_at=assessment.assessed_at,
        finding_scores={
            rule_id: RiskScoreResponse(score=score.score, breakdown=score.breakdown)
            for rule_id, score in assessment.finding_scores.items()
        },
    )


@router.get("/assessment", response_model=RiskAssessmentResponse)
async def get_assessment(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RiskAssessmentResponse:
    assessment = await _service().assess(session, current_user.id)
    return _to_assessment_response(assessment)


@router.get("/findings", response_model=list[RuleFindingResponse])
async def get_findings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[RuleFindingResponse]:
    assessment = await _service().assess(session, current_user.id)
    return [
        RuleFindingResponse(
            rule_id=f.rule_id, severity=f.severity, evidence=f.evidence, human_statement=f.human_statement
        )
        for f in assessment.findings
    ]


@router.get("/collisions", response_model=list[ActiveCollisionResponse])
async def get_active_collisions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ActiveCollisionResponse]:
    rows = await _service().get_active_collisions(session, current_user.id)
    return [
        ActiveCollisionResponse(
            id=row.id,
            condition_ids=row.condition_ids,
            joint_probability=float(row.joint_probability),
            individual_probabilities=row.individual_probabilities,
            amplification_factor=float(row.amplification_factor),
            severity=row.severity,
            urgency=row.urgency,
            first_impact_date=row.first_impact_date,
            human_statement=row.human_statement,
            detected_at=row.detected_at,
        )
        for row in rows
    ]


@router.get("/collisions/{collision_id}", response_model=CollisionDetailResponse)
async def get_collision_detail(
    collision_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CollisionDetailResponse:
    row = await _service().get_collision(session, current_user.id, collision_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collision not found")
    return CollisionDetailResponse(
        id=row.id,
        condition_ids=row.condition_ids,
        joint_probability=float(row.joint_probability),
        individual_probabilities=row.individual_probabilities,
        amplification_factor=float(row.amplification_factor),
        severity=row.severity,
        urgency=row.urgency,
        first_impact_date=row.first_impact_date,
        human_statement=row.human_statement,
        detected_at=row.detected_at,
        evidence=row.evidence,
        simulation_run_id=row.simulation_run_id,
        resolved_at=row.resolved_at,
        resolution_reason=row.resolution_reason,
    )


@router.post("/collisions/{collision_id}/dismiss", response_model=CollisionDetailResponse)
async def dismiss_collision(
    collision_id: UUID,
    payload: DismissCollisionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CollisionDetailResponse:
    row = await _service().resolve_collision(session, current_user.id, collision_id, payload.reason)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collision not found or already resolved"
        )

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="risk.collision_dismissed",
        resource_type="collision_record",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"reason": payload.reason},
    )

    return CollisionDetailResponse(
        id=row.id,
        condition_ids=row.condition_ids,
        joint_probability=float(row.joint_probability),
        individual_probabilities=row.individual_probabilities,
        amplification_factor=float(row.amplification_factor),
        severity=row.severity,
        urgency=row.urgency,
        first_impact_date=row.first_impact_date,
        human_statement=row.human_statement,
        detected_at=row.detected_at,
        evidence=row.evidence,
        simulation_run_id=row.simulation_run_id,
        resolved_at=row.resolved_at,
        resolution_reason=row.resolution_reason,
    )


@router.get("/rules", response_model=list[RuleInfoResponse])
async def list_rules(current_user: User = Depends(get_current_user)) -> list[RuleInfoResponse]:
    return [
        RuleInfoResponse(
            rule_id=rule.rule_id,
            name=rule.name,
            description=rule.description,
            category=rule.category,
            base_severity=rule.base_severity,
            is_active=rule.is_active,
        )
        for rule in RULE_REGISTRY.values()
    ]


@router.get("/proposed-rules", response_model=list[ProposedRuleResponse])
async def list_proposed_rules(
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[ProposedRuleResponse]:
    result = await session.execute(
        select(ProposedRuleRecordRow)
        .where(ProposedRuleRecordRow.status == "pending_review")
        .order_by(ProposedRuleRecordRow.created_at.desc())
    )
    rows = list(result.scalars())
    return [
        ProposedRuleResponse(
            id=row.id,
            name=row.name,
            description=row.description,
            suggested_conditions=row.suggested_conditions,
            support=row.support,
            lift=float(row.lift),
            proposed_threshold=row.proposed_threshold,
            llm_rationale=row.llm_rationale,
            status=row.status,
            approved=row.approved,
            reviewed_by=row.reviewed_by,
            reviewed_at=row.reviewed_at,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.post("/proposed-rules/{proposed_rule_id}/approve", response_model=ProposedRuleResponse)
async def approve_proposed_rule_endpoint(
    proposed_rule_id: UUID,
    request: Request,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> ProposedRuleResponse:
    row = await approve_proposed_rule(session, proposed_rule_id, current_user.id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proposed rule not found or already reviewed"
        )

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="risk.proposed_rule_approved",
        resource_type="proposed_rule_record",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
    )

    return ProposedRuleResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        suggested_conditions=row.suggested_conditions,
        support=row.support,
        lift=float(row.lift),
        proposed_threshold=row.proposed_threshold,
        llm_rationale=row.llm_rationale,
        status=row.status,
        approved=row.approved,
        reviewed_by=row.reviewed_by,
        reviewed_at=row.reviewed_at,
        created_at=row.created_at,
    )
