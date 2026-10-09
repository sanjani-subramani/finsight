"""One comparable score so the Gate can rank findings and collisions
against each other on a single number, with a fully hand-reconstructable
breakdown.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

PROBABILITY_WEIGHT = 0.35
SEVERITY_WEIGHT = 0.25
URGENCY_WEIGHT = 0.20
MAGNITUDE_WEIGHT = 0.20

_SEVERITY_STRING_TO_SCALE = {"low": 1, "medium": 3, "high": 4, "critical": 5}
_URGENCY_STRING_TO_SCALE = {"low": 1, "medium": 3, "high": 4, "critical": 5}
_URGENCY_DAYS_CRITICAL = 3
_URGENCY_DAYS_HIGH = 7
_URGENCY_DAYS_MEDIUM = 14


@dataclass(frozen=True)
class RiskScore:
    score: float
    breakdown: dict[str, Any] = field(default_factory=dict)


def _normalize_severity(severity: int | str) -> float:
    # Findings carry an int severity (1-5, see rules.py); collisions
    # carry a string severity level (low/medium/high/critical, see
    # collision.py) — both land on the same [0, 1] scale here so they're
    # directly comparable when ranked together.
    scale = _SEVERITY_STRING_TO_SCALE.get(severity.lower(), 3) if isinstance(severity, str) else severity
    return max(0.0, min(1.0, (scale - 1) / 4))


def _normalize_urgency(urgency: int | str | None) -> float:
    if urgency is None:
        return 0.5  # unknown timing: neutral, neither dismissed nor alarmed
    if isinstance(urgency, str):
        scale = _URGENCY_STRING_TO_SCALE.get(urgency.lower(), 3)
    else:
        # int: "days until impact" — FEWER days is MORE urgent, the
        # inverse relationship of severity's scale.
        days = urgency
        if days <= _URGENCY_DAYS_CRITICAL:
            scale = 5
        elif days <= _URGENCY_DAYS_HIGH:
            scale = 4
        elif days <= _URGENCY_DAYS_MEDIUM:
            scale = 3
        else:
            scale = 1
    return max(0.0, min(1.0, (scale - 1) / 4))


def _normalize_magnitude(amount_at_risk: Decimal, monthly_obligations: Decimal) -> float:
    if monthly_obligations <= 0:
        return 1.0 if amount_at_risk > 0 else 0.0
    ratio = math.log1p(float(amount_at_risk)) / math.log1p(float(monthly_obligations))
    return max(0.0, min(1.0, ratio))


def compute_risk_score(
    probability: float,
    severity: int | str,
    urgency: int | str | None,
    confidence: float,
    amount_at_risk: Decimal,
    monthly_obligations: Decimal,
) -> RiskScore:
    """amount_at_risk / monthly_obligations decompose what the spec calls
    "financial_magnitude": the log1p-ratio formula genuinely needs both
    values (an absolute amount is meaningless as risk without something
    to compare it against), so this elaborates the single conceptual
    input into its two constituent numbers rather than passing an
    already-normalized magnitude in.
    """
    probability_term = max(0.0, min(1.0, probability))
    severity_normalized = _normalize_severity(severity)
    urgency_normalized = _normalize_urgency(urgency)
    magnitude_normalized = _normalize_magnitude(amount_at_risk, monthly_obligations)

    raw_score = (
        probability_term * PROBABILITY_WEIGHT
        + severity_normalized * SEVERITY_WEIGHT
        + urgency_normalized * URGENCY_WEIGHT
        + magnitude_normalized * MAGNITUDE_WEIGHT
    )

    # CRITICAL: confidence is a MULTIPLIER, not an additive term. A
    # high-probability finding built on data we do not trust must score
    # LOWER than the same finding on trusted data — adding confidence as
    # just another weighted term would still let a confident-SOUNDING but
    # unreliable finding rank near the top. This is the same principle as
    # the Step 8 confidence ceiling ("don't act loudly on data you don't
    # trust"), applied here to ranking instead of severity capping.
    confidence_clamped = max(0.0, min(1.0, confidence))
    score = raw_score * confidence_clamped

    breakdown: dict[str, Any] = {
        "probability": probability_term,
        "probability_weight": PROBABILITY_WEIGHT,
        "probability_contribution": probability_term * PROBABILITY_WEIGHT,
        "severity_normalized": severity_normalized,
        "severity_weight": SEVERITY_WEIGHT,
        "severity_contribution": severity_normalized * SEVERITY_WEIGHT,
        "urgency_normalized": urgency_normalized,
        "urgency_weight": URGENCY_WEIGHT,
        "urgency_contribution": urgency_normalized * URGENCY_WEIGHT,
        "magnitude_normalized": magnitude_normalized,
        "magnitude_weight": MAGNITUDE_WEIGHT,
        "magnitude_contribution": magnitude_normalized * MAGNITUDE_WEIGHT,
        "amount_at_risk": str(amount_at_risk),
        "monthly_obligations": str(monthly_obligations),
        "raw_score_before_confidence": raw_score,
        "confidence": confidence_clamped,
        "final_score": score,
    }

    return RiskScore(score=score, breakdown=breakdown)
