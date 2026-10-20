from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    OrgMembershipResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
)
from app.models.tables import OrgMembership, Organization, RefreshToken, User
from app.platform.audit import write_audit
from app.platform.config import get_settings
from app.platform.database import get_session
from app.platform.deps import get_client_ip, get_current_user
from app.platform.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    needs_rehash,
    verify_password,
)
from app.platform.timeutils import as_aware_utc

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

# Precomputed once at import time so the "user not found" branch of login()
# can run a real argon2 verification against *something*. Without this, a
# lookup miss would return almost instantly while a wrong-password attempt
# pays argon2's full (deliberately slow) cost — letting an attacker
# enumerate valid emails purely from response latency.
_DUMMY_PASSWORD_HASH = hash_password("not-a-real-password-x1")


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


async def _load_roles(session: AsyncSession, user_id: UUID) -> list[str]:
    result = await session.execute(
        select(OrgMembership.role).where(OrgMembership.user_id == user_id).distinct()
    )
    return [row[0] for row in result.all()]


async def _revoke_all_refresh_tokens(session: AsyncSession, user_id: UUID) -> None:
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
        )
    )
    for row in result.scalars():
        row.revoked_at = now


def _issue_refresh_token(
    user_id: UUID, user_agent: str | None
) -> tuple[str, RefreshToken]:
    raw, token_hash = create_refresh_token()
    row = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_days),
        user_agent=user_agent,
    )
    return raw, row


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    payload: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User:
    existing = await session.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    user = User(
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        risk_tolerance=payload.risk_tolerance,
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError as exc:
        # Closes the race between the check above and this insert: two
        # concurrent registrations for the same email would both pass the
        # SELECT and collide here instead.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from exc

    await write_audit(
        session,
        actor_user_id=user.id,
        action="user.registered",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
    )

    # Give the registering user their OWN organization, with owner role, so they
    # can immediately use the dashboard.
    #
    # SECURITY: this org MUST be created fresh for this user. A previous version
    # looked up `select(Organization).limit(1)` -- an unscoped query that returns
    # whichever org happens to be first in the table -- and granted the new user
    # `owner` on it. That is a cross-tenant privilege escalation: every account
    # created after the first one silently gained owner access to another
    # tenant's payment, reconciliation, dependency-graph and compliance data.
    # RBAC could not catch it, because RBAC checks what a role permits and
    # assumes the role itself was assigned to the right tenant.
    #
    # The slug uses the full user UUID, not a truncated prefix: `slug` is
    # UNIQUE, and an 8-hex-char prefix is only 32 bits, which collides with
    # ~50% probability around 77k users and would fail the registration.
    own_org = Organization(
        name=f"{user.display_name or 'Default'} Org",
        slug=f"org-{user.id.hex}",
    )
    session.add(own_org)
    await session.flush()

    membership = OrgMembership(
        user_id=user.id,
        org_id=own_org.id,
        role="owner",
    )
    session.add(membership)
    await session.flush()

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user is None:
        # See _DUMMY_PASSWORD_HASH comment: burn the same argon2 cost a
        # real wrong-password attempt would pay, so this branch and the
        # "wrong password" branch below are indistinguishable by timing.
        verify_password(payload.password, _DUMMY_PASSWORD_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if user.locked_until is not None and as_aware_utc(
        user.locked_until
    ) > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to repeated failed logins",
        )

    if not verify_password(payload.password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.max_failed_logins:
            user.locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=settings.lockout_minutes
            )
        await session.flush()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if needs_rehash(user.password_hash):
        # argon2 parameters (memory/time cost) can be tightened over time;
        # rehash transparently on a successful login rather than forcing a
        # separate migration step.
        user.password_hash = hash_password(payload.password)

    user.failed_login_count = 0
    user.locked_until = None

    roles = await _load_roles(session, user.id)
    access_token = create_access_token(user.id, roles)
    raw_refresh, refresh_row = _issue_refresh_token(
        user.id, request.headers.get("user-agent")
    )
    session.add(refresh_row)
    await session.flush()

    await write_audit(
        session,
        actor_user_id=user.id,
        action="user.login",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        token_type="bearer",
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    incoming_hash = hash_token(payload.refresh_token)
    token_result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == incoming_hash)
    )
    token_row = token_result.scalar_one_or_none()

    if token_row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if token_row.revoked_at is not None:
        # Reuse detection. Refresh tokens are single-use: each /refresh
        # call revokes the presented token and issues a new one. If a
        # token that is *already revoked* is presented again, either the
        # legitimate client replayed a stale request, or an attacker
        # stole a token earlier in the chain and is now racing the real
        # user. We can't tell those apart, so we treat it as theft: kill
        # every refresh token this user holds (forcing re-login
        # everywhere) and audit it loudly for investigation.
        await _revoke_all_refresh_tokens(session, token_row.user_id)
        await write_audit(
            session,
            actor_user_id=token_row.user_id,
            action="token.reuse_detected",
            resource_type="refresh_token",
            resource_id=str(token_row.id),
            ip_address=get_client_ip(request),
            trace_id=_trace_id(request),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if as_aware_utc(token_row.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    user_result = await session.execute(
        select(User).where(User.id == token_row.user_id)
    )
    user = user_result.scalar_one_or_none()
    if user is None or not user.is_active or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    raw_refresh, new_row = _issue_refresh_token(
        user.id, request.headers.get("user-agent")
    )
    session.add(new_row)
    await session.flush()

    token_row.revoked_at = datetime.now(timezone.utc)
    token_row.replaced_by = new_row.id

    roles = await _load_roles(session, user.id)
    access_token = create_access_token(user.id, roles)

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        token_type="bearer",
        expires_in=settings.access_token_minutes * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def logout(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> None:
    # Logout is idempotent from the client's perspective: an unknown or
    # already-revoked token still returns 204, so callers never need to
    # special-case "already logged out."
    incoming_hash = hash_token(payload.refresh_token)
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == incoming_hash)
    )
    token_row = result.scalar_one_or_none()

    if token_row is not None and token_row.revoked_at is None:
        token_row.revoked_at = datetime.now(timezone.utc)
        await write_audit(
            session,
            actor_user_id=token_row.user_id,
            action="user.logout",
            resource_type="user",
            resource_id=str(token_row.user_id),
            ip_address=get_client_ip(request),
            trace_id=_trace_id(request),
        )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/my-orgs", response_model=list[OrgMembershipResponse])
async def my_orgs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[OrgMembershipResponse]:
    # Nothing under app.api.routers.* org-scoped endpoints exposes this --
    # each of them requires an org_id to already be known (via
    # require_roles) rather than helping a client discover one. A
    # frontend org switcher has no other way to learn which orgs the
    # signed-in user belongs to, or what role gates which action in each.
    result = await session.execute(
        select(OrgMembership, Organization)
        .join(Organization, Organization.id == OrgMembership.org_id)
        .where(OrgMembership.user_id == current_user.id)
    )
    return [
        OrgMembershipResponse(org_id=org.id, org_name=org.name, org_slug=org.slug, role=membership.role)
        for membership, org in result.all()
    ]


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UpdateProfileRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    # Registration is the ONLY place risk_tolerance could previously be
    # set — there was no way to change it afterward, even though the
    # Gate's tolerance-adjustment stage (app.modules.decision.gate) and
    # arbitration's reduction ordering (app.modules.decision.policy) both
    # read it on every decision. A user who registered before they'd
    # thought about their real risk appetite had no way to correct it.
    changed_fields: dict[str, str] = {}
    if payload.risk_tolerance is not None and payload.risk_tolerance != current_user.risk_tolerance:
        changed_fields["risk_tolerance"] = payload.risk_tolerance
        current_user.risk_tolerance = payload.risk_tolerance
    if payload.display_name is not None and payload.display_name != current_user.display_name:
        changed_fields["display_name"] = payload.display_name
        current_user.display_name = payload.display_name

    if changed_fields:
        await write_audit(
            session,
            actor_user_id=current_user.id,
            action="user.profile_updated",
            resource_type="user",
            resource_id=str(current_user.id),
            ip_address=get_client_ip(request),
            trace_id=_trace_id(request),
            payload=changed_fields,
        )

    return current_user


@router.post(
    "/change-password", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    current_user.password_hash = hash_password(payload.new_password)
    await _revoke_all_refresh_tokens(session, current_user.id)

    await write_audit(
        session,
        actor_user_id=current_user.id,
        action="user.password_changed",
        resource_type="user",
        resource_id=str(current_user.id),
        ip_address=get_client_ip(request),
        trace_id=_trace_id(request),
    )
