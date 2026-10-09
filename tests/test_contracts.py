from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from app.contracts.events import (
    Confidence,
    DataSource,
    FinancialEventType,
    FinancialStateSnapshot,
    FinancialWeather,
    IncomeForecast,
    NormalizedFinancialEvent,
    Obligation,
)


def _make_event(**overrides) -> NormalizedFinancialEvent:
    fields = dict(
        user_id=uuid4(),
        event_type=FinancialEventType.expense,
        amount=Decimal("100.00"),
        occurred_at=datetime.now(timezone.utc),
        data_source=DataSource.manual,
        confidence_score=0.9,
    )
    fields.update(overrides)
    return NormalizedFinancialEvent(**fields)


def test_valid_event_constructs():
    event = _make_event()
    assert event.amount == Decimal("100.00")
    assert event.currency == "INR"
    assert event.schema_version == 1


def test_event_is_frozen():
    event = _make_event()
    with pytest.raises(ValidationError):
        event.amount = Decimal("50.00")


def test_unknown_field_raises():
    with pytest.raises(ValidationError):
        _make_event(unexpected_field="nope")


def test_negative_amount_raises():
    with pytest.raises(ValidationError):
        _make_event(amount=Decimal("-1.00"))


@pytest.mark.parametrize(
    "score,expected",
    [(0.9, Confidence.high), (0.6, Confidence.medium), (0.2, Confidence.low)],
)
def test_confidence_band(score, expected):
    event = _make_event(confidence_score=score)
    assert event.confidence_band == expected


def test_total_fixed_obligations_sums_correctly():
    obligations = [
        Obligation(
            label="Rent",
            amount=Decimal("15000.00"),
            due_date=date(2026, 10, 1),
            is_fixed=True,
            is_paid=False,
            confidence_score=0.9,
        ),
        Obligation(
            label="EMI",
            amount=Decimal("5000.00"),
            due_date=date(2026, 10, 5),
            is_fixed=True,
            is_paid=False,
            confidence_score=0.9,
        ),
        Obligation(
            label="Already paid bill",
            amount=Decimal("2000.00"),
            due_date=date(2026, 10, 3),
            is_fixed=True,
            is_paid=True,
            confidence_score=0.9,
        ),
        Obligation(
            label="Flexible spend",
            amount=Decimal("3000.00"),
            due_date=date(2026, 10, 10),
            is_fixed=False,
            is_paid=False,
            confidence_score=0.5,
        ),
    ]
    snapshot = FinancialStateSnapshot(
        user_id=uuid4(),
        cash_available=Decimal("50000.00"),
        emergency_fund=Decimal("20000.00"),
        income_forecast=IncomeForecast(source="declared", confidence_score=0.5),
        obligations=obligations,
        weather=FinancialWeather.stable,
        safe_to_spend=Decimal("10000.00"),
        state_confidence=0.7,
    )
    assert snapshot.total_fixed_obligations == Decimal("20000.00")


@given(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
def test_confidence_band_never_raises(score):
    event = _make_event(confidence_score=score)
    assert event.confidence_band in (
        Confidence.high,
        Confidence.medium,
        Confidence.low,
    )
