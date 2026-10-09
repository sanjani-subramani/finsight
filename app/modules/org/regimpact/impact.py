"""RegImpact's impact computation -- THE REUSE POINT.

This module does not reimplement graph traversal or transaction-volume
estimation: it calls the exact same FinGraph primitives
(graph_builder.build_graph, networkx.ancestors) and the same
PayTrace-linked volume estimator already built and tested in Step 16.
Regulatory impact analysis is not a new algorithm -- it is Step 16's
blast-radius computation, entered from a confirmed compliance rule
instead of a simulated failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

import networkx as nx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import ImpactReport as ImpactReportRow
from app.models.tables import RegulatoryRule as RegulatoryRuleRow
from app.modules.org.fingraph.graph_builder import build_graph
from app.modules.org.fingraph.impact import estimate_transaction_volume
from app.modules.org.regimpact.mapper import map_products_to_workflows, map_rule_to_products, map_workflows_to_services


@dataclass(frozen=True)
class ImpactReportResult:
    id: UUID
    org_id: UUID
    regulation_id: UUID
    rule_id: UUID
    affected_products: list[str]
    affected_workflows: list[str]
    affected_service_nodes: list[str]
    estimated_transactions: int
    required_changes: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def _describe_required_change(node_name: str, rule: RegulatoryRuleRow) -> str:
    deadline = (
        f"within {rule.deadline_days} day(s)" if rule.deadline_days is not None else "with no specified deadline"
    )
    return f"{node_name}: {rule.required_action} ({deadline})."


async def compute_regulatory_impact(
    session: AsyncSession, org_id: UUID, rule: RegulatoryRuleRow
) -> ImpactReportResult:
    products = await map_rule_to_products(session, org_id, rule)
    workflows = await map_products_to_workflows(session, org_id, products)
    direct_service_names = await map_workflows_to_services(session, org_id, workflows)

    # RegImpact does not reimplement graph traversal: it calls the same
    # FinGraph primitives already built and tested in Step 16. A
    # regulatory change to a directly-used service also affects
    # everything that depends on THAT service, exactly as a failure
    # would -- so ancestors() (not just the directly-used set) is what
    # "requires review" actually means here.
    graph = await build_graph(session, org_id)
    all_affected: set[str] = set(direct_service_names)
    for node_name in direct_service_names:
        if node_name in graph:
            all_affected |= nx.ancestors(graph, node_name)

    affected_service_nodes = sorted(all_affected)

    # CROSS-MODULE LINK to PayTrace: reuses Step 16's own rate-based
    # estimator rather than re-querying transaction_events itself.
    provider_names = affected_service_nodes or direct_service_names
    estimated_transactions = await estimate_transaction_volume(session, org_id, provider_names, None)

    required_changes = [_describe_required_change(node_name, rule) for node_name in affected_service_nodes]

    now = datetime.now(timezone.utc)
    row = ImpactReportRow(
        org_id=org_id,
        regulation_id=rule.regulation_id,
        rule_id=rule.id,
        affected_products=[p.name for p in products],
        affected_workflows=[w.name for w in workflows],
        affected_service_nodes=affected_service_nodes,
        estimated_transactions=estimated_transactions,
        required_changes=required_changes,
        generated_at=now,
    )
    session.add(row)
    await session.flush()

    return ImpactReportResult(
        id=row.id,
        org_id=org_id,
        regulation_id=rule.regulation_id,
        rule_id=rule.id,
        affected_products=[p.name for p in products],
        affected_workflows=[w.name for w in workflows],
        affected_service_nodes=affected_service_nodes,
        estimated_transactions=estimated_transactions,
        required_changes=required_changes,
        generated_at=now,
    )
