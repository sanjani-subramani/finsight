"""FinGraph impact analysis -- pure graph traversal, no AI, answering
"what happens if X fails?" with a measured blast radius.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import networkx as nx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import ImpactResult
from app.models.tables import DependencyNode as DependencyNodeRow
from app.models.tables import TransactionEvent as TransactionEventRow
from app.modules.org.fingraph.graph_builder import build_graph

# A node's node_type distinguishes infrastructure from business process:
# a "service" is a thing that can fail (a gateway, a database, an API);
# a "workflow" is a business process BUILT ON services (onboarding, loan
# disbursal) and only ever fails because something underneath it did.
WORKFLOW_NODE_TYPE = "workflow"

# Window used to measure a provider's recent transaction RATE, which
# estimated_transactions then projects across failure_duration_hours (if
# given) rather than just reporting a fixed historical count.
RATE_LOOKBACK_HOURS = 24


@dataclass(frozen=True)
class CentralityScore:
    node_name: str
    betweenness: float
    is_critical: bool
    node_type: str


def _node_provider(graph: nx.DiGraph, node_name: str) -> str:
    """The PayTrace provider string this node corresponds to -- explicit
    metadata.provider if the org set one (node names are often a friendly
    label like "Razorpay Gateway" while PayTrace records "razorpay"),
    otherwise the node's own name.
    """
    metadata = graph.nodes[node_name].get("metadata") or {}
    provider = metadata.get("provider")
    return str(provider) if provider else node_name


async def estimate_transaction_volume(
    session: AsyncSession, org_id: UUID, provider_names: list[str], failure_duration_hours: float | None
) -> int:
    """CROSS-MODULE LINK to PayTrace: FinGraph alone gives you "8 services
    affected" -- connecting to PayTrace's actual transaction_events turns
    that into "18,420 transactions", which is what actually motivates
    action. failure_duration_hours (if given) projects the provider's
    recent rate forward across the expected outage length; without it,
    this simply reports how much volume moved through in the lookback
    window itself.
    """
    if not provider_names:
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(hours=RATE_LOOKBACK_HOURS)
    result = await session.execute(
        select(func.count(func.distinct(TransactionEventRow.transaction_ref))).where(
            TransactionEventRow.org_id == org_id,
            TransactionEventRow.provider.in_(provider_names),
            TransactionEventRow.occurred_at >= cutoff,
        )
    )
    count = result.scalar_one() or 0
    if failure_duration_hours is None:
        return int(count)

    rate_per_hour = count / RATE_LOOKBACK_HOURS
    return int(round(rate_per_hour * failure_duration_hours))


async def _alternative_providers_for(session: AsyncSession, org_id: UUID, node_ids: set[UUID | None]) -> list[str]:
    ids = {i for i in node_ids if i is not None}
    if not ids:
        return []
    result = await session.execute(
        select(DependencyNodeRow.name).where(
            DependencyNodeRow.org_id == org_id, DependencyNodeRow.alternative_for.in_(ids)
        )
    )
    return sorted(row[0] for row in result.all())


def _critical_paths_to(graph: nx.DiGraph, affected: set[str], targets: list[str]) -> list[list[str]]:
    """For each affected node marked critical, the shortest dependency
    chain to whichever failed node it's closest to -- the specific chain
    that EXPLAINS why it's affected, not just the fact that it is.
    """
    paths: list[list[str]] = []
    for node in sorted(affected):
        if not graph.nodes[node].get("is_critical"):
            continue
        candidates: list[list[str]] = []
        for target in targets:
            try:
                candidates.append(nx.shortest_path(graph, node, target))
            except nx.NetworkXNoPath:
                continue
        if candidates:
            paths.append(min(candidates, key=len))
    return paths


def _split_affected(graph: nx.DiGraph, affected: set[str]) -> tuple[list[str], list[str]]:
    services = sorted(n for n in affected if graph.nodes[n].get("node_type") != WORKFLOW_NODE_TYPE)
    workflows = sorted(n for n in affected if graph.nodes[n].get("node_type") == WORKFLOW_NODE_TYPE)
    return services, workflows


async def compute_blast_radius(
    session: AsyncSession,
    org_id: UUID,
    failed_node_name: str,
    failure_duration_hours: float | None = None,
) -> ImpactResult:
    graph = await build_graph(session, org_id)
    if failed_node_name not in graph:
        raise ValueError(f"Node not found in dependency graph: {failed_node_name!r}")

    # ancestors() in a "depends_on" graph gives everything that
    # TRANSITIVELY depends on the failed node -- i.e. everything affected
    # by its failure. This IS the reachability computation.
    affected = nx.ancestors(graph, failed_node_name)

    affected_services, affected_workflows = _split_affected(graph, affected)
    critical_paths = _critical_paths_to(graph, affected, [failed_node_name])

    failed_node_id = graph.nodes[failed_node_name].get("node_id")
    alternative_providers = await _alternative_providers_for(session, org_id, {failed_node_id})

    provider_names = sorted({_node_provider(graph, n) for n in [*affected_services, failed_node_name]})
    estimated_transactions = await estimate_transaction_volume(
        session, org_id, provider_names, failure_duration_hours
    )

    return ImpactResult(
        org_id=org_id,
        failed_node=failed_node_name,
        affected_services=affected_services,
        affected_workflows=affected_workflows,
        estimated_transactions=estimated_transactions,
        critical_paths=critical_paths,
        alternative_providers=alternative_providers,
    )


async def compute_centrality(session: AsyncSession, org_id: UUID) -> dict[str, CentralityScore]:
    """High betweenness centrality identifies single points of failure
    even when no one has manually flagged a node "critical" -- the graph
    structure itself reveals it: a node many dependency paths flow
    through is dangerous regardless of anyone's opinion of it.
    """
    graph = await build_graph(session, org_id)
    betweenness = nx.betweenness_centrality(graph)
    return {
        name: CentralityScore(
            node_name=name,
            betweenness=score,
            is_critical=bool(graph.nodes[name].get("is_critical", False)),
            node_type=str(graph.nodes[name].get("node_type", "")),
        )
        for name, score in betweenness.items()
    }


async def what_if_multiple(
    session: AsyncSession,
    org_id: UUID,
    failed_nodes: list[str],
    failure_duration_hours: float | None = None,
) -> ImpactResult:
    """Same algorithm as compute_blast_radius, but with the UNION of
    ancestors across multiple simultaneously-failed nodes -- "what if both
    our KYC provider AND our SMS provider go down together."
    """
    graph = await build_graph(session, org_id)
    missing = [n for n in failed_nodes if n not in graph]
    if missing:
        raise ValueError(f"Node(s) not found in dependency graph: {missing}")

    affected: set[str] = set()
    for node in failed_nodes:
        affected |= nx.ancestors(graph, node)
    affected -= set(failed_nodes)  # one failed node may itself depend on another failed node

    affected_services, affected_workflows = _split_affected(graph, affected)
    critical_paths = _critical_paths_to(graph, affected, failed_nodes)

    failed_ids = {graph.nodes[n].get("node_id") for n in failed_nodes}
    alternative_providers = await _alternative_providers_for(session, org_id, failed_ids)

    provider_names = sorted({_node_provider(graph, n) for n in [*affected_services, *failed_nodes]})
    estimated_transactions = await estimate_transaction_volume(
        session, org_id, provider_names, failure_duration_hours
    )

    return ImpactResult(
        org_id=org_id,
        failed_node=" + ".join(sorted(failed_nodes)),
        affected_services=affected_services,
        affected_workflows=affected_workflows,
        estimated_transactions=estimated_transactions,
        critical_paths=critical_paths,
        alternative_providers=alternative_providers,
    )
