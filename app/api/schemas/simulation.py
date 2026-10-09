"""API request/response DTOs for simulation endpoints.

Plain Pydantic models, not the frozen event/state contracts in
app/contracts — these describe HTTP wire shapes for this router only.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SensitivityFactorResponse(BaseModel):
    name: str
    description: str
    prob_before: float
    prob_after: float
    delta: float
    actionable: bool


class RunResponse(BaseModel):
    run_id: UUID
    scenarios_run: int
    horizon_days: int
    seed: int
    shortfall_probability_by_horizon: dict[int, float]
    min_balance_p5: Decimal
    min_balance_p50: Decimal
    time_to_danger_days: int | None
    safe_to_spend: Decimal
    duration_ms: int
    from_cache: bool
    balance_matrix_summary: dict[str, Any]
    sensitivity: list[SensitivityFactorResponse]


class PurchaseRequest(BaseModel):
    amount: Decimal
    description: str = ""


class PurchaseVerdictResponse(BaseModel):
    affordable: bool
    prob_before: float
    prob_after: float
    wait_days_recommended: int | None
    reasoning_values: dict[str, Any]


class SimulationRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    scenarios: int
    horizon_days: int
    random_seed: int | None
    shortfall_probability: Decimal
    first_breach_date: date | None
    worst_case_balance: Decimal
    time_to_danger_days: int | None
    safe_to_spend: Decimal
    duration_ms: int | None
    created_at: datetime


class SimulationRunDetail(SimulationRunSummary):
    inputs_snapshot: dict[str, Any] | None
    percentile_curve: dict[str, Any] | None


class ReplayResponse(BaseModel):
    run_id: UUID
    matches: bool
    original_probability: float
    replayed_probability: float
