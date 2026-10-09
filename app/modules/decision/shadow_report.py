"""Full shadow-mode reporting -- extends Step 8's
app.modules.decision.shadow.compute_precision (plain measured counts,
never estimated) into a report an interviewer/reviewer can actually read,
in both JSON (for the API) and markdown (for a README or resume-prep
notes).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import mean
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import Intervention
from app.modules.decision.shadow import compute_precision
from app.platform.timeutils import as_aware_utc

# Below this many FIRED interventions for a severity, a precision number
# is statistically unstable -- report it, but flag it, rather than
# presenting it as a stable figure. This is basic statistical practice: a
# proportion's standard error shrinks slowly, and below ~30 samples a
# single additional outcome can swing the reported rate by several
# points. A precision claim on fewer samples than this must always carry
# this caveat, never be quoted as a bare percentage.
MIN_SAMPLE_SIZE_FOR_STABLE_PRECISION = 30


@dataclass(frozen=True)
class PrecisionStat:
    fired: int
    materialized: int
    precision: float | None
    sample_size_warning: bool


@dataclass(frozen=True)
class ShadowReport:
    window_start: datetime
    window_end: datetime
    total_interventions_evaluated: int
    precision_by_severity: dict[str, PrecisionStat] = field(default_factory=dict)
    # How many times the confidence ceiling (Step 6/8) downgraded a
    # decision that then correctly did NOT materialize -- evidence the
    # ceiling is doing real work, not just being cautious for no reason.
    confidence_ceiling_saves: int = 0
    false_alarm_rate_by_severity: dict[str, float | None] = field(default_factory=dict)
    avg_time_to_acknowledge_seconds: float | None = None


async def _avg_time_to_acknowledge(session: AsyncSession, since: datetime) -> float | None:
    """Only over DELIVERED, non-shadow interventions that have actually
    been acknowledged -- a shadow-mode intervention was never shown to
    anyone, so it has no acknowledgement time to measure, and one that
    hasn't been acknowledged yet can't contribute a finished duration.
    """
    result = await session.execute(
        select(Intervention).where(
            Intervention.created_at >= since,
            Intervention.shadow_mode.is_(False),
            Intervention.delivered.is_(True),
            Intervention.acknowledged_at.isnot(None),
        )
    )
    rows = list(result.scalars())
    if not rows:
        return None

    deltas = [
        (as_aware_utc(row.acknowledged_at) - as_aware_utc(row.delivered_at or row.created_at)).total_seconds()  # type: ignore[arg-type]
        for row in rows
    ]
    return mean(deltas)


async def generate_shadow_report(session: AsyncSession, since: datetime) -> ShadowReport:
    precision = await compute_precision(session, since)

    precision_by_severity: dict[str, PrecisionStat] = {}
    false_alarm_rate_by_severity: dict[str, float | None] = {}
    for severity, stat in precision.by_severity.items():
        precision_by_severity[severity] = PrecisionStat(
            fired=stat.total_fired,
            materialized=stat.materialized,
            precision=stat.precision,
            sample_size_warning=stat.total_fired < MIN_SAMPLE_SIZE_FOR_STABLE_PRECISION,
        )
        false_alarm_rate_by_severity[severity] = stat.false_alarm_rate

    avg_ack_seconds = await _avg_time_to_acknowledge(session, since)
    total_evaluated = sum(stat.total_fired for stat in precision.by_severity.values())

    return ShadowReport(
        window_start=since,
        window_end=datetime.now(timezone.utc),
        total_interventions_evaluated=total_evaluated,
        precision_by_severity=precision_by_severity,
        confidence_ceiling_saves=precision.confidence_ceiling_saves,
        false_alarm_rate_by_severity=false_alarm_rate_by_severity,
        avg_time_to_acknowledge_seconds=avg_ack_seconds,
    )


def to_json_dict(report: ShadowReport) -> dict[str, Any]:
    return {
        "window_start": report.window_start.isoformat(),
        "window_end": report.window_end.isoformat(),
        "total_interventions_evaluated": report.total_interventions_evaluated,
        "precision_by_severity": {
            severity: {
                "fired": stat.fired,
                "materialized": stat.materialized,
                "precision": stat.precision,
                "sample_size_warning": stat.sample_size_warning,
            }
            for severity, stat in report.precision_by_severity.items()
        },
        "confidence_ceiling_saves": report.confidence_ceiling_saves,
        "false_alarm_rate_by_severity": report.false_alarm_rate_by_severity,
        "avg_time_to_acknowledge_seconds": report.avg_time_to_acknowledge_seconds,
    }


def render_markdown(report: ShadowReport) -> str:
    lines = [
        "# Shadow Mode Precision Report",
        "",
        f"Window: {report.window_start.isoformat()} -> {report.window_end.isoformat()}",
        f"Total interventions evaluated: {report.total_interventions_evaluated}",
        "",
        "## Precision by severity",
        "",
        "| Severity | Fired | Materialized | Precision | Note |",
        "|---|---|---|---|---|",
    ]
    for severity in sorted(report.precision_by_severity):
        stat = report.precision_by_severity[severity]
        precision_str = f"{stat.precision:.1%}" if stat.precision is not None else "not yet measured"
        note = "⚠ fewer than 30 fired -- not statistically stable, do not quote as-is" if stat.sample_size_warning else ""
        lines.append(f"| {severity} | {stat.fired} | {stat.materialized} | {precision_str} | {note} |")

    ack = (
        f"{report.avg_time_to_acknowledge_seconds:.0f}s"
        if report.avg_time_to_acknowledge_seconds is not None
        else "not yet measured"
    )
    lines += [
        "",
        "## Confidence ceiling",
        "",
        f"Times the ceiling downgraded a decision that then correctly did NOT materialize: "
        f"{report.confidence_ceiling_saves}",
        "",
        "## Time to acknowledge",
        "",
        f"Average, over delivered non-shadow interventions: {ack}",
    ]
    return "\n".join(lines)
