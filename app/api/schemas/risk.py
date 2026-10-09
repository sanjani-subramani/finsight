"""API request/response DTOs for risk endpoints.

Plain Pydantic models describing HTTP wire shapes for this router only —
distinct from the dataclasses in app.modules.risk, which are the internal
domain representation.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class RuleFindingResponse(BaseModel):
    rule_id: str
    severity: int
    evidence: dict[str, Any]
    human_statement: str


class RiskScoreResponse(BaseModel):
    score: float
    breakdown: dict[str, Any]


class CollisionResponse(BaseModel):
    collision_id: UUID
    condition_ids: list[str]
    joint_probability: float
    individual_probabilities: dict[str, float]
    amplification_factor: float
    severity: str
    urgency: str
    first_impact_date: date | None
    evidence: dict[str, Any]
    human_statement: str


class RiskAssessmentResponse(BaseModel):
    snapshot_id: UUID
    simulation_run_id: UUID
    findings: list[RuleFindingResponse]
    collisions: list[CollisionResponse]
    overall_risk_score: float
    top_collision: CollisionResponse | None
    assessed_at: datetime
    finding_scores: dict[str, RiskScoreResponse]


class ActiveCollisionResponse(BaseModel):
    id: UUID
    condition_ids: list[str]
    joint_probability: float
    individual_probabilities: dict[str, float]
    amplification_factor: float
    severity: str
    urgency: str
    first_impact_date: date | None
    human_statement: str
    detected_at: datetime


class CollisionDetailResponse(ActiveCollisionResponse):
    evidence: dict[str, Any]
    simulation_run_id: UUID | None
    resolved_at: datetime | None
    resolution_reason: str | None


class DismissCollisionRequest(BaseModel):
    reason: str = "not applicable"


class RuleInfoResponse(BaseModel):
    rule_id: str
    name: str
    description: str
    category: str
    base_severity: int
    is_active: bool


class ProposedRuleResponse(BaseModel):
    id: UUID
    name: str
    description: str
    suggested_conditions: list[str]
    support: int
    lift: float
    proposed_threshold: dict[str, Any] | None
    llm_rationale: str | None
    status: str
    approved: bool
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    created_at: datetime
