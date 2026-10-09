"""ReconX run orchestrator -- ties ingestion, matching, and classification
together into one persisted reconciliation run.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ReconciliationResult, ReconStatus
from app.models.tables import ReconResult as ReconResultRow
from app.models.tables import ReconRun as ReconRunRow
from app.modules.org.reconx.classifier import MismatchClassification, classify_mismatch, find_duplicates
from app.modules.org.reconx.ingest import ReconRecord
from app.modules.org.reconx.matcher import MatchConfig, MatchResult, match_records

_SOURCE_PRIORITY: dict[str, int] = {"internal": 0, "gateway": 1, "bank": 2}

_STATUS_COUNTER_KEYS: dict[ReconStatus, str] = {
    ReconStatus.matched: "matched",
    ReconStatus.missing_in_bank: "missing_in_bank",
    ReconStatus.missing_in_gateway: "missing_in_gateway",
    ReconStatus.missing_in_internal: "missing_in_internal",
    ReconStatus.duplicate: "duplicates",
    ReconStatus.amount_mismatch: "amount_mismatches",
    ReconStatus.timing_difference: "timing_differences",
    ReconStatus.unresolved: "unresolved",
}


@dataclass(frozen=True)
class ReconRunResult:
    run_id: UUID
    total_records: int
    matched: int
    missing: int
    duplicates: int
    amount_mismatches: int
    timing_differences: int
    unresolved: int
    duration_ms: int
    summary_stats: dict[str, int]
    records: list[ReconciliationResult]


def _order_by_source(records: list[ReconRecord]) -> list[ReconRecord]:
    return sorted(records, key=lambda r: _SOURCE_PRIORITY[r.source])


def _to_reconciliation_result(
    run_id: UUID,
    org_id: UUID,
    record: ReconRecord,
    others: list[ReconRecord],
    classification: MismatchClassification,
) -> ReconciliationResult:
    amounts: dict[str, Decimal] = {record.source: record.amount}
    amounts.update({r.source: r.amount for r in others})
    return ReconciliationResult(
        org_id=org_id,
        run_id=run_id,
        transaction_ref=record.transaction_ref,
        status=classification.status,
        internal_amount=amounts.get("internal"),
        gateway_amount=amounts.get("gateway"),
        bank_amount=amounts.get("bank"),
        probable_cause=classification.probable_cause,
        cause_confidence=classification.cause_confidence,
        evidence=classification.evidence,
    )


async def run_reconciliation(
    session: AsyncSession,
    org_id: UUID,
    internal: list[ReconRecord],
    gateway: list[ReconRecord],
    bank: list[ReconRecord],
    config: MatchConfig | None = None,
    started_by: UUID | None = None,
) -> ReconRunResult:
    config = config or MatchConfig()
    start = time.perf_counter()

    internal_deduped, internal_dupes = find_duplicates(internal, config)
    gateway_deduped, gateway_dupes = find_duplicates(gateway, config)
    bank_deduped, bank_dupes = find_duplicates(bank, config)

    match_result: MatchResult = await match_records(internal_deduped, gateway_deduped, bank_deduped, config)

    run_id = uuid4()
    results: list[ReconciliationResult] = []

    for _record, classification in [*internal_dupes, *gateway_dupes, *bank_dupes]:
        results.append(_to_reconciliation_result(run_id, org_id, _record, [], classification))

    for m in match_result.matches:
        primary, *rest = _order_by_source(m.records)
        classification = await classify_mismatch(
            primary, rest, match_result, config=config, session=session, org_id=org_id
        )
        results.append(_to_reconciliation_result(run_id, org_id, primary, rest, classification))

    for records in match_result.unmatched.values():
        for record in records:
            classification = await classify_mismatch(
                record, [], match_result, config=config, session=session, org_id=org_id
            )
            results.append(_to_reconciliation_result(run_id, org_id, record, [], classification))

    duration_ms = int(round((time.perf_counter() - start) * 1000))

    summary_stats: dict[str, int] = dict.fromkeys(_STATUS_COUNTER_KEYS.values(), 0)
    for r in results:
        summary_stats[_STATUS_COUNTER_KEYS[r.status]] += 1

    total_records = len(internal) + len(gateway) + len(bank)
    # Every number in the summary must be derivable from the detail rows
    # -- this is the entire reason results are persisted per-transaction
    # rather than just a running tally.
    assert sum(summary_stats.values()) == len(results), "summary counts must equal the detail row count"

    missing_total = (
        summary_stats["missing_in_bank"] + summary_stats["missing_in_gateway"] + summary_stats["missing_in_internal"]
    )

    all_times = [r.occurred_at for r in [*internal, *gateway, *bank]]
    now = datetime.now(timezone.utc)
    period_start = min(all_times) if all_times else now
    period_end = max(all_times) if all_times else now

    session.add(
        ReconRunRow(
            id=run_id,
            org_id=org_id,
            started_by=started_by,
            period_start=period_start,
            period_end=period_end,
            total_records=total_records,
            matched=summary_stats["matched"],
            missing=missing_total,
            duplicates=summary_stats["duplicates"],
            amount_mismatch=summary_stats["amount_mismatches"],
            timing_differences=summary_stats["timing_differences"],
            unresolved=summary_stats["unresolved"],
            status="completed",
            duration_ms=duration_ms,
        )
    )
    # AsyncSessionLocal is configured with autoflush=False (see
    # app.platform.database), so the ReconRunRow add() above is NOT
    # visible to the database yet. The bulk INSERT below is a Core
    # statement referencing run_id by raw value, not an ORM relationship
    # -- it does not trigger autoflush the way an ORM query would, so
    # without this explicit flush it races the parent row and fails
    # run_id's foreign key under a real FK-enforcing database. SQLite
    # (used by the rest of this repo's test suite) does not enforce
    # foreign keys by default, which is why this was never caught
    # before a real Postgres run.
    await session.flush()
    # A run can produce tens of thousands of detail rows -- one INSERT
    # per row via the ORM's unit-of-work (session.add_all) is the actual
    # bottleneck at that scale (matching+classification is a fraction of
    # a second even for 100k records; per-row ORM inserts are not). A
    # single bulk INSERT keeps a large run comfortably fast.
    if results:
        await session.execute(
            insert(ReconResultRow),
            [
                {
                    "id": r.result_id,
                    "run_id": run_id,
                    "org_id": org_id,
                    "transaction_ref": r.transaction_ref,
                    "status": r.status.value,
                    "internal_amount": r.internal_amount,
                    "gateway_amount": r.gateway_amount,
                    "bank_amount": r.bank_amount,
                    "probable_cause": r.probable_cause,
                    "cause_confidence": r.cause_confidence,
                    "evidence": r.evidence,
                }
                for r in results
            ],
        )
    await session.flush()

    return ReconRunResult(
        run_id=run_id,
        total_records=total_records,
        matched=summary_stats["matched"],
        missing=missing_total,
        duplicates=summary_stats["duplicates"],
        amount_mismatches=summary_stats["amount_mismatches"],
        timing_differences=summary_stats["timing_differences"],
        unresolved=summary_stats["unresolved"],
        duration_ms=duration_ms,
        summary_stats=summary_stats,
        records=results,
    )
