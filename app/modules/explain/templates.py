"""Deterministic fallback narration — genuinely good, not a placeholder.

This is what a real user reads whenever the LLM is unavailable, invalid,
or simply not configured (the common case in this dev environment): per
the Step 12 architectural rule, deleting app.modules.explain entirely
must still leave a fully working product, and this module is what makes
that true. Every value below is read directly out of the trace/
intervention that already passed validate_trace_completeness when the
intervention was created — so a template is grounded by construction,
with nothing left to separately verify.
"""

from __future__ import annotations

from typing import Any

from app.contracts.events import ContextualIntervention, RecommendedAction, TraceStep


def _step_by_stage(trace: list[TraceStep], stage: str) -> TraceStep | None:
    for step in trace:
        if step.stage == stage:
            return step
    return None


def _find_value(step: TraceStep | None, *keys: str) -> Any | None:
    if step is None:
        return None
    for key in keys:
        if key in step.values:
            return step.values[key]
    return None


def classify_intervention_type(trace: list[TraceStep], intervention: ContextualIntervention) -> str:
    """One of: collision, threat, goal_conflict, weather_change,
    safe_to_spend. Best-effort classification from what's actually
    present in the trace -- there is no dedicated "intervention type"
    field on the frozen ContextualIntervention contract.
    """
    if intervention.triggered_by_threat_id is not None:
        return "threat"
    if _step_by_stage(trace, "collision") is not None:
        return "collision"

    rule_findings_step = _step_by_stage(trace, "rule_findings")
    if rule_findings_step is not None:
        for key in rule_findings_step.values:
            if key.startswith("goal_conflicts_obligation.") or key.startswith("goal_at_risk."):
                return "goal_conflict"

    # No dedicated "financial weather changed" trigger exists yet in the
    # pipeline (Steps 7-11 route everything through findings/collisions/
    # threats) -- this branch and its template exist so the type is ready
    # the moment one does, per the spec's explicit template list.
    if intervention.headline.upper().startswith("WEATHER"):
        return "weather_change"

    return "safe_to_spend"


def _recommendation_sentence(intervention: ContextualIntervention) -> str:
    if not intervention.recommended_actions:
        return ""
    action: RecommendedAction = intervention.recommended_actions[0]
    sentence = action.label.rstrip(".") + "."
    if action.expected_effect:
        sentence += f" {action.expected_effect}"
    return sentence


def _collision_amplification_sentence(trace: list[TraceStep]) -> str:
    collision_step = _step_by_stage(trace, "collision")
    joint_pct = _find_value(collision_step, "joint_probability_pct")
    baseline_pct = _find_value(collision_step, "baseline_probability_pct")
    if joint_pct is None or baseline_pct is None:
        return ""
    return f"Together, these factors raised your shortfall risk from {baseline_pct}% to {joint_pct}%."


def _render_collision(trace: list[TraceStep], intervention: ContextualIntervention) -> str:
    parts = [
        intervention.body,
        _collision_amplification_sentence(trace),
        _recommendation_sentence(intervention),
    ]
    return " ".join(p for p in parts if p)


def _render_threat(trace: list[TraceStep], intervention: ContextualIntervention) -> str:
    parts = [
        "A message you reported was flagged as a likely scam.",
        intervention.body,
        _recommendation_sentence(intervention),
    ]
    return " ".join(p for p in parts if p)


def _render_goal_conflict(trace: list[TraceStep], intervention: ContextualIntervention) -> str:
    parts = [
        "One of your savings goals is in tension with an upcoming obligation.",
        intervention.body,
        _recommendation_sentence(intervention),
    ]
    return " ".join(p for p in parts if p)


def _render_weather_change(trace: list[TraceStep], intervention: ContextualIntervention) -> str:
    parts = [
        "Your overall financial outlook has shifted.",
        intervention.body,
        _recommendation_sentence(intervention),
    ]
    return " ".join(p for p in parts if p)


def _render_safe_to_spend(trace: list[TraceStep], intervention: ContextualIntervention) -> str:
    parts = [
        intervention.body,
        _recommendation_sentence(intervention),
    ]
    return " ".join(p for p in parts if p)


_RENDERERS = {
    "collision": _render_collision,
    "threat": _render_threat,
    "goal_conflict": _render_goal_conflict,
    "weather_change": _render_weather_change,
    "safe_to_spend": _render_safe_to_spend,
}


def render_template(trace: list[TraceStep], intervention: ContextualIntervention) -> str:
    intervention_type = classify_intervention_type(trace, intervention)
    renderer = _RENDERERS[intervention_type]
    return renderer(trace, intervention)
