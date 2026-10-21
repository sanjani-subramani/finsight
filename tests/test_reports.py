"""Tests for the reports router (shadow precision, system health, load test)."""

from __future__ import annotations

from httpx import AsyncClient

STRONG_PASSWORD = "Str0ngPassw0rd"


async def _register_and_login(client: AsyncClient, email: str = "rpt1@example.com") -> dict:
    await client.post(
        "/auth/register",
        json={"email": email, "password": STRONG_PASSWORD, "display_name": "Report User"},
    )
    resp = await client.post("/auth/login", json={"email": email, "password": STRONG_PASSWORD})
    assert resp.status_code == 200
    return resp.json()


async def _make_admin(db_session, email: str) -> None:
    from sqlalchemy import select

    from app.models.tables import User

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.is_admin = True
    await db_session.commit()


async def _admin_headers(client: AsyncClient, db_session, email: str = "rpt1@example.com") -> dict:
    tokens = await _register_and_login(client, email)
    await _make_admin(db_session, email)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# --- Authorization ---


async def test_shadow_precision_requires_admin(client: AsyncClient) -> None:
    tokens = await _register_and_login(client, email="nonrpt@example.com")
    resp = await client.get(
        "/reports/shadow-precision",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 403


async def test_system_health_requires_admin(client: AsyncClient) -> None:
    tokens = await _register_and_login(client, email="nonrpt2@example.com")
    resp = await client.get(
        "/reports/system-health",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 403


async def test_unauthenticated_reports_rejected(client: AsyncClient) -> None:
    for path in ["/reports/shadow-precision", "/reports/system-health"]:
        resp = await client.get(path)
        assert resp.status_code == 401, f"{path} should require authentication"


# --- Happy-path with admin ---


async def test_shadow_precision_json_format(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "rpt_sp@example.com")
    resp = await client.get("/reports/shadow-precision?format=json", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    # Shadow report should have standard fields
    assert isinstance(body, dict)


async def test_shadow_precision_markdown_format(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "rpt_md@example.com")
    resp = await client.get("/reports/shadow-precision?format=markdown", headers=headers)
    assert resp.status_code == 200
    # Markdown format returns PlainTextResponse, not JSON
    assert "Shadow Mode" in resp.text or "shadow" in resp.text.lower()


async def test_system_health_returns_metrics(client: AsyncClient, db_session) -> None:
    headers = await _admin_headers(client, db_session, "rpt_sh@example.com")
    resp = await client.get("/reports/system-health", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
