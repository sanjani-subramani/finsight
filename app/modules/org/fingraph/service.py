"""FinGraphService -- the public face of app.modules.org.fingraph."""

from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ImpactResult
from app.models.tables import FailureSimulation as FailureSimulationRow
from app.modules.org.fingraph.impact import CentralityScore, compute_blast_radius, compute_centrality, what_if_multiple


class FinGraphService:
    async def simulate_failure(
        self, session: AsyncSession, org_id: UUID, node_name: str, duration_hours: float | None = None
    ) -> ImpactResult:
        result = await compute_blast_radius(session, org_id, node_name, duration_hours)
        await self._persist(session, org_id, result, duration_hours)
        return result

    async def simulate_multi_failure(
        self, session: AsyncSession, org_id: UUID, node_names: list[str], duration_hours: float | None = None
    ) -> ImpactResult:
        result = await what_if_multiple(session, org_id, node_names, duration_hours)
        await self._persist(session, org_id, result, duration_hours)
        return result

    async def get_critical_nodes(self, session: AsyncSession, org_id: UUID) -> list[CentralityScore]:
        centrality = await compute_centrality(session, org_id)
        return sorted(centrality.values(), key=lambda c: c.betweenness, reverse=True)

    async def get_simulation_history(self, session: AsyncSession, org_id: UUID) -> list[FailureSimulationRow]:
        result = await session.execute(
            select(FailureSimulationRow)
            .where(FailureSimulationRow.org_id == org_id)
            .order_by(FailureSimulationRow.created_at.desc())
        )
        return list(result.scalars())

    async def _persist(
        self, session: AsyncSession, org_id: UUID, result: ImpactResult, duration_hours: float | None
    ) -> None:
        # model_dump_json() -> json.loads() rather than model_dump()
        # directly: it renders UUIDs as plain strings, which is what the
        # JSONB column (and re-reading this history later) actually wants.
        session.add(
            FailureSimulationRow(
                org_id=org_id,
                failed_node=result.failed_node,
                duration_hours=duration_hours,
                result=json.loads(result.model_dump_json()),
            )
        )
        await session.flush()
