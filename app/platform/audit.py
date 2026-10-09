from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import AuditLog
from app.platform.logging import get_logger

logger = get_logger(__name__)


async def write_audit(
    session: AsyncSession,
    *,
    actor_user_id: UUID | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    trace_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    # Audit logging is best-effort and must never break the caller's actual
    # request (e.g. a user registering or logging in). We isolate the write
    # in its own savepoint so a failure here (constraint violation, DB
    # hiccup) rolls back only the audit row, not whatever the caller was
    # already doing in this transaction — and we swallow the exception
    # after logging it loudly, rather than let it propagate.
    try:
        async with session.begin_nested():
            session.add(
                AuditLog(
                    actor_user_id=actor_user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    ip_address=ip_address,
                    trace_id=trace_id,
                    payload=payload,
                )
            )
    except Exception:
        logger.error(
            "audit_write_failed",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            exc_info=True,
        )
