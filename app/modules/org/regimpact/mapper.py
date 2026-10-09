"""Deterministic mapping from a confirmed regulatory rule to the
products, workflows, and FinGraph service nodes it affects. No AI here --
extractor.py is the only place this package uses an LLM.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import DependencyNode as DependencyNodeRow
from app.models.tables import Product as ProductRow
from app.models.tables import RegulatoryRule as RegulatoryRuleRow
from app.models.tables import Workflow as WorkflowRow


async def map_rule_to_products(session: AsyncSession, org_id: UUID, rule: RegulatoryRuleRow) -> list[ProductRow]:
    """Exact category match only -- deliberately simple and conservative.
    A rule matching the wrong product because of a fuzzy/guessed category
    would itself BE a compliance failure, so this requires an exact,
    already-reviewed category tag on the product rather than inferring
    one from the rule text.
    """
    categories = rule.applies_to_product_categories or []
    if not categories:
        return []
    result = await session.execute(
        select(ProductRow).where(ProductRow.org_id == org_id, ProductRow.category.in_(categories))
    )
    return list(result.scalars())


async def map_products_to_workflows(
    session: AsyncSession, org_id: UUID, products: list[ProductRow]
) -> list[WorkflowRow]:
    if not products:
        return []
    product_ids = {str(p.id) for p in products}
    result = await session.execute(select(WorkflowRow).where(WorkflowRow.org_id == org_id))
    return [w for w in result.scalars() if product_ids & {str(i) for i in (w.uses_product_ids or [])}]


async def map_workflows_to_services(
    session: AsyncSession, org_id: UUID, workflows: list[WorkflowRow]
) -> list[str]:
    """Returns FinGraph node NAMES, not ids -- callers pass these straight
    into app.modules.org.fingraph.graph_builder.build_graph's
    node-name-keyed graph.
    """
    node_id_strings: set[str] = set()
    for w in workflows:
        node_id_strings.update(str(i) for i in (w.uses_service_node_ids or []))
    if not node_id_strings:
        return []

    node_ids = {UUID(i) for i in node_id_strings}
    result = await session.execute(
        select(DependencyNodeRow.name).where(
            DependencyNodeRow.org_id == org_id, DependencyNodeRow.id.in_(node_ids)
        )
    )
    return sorted(row[0] for row in result.all())
