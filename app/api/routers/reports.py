"""Operational reporting endpoints (Step 19 §5) -- the single place an
interviewer-facing demo (or an on-call engineer) hits to see real
measured numbers: shadow-mode precision, the latest load test run, and
live consumer lag / DLQ depth / latency percentiles. Every number here is
either read straight from Postgres/Redis or from a load_test.py JSON
report on disk -- nothing is computed live except simple aggregation.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import Intervention, SimulationRun, User
from app.modules.decision.shadow_report import generate_shadow_report, render_markdown, to_json_dict
from app.platform.database import get_session
from app.platform.deps import require_admin
from app.platform.eventbus import Topic, get_redis_client, stream_key
from app.platform.timeutils import as_aware_utc

router = APIRouter(prefix="/reports", tags=["reports"])

DEFAULT_PRECISION_LOOKBACK_DAYS = 30
DEFAULT_HEALTH_LOOKBACK_HOURS = 24
CONSUMER_GROUP = "pipeline"
# reports.py is app/api/routers/reports.py -- parents[0]=routers,
# [1]=api, [2]=app, [3]=repo root, where scripts/ actually lives. This
# was off by one (pointed at app/scripts/, which doesn't exist) until
# caught by actually calling this endpoint against a real prior
# load_test.py run instead of a mocked path.
LOAD_TEST_REPORT_PATH = Path(__file__).resolve().parents[3] / "scripts" / "load_test_report.json"


@router.get("/shadow-precision")
async def get_shadow_precision(
    since: datetime | None = Query(None),
    format: str = Query("json", pattern="^(json|markdown)$"),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> Any:
    resolved_since = since or (datetime.now(timezone.utc) - timedelta(days=DEFAULT_PRECISION_LOOKBACK_DAYS))
    report = await generate_shadow_report(session, resolved_since)
    if format == "markdown":
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(render_markdown(report))
    return to_json_dict(report)


@router.get("/load-test")
async def get_load_test_report(current_user: User = Depends(require_admin)) -> Any:
    if not LOAD_TEST_REPORT_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No load test report found at {LOAD_TEST_REPORT_PATH}. "
                "Run `python scripts/load_test.py` first -- this endpoint never estimates, it only serves "
                "a real prior run's output."
            ),
        )
    return json.loads(LOAD_TEST_REPORT_PATH.read_text())


async def _stream_lag(topic: Topic) -> dict[str, Any]:
    redis_client = get_redis_client()
    key = stream_key(topic)
    length = await redis_client.xlen(key)
    pending_count = 0
    try:
        summary = await redis_client.xpending(key, CONSUMER_GROUP)
        # redis-py returns either a dict (async client) or a list
        # depending on version -- handle both rather than assuming one.
        if isinstance(summary, dict):
            pending_count = summary.get("pending", 0) or 0
        elif isinstance(summary, (list, tuple)) and summary:
            pending_count = summary[0] or 0
    except Exception:
        # No consumer group yet (nothing has ever consumed this topic) --
        # zero pending is the correct answer, not an error.
        pending_count = 0
    return {"topic": topic.value, "stream_length": length, "pending_count": pending_count}


def _percentiles(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"p50": None, "p95": None, "p99": None, "count": 0}
    arr = np.array(values, dtype=float)
    return {
        "p50": float(np.percentile(arr, 50)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
        "count": len(values),
    }


@router.get("/system-health")
async def get_system_health(
    window_hours: int = Query(DEFAULT_HEALTH_LOOKBACK_HOURS, ge=1, le=24 * 30),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    consumer_lag = [await _stream_lag(topic) for topic in Topic if topic != Topic.DEAD_LETTER]
    dlq = await _stream_lag(Topic.DEAD_LETTER)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)

    sim_result = await session.execute(
        select(SimulationRun.duration_ms).where(SimulationRun.created_at >= cutoff)
    )
    simulation_durations = [float(d) for (d,) in sim_result.all() if d is not None]

    intervention_result = await session.execute(
        select(Intervention.created_at, Intervention.delivered_at).where(
            Intervention.created_at >= cutoff,
            Intervention.delivered.is_(True),
            Intervention.delivered_at.isnot(None),
        )
    )
    delivery_latencies_ms = [
        (as_aware_utc(delivered_at) - as_aware_utc(created_at)).total_seconds() * 1000
        for created_at, delivered_at in intervention_result.all()
        if delivered_at is not None
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_hours": window_hours,
        "consumer_lag_by_topic": consumer_lag,
        "dead_letter_queue_depth": dlq["stream_length"],
        "simulation_duration_ms": _percentiles(simulation_durations),
        "intervention_delivery_latency_ms": _percentiles(delivery_latencies_ms),
    }
