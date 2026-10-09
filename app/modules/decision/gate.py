"""The Intervention Gate — decides whether FinSentinel interrupts the
user, and at what severity. Fully deterministic: same GateInput always
produces the same GateDecision, no randomness, no I/O, no LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.contracts.events import Severity
from app.platform.config import Settings, get_settings

# Stage 1 weights — mirrors app.modules.risk.scoring's weighting
# philosophy (probability dominates, severity/urgency/magnitude share the
# rest) but is an intentionally separate formula: the Gate decides
# whether to interrupt the user at all, which is a different question
# from how risk.scoring ranks findings against each other.
PROBABILITY_WEIGHT = 0.35
SEVERITY_WEIGHT = 0.25
URGENCY_WEIGHT = 0.20
MAGNITUDE_WEIGHT = 0.20

# Base severity thresholds. Justification for each cutoff:
# CRITICAL (>=0.70): the weighted score is dominated by probability
# (0.35 weight) and severity (0.25) — reaching 0.70 essentially requires
# both a high shortfall probability AND a high-severity finding at once,
# which is exactly the "this will very likely hurt, and hurt badly" case
# that must interrupt the user regardless of what else is going on.
BASE_SEVERITY_CRITICAL_THRESHOLD = 0.70
# NOTIFY (>=0.45): roughly "more likely than not to matter" — worth a
# proactive nudge, but not alarming enough to justify breaking through
# fatigue damping or a low confidence ceiling.
BASE_SEVERITY_NOTIFY_THRESHOLD = 0.45
# MONITOR (>=0.20): below the bar for interrupting the user at all, but
# above pure noise — worth quietly tracking (visible in-app, never
# pushed) in case it compounds with something else later.
BASE_SEVERITY_MONITOR_THRESHOLD = 0.20

# Fatigue damping: 3+ interventions in a rolling 24h window is the point
# where a real user starts to experience the product as "nagging" rather
# than "helpful" — alert fatigue causes people to mute or uninstall,
# which permanently silences even the alerts that matter. One demoted
# MONITOR-worthy NOTIFY is a far cheaper mistake than that.
FATIGUE_INTERVENTION_COUNT_THRESHOLD = 3

# User-tolerance adjustment thresholds, stated directly in the spec.
CONSERVATIVE_PROMOTE_PROBABILITY_THRESHOLD = 0.30
AGGRESSIVE_DEMOTE_PROBABILITY_THRESHOLD = 0.40

_SEVERITY_RANK: dict[Severity, int] = {
    Severity.ignore: 0,
    Severity.monitor: 1,
    Severity.notify: 2,
    Severity.critical: 3,
}


@dataclass(frozen=True)
class GateInput:
    probability: float
    severity_signal: float  # 0-1, e.g. risk.scoring's severity_normalized
    urgency_score: float  # 0-1
    data_confidence: float  # 0-1
    financial_magnitude: float  # 0-1, e.g. risk.scoring's magnitude_normalized
    user_risk_tolerance: str  # "conservative" | "balanced" | "aggressive"
    recent_intervention_count: int  # interventions fired for this user in the last 24h
    hours_since_last_intervention: float | None  # carried through for trace context / future use


@dataclass(frozen=True)
class GateDecision:
    severity: Severity
    severity_raw: Severity  # Stage 1 result, before any ceiling/damping/tolerance adjustment
    confidence_ceiling_applied: bool
    fatigue_damped: bool
    tolerance_adjusted: bool
    base_score: float
    stage_results: list[dict[str, Any]] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)


def _base_severity(base_score: float) -> Severity:
    if base_score >= BASE_SEVERITY_CRITICAL_THRESHOLD:
        return Severity.critical
    if base_score >= BASE_SEVERITY_NOTIFY_THRESHOLD:
        return Severity.notify
    if base_score >= BASE_SEVERITY_MONITOR_THRESHOLD:
        return Severity.monitor
    return Severity.ignore


def _cap(severity: Severity, cap: Severity) -> Severity:
    return severity if _SEVERITY_RANK[severity] <= _SEVERITY_RANK[cap] else cap


def evaluate_gate(inp: GateInput, settings: Settings | None = None) -> GateDecision:
    settings = settings or get_settings()
    stage_results: list[dict[str, Any]] = []
    reasoning: list[str] = []

    # --- Stage 1: base severity from a weighted score -----------------
    base_score = (
        inp.probability * PROBABILITY_WEIGHT
        + inp.severity_signal * SEVERITY_WEIGHT
        + inp.urgency_score * URGENCY_WEIGHT
        + inp.financial_magnitude * MAGNITUDE_WEIGHT
    )
    severity = _base_severity(base_score)
    severity_raw = severity
    stage_results.append({"stage": "base_severity", "severity": severity.value, "base_score": base_score})
    reasoning.append(
        f"Base score {base_score:.3f} (probability={inp.probability:.2f}, "
        f"severity_signal={inp.severity_signal:.2f}, urgency={inp.urgency_score:.2f}, "
        f"magnitude={inp.financial_magnitude:.2f}) classified as {severity.value.upper()}."
    )

    # --- Stage 2: CONFIDENCE CEILING (Innovation 4) --------------------
    # We must NEVER scream CRITICAL — or even NOTIFY — on data we do not
    # trust. Low data_confidence means the underlying events could be
    # wrong, duplicated, or stale; acting loudly on that is worse than
    # not acting at all, because a wrong "act now" destroys user trust
    # permanently. Uncertain data earns "I am watching this" (MONITOR),
    # never "act now" (NOTIFY/CRITICAL). This is a CEILING, not a
    # demotion of severity's own reasoning — Stage 1's severity_raw is
    # preserved untouched precisely so the ceiling's effect is visible
    # and auditable, not silently baked in.
    confidence_ceiling_applied = False
    if inp.data_confidence < settings.CONFIDENCE_CEILING_NOTIFY:
        capped = _cap(severity, Severity.monitor)
        if capped != severity:
            confidence_ceiling_applied = True
        severity = capped
        reasoning.append(
            f"Data confidence {inp.data_confidence:.2f} is below the MONITOR ceiling "
            f"({settings.CONFIDENCE_CEILING_NOTIFY:.2f}); severity capped at MONITOR."
        )
    elif inp.data_confidence < settings.CONFIDENCE_CEILING_CRITICAL:
        capped = _cap(severity, Severity.notify)
        if capped != severity:
            confidence_ceiling_applied = True
        severity = capped
        reasoning.append(
            f"Data confidence {inp.data_confidence:.2f} is below the CRITICAL ceiling "
            f"({settings.CONFIDENCE_CEILING_CRITICAL:.2f}); severity capped at NOTIFY."
        )
    else:
        reasoning.append(f"Data confidence {inp.data_confidence:.2f} clears the CRITICAL ceiling; no cap applied.")
    stage_results.append(
        {
            "stage": "confidence_ceiling",
            "severity": severity.value,
            "confidence_ceiling_applied": confidence_ceiling_applied,
        }
    )

    # --- Stage 3: FATIGUE DAMPING --------------------------------------
    # CRITICAL is never demoted here, on purpose: a genuine emergency
    # must always reach the user no matter how many notifications came
    # before it. Only NOTIFY gets damped to MONITOR, because repeated
    # interruptions for merely "worth a nudge" findings are exactly what
    # trains a user to swipe the notification away unread — alert fatigue
    # makes people mute the product entirely, which silences every future
    # alert including the ones that matter. Losing one medium-severity
    # notification is a far cheaper mistake than losing the channel.
    fatigue_damped = False
    if severity == Severity.notify and inp.recent_intervention_count >= FATIGUE_INTERVENTION_COUNT_THRESHOLD:
        severity = Severity.monitor
        fatigue_damped = True
        reasoning.append(
            f"{inp.recent_intervention_count} interventions already fired in the last 24h "
            f"(>= {FATIGUE_INTERVENTION_COUNT_THRESHOLD}); NOTIFY damped to MONITOR to avoid alert fatigue."
        )
    else:
        reasoning.append(
            f"{inp.recent_intervention_count} interventions in the last 24h; no fatigue damping applied."
        )
    stage_results.append({"stage": "fatigue_damping", "severity": severity.value, "fatigue_damped": fatigue_damped})

    # --- Stage 4: USER TOLERANCE ---------------------------------------
    tolerance_adjusted = False
    if (
        inp.user_risk_tolerance == "conservative"
        and severity == Severity.monitor
        and inp.probability >= CONSERVATIVE_PROMOTE_PROBABILITY_THRESHOLD
    ):
        severity = Severity.notify
        tolerance_adjusted = True
        reasoning.append(
            f"Conservative user tolerance: probability {inp.probability:.2f} >= "
            f"{CONSERVATIVE_PROMOTE_PROBABILITY_THRESHOLD:.2f}; MONITOR promoted to NOTIFY."
        )
    elif (
        inp.user_risk_tolerance == "aggressive"
        and severity == Severity.notify
        and inp.probability < AGGRESSIVE_DEMOTE_PROBABILITY_THRESHOLD
    ):
        severity = Severity.monitor
        tolerance_adjusted = True
        reasoning.append(
            f"Aggressive user tolerance: probability {inp.probability:.2f} < "
            f"{AGGRESSIVE_DEMOTE_PROBABILITY_THRESHOLD:.2f}; NOTIFY demoted to MONITOR."
        )
    else:
        reasoning.append(f"User tolerance '{inp.user_risk_tolerance}': no adjustment applied.")
    stage_results.append({"stage": "user_tolerance", "severity": severity.value, "tolerance_adjusted": tolerance_adjusted})

    return GateDecision(
        severity=severity,
        severity_raw=severity_raw,
        confidence_ceiling_applied=confidence_ceiling_applied,
        fatigue_damped=fatigue_damped,
        tolerance_adjusted=tolerance_adjusted,
        base_score=base_score,
        stage_results=stage_results,
        reasoning=reasoning,
    )
