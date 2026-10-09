"""Demo data generator: a realistic 90-day freelancer financial history.

Irregular income from a few clients (sometimes paid late), fixed monthly
rent and EMI, and daily-ish small spending on food/transport/subscriptions.

Hard product requirement: simulated data must never be mistaken for real
data. Every event this module produces has data_source=SIMULATED, and
_make_event is the *only* place a simulated event is constructed — it
hardcodes that data source and asserts it rather than accepting it as a
caller-supplied parameter, so nothing here can ever blur real and
simulated history together.
"""

from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from app.contracts.events import DataSource, FinancialEventType, NormalizedFinancialEvent

CLIENTS = ["Acme Corp", "Beta Studios", "Nimbus Freelance Client"]
FOOD_MERCHANTS = ["Swiggy", "Zomato", "Local Cafe", "Grocery Store"]
TRANSPORT_MERCHANTS = ["Ola", "Uber", "Metro Card Recharge"]
SUBSCRIPTIONS = [
    ("Netflix", Decimal("199.00")),
    ("Spotify", Decimal("119.00")),
    ("Cloud Storage", Decimal("99.00")),
]


def _make_event(
    user_id: UUID,
    event_type: FinancialEventType,
    amount: Decimal,
    occurred_at: datetime,
    *,
    counterparty: str | None = None,
    category: str | None = None,
    description: str | None = None,
    effective_date: date | None = None,
) -> NormalizedFinancialEvent:
    event = NormalizedFinancialEvent(
        user_id=user_id,
        event_type=event_type,
        amount=amount,
        occurred_at=occurred_at,
        effective_date=effective_date,
        counterparty=counterparty,
        category=category,
        description=description,
        data_source=DataSource.simulated,
        confidence_score=1.0,
        raw_payload={"simulated": True},
    )
    # Hard product requirement: simulated and real data must never blur.
    # This assertion guards against a future edit here accidentally
    # wiring in a caller-supplied data_source.
    assert event.data_source is DataSource.simulated
    return event


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, 28)  # keep it simple/safe across month lengths
    return date(year, month, day)


def generate_freelancer_history(
    user_id: UUID,
    *,
    start_date: date | None = None,
    days: int = 90,
    seed: int | None = None,
) -> list[NormalizedFinancialEvent]:
    rng = random.Random(seed)
    start = start_date or (date.today() - timedelta(days=days))
    end = start + timedelta(days=days)
    months_covered = days // 30 + 2

    events: list[NormalizedFinancialEvent] = []

    # --- Irregular income from 2-3 clients, some paid late ---
    client_count = rng.choice([2, 3])
    clients = rng.sample(CLIENTS, client_count)
    for client in clients:
        base_amount = Decimal(rng.randrange(15000, 60000, 500))
        pay_day = rng.randint(1, 28)
        for month_offset in range(months_covered):
            due = _add_months(start, month_offset).replace(day=min(pay_day, 28))
            lateness_days = rng.choice([0, 0, 0, 2, 5, 9])
            paid_on = due + timedelta(days=lateness_days)
            if not (start <= paid_on <= end):
                continue
            jitter = Decimal(rng.randrange(-1000, 1000, 100))
            amount = max(base_amount + jitter, Decimal("1000"))
            events.append(
                _make_event(
                    user_id,
                    FinancialEventType.income_received,
                    amount,
                    datetime.combine(paid_on, time(10, 0), tzinfo=timezone.utc),
                    counterparty=client,
                    category="freelance_income",
                    description=f"Payment received from {client}",
                    effective_date=paid_on,
                )
            )

    # --- Fixed monthly rent + EMI ---
    rent_amount = Decimal(rng.randrange(12000, 25000, 500))
    emi_amount = Decimal(rng.randrange(5000, 15000, 500))
    for month_offset in range(months_covered):
        rent_day = _add_months(start, month_offset).replace(day=3)
        if start <= rent_day <= end:
            events.append(
                _make_event(
                    user_id,
                    FinancialEventType.expense,
                    rent_amount,
                    datetime.combine(rent_day, time(9, 0), tzinfo=timezone.utc),
                    counterparty="Landlord",
                    category="rent",
                    description="Monthly rent payment",
                    effective_date=rent_day,
                )
            )

        emi_day = _add_months(start, month_offset).replace(day=5)
        if start <= emi_day <= end:
            events.append(
                _make_event(
                    user_id,
                    FinancialEventType.emi_paid,
                    emi_amount,
                    datetime.combine(emi_day, time(9, 30), tzinfo=timezone.utc),
                    counterparty="Bank Loan Account",
                    category="emi",
                    description="Monthly EMI debit",
                    effective_date=emi_day,
                )
            )

    # --- Daily-ish small expenses ---
    for offset in range(days):
        day = start + timedelta(days=offset)

        if rng.random() < 0.75:
            merchant = rng.choice(FOOD_MERCHANTS)
            amount = Decimal(rng.randrange(80, 600))
            events.append(
                _make_event(
                    user_id,
                    FinancialEventType.expense,
                    amount,
                    datetime.combine(day, time(rng.randint(8, 21), 0), tzinfo=timezone.utc),
                    counterparty=merchant,
                    category="food",
                    description=f"Food order - {merchant}",
                    effective_date=day,
                )
            )

        if rng.random() < 0.4:
            merchant = rng.choice(TRANSPORT_MERCHANTS)
            amount = Decimal(rng.randrange(50, 400))
            events.append(
                _make_event(
                    user_id,
                    FinancialEventType.expense,
                    amount,
                    datetime.combine(day, time(rng.randint(7, 22), 0), tzinfo=timezone.utc),
                    counterparty=merchant,
                    category="transport",
                    description=f"Transport - {merchant}",
                    effective_date=day,
                )
            )

    # --- Monthly subscriptions ---
    for name, amount in SUBSCRIPTIONS:
        sub_day = rng.randint(1, 28)
        for month_offset in range(months_covered):
            billed = _add_months(start, month_offset).replace(day=sub_day)
            if start <= billed <= end:
                events.append(
                    _make_event(
                        user_id,
                        FinancialEventType.expense,
                        amount,
                        datetime.combine(billed, time(6, 0), tzinfo=timezone.utc),
                        counterparty=name,
                        category="subscription",
                        description=f"{name} subscription",
                        effective_date=billed,
                    )
                )

    events.sort(key=lambda e: e.occurred_at)
    return events
