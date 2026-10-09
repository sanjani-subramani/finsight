from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.paytrace import (
    AnomalyResponse,
    ClassificationResponse,
    PaymentHealthResponse,
    ProviderAlertResponse,
    ProviderStatsResponse,
    TimelineEntryResponse,
    TransactionDetailResponse,
    TransactionEventBatchRequest,
    TransactionEventRequest,
    TransactionSearchResponse,
    TransactionStateResponse,
    TransactionSummaryResponse,
)
from app.contracts.events import TransactionEvent, TxnStage
from app.models.tables import User
from app.modules.org.paytrace.analytics import PaymentHealth, ProviderAlert
from app.modules.org.paytrace.classifier import FailureClassification, FailureMode
from app.modules.org.paytrace.service import (
    PayTraceService,
    TransactionDetail,
    TransactionSearchFilters,
    TransactionSummary,
)
from app.modules.org.paytrace.state_machine import TransactionState
from app.platform.database import get_session
from app.platform.deps import require_roles

router = APIRouter(prefix="/org/{org_id}/paytrace", tags=["paytrace"])

# Any org member can view PayTrace data; only owner/ops_engineer can feed
# it new events. recon_analyst and viewer exist specifically to look at
# reconciliation-adjacent data like this without being able to write it.
_READ_ROLES = ("owner", "ops_engineer", "recon_analyst", "viewer")
_WRITE_ROLES = ("owner", "ops_engineer")


def _to_request_event(org_id: UUID, payload: TransactionEventRequest) -> TransactionEvent:
    return TransactionEvent(
        org_id=org_id,
        transaction_ref=payload.transaction_ref,
        stage=payload.stage,
        occurred_at=payload.occurred_at,
        amount=payload.amount,
        provider=payload.provider,
        provider_ref=payload.provider_ref,
        error_code=payload.error_code,
        latency_ms=payload.latency_ms,
        idempotency_key=payload.idempotency_key,
        raw_payload=payload.raw_payload,
    )


def _to_state_response(state: TransactionState) -> TransactionStateResponse:
    return TransactionStateResponse(
        transaction_ref=state.transaction_ref,
        current_stage=state.current_stage.value if state.current_stage else None,
        timeline=[
            TimelineEntryResponse(
                stage=entry.stage.value,
                occurred_at=entry.occurred_at,
                amount=entry.amount,
                provider=entry.provider,
                provider_ref=entry.provider_ref,
                error_code=entry.error_code,
                latency_ms=entry.latency_ms,
            )
            for entry in state.timeline
        ],
        anomalies=[
            AnomalyResponse(
                kind=anomaly.kind,
                description=anomaly.description,
                from_stage=anomaly.from_stage.value if anomaly.from_stage else None,
                to_stage=anomaly.to_stage.value if anomaly.to_stage else None,
                occurred_at=anomaly.occurred_at,
                gap_ms=anomaly.gap_ms,
            )
            for anomaly in state.anomalies
        ],
        duration_by_stage={stage.value: ms for stage, ms in state.duration_by_stage.items()},
        total_duration_ms=state.total_duration_ms,
        is_terminal=state.is_terminal,
    )


def _to_classification_response(classification: FailureClassification) -> ClassificationResponse:
    return ClassificationResponse(
        mode=classification.mode.value,
        confidence=classification.confidence,
        evidence=classification.evidence,
        recommended_action=classification.recommended_action,
        human_summary=classification.human_summary,
    )


def _to_detail_response(detail: TransactionDetail) -> TransactionDetailResponse:
    return TransactionDetailResponse(
        state=_to_state_response(detail.state),
        classification=_to_classification_response(detail.classification),
    )


def _to_summary_response(summary: TransactionSummary) -> TransactionSummaryResponse:
    return TransactionSummaryResponse(
        transaction_ref=summary.transaction_ref,
        current_stage=summary.current_stage.value if summary.current_stage else None,
        provider=summary.provider,
        last_event_at=summary.last_event_at,
        is_terminal=summary.is_terminal,
        failure_mode=summary.classification.mode.value,
        confidence=summary.classification.confidence,
        recommended_action=summary.classification.recommended_action,
    )


def _to_health_response(health: PaymentHealth) -> PaymentHealthResponse:
    return PaymentHealthResponse(
        total_transactions=health.total_transactions,
        success_rate=health.success_rate,
        failure_breakdown={mode.value: count for mode, count in health.failure_breakdown.items()},
        avg_latency_by_stage={stage.value: ms for stage, ms in health.avg_latency_by_stage.items()},
        p95_latency_by_stage={stage.value: ms for stage, ms in health.p95_latency_by_stage.items()},
        webhook_success_rate=health.webhook_success_rate,
        settlement_success_rate=health.settlement_success_rate,
        providers=[
            ProviderStatsResponse(
                provider=p.provider,
                total_transactions=p.total_transactions,
                success_rate=p.success_rate,
                avg_latency_ms=p.avg_latency_ms,
                failure_breakdown={mode.value: count for mode, count in p.failure_breakdown.items()},
            )
            for p in health.providers
        ],
        anomaly_count=health.anomaly_count,
        computed_at=health.computed_at,
    )


def _to_alert_response(alert: ProviderAlert) -> ProviderAlertResponse:
    return ProviderAlertResponse(
        provider=alert.provider,
        current_failure_rate=alert.current_failure_rate,
        baseline_failure_rate=alert.baseline_failure_rate,
        ratio=alert.ratio,
        current_transaction_count=alert.current_transaction_count,
        message=alert.message,
    )


@router.post("/events", response_model=TransactionStateResponse)
async def ingest_event(
    org_id: UUID,
    payload: TransactionEventRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> TransactionStateResponse:
    state = await PayTraceService().ingest_event(session, org_id, _to_request_event(org_id, payload))
    return _to_state_response(state)


@router.post("/events/batch", response_model=dict[str, TransactionStateResponse])
async def ingest_events_batch(
    org_id: UUID,
    payload: TransactionEventBatchRequest,
    current_user: User = Depends(require_roles(*_WRITE_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> dict[str, TransactionStateResponse]:
    events = [_to_request_event(org_id, item) for item in payload.events]
    results = await PayTraceService().ingest_batch(session, org_id, events)
    return {ref: _to_state_response(state) for ref, state in results.items()}


@router.get("/transactions", response_model=TransactionSearchResponse)
async def search_transactions(
    org_id: UUID,
    status_filter: TxnStage | None = Query(None, alias="status"),
    provider: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    failure_mode: FailureMode | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> TransactionSearchResponse:
    filters = TransactionSearchFilters(
        status=status_filter,
        provider=provider,
        date_from=datetime.fromisoformat(date_from) if date_from else None,
        date_to=datetime.fromisoformat(date_to) if date_to else None,
        failure_mode=failure_mode,
    )
    result = await PayTraceService().search_transactions(session, org_id, filters, limit=limit, offset=offset)
    return TransactionSearchResponse(
        items=[_to_summary_response(item) for item in result.items],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
    )


@router.get("/transactions/{transaction_ref}", response_model=TransactionDetailResponse)
async def get_transaction(
    org_id: UUID,
    transaction_ref: str,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> TransactionDetailResponse:
    detail = await PayTraceService().get_transaction(session, org_id, transaction_ref)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return _to_detail_response(detail)


@router.get("/health", response_model=PaymentHealthResponse)
async def get_health(
    org_id: UUID,
    window_hours: int = Query(24, ge=1, le=24 * 30),
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> PaymentHealthResponse:
    health = await PayTraceService().get_health(session, org_id, window_hours=window_hours)
    return _to_health_response(health)


@router.get("/providers", response_model=list[ProviderStatsResponse])
async def get_providers(
    org_id: UUID,
    window_hours: int = Query(24, ge=1, le=24 * 30),
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[ProviderStatsResponse]:
    health = await PayTraceService().get_health(session, org_id, window_hours=window_hours)
    return [
        ProviderStatsResponse(
            provider=p.provider,
            total_transactions=p.total_transactions,
            success_rate=p.success_rate,
            avg_latency_ms=p.avg_latency_ms,
            failure_breakdown={mode.value: count for mode, count in p.failure_breakdown.items()},
        )
        for p in health.providers
    ]


@router.get("/alerts", response_model=list[ProviderAlertResponse])
async def get_alerts(
    org_id: UUID,
    current_user: User = Depends(require_roles(*_READ_ROLES)),
    session: AsyncSession = Depends(get_session),
) -> list[ProviderAlertResponse]:
    alerts = await PayTraceService().get_provider_alerts(session, org_id)
    return [_to_alert_response(a) for a in alerts]
