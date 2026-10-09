"""Structured JSON logging.

Every log call goes through structlog's contextvars machinery, so a
trace_id bound once per request (see TraceIDMiddleware) is automatically
attached to every log line emitted while handling that request, without
threading it through every function signature.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def _configure() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )


_configure()


def get_logger(name: str | None = None) -> Any:
    return structlog.get_logger(name)


def bind_trace_id(trace_id: str) -> None:
    structlog.contextvars.bind_contextvars(trace_id=trace_id)


def clear_log_context() -> None:
    structlog.contextvars.clear_contextvars()
