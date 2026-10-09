"""API request/response DTOs for admin operational endpoints (Step 9)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class QueueDepthResponse(BaseModel):
    topic: str
    length: int
    pending: int


class DlqMessageResponse(BaseModel):
    message_id: str
    trace_id: str
    original_topic: str
    original_message_id: str
    reason: str
    payload: dict[str, Any]


class DlqReplayResponse(BaseModel):
    new_message_id: str
    original_topic: str


class WorkerHealthResponse(BaseModel):
    healthy: bool
    info: str | None


class AuditEntry(BaseModel):
    id: str
    actor_user_id: str | None = None
    actor_email: str | None = None
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    trace_id: str | None = None
    created_at: str
    detail: str | None = None


class AuditPage(BaseModel):
    items: list[AuditEntry]
    total: int
