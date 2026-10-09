"""Bridge from the Digital Twin to the pure simulation engine.

Everything with I/O (DB queries, the LLM inside distribution fitting)
lives here. engine.simulate() itself never sees a session.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import FinancialEventType, FinancialStateSnapshot
from app.models.tables import FinancialEvent, IncomeSource
from app.modules.simulation.distributions import DistributionSpec, fit_income_distribution
from app.modules.simulation.engine import IncomeSpec, ObligationSpec, SimulationInput
from app.platform.config import Settings, get_settings

DISCRETIONARY_LOOKBACK_DAYS = 60
DEFAULT_DAY_UNCERTAINTY = 3.0


def _seed_from_state(user_id: UUID, snapshot_id: UUID) -> int:
    # Deterministic from user_id + snapshot_id: the same twin state
    # always produces the same simulated probability. This matters
    # because a user refreshing the screen must never see the number
    # jitter for no reason — a probability that changes on every reload
    # (even though nothing about their finances did) reads as broken,
    # not as "randomness." A new snapshot_id (i.e. genuinely new events
    # folded in) is the only thing that should move the seed.
    basis = f"{user_id}:{snapshot_id}".encode()
    digest = hashlib.sha256(basis).hexdigest()
    # numpy's default_rng seed must fit in a 64-bit unsigned int.
    return int(digest, 16) % (2**63 - 1)


async def _fit_income_specs(
    session: AsyncSession,
    user_id: UUID,
    today: date,
    settings: Settings,
) -> list[IncomeSpec]:
    result = await session.execute(
        select(IncomeSource).where(IncomeSource.user_id == user_id, IncomeSource.is_active.is_(True))
    )
    sources = list(result.scalars())

    specs: list[IncomeSpec] = []
    for source in sources:
        history_result = await session.execute(
            select(FinancialEvent).where(
                FinancialEvent.user_id == user_id,
                FinancialEvent.event_type == FinancialEventType.income_received.value,
                FinancialEvent.counterparty == source.counterparty,
                FinancialEvent.duplicate_of.is_(None),
                FinancialEvent.superseded_by.is_(None),
            )
        )
        history = list(history_result.scalars())
        amounts = [Decimal(str(e.amount)) for e in history if e.amount is not None]

        if amounts:
            distribution = await fit_income_distribution(
                amounts, description=source.label, settings=settings
            )
        elif source.declared_min is not None and source.declared_max is not None:
            # No observed history yet — fall back to a flat empirical
            # distribution over the declared range's midpoint so a
            # brand-new, cold-start income source still contributes
            # something rather than being silently dropped from the sim.
            mid = (Decimal(str(source.declared_min)) + Decimal(str(source.declared_max))) / 2
            distribution = DistributionSpec(family="empirical", params={"values": [float(mid)]})
        else:
            continue  # nothing to simulate for this source at all

        if source.declared_frequency_days is None:
            expected_day = DISCRETIONARY_LOOKBACK_DAYS // 2  # no cadence known — guess mid-horizon
        elif source.last_received_date is not None:
            days_since_last = (today - source.last_received_date).days
            expected_day = max(0, source.declared_frequency_days - days_since_last)
        else:
            expected_day = source.declared_frequency_days

        if source.observed_delay_std_days is None:
            day_uncertainty = DEFAULT_DAY_UNCERTAINTY
        else:
            day_uncertainty = max(float(source.observed_delay_std_days), 1.0)

        specs.append(
            IncomeSpec(
                label=source.label,
                distribution=distribution,
                expected_day=expected_day,
                day_uncertainty_std=day_uncertainty,
            )
        )

    return specs


def _obligation_specs(snapshot: FinancialStateSnapshot, today: date) -> list[ObligationSpec]:
    specs: list[ObligationSpec] = []
    for obligation in snapshot.obligations:
        if obligation.is_paid:
            continue
        day_offset = (obligation.due_date - today).days
        if day_offset < 0:
            day_offset = 0  # already overdue — treat as due immediately
        specs.append(
            ObligationSpec(
                label=obligation.label,
                amount=obligation.amount,
                day_offset=day_offset,
                is_flexible=not obligation.is_fixed,
            )
        )
    return specs


async def _estimate_discretionary_spend(
    session: AsyncSession, user_id: UUID, today: date
) -> tuple[Decimal, Decimal]:
    """Mean/std of daily discretionary spend from the last 60 days of
    EXPENSE events, EXCLUDING anything matched to a recorded obligation.

    Obligation payments (rent, EMI, ...) are modelled explicitly and
    deterministically elsewhere in the simulation via ObligationSpec —
    counting them again here as "discretionary" would double-subtract
    the same rupee from every scenario's cash, making the simulation
    pessimistic in a way that has nothing to do with real uncertainty.
    """
    cutoff = datetime.combine(
        today, datetime.min.time(), tzinfo=timezone.utc
    ) - timedelta(days=DISCRETIONARY_LOOKBACK_DAYS)

    result = await session.execute(
        select(FinancialEvent).where(
            FinancialEvent.user_id == user_id,
            FinancialEvent.event_type == FinancialEventType.expense.value,
            FinancialEvent.occurred_at >= cutoff,
            FinancialEvent.duplicate_of.is_(None),
            FinancialEvent.superseded_by.is_(None),
        )
    )
    events = list(result.scalars())

    # Exclude anything already accounted for as an obligation payment —
    # obligation categories are a reasonable proxy since bill/EMI/rent
    # payments recorded as plain EXPENSE events still carry the same
    # category the recurring-detection pipeline assigned.
    obligation_categories = {"rent", "emi"}
    daily_totals: dict[date, Decimal] = {}
    for event in events:
        if (event.category or "").lower() in obligation_categories:
            continue
        if event.amount is None:
            continue
        day = event.occurred_at.date()
        daily_totals[day] = daily_totals.get(day, Decimal("0")) + Decimal(str(event.amount))

    if not daily_totals:
        return Decimal("0"), Decimal("0")

    values = np.array([float(v) for v in daily_totals.values()])
    mean = float(np.mean(values))
    std = float(np.std(values))
    return Decimal(str(round(mean, 2))), Decimal(str(round(std, 2)))


async def build_simulation_input(
    session: AsyncSession,
    snapshot: FinancialStateSnapshot,
    horizon_days: int,
    scenarios: int,
    seed: int | None = None,
) -> SimulationInput:
    settings = get_settings()
    today = date.today()

    income_specs = await _fit_income_specs(session, snapshot.user_id, today, settings)
    obligation_specs = _obligation_specs(snapshot, today)
    discretionary_mean, discretionary_std = await _estimate_discretionary_spend(
        session, snapshot.user_id, today
    )

    resolved_seed = seed if seed is not None else _seed_from_state(snapshot.user_id, snapshot.snapshot_id)

    return SimulationInput(
        starting_cash=snapshot.cash_available,
        income_events=income_specs,
        obligations=obligation_specs,
        discretionary_daily_mean=discretionary_mean,
        discretionary_daily_std=discretionary_std,
        horizon_days=horizon_days,
        scenarios=scenarios,
        seed=resolved_seed,
    )
