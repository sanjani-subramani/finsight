"""CRUD for building/maintaining an org's dependency graph. An org sets
this up once and updates it rarely, unlike PayTrace/ReconX which ingest
continuously -- so correctness (never silently writing a cycle) matters
more here than throughput.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import DependencyEdge as DependencyEdgeRow
from app.models.tables import DependencyNode as DependencyNodeRow
from app.modules.org.fingraph.graph_builder import build_graph, detect_cycles, validate_and_build
from app.modules.org.fingraph.impact import CentralityScore, compute_centrality

DEFAULT_EDGE_TYPE = "depends_on"
DEFAULT_EDGE_WEIGHT = 1.0
TOP_CENTRALITY_COUNT = 5


class CycleError(ValueError):
    """Raised when writing an edge would create a dependency cycle."""


async def _get_node_by_name(session: AsyncSession, org_id: UUID, name: str) -> DependencyNodeRow | None:
    result = await session.execute(
        select(DependencyNodeRow).where(DependencyNodeRow.org_id == org_id, DependencyNodeRow.name == name)
    )
    return result.scalar_one_or_none()


async def add_node(
    session: AsyncSession,
    org_id: UUID,
    name: str,
    node_type: str,
    is_critical: bool = False,
    alternative_for: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> DependencyNodeRow:
    row = DependencyNodeRow(
        org_id=org_id,
        name=name,
        node_type=node_type,
        is_critical=is_critical,
        alternative_for=alternative_for,
        metadata_json=metadata or {},
    )
    session.add(row)
    await session.flush()
    return row


async def add_edge(
    session: AsyncSession,
    org_id: UUID,
    from_name: str,
    to_name: str,
    edge_type: str = DEFAULT_EDGE_TYPE,
    weight: float = DEFAULT_EDGE_WEIGHT,
) -> DependencyEdgeRow:
    from_node = await _get_node_by_name(session, org_id, from_name)
    to_node = await _get_node_by_name(session, org_id, to_name)
    if from_node is None or to_node is None:
        raise ValueError(f"Both nodes must exist before adding an edge: {from_name!r} -> {to_name!r}")

    graph = await build_graph(session, org_id)
    graph.add_edge(from_name, to_name)
    cycles = detect_cycles(graph)
    if cycles:
        raise CycleError(
            f"Adding {from_name!r} -> {to_name!r} would create a dependency cycle: {' -> '.join(cycles[0])}"
        )

    row = DependencyEdgeRow(
        org_id=org_id, from_node_id=from_node.id, to_node_id=to_node.id, edge_type=edge_type, weight=weight
    )
    session.add(row)
    await session.flush()
    return row


async def remove_node(session: AsyncSession, org_id: UUID, name: str) -> bool:
    node = await _get_node_by_name(session, org_id, name)
    if node is None:
        return False
    await session.execute(
        delete(DependencyEdgeRow).where(
            DependencyEdgeRow.org_id == org_id,
            or_(DependencyEdgeRow.from_node_id == node.id, DependencyEdgeRow.to_node_id == node.id),
        )
    )
    await session.delete(node)
    await session.flush()
    return True


async def remove_edge(
    session: AsyncSession, org_id: UUID, from_name: str, to_name: str, edge_type: str = DEFAULT_EDGE_TYPE
) -> bool:
    from_node = await _get_node_by_name(session, org_id, from_name)
    to_node = await _get_node_by_name(session, org_id, to_name)
    if from_node is None or to_node is None:
        return False

    result = await session.execute(
        select(DependencyEdgeRow).where(
            DependencyEdgeRow.org_id == org_id,
            DependencyEdgeRow.from_node_id == from_node.id,
            DependencyEdgeRow.to_node_id == to_node.id,
            DependencyEdgeRow.edge_type == edge_type,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        return False
    await session.delete(row)
    await session.flush()
    return True


async def bulk_import(
    session: AsyncSession, org_id: UUID, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> None:
    """Seed a graph from a CSV/JSON description in one call. Nodes already
    present (by name) are left as-is rather than duplicated -- bulk_import
    is meant to be safe to re-run against a partially-seeded org.
    """
    existing_result = await session.execute(select(DependencyNodeRow).where(DependencyNodeRow.org_id == org_id))
    name_to_id: dict[str, UUID] = {row.name: row.id for row in existing_result.scalars()}

    for n in nodes:
        if n["name"] in name_to_id:
            continue
        row = DependencyNodeRow(
            org_id=org_id,
            name=n["name"],
            node_type=n["node_type"],
            is_critical=n.get("is_critical", False),
            alternative_for=n.get("alternative_for"),
            metadata_json=n.get("metadata") or {},
        )
        session.add(row)
        await session.flush()
        name_to_id[n["name"]] = row.id

    # Build the in-memory graph once (reflecting all nodes plus any edges
    # already persisted) and grow it incrementally -- checking for a cycle
    # via a fresh DB round trip per edge would be needless overhead for a
    # call whose entire purpose is loading many edges at once.
    graph = await build_graph(session, org_id)

    for e in edges:
        from_name, to_name = e["from_name"], e["to_name"]
        if from_name not in name_to_id or to_name not in name_to_id:
            raise ValueError(f"Unknown node referenced by edge: {from_name!r} -> {to_name!r}")

        graph.add_edge(from_name, to_name)
        cycles = detect_cycles(graph)
        if cycles:
            raise CycleError(
                f"Importing {from_name!r} -> {to_name!r} would create a dependency cycle: "
                f"{' -> '.join(cycles[0])}"
            )

        session.add(
            DependencyEdgeRow(
                org_id=org_id,
                from_node_id=name_to_id[from_name],
                to_node_id=name_to_id[to_name],
                edge_type=e.get("edge_type", DEFAULT_EDGE_TYPE),
                weight=e.get("weight", DEFAULT_EDGE_WEIGHT),
            )
        )

    await session.flush()


@dataclass(frozen=True)
class GraphSummary:
    node_count: int
    edge_count: int
    cycle_warnings: list[str] = field(default_factory=list)
    top_by_centrality: list[CentralityScore] = field(default_factory=list)


async def get_graph_summary(session: AsyncSession, org_id: UUID) -> GraphSummary:
    build_result = await validate_and_build(session, org_id)
    centrality = await compute_centrality(session, org_id)
    top = sorted(centrality.values(), key=lambda c: c.betweenness, reverse=True)[:TOP_CENTRALITY_COUNT]
    return GraphSummary(
        node_count=build_result.graph.number_of_nodes(),
        edge_count=build_result.graph.number_of_edges(),
        cycle_warnings=build_result.warnings,
        top_by_centrality=top,
    )
