"""API request/response DTOs for twin endpoints.

Plain Pydantic models, not the frozen event/state contracts in
app/contracts — these describe HTTP wire shapes for this router only.
GET /twin/snapshot, /twin/obligations, and /twin/goals return the frozen
contracts directly (FinancialStateSnapshot, Obligation, Goal) since those
are already well-formed, stable read shapes.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.contracts.events import FinancialWeather


class StateResponse(BaseModel):
    cash_available: Decimal
    weather: FinancialWeather
    state_confidence: float


class ObligationCreateRequest(BaseModel):
    label: str
    amount: Decimal
    due_date: date
    category: str | None = None
    is_fixed: bool = True
    is_recurring: bool = False
    recurrence_rule: str | None = None


class ObligationUpdateRequest(BaseModel):
    label: str | None = None
    amount: Decimal | None = None
    due_date: date | None = None
    category: str | None = None
    is_fixed: bool | None = None
    is_paid: bool | None = None
    is_recurring: bool | None = None
    recurrence_rule: str | None = None


class ObligationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    amount: Decimal
    due_date: date
    category: str | None
    is_fixed: bool
    is_recurring: bool
    recurrence_rule: str | None
    is_paid: bool
    confidence_score: Decimal


class GoalCreateRequest(BaseModel):
    label: str
    target_amount: Decimal
    saved_amount: Decimal = Decimal("0")
    target_date: date | None = None
    priority: int = 3
    is_flexible: bool = True


class GoalUpdateRequest(BaseModel):
    label: str | None = None
    target_amount: Decimal | None = None
    saved_amount: Decimal | None = None
    target_date: date | None = None
    priority: int | None = None
    is_flexible: bool | None = None


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    target_amount: Decimal
    saved_amount: Decimal
    target_date: date | None
    priority: int
    is_flexible: bool


class IncomeSourceCreateRequest(BaseModel):
    label: str
    counterparty: str | None = None
    declared_min: Decimal | None = None
    declared_max: Decimal | None = None
    declared_frequency_days: int | None = None


class IncomeSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    counterparty: str | None
    declared_min: Decimal | None
    declared_max: Decimal | None
    declared_frequency_days: int | None
    observed_p10: Decimal | None
    observed_p50: Decimal | None
    observed_p90: Decimal | None
    observation_count: int
    forecast_mode: str
    confidence_score: Decimal


class RecurringCandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    counterparty: str
    category: str | None
    suggested_amount: Decimal
    interval_days: int
    day_of_month: int | None
    confidence: Decimal
    detection_method: str
    status: str
