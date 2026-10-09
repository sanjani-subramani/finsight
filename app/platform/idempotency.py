from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import IdempotencyKey
from app.platform.timeutils import as_aware_utc

IDEMPOTENCY_KEY_TTL_HOURS = 24

# How long a caller will wait for a CONCURRENT identical request to finish
# before giving up. 50 requests racing on the same key is exactly the
# scenario this exists for (see tests/integration/test_idempotency_under_concurrency.py)
# — the loser of the claim race must wait for the winner's real work
# (which can include an LLM call, a simulation run, ...) rather than a
# couple of retries at DB speed.
MAX_WAIT_ATTEMPTS = 100
WAIT_INTERVAL_SECONDS = 0.1


class StoredResponse(TypedDict):
    status_code: int | None
    body: Any


def _canonical_hash(body: Any) -> str:
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def _load(session: AsyncSession, key: str) -> IdempotencyKey | None:
    result = await session.execute(select(IdempotencyKey).where(IdempotencyKey.key == key))
    row = result.scalar_one_or_none()
    if row is not None and as_aware_utc(row.expires_at) < datetime.now(timezone.utc):
        return None
    return row


async def idempotent(
    session: AsyncSession,
    *,
    key: str,
    user_id: UUID | None,
    endpoint: str,
    request_body: Any,
) -> StoredResponse | None:
    """Atomically claims `key` for the caller to process, or returns the
    already-completed response from whoever claimed it first (waiting
    briefly if that request is still in flight).

    Returns None if THIS call won the claim and must now do the real
    work and call store_idempotent_response(). Returns the stored
    response if some other request (concurrent or prior) already fully
    handled this exact (key, body) pair. Raises 409 if the key was
    reused with a *different* body — same key, different payload is a
    client bug and must be loud, not silently accepted.

    Concurrency note: an earlier version of this function only checked
    "does a row exist" before letting the caller proceed to do the work
    and insert its result afterward — under N truly concurrent requests
    with the same key, every one of them could see "no row yet" before
    any of them committed, so all N would proceed to do the work
    independently (see the migration/commit history for the Step 19
    integration test that caught this against real Postgres; SQLite's
    default transaction behavior in the unit suite never exercised the
    real race). The fix: the claim itself is a single INSERT, committed
    immediately as its own short transaction, relying on `key` being the
    table's primary key — Postgres guarantees exactly one such INSERT
    can succeed for a given key, and every other concurrent caller gets
    a real IntegrityError to react to instead of silently racing ahead.
    """
    request_hash = _canonical_hash(request_body)

    existing = await _load(session, key)
    if existing is not None:
        return await _resolve_existing(session, existing, key, request_hash)

    claim = IdempotencyKey(
        key=key,
        user_id=user_id,
        endpoint=endpoint,
        request_hash=request_hash,
        response_body=None,
        status_code=None,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=IDEMPOTENCY_KEY_TTL_HOURS),
    )
    session.add(claim)
    try:
        await session.commit()
        return None  # this call WON the claim -- caller does the real work
    except IntegrityError:
        await session.rollback()
        # Lost the race: someone else's claim committed first. Their row
        # may still have response_body=None if they're mid-work -- wait
        # for it to resolve rather than treating "row exists but empty"
        # as a fresh 404.
        return await _wait_for_resolution(session, key, request_hash)


async def _resolve_existing(
    session: AsyncSession, existing: IdempotencyKey, key: str, request_hash: str
) -> StoredResponse | None:
    if existing.request_hash != request_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency key was already used with a different request body",
        )
    if existing.response_body is not None:
        return StoredResponse(status_code=existing.status_code, body=existing.response_body)
    # Claimed by another request that hasn't finished yet.
    return await _wait_for_resolution(session, key, request_hash)


async def _wait_for_resolution(session: AsyncSession, key: str, request_hash: str) -> StoredResponse:
    for _ in range(MAX_WAIT_ATTEMPTS):
        await asyncio.sleep(WAIT_INTERVAL_SECONDS)
        # A fresh SELECT, not a cached ORM identity-map hit -- this must
        # observe the OTHER request's committed write.
        session.expire_all()
        row = await _load(session, key)
        if row is not None and row.response_body is not None:
            if row.request_hash != request_hash:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key was already used with a different request body",
                )
            return StoredResponse(status_code=row.status_code, body=row.response_body)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Timed out waiting for an identical in-flight request to complete",
    )


async def store_idempotent_response(
    session: AsyncSession,
    *,
    key: str,
    user_id: UUID | None,
    endpoint: str,
    request_body: Any,
    response_body: Any,
    status_code: int,
) -> None:
    request_hash = _canonical_hash(request_body)
    # merge() here is an UPDATE in practice: idempotent() always inserts
    # the claim row first, so this key already exists with
    # response_body=None -- merge() fills it in rather than inserting a
    # second row.
    await session.merge(
        IdempotencyKey(
            key=key,
            user_id=user_id,
            endpoint=endpoint,
            request_hash=request_hash,
            response_body=response_body,
            status_code=status_code,
            expires_at=datetime.now(timezone.utc)
            + timedelta(hours=IDEMPOTENCY_KEY_TTL_HOURS),
        )
    )
    await session.flush()
