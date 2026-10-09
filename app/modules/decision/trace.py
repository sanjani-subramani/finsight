"""Decision Trace builder — the explainability engine.

Every number FinSentinel puts in front of a user (in a headline, a body,
or a recommended action) must be traceable back to a concrete computation
step. This module builds that trace and validates the "no unsupported
number" invariant before an intervention is ever persisted or shown.

Statements are TEMPLATE-BASED with real values substituted — no LLM here.
The trace itself must be fully deterministic and re-derivable from the
same inputs; Step 12 may later add an LLM narrator that READS a trace and
turns it into prose, but it never WRITES one.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from app.contracts.events import ContextualIntervention, TraceStep

# The exact order every trace must follow — this is what makes traces
# comparable across interventions and lets a UI render a consistent
# step-by-step "why" timeline regardless of which stages a given
# intervention actually needed.
TRACE_STAGE_ORDER: tuple[str, ...] = (
    "event",
    "state_change",
    "simulation",
    "rule_findings",
    "collision",
    "risk_score",
    "gate_stage_1",
    "gate_stage_2",
    "gate_stage_3",
    "gate_stage_4",
    "arbitration",
    "recommendation",
)

# Matches integers and decimals, including negatives and comma thousands
# separators (e.g. "-15,000.50"), so we can pull every literal number out
# of free-text headline/body/label strings for the completeness check.
_NUMBER_PATTERN = re.compile(r"-?\d[\d,]*(?:\.\d+)?")

# An embedded calendar date ("...due on 2026-09-19...", common in
# obligation/collision statements) is NOT an asserted figure needing its
# own trace support -- it's calendar context, already fully legible as
# plain text. Without stripping it first, _NUMBER_PATTERN misreads the
# hyphens as unary minus signs and splits it into three spurious
# "numbers" (2026, -9, -19), none of which any TraceStep could ever
# plausibly carry, permanently false-failing any intervention whose text
# happens to mention a date.
_ISO_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


class TraceBuilder:
    """Accumulates TraceStep entries in TRACE_STAGE_ORDER order.

    add() enforces the ordering: a stage may only be added at or after
    the furthest stage already added (stages may be skipped — not every
    intervention has a collision — but never added out of order or
    repeated).
    """

    def __init__(self) -> None:
        self._steps: list[TraceStep] = []
        self._furthest_stage_index = -1

    def add(self, stage: str, statement: str, values: dict[str, Any] | None = None) -> None:
        if stage not in TRACE_STAGE_ORDER:
            raise ValueError(f"Unknown trace stage: {stage!r}")
        stage_index = TRACE_STAGE_ORDER.index(stage)
        if stage_index <= self._furthest_stage_index and self._steps and self._steps[-1].stage == stage:
            # Same stage added twice in a row is almost certainly a bug
            # (e.g. calling add("rule_findings", ...) once per finding
            # without realising it) — every stage in TRACE_STAGE_ORDER is
            # meant to be a single trace entry.
            raise ValueError(f"Trace stage {stage!r} was already added")
        if stage_index < self._furthest_stage_index:
            raise ValueError(
                f"Trace stage {stage!r} is out of order (already past it in TRACE_STAGE_ORDER)"
            )
        self._furthest_stage_index = stage_index
        self._steps.append(
            TraceStep(order=len(self._steps), stage=stage, statement=statement, values=values or {})
        )

    def build(self) -> list[TraceStep]:
        return list(self._steps)


def _numbers_in_text(text: str) -> set[Decimal]:
    found: set[Decimal] = set()
    text = _ISO_DATE_PATTERN.sub(" ", text)
    for match in _NUMBER_PATTERN.findall(text):
        try:
            found.add(Decimal(match.replace(",", "")))
        except InvalidOperation:
            continue
    return found


def _numbers_in_values(values: dict[str, Any]) -> set[Decimal]:
    # Comparison is numeric (via Decimal), not string-based: 15000,
    # 15000.0 and "15,000.00" from different steps/types must all be
    # recognised as the same supporting number. Percentages are the one
    # place this needs a deliberate convention: if a headline says "41%",
    # the supporting TraceStep.values entry must record the number AS
    # DISPLAYED (41), not the raw 0-1 fraction (0.41) — those are not the
    # same number, and no amount of type coercion makes them match.
    found: set[Decimal] = set()
    for value in values.values():
        if isinstance(value, bool):
            continue  # bool is a subclass of int; not a "number" in this sense
        if isinstance(value, Decimal):
            found.add(value)
        elif isinstance(value, (int, float)):
            found.add(Decimal(str(value)))
        elif isinstance(value, str):
            found |= _numbers_in_text(value)
    return found


def validate_trace_completeness(trace: list[TraceStep], intervention: ContextualIntervention) -> None:
    """Raises ValueError if any number in the headline, body, or a
    recommended action's label/amount does not appear in at least one
    TraceStep.values entry.

    This is what prevents the system from asserting a number it cannot
    justify, and it is what makes "why 41%?" mechanically answerable —
    every figure a user sees must be traceable to a concrete computation
    recorded in the trace, not just prose that happens to mention it.
    """
    supported: set[Decimal] = set()
    for step in trace:
        supported |= _numbers_in_values(step.values)

    unsupported: set[Decimal] = set()
    for number in _numbers_in_text(intervention.headline) | _numbers_in_text(intervention.body):
        if number not in supported:
            unsupported.add(number)

    for action in intervention.recommended_actions:
        action_text = action.label + (f" {action.expected_effect}" if action.expected_effect else "")
        for number in _numbers_in_text(action_text):
            if number not in supported:
                unsupported.add(number)
        if action.amount is not None and action.amount not in supported:
            unsupported.add(action.amount)

    if unsupported:
        raise ValueError(
            f"Intervention {intervention.intervention_id} asserts unsupported number(s) "
            f"{sorted(unsupported)} not found in any trace step's values"
        )
