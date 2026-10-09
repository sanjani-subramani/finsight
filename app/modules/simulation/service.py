"""SimulationService — the public face of app.modules.simulation.

Orchestrates: get a Twin snapshot -> build a SimulationInput -> check the
Redis cache -> simulate() -> derive safe-to-spend and sensitivity ->
persist -> return.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ShortfallRisk
from app.models.tables import SimulationRun, User
from app.modules.simulation.builder import build_simulation_input
from app.modules.simulation.distributions import DistributionSpec
from app.modules.simulation.engine import IncomeSpec, ObligationSpec, SimulationInput, SimulationResult, simulate
from app.modules.simulation.safe_to_spend import PurchaseVerdict, SafeToSpendResult, compute_safe_to_spend
from app.modules.simulation.safe_to_spend import evaluate_purchase as _evaluate_purchase
from app.modules.simulation.sensitivity import SensitivityFactor, analyse_sensitivity
from app.platform.cache import RedisLike
from app.platform.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

_default_redis_client: RedisLike | None = None


def _get_redis(injected: RedisLike | None) -> RedisLike:
    if injected is not None:
        return injected
    global _default_redis_client
    if _default_redis_client is None:
        _default_redis_client = redis.from_url(get_settings().REDIS_URL, decode_responses=True)
    return _default_redis_client


# ---------------------------------------------------------------------------
# (de)serialization — SimulationInput/Result live as frozen dataclasses of
# Decimal/numpy-derived values; the DB and Redis only speak JSON.
# ---------------------------------------------------------------------------


def _serialize_distribution(spec: DistributionSpec) -> dict[str, Any]:
    return {"family": spec.family, "params": spec.params, "method": spec.method, "confidence": spec.confidence}


def _deserialize_distribution(data: dict[str, Any]) -> DistributionSpec:
    return DistributionSpec(
        family=data["family"], params=data["params"], method=data["method"], confidence=data["confidence"]
    )


def _serialize_income_spec(spec: IncomeSpec) -> dict[str, Any]:
    return {
        "label": spec.label,
        "distribution": _serialize_distribution(spec.distribution),
        "expected_day": spec.expected_day,
        "day_uncertainty_std": spec.day_uncertainty_std,
    }


def _deserialize_income_spec(data: dict[str, Any]) -> IncomeSpec:
    return IncomeSpec(
        label=data["label"],
        distribution=_deserialize_distribution(data["distribution"]),
        expected_day=data["expected_day"],
        day_uncertainty_std=data["day_uncertainty_std"],
    )


def _serialize_obligation_spec(spec: ObligationSpec) -> dict[str, Any]:
    return {
        "label": spec.label,
        "amount": str(spec.amount),
        "day_offset": spec.day_offset,
        "is_flexible": spec.is_flexible,
    }


def _deserialize_obligation_spec(data: dict[str, Any]) -> ObligationSpec:
    return ObligationSpec(
        label=data["label"],
        amount=Decimal(data["amount"]),
        day_offset=data["day_offset"],
        is_flexible=data["is_flexible"],
    )


def _serialize_input(inp: SimulationInput) -> dict[str, Any]:
    return {
        "starting_cash": str(inp.starting_cash),
        "income_events": [_serialize_income_spec(s) for s in inp.income_events],
        "obligations": [_serialize_obligation_spec(o) for o in inp.obligations],
        "discretionary_daily_mean": str(inp.discretionary_daily_mean),
        "discretionary_daily_std": str(inp.discretionary_daily_std),
        "horizon_days": inp.horizon_days,
        "scenarios": inp.scenarios,
        "seed": inp.seed,
    }


def _deserialize_input(data: dict[str, Any]) -> SimulationInput:
    return SimulationInput(
        starting_cash=Decimal(data["starting_cash"]),
        income_events=[_deserialize_income_spec(s) for s in data["income_events"]],
        obligations=[_deserialize_obligation_spec(o) for o in data["obligations"]],
        discretionary_daily_mean=Decimal(data["discretionary_daily_mean"]),
        discretionary_daily_std=Decimal(data["discretionary_daily_std"]),
        horizon_days=data["horizon_days"],
        scenarios=data["scenarios"],
        seed=data["seed"],
    )


def _serialize_safe_to_spend(r: SafeToSpendResult) -> dict[str, Any]:
    return {
        "amount": str(r.amount),
        "threshold_used": r.threshold_used,
        "risk_tolerance": r.risk_tolerance,
        "iterations": r.iterations,
        "final_shortfall_probability": r.final_shortfall_probability,
    }


def _deserialize_safe_to_spend(data: dict[str, Any]) -> SafeToSpendResult:
    return SafeToSpendResult(
        amount=Decimal(data["amount"]),
        threshold_used=data["threshold_used"],
        risk_tolerance=data["risk_tolerance"],
        iterations=data["iterations"],
        final_shortfall_probability=data["final_shortfall_probability"],
    )


def _serialize_sensitivity(factors: list[SensitivityFactor]) -> list[dict[str, Any]]:
    return [
        {
            "name": f.name,
            "description": f.description,
            "prob_before": f.prob_before,
            "prob_after": f.prob_after,
            "delta": f.delta,
            "actionable": f.actionable,
        }
        for f in factors
    ]


def _deserialize_sensitivity(data: list[dict[str, Any]]) -> list[SensitivityFactor]:
    return [SensitivityFactor(**d) for d in data]


def _build_shortfall_risks(result: SimulationResult) -> list[ShortfallRisk]:
    breach_date = _representative_breach_date(result)
    return [
        ShortfallRisk(
            horizon_days=horizon,
            probability=probability,
            first_breach_date=breach_date,
            worst_case_balance=result.min_balance_p5,
            scenarios_run=result.scenarios_run,
        )
        for horizon, probability in sorted(result.shortfall_probability_by_horizon.items())
    ]


def _representative_breach_date(result: SimulationResult) -> date | None:
    percentiles = result.first_breach_day_distribution.get("percentiles")
    if not percentiles:
        return None
    median_day = percentiles.get("p50")
    if median_day is None:
        return None
    return date.today() + timedelta(days=round(median_day))


@dataclass(frozen=True)
class SimulationOutcome:
    run_id: UUID
    result: SimulationResult
    safe_to_spend: SafeToSpendResult
    sensitivity: list[SensitivityFactor]
    shortfall_risks: list[ShortfallRisk]
    from_cache: bool


@dataclass(frozen=True)
class ReplayResult:
    run_id: UUID
    matches: bool
    original_probability: float
    replayed_probability: float
    replayed_result: SimulationResult


class SimulationService:
    async def run(
        self,
        session: AsyncSession,
        user_id: UUID,
        horizon_days: int = 90,
        scenarios: int = 1000,
        force_refresh: bool = False,
        redis_client: RedisLike | None = None,
    ) -> SimulationOutcome:
        # Deferred import: app.modules.twin.service.TwinService.get_snapshot
        # enriches its snapshot by calling INTO this service, so importing
        # TwinService at module load time here would create a genuine
        # circular import. We use get_base_snapshot() specifically (never
        # get_snapshot()) so this call can never recurse back into another
        # simulation run.
        from app.modules.twin.service import TwinService

        snapshot = await TwinService().get_base_snapshot(session, user_id)
        sim_input = await build_simulation_input(session, snapshot, horizon_days, scenarios)

        # Cache key includes snapshot_id: a state change (new event,
        # obligation, or goal) produces a new snapshot_id and therefore
        # automatically misses the cache — no separate invalidation logic
        # needed here.
        cache_key = self._cache_key(user_id, snapshot.snapshot_id, horizon_days, scenarios)

        if not force_refresh:
            cached_run_id = await self._read_cache(cache_key, redis_client)
            if cached_run_id is not None:
                outcome = await self._load_outcome_from_run(session, cached_run_id, from_cache=True)
                if outcome is not None:
                    return outcome

        result = simulate(sim_input)
        risk_tolerance = await self._risk_tolerance(session, user_id)
        safe_to_spend_result = compute_safe_to_spend(sim_input, risk_tolerance)
        sensitivity_factors = analyse_sensitivity(sim_input, result)

        run_row = await self._persist_run(
            session, user_id, sim_input, result, safe_to_spend_result, sensitivity_factors
        )
        await self._write_cache(cache_key, run_row.id, redis_client)

        return SimulationOutcome(
            run_id=run_row.id,
            result=result,
            safe_to_spend=safe_to_spend_result,
            sensitivity=sensitivity_factors,
            shortfall_risks=_build_shortfall_risks(result),
            from_cache=False,
        )

    async def evaluate_purchase(
        self,
        session: AsyncSession,
        user_id: UUID,
        amount: Decimal,
        description: str,
        horizon_days: int = 90,
        scenarios: int = 1000,
    ) -> PurchaseVerdict:
        from app.modules.twin.service import TwinService

        snapshot = await TwinService().get_base_snapshot(session, user_id)
        sim_input = await build_simulation_input(session, snapshot, horizon_days, scenarios)
        risk_tolerance = await self._risk_tolerance(session, user_id)
        return _evaluate_purchase(sim_input, amount, risk_tolerance)

    async def replay_run(self, session: AsyncSession, run_id: UUID) -> ReplayResult | None:
        """Re-runs a stored simulation from its saved seed and inputs and
        checks the result matches exactly. This proves the engine is
        genuinely reproducible (same seed + same input -> identical
        output, not just "close"), which is what makes stored results
        auditable and is the foundation Counterfactual Replay builds on."""
        result_query = await session.execute(select(SimulationRun).where(SimulationRun.id == run_id))
        row = result_query.scalar_one_or_none()
        if row is None or row.inputs_snapshot is None:
            return None

        reconstructed_input = _deserialize_input(row.inputs_snapshot)
        replayed_result = simulate(reconstructed_input)

        original_probability = float(row.shortfall_probability)
        replayed_probability = replayed_result.shortfall_probability_by_horizon.get(
            reconstructed_input.horizon_days,
            max(replayed_result.shortfall_probability_by_horizon.values()),
        )
        matches = abs(original_probability - replayed_probability) < 1e-9

        if not matches:
            logger.error(
                "simulation_replay_mismatch",
                run_id=str(run_id),
                original=original_probability,
                replayed=replayed_probability,
            )

        return ReplayResult(
            run_id=run_id,
            matches=matches,
            original_probability=original_probability,
            replayed_probability=replayed_probability,
            replayed_result=replayed_result,
        )

    async def get_run(self, session: AsyncSession, user_id: UUID, run_id: UUID) -> SimulationRun | None:
        result = await session.execute(
            select(SimulationRun).where(SimulationRun.id == run_id, SimulationRun.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_runs(self, session: AsyncSession, user_id: UUID, limit: int = 20) -> list[SimulationRun]:
        result = await session.execute(
            select(SimulationRun)
            .where(SimulationRun.user_id == user_id)
            .order_by(SimulationRun.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars())

    async def _risk_tolerance(self, session: AsyncSession, user_id: UUID) -> str:
        result = await session.execute(select(User.risk_tolerance).where(User.id == user_id))
        value = result.scalar_one_or_none()
        return value or "balanced"

    async def _persist_run(
        self,
        session: AsyncSession,
        user_id: UUID,
        sim_input: SimulationInput,
        result: SimulationResult,
        safe_to_spend_result: SafeToSpendResult,
        sensitivity_factors: list[SensitivityFactor],
    ) -> SimulationRun:
        headline_probability = result.shortfall_probability_by_horizon.get(
            sim_input.horizon_days, max(result.shortfall_probability_by_horizon.values())
        )

        # Storing the seed AND the full inputs (not just the outputs)
        # makes every result reproducible after the fact — required for
        # auditability ("why did we tell this user their risk was 14%?")
        # and for Shadow Mode measurement later, which needs to re-derive
        # exactly what the model would have said at any past point.
        percentile_curve_blob = {
            "balance_matrix_summary": result.balance_matrix_summary,
            "shortfall_probability_by_horizon": {
                str(k): v for k, v in result.shortfall_probability_by_horizon.items()
            },
            "min_balance_p50": str(result.min_balance_p50),
            "first_breach_day_distribution": result.first_breach_day_distribution,
            "safe_to_spend_detail": _serialize_safe_to_spend(safe_to_spend_result),
            "sensitivity": _serialize_sensitivity(sensitivity_factors),
        }

        row = SimulationRun(
            user_id=user_id,
            scenarios=result.scenarios_run,
            horizon_days=sim_input.horizon_days,
            random_seed=sim_input.seed,
            shortfall_probability=headline_probability,
            first_breach_date=_representative_breach_date(result),
            worst_case_balance=result.min_balance_p5,
            time_to_danger_days=result.time_to_danger_days,
            safe_to_spend=safe_to_spend_result.amount,
            inputs_snapshot=_serialize_input(sim_input),
            percentile_curve=percentile_curve_blob,
            duration_ms=result.duration_ms,
        )
        session.add(row)
        await session.flush()
        return row

    async def _load_outcome_from_run(
        self, session: AsyncSession, run_id: UUID, from_cache: bool
    ) -> SimulationOutcome | None:
        result_query = await session.execute(select(SimulationRun).where(SimulationRun.id == run_id))
        row = result_query.scalar_one_or_none()
        if row is None or row.percentile_curve is None:
            return None

        blob = row.percentile_curve
        try:
            result = SimulationResult(
                balance_matrix_summary=blob["balance_matrix_summary"],
                shortfall_probability_by_horizon={
                    int(k): v for k, v in blob["shortfall_probability_by_horizon"].items()
                },
                min_balance_p5=Decimal(str(row.worst_case_balance)),
                min_balance_p50=Decimal(blob["min_balance_p50"]),
                first_breach_day_distribution=blob["first_breach_day_distribution"],
                time_to_danger_days=row.time_to_danger_days,
                scenarios_run=row.scenarios,
                seed=row.random_seed or 0,
                duration_ms=row.duration_ms or 0,
            )
            safe_to_spend_result = _deserialize_safe_to_spend(blob["safe_to_spend_detail"])
            sensitivity_factors = _deserialize_sensitivity(blob["sensitivity"])
        except (KeyError, TypeError):
            logger.warning("simulation_cache_run_corrupt", run_id=str(run_id))
            return None

        return SimulationOutcome(
            run_id=row.id,
            result=result,
            safe_to_spend=safe_to_spend_result,
            sensitivity=sensitivity_factors,
            shortfall_risks=_build_shortfall_risks(result),
            from_cache=from_cache,
        )

    def _cache_key(self, user_id: UUID, snapshot_id: UUID, horizon_days: int, scenarios: int) -> str:
        return f"simulation:{user_id}:{snapshot_id}:{horizon_days}:{scenarios}"

    async def _read_cache(self, key: str, redis_client: RedisLike | None) -> UUID | None:
        try:
            raw = await _get_redis(redis_client).get(key)
        except Exception:
            logger.warning("simulation_cache_read_failed", exc_info=True)
            return None
        if not raw:
            return None
        try:
            return UUID(raw)
        except ValueError:
            return None

    async def _write_cache(self, key: str, run_id: UUID, redis_client: RedisLike | None) -> None:
        try:
            await _get_redis(redis_client).set(key, str(run_id))
        except Exception:
            logger.warning("simulation_cache_write_failed", exc_info=True)
