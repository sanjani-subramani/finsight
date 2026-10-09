"""API request/response DTOs for the LLM Narrator (Step 12)."""

from __future__ import annotations

from pydantic import BaseModel


class NarrationResponse(BaseModel):
    text: str
    source: str
    validation_passed: bool
    violations: list[str]
    cached: bool
    duration_ms: int


class TraceStepNarrationResponse(BaseModel):
    order: int
    stage: str
    narration: NarrationResponse


class ExplainHealthResponse(BaseModel):
    llm_configured: bool
    llm_reachable: bool | None
