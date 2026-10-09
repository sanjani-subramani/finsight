"""Event sourcing fold — the heart of the Digital Twin.

apply_event is a pure, synchronous fold step: given the accumulator state
so far and one financial_events row, it returns the new state. Everything
else in this module (rebuild_state, incremental_update) is just different
ways of feeding events through that one function.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import DataSource, FinancialEventType
from app.models.tables import FinancialEvent, TwinState
from app.platform.timeutils import as_aware_utc


@dataclass
class TwinAccumulator:
    cash: Decimal = Decimal("0")
    emergency_fund: Decimal = Decimal("0")
    # Keyed by a normalized-counterparty-derived string; values are plain
    # JSON-safe dicts (amounts/dates as strings) so the whole accumulator
    # round-trips through TwinState.fold_state without a custom codec.
    pending_income: dict[str, dict[str, Any]] = field(default_factory=dict)
    obligations_seen: dict[str, dict[str, Any]] = field(default_factory=dict)
    goals: dict[str, dict[str, Any]] = field(default_factory=dict)
    events_applied: int = 0
    last_event_id: UUID | None = None
    confidence_inputs: list[float] = field(default_factory=list)
    simulated_seen: bool = False
    reconciliation_deltas: list[dict[str, Any]] = field(default_factory=list)


def _norm(s: str | None) -> str:
    return (s or "").strip().upper()


def _due_date_of(event: FinancialEvent) -> date:
    if event.effective_date is not None:
        return event.effective_date
    return as_aware_utc(event.occurred_at).date()


def apply_event(state: TwinAccumulator, event: FinancialEvent) -> TwinAccumulator:
    # SKIP duplicates: a duplicate_of event describes the SAME real-world
    # transaction as another event already folded in — applying it again
    # would double-count the cash movement for something that only
    # happened once.
    if event.duplicate_of is not None:
        return state

    # SKIP superseded events: this row LOST a conflict resolution (see
    # app.modules.confidence.conflict) — a more authoritative source
    # disagreed and won. The winning event is what gets folded in; this
    # one's value was judged wrong.
    if event.superseded_by is not None:
        return state

    event_type = FinancialEventType(event.event_type)
    source = DataSource(event.data_source)
    # All arithmetic uses Decimal, never float: binary floating point
    # can't represent most decimal fractions exactly, and folding
    # thousands of events through a float accumulator would compound
    # that error into real, visible drift in the user's cash position.
    amount = Decimal(str(event.amount)) if event.amount is not None else None

    if source == DataSource.simulated:
        # Must propagate to the snapshot so the UI can badge it — real
        # and simulated data must never look the same to the user.
        state.simulated_seen = True

    if event_type in (FinancialEventType.income_received, FinancialEventType.transfer_in):
        if amount is not None:
            state.cash += amount
        _resolve_pending_income(state, event)

    elif event_type in (FinancialEventType.expense, FinancialEventType.transfer_out):
        if amount is not None:
            state.cash -= amount

    elif event_type in (FinancialEventType.bill_paid, FinancialEventType.emi_paid):
        if amount is not None:
            state.cash -= amount
        _mark_matching_obligation_paid(state, event)

    elif event_type in (FinancialEventType.bill_due, FinancialEventType.emi_due):
        _register_obligation(state, event, amount)

    elif event_type == FinancialEventType.income_expected:
        _register_pending_income(state, event, amount)

    elif event_type == FinancialEventType.income_delayed:
        _delay_pending_income(state, event)

    elif event_type == FinancialEventType.balance_snapshot:
        if amount is not None:
            # AUTHORITATIVE RESET — the self-healing property of the
            # design. A bank stating the actual balance outranks our own
            # accumulated arithmetic: we may have missed an event (a cash
            # withdrawal with no SMS, a CSV file not yet imported, a
            # duplicate we failed to catch). Rather than let that drift
            # compound silently forever, a balance_snapshot immediately
            # corrects it — and we record what the correction *was* so
            # it's visible and auditable rather than a silent jump.
            delta = amount - state.cash
            state.reconciliation_deltas.append(
                {
                    "event_id": str(event.id),
                    "occurred_at": event.occurred_at.isoformat(),
                    "previous_cash": str(state.cash),
                    "stated_balance": str(amount),
                    "delta": str(delta),
                }
            )
            state.cash = amount

    elif event_type in (FinancialEventType.goal_created, FinancialEventType.goal_updated):
        _upsert_goal(state, event)

    state.events_applied += 1
    state.last_event_id = event.id
    state.confidence_inputs.append(float(event.confidence_score))

    return state


def _register_obligation(state: TwinAccumulator, event: FinancialEvent, amount: Decimal | None) -> None:
    due = _due_date_of(event)
    key = f"{_norm(event.counterparty)}:{due.isoformat()}:{event.id}"
    state.obligations_seen[key] = {
        "label": event.description or event.counterparty or event.event_type,
        "counterparty": event.counterparty,
        "amount": str(amount) if amount is not None else None,
        "due_date": due.isoformat(),
        "category": event.category,
        "is_fixed": True,
        "is_paid": False,
        "confidence_score": float(event.confidence_score),
        "source_event_id": str(event.id),
    }


def _mark_matching_obligation_paid(state: TwinAccumulator, event: FinancialEvent) -> None:
    target = _norm(event.counterparty)
    if not target:
        return
    paid_on = _due_date_of(event)
    candidates = [
        (k, o)
        for k, o in state.obligations_seen.items()
        if not o["is_paid"] and _norm(o.get("counterparty")) == target
    ]
    if not candidates:
        return

    def _distance(item: tuple[str, dict[str, Any]]) -> int:
        due = date.fromisoformat(item[1]["due_date"])
        return abs((due - paid_on).days)

    key, _matched = min(candidates, key=_distance)
    state.obligations_seen[key]["is_paid"] = True
    state.obligations_seen[key]["paid_by_event_id"] = str(event.id)


def _register_pending_income(state: TwinAccumulator, event: FinancialEvent, amount: Decimal | None) -> None:
    key = _norm(event.counterparty) or f"UNKNOWN:{event.id}"
    state.pending_income[key] = {
        "counterparty": event.counterparty,
        "amount": str(amount) if amount is not None else None,
        "expected_arrival": _due_date_of(event).isoformat(),
        "confidence_score": float(event.confidence_score),
        "source_event_id": str(event.id),
    }


def _delay_pending_income(state: TwinAccumulator, event: FinancialEvent) -> None:
    key = _norm(event.counterparty)
    new_arrival = _due_date_of(event)
    entry = state.pending_income.get(key)
    if entry is not None:
        entry["expected_arrival"] = new_arrival.isoformat()
        entry["delayed_by_event_id"] = str(event.id)
    else:
        # No prior INCOME_EXPECTED registered for this counterparty —
        # register a fresh pending entry so the delay information isn't
        # simply dropped.
        state.pending_income[key] = {
            "counterparty": event.counterparty,
            "amount": None,
            "expected_arrival": new_arrival.isoformat(),
            "confidence_score": float(event.confidence_score),
            "source_event_id": str(event.id),
        }


def _resolve_pending_income(state: TwinAccumulator, event: FinancialEvent) -> None:
    key = _norm(event.counterparty)
    state.pending_income.pop(key, None)  # arrived — no longer pending


def _upsert_goal(state: TwinAccumulator, event: FinancialEvent) -> None:
    payload = event.raw_payload or {}
    goal_id = str(payload.get("goal_id") or event.id)
    existing = state.goals.get(goal_id, {})
    state.goals[goal_id] = {
        "label": payload.get("label", existing.get("label") or event.description or "Goal"),
        "target_amount": str(payload.get("target_amount", existing.get("target_amount", "0"))),
        "saved_amount": str(payload.get("saved_amount", existing.get("saved_amount", "0"))),
        "target_date": payload.get("target_date", existing.get("target_date")),
        "priority": int(payload.get("priority", existing.get("priority", 3))),
        "is_flexible": bool(payload.get("is_flexible", existing.get("is_flexible", True))),
    }


async def rebuild_state(
    session: AsyncSession, user_id: UUID, up_to: datetime | None = None
) -> TwinAccumulator:
    """Replays ALL events in occurred_at order. `up_to` enables
    point-in-time rebuild — Counterfactual Replay (a later step) needs
    exactly this."""
    stmt = select(FinancialEvent).where(FinancialEvent.user_id == user_id)
    if up_to is not None:
        stmt = stmt.where(FinancialEvent.occurred_at <= up_to)
    stmt = stmt.order_by(FinancialEvent.occurred_at, FinancialEvent.ingested_at)

    result = await session.execute(stmt)
    state = TwinAccumulator()
    for event in result.scalars():
        state = apply_event(state, event)
    return state


async def incremental_update(
    session: AsyncSession, user_id: UUID, new_event: FinancialEvent
) -> TwinAccumulator:
    """Applies exactly one event on top of the persisted accumulator,
    without replaying the event log.

    Correctness rests entirely on apply_event being a pure fold step:
    fold(events) == apply_event(fold(events[:-1]), events[-1]). Loading
    the persisted accumulator (TwinState.fold_state, an O(1) lookup)
    rather than keeping fold state in a module-global is what makes this
    safe across requests and processes — and, combined with fold_state
    persisting pending_income/obligations_seen/goals (not just the
    scalar cash/emergency_fund columns), is what makes this genuinely
    equivalent to rebuild_state rather than an approximation of it.
    """
    row = await _load_twin_state_row(session, user_id)
    state = _accumulator_from_row(row)
    state = apply_event(state, new_event)
    await _persist_fold_columns(session, user_id, state)
    return state


async def _load_twin_state_row(session: AsyncSession, user_id: UUID) -> TwinState | None:
    result = await session.execute(select(TwinState).where(TwinState.user_id == user_id))
    return result.scalar_one_or_none()


def _accumulator_from_row(row: TwinState | None) -> TwinAccumulator:
    if row is None:
        return TwinAccumulator()
    fold_state = row.fold_state or {}
    return TwinAccumulator(
        cash=Decimal(str(row.cash_available)),
        emergency_fund=Decimal(str(row.emergency_fund)),
        pending_income=dict(fold_state.get("pending_income") or {}),
        obligations_seen=dict(fold_state.get("obligations_seen") or {}),
        goals=dict(fold_state.get("goals") or {}),
        events_applied=row.events_applied,
        last_event_id=row.last_event_id,
        simulated_seen=row.contains_simulated_data,
        reconciliation_deltas=list(fold_state.get("reconciliation_deltas") or []),
    )


async def _persist_fold_columns(session: AsyncSession, user_id: UUID, state: TwinAccumulator) -> TwinState:
    # Deliberately touches only the "raw arithmetic" columns this module
    # owns (cash, emergency_fund, fold bookkeeping) — weather and
    # state_confidence are computed/persisted separately by
    # app.modules.twin.snapshot, which owns those derived columns on the
    # same row.
    row = await _load_twin_state_row(session, user_id)
    fold_state = {
        "pending_income": state.pending_income,
        "obligations_seen": state.obligations_seen,
        "goals": state.goals,
        "reconciliation_deltas": state.reconciliation_deltas,
    }
    if row is None:
        row = TwinState(
            user_id=user_id,
            cash_available=state.cash,
            emergency_fund=state.emergency_fund,
            weather="stable",
            state_confidence=0.0,
            unconfirmed_event_count=0,
            contains_simulated_data=state.simulated_seen,
            last_event_id=state.last_event_id,
            events_applied=state.events_applied,
            fold_state=fold_state,
        )
        session.add(row)
    else:
        row.cash_available = float(state.cash)
        row.emergency_fund = float(state.emergency_fund)
        row.contains_simulated_data = state.simulated_seen
        row.last_event_id = state.last_event_id
        row.events_applied = state.events_applied
        row.fold_state = fold_state
    await session.flush()
    return row
