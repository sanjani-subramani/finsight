"""Password hashing and JWT/refresh-token primitives.

Nothing here talks to the database — it is pure crypto/encoding logic so it
can be unit tested in isolation and reused by any module that needs it.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.platform.config import get_settings

settings = get_settings()

_hasher = PasswordHasher()

JWT_ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        # Defense in depth: a malformed/foreign hash raises argon2's
        # InvalidHash (or similar) rather than VerifyMismatchError. Either
        # way, "can't verify" must mean "not authenticated" — it must never
        # propagate as an unhandled 500 from a login attempt.
        return False


def needs_rehash(hashed: str) -> bool:
    return _hasher.check_needs_rehash(hashed)


def create_access_token(user_id: UUID, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)
    claims: dict[str, Any] = {
        "sub": str(user_id),
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
        "typ": "access",
        "jti": str(uuid4()),
    }
    return jwt.encode(claims, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token() -> tuple[str, str]:
    """Return (raw_token, sha256_hash). The raw token goes to the client and
    is never stored; only its hash is persisted, so a leaked database dump
    cannot be used to impersonate a user."""
    raw = secrets.token_urlsafe(48)
    return raw, hash_token(raw)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
