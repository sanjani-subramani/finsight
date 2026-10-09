"""ReconService -- the public face of app.modules.org.reconx."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ReconStatus
from app.models.tables import ReconResult as ReconResultRow
from app.models.tables import ReconRun as ReconRunRow
from app.modules.org.reconx.engine import ReconRunResult, run_reconciliation
from app.modules.org.reconx.ingest import ReconRecord
from app.modules.org.reconx.matcher import MatchConfig
from app.platform.timeutils import as_aware_utc

EXPORT_COLUMNS = [
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
]


@dataclass(frozen=True)
class ReconResultDetail:
    result_id: UUID
    run_id: UUID
    transaction_ref: str
    status: ReconStatus
    internal_amount: Decimal | None
    gateway_amount: Decimal | None
    bank_amount: Decimal | None
    probable_cause: str | None
    cause_confidence: float | None
    evidence: list[str] = field(default_factory=list)
    resolved: bool = False
    resolved_by: UUID | None = None
    resolution_note: str | None = None


@dataclass(frozen=True)
class ReconRunSummary:
    run_id: UUID
    period_start: datetime
    period_end: datetime
    total_records: int
    matched: int
    missing: int
    duplicates: int
    amount_mismatches: int
    timing_differences: int
    unresolved: int
    status: str
    duration_ms: int | None
    created_at: datetime


@dataclass(frozen=True)
class ReconRunDetail:
    summary: ReconRunSummary
    results: list[ReconResultDetail]


def _row_to_summary(row: ReconRunRow) -> ReconRunSummary:
    return ReconRunSummary(
        run_id=row.id,
        period_start=as_aware_utc(row.period_start),
        period_end=as_aware_utc(row.period_end),
        total_records=row.total_records,
        matched=row.matched,
        missing=row.missing,
        duplicates=row.duplicates,
        amount_mismatches=row.amount_mismatch,
        timing_differences=row.timing_differences,
        unresolved=row.unresolved,
        status=row.status,
        duration_ms=row.duration_ms,
        created_at=as_aware_utc(row.created_at),
    )


def _row_to_result_detail(row: ReconResultRow) -> ReconResultDetail:
    return ReconResultDetail(
        result_id=row.id,
        run_id=row.run_id,
        transaction_ref=row.transaction_ref,
        status=ReconStatus(row.status),
        internal_amount=Decimal(str(row.internal_amount)) if row.internal_amount is not None else None,
        gateway_amount=Decimal(str(row.gateway_amount)) if row.gateway_amount is not None else None,
        bank_amount=Decimal(str(row.bank_amount)) if row.bank_amount is not None else None,
        probable_cause=row.probable_cause,
        cause_confidence=row.cause_confidence,
        evidence=list(row.evidence or []),
        resolved=row.resolved,
        resolved_by=row.resolved_by,
        resolution_note=row.resolution_note,
    )


class ReconService:
    async def create_run(
        self,
        session: AsyncSession,
        org_id: UUID,
        internal: list[ReconRecord],
        gateway: list[ReconRecord],
        bank: list[ReconRecord],
        config: MatchConfig | None = None,
        started_by: UUID | None = None,
    ) -> ReconRunResult:
        return await run_reconciliation(session, org_id, internal, gateway, bank, config, started_by)

    async def get_run(self, session: AsyncSession, org_id: UUID, run_id: UUID) -> ReconRunDetail | None:
        run_result = await session.execute(
            select(ReconRunRow).where(ReconRunRow.id == run_id, ReconRunRow.org_id == org_id)
        )
        run_row = run_result.scalar_one_or_none()
        if run_row is None:
            return None

        results_result = await session.execute(
            select(ReconResultRow).where(ReconResultRow.run_id == run_id, ReconResultRow.org_id == org_id)
        )
        results = [_row_to_result_detail(r) for r in results_result.scalars()]
        return ReconRunDetail(summary=_row_to_summary(run_row), results=results)

    async def get_runs(self, session: AsyncSession, org_id: UUID) -> list[ReconRunSummary]:
        result = await session.execute(
            select(ReconRunRow).where(ReconRunRow.org_id == org_id).order_by(ReconRunRow.created_at.desc())
        )
        return [_row_to_summary(row) for row in result.scalars()]

    async def get_mismatches(self, session: AsyncSession, org_id: UUID, run_id: UUID) -> list[ReconResultDetail] | None:
        detail = await self.get_run(session, org_id, run_id)
        if detail is None:
            return None
        return [r for r in detail.results if r.status != ReconStatus.matched]

    async def resolve_manually(
        self,
        session: AsyncSession,
        org_id: UUID,
        result_id: UUID,
        resolution_note: str,
        resolved_by: UUID,
    ) -> ReconResultDetail | None:
        result = await session.execute(
            select(ReconResultRow).where(ReconResultRow.id == result_id, ReconResultRow.org_id == org_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None

        row.resolved = True
        row.resolved_by = resolved_by
        row.resolution_note = resolution_note
        await session.flush()
        return _row_to_result_detail(row)

    async def export_results(
        self, session: AsyncSession, org_id: UUID, run_id: UUID, format: str = "csv"
    ) -> str:
        if format != "csv":
            raise ValueError(f"Unsupported export format: {format!r}")

        detail = await self.get_run(session, org_id, run_id)
        if detail is None:
            raise ValueError(f"No such reconciliation run: {run_id}")

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        for r in detail.results:
            writer.writerow(
                {
                    "result_id": str(r.result_id),
                    "run_id": str(r.run_id),
                    "transaction_ref": r.transaction_ref,
                    "status": r.status.value,
                    "internal_amount": r.internal_amount,
                    "gateway_amount": r.gateway_amount,
                    "bank_amount": r.bank_amount,
                    "probable_cause": r.probable_cause,
                    "cause_confidence": r.cause_confidence,
                    "evidence": "; ".join(r.evidence),
                    "resolved": r.resolved,
                    "resolved_by": str(r.resolved_by) if r.resolved_by else "",
                    "resolution_note": r.resolution_note or "",
                }
            )
        return buffer.getvalue()
