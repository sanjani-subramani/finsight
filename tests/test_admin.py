"""Tests for the admin router (queues, DLQ, workers, audit log)."""

from __future__ import annotations

from httpx import AsyncClient

STRONG_PASSWORD = "Str0ngPassw0rd"


async def _register_and_login(client: AsyncClient, email: str = "admin1@example.com") -> dict:
    await client.post(
        "/auth/register",
        json={"email": email, "password": STRONG_PASSWORD, "display_name": "Admin User"},
    )
    resp = await client.post("/auth/login", json={"email": email, "password": STRONG_PASSWORD})
    assert resp.status_code == 200
    return resp.json()


async def _make_admin(db_session, email: str) -> None:
    """Promote a user to admin by flipping is_admin in the DB."""
    from sqlalchemy import select

    from app.models.tables import User

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.is_admin = True
    await db_session.commit()


async def _admin_headers(client: AsyncClient, db_session, email: str = "admin1@example.com") -> dict:
    tokens = await _register_and_login(client, email)
    await _make_admin(db_session, email)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# --- Authorization ---


async def test_queues_requires_admin(client: AsyncClient) -> None:
    tokens = await _register_and_login(client, email="nonadmin@example.com")
    resp = await client.get(
        "/admin/queues", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 403


async def test_dlq_requires_admin(client: AsyncClient) -> None:
    tokens = await _register_and_login(client, email="nonadmin2@example.com")
    resp = await client.get(
        "/admin/dlq", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 403


async def test_workers_requires_admin(client: AsyncClient) -> None:
    tokens = await _register_and_login(client, email="nonadmin3@example.com")
    resp = await client.get(
        "/admin/workers", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 403


async def test_audit_log_requires_admin(client: AsyncClient) -> None:
    tokens = await _register_and_login(client, email="nonadmin4@example.com")
    resp = await client.get(
        "/admin/audit-log", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 403


async def test_unauthenticated_admin_endpoints_rejected(client: AsyncClient) -> None:
    for path in ["/admin/queues", "/admin/dlq", "/admin/workers", "/admin/audit-log"]:
        resp = await client.get(path)
        assert resp.status_code == 401, f"{path} should require authentication"


# --- Happy-path with admin ---


async def test_queues_returns_list(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "admin_q@example.com")
    resp = await client.get("/admin/queues", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Each entry should have topic, length, pending
    if data:
        assert "topic" in data[0]
        assert "length" in data[0]


async def test_dlq_returns_list(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "admin_dlq@example.com")
    resp = await client.get("/admin/dlq", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_workers_returns_health(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "admin_w@example.com")
    resp = await client.get("/admin/workers", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "healthy" in body


async def test_worker_health_status_returns_dict(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "admin_wh@example.com")
    resp = await client.get("/admin/worker-health", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "status" in body
    assert "healthy" in body


async def test_audit_log_returns_paginated(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "admin_al@example.com")
    resp = await client.get("/admin/audit-log", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert isinstance(body["items"], list)


async def test_audit_log_filters_by_action(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "admin_af@example.com")
    resp = await client.get("/admin/audit-log?action=user.registered", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    for item in body["items"]:
        assert "user.registered" in item["action"].lower()


async def test_dlq_replay_nonexistent_message_returns_404(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "admin_replay@example.com")
    resp = await client.post("/admin/dlq/0-0/replay", headers=headers)
    assert resp.status_code == 404
