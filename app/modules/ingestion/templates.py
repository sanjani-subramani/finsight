"""Regex templates for Indian bank/UPI transaction SMS.

Each template is a pure pattern-matching spec: a sender-ID filter, a body
regex with named capture groups, and the FinancialEventType it implies on
a match. sms_parser.py owns all the logic for trying these in order,
extracting fields, and turning a match into a NormalizedFinancialEvent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.contracts.events import FinancialEventType

# Confidence assigned to a template match when no sender-based adjustment
# applies (see sms_parser._resolve_confidence: bumped to 0.95 for a
# KNOWN_BANK_SENDERS match, dropped to 0.80 for an unrecognized sender).
DEFAULT_TEMPLATE_CONFIDENCE = 0.90

# Sender IDs (DLT headers) for banks/UPI apps we recognize with high
# confidence. Real sender IDs often carry a 2-letter DLT prefix
# ("VM-HDFCBK-S", "AD-SBIINB") so membership is checked by substring, not
# exact match — see sms_parser._is_known_sender.
KNOWN_BANK_SENDERS = {
    "HDFCBK",
    "SBIINB",
    "SBIPSG",
    "ICICIB",
    "ICICIT",
    "AXISBK",
    "KOTAKB",
    "PAYTM",
    "GPAY",
    "PHONPE",
}

# Building blocks, tolerant of comma-separated amounts (Indian or
# international grouping), optional decimals, and varying whitespace.
_AMOUNT = r"\d[\d,]*(?:\.\d{1,2})?"
_DATE = r"(?P<txn_date>\d{1,2}[-/](?:\d{1,2}|[A-Za-z]{3,9})[-/]\d{2,4})"
_ACCOUNT_TAIL = r"(?:[Xx]{2,4})?(?P<account_tail>\d{3,6})"

# The counterparty capture is lazy (`+?`) and, in most templates, every
# token after it (balance, ref no, ...) is itself optional — so without an
# explicit stop condition the lazy quantifier would grab a single
# character and immediately let the rest of the pattern match empty.
# _PARTY_END pins it to the next recognizable keyword or end-of-string,
# with \b word boundaries so a keyword embedded inside a name (e.g. the
# "ON" inside "AMAZON") can't trigger a premature stop.
_PARTY_END = (
    r"(?=\.?\s*(?:"
    r"\b(?:Avl|UPI|Ref|Bal|Limit|bill|is\s+due|from|in\s+your|on)\b"
    r"|$"
    r"))"
)
# UPI counterparties are VPAs like "raj@okhdfcbank" — '@' must be allowed.
_PARTY = rf"(?P<counterparty>[A-Za-z0-9&.'@\- ]+?){_PARTY_END}"
_BALANCE = rf"(?P<balance>{_AMOUNT})"


@dataclass(frozen=True)
class SmsTemplate:
    name: str
    sender_pattern: re.Pattern[str] | None
    body_pattern: re.Pattern[str]
    event_type: FinancialEventType
    field_map: dict[str, str]
    confidence: float = DEFAULT_TEMPLATE_CONFIDENCE


def _make_template(
    *,
    name: str,
    sender: str | None,
    body: str,
    event_type: FinancialEventType,
) -> SmsTemplate:
    body_pattern = re.compile(body, re.IGNORECASE)
    sender_pattern = re.compile(sender, re.IGNORECASE) if sender else None
    # Group names in every pattern here are already the canonical field
    # names (amount, counterparty, account_tail, balance, txn_date,
    # ref_no), so this is an identity map — but deriving it from the
    # compiled pattern (rather than hand-duplicating the group list) means
    # it can never drift out of sync with the regex.
    field_map = {group_name: group_name for group_name in body_pattern.groupindex}
    return SmsTemplate(
        name=name,
        sender_pattern=sender_pattern,
        body_pattern=body_pattern,
        event_type=event_type,
        field_map=field_map,
    )


# ---------------------------------------------------------------------------
# HDFC
# ---------------------------------------------------------------------------

HDFC_CREDIT = _make_template(
    name="hdfc_credit",
    sender="HDFCBK",
    body=(
        rf"Rs\.?\s*(?P<amount>{_AMOUNT})\s*credited\s+to\s+A/?c\.?\s*{_ACCOUNT_TAIL}\s*"
        rf"on\s*{_DATE}\s*from\s+{_PARTY}\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*Rs\.?\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.income_received,
)

HDFC_DEBIT = _make_template(
    name="hdfc_debit",
    sender="HDFCBK",
    body=(
        rf"Rs\.?\s*(?P<amount>{_AMOUNT})\s*debited\s+from\s+A/?c\.?\s*{_ACCOUNT_TAIL}\s*"
        rf"on\s*{_DATE}\s*to\s+{_PARTY}\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*Rs\.?\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.expense,
)

# ---------------------------------------------------------------------------
# SBI — "Rs" without a dot, lowercase "a/c"
# ---------------------------------------------------------------------------

SBI_CREDIT = _make_template(
    name="sbi_credit",
    sender="SBI",
    body=(
        rf"(?:your\s+)?a/?c\.?\s*{_ACCOUNT_TAIL}\s*credited\s+with\s+Rs\.?\s*(?P<amount>{_AMOUNT})\s*"
        rf"on\s*{_DATE}\s*by\s+{_PARTY}\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*Rs\.?\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.income_received,
)

SBI_DEBIT = _make_template(
    name="sbi_debit",
    sender="SBI",
    body=(
        rf"(?:your\s+)?a/?c\.?\s*{_ACCOUNT_TAIL}\s*debited\s+by\s+Rs\.?\s*(?P<amount>{_AMOUNT})\s*"
        rf"on\s*{_DATE}\s*trf\s+to\s+{_PARTY}\.?\s*"
        rf"(?:Ref\.?\s*No\.?\s*[:\-]?\s*(?P<ref_no>[A-Za-z0-9]+))?\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*Rs\.?\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.expense,
)

# ---------------------------------------------------------------------------
# ICICI
# ---------------------------------------------------------------------------

ICICI_CREDIT = _make_template(
    name="icici_credit",
    sender="ICICI",
    body=(
        rf"ICICI\s*Bank\s*Acct\.?\s*{_ACCOUNT_TAIL}\s*credited\s*Rs\.?\s*(?P<amount>{_AMOUNT})\s*"
        rf"on\s*{_DATE}\s*from\s+{_PARTY}\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*:?\s*Rs\.?\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.income_received,
)

ICICI_DEBIT = _make_template(
    name="icici_debit",
    sender="ICICI",
    body=(
        rf"ICICI\s*Bank\s*Acct\.?\s*{_ACCOUNT_TAIL}\s*debited\s*for\s*Rs\.?\s*(?P<amount>{_AMOUNT})\s*"
        rf"on\s*{_DATE}\s*towards\s+{_PARTY}\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*:?\s*Rs\.?\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.expense,
)

# ---------------------------------------------------------------------------
# Axis
# ---------------------------------------------------------------------------

AXIS_CREDIT = _make_template(
    name="axis_credit",
    sender="AXISBK",
    body=(
        rf"Rs\.?\s*(?P<amount>{_AMOUNT})\s*credited\s+to\s+A/?c\.?\s*no\.?\s*{_ACCOUNT_TAIL}\s*"
        rf"on\s*{_DATE}\s*by\s+{_PARTY}\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*INR\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.income_received,
)

AXIS_DEBIT = _make_template(
    name="axis_debit",
    sender="AXISBK",
    body=(
        rf"Rs\.?\s*(?P<amount>{_AMOUNT})\s*debited\s+from\s+A/?c\.?\s*no\.?\s*{_ACCOUNT_TAIL}\s*"
        rf"on\s*{_DATE}\s*for\s+{_PARTY}\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*INR\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.expense,
)

# ---------------------------------------------------------------------------
# Kotak
# ---------------------------------------------------------------------------

KOTAK_CREDIT = _make_template(
    name="kotak_credit",
    sender="KOTAKB",
    body=(
        rf"INR\s*(?P<amount>{_AMOUNT})\s*credited\s+to\s+a/?c\.?\s*{_ACCOUNT_TAIL}\s*"
        rf"on\s*{_DATE}\s*from\s+{_PARTY}\.?\s*"
        rf"(?:Bal\.?\s*INR\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.income_received,
)

KOTAK_DEBIT = _make_template(
    name="kotak_debit",
    sender="KOTAKB",
    body=(
        rf"INR\s*(?P<amount>{_AMOUNT})\s*debited\s+from\s+a/?c\.?\s*{_ACCOUNT_TAIL}\s*"
        rf"on\s*{_DATE}\s*for\s+{_PARTY}\.?\s*"
        rf"(?:Bal\.?\s*INR\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.expense,
)

# ---------------------------------------------------------------------------
# UPI (GPay / PhonePe / Paytm) — sender varies a lot in practice, so these
# are sender-agnostic and rely on body wording alone.
# ---------------------------------------------------------------------------

UPI_SENT = _make_template(
    name="upi_sent",
    sender=None,
    body=(
        rf"Rs\.?\s*(?P<amount>{_AMOUNT})\s*sent\s+to\s+{_PARTY}\s*from\s+your\s+A/?c\.?\s*{_ACCOUNT_TAIL}\s*"
        rf"on\s*{_DATE}\.?\s*"
        rf"(?:UPI\s*Ref\.?\s*No\.?\s*[:\-]?\s*(?P<ref_no>[A-Za-z0-9]+))?"
    ),
    event_type=FinancialEventType.transfer_out,
)

UPI_RECEIVED = _make_template(
    name="upi_received",
    sender=None,
    body=(
        rf"(?:you\s+have\s+)?received\s+Rs\.?\s*(?P<amount>{_AMOUNT})\s*from\s+{_PARTY}\s*"
        rf"in\s+your\s+A/?c\.?\s*{_ACCOUNT_TAIL}\s*on\s*{_DATE}\.?\s*"
        rf"(?:UPI\s*Ref\.?\s*No\.?\s*[:\-]?\s*(?P<ref_no>[A-Za-z0-9]+))?"
    ),
    event_type=FinancialEventType.transfer_in,
)

# ---------------------------------------------------------------------------
# Card transaction alert
# ---------------------------------------------------------------------------

CARD_TRANSACTION = _make_template(
    name="card_transaction",
    sender=None,
    body=(
        rf"Credit\s*Card\.?\s*{_ACCOUNT_TAIL}\s*has\s+been\s+used\s+for\s+Rs\.?\s*(?P<amount>{_AMOUNT})\s*"
        rf"at\s+{_PARTY}\s*on\s*{_DATE}\.?\s*"
        rf"(?:Avl\.?\s*Limit\.?\s*Rs\.?\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.expense,
)

# ---------------------------------------------------------------------------
# EMI debit alert
# ---------------------------------------------------------------------------

EMI_DEBIT = _make_template(
    name="emi_debit",
    sender=None,
    body=(
        rf"Rs\.?\s*(?P<amount>{_AMOUNT})\s*has\s+been\s+debited\s+towards\s+EMI\s+for\s+Loan\s+A/?c\.?\s*{_ACCOUNT_TAIL}\s*"
        rf"on\s*{_DATE}\.?\s*"
        rf"(?:Avl\.?\s*Bal\.?\s*Rs\.?\s*{_BALANCE})?"
    ),
    event_type=FinancialEventType.emi_paid,
)

# ---------------------------------------------------------------------------
# Bill due reminder — no account_tail, counterparty is the biller name
# ---------------------------------------------------------------------------

BILL_DUE = _make_template(
    name="bill_due",
    sender=None,
    body=(
        rf"Your\s+{_PARTY}\s+bill\s+of\s+Rs\.?\s*(?P<amount>{_AMOUNT})\s*is\s+due\s+on\s*{_DATE}"
    ),
    event_type=FinancialEventType.bill_due,
)


# Bank-specific templates first (gated by sender_pattern), then
# sender-agnostic ones — this keeps a bank SMS from ever being misread by
# a looser generic pattern when a precise one is available.
TEMPLATES: list[SmsTemplate] = [
    HDFC_CREDIT,
    HDFC_DEBIT,
    SBI_CREDIT,
    SBI_DEBIT,
    ICICI_CREDIT,
    ICICI_DEBIT,
    AXIS_CREDIT,
    AXIS_DEBIT,
    KOTAK_CREDIT,
    KOTAK_DEBIT,
    UPI_SENT,
    UPI_RECEIVED,
    CARD_TRANSACTION,
    EMI_DEBIT,
    BILL_DUE,
]
