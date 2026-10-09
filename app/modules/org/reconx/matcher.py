"""ReconX matching engine — deterministic, configurable, auditable.

Three passes, each looser (and lower-confidence) than the last:
  1. EXACT REF     -- normalized ref matches across sources. The common case.
  2. PARTIAL REF   -- ref substring containment + amount + time window.
  3. HEURISTIC     -- amount + same-day, ONLY when the candidate is
                      unambiguous. A wrong match is worse than no match, so
                      two equally-plausible candidates are left unresolved
                      rather than guessed at.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from app.modules.org.reconx.ingest import ReconRecord, SourceName, normalize_ref

_SOURCES: tuple[SourceName, ...] = ("internal", "gateway", "bank")

MatchMethod = Literal["exact", "partial", "heuristic"]

EXACT_CONFIDENCE = 0.95
PARTIAL_CONFIDENCE = 0.80
HEURISTIC_CONFIDENCE = 0.60
HEURISTIC_WINDOW_HOURS = 24


@dataclass(frozen=True)
class MatchConfig:
    amount_tolerance_pct: float = 0.01
    amount_tolerance_abs: Decimal = Decimal("1.00")
    time_window_hours: int = 72
    ref_similarity_threshold: float = 0.85


@dataclass(frozen=True)
class Match:
    match_id: UUID
    records: list[ReconRecord]
    method: MatchMethod
    confidence: float
    explanation: str


@dataclass(frozen=True)
class MatchResult:
    matches: list[Match]
    # Pass-3 candidates deliberately NOT matched because two or more
    # equally-plausible counterparts existed at the same amount/date.
    ambiguous: list[ReconRecord] = field(default_factory=list)
    unmatched: dict[SourceName, list[ReconRecord]] = field(default_factory=dict)


def amounts_within_tolerance(a: Decimal, b: Decimal, config: MatchConfig) -> bool:
    diff = abs(a - b)
    if diff <= config.amount_tolerance_abs:
        return True
    base = max(abs(a), abs(b))
    if base == 0:
        return diff == 0
    return (diff / base) <= Decimal(str(config.amount_tolerance_pct))


def within_window(a: datetime, b: datetime, hours: int) -> bool:
    return abs(a - b) <= timedelta(hours=hours)


def ref_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def _index_by_ref(records: list[ReconRecord]) -> dict[str, ReconRecord]:
    """Keyed by normalized ref. Assumes the caller has already stripped
    same-source duplicates (see classifier.find_duplicates) -- at most one
    record per normalized ref is expected here. On the rare occasion two
    records still share a ref (e.g. a same-ref-different-amount pair that
    find_duplicates deliberately declined to call a duplicate), the first
    one chronologically wins rather than silently being overwritten.
    """
    index: dict[str, ReconRecord] = {}
    for r in records:
        index.setdefault(normalize_ref(r.transaction_ref), r)
    return index


async def match_records(
    internal: list[ReconRecord],
    gateway: list[ReconRecord],
    bank: list[ReconRecord],
    config: MatchConfig | None = None,
) -> MatchResult:
    config = config or MatchConfig()
    by_source: dict[SourceName, dict[str, ReconRecord]] = {
        "internal": _index_by_ref(internal),
        "gateway": _index_by_ref(gateway),
        "bank": _index_by_ref(bank),
    }

    matches: list[Match] = []
    consumed: dict[SourceName, set[str]] = {src: set() for src in _SOURCES}

    # PASS 1 -- exact normalized ref, present in 2 or more sources.
    all_refs = set(by_source["internal"]) | set(by_source["gateway"]) | set(by_source["bank"])
    for ref in sorted(all_refs):
        present = {src: recs[ref] for src, recs in by_source.items() if ref in recs}
        if len(present) >= 2:
            matches.append(
                Match(
                    match_id=uuid4(),
                    records=list(present.values()),
                    method="exact",
                    confidence=EXACT_CONFIDENCE,
                    explanation=f"Normalized ref '{ref}' matched exactly across {', '.join(sorted(present))}.",
                )
            )
            for src in present:
                consumed[src].add(ref)

    leftover: dict[SourceName, list[ReconRecord]] = {
        src: [rec for ref, rec in recs.items() if ref not in consumed[src]] for src, recs in by_source.items()
    }

    partial_matches, leftover = _match_partial(leftover, config)
    matches.extend(partial_matches)

    heuristic_matches, leftover, ambiguous = _match_heuristic(leftover, config)
    matches.extend(heuristic_matches)

    return MatchResult(matches=matches, ambiguous=ambiguous, unmatched=leftover)


def _match_partial(
    leftover: dict[SourceName, list[ReconRecord]], config: MatchConfig
) -> tuple[list[Match], dict[SourceName, list[ReconRecord]]]:
    def linked(a: ReconRecord, b: ReconRecord) -> bool:
        ref_a, ref_b = normalize_ref(a.transaction_ref), normalize_ref(b.transaction_ref)
        if not (ref_a in ref_b or ref_b in ref_a):
            return False
        if not amounts_within_tolerance(a.amount, b.amount, config):
            return False
        return within_window(a.occurred_at, b.occurred_at, config.time_window_hours)

    pools = {src: list(recs) for src, recs in leftover.items()}
    matches: list[Match] = []

    for i, src_a in enumerate(_SOURCES):
        for src_b in _SOURCES[i + 1 :]:
            still_a: list[ReconRecord] = []
            for rec_a in pools[src_a]:
                partner_idx = next((idx for idx, rec_b in enumerate(pools[src_b]) if linked(rec_a, rec_b)), None)
                if partner_idx is None:
                    still_a.append(rec_a)
                    continue
                rec_b = pools[src_b].pop(partner_idx)
                matches.append(
                    Match(
                        match_id=uuid4(),
                        records=[rec_a, rec_b],
                        method="partial",
                        confidence=PARTIAL_CONFIDENCE,
                        explanation=(
                            f"{src_a} ref '{rec_a.transaction_ref}' and {src_b} ref '{rec_b.transaction_ref}' "
                            "share a common ref substring, matching amount, and occur within the settlement "
                            "window."
                        ),
                    )
                )
            pools[src_a] = still_a

    return matches, dict(pools)


def _match_heuristic(
    leftover: dict[SourceName, list[ReconRecord]], config: MatchConfig
) -> tuple[list[Match], dict[SourceName, list[ReconRecord]], list[ReconRecord]]:
    def linked(a: ReconRecord, b: ReconRecord) -> bool:
        if not amounts_within_tolerance(a.amount, b.amount, config):
            return False
        return within_window(a.occurred_at, b.occurred_at, HEURISTIC_WINDOW_HOURS)

    pools = {src: list(recs) for src, recs in leftover.items()}
    matches: list[Match] = []
    ambiguous: list[ReconRecord] = []
    ambiguous_ids: set[int] = set()

    def _mark_ambiguous(rec: ReconRecord) -> None:
        if id(rec) not in ambiguous_ids:
            ambiguous_ids.add(id(rec))
            ambiguous.append(rec)

    for i, src_a in enumerate(_SOURCES):
        for src_b in _SOURCES[i + 1 :]:
            still_a: list[ReconRecord] = []
            for rec_a in pools[src_a]:
                candidates = [idx for idx, rec_b in enumerate(pools[src_b]) if linked(rec_a, rec_b)]
                if not candidates:
                    still_a.append(rec_a)
                elif len(candidates) == 1:
                    rec_b = pools[src_b].pop(candidates[0])
                    matches.append(
                        Match(
                            match_id=uuid4(),
                            records=[rec_a, rec_b],
                            method="heuristic",
                            confidence=HEURISTIC_CONFIDENCE,
                            explanation=(
                                f"{src_a} ref '{rec_a.transaction_ref}' and {src_b} ref '{rec_b.transaction_ref}' "
                                "share the same amount and date, and are each other's only candidate."
                            ),
                        )
                    )
                else:
                    _mark_ambiguous(rec_a)
                    for idx in candidates:
                        _mark_ambiguous(pools[src_b][idx])
                    still_a.append(rec_a)
            pools[src_a] = still_a

    return matches, dict(pools), ambiguous
