from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.models.tables import Intervention
from app.modules.decision.shadow_report import (
    MIN_SAMPLE_SIZE_FOR_STABLE_PRECISION,
    generate_shadow_report,
    render_markdown,
    to_json_dict,
)


def _intervention(
    *,
    severity: str = "notify",
    materialized: bool | None = None,
    confidence_ceiling_applied: bool = False,
    shadow_mode: bool = False,
    delivered: bool = False,
    delivered_at: datetime | None = None,
    acknowledged_at: datetime | None = None,
) -> Intervention:
    return Intervention(
        user_id=uuid4(),
        severity=severity,
        severity_raw=0.5,
        confidence_ceiling_applied=confidence_ceiling_applied,
        headline="h",
        body="b",
        probability=0.5,
        urgency_score=0.5,
        data_confidence=0.9,
        shadow_mode=shadow_mode,
        delivered=delivered,
        delivered_at=delivered_at,
        user_acknowledged=acknowledged_at is not None,
        acknowledged_at=acknowledged_at,
        outcome_materialized=materialized,
        outcome_checked_at=datetime.now(timezone.utc) if materialized is not None else None,
    )


async def test_sample_size_warning_true_below_threshold(db_session):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    for materialized in (True, False):
        db_session.add(_intervention(severity="notify", materialized=materialized))
    await db_session.flush()

    report = await generate_shadow_report(db_session, since)

    notify = report.precision_by_severity["notify"]
    assert notify.fired == 2
    assert notify.sample_size_warning is True, "fewer than 30 fired must be flagged, not presented as stable"


async def test_sample_size_warning_false_at_or_above_threshold(db_session):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    for _ in range(MIN_SAMPLE_SIZE_FOR_STABLE_PRECISION):
        db_session.add(_intervention(severity="monitor", materialized=True))
    await db_session.flush()

    report = await generate_shadow_report(db_session, since)

    monitor = report.precision_by_severity["monitor"]
    assert monitor.fired == MIN_SAMPLE_SIZE_FOR_STABLE_PRECISION
    assert monitor.sample_size_warning is False


async def test_confidence_ceiling_saves_and_precision_passthrough_from_step_8(db_session):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.add(_intervention(severity="critical", confidence_ceiling_applied=True, materialized=False))
    db_session.add(_intervention(severity="critical", confidence_ceiling_applied=True, materialized=True))
    await db_session.flush()

    report = await generate_shadow_report(db_session, since)

    assert report.confidence_ceiling_saves == 1
    critical = report.precision_by_severity["critical"]
    assert critical.fired == 2
    assert critical.materialized == 1
    assert critical.precision == pytest.approx(0.5)
    assert report.false_alarm_rate_by_severity["critical"] == pytest.approx(0.5)


async def test_avg_time_to_acknowledge_only_counts_delivered_nonshadow_acknowledged(db_session):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    delivered_at = datetime.now(timezone.utc) - timedelta(minutes=10)

    # Counts: delivered, non-shadow, acknowledged 2 minutes after delivery.
    db_session.add(
        _intervention(delivered=True, delivered_at=delivered_at, acknowledged_at=delivered_at + timedelta(minutes=2))
    )
    # Does NOT count: shadow mode (never shown to anyone).
    db_session.add(
        _intervention(
            shadow_mode=True, delivered=True, delivered_at=delivered_at, acknowledged_at=delivered_at + timedelta(minutes=99)
        )
    )
    # Does NOT count: delivered but never acknowledged.
    db_session.add(_intervention(delivered=True, delivered_at=delivered_at, acknowledged_at=None))
    await db_session.flush()

    report = await generate_shadow_report(db_session, since)

    assert report.avg_time_to_acknowledge_seconds == pytest.approx(120.0, abs=1.0)


async def test_avg_time_to_acknowledge_none_when_nothing_measured(db_session):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    report = await generate_shadow_report(db_session, since)
    assert report.avg_time_to_acknowledge_seconds is None


async def test_render_markdown_visibly_flags_low_sample_size(db_session):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.add(_intervention(severity="notify", materialized=True))
    await db_session.flush()

    report = await generate_shadow_report(db_session, since)
    markdown = render_markdown(report)

    assert "notify" in markdown
    assert "not statistically stable" in markdown


async def test_to_json_dict_round_trips_all_fields(db_session):
    since = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.add(_intervention(severity="notify", materialized=True))
    await db_session.flush()

    report = await generate_shadow_report(db_session, since)
    payload = to_json_dict(report)

    assert payload["total_interventions_evaluated"] == 1
    assert payload["precision_by_severity"]["notify"]["fired"] == 1
    assert payload["precision_by_severity"]["notify"]["sample_size_warning"] is True
    assert "confidence_ceiling_saves" in payload
    assert "avg_time_to_acknowledge_seconds" in payload
