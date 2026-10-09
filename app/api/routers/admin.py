"""Admin operational endpoints for the event bus / pipeline (Step 9)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.admin import (
    AuditEntry,
    AuditPage,
    DlqMessageResponse,
    DlqReplayResponse,
    QueueDepthResponse,
    WorkerHealthResponse,
)
from app.models.tables import AuditLog, User
from app.platform.database import get_session
from app.platform.deps import require_admin
from app.platform.eventbus import EventBus, Topic, get_redis_client, stream_key

router = APIRouter(prefix="/admin", tags=["admin"])

CONSUMER_GROUP = "pipeline"
# Matches arq's own default (arq.worker.default_queue_name +
# health_check_key_suffix) — WorkerSettings in app.platform.worker doesn't
# override queue_name, so this is the key the worker actually writes to.
WORKER_HEALTH_CHECK_KEY = "arq:queue:health-check"
_PIPELINE_TOPICS = [topic for topic in Topic if topic != Topic.DEAD_LETTER]


@router.get("/queues", response_model=list[QueueDepthResponse])
async def get_queue_depths(current_user: User = Depends(require_admin)) -> list[QueueDepthResponse]:
    redis_client = get_redis_client()
    results: list[QueueDepthResponse] = []
    for topic in _PIPELINE_TOPICS:
        key = stream_key(topic)
        length = await redis_client.xlen(key)
        try:
            summary = await redis_client.xpending(key, CONSUMER_GROUP)
            pending = summary.get("pending", 0) if isinstance(summary, dict) else 0
        except Exception:
            # No consumer group yet (nothing has ever subscribed to this
            # topic) — zero pending is the correct answer, not an error.
            pending = 0
        results.append(QueueDepthResponse(topic=topic.value, length=length, pending=pending))
    return results


@router.get("/dlq", response_model=list[DlqMessageResponse])
async def list_dead_letters(
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(require_admin),
) -> list[DlqMessageResponse]:
    redis_client = get_redis_client()
    entries = await redis_client.xrange(stream_key(Topic.DEAD_LETTER), count=limit)
    results: list[DlqMessageResponse] = []
    for message_id, fields in entries:
        payload = json.loads(fields.get("payload", "{}"))
        results.append(
            DlqMessageResponse(
                message_id=str(message_id),
                trace_id=fields.get("trace_id", ""),
                original_topic=payload.get("original_topic", ""),
                original_message_id=payload.get("original_message_id", ""),
                reason=payload.get("reason", ""),
                payload=payload.get("payload", {}),
            )
        )
    return results


@router.post("/dlq/{message_id}/replay", response_model=DlqReplayResponse)
async def replay_dead_letter(
    message_id: str,
    current_user: User = Depends(require_admin),
) -> DlqReplayResponse:
    redis_client = get_redis_client()
    entries = await redis_client.xrange(stream_key(Topic.DEAD_LETTER), min=message_id, max=message_id, count=1)
    if not entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dead letter message not found")

    _id, fields = entries[0]
    dlq_payload = json.loads(fields.get("payload", "{}"))
    original_topic = Topic(dlq_payload["original_topic"])
    trace_id = fields.get("trace_id", "")

    new_id = await EventBus(redis_client).publish(original_topic, dlq_payload["payload"], trace_id)
    return DlqReplayResponse(new_message_id=new_id, original_topic=original_topic.value)


@router.get("/workers", response_model=WorkerHealthResponse)
async def get_worker_health(current_user: User = Depends(require_admin)) -> WorkerHealthResponse:
    redis_client = get_redis_client()
    # arq writes this key with a TTL slightly longer than its health check
    # interval (see Worker.record_health) — its presence IS the liveness
    # signal; it expires on its own if the worker process dies.
    info = await redis_client.get(WORKER_HEALTH_CHECK_KEY)
    return WorkerHealthResponse(healthy=info is not None, info=info)


@router.get("/worker-health")
async def get_worker_health_status(current_user: User = Depends(require_admin)) -> dict[str, Any]:
    redis_client = get_redis_client()
    raw = await redis_client.get(WORKER_HEALTH_CHECK_KEY)
    status_str = "healthy" if raw else "unhealthy"
    info_str = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    last_heartbeat = None
    seconds_since_heartbeat = None

    if info_str:
        try:
            parsed = json.loads(info_str)
            last_heartbeat = parsed.get("last_heartbeat") or parsed.get("timestamp")
        except Exception:
            pass

    return {
        "status": status_str,
        "healthy": raw is not None,
        "last_heartbeat": last_heartbeat,
        "seconds_since_heartbeat": seconds_since_heartbeat,
        "info": info_str,
    }


@router.get("/audit-log", response_model=AuditPage)
async def list_audit_logs(
    action: str | None = Query(None),
    actor_user_id: uuid.UUID | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> AuditPage:
    query = select(AuditLog, User.email).outerjoin(User, AuditLog.actor_user_id == User.id)
    count_query = select(func.count(AuditLog.id))

    if action:
        query = query.where(AuditLog.action.ilike(f"%{action}%"))
        count_query = count_query.where(AuditLog.action.ilike(f"%{action}%"))
    if actor_user_id:
        query = query.where(AuditLog.actor_user_id == actor_user_id)
        count_query = count_query.where(AuditLog.actor_user_id == actor_user_id)
    if date_from:
        query = query.where(AuditLog.occurred_at >= date_from)
        count_query = count_query.where(AuditLog.occurred_at >= date_from)
    if date_to:
        query = query.where(AuditLog.occurred_at <= date_to)
        count_query = count_query.where(AuditLog.occurred_at <= date_to)

    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(AuditLog.occurred_at.desc()).offset(offset).limit(limit)
    rows = await session.execute(query)

    items: list[AuditEntry] = []
    for audit, email in rows.all():
        detail_str = None
        if audit.payload:
            detail_str = json.dumps(audit.payload)
        items.append(
            AuditEntry(
                id=str(audit.id),
                actor_user_id=str(audit.actor_user_id) if audit.actor_user_id else None,
                actor_email=email,
                action=audit.action,
                resource_type=audit.resource_type,
                resource_id=audit.resource_id,
                ip_address=audit.ip_address,
                trace_id=audit.trace_id,
                created_at=audit.occurred_at.isoformat() if audit.occurred_at else "",
                detail=detail_str,
            )
        )

    return AuditPage(items=items, total=total)

