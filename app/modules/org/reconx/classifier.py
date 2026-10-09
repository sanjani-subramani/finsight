"""Classify every matched group and every leftover record produced by
app.modules.org.reconx.matcher into exactly one ReconStatus, with a
probable cause, confidence, evidence, and recommended action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ReconStatus
from app.modules.org.reconx.ingest import ReconRecord, normalize_ref
from app.modules.org.reconx.matcher import MatchConfig, MatchResult, amounts_within_tolerance, ref_similarity

TIMING_DIFFERENCE_HOURS = 24
# A difference this small (in absolute terms, or as a tiny fraction of the
# amount) looks like currency-conversion rounding rather than a fee.
ROUNDING_DIFF_ABS_THRESHOLD = Decimal("5.00")
ROUNDING_DIFF_RATIO_THRESHOLD = 0.001
# Above rounding but still small enough to be a processing fee; above
# this, it looks more like a partial capture/settlement than a fee.
FEE_DIFF_RATIO_THRESHOLD = 0.05


_RECOMMENDED_ACTIONS: dict[ReconStatus, str] = {
    ReconStatus.matched: "No action needed",
    ReconStatus.missing_in_bank: "Confirm with the bank statement provider; escalate if the settlement window has passed",
    ReconStatus.missing_in_gateway: "Confirm this was a direct bank transfer; no gateway action needed",
    ReconStatus.missing_in_internal: "Backfill the internal ledger entry",
    ReconStatus.duplicate: "Investigate and void the duplicate entry",
    ReconStatus.amount_mismatch: "Reconcile the amount difference against the provider's fee schedule",
    ReconStatus.timing_difference: "No action needed — timing only, amounts agree",
    ReconStatus.unresolved: "Manual review required",
}


@dataclass(frozen=True)
class MismatchClassification:
    status: ReconStatus
    probable_cause: str | None
    cause_confidence: float | None
    evidence: list[str] = field(default_factory=list)
    recommended_action: str | None = None


def find_duplicates(
    records: list[ReconRecord], config: MatchConfig
) -> tuple[list[ReconRecord], list[tuple[ReconRecord, MismatchClassification]]]:
    """Same normalized ref appearing 2+ times in ONE source with matching
    amounts is a DUPLICATE, not a matching problem -- detected and removed
    BEFORE the record pool reaches matcher.match_records (which assumes at
    most one record per normalized ref per source). Returns
    (deduplicated records to match, duplicate records with their
    classification).
    """
    by_ref: dict[str, list[ReconRecord]] = {}
    for r in records:
        by_ref.setdefault(normalize_ref(r.transaction_ref), []).append(r)

    deduped: list[ReconRecord] = []
    duplicates: list[tuple[ReconRecord, MismatchClassification]] = []
    for ref, group in by_ref.items():
        if len(group) == 1:
            deduped.append(group[0])
            continue

        ordered = sorted(group, key=lambda r: r.occurred_at)
        first = ordered[0]
        deduped.append(first)
        for extra in ordered[1:]:
            if not amounts_within_tolerance(first.amount, extra.amount, config):
                # Same ref, different amount -- not confidently a
                # duplicate; let normal matching/AMOUNT_MISMATCH handling
                # deal with it rather than guessing here.
                deduped.append(extra)
                continue
            duplicates.append(
                (
                    extra,
                    MismatchClassification(
                        status=ReconStatus.duplicate,
                        probable_cause=f"Duplicate of the {first.source} record dated {first.occurred_at.isoformat()}",
                        cause_confidence=0.95,
                        evidence=[
                            f"Normalized ref '{ref}' appears {len(group)} times in {first.source}",
                            f"Amounts match within tolerance ({first.amount} vs {extra.amount})",
                        ],
                        recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.duplicate],
                    ),
                )
            )
    return deduped, duplicates


def _is_ambiguous(record: ReconRecord, match_result: MatchResult) -> bool:
    return any(id(record) == id(r) for r in match_result.ambiguous)


async def classify_mismatch(
    record: ReconRecord,
    matched_records: list[ReconRecord],
    match_result: MatchResult,
    *,
    config: MatchConfig | None = None,
    session: AsyncSession | None = None,
    org_id: UUID | None = None,
) -> MismatchClassification:
    """`session`/`org_id` are optional and used only for the PayTrace
    cross-module link on MISSING_IN_INTERNAL; the core status/cause logic
    needs neither.
    """
    config = config or MatchConfig()

    if _is_ambiguous(record, match_result):
        return MismatchClassification(
            status=ReconStatus.unresolved,
            probable_cause="Multiple equally-plausible candidates at the same amount and date",
            cause_confidence=None,
            evidence=[
                f"{len(match_result.ambiguous)} records shared this amount/date across sources; "
                "a wrong match is worse than no match, so none were paired"
            ],
            recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.unresolved],
        )

    present_sources = {record.source} | {m.source for m in matched_records}

    if present_sources == {"internal", "gateway", "bank"}:
        return _classify_present_in_all(record, matched_records, config)
    if present_sources == {"internal", "gateway"}:
        return _classify_missing_in_bank(record, matched_records, match_result, config)
    if present_sources == {"internal", "bank"}:
        return _classify_missing_in_gateway()
    if present_sources == {"gateway", "bank"}:
        return await _classify_missing_in_internal(record, session, org_id)

    return MismatchClassification(
        status=ReconStatus.unresolved,
        probable_cause="No matching record found in any other source",
        cause_confidence=None,
        evidence=[f"Only present in {record.source}"],
        recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.unresolved],
    )


def _amounts_effectively_equal(a: Decimal, b: Decimal, config: MatchConfig) -> bool:
    """A stricter bar than the matcher's amounts_within_tolerance: that
    1%-of-amount tolerance exists so the MATCHER still links two records
    as "the same transaction" despite a fee being deducted along the way
    -- it is NOT license for the classifier to then bury that fee and
    call the group a clean MATCHED. Only genuine rounding (a few rupees,
    per amount_tolerance_abs) is invisible here; anything bigger is a
    reportable AMOUNT_MISMATCH even if the matcher tolerated it.
    """
    return abs(a - b) <= config.amount_tolerance_abs


def _classify_present_in_all(
    record: ReconRecord, matched_records: list[ReconRecord], config: MatchConfig
) -> MismatchClassification:
    all_records = sorted([record, *matched_records], key=lambda r: r.source)
    amounts = {r.source: r.amount for r in all_records}
    highest, lowest = max(amounts.values()), min(amounts.values())

    if not _amounts_effectively_equal(highest, lowest, config):
        diff = highest - lowest
        ratio = float(diff / highest) if highest else 0.0
        if diff <= ROUNDING_DIFF_ABS_THRESHOLD and ratio <= ROUNDING_DIFF_RATIO_THRESHOLD:
            cause = "currency conversion rounding"
        elif ratio <= FEE_DIFF_RATIO_THRESHOLD:
            cause = "processing fee deducted"
        else:
            cause = "partial settlement"
        return MismatchClassification(
            status=ReconStatus.amount_mismatch,
            probable_cause=cause,
            cause_confidence=0.8,
            evidence=[f"{r.source}={r.amount}" for r in all_records],
            recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.amount_mismatch],
        )

    times = [r.occurred_at for r in all_records]
    if max(times) - min(times) > timedelta(hours=TIMING_DIFFERENCE_HOURS):
        return MismatchClassification(
            status=ReconStatus.timing_difference,
            probable_cause="Settlement recorded on a different day across sources",
            cause_confidence=0.85,
            evidence=[f"{r.source}={r.occurred_at.isoformat()}" for r in all_records],
            recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.timing_difference],
        )

    return MismatchClassification(
        status=ReconStatus.matched,
        probable_cause=None,
        cause_confidence=1.0,
        evidence=[f"{r.source}={r.amount}" for r in all_records],
        recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.matched],
    )


def _classify_missing_in_bank(
    record: ReconRecord, matched_records: list[ReconRecord], match_result: MatchResult, config: MatchConfig
) -> MismatchClassification:
    error_code = record.raw_fields.get("error_code") or next(
        (m.raw_fields.get("error_code") for m in matched_records if m.raw_fields.get("error_code")), None
    )
    if error_code:
        return MismatchClassification(
            status=ReconStatus.missing_in_bank,
            probable_cause="bank rejection",
            cause_confidence=0.85,
            evidence=[f"error_code={error_code}"],
            recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.missing_in_bank],
        )

    ref = normalize_ref(record.transaction_ref)
    bank_candidates = match_result.unmatched.get("bank", [])
    if bank_candidates:
        best = max(bank_candidates, key=lambda r: ref_similarity(ref, normalize_ref(r.transaction_ref)))
        score = ref_similarity(ref, normalize_ref(best.transaction_ref))
        if score >= config.ref_similarity_threshold:
            return MismatchClassification(
                status=ReconStatus.missing_in_bank,
                probable_cause="ref formatting mismatch",
                cause_confidence=round(score, 2),
                evidence=[
                    f"bank ref '{best.transaction_ref}' is {score:.0%} similar but fell outside matching criteria"
                ],
                recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.missing_in_bank],
            )

    age = datetime.now(timezone.utc) - record.occurred_at
    if age <= timedelta(hours=config.time_window_hours):
        return MismatchClassification(
            status=ReconStatus.missing_in_bank,
            probable_cause="settlement delay",
            cause_confidence=0.7,
            evidence=[f"Only {age} old; within the {config.time_window_hours}h settlement window"],
            recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.missing_in_bank],
        )

    return MismatchClassification(
        status=ReconStatus.missing_in_bank,
        probable_cause="unexplained bank gap",
        cause_confidence=0.4,
        evidence=[f"{age} old with no bank record, error code, or similar ref found"],
        recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.missing_in_bank],
    )


def _classify_missing_in_gateway() -> MismatchClassification:
    return MismatchClassification(
        status=ReconStatus.missing_in_gateway,
        probable_cause="direct bank transfer bypassing gateway",
        cause_confidence=0.75,
        evidence=["Present in the internal ledger and bank statement, but never seen by any payment gateway"],
        recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.missing_in_gateway],
    )


async def _classify_missing_in_internal(
    record: ReconRecord, session: AsyncSession | None, org_id: UUID | None
) -> MismatchClassification:
    if session is not None and org_id is not None:
        # CROSS-MODULE LINK: PayTrace (Step 14) already reconstructs each
        # transaction's lifecycle from gateway/bank/webhook events. A
        # WEBHOOK_LOST classification there is frequently the exact reason
        # this transaction never reached the internal ledger -- the bank
        # and gateway both saw it succeed, but the webhook telling this
        # org's system to record it never arrived.
        from app.modules.org.paytrace.classifier import FailureMode
        from app.modules.org.paytrace.service import PayTraceService

        detail = await PayTraceService().get_transaction(session, org_id, record.transaction_ref)
        if detail is not None and detail.classification.mode == FailureMode.WEBHOOK_LOST:
            return MismatchClassification(
                status=ReconStatus.missing_in_internal,
                probable_cause="webhook failure",
                cause_confidence=0.9,
                evidence=[
                    "PayTrace classifies this transaction as WEBHOOK_LOST",
                    detail.classification.human_summary,
                ],
                recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.missing_in_internal],
            )

    return MismatchClassification(
        status=ReconStatus.missing_in_internal,
        probable_cause="manual transaction not entered",
        cause_confidence=0.6,
        evidence=["Present in gateway and bank records but no matching internal ledger entry"],
        recommended_action=_RECOMMENDED_ACTIONS[ReconStatus.missing_in_internal],
    )
