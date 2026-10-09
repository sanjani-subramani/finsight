"""Thin, shared wrapper for calling the Groq chat completions API.

Lives in app.platform (not inside any one module) because more than one
module needs it — per the module boundary rule (see README), a module may
depend on app.platform but never on another module's internals, so shared
infrastructure like "how do we call the LLM" belongs here, not duplicated
or cross-imported between app.modules.ingestion and app.modules.confidence.
"""

from __future__ import annotations

import httpx

from app.platform.config import Settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TIMEOUT_SECONDS = 10.0


async def call_groq_json(
    system_prompt: str,
    user_content: str,
    settings: Settings,
    *,
    http_client: httpx.AsyncClient | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    retries: int = 1,
    temperature: float = 0.0,
    max_tokens: int | None = None,
) -> str | None:
    """Returns the raw JSON string content of the model's reply, or None
    on any failure (missing key, network error after retries, HTTP
    error). Callers own json.loads + their own Pydantic validation — the
    expected response shape differs per caller.

    temperature defaults to 0.0 (deterministic) — every existing caller
    relies on that for reproducibility. A caller producing user-facing
    prose rather than a classification (e.g. the Step 12 narrator) may
    raise it slightly for readability; the fact-checking that makes that
    safe happens entirely outside this function.
    """
    if not settings.GROQ_API_KEY:
        return None

    payload: dict[str, object] = {
        "model": GROQ_MODEL,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    owns_client = http_client is None
    client = http_client or httpx.AsyncClient(timeout=timeout_seconds)

    try:
        for attempt in range(retries + 1):
            try:
                response = await client.post(GROQ_API_URL, json=payload, headers=headers)
                response.raise_for_status()
                body = response.json()
                content: str = body["choices"][0]["message"]["content"]
                return content
            except httpx.HTTPStatusError:
                # A real API error (4xx/5xx) — not transient, don't retry.
                logger.warning("groq_call_http_error")
                return None
            except httpx.RequestError:
                if attempt < retries:
                    continue
                logger.warning("groq_call_network_error")
                return None
            except (KeyError, IndexError):
                logger.warning("groq_call_malformed_response")
                return None
        return None
    finally:
        if owns_client:
            await client.aclose()
