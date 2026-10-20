import pytest
from httpx import AsyncClient

STRONG_PASSWORD = "Str0ngPassw0rd"
ANOTHER_STRONG_PASSWORD = "An0therStr0ngPass"


def _register_payload(email: str = "user1@example.com", password: str = STRONG_PASSWORD) -> dict:
    return {
        "email": email,
        "password": password,
        "display_name": "Test User",
    }


async def _register_and_login(client: AsyncClient, email: str = "user1@example.com") -> dict:
    await client.post("/auth/register", json=_register_payload(email=email))
    resp = await client.post(
        "/auth/login", json={"email": email, "password": STRONG_PASSWORD}
    )
    assert resp.status_code == 200
    return resp.json()


async def test_register_succeeds(client: AsyncClient) -> None:
    resp = await client.post("/auth/register", json=_register_payload())
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "user1@example.com"
    assert "password_hash" not in body


async def test_register_duplicate_email_conflict(client: AsyncClient) -> None:
    await client.post("/auth/register", json=_register_payload())
    resp = await client.post("/auth/register", json=_register_payload())
    assert resp.status_code == 409


@pytest.mark.parametrize(
    "password",
    [
        "short1A",  # too short
        "alllettersnodigits",  # no digit
        "1234567890123",  # no letter
        "password123",  # common password
    ],
)
async def test_weak_password_rejected(client: AsyncClient, password: str) -> None:
    resp = await client.post(
        "/auth/register", json=_register_payload(password=password)
    )
    assert resp.status_code == 422


async def test_login_returns_both_tokens(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"


async def test_login_wrong_password_unauthorized(client: AsyncClient) -> None:
    await client.post("/auth/register", json=_register_payload())
    resp = await client.post(
        "/auth/login", json={"email": "user1@example.com", "password": "WrongPassw0rd"}
    )
    assert resp.status_code == 401


async def test_account_locks_after_max_failed_logins(client: AsyncClient) -> None:
    await client.post("/auth/register", json=_register_payload())

    for _ in range(5):
        resp = await client.post(
            "/auth/login",
            json={"email": "user1@example.com", "password": "WrongPassw0rd"},
        )
        assert resp.status_code == 401

    # Even the *correct* password is now rejected while the lock is active.
    resp = await client.post(
        "/auth/login",
        json={"email": "user1@example.com", "password": STRONG_PASSWORD},
    )
    assert resp.status_code == 423


async def test_me_without_token_unauthorized(client: AsyncClient) -> None:
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_with_valid_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    resp = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "user1@example.com"
    assert "password_hash" not in body


async def test_refresh_rotates_and_invalidates_old_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    old_refresh = tokens["refresh_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert new_tokens["refresh_token"] != old_refresh

    # The old refresh token must no longer work.
    resp = await client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 401


async def test_refresh_reuse_revokes_entire_chain(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    refresh_1 = tokens["refresh_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_1})
    assert resp.status_code == 200
    refresh_2 = resp.json()["refresh_token"]

    # Reusing the already-rotated-away token is theft signal: it should
    # revoke the whole chain, including the token that replaced it.
    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_1})
    assert resp.status_code == 401

    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_2})
    assert resp.status_code == 401


async def test_change_password_invalidates_all_refresh_tokens(
    client: AsyncClient,
) -> None:
    tokens = await _register_and_login(client)

    resp = await client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"old_password": STRONG_PASSWORD, "new_password": ANOTHER_STRONG_PASSWORD},
    )
    assert resp.status_code == 204

    resp = await client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert resp.status_code == 401

    # New password works, old one doesn't.
    resp = await client.post(
        "/auth/login",
        json={"email": "user1@example.com", "password": ANOTHER_STRONG_PASSWORD},
    )
    assert resp.status_code == 200

    resp = await client.post(
        "/auth/login", json={"email": "user1@example.com", "password": STRONG_PASSWORD}
    )
    assert resp.status_code == 401


async def test_password_hash_never_in_any_response(client: AsyncClient) -> None:
    register_resp = await client.post("/auth/register", json=_register_payload())
    assert "password_hash" not in register_resp.text

    tokens = await _register_and_login(client, email="user2@example.com")
    me_resp = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert "password_hash" not in me_resp.text


async def test_update_profile_changes_risk_tolerance(client: AsyncClient) -> None:
    tokens = await _register_and_login(client, email="user3@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    me_resp = await client.get("/auth/me", headers=headers)
    assert me_resp.json()["risk_tolerance"] == "balanced"

    patch_resp = await client.patch(
        "/auth/me", json={"risk_tolerance": "aggressive"}, headers=headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["risk_tolerance"] == "aggressive"

    me_resp_after = await client.get("/auth/me", headers=headers)
    assert me_resp_after.json()["risk_tolerance"] == "aggressive"


async def test_update_profile_rejects_invalid_risk_tolerance(client: AsyncClient) -> None:
    tokens = await _register_and_login(client, email="user4@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.patch("/auth/me", json={"risk_tolerance": "reckless"}, headers=headers)
    assert resp.status_code == 422


async def test_my_orgs_lists_every_org_the_user_belongs_to(client: AsyncClient, db_session) -> None:
    from sqlalchemy import select

    from app.models.tables import Organization, OrgMembership, User

    tokens = await _register_and_login(client, email="user5@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    result = await db_session.execute(select(User).where(User.email == "user5@example.com"))
    user = result.scalar_one()

    org_a = Organization(name="Acme Payments", slug="acme-payments")
    org_b = Organization(name="Beta Bank", slug="beta-bank")
    db_session.add_all([org_a, org_b])
    await db_session.flush()
    db_session.add_all(
        [
            OrgMembership(user_id=user.id, org_id=org_a.id, role="owner"),
            OrgMembership(user_id=user.id, org_id=org_b.id, role="viewer"),
        ]
    )
    await db_session.commit()

    resp = await client.get("/auth/my-orgs", headers=headers)
    assert resp.status_code == 200
    by_slug = {row["org_slug"]: row["role"] for row in resp.json()}

    # Registration also creates the user's own org, so expect it alongside the
    # two memberships added above.
    assert by_slug[f"org-{user.id.hex}"] == "owner"
    assert by_slug["acme-payments"] == "owner"
    assert by_slug["beta-bank"] == "viewer"
    assert len(by_slug) == 3


async def test_my_orgs_returns_only_the_users_own_org_after_registration(
    client: AsyncClient,
) -> None:
    tokens = await _register_and_login(client, email="user6@example.com")
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get("/auth/my-orgs", headers=headers)
    assert resp.status_code == 200

    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["role"] == "owner"


async def test_registration_never_joins_another_users_existing_org(
    client: AsyncClient,
) -> None:
    """Regression test for a cross-tenant privilege escalation.

    Registration used to attach every new user as `owner` of whichever
    organization was first in the table (an unscoped
    `select(Organization).limit(1)`). The second user to ever sign up gained
    owner access to the first user's org -- and therefore to another tenant's
    payment, reconciliation, dependency-graph and compliance data.

    Each registrant must get their own, separate organization.
    """
    alice = await _register_and_login(client, email="alice@acme-example.com")
    bob = await _register_and_login(client, email="bob@rival-example.com")

    alice_orgs = (
        await client.get(
            "/auth/my-orgs",
            headers={"Authorization": f"Bearer {alice['access_token']}"},
        )
    ).json()
    bob_orgs = (
        await client.get(
            "/auth/my-orgs",
            headers={"Authorization": f"Bearer {bob['access_token']}"},
        )
    ).json()

    alice_org_ids = {row["org_id"] for row in alice_orgs}
    bob_org_ids = {row["org_id"] for row in bob_orgs}

    assert alice_org_ids, "alice should own an org"
    assert bob_org_ids, "bob should own an org"
    assert not (alice_org_ids & bob_org_ids), (
        "cross-tenant breach: bob was granted access to alice's organization"
    )
