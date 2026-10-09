"""API request/response DTOs for FinGraph (Step 16).

Plain Pydantic models, not the frozen event/state contracts in
app/contracts — these describe HTTP wire shapes for this router only.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AddNodeRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    node_type: str = Field(min_length=1, max_length=64)
    is_critical: bool = False
    alternative_for: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AddEdgeRequest(BaseModel):
    from_name: str
    to_name: str
    edge_type: str = "depends_on"
    weight: float = 1.0


class BulkNodeSpec(BaseModel):
    name: str
    node_type: str
    is_critical: bool = False
    alternative_for: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BulkEdgeSpec(BaseModel):
    from_name: str
    to_name: str
    edge_type: str = "depends_on"
    weight: float = 1.0


class BulkImportRequest(BaseModel):
    nodes: list[BulkNodeSpec] = Field(default_factory=list)
    edges: list[BulkEdgeSpec] = Field(default_factory=list)


class SimulateRequest(BaseModel):
    node_name: str
    duration_hours: float | None = None


class SimulateMultiRequest(BaseModel):
    node_names: list[str] = Field(min_length=1)
    duration_hours: float | None = None


class GraphNodeResponse(BaseModel):
    id: UUID
    name: str
    node_type: str
    is_critical: bool
    alternative_for: UUID | None
    metadata: dict[str, Any]


class GraphEdgeResponse(BaseModel):
    from_name: str
    to_name: str
    edge_type: str
    weight: float


class GraphResponse(BaseModel):
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]
    cycle_warnings: list[str]


class CentralityResponse(BaseModel):
    node_name: str
    betweenness: float
    is_critical: bool
    node_type: str


class ImpactResultResponse(BaseModel):
    impact_id: UUID
    failed_node: str
    affected_services: list[str]
    affected_workflows: list[str]
    estimated_transactions: int
    critical_paths: list[list[str]]
    alternative_providers: list[str]


class SimulationHistoryResponse(BaseModel):
    id: UUID
    failed_node: str
    duration_hours: float | None
    result: dict[str, Any]
    created_at: datetime
