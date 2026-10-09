import json
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import numpy as np
import pytest
from hypothesis import given
from hypothesis import settings as hyp_settings
from hypothesis import strategies as st

from app.contracts.events import FinancialWeather
from app.models.tables import FinancialEvent
from app.models.tables import IncomeSource
from app.models.tables import Obligation as ObligationRow
from app.modules.confidence.counterparty import CounterpartyResolver
from app.modules.twin import fold
from app.modules.twin.fold import TwinAccumulator, apply_event, incremental_update, rebuild_state
from app.modules.twin.forecast import IncomeForecaster, _forecast_one_source, update_observations
from app.modules.twin.obligations import detect_recurring, expand_recurring
from app.modules.twin.snapshot import build_snapshot, invalidate_snapshot
from app.modules.twin.weather import compute_weather
from app.platform.config import get_settings


# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------


class _FakeRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str) -> None:
        self._store[key] = value


class _FakeGroqClient:
    def __init__(self, content: str) -> None:
        self.content = content

    async def post(self, url, json=None, headers=None):
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": self.content}}]},
            request=httpx.Request("POST", url),
        )

    async def aclose(self) -> None:
        pass


def _llm_settings_with_key():
    return get_settings().model_copy(update={"GROQ_API_KEY": "test-key-not-real"})


def _resolver() -> CounterpartyResolver:
    return CounterpartyResolver(redis_client=_FakeRedis())


def _make_event(
    user_id,
    event_type: str = "expense",
    amount: Decimal | None = Decimal("100.00"),
    occurred_at: datetime | None = None,
    data_source: str = "manual",
    confidence_score: float = 0.9,
    counterparty: str | None = None,
    category: str | None = None,
    description: str | None = None,
    effective_date: date | None = None,
    duplicate_of=None,
    superseded_by=None,
    raw_payload: dict | None = None,
) -> FinancialEvent:
    return FinancialEvent(
        id=uuid4(),
        user_id=user_id,
        schema_version=1,
        event_type=event_type,
        amount=amount,
        currency="INR",
        occurred_at=occurred_at or datetime.now(timezone.utc),
        ingested_at=datetime.now(timezone.utc),
        effective_date=effective_date,
        counterparty=counterparty,
        category=category,
        description=description,
        data_source=data_source,
        confidence_score=confidence_score,
        duplicate_of=duplicate_of,
        superseded_by=superseded_by,
        raw_payload=raw_payload,
    )


# ---------------------------------------------------------------------------
# FOLD
# ---------------------------------------------------------------------------


def test_income_increases_cash_expense_decreases_it():
    state = TwinAccumulator()
    state = apply_event(
        state, _make_event(uuid4(), event_type="income_received", amount=Decimal("1000.00"))
    )
    assert state.cash == Decimal("1000.00")

    state = apply_event(state, _make_event(uuid4(), event_type="expense", amount=Decimal("300.00")))
    assert state.cash == Decimal("700.00")


def test_duplicate_and_superseded_events_are_skipped():
    state = TwinAccumulator()

    dup = _make_event(
        uuid4(), event_type="income_received", amount=Decimal("500.00"), duplicate_of=uuid4()
    )
    state = apply_event(state, dup)
    assert state.cash == Decimal("0") and state.events_applied == 0

    superseded = _make_event(
        uuid4(), event_type="income_received", amount=Decimal("500.00"), superseded_by=uuid4()
    )
    state = apply_event(state, superseded)
    assert state.cash == Decimal("0") and state.events_applied == 0


def test_balance_snapshot_resets_cash_authoritatively():
    state = TwinAccumulator(cash=Decimal("100.00"))
    state = apply_event(
        state, _make_event(uuid4(), event_type="balance_snapshot", amount=Decimal("5000.00"))
    )
    assert state.cash == Decimal("5000.00")
    assert len(state.reconciliation_deltas) == 1
    assert state.reconciliation_deltas[0]["delta"] == "4900.00"


async def test_simulated_data_sets_contains_simulated_data_on_snapshot(db_session):
    user_id = uuid4()
    db_session.add(
        _make_event(
            user_id,
            event_type="income_received",
            amount=Decimal("1000.00"),
            data_source="simulated",
            confidence_score=1.0,
        )
    )
    await db_session.flush()

    snapshot = await build_snapshot(db_session, user_id, use_cache=False)
    assert snapshot.contains_simulated_data is True


def test_decimal_precision_100_events_of_0_01_sum_exactly():
    state = TwinAccumulator()
    for _ in range(100):
        state = apply_event(
            state, _make_event(uuid4(), event_type="income_received", amount=Decimal("0.01"))
        )
    assert state.cash == Decimal("1.00")


async def test_incremental_update_matches_full_rebuild(db_session):
    user_id = uuid4()
    events = [
        _make_event(
            user_id,
            event_type="income_received",
            amount=Decimal("1000.00"),
            occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ),
        _make_event(
            user_id,
            event_type="expense",
            amount=Decimal("200.00"),
            occurred_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        ),
        _make_event(
            user_id,
            event_type="bill_due",
            amount=Decimal("500.00"),
            counterparty="Landlord",
            occurred_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
            effective_date=date(2026, 1, 10),
        ),
        _make_event(
            user_id,
            event_type="bill_paid",
            amount=Decimal("500.00"),
            counterparty="Landlord",
            occurred_at=datetime(2026, 1, 10, tzinfo=timezone.utc),
        ),
    ]
    for e in events:
        db_session.add(e)
    await db_session.flush()

    full_state = await rebuild_state(db_session, user_id)

    prior_state = await rebuild_state(db_session, user_id, up_to=events[-2].occurred_at)
    await fold._persist_fold_columns(db_session, user_id, prior_state)
    incremental_state = await incremental_update(db_session, user_id, events[-1])

    assert incremental_state.cash == full_state.cash
    assert incremental_state.events_applied == full_state.events_applied
    assert incremental_state.obligations_seen == full_state.obligations_seen


async def test_point_in_time_rebuild_returns_historical_state(db_session):
    user_id = uuid4()
    e1 = _make_event(
        user_id,
        event_type="income_received",
        amount=Decimal("1000.00"),
        occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    e2 = _make_event(
        user_id,
        event_type="income_received",
        amount=Decimal("500.00"),
        occurred_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
    )
    db_session.add_all([e1, e2])
    await db_session.flush()

    historical = await rebuild_state(db_session, user_id, up_to=datetime(2026, 1, 15, tzinfo=timezone.utc))
    assert historical.cash == Decimal("1000.00")

    full = await rebuild_state(db_session, user_id)
    assert full.cash == Decimal("1500.00")


# ---------------------------------------------------------------------------
# FORECAST
# ---------------------------------------------------------------------------


async def test_zero_observations_declared_mode(db_session):
    user_id = uuid4()
    source = IncomeSource(
        user_id=user_id,
        label="Client A",
        counterparty="CLIENT A",
        declared_min=Decimal("10000"),
        declared_max=Decimal("20000"),
        declared_frequency_days=30,
        observation_count=0,
        forecast_mode="declared",
        confidence_score=0.30,
        is_active=True,
    )
    db_session.add(source)
    await db_session.flush()

    forecast = await IncomeForecaster().forecast(db_session, user_id)
    assert forecast.source == "declared"
    assert forecast.confidence_score == pytest.approx(0.30)
    assert forecast.p10 == Decimal("10000")
    assert forecast.p90 == Decimal("20000")


async def test_five_observations_hybrid_blended(db_session):
    user_id = uuid4()
    source = IncomeSource(
        user_id=user_id,
        label="Client B",
        counterparty="CLIENT B",
        declared_min=Decimal("10000"),
        declared_max=Decimal("20000"),
        declared_frequency_days=30,
        observation_count=0,
        forecast_mode="declared",
        confidence_score=0.30,
        is_active=True,
    )
    db_session.add(source)
    await db_session.flush()

    base_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    amounts = [Decimal("25000"), Decimal("26000"), Decimal("24000"), Decimal("25500"), Decimal("24500")]
    last_event = None
    for i, amt in enumerate(amounts):
        event = _make_event(
            user_id,
            event_type="income_received",
            amount=amt,
            occurred_at=base_date + timedelta(days=30 * i),
            counterparty="CLIENT B",
            data_source="sms",
        )
        db_session.add(event)
        last_event = event
    await db_session.flush()

    await update_observations(db_session, source, last_event)

    assert source.observation_count == 5
    assert source.forecast_mode == "hybrid"

    forecast = await IncomeForecaster().forecast(db_session, user_id)
    assert forecast.source == "hybrid"
    # Blended p50 lands strictly between the declared midpoint (15000)
    # and the (much higher) observed reality — trust shifting toward
    # what actually happened.
    assert Decimal("15000") < forecast.p50 < Decimal("26000")


async def test_ten_observations_observed_pure_percentiles(db_session):
    user_id = uuid4()
    source = IncomeSource(
        user_id=user_id,
        label="Client C",
        counterparty="CLIENT C",
        declared_min=Decimal("10000"),
        declared_max=Decimal("20000"),
        declared_frequency_days=15,
        observation_count=0,
        forecast_mode="declared",
        confidence_score=0.30,
        is_active=True,
    )
    db_session.add(source)
    await db_session.flush()

    base_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    amounts = [Decimal(str(18000 + i * 100)) for i in range(10)]
    last_event = None
    for i, amt in enumerate(amounts):
        event = _make_event(
            user_id,
            event_type="income_received",
            amount=amt,
            occurred_at=base_date + timedelta(days=15 * i),
            counterparty="CLIENT C",
            data_source="sms",
        )
        db_session.add(event)
        last_event = event
    await db_session.flush()

    await update_observations(db_session, source, last_event)
    forecast = await IncomeForecaster().forecast(db_session, user_id)

    assert forecast.source == "observed"
    expected_p50 = np.percentile([float(a) for a in amounts], 50)
    assert float(forecast.p50) == pytest.approx(expected_p50, abs=1.0)


@given(
    declared_min=st.decimals(min_value=Decimal("100"), max_value=Decimal("50000"), places=2, allow_nan=False),
    spread=st.decimals(min_value=Decimal("0"), max_value=Decimal("50000"), places=2, allow_nan=False),
    obs_count=st.integers(min_value=0, max_value=20),
    observed_low=st.floats(min_value=0, max_value=100_000, allow_nan=False),
    mid_extra=st.floats(min_value=0, max_value=50_000, allow_nan=False),
    high_extra=st.floats(min_value=0, max_value=50_000, allow_nan=False),
)
@hyp_settings(deadline=None, max_examples=50)
def test_forecast_percentile_ordering_always_holds(
    declared_min, spread, obs_count, observed_low, mid_extra, high_extra
):
    declared_max = declared_min + spread
    observed_p10 = observed_low
    observed_p50 = observed_p10 + mid_extra
    observed_p90 = observed_p50 + high_extra

    source = IncomeSource(
        user_id=uuid4(),
        label="x",
        declared_min=declared_min,
        declared_max=declared_max,
        declared_frequency_days=30,
        observed_p10=observed_p10,
        observed_p50=observed_p50,
        observed_p90=observed_p90,
        observation_count=obs_count,
        forecast_mode="declared",
        confidence_score=0.3,
        is_active=True,
    )
    result = _forecast_one_source(source)
    if result.p10 is not None and result.p50 is not None:
        assert result.p10 <= result.p50
    if result.p50 is not None and result.p90 is not None:
        assert result.p50 <= result.p90


async def test_one_outlier_income_does_not_move_median_much(db_session):
    user_id = uuid4()
    source = IncomeSource(
        user_id=user_id,
        label="Freelancer",
        counterparty="FREELANCE CLIENT",
        declared_min=Decimal("15000"),
        declared_max=Decimal("25000"),
        declared_frequency_days=15,
        observation_count=0,
        forecast_mode="declared",
        confidence_score=0.30,
        is_active=True,
    )
    db_session.add(source)
    await db_session.flush()

    base_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    amounts = [Decimal("20000")] * 7 + [Decimal("200000")]  # one huge outlier among 8 typical payments
    last_event = None
    for i, amt in enumerate(amounts):
        event = _make_event(
            user_id,
            event_type="income_received",
            amount=amt,
            occurred_at=base_date + timedelta(days=15 * i),
            counterparty="FREELANCE CLIENT",
            data_source="sms",
        )
        db_session.add(event)
        last_event = event
    await db_session.flush()

    await update_observations(db_session, source, last_event)
    assert source.observed_p50 == pytest.approx(20000, abs=500)


async def test_arrival_delay_modelling_produces_sensible_uncertainty(db_session):
    user_id = uuid4()
    source = IncomeSource(
        user_id=user_id,
        label="Client D",
        counterparty="CLIENT D",
        declared_min=Decimal("10000"),
        declared_max=Decimal("10000"),
        declared_frequency_days=30,
        observation_count=0,
        forecast_mode="declared",
        confidence_score=0.30,
        is_active=True,
    )
    db_session.add(source)
    await db_session.flush()

    base_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    # Intervals of 30, 35, 31, 34 days vs. a declared 30-day frequency ->
    # consistently a little late.
    offsets = [0, 30, 65, 96, 130]
    last_event = None
    for offset in offsets:
        event = _make_event(
            user_id,
            event_type="income_received",
            amount=Decimal("10000"),
            occurred_at=base_date + timedelta(days=offset),
            counterparty="CLIENT D",
            data_source="sms",
        )
        db_session.add(event)
        last_event = event
    await db_session.flush()

    await update_observations(db_session, source, last_event)

    assert source.observed_delay_mean_days is not None
    assert source.observed_delay_mean_days > 0  # consistently late, on average
    assert source.observed_delay_std_days is not None

    one_source = _forecast_one_source(source)
    assert one_source.arrival_uncertainty_days >= 1


# ---------------------------------------------------------------------------
# OBLIGATIONS
# ---------------------------------------------------------------------------


def test_monthly_recurrence_expands_across_90_day_horizon():
    parent = ObligationRow(
        id=uuid4(),
        user_id=uuid4(),
        label="Rent",
        amount=Decimal("15000.00"),
        due_date=date(2026, 1, 5),
        category="rent",
        is_fixed=True,
        is_recurring=True,
        recurrence_rule="MONTHLY:5",
        is_paid=False,
        data_source="manual",
        confidence_score=1.0,
    )
    projected = expand_recurring(parent, horizon_days=90, today=date(2026, 1, 1))

    assert len(projected) >= 2
    assert all(p.due_date.day == 5 for p in projected)
    assert all(p.due_date > date(2026, 1, 5) for p in projected)
    # Projected instances get confidence = parent * 0.9 — slightly less
    # certain than a recorded obligation.
    assert all(p.confidence_score == pytest.approx(0.9) for p in projected)


async def test_three_identical_monthly_payments_detected_statistically_no_llm(db_session):
    user_id = uuid4()
    base = datetime(2026, 1, 5, tzinfo=timezone.utc)
    for i in range(3):
        db_session.add(
            _make_event(
                user_id,
                event_type="expense",
                amount=Decimal("15000.00"),
                occurred_at=base + timedelta(days=30 * i),
                counterparty="LANDLORD",
                data_source="sms",
            )
        )
    await db_session.flush()

    llm_client_mock = AsyncMock()
    candidates = await detect_recurring(
        db_session, user_id, resolver=_resolver(), http_client=llm_client_mock
    )

    assert len(candidates) == 1
    assert candidates[0].detection_method == "statistical"
    llm_client_mock.post.assert_not_called()


async def test_irregular_amount_escalates_to_llm_band(db_session):
    user_id = uuid4()
    base = datetime(2026, 1, 5, tzinfo=timezone.utc)
    amounts = [Decimal("1000.00"), Decimal("1250.00"), Decimal("900.00")]  # ~14% variance -> ambiguous
    for i, amt in enumerate(amounts):
        db_session.add(
            _make_event(
                user_id,
                event_type="expense",
                amount=amt,
                occurred_at=base + timedelta(days=30 * i),
                counterparty="ELECTRICITY BOARD",
                data_source="sms",
            )
        )
    await db_session.flush()

    fake_client = _FakeGroqClient(
        json.dumps(
            {
                "is_recurring": True,
                "kind": "electricity_bill",
                "confidence": 0.8,
                "reasoning": "Variable usage-based bill",
            }
        )
    )
    candidates = await detect_recurring(
        db_session,
        user_id,
        resolver=_resolver(),
        settings=_llm_settings_with_key(),
        http_client=fake_client,
    )

    assert len(candidates) == 1
    assert candidates[0].detection_method == "llm"


async def test_no_llm_key_ambiguous_band_skipped_without_error(db_session):
    user_id = uuid4()
    base = datetime(2026, 1, 5, tzinfo=timezone.utc)
    amounts = [Decimal("1000.00"), Decimal("1250.00"), Decimal("900.00")]
    for i, amt in enumerate(amounts):
        db_session.add(
            _make_event(
                user_id,
                event_type="expense",
                amount=amt,
                occurred_at=base + timedelta(days=30 * i),
                counterparty="ELECTRICITY BOARD",
                data_source="sms",
            )
        )
    await db_session.flush()

    # Default settings -> no GROQ_API_KEY in this test environment.
    candidates = await detect_recurring(db_session, user_id, resolver=_resolver())
    assert candidates == []


# ---------------------------------------------------------------------------
# WEATHER
# ---------------------------------------------------------------------------


def test_weather_coverage_2_5_stable():
    result = compute_weather(
        cash=Decimal("2000"), obligations_30d=Decimal("1000"), income_p10=Decimal("500"), confidence=0.9
    )
    assert result.weather == FinancialWeather.stable


def test_weather_coverage_1_5_pressure():
    result = compute_weather(
        cash=Decimal("1000"), obligations_30d=Decimal("1000"), income_p10=Decimal("500"), confidence=0.9
    )
    assert result.weather == FinancialWeather.pressure


def test_weather_coverage_1_1_risk():
    result = compute_weather(
        cash=Decimal("600"), obligations_30d=Decimal("1000"), income_p10=Decimal("500"), confidence=0.9
    )
    assert result.weather == FinancialWeather.risk


def test_weather_coverage_0_8_critical():
    result = compute_weather(
        cash=Decimal("300"), obligations_30d=Decimal("1000"), income_p10=Decimal("500"), confidence=0.9
    )
    assert result.weather == FinancialWeather.critical


def test_weather_low_confidence_caps_severity_at_pressure():
    # coverage = 500/1000 = 0.5 -> would be CRITICAL, but confidence 0.4 caps it.
    result = compute_weather(
        cash=Decimal("0"), obligations_30d=Decimal("1000"), income_p10=Decimal("500"), confidence=0.4
    )
    assert result.weather == FinancialWeather.pressure
    assert result.confidence_capped is True


def test_weather_uses_income_p10_not_p50():
    pessimistic = compute_weather(
        cash=Decimal("0"), obligations_30d=Decimal("1000"), income_p10=Decimal("200"), confidence=0.9
    )
    optimistic = compute_weather(
        cash=Decimal("0"), obligations_30d=Decimal("1000"), income_p10=Decimal("2500"), confidence=0.9
    )
    assert pessimistic.weather in (FinancialWeather.risk, FinancialWeather.critical)
    assert optimistic.weather == FinancialWeather.stable
    assert pessimistic.income_p10 == Decimal("200")


# ---------------------------------------------------------------------------
# SNAPSHOT
# ---------------------------------------------------------------------------


async def test_snapshot_contains_all_required_fields(db_session):
    user_id = uuid4()
    db_session.add(
        _make_event(
            user_id,
            event_type="income_received",
            amount=Decimal("20000.00"),
            data_source="manual",
            confidence_score=1.0,
        )
    )
    await db_session.flush()

    snapshot = await build_snapshot(db_session, user_id, use_cache=False)
    assert snapshot.user_id == user_id
    assert snapshot.cash_available == Decimal("20000.00")
    assert snapshot.weather is not None
    assert snapshot.income_forecast is not None
    assert isinstance(snapshot.obligations, list)
    assert isinstance(snapshot.goals, list)
    assert 0.0 <= snapshot.state_confidence <= 1.0


async def test_cache_hit_returns_identical_data(db_session):
    user_id = uuid4()
    db_session.add(
        _make_event(
            user_id,
            event_type="income_received",
            amount=Decimal("5000.00"),
            data_source="manual",
            confidence_score=1.0,
        )
    )
    await db_session.flush()

    fake_redis = _FakeRedis()
    first = await build_snapshot(db_session, user_id, use_cache=True, redis_client=fake_redis)
    second = await build_snapshot(db_session, user_id, use_cache=True, redis_client=fake_redis)

    assert first.snapshot_id == second.snapshot_id
    assert first == second


async def test_new_event_invalidates_cache(db_session):
    user_id = uuid4()
    db_session.add(
        _make_event(
            user_id,
            event_type="income_received",
            amount=Decimal("1000.00"),
            data_source="manual",
            confidence_score=1.0,
        )
    )
    await db_session.flush()

    fake_redis = _FakeRedis()
    first = await build_snapshot(db_session, user_id, use_cache=True, redis_client=fake_redis)
    assert first.cash_available == Decimal("1000.00")

    # In production this is exactly what TwinService.on_event_ingested
    # does: fold the new event into the persisted accumulator, then
    # invalidate. Simulated explicitly here since the test adds the event
    # directly rather than going through the ingestion router.
    new_event = _make_event(
        user_id,
        event_type="income_received",
        amount=Decimal("500.00"),
        data_source="manual",
        confidence_score=1.0,
    )
    db_session.add(new_event)
    await db_session.flush()
    await fold.incremental_update(db_session, user_id, new_event)
    await invalidate_snapshot(user_id, redis_client=fake_redis)

    second = await build_snapshot(db_session, user_id, use_cache=True, redis_client=fake_redis)
    assert second.cash_available == Decimal("1500.00")
    assert second.cash_available != first.cash_available


async def test_total_fixed_obligations_sums_correctly_in_snapshot(db_session):
    from app.modules.twin.service import TwinService

    user_id = uuid4()
    service = TwinService()
    await service.add_obligation(
        db_session,
        user_id,
        label="Rent",
        amount=Decimal("15000.00"),
        due_date=date.today() + timedelta(days=5),
        is_fixed=True,
    )
    await service.add_obligation(
        db_session,
        user_id,
        label="Streaming subscription",
        amount=Decimal("500.00"),
        due_date=date.today() + timedelta(days=10),
        is_fixed=False,
    )

    snapshot = await build_snapshot(db_session, user_id, use_cache=False)
    assert snapshot.total_fixed_obligations == Decimal("15000.00")
