"""FinGraph graph construction -- loads the persisted dependency graph
(Step 2's DependencyNode/DependencyEdge tables) into an in-memory NetworkX
DiGraph for traversal.

An edge A -> B means "A depends on B": if B fails, A is affected. This
direction matters everywhere downstream -- app.modules.org.fingraph.impact
computes blast radius via nx.ancestors(), which only makes sense because
edges point from dependent to dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import DependencyEdge as DependencyEdgeRow
from app.models.tables import DependencyNode as DependencyNodeRow


async def build_graph(session: AsyncSession, org_id: UUID) -> nx.DiGraph:
    nodes_result = await session.execute(select(DependencyNodeRow).where(DependencyNodeRow.org_id == org_id))
    nodes = list(nodes_result.scalars())

    edges_result = await session.execute(select(DependencyEdgeRow).where(DependencyEdgeRow.org_id == org_id))
    edges = list(edges_result.scalars())

    graph: nx.DiGraph = nx.DiGraph()
    for n in nodes:
        graph.add_node(
            n.name,
            node_id=n.id,
            node_type=n.node_type,
            is_critical=n.is_critical,
            alternative_for=n.alternative_for,
            metadata=n.metadata_json or {},
        )

    id_to_name = {n.id: n.name for n in nodes}
    for e in edges:
        from_name = id_to_name.get(e.from_node_id)
        to_name = id_to_name.get(e.to_node_id)
        if from_name is None or to_name is None:
            # A dangling edge (referencing a node not in this org's node
            # set) shouldn't happen via graph_management's own writes, but
            # silently skipping rather than raising keeps a single stray
            # row from taking down every blast-radius query for the org.
            continue
        graph.add_edge(from_name, to_name, edge_type=e.edge_type, weight=float(e.weight) if e.weight is not None else 1.0)

    return graph


def detect_cycles(graph: nx.DiGraph) -> list[list[str]]:
    """A dependency cycle (A depends on B depends on A) is almost always a
    modelling error -- nothing can "fail" cleanly in a cycle, and
    ancestors()/shortest_path() give confusing or misleading answers on
    one. Returns every cycle found; callers decide whether to warn or
    reject outright.
    """
    return [list(cycle) for cycle in nx.simple_cycles(graph)]


@dataclass(frozen=True)
class GraphBuildResult:
    graph: nx.DiGraph
    warnings: list[str] = field(default_factory=list)


async def validate_and_build(session: AsyncSession, org_id: UUID) -> GraphBuildResult:
    """We build defensively because a bad graph produces a confidently
    wrong blast radius, which is worse than no analysis at all -- cycles
    are surfaced as warnings rather than silently ignored.
    """
    graph = await build_graph(session, org_id)
    cycles = detect_cycles(graph)
    warnings = [
        f"Dependency cycle detected: {' -> '.join([*cycle, cycle[0]])}" for cycle in cycles
    ]
    return GraphBuildResult(graph=graph, warnings=warnings)
