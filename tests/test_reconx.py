from __future__ import annotations

import csv
import io
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.contracts.events import ReconStatus, TxnStage
from app.models.tables import TransactionEvent as TransactionEventRow
from app.modules.org.reconx.classifier import classify_mismatch, find_duplicates
from app.modules.org.reconx.engine import run_reconciliation
from app.modules.org.reconx.ingest import ReconRecord, normalize_ref
from app.modules.org.reconx.matcher import MatchConfig, match_records
from app.modules.org.reconx.service import ReconService

_BASE = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _rec(
    source: str,
    ref: str,
    amount: str,
    occurred_at: datetime = _BASE,
    *,
    raw_fields: dict | None = None,
) -> ReconRecord:
    return ReconRecord(
        source=source,  # type: ignore[arg-type]
        transaction_ref=ref,
        amount=Decimal(amount),
        occurred_at=occurred_at,
        raw_fields=raw_fields or {},
    )


# ---------------------------------------------------------------------------
# Ref normalization
# ---------------------------------------------------------------------------


def test_ref_normalization_strips_prefix_and_suffix():
    assert normalize_ref("ACME-TX8921-0112") == "TX8921"
    assert normalize_ref("TX8921") == "TX8921"


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_exact_ref_match_across_all_three_sources():
    internal = [_rec("internal", "TX8921", "1000.00")]
    gateway = [_rec("gateway", "TX8921", "1000.00")]
    bank = [_rec("bank", "TX8921", "1000.00")]

    result = await match_records(internal, gateway, bank)

    assert len(result.matches) == 1
    match = result.matches[0]
    assert match.method == "exact"
    assert match.confidence == 0.95
    assert {r.source for r in match.records} == {"internal", "gateway", "bank"}


@pytest.mark.asyncio
async def test_reformatted_ref_matches_via_partial_ref():
    # No separator between the merchant prefix and the core ref, unlike
    # "ACME-TX8921-0112" (which normalize_ref collapses to "TX8921" on its
    # own, via the hyphen split) -- this is the case partial (substring)
    # matching exists for: normalization alone can't isolate "TX8921" out
    # of "ACMETX8921REF" without a separator to split on.
    internal = [_rec("internal", "ACMETX8921REF", "1000.00", _BASE)]
    gateway = [_rec("gateway", "TX8921", "1000.00", _BASE + timedelta(hours=1))]

    result = await match_records(internal, gateway, [])

    assert len(result.matches) == 1
    match = result.matches[0]
    assert match.method == "partial"
    assert match.confidence == 0.80


@pytest.mark.asyncio
async def test_same_amount_same_day_unique_is_a_heuristic_match():
    # Refs share nothing in common (no substring relationship) so pass 2
    # can't find them; only amount + date can.
    internal = [_rec("internal", "ZZZ111", "777.00", _BASE)]
    gateway = [_rec("gateway", "QQQ999", "777.00", _BASE + timedelta(hours=2))]

    result = await match_records(internal, gateway, [])

    assert len(result.matches) == 1
    match = result.matches[0]
    assert match.method == "heuristic"
    assert match.confidence == 0.60


@pytest.mark.asyncio
async def test_two_candidates_at_same_amount_and_date_are_never_guessed():
    internal = [_rec("internal", "ZZZ111", "777.00", _BASE)]
    gateway = [
        _rec("gateway", "QQQ999", "777.00", _BASE + timedelta(hours=1)),
        _rec("gateway", "RRR888", "777.00", _BASE + timedelta(hours=2)),
    ]

    result = await match_records(internal, gateway, [])

    assert result.matches == []
    assert len(result.ambiguous) == 3  # the internal record + both candidates


@pytest.mark.asyncio
async def test_amount_within_one_percent_matches_five_percent_does_not():
    config = MatchConfig()
    internal_close = [_rec("internal", "AAA111", "1000.00", _BASE)]
    gateway_close = [_rec("gateway", "AAA111", "1005.00", _BASE)]  # 0.5% off, within 1%

    close_result = await match_records(internal_close, gateway_close, [], config)
    assert len(close_result.matches) == 1  # exact ref pass matches regardless of amount

    # Pass-2/3 rely on amount tolerance directly when refs don't align --
    # verify the tolerance check itself using a non-matching ref pair.
    far_internal = [_rec("internal", "ZZZ222", "1000.00", _BASE)]
    far_gateway = [_rec("gateway", "YYY333", "1050.00", _BASE)]  # 5% off
    far_result = await match_records(far_internal, far_gateway, [], config)
    assert far_result.matches == []
    assert far_result.unmatched["internal"] == far_internal
    assert far_result.unmatched["gateway"] == far_gateway


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_present_in_internal_and_gateway_not_bank_is_missing_in_bank():
    recent = datetime.now(timezone.utc) - timedelta(hours=2)
    internal = [_rec("internal", "TX500", "500.00", recent)]
    gateway = [_rec("gateway", "TX500", "500.00", recent)]

    result = await match_records(internal, gateway, [])
    assert len(result.matches) == 1
    match = result.matches[0]

    classification = await classify_mismatch(match.records[0], match.records[1:], result)
    assert classification.status == ReconStatus.missing_in_bank


@pytest.mark.asyncio
async def test_present_in_gateway_and_bank_not_internal_is_missing_in_internal():
    gateway = [_rec("gateway", "TX600", "600.00")]
    bank = [_rec("bank", "TX600", "600.00")]

    result = await match_records([], gateway, bank)
    assert len(result.matches) == 1
    match = result.matches[0]

    classification = await classify_mismatch(match.records[0], match.records[1:], result)
    assert classification.status == ReconStatus.missing_in_internal
    assert classification.probable_cause == "manual transaction not entered"


@pytest.mark.asyncio
async def test_missing_in_internal_links_to_paytrace_webhook_lost(db_session):
    org_id = uuid4()
    ref = "TX700"
    now = datetime.now(timezone.utc)

    # Seed PayTrace history for this ref: bank_accepted -> webhook_failed
    # -> settled is the canonical WEBHOOK_LOST pattern (money moved, but
    # the webhook telling the internal system to record it never arrived).
    for stage, offset in [
        (TxnStage.initiated, 0),
        (TxnStage.gateway_accepted, 2),
        (TxnStage.bank_accepted, 5),
        (TxnStage.webhook_failed, 8),
        (TxnStage.settled, 20),
    ]:
        db_session.add(
            TransactionEventRow(
                org_id=org_id,
                transaction_ref=ref,
                stage=stage.value,
                occurred_at=now - timedelta(seconds=60 - offset),
                amount=Decimal("600.00"),
                provider="razorpay",
                idempotency_key=f"{ref}-{stage.value}",
            )
        )
    await db_session.commit()

    gateway = [_rec("gateway", ref, "600.00", now - timedelta(seconds=40))]
    bank = [_rec("bank", ref, "600.00", now - timedelta(seconds=40))]
    match_result = await match_records([], gateway, bank)
    match = match_result.matches[0]

    classification = await classify_mismatch(
        match.records[0], match.records[1:], match_result, session=db_session, org_id=org_id
    )

    assert classification.status == ReconStatus.missing_in_internal
    assert classification.probable_cause == "webhook failure"
    assert any("WEBHOOK_LOST" in e for e in classification.evidence)


@pytest.mark.asyncio
async def test_duplicate_ref_in_one_source_is_flagged():
    config = MatchConfig()
    records = [
        _rec("internal", "TX800", "1200.00", _BASE),
        _rec("internal", "TX800", "1200.00", _BASE + timedelta(minutes=5)),
    ]

    deduped, duplicates = find_duplicates(records, config)

    assert len(deduped) == 1
    assert len(duplicates) == 1
    dup_record, classification = duplicates[0]
    assert dup_record.occurred_at == records[1].occurred_at
    assert classification.status == ReconStatus.duplicate


@pytest.mark.asyncio
async def test_amount_mismatch_by_fifty_on_ten_thousand_is_processing_fee():
    internal = [_rec("internal", "TX900", "10000.00", _BASE)]
    gateway = [_rec("gateway", "TX900", "10000.00", _BASE)]
    bank = [_rec("bank", "TX900", "9950.00", _BASE)]

    result = await match_records(internal, gateway, bank)
    match = result.matches[0]

    classification = await classify_mismatch(match.records[0], match.records[1:], result)

    assert classification.status == ReconStatus.amount_mismatch
    assert classification.probable_cause == "processing fee deducted"


@pytest.mark.asyncio
async def test_dates_differing_by_three_days_is_timing_difference():
    internal = [_rec("internal", "TX950", "300.00", _BASE)]
    gateway = [_rec("gateway", "TX950", "300.00", _BASE)]
    bank = [_rec("bank", "TX950", "300.00", _BASE + timedelta(days=3))]

    result = await match_records(internal, gateway, bank)
    match = result.matches[0]

    classification = await classify_mismatch(match.records[0], match.records[1:], result)

    assert classification.status == ReconStatus.timing_difference


# ---------------------------------------------------------------------------
# Integrity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_summary_counts_equal_detail_row_counts(db_session):
    org_id = uuid4()
    now = datetime.now(timezone.utc) - timedelta(hours=1)

    internal = [_rec("internal", f"TX{i}", "100.00", now) for i in range(20)]
    gateway = [_rec("gateway", f"TX{i}", "100.00", now) for i in range(20)]
    bank = [_rec("bank", f"TX{i}", "100.00", now) for i in range(18)]  # 2 missing in bank

    run_result = await run_reconciliation(db_session, org_id, internal, gateway, bank)

    assert (
        run_result.matched
        + run_result.missing
        + run_result.duplicates
        + run_result.amount_mismatches
        + run_result.timing_differences
        + run_result.unresolved
        == len(run_result.records)
    )
    assert run_result.matched == 18
    assert run_result.missing == 2


@pytest.mark.asyncio
async def test_one_hundred_thousand_records_reconcile_under_ten_seconds(db_session):
    org_id = uuid4()
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    count = 33_334  # ~100,000 records across 3 sources

    internal = [_rec("internal", f"PERF{i}", "50.00", now) for i in range(count)]
    gateway = [_rec("gateway", f"PERF{i}", "50.00", now) for i in range(count)]
    bank = [_rec("bank", f"PERF{i}", "50.00", now) for i in range(count)]

    start = time.perf_counter()
    run_result = await run_reconciliation(db_session, org_id, internal, gateway, bank)
    elapsed = time.perf_counter() - start

    assert run_result.total_records == count * 3
    assert run_result.matched == count
    assert elapsed < 10.0


@pytest.mark.asyncio
async def test_manual_resolution_marks_the_record_and_persists_the_note(db_session):
    org_id = uuid4()
    resolver_id = uuid4()
    now = datetime.now(timezone.utc) - timedelta(hours=1)

    internal = [_rec("internal", "TXR1", "42.00", now)]
    gateway = [_rec("gateway", "TXR1", "42.00", now)]
    run_result = await run_reconciliation(db_session, org_id, internal, gateway, [])

    service = ReconService()
    target = run_result.records[0]
    resolved = await service.resolve_manually(
        db_session, org_id, target.result_id, "Confirmed with bank; settled next cycle.", resolver_id
    )
    assert resolved is not None
    assert resolved.resolved is True
    assert resolved.resolution_note == "Confirmed with bank; settled next cycle."
    assert resolved.resolved_by == resolver_id

    detail = await service.get_run(db_session, org_id, run_result.run_id)
    assert detail is not None
    persisted = next(r for r in detail.results if r.result_id == target.result_id)
    assert persisted.resolved is True
    assert persisted.resolution_note == "Confirmed with bank; settled next cycle."


@pytest.mark.asyncio
async def test_csv_export_contains_every_column(db_session):
    org_id = uuid4()
    now = datetime.now(timezone.utc) - timedelta(hours=1)

    internal = [_rec("internal", "TXE1", "10.00", now)]
    gateway = [_rec("gateway", "TXE1", "10.00", now)]
    bank = [_rec("bank", "TXE1", "10.00", now)]
    run_result = await run_reconciliation(db_session, org_id, internal, gateway, bank)

    service = ReconService()
    csv_text = await service.export_results(db_session, org_id, run_result.run_id, format="csv")

    reader = csv.reader(io.StringIO(csv_text))
    header = next(reader)
    assert set(header) == {
        "result_id",
        "run_id",
        "transaction_ref",
        "status",
        "internal_amount",
        "gateway_amount",
        "bank_amount",
        "probable_cause",
        "cause_confidence",
        "evidence",
        "resolved",
        "resolved_by",
        "resolution_note",
    }
    rows = list(reader)
    assert len(rows) == 1
