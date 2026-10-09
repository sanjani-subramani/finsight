from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.routers.admin import router as admin_router
from app.api.routers.arbitration import router as arbitration_router
from app.api.routers.auth import router as auth_router
from app.api.routers.confidence import router as confidence_router
from app.api.routers.decision import router as decision_router
from app.api.routers.explain import router as explain_router
from app.api.routers.fingraph import router as fingraph_router
from app.api.routers.ingestion import router as ingestion_router
from app.api.routers.paytrace import router as paytrace_router
from app.api.routers.reconx import router as reconx_router
from app.api.routers.regimpact import router as regimpact_router
from app.api.routers.reports import router as reports_router
from app.api.routers.risk import router as risk_router
from app.api.routers.simulation import router as simulation_router
from app.api.routers.threat import router as threat_router
from app.api.routers.twin import router as twin_router
from app.platform.config import get_settings
from app.platform.database import engine
from app.platform.logging import get_logger
from app.platform.middleware import RequestLoggingMiddleware, TraceIDMiddleware

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(title="FinSentinel API", version="0.1.0")

# Middleware executes outer-to-inner in the order added below (CORS wraps
# everything, TraceID runs next so a trace_id exists before anything logs,
# RequestLogging is innermost, closest to the router).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TraceIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(confidence_router)
app.include_router(twin_router)
app.include_router(simulation_router)
app.include_router(risk_router)
app.include_router(decision_router)
app.include_router(admin_router)
app.include_router(threat_router)
app.include_router(arbitration_router)
app.include_router(explain_router)
app.include_router(paytrace_router)
app.include_router(reconx_router)
app.include_router(fingraph_router)
app.include_router(regimpact_router)
app.include_router(reports_router)


def _error_body(code: str, message: str, request: Request) -> dict:
    trace_id = getattr(request.state, "trace_id", None)
    return {"error": {"code": code, "message": message, "trace_id": trace_id}}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(str(exc.status_code), str(exc.detail), request),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body(
            "validation_error", "Request validation failed", request
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", None)
    logger.error("unhandled_exception", trace_id=trace_id, exc_info=True)
    # Stack traces and raw exception messages can leak file paths, library
    # versions, or query fragments — fine for local debugging, never for a
    # client outside development.
    message = str(exc) if settings.ENVIRONMENT == "development" else "Internal server error"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body("internal_error", message, request),
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "finsentinel", "version": "0.1.0"}


@app.get("/health/db")
async def health_db() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        return {"status": "error", "database": "unreachable", "detail": str(exc)}
