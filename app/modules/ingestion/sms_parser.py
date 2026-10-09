"""Deterministic, regex-template-based SMS parsing.

This is the first (and cheapest, and most trustworthy) stage of the
ingestion cascade: if a bank/UPI SMS matches one of our known templates,
we never need to call an LLM for it at all.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID

from app.contracts.events import DataSource, NormalizedFinancialEvent
from app.modules.ingestion.templates import TEMPLATES, KNOWN_BANK_SENDERS, SmsTemplate

_MONTH_ABBREVIATIONS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


@dataclass
class ParseResult:
    event: NormalizedFinancialEvent | None
    method: str  # "template" | "unmatched"
    confidence: float
    reason: str


def normalize_text(raw: str) -> str:
    # Only the rupee symbol is unified to "Rs." here. "INR" is left alone
    # deliberately: several real bank templates (Kotak, Axis) use the
    # literal word "INR" as their currency marker, and normalizing it away
    # would break those templates' own matching.
    text = raw.replace("₹", "Rs.")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_amount(raw: str) -> Decimal:
    # Never use float() for money: binary floating point can't represent
    # most decimal fractions exactly (0.1 + 0.2 != 0.3 in float), which is
    # unacceptable once the number represents currency. Decimal(str) on
    # the comma-stripped text preserves the exact value the SMS contained.
    cleaned = raw.replace(",", "").strip()
    return Decimal(cleaned)


def parse_indian_date(raw: str) -> date:
    # Indian bank SMS always use DD-MM(-YY|YYYY) or DD-Mon-YY ordering.
    # We must never fall back to US MM-DD parsing here: "05-06-26" is
    # 5 June 2026, not May 6th.
    raw = raw.strip()
    parts = re.split(r"[-/]", raw)
    if len(parts) != 3:
        raise ValueError(f"unrecognized date format: {raw!r}")
    day_s, month_s, year_s = parts
    day = int(day_s)
    if month_s.isdigit():
        month = int(month_s)
    else:
        month = _MONTH_ABBREVIATIONS.get(month_s.lower()[:3], 0)
        if month == 0:
            raise ValueError(f"unrecognized month: {month_s!r}")
    year = int(year_s)
    if year < 100:
        year += 2000
    return date(year, month, day)


def _is_known_sender(sender: str) -> bool:
    upper = sender.upper()
    return any(code in upper for code in KNOWN_BANK_SENDERS)


def _resolve_confidence(template: SmsTemplate, sender: str) -> float:
    if not sender:
        return template.confidence
    if _is_known_sender(sender):
        return 0.95
    return 0.80


class SmsParser:
    def __init__(self, templates: list[SmsTemplate] | None = None) -> None:
        self._templates = templates if templates is not None else TEMPLATES

    def parse(
        self,
        raw_sms: str,
        sender: str,
        user_id: UUID,
        received_at: datetime | None = None,
    ) -> ParseResult:
        normalized = normalize_text(raw_sms)

        # template.sender_pattern is metadata, not a hard filter: each
        # bank's body wording is already distinct enough to disambiguate
        # (HDFC's "Rs.X credited to A/c" vs SBI's "A/c credited with Rs
        # X" never overlap), so we deliberately still try every template
        # against the body regardless of sender. This is what lets a
        # correctly-shaped SMS from an unrecognized sender still match at
        # the lower "unknown sender" confidence tier instead of being
        # rejected outright — see _resolve_confidence.
        for template in self._templates:
            match = template.body_pattern.search(normalized)
            if match is None:
                continue

            confidence = _resolve_confidence(template, sender)
            event = self._build_event(
                template, match, sender, user_id, raw_sms, received_at, confidence
            )
            if event is None:
                # Matched the shape but a field (amount/date) was
                # unparseable — try the next template rather than giving
                # up outright.
                continue

            return ParseResult(
                event=event,
                method="template",
                confidence=confidence,
                reason=f"matched template {template.name!r}",
            )

        return ParseResult(
            event=None,
            method="unmatched",
            confidence=0.0,
            reason="no SMS template matched",
        )

    def _build_event(
        self,
        template: SmsTemplate,
        match: re.Match[str],
        sender: str,
        user_id: UUID,
        raw_sms: str,
        received_at: datetime | None,
        confidence: float,
    ) -> NormalizedFinancialEvent | None:
        groups = match.groupdict()

        amount: Decimal | None = None
        if groups.get("amount"):
            try:
                amount = parse_amount(groups["amount"])
            except InvalidOperation:
                return None

        effective_date: date | None = None
        if groups.get("txn_date"):
            try:
                effective_date = parse_indian_date(groups["txn_date"])
            except ValueError:
                effective_date = None

        if effective_date is not None:
            occurred_at = datetime.combine(effective_date, time.min, tzinfo=timezone.utc)
        elif received_at is not None:
            occurred_at = received_at
        else:
            occurred_at = datetime.now(timezone.utc)

        raw_payload = {
            "template": template.name,
            "sender": sender,
            "account_tail": groups.get("account_tail"),
            "balance_after": groups.get("balance"),
            "ref_no": groups.get("ref_no"),
            "raw_text": raw_sms,
        }

        return NormalizedFinancialEvent(
            user_id=user_id,
            event_type=template.event_type,
            amount=amount,
            occurred_at=occurred_at,
            effective_date=effective_date,
            counterparty=groups.get("counterparty"),
            data_source=DataSource.sms,
            confidence_score=confidence,
            raw_payload=raw_payload,
        )
