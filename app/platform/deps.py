from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import OrgMembership, User
from app.platform.database import get_session
from app.platform.security import decode_token

_bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None:
        raise _UNAUTHORIZED

    try:
        claims = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise _UNAUTHORIZED from exc

    if claims.get("typ") != "access":
        raise _UNAUTHORIZED

    try:
        user_id = UUID(claims["sub"])
    except (KeyError, ValueError, TypeError) as exc:
        raise _UNAUTHORIZED from exc

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active or user.deleted_at is not None:
        raise _UNAUTHORIZED

    return user


def require_roles(
    *roles: str,
) -> Callable[..., Coroutine[Any, Any, User]]:
    """Dependency factory for org-scoped endpoints. Usage:

        @router.get("/orgs/{org_id}/...")
        async def handler(user: User = Depends(require_roles("owner", "ops_engineer"))):
            ...

    The route must declare an `org_id` path parameter — FastAPI injects it
    into this dependency automatically.
    """

    async def _dependency(
        org_id: UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> User:
        result = await session.execute(
            select(OrgMembership).where(
                OrgMembership.user_id == current_user.id,
                OrgMembership.org_id == org_id,
            )
        )
        membership = result.scalar_one_or_none()

        if membership is None or membership.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required role for this organization",
            )

        return current_user

    return _dependency


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Gate for global (non org-scoped) admin endpoints — e.g.
    app.modules.risk's proposed-rules review. require_roles() can't cover
    this: it requires an org_id path parameter and checks org membership,
    but reviewing an LLM-proposed rule isn't scoped to any one org.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # X-Forwarded-For may be a chain "client, proxy1, proxy2"; the
        # first entry is the client as seen by the nearest proxy. This is
        # only as trustworthy as that proxy — it must be configured to
        # strip/overwrite any client-supplied XFF header, or a client could
        # spoof its own IP here.
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"
