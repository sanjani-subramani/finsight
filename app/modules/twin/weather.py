"""Financial Weather computation.

Deterministic thresholds ONLY — no AI, no ambiguity, no model call that
could fail or hallucinate a wrong severity for something as visible and
consequential as "how worried should this person be right now."
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal

from app.contracts.events import FinancialWeather

# coverage = (cash + income_p10) / obligations_due_30d
COVERAGE_STABLE = 2.0
COVERAGE_PRESSURE = 1.3
COVERAGE_RISK = 1.0

# We must not scream CRITICAL based on data we do not trust — the same
# principle as the confidence ceiling applied to interventions later in
# the system, just applied earlier, at the source of the signal itself.
LOW_CONFIDENCE_THRESHOLD = 0.5
LOW_CONFIDENCE_SEVERITY_CAP = FinancialWeather.pressure

_SEVERITY_ORDER = [
    FinancialWeather.stable,
    FinancialWeather.pressure,
    FinancialWeather.risk,
    FinancialWeather.critical,
]


@dataclass
class WeatherResult:
    weather: FinancialWeather
    coverage: float
    cash: Decimal
    income_p10: Decimal
    obligations_due_30d: Decimal
    confidence: float
    confidence_capped: bool
    thresholds: dict[str, float]


def compute_weather(
    cash: Decimal,
    obligations_30d: Decimal,
    income_p10: Decimal | None,
    confidence: float,
) -> WeatherResult:
    # Use income_p10 (the pessimistic percentile), not p50: weather
    # should reflect the realistic downside, not the hopeful middle. A
    # user whose median case is fine but whose 10th-percentile income
    # misses rent deserves to know that *now*, not after it happens.
    p10 = income_p10 if income_p10 is not None else Decimal("0")

    if obligations_30d <= 0:
        coverage = math.inf
    else:
        coverage = float((cash + p10) / obligations_30d)

    if coverage >= COVERAGE_STABLE:
        weather = FinancialWeather.stable
    elif coverage >= COVERAGE_PRESSURE:
        weather = FinancialWeather.pressure
    elif coverage >= COVERAGE_RISK:
        weather = FinancialWeather.risk
    else:
        weather = FinancialWeather.critical

    confidence_capped = False
    if confidence < LOW_CONFIDENCE_THRESHOLD and _SEVERITY_ORDER.index(weather) > _SEVERITY_ORDER.index(
        LOW_CONFIDENCE_SEVERITY_CAP
    ):
        weather = LOW_CONFIDENCE_SEVERITY_CAP
        confidence_capped = True

    return WeatherResult(
        weather=weather,
        coverage=coverage,
        cash=cash,
        income_p10=p10,
        obligations_due_30d=obligations_30d,
        confidence=confidence,
        confidence_capped=confidence_capped,
        thresholds={
            "stable": COVERAGE_STABLE,
            "pressure": COVERAGE_PRESSURE,
            "risk": COVERAGE_RISK,
            "low_confidence_threshold": LOW_CONFIDENCE_THRESHOLD,
        },
    )
