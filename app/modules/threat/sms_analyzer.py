"""SMS scam analysis: deterministic rules first, LLM escalation only for
the ambiguous middle band. See patterns.py and llm_analyzer.py for the
two layers this combines.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from app.contracts.events import ThreatCategory, ThreatSignal
from app.modules.threat.llm_analyzer import classify_with_llm
from app.modules.threat.patterns import score_signals
from app.modules.threat.url_analyzer import UrlAnalysis, analyse_url
from app.platform.config import Settings

# Below this, the rule signals found are weak enough that the message is
# more likely benign than not — escalating to the LLM for every faint
# signal would be needless cost for little payoff.
AMBIGUOUS_BAND_LOW = 0.25
# Above this, the rule layer is already confident. An LLM call can only
# add a small, capped signal (see llm_analyzer.MAX_SIGNAL_WEIGHT), so it
# would rarely change the outcome — and the confident case is exactly
# where speed (skipping an extra network round trip) matters most.
AMBIGUOUS_BAND_HIGH = 0.65

_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
# UPI IDs look like "name@handle" (e.g. "9876543210@paytm"), which is
# also the shape of an email address — the negative lookahead for a
# following "." excludes "user@example.com" (a real domain has a TLD)
# while still matching short UPI PSP handles, which don't.
_UPI_ID_PATTERN = re.compile(r"\b[\w.\-]{2,256}@[a-zA-Z]{2,20}\b(?!\.)")
_AMOUNT_PATTERN = re.compile(r"(?:rs\.?|inr|₹)\s?([\d,]+(?:\.\d{1,2})?)", re.IGNORECASE)

# Genuine bank/service sender IDs are short alphanumeric codes, often
# with a 2-letter telecom prefix (e.g. "AX-HDFCBK", "VM-ICICIB") — never
# a bare 10-digit mobile number. A message CLAIMING bank origin while
# sent from an ordinary phone number is a strong tell.
_MOBILE_NUMBER_SENDER = re.compile(r"^\+?91?[6-9]\d{9}$")
_BANK_CLAIM_WORDS = re.compile(r"\bbank\b", re.IGNORECASE)


@dataclass(frozen=True)
class ThreatAnalysis:
    signals: list[ThreatSignal]
    rule_score: float
    final_score: float
    requested_amount: Decimal | None = None
    payee_identifier: str | None = None
    urls: list[UrlAnalysis] = field(default_factory=list)
    llm_escalated: bool = False


def _extract_urls(text: str) -> list[str]:
    return _URL_PATTERN.findall(text)


def _extract_upi_ids(text: str) -> list[str]:
    return _UPI_ID_PATTERN.findall(text)


def _extract_amount(text: str) -> Decimal | None:
    match = _AMOUNT_PATTERN.search(text)
    if not match:
        return None
    try:
        return Decimal(match.group(1).replace(",", ""))
    except InvalidOperation:
        return None


def _sender_signal(sender: str, body: str) -> ThreatSignal | None:
    if not sender:
        return None
    if _MOBILE_NUMBER_SENDER.match(sender.strip()) and _BANK_CLAIM_WORDS.search(body):
        return ThreatSignal(
            name="mobile_number_claims_bank",
            category=ThreatCategory.bank_impersonation,
            weight=25,
            evidence=f"Sent from an ordinary mobile number ('{sender}') while claiming to be from a bank",
            detector="rule",
        )
    return None


def _compute_rule_score(signals: list[ThreatSignal]) -> float:
    total_weight = sum(signal.weight for signal in signals if signal.detector == "rule")
    return min(1.0, total_weight / 100)


def _compute_final_score(signals: list[ThreatSignal]) -> float:
    # Sums EVERY signal, rule and model alike — there is no separate
    # "model score" that could ever be substituted for the rule score,
    # only addition on top of it. See llm_analyzer.py's module docstring.
    total_weight = sum(signal.weight for signal in signals)
    return min(1.0, total_weight / 100)


async def analyse_sms(
    body: str,
    sender: str,
    *,
    settings: Settings | None = None,
    http_client: Any | None = None,
) -> ThreatAnalysis:
    signals = list(score_signals(body))

    sender_signal = _sender_signal(sender, body)
    if sender_signal is not None:
        signals.append(sender_signal)

    urls = _extract_urls(body)
    url_analyses: list[UrlAnalysis] = []
    payment_claim = bool(_AMOUNT_PATTERN.search(body)) or any(
        signal.category == ThreatCategory.upi_scam for signal in signals
    )
    for url in urls:
        analysis = await analyse_url(url, text_claims_payment=payment_claim)
        url_analyses.append(analysis)
        signals.extend(analysis.signals)

    upi_ids = _extract_upi_ids(body)
    payee_identifier = upi_ids[0] if upi_ids else None
    requested_amount = _extract_amount(body)

    rule_score = _compute_rule_score(signals)

    # LLM escalation ONLY in the ambiguous middle band — see the module
    # constants' comments for why each boundary is where it is.
    llm_escalated = False
    if AMBIGUOUS_BAND_LOW <= rule_score <= AMBIGUOUS_BAND_HIGH:
        llm_escalated = True
        model_signals = await classify_with_llm(body, settings=settings, http_client=http_client)
        signals.extend(model_signals)

    final_score = _compute_final_score(signals)

    return ThreatAnalysis(
        signals=signals,
        rule_score=rule_score,
        final_score=final_score,
        requested_amount=requested_amount,
        payee_identifier=payee_identifier,
        urls=url_analyses,
        llm_escalated=llm_escalated,
    )
