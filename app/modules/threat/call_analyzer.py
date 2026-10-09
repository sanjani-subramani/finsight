"""Call/transcript scam analysis.

PLATFORM CONSTRAINT — documented honestly, not glossed over: live call
audio interception is NOT available on iOS at all (CallKit exposes no
raw audio tap to third-party apps), and Android restricts the
CAPTURE_AUDIO_OUTPUT permission to system/privileged apps only. A normal
consumer app cannot listen to a live phone call on either platform.

This module therefore analyses:
  (a) user-initiated recordings — the user explicitly records a call they
      suspect, which both platforms DO allow for the user's own audio,
  (b) uploaded audio, transcribed locally via transcribe_audio(), and
  (c) simulated/typed transcripts, for demos and testing.

The THREAT ENGINE below (analyse_transcript) is fully real — the same
rule+LLM cascade as SMS, tuned for conversational patterns. Only the live
audio CAPTURE path is constrained by the OS; detection itself is not.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.contracts.events import ThreatCategory, ThreatSignal
from app.modules.threat.llm_analyzer import classify_with_llm
from app.modules.threat.patterns import score_signals
from app.modules.threat.sms_analyzer import AMBIGUOUS_BAND_HIGH, AMBIGUOUS_BAND_LOW, ThreatAnalysis
from app.platform.config import Settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

_STAYS_ON_LINE = re.compile(r"\bstay\s*on\s*(the\s*)?line\b", re.IGNORECASE)
_DISCOURAGES_VERIFICATION = re.compile(
    r"\b(do\s*not|don'?t)\s*(hang\s*up|disconnect|call\s*(the\s*)?bank|verify|check\s*with)\b", re.IGNORECASE
)
_URGENCY_WORD = re.compile(r"\b(right now|this instant|immediately|urgent(ly)?|last warning|hurry)\b", re.IGNORECASE)


def _call_specific_signals(transcript_text: str) -> list[ThreatSignal]:
    signals: list[ThreatSignal] = []

    if _STAYS_ON_LINE.search(transcript_text):
        signals.append(
            ThreatSignal(
                name="stay_on_line_request",
                category=ThreatCategory.social_engineering,
                weight=22,
                evidence="Caller asks the user to stay on the line while performing a transaction",
                detector="rule",
            )
        )

    if _DISCOURAGES_VERIFICATION.search(transcript_text):
        signals.append(
            ThreatSignal(
                name="discourages_independent_verification",
                category=ThreatCategory.social_engineering,
                weight=25,
                evidence="Caller discourages hanging up or verifying independently",
                detector="rule",
            )
        )

    # Escalating urgency ACROSS the conversation: count urgency phrases
    # in each half of the transcript separately. A single urgent remark
    # near the start is normal impatience; urgency that GROWS as the
    # call progresses is the manipulation pattern this specifically
    # targets (a static count can't tell the two apart).
    midpoint = len(transcript_text) // 2
    first_half_count = len(_URGENCY_WORD.findall(transcript_text[:midpoint]))
    second_half_count = len(_URGENCY_WORD.findall(transcript_text[midpoint:]))
    if second_half_count > first_half_count and second_half_count >= 2:
        signals.append(
            ThreatSignal(
                name="escalating_urgency",
                category=ThreatCategory.urgency_manipulation,
                weight=20,
                evidence=(
                    f"Urgency language increases across the call "
                    f"({first_half_count} mention(s) early, {second_half_count} later)"
                ),
                detector="rule",
            )
        )

    return signals


def _compute_scores(signals: list[ThreatSignal]) -> tuple[float, float]:
    # Same additive-only formula as sms_analyzer.py, duplicated (not
    # imported) since it's two lines and these are siblings within the
    # same module, not a cross-module reach.
    rule_weight = sum(signal.weight for signal in signals if signal.detector == "rule")
    total_weight = sum(signal.weight for signal in signals)
    return min(1.0, rule_weight / 100), min(1.0, total_weight / 100)


async def analyse_transcript(
    transcript_text: str,
    *,
    settings: Settings | None = None,
    http_client: Any | None = None,
) -> ThreatAnalysis:
    signals = list(score_signals(transcript_text))
    signals.extend(_call_specific_signals(transcript_text))

    rule_score, _ = _compute_scores(signals)

    llm_escalated = False
    if AMBIGUOUS_BAND_LOW <= rule_score <= AMBIGUOUS_BAND_HIGH:
        llm_escalated = True
        model_signals = await classify_with_llm(transcript_text, settings=settings, http_client=http_client)
        signals.extend(model_signals)

    rule_score, final_score = _compute_scores(signals)

    return ThreatAnalysis(
        signals=signals,
        rule_score=rule_score,
        final_score=final_score,
        llm_escalated=llm_escalated,
    )


@dataclass(frozen=True)
class TranscriptionResult:
    text: str | None
    available: bool
    reason: str | None = None


_whisper_model_cache: Any = None


def _get_whisper_model(model_class: Any) -> Any:
    global _whisper_model_cache
    if _whisper_model_cache is None:
        _whisper_model_cache = model_class("base", device="cpu", compute_type="int8")
    return _whisper_model_cache


async def transcribe_audio(file_path: str | Path) -> TranscriptionResult:
    """Transcribes a local audio file with faster-whisper, if installed.

    Local transcription means the audio NEVER leaves this machine — a
    deliberate privacy choice for a financial product. The alternative
    (a cloud speech-to-text API) would mean sending potentially sensitive
    call audio to a third party, which this product will not do.
    """
    try:
        from faster_whisper import WhisperModel  # type: ignore[import-not-found]
    except ImportError:
        return TranscriptionResult(
            text=None,
            available=False,
            reason="faster-whisper is not installed; audio transcription is unavailable in this environment",
        )

    try:
        model = _get_whisper_model(WhisperModel)
        segments, _info = await asyncio.to_thread(model.transcribe, str(file_path))
        text = " ".join(segment.text.strip() for segment in segments)
        return TranscriptionResult(text=text, available=True)
    except Exception:
        logger.error("transcription_failed", file=str(file_path), exc_info=True)
        return TranscriptionResult(text=None, available=False, reason="transcription failed")
