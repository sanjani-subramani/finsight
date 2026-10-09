"""Income forecasting.

Each income source graduates through three modes as evidence accumulates
(see app.models.tables.IncomeSource's own docstring): DECLARED (0-2
observations, pure user input), HYBRID (3-7, a blend), OBSERVED (8+,
pure statistics). update_observations is the only place that touches raw
event history and numpy; forecast() reads the percentiles it already
computed and persisted, blending or passing them through per source.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Literal
from uuid import UUID

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import FinancialEventType, IncomeForecast
from app.models.tables import FinancialEvent, IncomeSource
from app.platform.timeutils import as_aware_utc

DECLARED_CONFIDENCE = 0.30
DEFAULT_ARRIVAL_UNCERTAINTY_DAYS = 3

ForecastMode = Literal["declared", "hybrid", "observed"]


@dataclass
class _SourceForecast:
    p10: Decimal | None
    p50: Decimal | None
    p90: Decimal | None
    declared_min: Decimal | None
    declared_max: Decimal | None
    confidence: float
    mode: ForecastMode
    expected_arrival: date | None
    arrival_uncertainty_days: int
    sample_size: int


def _dec(value: float | None) -> Decimal | None:
    return Decimal(str(value)) if value is not None else None


def _blend(observed: float | None, declared: Decimal | None, w: Decimal) -> Decimal | None:
    obs_dec = _dec(observed)
    if obs_dec is not None and declared is not None:
        return obs_dec * w + declared * (1 - w)
    return obs_dec if obs_dec is not None else declared


def _declared_mid(declared_min: Decimal | None, declared_max: Decimal | None) -> Decimal | None:
    if declared_min is not None and declared_max is not None:
        return (declared_min + declared_max) / 2
    return None


def _forecast_one_source(source: IncomeSource) -> _SourceForecast:
    obs_count = source.observation_count or 0
    declared_min = _dec(source.declared_min)
    declared_max = _dec(source.declared_max)

    mode: ForecastMode
    if obs_count <= 2:
        mode = "declared"
        p10, p50, p90 = declared_min, _declared_mid(declared_min, declared_max), declared_max
        confidence = DECLARED_CONFIDENCE
    elif obs_count <= 7:
        mode = "hybrid"
        # The weight ramps linearly with observation_count so trust
        # shifts gradually from what the user claimed to what actually
        # happened: a single anomalous 3rd payment shouldn't instantly
        # override weeks of declared expectation, but by observation 7
        # the system should be mostly trusting reality.
        w = Decimal(str((obs_count - 2) / 6))
        p10 = _blend(source.observed_p10, declared_min, w)
        p50 = _blend(source.observed_p50, _declared_mid(declared_min, declared_max), w)
        p90 = _blend(source.observed_p90, declared_max, w)
        confidence = min(1.0, 0.50 + 0.03 * obs_count)
    else:
        mode = "observed"
        p10, p50, p90 = _dec(source.observed_p10), _dec(source.observed_p50), _dec(source.observed_p90)
        confidence = min(0.90, 0.70 + 0.02 * obs_count)

    delay_std = source.observed_delay_std_days
    arrival_uncertainty_days = (
        int(math.ceil(delay_std)) if delay_std is not None else DEFAULT_ARRIVAL_UNCERTAINTY_DAYS
    )

    expected_arrival: date | None = None
    if source.last_received_date is not None and source.declared_frequency_days is not None:
        delay_mean = source.observed_delay_mean_days or 0.0
        expected_arrival = (
            source.last_received_date
            + timedelta(days=source.declared_frequency_days)
            + timedelta(days=round(delay_mean))
        )

    return _SourceForecast(
        p10=p10,
        p50=p50,
        p90=p90,
        declared_min=declared_min,
        declared_max=declared_max,
        confidence=confidence,
        mode=mode,
        expected_arrival=expected_arrival,
        arrival_uncertainty_days=arrival_uncertainty_days,
        sample_size=obs_count,
    )


def _aggregate(sources: list[_SourceForecast]) -> IncomeForecast:
    if not sources:
        return IncomeForecast(source="declared", confidence_score=0.0, sample_size=0)

    def _sum(values: list[Decimal | None]) -> Decimal | None:
        present = [v for v in values if v is not None]
        return sum(present, Decimal("0")) if present else None

    # Aggregating multiple income sources by SUMMING their percentiles
    # assumes each source's variability is independent of the others'.
    # That's a simplification — if a freelancer's clients are
    # concentrated in one sector, a downturn could hit several of them
    # at once, so the true combined p10 is probably somewhat lower than
    # this sum implies.
    p10 = _sum([s.p10 for s in sources])
    p50 = _sum([s.p50 for s in sources])
    p90 = _sum([s.p90 for s in sources])

    sample_size = sum(s.sample_size for s in sources)

    # Confidence weighted by each source's own p50 magnitude — a bigger
    # income source's certainty should matter more to the aggregate than
    # a tiny side income's, the same magnitude-weighting principle the
    # confidence engine (Step 4) uses for state_confidence.
    weight_total = sum(float(s.p50) for s in sources if s.p50 is not None)
    if weight_total > 0:
        confidence = sum(
            s.confidence * (float(s.p50) / weight_total if s.p50 is not None else 0.0)
            for s in sources
        )
    else:
        confidence = sum(s.confidence for s in sources) / len(sources)

    dominant = max(sources, key=lambda s: float(s.p50 or 0))

    expected_arrivals = [s.expected_arrival for s in sources if s.expected_arrival is not None]
    expected_arrival = min(expected_arrivals) if expected_arrivals else None
    arrival_uncertainty_days = max((s.arrival_uncertainty_days for s in sources), default=DEFAULT_ARRIVAL_UNCERTAINTY_DAYS)

    return IncomeForecast(
        expected_min=_sum([s.declared_min for s in sources]),
        expected_max=_sum([s.declared_max for s in sources]),
        p10=p10,
        p50=p50,
        p90=p90,
        expected_arrival=expected_arrival,
        arrival_uncertainty_days=arrival_uncertainty_days,
        source=dominant.mode,
        sample_size=sample_size,
        confidence_score=round(min(1.0, max(0.0, confidence)), 4),
    )


class IncomeForecaster:
    async def forecast(self, session: AsyncSession, user_id: UUID) -> IncomeForecast:
        result = await session.execute(
            select(IncomeSource).where(
                IncomeSource.user_id == user_id, IncomeSource.is_active.is_(True)
            )
        )
        sources = list(result.scalars())
        per_source = [_forecast_one_source(s) for s in sources]
        return _aggregate(per_source)


def _compute_delays(source: IncomeSource, history: list[FinancialEvent]) -> list[float]:
    # AMOUNT and TIMING are independent sources of uncertainty — a client
    # who always pays ₹20,000 but always 10 days late is a very different
    # risk from one who pays on time but a variable amount. So delay is
    # modelled entirely separately from the percentile amounts above,
    # from the gap between consecutive receipts vs. the declared
    # frequency (how many days later/earlier than expected each payment
    # actually arrived).
    if not source.declared_frequency_days or len(history) < 2:
        return []
    ordered = sorted(history, key=lambda e: as_aware_utc(e.occurred_at))
    deltas = []
    for prev_event, curr_event in zip(ordered, ordered[1:]):
        actual_interval = (
            as_aware_utc(curr_event.occurred_at).date() - as_aware_utc(prev_event.occurred_at).date()
        ).days
        deltas.append(float(actual_interval - source.declared_frequency_days))
    return deltas


async def _load_income_history(session: AsyncSession, source: IncomeSource) -> list[FinancialEvent]:
    result = await session.execute(
        select(FinancialEvent).where(
            FinancialEvent.user_id == source.user_id,
            FinancialEvent.event_type == FinancialEventType.income_received.value,
            FinancialEvent.counterparty == source.counterparty,
            FinancialEvent.duplicate_of.is_(None),
            FinancialEvent.superseded_by.is_(None),
        )
    )
    return list(result.scalars())


async def update_observations(
    session: AsyncSession, income_source: IncomeSource, received_event: FinancialEvent
) -> None:
    """Called when an INCOME_RECEIVED event is matched to income_source
    (matching — typically via the confidence engine's counterparty
    resolver — is the caller's job, not this function's). Increments
    observation_count, recomputes observed_* fields, and advances
    forecast_mode when thresholds are crossed."""
    if received_event.amount is None:
        return
    if received_event.event_type != FinancialEventType.income_received.value:
        return

    history = await _load_income_history(session, income_source)
    amounts = [float(e.amount) for e in history if e.amount is not None]
    if not amounts:
        return

    income_source.observation_count = len(amounts)

    # Use MEDIAN (the 50th percentile), never mean, for the central
    # estimate: one ₹200,000 one-off project should not drag a
    # freelancer's baseline monthly expectation upward — a mean would let
    # it; a median shrugs it off as a single outlier.
    p10, p50, p90 = np.percentile(amounts, [10, 50, 90])
    income_source.observed_p10 = float(round(p10, 2))
    income_source.observed_p50 = float(round(p50, 2))
    income_source.observed_p90 = float(round(p90, 2))

    delays = _compute_delays(income_source, history)
    if delays:
        income_source.observed_delay_mean_days = float(round(np.mean(delays), 2))
        income_source.observed_delay_std_days = (
            float(round(np.std(delays), 2)) if len(delays) > 1 else 0.0
        )

    latest = max(history, key=lambda e: as_aware_utc(e.occurred_at))
    income_source.last_received_date = as_aware_utc(latest.occurred_at).date()

    if income_source.observation_count >= 8:
        income_source.forecast_mode = "observed"
    elif income_source.observation_count >= 3:
        income_source.forecast_mode = "hybrid"
    else:
        income_source.forecast_mode = "declared"
