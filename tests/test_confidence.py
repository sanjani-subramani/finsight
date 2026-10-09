import asyncio
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as hyp_settings
from hypothesis import strategies as st
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.models.tables import Base, FinancialEvent
from app.modules.confidence.aggregator import compute_state_confidence
from app.modules.confidence.conflict import apply_resolution, detect_conflicts, resolve_conflict
from app.modules.confidence.counterparty import CounterpartyResolver
from app.modules.confidence.dedup import find_duplicates, mark_duplicate
from app.modules.confidence.decay import CONFIDENCE_FLOOR, apply_decay
from app.platform.config import get_settings


class _FakeRedis:
    """In-memory stand-in for redis.asyncio.Redis — avoids needing a live
    Redis server in this test environment."""

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


async def _make_row(
    session: AsyncSession,
    *,
    user_id,
    amount: Decimal,
    occurred_at: datetime,
    data_source: str,
    confidence_score: float,
    event_type: str = "income_received",
    counterparty: str | None = "ACME SOLUTIONS",
    ingested_at: datetime | None = None,
) -> FinancialEvent:
    row = FinancialEvent(
        id=uuid4(),
        user_id=user_id,
        schema_version=1,
        event_type=event_type,
        amount=amount,
        currency="INR",
        occurred_at=occurred_at,
        ingested_at=ingested_at or datetime.now(timezone.utc),
        data_source=data_source,
        confidence_score=confidence_score,
        counterparty=counterparty,
    )
    session.add(row)
    await session.flush()
    return row


def _fake_event(*, data_source: str, confidence_score: float, amount: str = "1000.00") -> FinancialEvent:
    """A plain (non-persisted) FinancialEvent — resolve_conflict is a pure
    function over attributes, so it doesn't need a real DB row."""
    return FinancialEvent(
        id=uuid4(),
        user_id=uuid4(),
        schema_version=1,
        event_type="expense",
        amount=Decimal(amount),
        currency="INR",
        occurred_at=datetime.now(timezone.utc),
        ingested_at=datetime.now(timezone.utc),
        data_source=data_source,
        confidence_score=confidence_score,
        counterparty="TEST",
    )


# ---------------------------------------------------------------------------
# Dedup: exact / near duplicates vs conflicts vs unrelated transactions
# ---------------------------------------------------------------------------


async def test_exact_duplicate_across_sms_and_csv_is_detected_and_marked(db_session):
    user_id = uuid4()
    occurred = datetime.now(timezone.utc)

    sms_row = await _make_row(
        db_session, user_id=user_id, amount=Decimal("18000.00"), occurred_at=occurred,
        data_source="sms", confidence_score=0.90, counterparty="ACME SOLUTIONS",
    )
    csv_row = await _make_row(
        db_session, user_id=user_id, amount=Decimal("18000.00"), occurred_at=occurred,
        data_source="bank_csv", confidence_score=0.95, counterparty="ACME SOLUTIONS PVT LTD",
    )

    candidates = await find_duplicates(db_session, csv_row, resolver=_resolver())
    assert len(candidates) == 1
    assert candidates[0].existing_event_id == sms_row.id

    await mark_duplicate(db_session, csv_row.id, sms_row.id)
    await db_session.flush()

    assert csv_row.duplicate_of == sms_row.id
    # append-only: the duplicate row must still exist, never deleted.
    still_there = await db_session.get(FinancialEvent, csv_row.id)
    assert still_there is not None


async def test_amount_differing_by_0_3_percent_is_treated_as_same_event(db_session):
    user_id = uuid4()
    occurred = datetime.now(timezone.utc)
    a = await _make_row(
        db_session, user_id=user_id, amount=Decimal("10000.00"), occurred_at=occurred,
        data_source="sms", confidence_score=0.90,
    )
    b = await _make_row(
        db_session, user_id=user_id, amount=Decimal("10030.00"), occurred_at=occurred,  # +0.3%
        data_source="bank_csv", confidence_score=0.95,
    )

    candidates = await find_duplicates(db_session, b, resolver=_resolver())
    assert len(candidates) == 1
    assert candidates[0].existing_event_id == a.id


async def test_amount_differing_by_5_percent_is_conflict_not_duplicate(db_session):
    user_id = uuid4()
    occurred = datetime.now(timezone.utc)
    a = await _make_row(
        db_session, user_id=user_id, amount=Decimal("10000.00"), occurred_at=occurred,
        data_source="sms", confidence_score=0.90,
    )
    b = await _make_row(
        db_session, user_id=user_id, amount=Decimal("10500.00"), occurred_at=occurred,  # +5%
        data_source="bank_csv", confidence_score=0.95,
    )

    duplicates = await find_duplicates(db_session, b, resolver=_resolver())
    assert duplicates == []

    conflicts = await detect_conflicts(db_session, b, resolver=_resolver())
    assert len(conflicts) == 1
    assert conflicts[0].event_b_id == a.id


async def test_amount_differing_by_50_percent_is_neither_duplicate_nor_conflict(db_session):
    user_id = uuid4()
    occurred = datetime.now(timezone.utc)
    a = await _make_row(
        db_session, user_id=user_id, amount=Decimal("10000.00"), occurred_at=occurred,
        data_source="sms", confidence_score=0.90,
    )
    b = await _make_row(
        db_session, user_id=user_id, amount=Decimal("15000.00"), occurred_at=occurred,  # +50%
        data_source="bank_csv", confidence_score=0.95,
    )

    assert await find_duplicates(db_session, b, resolver=_resolver()) == []
    assert await detect_conflicts(db_session, b, resolver=_resolver()) == []
    assert a.id  # sanity: both rows exist independently, as separate transactions


# ---------------------------------------------------------------------------
# Conflict resolution: authority ranking
# ---------------------------------------------------------------------------


def test_bank_csv_beats_sms_in_conflict_resolution():
    sms_event = _fake_event(data_source="sms", confidence_score=0.90)
    bank_event = _fake_event(data_source="bank_csv", confidence_score=0.95)
    resolution = resolve_conflict(sms_event, bank_event)
    assert resolution.winner_id == bank_event.id


def test_manual_beats_sms_normally():
    manual_event = _fake_event(data_source="manual", confidence_score=1.0)
    sms_event = _fake_event(data_source="sms", confidence_score=0.90)
    resolution = resolve_conflict(manual_event, sms_event)
    assert resolution.winner_id == manual_event.id


def test_manual_loses_to_bank_csv_when_directly_contradicted():
    # The subtle rule: manual is normally most authoritative, but a bank
    # record directly contradicting it wins — banks don't typo, users do.
    manual_event = _fake_event(data_source="manual", confidence_score=1.0)
    bank_event = _fake_event(data_source="bank_csv", confidence_score=0.95)
    resolution = resolve_conflict(manual_event, bank_event)
    assert resolution.winner_id == bank_event.id


def test_conflict_winner_confidence_drops_by_point_one():
    bank_event = _fake_event(data_source="bank_csv", confidence_score=0.95)
    sms_event = _fake_event(data_source="sms", confidence_score=0.90)
    resolution = resolve_conflict(bank_event, sms_event)
    assert resolution.winner_id == bank_event.id
    assert resolution.winner_new_confidence == pytest.approx(0.85)


async def test_loser_gets_superseded_by_and_is_not_deleted(db_session):
    user_id = uuid4()
    occurred = datetime.now(timezone.utc)
    bank_row = await _make_row(
        db_session, user_id=user_id, amount=Decimal("10000.00"), occurred_at=occurred,
        data_source="bank_csv", confidence_score=0.95,
    )
    sms_row = await _make_row(
        db_session, user_id=user_id, amount=Decimal("10500.00"), occurred_at=occurred,
        data_source="sms", confidence_score=0.90,
    )

    resolution = resolve_conflict(bank_row, sms_row)
    await apply_resolution(db_session, resolution, bank_row, sms_row)
    await db_session.flush()

    assert sms_row.superseded_by == bank_row.id
    assert bank_row.confidence_score == pytest.approx(0.85)

    still_there = await db_session.get(FinancialEvent, sms_row.id)
    assert still_there is not None  # append-only: never deleted


# ---------------------------------------------------------------------------
# Counterparty resolution
# ---------------------------------------------------------------------------


async def test_counterparty_exact_match_after_normalization():
    result = await _resolver().resolve("ACME SOLUTIONS PVT LTD", "Acme Solutions")
    assert result.is_same is True
    assert result.method == "exact"


async def test_counterparty_ambiguous_pair_resolves_via_llm():
    fake_client = _FakeGroqClient(
        json.dumps({"is_same": True, "confidence": 0.85, "reasoning": "abbreviated business name"})
    )
    resolver = CounterpartyResolver(
        http_client=fake_client, settings=_llm_settings_with_key(), redis_client=_FakeRedis()
    )
    result = await resolver.resolve("ACMESOL", "ACME SOLUTIONS")
    assert result.method == "llm"
    assert result.is_same is True


async def test_counterparty_clearly_different_entities():
    result = await _resolver().resolve("SWIGGY", "ZOMATO")
    assert result.is_same is False
    assert result.method == "fuzzy_low"


async def test_counterparty_ambiguous_band_with_no_llm_key_defaults_not_same():
    # No settings override -> real cached Settings, whose GROQ_API_KEY is
    # empty in this test environment (see .env.example / .env).
    result = await _resolver().resolve("ACMESOL", "ACME SOLUTIONS")
    assert result.is_same is False
    assert result.method == "no_llm_default"


# ---------------------------------------------------------------------------
# Decay
# ---------------------------------------------------------------------------


def test_decay_180_day_unconfirmed_event_has_materially_lower_confidence():
    decayed = apply_decay(0.90, age_days=180, is_confirmed=False)
    assert decayed < 0.90 * 0.5
    assert decayed >= CONFIDENCE_FLOOR


def test_decay_confirmed_event_does_not_decay():
    decayed = apply_decay(0.90, age_days=500, is_confirmed=True)
    assert decayed == 0.90


def test_decay_never_goes_below_floor():
    decayed = apply_decay(0.90, age_days=100_000, is_confirmed=False)
    assert decayed == pytest.approx(CONFIDENCE_FLOOR)


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------


async def test_magnitude_weighting_a_large_uncertain_event_impacts_confidence_more(db_session):
    # log1p compresses raw magnitude (a ₹18,000 event does not get 360x
    # the weight of a ₹50 one — only log1p(18000)/log1p(50) ≈ 2.5x), so
    # this is checked as one large vs one small event against the SAME
    # confident anchor, which is where the effect is unambiguous: given
    # enough small transactions their combined weight can still exceed
    # one big one (that's expected — many real small transactions really
    # do represent substantial activity), but per event, a big one always
    # pulls harder than a small one at equal uncertainty.
    anchor_amount = Decimal("5000.00")
    now = datetime.now(timezone.utc)

    user_a = uuid4()
    await _make_row(db_session, user_id=user_a, amount=anchor_amount, occurred_at=now, data_source="manual", confidence_score=1.0, counterparty="ANCHOR")
    await _make_row(db_session, user_id=user_a, amount=Decimal("18000.00"), occurred_at=now, data_source="sms", confidence_score=0.3, counterparty="BIG UNCERTAIN")
    state_large = await compute_state_confidence(db_session, user_a, resolver=_resolver())

    user_b = uuid4()
    await _make_row(db_session, user_id=user_b, amount=anchor_amount, occurred_at=now, data_source="manual", confidence_score=1.0, counterparty="ANCHOR")
    await _make_row(db_session, user_id=user_b, amount=Decimal("50.00"), occurred_at=now, data_source="sms", confidence_score=0.3, counterparty="SMALL UNCERTAIN")
    state_small = await compute_state_confidence(db_session, user_b, resolver=_resolver())

    assert state_large.score < state_small.score


async def test_simulated_data_presence_applies_penalty(db_session):
    now = datetime.now(timezone.utc)

    user_a = uuid4()
    await _make_row(db_session, user_id=user_a, amount=Decimal("1000.00"), occurred_at=now, data_source="manual", confidence_score=1.0)
    state_without_sim = await compute_state_confidence(db_session, user_a, resolver=_resolver())

    user_b = uuid4()
    await _make_row(db_session, user_id=user_b, amount=Decimal("1000.00"), occurred_at=now, data_source="manual", confidence_score=1.0)
    await _make_row(db_session, user_id=user_b, amount=Decimal("500.00"), occurred_at=now, data_source="simulated", confidence_score=1.0)
    state_with_sim = await compute_state_confidence(db_session, user_b, resolver=_resolver())

    assert state_with_sim.simulated_count == 1
    assert state_with_sim.breakdown["simulated_penalty"] == 0.10
    assert state_with_sim.score < state_without_sim.score


async def test_breakdown_contains_enough_to_reconstruct_final_score(db_session):
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    await _make_row(db_session, user_id=user_id, amount=Decimal("1000.00"), occurred_at=now, data_source="manual", confidence_score=0.8)

    state = await compute_state_confidence(db_session, user_id, resolver=_resolver())
    b = state.breakdown

    reconstructed = max(
        0.0, min(1.0, b["weighted_mean_confidence"] - b["conflict_penalty"] - b["simulated_penalty"])
    )
    assert reconstructed == pytest.approx(state.score, abs=1e-4)
    assert "per_event" in b
    assert len(b["per_event"]) == state.contributing_events


# ---------------------------------------------------------------------------
# Property test: score is always in [0, 1]
# ---------------------------------------------------------------------------


@given(
    st.lists(
        st.tuples(
            st.decimals(min_value=Decimal("0.01"), max_value=Decimal("100000"), places=2, allow_nan=False),
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            st.sampled_from(["sms", "bank_csv", "manual", "receipt_ocr", "simulated", "system"]),
            st.integers(min_value=0, max_value=400),
        ),
        min_size=0,
        max_size=8,
    )
)
@hyp_settings(deadline=None, max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_compute_state_confidence_always_in_unit_interval(events_spec):
    async def _run() -> None:
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with session_factory() as session:
            user_id = uuid4()
            now = datetime.now(timezone.utc)
            for amount, confidence, source, age_days in events_spec:
                session.add(
                    FinancialEvent(
                        id=uuid4(),
                        user_id=user_id,
                        schema_version=1,
                        event_type="expense",
                        amount=amount,
                        currency="INR",
                        occurred_at=now - timedelta(days=age_days),
                        ingested_at=now,
                        data_source=source,
                        confidence_score=confidence,
                    )
                )
            await session.flush()

            state = await compute_state_confidence(session, user_id)
            assert 0.0 <= state.score <= 1.0

        await engine.dispose()

    asyncio.run(_run())
