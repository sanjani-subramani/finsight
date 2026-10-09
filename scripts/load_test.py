#!/usr/bin/env python
"""FinSentinel load test (Step 19 §3).

WHY plain asyncio + httpx, not locust: locust gives a web UI and
standard percentile reporting for free, which is genuinely worth the
extra dependency for a large, long-running load test with many distinct
user behaviors. This script needs something locust makes awkward,
though: Scenario B has to isolate "our compute time" from "network +
queueing overhead" by reading SimulationRun.duration_ms directly out of
Postgres for the runs this exact test created, and Scenario C has to
sample Redis XLEN/XPENDING every few seconds on the same clock as the
publish loop. Locust runs each User in its own greenlet/process
independent of a single asyncio event loop, which complicates sharing
one coherent timeline across HTTP timing + DB introspection + Redis
introspection. At FinSentinel's current scale, a single asyncio script
keeps all three measurements on one clock, in one file, with no
extra moving parts. Revisit this choice if the target load grows enough
to need locust's distributed workers.

Usage:
    python scripts/load_test.py --base-url http://127.0.0.1:8000 --scenario all

Output: a plain-text summary to stdout and a JSON report written to
scripts/load_test_report.json (or --output). Every percentile quoted in
docs/MEASURED_METRICS.md must come from a run of THIS script -- never a
hand-estimated number.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

STRONG_PASSWORD = "Str0ngPassw0rd123"
DEFAULT_REPORT_PATH = Path(__file__).parent / "load_test_report.json"


def percentiles(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"p50": None, "p95": None, "p99": None, "min": None, "max": None, "mean": None, "count": 0}
    ordered = sorted(values)

    def pct(p: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        k = (len(ordered) - 1) * p
        lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
        frac = k - lo
        return ordered[lo] + (ordered[hi] - ordered[lo]) * frac

    return {
        "p50": pct(0.50),
        "p95": pct(0.95),
        "p99": pct(0.99),
        "min": ordered[0],
        "max": ordered[-1],
        "mean": statistics.fmean(ordered),
        "count": len(ordered),
    }


@dataclass
class ScenarioResult:
    name: str
    description: str
    latencies_ms: dict[str, float | None] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)
    errors: int = 0


async def _register_and_login(client: httpx.AsyncClient, email: str) -> str:
    await client.post(
        "/auth/register", json={"email": email, "password": STRONG_PASSWORD, "display_name": "Load Test User"}
    )
    resp = await client.post("/auth/login", json={"email": email, "password": STRONG_PASSWORD})
    resp.raise_for_status()
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Scenario A -- SMS ingestion burst
# ---------------------------------------------------------------------------

_SAMPLE_SMS_TEMPLATES = [
    "Rs.{amt}.00 credited to A/c XX4417 on {date} from LOAD TEST SENDER. Avl Bal Rs.{bal}.00",
    "Rs.{amt}.00 debited from A/c XX4417 on {date} at LOAD TEST MERCHANT. Avl Bal Rs.{bal}.00",
]


async def _run_one_sms_user(
    base_url: str, user_index: int, sms_per_user: int, window_seconds: float, latencies: list[float], errors: list[int]
) -> None:
    spacing = window_seconds / max(sms_per_user, 1)
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        email = f"loadtest-sms-{uuid4().hex[:8]}@example.com"
        token = await _register_and_login(client, email)
        headers = {"Authorization": f"Bearer {token}"}

        for i in range(sms_per_user):
            amt = 1000 + user_index * 7 + i
            sms = _SAMPLE_SMS_TEMPLATES[i % 2].format(amt=amt, date="12-01-26", bal=amt + 5000)
            start = time.perf_counter()
            try:
                resp = await client.post("/ingest/sms", json={"raw_sms": sms, "sender": "LOADTEST"}, headers=headers)
                resp.raise_for_status()
                trace_id = resp.json()["trace_id"]

                deadline = time.perf_counter() + 30
                while time.perf_counter() < deadline:
                    status_resp = await client.get(f"/ingest/status/{trace_id}", headers=headers)
                    stage = status_resp.json().get("status")
                    if stage in ("risk_assessed_complete", "intervention_delivered", "dead_letter"):
                        break
                    await asyncio.sleep(0.5)
                latencies.append((time.perf_counter() - start) * 1000)
            except Exception:
                errors[0] += 1
            await asyncio.sleep(spacing)


async def scenario_sms_burst(base_url: str, users: int, sms_per_user: int, window_seconds: float) -> ScenarioResult:
    latencies: list[float] = []
    errors = [0]
    await asyncio.gather(
        *(
            _run_one_sms_user(base_url, i, sms_per_user, window_seconds, latencies, errors)
            for i in range(users)
        )
    )
    result = ScenarioResult(
        name="A_sms_ingestion_burst",
        description=(
            f"{users} concurrent users x {sms_per_user} SMS each over {window_seconds}s. "
            "Latency = time from POST /ingest/sms to the pipeline reaching a terminal stage "
            "(intervention landed or the chain concluded without one)."
        ),
        latencies_ms=percentiles(latencies),
    )
    result.errors = errors[0]
    return result


# ---------------------------------------------------------------------------
# Scenario B -- simulation-heavy load
# ---------------------------------------------------------------------------


async def _run_one_simulation_user(base_url: str, headers_list: list[dict], latencies: list[float], errors: list[int]) -> None:
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        for headers in headers_list:
            start = time.perf_counter()
            try:
                resp = await client.get("/simulation/run", headers=headers)
                resp.raise_for_status()
                latencies.append((time.perf_counter() - start) * 1000)
            except Exception:
                errors[0] += 1


async def scenario_simulation_load(
    base_url: str, database_url: str, concurrency: int, requests_per_user: int
) -> ScenarioResult:
    # One user per concurrent caller -- simulation is cached per
    # snapshot_id, so hammering the SAME user would measure cache hits,
    # not the compute path this scenario exists to isolate.
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as setup_client:
        headers_per_user = []
        for i in range(concurrency):
            email = f"loadtest-sim-{uuid4().hex[:8]}@example.com"
            token = await _register_and_login(setup_client, email)
            headers = {"Authorization": f"Bearer {token}"}
            # Give each user something to simulate over.
            await setup_client.post(
                "/twin/income-sources",
                json={"label": "Salary", "declared_min": "15000", "declared_max": "20000", "declared_frequency_days": 30},
                headers=headers,
            )
            headers_per_user.append(headers)

    window_start = datetime.now(timezone.utc)
    latencies: list[float] = []
    errors = [0]
    await asyncio.gather(
        *(
            _run_one_simulation_user(base_url, [h] * requests_per_user, latencies, errors)
            for h in headers_per_user
        )
    )
    window_end = datetime.now(timezone.utc)

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    internal_durations: list[float] = []
    async with session_factory() as session:
        from app.models.tables import SimulationRun

        db_result = await session.execute(
            select(SimulationRun.duration_ms).where(
                SimulationRun.created_at >= window_start, SimulationRun.created_at <= window_end
            )
        )
        internal_durations = [float(d) for (d,) in db_result.all() if d is not None]
    await engine.dispose()

    scenario_result = ScenarioResult(
        name="B_simulation_heavy_load",
        description=(
            f"{concurrency} concurrent users x {requests_per_user} GET /simulation/run each. "
            "external_latency_ms is wall-clock HTTP round trip; internal_duration_ms is the SAME "
            "window's SimulationRun.duration_ms rows read straight from Postgres -- the engine's own "
            "compute time, isolated from network and queueing. A slow external p95 with a fast internal "
            "p95 means fix the queueing/network path; a slow internal p95 means fix the engine itself. "
            "Conflating the two leads to optimizing the wrong thing."
        ),
        latencies_ms=percentiles(latencies),
    )
    scenario_result.extra["internal_duration_ms"] = percentiles(internal_durations)
    scenario_result.errors = errors[0]
    return scenario_result


# ---------------------------------------------------------------------------
# Scenario C -- consumer lag under sustained publish
# ---------------------------------------------------------------------------


async def _pending_count(redis_client: aioredis.Redis, key: str, group: str) -> int:
    # XLEN never shrinks on its own -- app.platform.eventbus.EventBus.ack()
    # only XACKs a message (removing it from the consumer group's PEL); it
    # never XDELs/XTRIMs the stream entry itself. So a stream's XLEN grows
    # monotonically with publish volume REGARDLESS of whether the consumer
    # is keeping up -- it is not, by itself, a lag signal. XPENDING (the
    # consumer group's own in-flight/unacked count) is what actually
    # answers "is the consumer falling behind": same helper
    # app.api.routers.reports._stream_lag uses for /reports/system-health.
    try:
        summary = await redis_client.xpending(key, group)
    except Exception:
        return 0
    if isinstance(summary, dict):
        return int(summary.get("pending", 0) or 0)
    if isinstance(summary, (list, tuple)) and summary:
        return int(summary[0] or 0)
    return 0


async def scenario_consumer_lag(
    base_url: str, redis_url: str, duration_seconds: float, publish_rate_per_second: float, sample_interval_seconds: float
) -> ScenarioResult:
    from app.platform.eventbus import Topic, stream_key
    from app.platform.worker import CONSUMER_GROUP

    redis_client = aioredis.from_url(redis_url, decode_responses=True)
    samples: list[dict[str, Any]] = []

    async def publisher() -> None:
        async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
            email = f"loadtest-lag-{uuid4().hex[:8]}@example.com"
            token = await _register_and_login(client, email)
            headers = {"Authorization": f"Bearer {token}"}
            interval = 1.0 / max(publish_rate_per_second, 0.01)
            deadline = time.perf_counter() + duration_seconds
            i = 0
            while time.perf_counter() < deadline:
                sms = _SAMPLE_SMS_TEMPLATES[i % 2].format(amt=1000 + i, date="12-01-26", bal=6000 + i)
                try:
                    await client.post("/ingest/sms", json={"raw_sms": sms, "sender": "LAGTEST"}, headers=headers)
                except Exception:
                    pass
                i += 1
                await asyncio.sleep(interval)

    async def sampler() -> None:
        deadline = time.perf_counter() + duration_seconds + sample_interval_seconds
        start = time.perf_counter()
        while time.perf_counter() < deadline:
            sample: dict[str, Any] = {"t_seconds": round(time.perf_counter() - start, 1)}
            for topic in Topic:
                key = stream_key(topic)
                try:
                    length = await redis_client.xlen(key)
                except Exception:
                    length = None
                sample[topic.value] = length
                sample[f"{topic.value}_pending"] = await _pending_count(redis_client, key, CONSUMER_GROUP)
            samples.append(sample)
            await asyncio.sleep(sample_interval_seconds)

    await asyncio.gather(publisher(), sampler())
    await redis_client.aclose()

    # XLEN is reported for context only -- it grows monotonically with
    # publish volume regardless of consumer speed (see _pending_count's
    # docstring), so it is NOT the lag signal. PENDING (the consumer
    # group's own unacked/in-flight count) is: "flat" = the tail isn't
    # meaningfully higher than the head; a pending count climbing over
    # the run means the consumer can't keep up with the publish rate at
    # this volume.
    financial_event_lengths: list[float] = [
        float(s["financial_event"]) for s in samples if s.get("financial_event") is not None
    ]
    financial_event_pending: list[float] = [
        float(s["financial_event_pending"]) for s in samples if s.get("financial_event_pending") is not None
    ]
    head = (
        statistics.fmean(financial_event_lengths[: max(1, len(financial_event_lengths) // 5)])
        if financial_event_lengths
        else 0.0
    )
    tail = (
        statistics.fmean(financial_event_lengths[-max(1, len(financial_event_lengths) // 5) :])
        if financial_event_lengths
        else 0.0
    )
    pending_head = (
        statistics.fmean(financial_event_pending[: max(1, len(financial_event_pending) // 5)])
        if financial_event_pending
        else 0.0
    )
    pending_tail = (
        statistics.fmean(financial_event_pending[-max(1, len(financial_event_pending) // 5) :])
        if financial_event_pending
        else 0.0
    )

    result = ScenarioResult(
        name="C_consumer_lag_under_sustained_publish",
        description=(
            f"Published at ~{publish_rate_per_second}/s for {duration_seconds}s, sampling stream XLEN "
            f"AND XPENDING every {sample_interval_seconds}s. XLEN always grows with publish volume "
            "(EventBus.ack() never trims the stream) so it is context, not a lag signal. "
            "pending_head_avg/pending_tail_avg (first vs last fifth of samples) close to 1.0 means "
            "lag stayed flat; well above 1.0 means the consumer is falling behind."
        ),
    )
    result.extra["samples"] = samples
    result.extra["financial_event_stream_head_avg"] = head
    result.extra["financial_event_stream_tail_avg"] = tail
    result.extra["lag_ratio_tail_over_head"] = (tail / head) if head else None
    result.extra["financial_event_pending_head_avg"] = pending_head
    result.extra["financial_event_pending_tail_avg"] = pending_tail
    result.extra["pending_lag_ratio_tail_over_head"] = (pending_tail / pending_head) if pending_head else None
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--database-url", default=None, help="defaults to settings.DATABASE_URL")
    parser.add_argument("--redis-url", default=None, help="defaults to settings.REDIS_URL")
    parser.add_argument("--scenario", choices=["a", "b", "c", "all"], default="all")
    parser.add_argument("--output", default=str(DEFAULT_REPORT_PATH))
    # Defaults below are REDUCED from the spec's literal scale (N users x
    # 30s for A, 5min for C) so a run fits inside an interactive
    # development session -- pass the larger values explicitly for a
    # full-scale run against a properly provisioned environment.
    parser.add_argument("--sms-users", type=int, default=5)
    parser.add_argument("--sms-per-user", type=int, default=5)
    parser.add_argument("--sms-window-seconds", type=float, default=15.0)
    parser.add_argument("--sim-concurrency", type=int, default=10)
    parser.add_argument("--sim-requests-per-user", type=int, default=3)
    parser.add_argument("--lag-duration-seconds", type=float, default=30.0)
    parser.add_argument("--lag-publish-rate", type=float, default=2.0)
    parser.add_argument("--lag-sample-interval-seconds", type=float, default=5.0)
    args = parser.parse_args()

    from app.platform.config import get_settings

    settings = get_settings()
    database_url = args.database_url or settings.DATABASE_URL
    redis_url = args.redis_url or settings.REDIS_URL

    results: list[ScenarioResult] = []
    run_scenarios = ["a", "b", "c"] if args.scenario == "all" else [args.scenario]

    if "a" in run_scenarios:
        print(f"--- Scenario A: SMS ingestion burst ({args.sms_users} users) ---")
        results.append(
            await scenario_sms_burst(args.base_url, args.sms_users, args.sms_per_user, args.sms_window_seconds)
        )
    if "b" in run_scenarios:
        print(f"--- Scenario B: simulation-heavy load ({args.sim_concurrency} concurrent) ---")
        results.append(
            await scenario_simulation_load(
                args.base_url, database_url, args.sim_concurrency, args.sim_requests_per_user
            )
        )
    if "c" in run_scenarios:
        print(f"--- Scenario C: consumer lag under sustained publish ({args.lag_duration_seconds}s) ---")
        results.append(
            await scenario_consumer_lag(
                args.base_url, redis_url, args.lag_duration_seconds, args.lag_publish_rate, args.lag_sample_interval_seconds
            )
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "scenarios": [asdict(r) for r in results],
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(report, indent=2, default=str))

    print("\n=== LOAD TEST REPORT ===")
    for r in results:
        print(f"\n[{r.name}] {r.description}")
        if r.latencies_ms:
            lat = r.latencies_ms
            print(
                f"  latency_ms: p50={lat['p50']:.1f} p95={lat['p95']:.1f} p99={lat['p99']:.1f} "
                f"mean={lat['mean']:.1f} min={lat['min']:.1f} max={lat['max']:.1f} n={lat['count']}"
                if lat.get("count")
                else "  latency_ms: no successful samples"
            )
        if "internal_duration_ms" in r.extra:
            idur = r.extra["internal_duration_ms"]
            if idur.get("count"):
                print(
                    f"  internal_duration_ms (SimulationRun.duration_ms): p50={idur['p50']:.1f} "
                    f"p95={idur['p95']:.1f} p99={idur['p99']:.1f} n={idur['count']}"
                )
        if "lag_ratio_tail_over_head" in r.extra:
            print(f"  financial_event stream XLEN (context only, never shrinks) "
                  f"head_avg={r.extra['financial_event_stream_head_avg']:.2f} "
                  f"tail_avg={r.extra['financial_event_stream_tail_avg']:.2f} "
                  f"ratio={r.extra['lag_ratio_tail_over_head']}")
            print(f"  financial_event PENDING (actual lag signal) "
                  f"head_avg={r.extra['financial_event_pending_head_avg']:.2f} "
                  f"tail_avg={r.extra['financial_event_pending_tail_avg']:.2f} "
                  f"ratio={r.extra['pending_lag_ratio_tail_over_head']}")
        print(f"  errors: {r.errors}")

    print(f"\nFull JSON report written to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
