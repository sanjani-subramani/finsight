"""Extraction and validation — the anti-hallucination safety layer.

app.modules.explain.narrator's LLM output is NEVER trusted on its own
merit. Every number, currency amount, percentage, and date it produces is
checked here against GroundedFacts — extracted directly from the
deterministic decision trace BEFORE the LLM ever runs. A number the LLM
invents cannot reach the user: if validate_narration finds even one
unsupported value or forbidden claim, the narrator discards the entire
output and falls back to the deterministic template (see narrator.py). We
do not partially trust or "repair" LLM prose — the check is binary.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from app.contracts.events import ContextualIntervention, TraceStep

# One combined pattern, not three separate scans: Python's alternation
# tries "currency", then "percent", then "isodate", then "number" AT EACH
# POSITION and commits to the first one that matches there, advancing
# past the whole match before continuing. That ordering is what keeps a
# token like "Rs.15,000" or "41%" from ALSO being counted a second time
# as a bare number by the (later, more permissive) "number" alternative.
_TOKEN_PATTERN = re.compile(
    r"(?P<currency>(?:₹|rs\.?|inr)\s?-?\d[\d,]*(?:\.\d+)?)"
    r"|(?P<percent>-?\d+(?:\.\d+)?\s*%)"
    r"|(?P<isodate>\d{4}-\d{2}-\d{2})"
    r"|(?P<number>-?\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_DIGITS_PATTERN = re.compile(r"-?\d[\d,]*(?:\.\d+)?")

# Guarantees, advice-beyond-the-trace, and product/institution
# recommendations — the three forbidden claim categories from the spec.
# This is necessarily a heuristic, not a semantic understanding of the
# text; it is intentionally conservative (a few false positives are a far
# cheaper mistake than one missed guarantee-style claim reaching a user).
FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("guarantee_you_will", re.compile(r"\byou will\b", re.IGNORECASE)),
    ("guarantee_guaranteed", re.compile(r"\bguarantee(s|d)?\b", re.IGNORECASE)),
    ("guarantee_definitely", re.compile(r"\bdefinitely\b", re.IGNORECASE)),
    ("guarantee_certainly", re.compile(r"\bcertainly\b", re.IGNORECASE)),
    ("guarantee_for_sure", re.compile(r"\bfor sure\b", re.IGNORECASE)),
    (
        "advice_beyond_trace",
        re.compile(r"\byou should (invest|buy|purchase|open|switch to|sell)\b", re.IGNORECASE),
    ),
    (
        "product_or_institution_recommendation",
        re.compile(
            r"\b(we recommend|i recommend|try)\s+(the\s+)?[\w\s]{0,30}"
            r"(fund|policy|plan|scheme|card|account|bank|broker)\b",
            re.IGNORECASE,
        ),
    ),
)


@dataclass(frozen=True)
class GroundedFacts:
    """A normalised, searchable set of every number/date/entity/action
    that legitimately appears in a decision trace + intervention. Includes
    BOTH raw and percentage-scaled forms of any fraction/whole-number
    found, so validation can accept "41%" against a trace value stored as
    either 41 or 0.41 without caring which representation the trace used.
    """

    numbers: set[Decimal] = field(default_factory=set)
    amounts: set[Decimal] = field(default_factory=set)
    dates: set[str] = field(default_factory=set)
    entities: set[str] = field(default_factory=set)
    actions: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    violations: list[str] = field(default_factory=list)


def _add_number(numbers: set[Decimal], value: Decimal) -> None:
    numbers.add(value)
    # A percentage can legitimately be written either way in the trace
    # (e.g. "shortfall_probability_pct": 41 vs breakdown["probability"]:
    # 0.41) — pre-computing both directions here means validation later
    # never has to guess which one a given trace step used.
    if 0 <= value <= 1:
        numbers.add((value * 100).quantize(Decimal("0.01")))
    if 0 <= value <= 100:
        numbers.add((value / 100).quantize(Decimal("0.0001")))


def _ingest_scalar(facts_numbers: set[Decimal], facts_amounts: set[Decimal], key: str, value: object) -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float, Decimal)):
        try:
            decimal_value = Decimal(str(value))
        except InvalidOperation:
            return
        _add_number(facts_numbers, decimal_value)
        lowered_key = key.lower()
        if "amount" in lowered_key or "cash" in lowered_key or "obligation" in lowered_key or "balance" in lowered_key:
            facts_amounts.add(decimal_value)


def _ingest_text(facts_numbers: set[Decimal], entities: set[str], text: str) -> None:
    for match in _DIGITS_PATTERN.findall(text):
        try:
            _add_number(facts_numbers, Decimal(match.replace(",", "")))
        except InvalidOperation:
            continue
    stripped = text.strip()
    if stripped and not _DIGITS_PATTERN.fullmatch(stripped):
        entities.add(stripped)


def extract_facts(trace: list[TraceStep], intervention: ContextualIntervention) -> GroundedFacts:
    numbers: set[Decimal] = set()
    amounts: set[Decimal] = set()
    dates: set[str] = set()
    entities: set[str] = set()
    actions: set[str] = set()

    for step in trace:
        entities.add(step.stage)
        _ingest_text(numbers, entities, step.statement)
        for key, value in step.values.items():
            if isinstance(value, str):
                _ingest_text(numbers, entities, value)
                # A raw ISO date string stored as a value (e.g. a due_date)
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    dates.add(value)
            elif isinstance(value, (list, dict)):
                continue  # nested structures (e.g. collision.evidence["findings"]) -- not scanned; see module note
            else:
                _ingest_scalar(numbers, amounts, key, value)

    for action in intervention.recommended_actions:
        actions.add(action.action_type)
        _ingest_text(numbers, entities, action.label)
        if action.expected_effect:
            _ingest_text(numbers, entities, action.expected_effect)
        if action.amount is not None:
            amounts.add(action.amount)
            _add_number(numbers, action.amount)
        if action.projected_risk_after is not None:
            _add_number(numbers, Decimal(str(action.projected_risk_after)))

    _ingest_text(numbers, entities, intervention.headline)
    _ingest_text(numbers, entities, intervention.body)

    return GroundedFacts(numbers=numbers, amounts=amounts, dates=dates, entities=entities, actions=actions)


def validate_narration(narration: str, facts: GroundedFacts) -> ValidationResult:
    violations: list[str] = []
    supported = facts.numbers | facts.amounts

    for match in _TOKEN_PATTERN.finditer(narration):
        kind = match.lastgroup
        raw = match.group(0)

        if kind == "isodate":
            if raw not in facts.dates:
                violations.append(f"Unsupported date: {raw!r}")
            continue

        if kind == "currency":
            digits_match = _DIGITS_PATTERN.search(raw)
            if digits_match is None:
                continue
            digits = digits_match.group(0)
        elif kind == "percent":
            digits = raw.rstrip("% ").strip()
        else:  # bare number
            digits = raw

        try:
            value = Decimal(digits.replace(",", ""))
        except InvalidOperation:
            continue

        # Accept small formatting variance: a percentage written as "41%"
        # matches a trace value stored as either 41 or 0.41 — both forms
        # were pre-computed into `supported` by extract_facts, so a single
        # membership check covers both directions without extra logic here.
        if value not in supported:
            violations.append(f"Unsupported {kind}: {raw!r}")

    for name, pattern in FORBIDDEN_PATTERNS:
        if pattern.search(narration):
            violations.append(f"Forbidden claim pattern ({name}): matched {pattern.pattern!r}")

    return ValidationResult(valid=not violations, violations=violations)
