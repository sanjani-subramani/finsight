import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.idempotency import idempotent, store_idempotent_response


async def test_same_key_same_body_replays_response_without_rerunning_handler(
    db_session: AsyncSession,
) -> None:
    calls = {"count": 0}
    key = "idem-key-1"
    body = {"amount": 100, "currency": "INR"}
    response_body = None

    for _ in range(2):
        cached = await idempotent(
            db_session, key=key, user_id=None, endpoint="/test", request_body=body
        )
        if cached is None:
            calls["count"] += 1
            response_body = {"result": "ok", "amount": body["amount"]}
            await store_idempotent_response(
                db_session,
                key=key,
                user_id=None,
                endpoint="/test",
                request_body=body,
                response_body=response_body,
                status_code=200,
            )
        else:
            response_body = cached["body"]

    assert calls["count"] == 1
    assert response_body == {"result": "ok", "amount": 100}


async def test_same_key_different_body_raises_conflict(
    db_session: AsyncSession,
) -> None:
    key = "idem-key-2"

    assert (
        await idempotent(
            db_session, key=key, user_id=None, endpoint="/test", request_body={"a": 1}
        )
        is None
    )
    await store_idempotent_response(
        db_session,
        key=key,
        user_id=None,
        endpoint="/test",
        request_body={"a": 1},
        response_body={"ok": True},
        status_code=200,
    )

    with pytest.raises(HTTPException) as exc_info:
        await idempotent(
            db_session, key=key, user_id=None, endpoint="/test", request_body={"a": 2}
        )

    assert exc_info.value.status_code == 409
