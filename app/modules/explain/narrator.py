"""class Narrator — turns a deterministic decision trace into natural
language, WITHOUT introducing any fact not present in the trace.

ARCHITECTURAL RULE: this whole module (app.modules.explain) is OPTIONAL.
Nothing outside app.modules.explain imports from it, and nothing in
app.modules.decision/risk/twin/... depends on it existing. Narrator only
CONSUMES an already-complete, already-validated ContextualIntervention/
TraceStep produced upstream; deleting this entire package must still
leave a fully working product that shows template-based text (see
templates.py, which every code path here falls back to).
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, replace
from typing import Any, Literal
from uuid import UUID

from app.contracts.events import ContextualIntervention, TraceStep
from app.modules.explain.grounding import extract_facts, validate_narration
from app.modules.explain.templates import render_template
from app.platform.cache import RedisLike
from app.platform.config import Settings, get_settings
from app.platform.llm_client import call_groq_json
from app.platform.logging import get_logger

logger = get_logger(__name__)

# Slight variation is fine for readability -- narration is prose, not a
# classification decision -- because facts are checked completely
# separately (validate_narration) regardless of how the wording varies
# between calls.
NARRATOR_TEMPERATURE = 0.3
MAX_TOKENS = 300
# A trace is immutable once its intervention is created, so its
# narration can be cached indefinitely for practical purposes; a week is
# just a sane upper bound rather than "forever" for storage hygiene.
CACHE_TTL_SECONDS = 7 * 24 * 3600

_LENGTH_INSTRUCTIONS = {
    "concise": "Write 2 to 4 sentences.",
    "detailed": "Write up to 6 sentences.",
}

_SYSTEM_PROMPT_TEMPLATE = """You rephrase an ALREADY-COMPLETED, already-computed financial risk analysis into plain language for an Indian retail banking user.

Rules, all mandatory:
- You may ONLY use facts present in the trace given to you below.
- You must NOT introduce any number, date, amount, or claim that is not
  already in the trace. Every figure you mention must come directly from it.
- You must NOT give financial advice beyond the recommendation already
  present in the trace -- no product suggestions, no "you should invest in...".
- You must NOT guarantee outcomes -- this analysis is PROBABILISTIC. Never
  say "you will", "guaranteed", "definitely", or similar.
- Plain language, no jargon. Use Indian rupee formatting (e.g. Rs.15,000).
- {length_instruction}

Respond with valid JSON matching this schema and nothing else -- no
markdown, no commentary, no code fences:
{{"narration": "your rephrased text"}}
"""


@dataclass(frozen=True)
class NarrationResult:
    text: str
    source: Literal["llm", "template_fallback"]
    validation_passed: bool
    violations: list[str] = field(default_factory=list)
    cached: bool = False
    duration_ms: int = 0


def _trace_cache_key(trace: list[TraceStep], intervention_id: UUID, style: str) -> str:
    payload = json.dumps(
        {
            "intervention_id": str(intervention_id),
            "style": style,
            "trace": [step.model_dump(mode="json") for step in trace],
        },
        sort_keys=True,
        default=str,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"narration:{digest}"


class Narrator:
    def __init__(
        self,
        redis_client: RedisLike | None = None,
        settings: Settings | None = None,
        http_client: Any | None = None,
    ) -> None:
        self._redis = redis_client
        self._settings = settings or get_settings()
        self._http_client = http_client

    async def narrate(
        self, trace: list[TraceStep], intervention: ContextualIntervention, style: str = "concise"
    ) -> NarrationResult:
        start = time.monotonic()
        cache_key = _trace_cache_key(trace, intervention.intervention_id, style)

        cached_result = await self._read_cache(cache_key)
        if cached_result is not None:
            return replace(cached_result, duration_ms=_elapsed_ms(start))

        template_text = render_template(trace, intervention)

        # Step 1: no LLM key -> template narration immediately. The shield
        # must work without AI, and this is the cheapest possible path.
        if not self._settings.GROQ_API_KEY:
            result = NarrationResult(
                text=template_text, source="template_fallback", validation_passed=True,
                duration_ms=_elapsed_ms(start),
            )
            await self._write_cache(cache_key, result)
            return result

        llm_text = await self._call_llm(trace, style)

        if llm_text is None:
            result = NarrationResult(
                text=template_text, source="template_fallback", validation_passed=False,
                violations=["llm_call_failed_or_unavailable"], duration_ms=_elapsed_ms(start),
            )
            await self._write_cache(cache_key, result)
            return result

        facts = extract_facts(trace, intervention)
        validation = validate_narration(llm_text, facts)

        if validation.valid:
            result = NarrationResult(
                text=llm_text, source="llm", validation_passed=True, duration_ms=_elapsed_ms(start)
            )
        else:
            # INVALID: discard the LLM output entirely. Do NOT retry, do
            # NOT attempt to repair it -- a silently "fixed" hallucination
            # is worse than a plainer, fully-trustworthy template
            # sentence, because a repair attempt is itself unverified.
            logger.warning("narration_validation_failed", violations=validation.violations)
            result = NarrationResult(
                text=template_text, source="template_fallback", validation_passed=False,
                violations=validation.violations, duration_ms=_elapsed_ms(start),
            )

        await self._write_cache(cache_key, result)
        return result

    async def _call_llm(self, trace: list[TraceStep], style: str) -> str | None:
        length_instruction = _LENGTH_INSTRUCTIONS.get(style, _LENGTH_INSTRUCTIONS["concise"])
        system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(length_instruction=length_instruction)
        trace_json = json.dumps([step.model_dump(mode="json") for step in trace], default=str)
        # The trace is DATA, delimited and clearly labelled as such — same
        # untrusted-input posture as every other LLM call in this codebase
        # (see e.g. app.modules.threat.llm_analyzer), even though a trace
        # is internally generated rather than attacker-controlled: it may
        # still embed free-text evidence strings originally sourced from
        # an SMS body or call transcript.
        user_content = f"<trace>\n{trace_json}\n</trace>"

        try:
            content = await call_groq_json(
                system_prompt,
                user_content,
                self._settings,
                http_client=self._http_client,
                retries=0,
                temperature=NARRATOR_TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
        except Exception:
            logger.warning("narrator_llm_call_raised", exc_info=True)
            return None

        if content is None:
            return None

        try:
            parsed = json.loads(content)
            narration = parsed["narration"]
        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning("narrator_llm_invalid_json")
            return None

        return str(narration) if narration else None

    async def _read_cache(self, key: str) -> NarrationResult | None:
        if self._redis is None:
            return None
        try:
            raw = await self._redis.get(key)
        except Exception:
            logger.warning("narration_cache_read_failed", exc_info=True)
            return None
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            return NarrationResult(
                text=data["text"], source=data["source"], validation_passed=data["validation_passed"],
                violations=data.get("violations", []), cached=True, duration_ms=0,
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    async def _write_cache(self, key: str, result: NarrationResult) -> None:
        if self._redis is None:
            return
        payload = json.dumps(
            {
                "text": result.text,
                "source": result.source,
                "validation_passed": result.validation_passed,
                "violations": result.violations,
            }
        )
        try:
            await self._redis.setex(key, CACHE_TTL_SECONDS, payload)
        except Exception:
            logger.warning("narration_cache_write_failed", exc_info=True)


def _elapsed_ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)
