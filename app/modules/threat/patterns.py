"""Rule-based scam signals as DATA, not code.

Every signal is declared here as a ScamPattern (name, category, weight,
a compiled regex, and an evidence label) rather than scattered across
if/else branches — this keeps the deterministic rule layer auditable,
independently testable, and trivially extensible (add a pattern, don't
touch the scoring logic).

Weights are 0-100 and are meant to be summed and capped at 1.0 by the
caller (see sms_analyzer.score_signals's rule_score formula) — they are
NOT probabilities on their own, just relative severity within the rule
layer. Real scam SMS in India frequently mix Hindi/English ("Hinglish"),
so common phrases include transliterated variants, not just English.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.contracts.events import ThreatCategory, ThreatSignal


@dataclass(frozen=True)
class ScamPattern:
    name: str
    category: ThreatCategory
    weight: float
    pattern: re.Pattern[str]
    evidence_label: str


def _rx(*alternatives: str) -> re.Pattern[str]:
    return re.compile("|".join(alternatives), re.IGNORECASE | re.UNICODE)


# ---------------------------------------------------------------------------
# OTP / CREDENTIALS -- highest weight: a legitimate bank NEVER asks for
# these over SMS/call, so a request for them is close to a smoking gun.
# ---------------------------------------------------------------------------

_OTP_REQUEST = _rx(
    r"\b(share|tell|send|provide|give|read out|reveal)\b[^.\n]{0,30}\b(otp|one[\s-]?time[\s-]?password|cvv|pin|password)\b",
    r"\b(otp|cvv|pin|password)\b[^.\n]{0,30}\b(share|tell|send|batao|bataye|bataiye|bhejo|bhejein)\b",
    r"\botp\s*(bata|batao|bataye|bataiye|share\s*kare)",
)

_CREDENTIAL_REQUEST = _rx(
    r"\b(card|debit card|credit card)\s*(number|no\.?)\b",
    r"\baccount\s*(number|no\.?|details)\b",
    r"\bupi\s*pin\b",
    r"\b(expiry date|card expiry)\b",
    r"\bkarad\s*number|khata\s*number|account\s*ka\s*number\b",
)

_SHARE_SCREEN_REQUEST = _rx(
    r"\banydesk\b", r"\bteamviewer\b", r"\bquicksupport\b", r"\bquick support\b",
    r"\bscreen\s*shar(e|ing)\b", r"\bremote\s*access\b", r"\bremote\s*support\s*app\b",
)

# ---------------------------------------------------------------------------
# BANK IMPERSONATION
# ---------------------------------------------------------------------------

_CLAIMS_BANK_OFFICIAL = _rx(
    r"\b(this is|i am|we are)\b[^.\n]{0,20}\bcalling from\b[^.\n]{0,30}\bbank\b",
    r"\bbank\s*(representative|executive|official|officer)\b",
    r"\bcustomer\s*care\s*(executive|officer)\b",
    r"\bbank\s*se\s*bol\s*raha\s*hoon\b",
    r"\bmain\s*bank\s*(se|ka)\b",
)

_KYC_EXPIRY_CLAIM = _rx(
    r"\bkyc\b[^.\n]{0,25}\b(expir|update|pending|verify|re-?kyc|incomplete|block)\w*",
    r"\b(update|verify)\w*[^.\n]{0,15}\bkyc\b",
    r"\bkyc\s*(update|verify)\s*(kare|karein|karo)",
)

_ACCOUNT_BLOCK_THREAT = _rx(
    r"\baccount\s*(will be|is|has been)?\s*(block|suspend|freeze|deactivat)\w*",
    r"\baccount\s*block\s*ho\s*jayega\b",
    r"\bkhata\s*band\s*ho\s*jayega\b",
)

# ---------------------------------------------------------------------------
# URGENCY MANIPULATION
# ---------------------------------------------------------------------------

_IMMEDIATE_ACTION = _rx(
    r"\bact\s*(now|immediately)\b", r"\bimmediate(ly)?\s*action\b",
    r"\bwithin\s*(the\s*next\s*)?\d+\s*(minutes?|hours?|hrs?)\b",
    r"\bturant\b", r"\babhi\s*(karein|karo|kijiye)\b",
)

_TIME_LIMIT = _rx(
    r"\bexpires?\s*(today|soon|in\s*\d+)\b", r"\bvalid\s*(for|till|until)\s*\d+\s*(minutes?|hours?|hrs?|days?)\b",
    r"\blast\s*chance\b", r"\btoday\s*only\b", r"\baaj\s*hi\b",
)

_THREAT_OF_LOSS = _rx(
    r"\byou\s*will\s*lose\s*(access|money|your)\b", r"\bmoney\s*will\s*be\s*deduct\w*",
    r"\bpenalty\s*(of|will)\b", r"\bfine\s*will\s*be\s*(charged|levied)\b",
    r"\bpaisa\s*kat\s*jayega\b",
)

# ---------------------------------------------------------------------------
# UPI / PAYMENT
# ---------------------------------------------------------------------------

# THE single most common UPI scam in India: a "collect request" is
# actually a request to DEBIT the victim's account, but scammers frame
# approving it as the action needed to RECEIVE money — "accept/approve
# this request to get your payment/refund/cashback". A user who taps
# "accept" on what they believe is an incoming payment is actually
# authorizing an outgoing one.
_COLLECT_REQUEST_DISGUISED = _rx(
    r"\b(accept|approve)\b[^.\n]{0,30}\b(to\s*(receive|get)|request)\b[^.\n]{0,20}\b(money|payment|refund|cashback|amount|rs\.?|rupees|₹)\b",
    r"\b(collect\s*request)\b[^.\n]{0,20}\b(receive|accept|approve)\b",
    r"\bpaise\s*(pane|milne)\s*ke\s*liye\s*(accept|approve)\s*kare\b",
)

_REFUND_SCAM = _rx(
    r"\brefund\s*of\s*(rs\.?|₹|inr)?\s*\d", r"\bclaim\s*(your\s*)?refund\b", r"\brefund\s*(pending|processing)\b",
)

_CASHBACK_SCAM = _rx(
    r"\bcashback\s*of\s*(rs\.?|₹|inr)?\s*\d", r"\bclaim\s*(your\s*)?cashback\b", r"\bguaranteed\s*cashback\b",
)

_WRONG_TRANSFER_SCAM = _rx(
    r"\bsent\s*(money|amount)\s*by\s*mistake\b", r"\bwrong(ly)?\s*transfer\w*",
    r"\bplease\s*return\s*(the\s*)?(amount|money)\b", r"\bgalti\s*se\s*paisa\s*bhej\s*diya\b",
)

# ---------------------------------------------------------------------------
# SOCIAL ENGINEERING
# ---------------------------------------------------------------------------

_AUTHORITY_CLAIM = _rx(
    r"\bincome\s*tax\s*department\b", r"\breserve\s*bank\s*of\s*india\b", r"\brbi\b",
    r"\bcyber\s*(cell|crime)\b", r"\bpolice\s*(department|station)\b", r"\bcourt\s*notice\b",
)

_LOTTERY_PRIZE = _rx(
    r"\byou\s*(have\s*)?won\b", r"\blucky\s*(draw|winner)\b", r"\bprize\s*of\s*(rs\.?|₹|inr)?\s*\d",
    r"\bcongratulations\b[^.\n]{0,20}\bwin\w*", r"\blottery\b",
)

_JOB_OFFER_FEE = _rx(
    r"\bwork\s*from\s*home\b[^.\n]{0,30}\b(earn|salary)\b", r"\bregistration\s*fee\b[^.\n]{0,20}\bjob\b",
    r"\bprocessing\s*fee\b[^.\n]{0,20}\bjob\b", r"\bpart\s*time\s*job\b[^.\n]{0,20}\bearn\b",
)

_INVESTMENT_GUARANTEE = _rx(
    r"\bguaranteed\s*returns?\b", r"\bdouble\s*your\s*money\b", r"\bassured\s*profit\b", r"\bno\s*risk\s*investment\b",
)

_ROMANCE_PATTERN = _rx(
    r"\bneed\s*money\s*for\s*(an\s*)?emergency\b", r"\btrust\s*me\s*(my\s*)?(love|dear|darling)\b",
    r"\bsend\s*money\s*my\s*(love|dear|darling)\b",
)


PATTERNS: tuple[ScamPattern, ...] = (
    ScamPattern("otp_request", ThreatCategory.otp_request, 30, _OTP_REQUEST, "Requests OTP/PIN/CVV/password"),
    ScamPattern(
        "credential_request", ThreatCategory.credential_request, 30, _CREDENTIAL_REQUEST,
        "Requests card/account number or UPI PIN",
    ),
    ScamPattern(
        "share_screen_request", ThreatCategory.social_engineering, 28, _SHARE_SCREEN_REQUEST,
        "Requests a remote-access/screen-share app",
    ),
    ScamPattern(
        "claims_bank_official", ThreatCategory.bank_impersonation, 25, _CLAIMS_BANK_OFFICIAL,
        "Claims to be a bank representative",
    ),
    # NOTE: fake_bank_sender_id here is a TEXT-level heuristic (the body
    # over-asserts its own bank legitimacy, e.g. "official SBI message" —
    # a genuine bank template never needs to say this about itself). The
    # STRUCTURAL check on the actual SMS sender ID field (a mobile number
    # claiming to be a bank) is a separate signal built directly in
    # sms_analyzer.py, since patterns.py's matchers only see message text.
    ScamPattern(
        "fake_bank_sender_id", ThreatCategory.bank_impersonation, 22,
        _rx(r"\bofficial\s*(sbi|hdfc|icici|axis|kotak|pnb|bob)\s*(message|sms|alert)\b"),
        "Message body over-asserts official bank sender identity",
    ),
    ScamPattern("kyc_expiry_claim", ThreatCategory.kyc_scam, 24, _KYC_EXPIRY_CLAIM, "Claims KYC is expiring/pending"),
    ScamPattern(
        "account_block_threat", ThreatCategory.bank_impersonation, 23, _ACCOUNT_BLOCK_THREAT,
        "Threatens account block/suspension",
    ),
    ScamPattern(
        "immediate_action", ThreatCategory.urgency_manipulation, 20, _IMMEDIATE_ACTION, "Demands immediate action"
    ),
    ScamPattern("time_limit", ThreatCategory.urgency_manipulation, 18, _TIME_LIMIT, "Imposes an artificial time limit"),
    ScamPattern(
        "threat_of_loss", ThreatCategory.urgency_manipulation, 20, _THREAT_OF_LOSS, "Threatens financial loss/penalty"
    ),
    ScamPattern(
        "collect_request_disguised", ThreatCategory.upi_scam, 26, _COLLECT_REQUEST_DISGUISED,
        "UPI collect (debit) request disguised as an incoming payment",
    ),
    ScamPattern("refund_scam", ThreatCategory.upi_scam, 24, _REFUND_SCAM, "Fake refund claim"),
    ScamPattern("cashback_scam", ThreatCategory.upi_scam, 20, _CASHBACK_SCAM, "Fake cashback claim"),
    ScamPattern(
        "wrong_transfer_scam", ThreatCategory.upi_scam, 22, _WRONG_TRANSFER_SCAM,
        "Claims money was sent by mistake, asks for return",
    ),
    ScamPattern("authority_claim", ThreatCategory.social_engineering, 18, _AUTHORITY_CLAIM, "Claims to be a government/law authority"),
    ScamPattern("lottery_prize", ThreatCategory.social_engineering, 25, _LOTTERY_PRIZE, "Fake lottery/prize claim"),
    ScamPattern("job_offer_fee", ThreatCategory.social_engineering, 24, _JOB_OFFER_FEE, "Job offer requiring an upfront fee"),
    ScamPattern(
        "investment_guarantee", ThreatCategory.social_engineering, 22, _INVESTMENT_GUARANTEE,
        "Guarantees investment returns",
    ),
    ScamPattern(
        "romance_pattern", ThreatCategory.social_engineering, 20, _ROMANCE_PATTERN,
        "Romance-scam emergency money request pattern",
    ),
)


def score_signals(text: str) -> list[ThreatSignal]:
    """Deterministic, LLM-free scoring pass over free text (SMS body or
    call transcript). Every matching pattern becomes one ThreatSignal
    with detector="rule" — this is the layer the LLM can add to but never
    override (see llm_analyzer.py)."""
    signals: list[ThreatSignal] = []
    for scam_pattern in PATTERNS:
        match = scam_pattern.pattern.search(text)
        if match is None:
            continue
        signals.append(
            ThreatSignal(
                name=scam_pattern.name,
                category=scam_pattern.category,
                weight=scam_pattern.weight,
                evidence=f"{scam_pattern.evidence_label}: {match.group(0)!r}",
                detector="rule",
            )
        )
    return signals
