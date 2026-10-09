"""RegImpactService -- the public face of app.modules.org.regimpact.

HARD REQUIREMENT: rules are NEVER auto-activated. RegulationExtractor
proposes candidate rules at status="pending_review"; only a human
reviewer's explicit "confirmed" decision (review_rule) makes a rule
eligible for run_impact_analysis. This mirrors Step 7's discovery pattern
(see app.modules.risk.discovery) -- AI proposes, a human is accountable
for accepting.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import ImpactReport as ImpactReportRow
from app.models.tables import Product as ProductRow
from app.models.tables import Regulation as RegulationRow
from app.models.tables import RegulatoryRule as RegulatoryRuleRow
from app.models.tables import Workflow as WorkflowRow
from app.modules.org.regimpact.extractor import RegulationExtractor
from app.modules.org.regimpact.impact import ImpactReportResult, compute_regulatory_impact
from app.platform.config import Settings


class RuleNotConfirmedError(ValueError):
    """Raised by run_impact_analysis when the target rule is not
    status="confirmed" -- THE enforcement point for the human-review
    requirement. There is no bypass parameter; a caller wanting impact
    analysis must first call review_rule(decision="confirmed").
    """


class RegImpactService:
    async def create_product(
        self, session: AsyncSession, org_id: UUID, name: str, description: str | None, category: str
    ) -> ProductRow:
        row = ProductRow(org_id=org_id, name=name, description=description, category=category)
        session.add(row)
        await session.flush()
        return row

    async def create_workflow(
        self,
        session: AsyncSession,
        org_id: UUID,
        name: str,
        description: str | None,
        uses_service_node_ids: list[UUID],
        uses_product_ids: list[UUID],
    ) -> WorkflowRow:
        row = WorkflowRow(
            org_id=org_id,
            name=name,
            description=description,
            uses_service_node_ids=[str(i) for i in uses_service_node_ids],
            uses_product_ids=[str(i) for i in uses_product_ids],
        )
        session.add(row)
        await session.flush()
        return row

    async def ingest_regulation(
        self,
        session: AsyncSession,
        org_id: UUID,
        title: str,
        source_text: str,
        source_url: str | None,
        effective_date: date | None,
        ingested_by: UUID | None,
        *,
        settings: Settings | None = None,
        http_client: Any | None = None,
    ) -> RegulationRow:
        regulation = RegulationRow(
            org_id=org_id,
            title=title,
            source_text=source_text,
            source_url=source_url,
            effective_date=effective_date,
            ingested_by=ingested_by,
        )
        session.add(regulation)
        await session.flush()

        # Every extracted item lands as status="pending_review" -- never
        # confirmed, never auto-mapped. If extraction returns [] (no LLM
        # key, or the model/response failed validation entirely), the
        # regulation is still stored; it simply has zero rules, which is
        # this system's "requires manual entry" signal rather than a crash.
        extracted = await RegulationExtractor().extract(source_text, settings=settings, http_client=http_client)
        for item in extracted:
            session.add(
                RegulatoryRuleRow(
                    regulation_id=regulation.id,
                    org_id=org_id,
                    rule_text=item.rule_summary,
                    trigger_condition=item.trigger_condition,
                    threshold_json=item.threshold,
                    required_action=item.required_action,
                    deadline_days=item.deadline_days,
                    applies_to_product_categories=item.applies_to,
                    extraction_confidence=item.confidence,
                    ambiguities=item.ambiguities,
                    status="pending_review",
                )
            )
        await session.flush()
        return regulation

    async def review_rule(
        self,
        session: AsyncSession,
        org_id: UUID,
        rule_id: UUID,
        decision: Literal["confirmed", "rejected"],
        reviewer_id: UUID,
        note: str | None = None,
    ) -> RegulatoryRuleRow | None:
        rule = await self._get_rule(session, org_id, rule_id)
        if rule is None:
            return None
        rule.status = decision
        rule.reviewed_by = reviewer_id
        rule.reviewed_at = datetime.now(timezone.utc)
        rule.review_note = note
        await session.flush()
        return rule

    async def run_impact_analysis(self, session: AsyncSession, org_id: UUID, rule_id: UUID) -> ImpactReportResult:
        rule = await self._get_rule(session, org_id, rule_id)
        if rule is None:
            raise ValueError(f"No such regulatory rule: {rule_id}")
        if rule.status != "confirmed":
            raise RuleNotConfirmedError(
                f"Rule {rule_id} is {rule.status!r}, not 'confirmed' -- it must be reviewed and "
                "confirmed by a human before impact analysis can run."
            )
        return await compute_regulatory_impact(session, org_id, rule)

    async def get_pending_review(self, session: AsyncSession, org_id: UUID) -> list[RegulatoryRuleRow]:
        result = await session.execute(
            select(RegulatoryRuleRow).where(
                RegulatoryRuleRow.org_id == org_id, RegulatoryRuleRow.status == "pending_review"
            )
        )
        return list(result.scalars())

    async def get_confirmed_rules(self, session: AsyncSession, org_id: UUID) -> list[RegulatoryRuleRow]:
        """Org-wide confirmed rules -- the dashboard's Compliance page
        (Step 18) lists these as candidates for run_impact_analysis,
        the same way get_pending_review backs its review queue.
        """
        result = await session.execute(
            select(RegulatoryRuleRow).where(
                RegulatoryRuleRow.org_id == org_id, RegulatoryRuleRow.status == "confirmed"
            )
        )
        return list(result.scalars())

    async def get_impact_history(
        self, session: AsyncSession, org_id: UUID, regulation_id: UUID | None = None
    ) -> list[ImpactReportRow]:
        conditions = [ImpactReportRow.org_id == org_id]
        if regulation_id is not None:
            conditions.append(ImpactReportRow.regulation_id == regulation_id)
        result = await session.execute(
            select(ImpactReportRow).where(*conditions).order_by(ImpactReportRow.generated_at.desc())
        )
        return list(result.scalars())

    async def _get_rule(self, session: AsyncSession, org_id: UUID, rule_id: UUID) -> RegulatoryRuleRow | None:
        result = await session.execute(
            select(RegulatoryRuleRow).where(RegulatoryRuleRow.id == rule_id, RegulatoryRuleRow.org_id == org_id)
        )
        return result.scalar_one_or_none()
