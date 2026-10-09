from __future__ import annotations

import io
import json
from datetime import date, datetime, time, timezone
from uuid import UUID, uuid4

import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.ingestion import (
    BatchIngestionResponse,
    CsvImportRequest,
    FinancialEventResponse,
    IngestAcceptedResponse,
    IngestionResponse,
    IngestionStatusResponse,
    ManualEventRequest,
    QuarantinedInputResponse,
    SmsIngestRequest,
)
from app.contracts.events import DataSource, FinancialEventType
from app.models.tables import FinancialEvent, QuarantinedInput, User
from app.modules.confidence.service import ConfidenceService
from app.modules.ingestion.normalizer import IngestionOutcome, Normalizer, normalize_csv_row, normalize_manual
from app.modules.ingestion.repository import quarantine_raw, write_event
from app.modules.pipeline.handlers import get_pipeline_status, set_pipeline_status
from app.modules.twin.service import TwinService
from app.platform.audit import write_audit
from app.platform.database import get_session
from app.platform.deps import get_client_ip, get_current_user
from app.platform.eventbus import EventBus, Topic, get_redis_client
from app.platform.idempotency import idempotent, store_idempotent_response
from app.platform.logging import get_logger
from app.platform.ratelimit import check_rate_limit

router = APIRouter(prefix="/ingest", tags=["ingestion"])
logger = get_logger(__name__)

MAX_BATCH_SIZE = 100
BATCH_RATE_LIMIT = 5
BATCH_RATE_WINDOW_SECONDS = 60


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


async def _enforce_batch_rate_limit(
    current_user: User = Depends(get_current_user),
) -> User:
    allowed = await check_rate_limit(
        f"ratelimit:ingest_sms_batch:{current_user.id}",
        limit=BATCH_RATE_LIMIT,
        window_seconds=BATCH_RATE_WINDOW_SECONDS,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many batch ingestion requests; slow down.",
        )
    return current_user


async def _persist_outcome(
    session: AsyncSession,
    outcome: IngestionOutcome,
    current_user: User,
    request: Request,
    *,
    sender: str | None,
) -> IngestionResponse:
    if outcome.quarantined or outcome.event is None:
        await quarantine_raw(
            session,
            user_id=current_user.id,
            raw_input=outcome.raw_input,
            sender=sender,
            reason=outcome.reason,
            attempted_methods=[outcome.method],
        )
        await write_audit(
            session,
            actor_user_id=current_user.id,
            action="ingestion.quarantined",
            resource_type="quarantined_input",
            ip_address=get_client_ip(request),
            trace_id=_trace_id(request),
            payload={"reason": outcome.reason, "method": outcome.method},
        )
        return IngestionResponse(
            event_id=None,
            method=outcome.method,
            confidence=outcome.confidence,
            was_duplicate=False,
            quarantined=True,
            reason=outcome.reason,
        )

    row, was_duplicate = await write_event(session, outcome.event, outcome.event.source_ref)
    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="ingestion.duplicate" if was_duplicate else "ingestion.created",
        resource_type="financial_event",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"method": outcome.method, "confidence": outcome.confidence},
    )
    if not was_duplicate:
        # Step 3's write_event only catches an exact re-ingestion of the
        # same source_ref. This runs the confidence engine's own,
        # harder, cross-source duplicate/conflict detection on every
        # genuinely new row.
        await ConfidenceService().process_event(session, row.id)
        # Must run AFTER confidence processing: if that just marked this
        # row a cross-source duplicate, the fold needs to see the fresh
        # duplicate_of value so it correctly skips it (apply_event checks
        # this) instead of double-counting the cash movement.
        await TwinService().on_event_ingested(session, row)

    return IngestionResponse(
        event_id=row.id,
        method=outcome.method,
        confidence=outcome.confidence,
        was_duplicate=was_duplicate,
        quarantined=False,
        reason=outcome.reason,
    )


@router.post("/sms", response_model=IngestAcceptedResponse | IngestionResponse)
async def ingest_sms(
    payload: SmsIngestRequest,
    request: Request,
    response: Response,
    # Exists for deterministic tests and demos that need the old
    # synchronous behaviour (an immediate, fully-processed response) --
    # NOT for production use, which should always take the default async
    # path so heavy processing (confidence, twin, simulation, risk,
    # decision) never runs inline in the request.
    sync: bool = Query(False),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> IngestAcceptedResponse | IngestionResponse:
    normalizer = Normalizer()
    outcome = await normalizer.normalize_sms(
        payload.raw_sms, payload.sender, current_user.id, received_at=payload.received_at
    )

    if sync:
        response.status_code = status.HTTP_201_CREATED
        return await _persist_outcome(session, outcome, current_user, request, sender=payload.sender)

    response.status_code = status.HTTP_202_ACCEPTED
    trace_id = _trace_id(request) or str(uuid4())

    if outcome.quarantined or outcome.event is None:
        await quarantine_raw(
            session,
            user_id=current_user.id,
            raw_input=outcome.raw_input,
            sender=payload.sender,
            reason=outcome.reason,
            attempted_methods=[outcome.method],
        )
        await write_audit(
            session,
            actor_user_id=current_user.id,
            action="ingestion.quarantined",
            resource_type="quarantined_input",
            ip_address=get_client_ip(request),
            trace_id=trace_id,
            payload={"reason": outcome.reason, "method": outcome.method},
        )
        return IngestAcceptedResponse(
            trace_id=trace_id, event_id=None, quarantined=True, reason=outcome.reason, status="quarantined"
        )

    row, was_duplicate = await write_event(session, outcome.event, outcome.event.source_ref)
    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="ingestion.duplicate" if was_duplicate else "ingestion.created",
        resource_type="financial_event",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=trace_id,
        payload={"method": outcome.method, "confidence": outcome.confidence},
    )

    if was_duplicate:
        # A duplicate never triggers new downstream processing -- the
        # confidence engine and twin fold already ran for the original row.
        pipeline_stage = "duplicate"
    else:
        # COMMIT before publishing, not after: get_session's dependency
        # teardown would otherwise commit this row only after the
        # response is built, by which point the message below is already
        # on the bus. A consumer (the real ARQ worker in production, or
        # this test suite's in-process pipeline_worker) that reads it
        # before that teardown commit runs queries financial_events on
        # its OWN session/connection and — under real transaction
        # isolation, unlike this repo's SQLite unit tests, which never
        # exercise this ordering against a second connection — gets
        # nothing back: "no financial_events row with id ...". The row
        # (and its audit trail above) must be durably visible to other
        # connections before anything is told it exists.
        await session.commit()
        redis_client = get_redis_client()
        await set_pipeline_status(redis_client, trace_id, "queued")
        await EventBus(redis_client).publish(
            Topic.FINANCIAL_EVENT, {"event_id": str(row.id), "user_id": str(current_user.id)}, trace_id
        )
        pipeline_stage = "queued"

    return IngestAcceptedResponse(
        trace_id=trace_id, event_id=row.id, quarantined=False, reason=outcome.reason, status=pipeline_stage
    )


@router.get("/status/{trace_id}", response_model=IngestionStatusResponse)
async def get_ingestion_status(
    trace_id: str,
    current_user: User = Depends(get_current_user),
) -> IngestionStatusResponse:
    redis_client = get_redis_client()
    stage = await get_pipeline_status(redis_client, trace_id)
    return IngestionStatusResponse(trace_id=trace_id, status=stage or "unknown")


@router.post("/sms/batch", response_model=BatchIngestionResponse)
async def ingest_sms_batch(
    items: list[SmsIngestRequest],
    request: Request,
    current_user: User = Depends(_enforce_batch_rate_limit),
    session: AsyncSession = Depends(get_session),
) -> BatchIngestionResponse:
    if len(items) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Batch size cannot exceed {MAX_BATCH_SIZE}",
        )

    normalizer = Normalizer()
    results: list[IngestionResponse] = []
    created = duplicates = quarantined = 0

    for item in items:
        # One item's failure must never abort the rest of the batch.
        try:
            outcome = await normalizer.normalize_sms(
                item.raw_sms, item.sender, current_user.id, received_at=item.received_at
            )
            result = await _persist_outcome(
                session, outcome, current_user, request, sender=item.sender
            )
        except Exception:
            logger.error("batch_sms_item_failed", exc_info=True)
            result = IngestionResponse(
                event_id=None,
                method="error",
                confidence=0.0,
                was_duplicate=False,
                quarantined=True,
                reason="internal error processing this item",
            )

        results.append(result)
        if result.quarantined:
            quarantined += 1
        elif result.was_duplicate:
            duplicates += 1
        else:
            created += 1

    return BatchIngestionResponse(
        processed=len(items),
        created=created,
        duplicates=duplicates,
        quarantined=quarantined,
        results=results,
    )


@router.post(
    "/manual", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED
)
async def ingest_manual(
    payload: ManualEventRequest,
    request: Request,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> IngestionResponse:
    request_body = payload.model_dump(mode="json")

    cached = await idempotent(
        session,
        key=idempotency_key,
        user_id=current_user.id,
        endpoint="/ingest/manual",
        request_body=request_body,
    )
    if cached is not None:
        return IngestionResponse.model_validate(cached["body"])

    event = normalize_manual(payload.model_dump(), current_user.id)
    row, was_duplicate = await write_event(session, event, event.source_ref)

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="ingestion.manual_created",
        resource_type="financial_event",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
    )
    if not was_duplicate:
        await ConfidenceService().process_event(session, row.id)
        await TwinService().on_event_ingested(session, row)

    response = IngestionResponse(
        event_id=row.id,
        method="manual",
        confidence=event.confidence_score,
        was_duplicate=was_duplicate,
        quarantined=False,
        reason=None,
    )
    await store_idempotent_response(
        session,
        key=idempotency_key,
        user_id=current_user.id,
        endpoint="/ingest/manual",
        request_body=request_body,
        response_body=response.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )
    return response


@router.post("/csv", response_model=BatchIngestionResponse)
async def ingest_csv(
    request: Request,
    file: UploadFile = File(...),
    mapping: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> BatchIngestionResponse:
    try:
        column_mapping = CsvImportRequest.model_validate_json(mapping).column_mapping
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid column mapping: {exc}",
        ) from exc

    raw_bytes = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse CSV file: {exc}",
        ) from exc

    results: list[IngestionResponse] = []
    created = duplicates = quarantined = 0

    for _, row in df.iterrows():
        row_dict = row.to_dict()
        try:
            event = normalize_csv_row(row_dict, column_mapping, current_user.id)
        except (ValueError, KeyError) as exc:
            await quarantine_raw(
                session,
                user_id=current_user.id,
                raw_input=json.dumps(row_dict, default=str),
                sender="csv_import",
                reason=str(exc),
                attempted_methods=["csv"],
            )
            results.append(
                IngestionResponse(
                    event_id=None,
                    method="csv",
                    confidence=0.0,
                    was_duplicate=False,
                    quarantined=True,
                    reason=str(exc),
                )
            )
            quarantined += 1
            continue

        row_db, was_duplicate = await write_event(session, event, event.source_ref)
        results.append(
            IngestionResponse(
                event_id=row_db.id,
                method="csv",
                confidence=event.confidence_score,
                was_duplicate=was_duplicate,
                quarantined=False,
                reason=None,
            )
        )
        if was_duplicate:
            duplicates += 1
        else:
            created += 1
            await ConfidenceService().process_event(session, row_db.id)
            await TwinService().on_event_ingested(session, row_db)

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="ingestion.csv_imported",
        resource_type="financial_event",
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"created": created, "duplicates": duplicates, "quarantined": quarantined},
    )

    return BatchIngestionResponse(
        processed=len(df),
        created=created,
        duplicates=duplicates,
        quarantined=quarantined,
        results=results,
    )


@router.get("/quarantine", response_model=list[QuarantinedInputResponse])
async def list_quarantine(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[QuarantinedInput]:
    result = await session.execute(
        select(QuarantinedInput)
        .where(
            QuarantinedInput.user_id == current_user.id,
            QuarantinedInput.resolved.is_(False),
        )
        .order_by(QuarantinedInput.created_at.desc())
    )
    return list(result.scalars())


@router.post("/quarantine/{quarantine_id}/resolve", response_model=IngestionResponse)
async def resolve_quarantine(
    quarantine_id: UUID,
    payload: ManualEventRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> IngestionResponse:
    result = await session.execute(
        select(QuarantinedInput).where(
            QuarantinedInput.id == quarantine_id,
            QuarantinedInput.user_id == current_user.id,
        )
    )
    quarantined_row = result.scalar_one_or_none()
    if quarantined_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quarantined input not found"
        )
    if quarantined_row.resolved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Already resolved"
        )

    event = normalize_manual(payload.model_dump(), current_user.id)
    row, was_duplicate = await write_event(session, event, event.source_ref)
    quarantined_row.resolved = True
    if not was_duplicate:
        await ConfidenceService().process_event(session, row.id)
        await TwinService().on_event_ingested(session, row)

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="ingestion.quarantine_resolved",
        resource_type="financial_event",
        resource_id=str(row.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
        payload={"quarantine_id": str(quarantine_id)},
    )

    return IngestionResponse(
        event_id=row.id,
        method="manual",
        confidence=event.confidence_score,
        was_duplicate=was_duplicate,
        quarantined=False,
        reason=None,
    )


@router.get("/events", response_model=list[FinancialEventResponse])
async def list_events(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    event_type: FinancialEventType | None = Query(None),
    data_source: DataSource | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[FinancialEvent]:
    stmt = select(FinancialEvent).where(FinancialEvent.user_id == current_user.id)

    if event_type is not None:
        stmt = stmt.where(FinancialEvent.event_type == event_type.value)
    if data_source is not None:
        stmt = stmt.where(FinancialEvent.data_source == data_source.value)
    if start_date is not None:
        stmt = stmt.where(
            FinancialEvent.occurred_at >= datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        )
    if end_date is not None:
        stmt = stmt.where(
            FinancialEvent.occurred_at <= datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        )

    stmt = stmt.order_by(FinancialEvent.occurred_at.desc()).limit(limit).offset(offset)

    result = await session.execute(stmt)
    return list(result.scalars())
