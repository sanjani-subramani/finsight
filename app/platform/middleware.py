from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.platform.logging import bind_trace_id, clear_log_context, get_logger

logger = get_logger(__name__)

Handler = Callable[[Request], Awaitable[Response]]


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Generates a trace_id per request, binds it to the structlog context
    (so every log line during this request carries it automatically), and
    echoes it back on the response so clients can correlate support
    requests with server-side logs."""

    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        bind_trace_id(trace_id)
        try:
            response = await call_next(request)
        finally:
            clear_log_context()
        response.headers["X-Trace-ID"] = trace_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs method, path, status, and duration for every request.

    We deliberately never log request or response bodies: they can contain
    passwords, tokens, or raw financial data, and log storage is not an
    acceptable place for either.
    """

    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response
