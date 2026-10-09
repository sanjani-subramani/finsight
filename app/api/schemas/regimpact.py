"""API request/response DTOs for RegImpact (Step 17).

Plain Pydantic models, not the frozen event/state contracts in
app/contracts — these describe HTTP wire shapes for this router only.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateProductRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = Field(min_length=1, max_length=128)


class CreateWorkflowRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    uses_service_node_ids: list[UUID] = Field(default_factory=list)
    uses_product_ids: list[UUID] = Field(default_factory=list)


class IngestRegulationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    source_text: str = Field(min_length=1)
    source_url: str | None = None
    effective_date: date | None = None


class ReviewRuleRequest(BaseModel):
    decision: Literal["confirmed", "rejected"]
    note: str | None = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    category: str


class WorkflowResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    uses_service_node_ids: list[str]
    uses_product_ids: list[str]


class RegulationResponse(BaseModel):
    id: UUID
    title: str
    source_url: str | None
    effective_date: date | None
    ingested_at: datetime


class RegulatoryRuleResponse(BaseModel):
    id: UUID
    regulation_id: UUID
    rule_text: str
    trigger_condition: str
    threshold_json: dict[str, Any] | None
    required_action: str
    deadline_days: int | None
    applies_to_product_categories: list[str]
    extraction_confidence: float | None
    ambiguities: list[str]
    status: str
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    review_note: str | None


class ImpactReportResponse(BaseModel):
    id: UUID
    regulation_id: UUID
    rule_id: UUID
    affected_products: list[str]
    affected_workflows: list[str]
    affected_service_nodes: list[str]
    estimated_transactions: int
    required_changes: list[str]
    generated_at: datetime
