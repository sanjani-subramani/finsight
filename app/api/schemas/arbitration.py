"""API request/response DTOs for Goal Arbitration (Step 11)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ClaimResponse(BaseModel):
    claim_id: str
    label: str
    tier: int
    amount: Decimal
    due_date: date | None
    source: str


class AllocationResponse(BaseModel):
    claims: list[ClaimResponse]
    allocations: dict[str, Decimal]
    reductions: dict[str, Decimal]
    unfunded: list[str]
    prob_before: float
    prob_after: float
    trade_off_statement: str


class AlternativeResponse(BaseModel):
    profile: str
    allocations: dict[str, Decimal]
    reductions: dict[str, Decimal]
    prob_after: float


class SimulateProposalRequest(BaseModel):
    # claim_id -> proposed reduction amount, e.g. {"goal:<uuid>": 2000}
    reductions: dict[str, Decimal]


class SimulateProposalResponse(BaseModel):
    prob_before: float
    prob_after: float
    improved: bool


class AcceptActionResponse(BaseModel):
    intervention_id: UUID
    action_index: int
    action_type: str
    accepted: bool
