"""ThreatService — the public face of app.modules.threat.

Routes a submission to the right channel analyzer, combines signals into
one risk_score, checks the threat's actual financial impact against the
Twin (impact.py — the differentiator), persists it, and publishes it to
the event bus. Routing the resulting decision is deliberately NOT done
here: app.modules.pipeline.handlers.handle_threat_event (subscribed to
Topic.THREAT_EVENT) is the single place that calls DecisionService.decide
for a threat, so a threat can never produce two interventions from two
different call sites racing each other.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contracts.events import (
    DataSource,
    FinancialEventType,
    ThreatCategory,
    ThreatChannel,
    ThreatEvent,
    ThreatSignal,
)
from app.models.tables import FinancialEvent
from app.models.tables import ThreatEvent as ThreatEventRow
from app.modules.threat.call_analyzer import analyse_transcript
from app.modules.threat.impact import (
    SEVERITY_MULTIPLIER,
    SEVERITY_MULTIPLIER_THRESHOLD,
    ThreatImpact,
    assess_financial_impact,
)
from app.modules.threat.qr_analyzer import analyse_qr
from app.modules.threat.sms_analyzer import ThreatAnalysis, analyse_sms
from app.modules.threat.url_analyzer import analyse_url
from app.platform.eventbus import EventBus, Topic
from app.platform.logging import get_logger

logger = get_logger(__name__)

TYPICAL_AMOUNT_LOOKBACK_DAYS = 90
RAW_REFERENCE_MAX_LENGTH = 500

_CHANNEL_DATA_SOURCE: dict[ThreatChannel, DataSource] = {
    ThreatChannel.sms: DataSource.sms,
    ThreatChannel.call: DataSource.manual,
    ThreatChannel.qr: DataSource.manual,
    ThreatChannel.link: DataSource.manual,
}


@dataclass(frozen=True)
class ThreatAnalysisResult:
    threat: ThreatEvent
    impact: ThreatImpact | None


def _primary_category(signals: list[ThreatSignal]) -> ThreatCategory:
    if not signals:
        return ThreatCategory.unknown
    return max(signals, key=lambda signal: signal.weight).category


def _score_from_signals(signals: list[ThreatSignal]) -> float:
    # Same additive-only formula as sms_analyzer._compute_final_score,
    # for channels (url/qr) whose analyzers return raw signals rather
    # than a pre-built ThreatAnalysis.
    return min(1.0, sum(signal.weight for signal in signals) / 100)


class ThreatService:
    async def analyse(
        self,
        session: AsyncSession,
        user_id: UUID,
        channel: ThreatChannel,
        payload: dict[str, Any],
        *,
        trace_id: str | None = None,
    ) -> ThreatAnalysisResult:
        analysis, requested_amount, payee_identifier, transcript_excerpt, raw_reference = await self._route(
            session, user_id, channel, payload
        )

        threat = ThreatEvent(
            threat_id=uuid4(),
            user_id=user_id,
            channel=channel,
            risk_score=analysis.final_score,
            signals=analysis.signals,
            primary_category=_primary_category(analysis.signals),
            requested_amount=requested_amount,
            payee_identifier=payee_identifier,
            raw_reference=raw_reference,
            transcript_excerpt=transcript_excerpt,
            data_source=_CHANNEL_DATA_SOURCE[channel],
            detection_confidence=0.75 if analysis.llm_escalated else 0.9,
        )

        impact: ThreatImpact | None = None
        if requested_amount is not None:
            impact = await assess_financial_impact(session, user_id, threat)
            if impact is not None and impact.prob_after >= SEVERITY_MULTIPLIER_THRESHOLD:
                amplified_score = min(1.0, threat.risk_score * SEVERITY_MULTIPLIER)
                threat = threat.model_copy(update={"risk_score": amplified_score})

        await self._persist(session, threat, impact)

        resolved_trace_id = trace_id or str(threat.threat_id)
        await EventBus().publish(
            Topic.THREAT_EVENT,
            {"threat_id": str(threat.threat_id), "user_id": str(user_id)},
            resolved_trace_id,
        )

        return ThreatAnalysisResult(threat=threat, impact=impact)

    async def get_events(self, session: AsyncSession, user_id: UUID, limit: int = 50) -> list[ThreatEventRow]:
        result = await session.execute(
            select(ThreatEventRow)
            .where(ThreatEventRow.user_id == user_id)
            .order_by(ThreatEventRow.detected_at.desc())
            .limit(limit)
        )
        return list(result.scalars())

    async def get_event(self, session: AsyncSession, user_id: UUID, threat_id: UUID) -> ThreatEventRow | None:
        result = await session.execute(
            select(ThreatEventRow).where(ThreatEventRow.id == threat_id, ThreatEventRow.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # -- routing --------------------------------------------------------

    async def _route(
        self, session: AsyncSession, user_id: UUID, channel: ThreatChannel, payload: dict[str, Any]
    ) -> tuple[ThreatAnalysis, Decimal | None, str | None, str | None, str | None]:
        """Returns (analysis, requested_amount, payee_identifier,
        transcript_excerpt, raw_reference)."""
        if channel == ThreatChannel.sms:
            body = str(payload["body"])
            sender = str(payload.get("sender", ""))
            analysis = await analyse_sms(body, sender)
            return analysis, analysis.requested_amount, analysis.payee_identifier, None, body[:RAW_REFERENCE_MAX_LENGTH]

        if channel == ThreatChannel.call:
            transcript = str(payload["transcript"])
            analysis = await analyse_transcript(transcript)
            return analysis, None, None, transcript[:RAW_REFERENCE_MAX_LENGTH], transcript[:RAW_REFERENCE_MAX_LENGTH]

        if channel == ThreatChannel.link:
            url = str(payload["url"])
            url_result = await analyse_url(url)
            analysis = ThreatAnalysis(
                signals=url_result.signals,
                rule_score=_score_from_signals(url_result.signals),
                final_score=_score_from_signals(url_result.signals),
            )
            return analysis, None, None, None, url[:RAW_REFERENCE_MAX_LENGTH]

        if channel == ThreatChannel.qr:
            qr_payload = str(payload["qr_payload"])
            claimed_merchant_name = payload.get("claimed_merchant_name")
            typical_amount = await self._typical_transaction_amount(session, user_id)
            # known_payee_vpas isn't wired to a real "VPA payment history"
            # table (none exists yet) — the newly-seen-payee check is
            # skipped rather than approximated against an unrelated field.
            qr_result = await analyse_qr(
                qr_payload, claimed_merchant_name=claimed_merchant_name, typical_transaction_amount=typical_amount
            )
            analysis = ThreatAnalysis(
                signals=qr_result.signals,
                rule_score=_score_from_signals(qr_result.signals),
                final_score=_score_from_signals(qr_result.signals),
            )
            return analysis, qr_result.amount, qr_result.payee_vpa, None, qr_payload[:RAW_REFERENCE_MAX_LENGTH]

        raise ValueError(f"Unsupported threat channel: {channel}")

    async def _typical_transaction_amount(self, session: AsyncSession, user_id: UUID) -> Decimal | None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=TYPICAL_AMOUNT_LOOKBACK_DAYS)
        result = await session.execute(
            select(FinancialEvent.amount).where(
                FinancialEvent.user_id == user_id,
                FinancialEvent.event_type == FinancialEventType.expense.value,
                FinancialEvent.occurred_at >= cutoff,
                FinancialEvent.amount.is_not(None),
            )
        )
        amounts = [float(row) for row in result.scalars() if row is not None]
        if not amounts:
            return None
        return Decimal(str(round(float(np.median(amounts)), 2)))

    # -- persistence --------------------------------------------------------

    async def _persist(self, session: AsyncSession, threat: ThreatEvent, impact: ThreatImpact | None) -> ThreatEventRow:
        row = ThreatEventRow(
            id=threat.threat_id,
            user_id=threat.user_id,
            channel=threat.channel.value,
            risk_score=threat.risk_score,
            primary_category=threat.primary_category.value,
            signals=[signal.model_dump(mode="json") for signal in threat.signals],
            requested_amount=threat.requested_amount,
            payee_identifier=threat.payee_identifier,
            raw_reference=threat.raw_reference,
            transcript_excerpt=threat.transcript_excerpt,
            data_source=threat.data_source.value,
            detection_confidence=threat.detection_confidence,
            financial_impact=_impact_to_dict(impact),
        )
        session.add(row)
        await session.flush()
        return row


def _impact_to_dict(impact: ThreatImpact | None) -> dict[str, Any] | None:
    if impact is None:
        return None
    return {
        "would_cause_shortfall": impact.would_cause_shortfall,
        "prob_before": impact.prob_before,
        "prob_after": impact.prob_after,
        "obligations_at_risk": impact.obligations_at_risk,
        "days_until_first_impact": impact.days_until_first_impact,
        "human_statement": impact.human_statement,
    }
