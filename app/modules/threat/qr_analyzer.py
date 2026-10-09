"""UPI QR code threat analysis.

Decodes the UPI deep-link payload a QR code encodes (upi://pay?pa=...)
and checks it against a few concrete red flags. A non-UPI QR containing a
plain URL is delegated to url_analyzer — a QR code is just a delivery
mechanism, not a separate threat category once decoded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs, urlsplit

from rapidfuzz import fuzz

from app.contracts.events import ThreatCategory, ThreatSignal
from app.modules.threat.url_analyzer import UrlAnalysis, analyse_url

# A payee VPA's local part (before the @) is compared against the
# claimed merchant name with fuzzy string matching, since real VPAs are
# rarely an exact match (e.g. "amazonpay" vs "Amazon"); below this
# similarity, the mismatch is treated as a red flag.
QR_PAYEE_NAME_MATCH_THRESHOLD = 55
# Legitimate one-off P2P/merchant amounts vary, but a QR asking for more
# than 3x what this user normally pays is unusual enough to flag.
LARGE_AMOUNT_MULTIPLIER = Decimal("3.0")


@dataclass(frozen=True)
class QrAnalysis:
    is_upi: bool
    payee_vpa: str | None = None
    payee_name: str | None = None
    amount: Decimal | None = None
    signals: list[ThreatSignal] = field(default_factory=list)
    url_analysis: UrlAnalysis | None = None


def _parse_upi_payload(payload: str) -> dict[str, str]:
    parsed = urlsplit(payload)
    query = parse_qs(parsed.query)
    return {key: values[0] for key, values in query.items() if values}


async def analyse_qr(
    payload: str,
    *,
    claimed_merchant_name: str | None = None,
    typical_transaction_amount: Decimal | None = None,
    known_payee_vpas: set[str] | None = None,
) -> QrAnalysis:
    if not payload.lower().startswith("upi://"):
        if "://" in payload:
            url_result = await analyse_url(payload)
            return QrAnalysis(is_upi=False, signals=url_result.signals, url_analysis=url_result)
        return QrAnalysis(is_upi=False)

    fields = _parse_upi_payload(payload)
    payee_vpa = fields.get("pa")
    payee_name = fields.get("pn")
    amount_str = fields.get("am")
    amount: Decimal | None = None
    if amount_str:
        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            amount = None

    signals: list[ThreatSignal] = []

    # Legitimate merchant QRs (posters, till stickers) are almost always
    # printed WITHOUT a pre-filled amount, so the same code works for any
    # purchase — a "scan and pay this exact amount" QR pre-fills it,
    # which is unusual coming from a claimed merchant rather than a
    # genuine one-off P2P request.
    if amount is not None and claimed_merchant_name:
        signals.append(
            ThreatSignal(
                name="qr_amount_prefilled",
                category=ThreatCategory.malicious_qr,
                weight=20,
                evidence=f"Amount Rs.{amount} is pre-filled on a QR claiming to be merchant '{claimed_merchant_name}'",
                detector="rule",
            )
        )

    if payee_vpa and claimed_merchant_name:
        vpa_local_part = payee_vpa.split("@")[0]
        similarity = fuzz.ratio(vpa_local_part.lower(), claimed_merchant_name.lower())
        if similarity < QR_PAYEE_NAME_MATCH_THRESHOLD:
            signals.append(
                ThreatSignal(
                    name="qr_payee_mismatch",
                    category=ThreatCategory.malicious_qr,
                    weight=30,
                    evidence=f"Payee VPA '{payee_vpa}' does not match claimed merchant '{claimed_merchant_name}'",
                    detector="rule",
                )
            )

    if amount is not None and typical_transaction_amount and typical_transaction_amount > 0:
        if amount > typical_transaction_amount * LARGE_AMOUNT_MULTIPLIER:
            signals.append(
                ThreatSignal(
                    name="qr_unusually_large_amount",
                    category=ThreatCategory.malicious_qr,
                    weight=22,
                    evidence=(
                        f"Amount Rs.{amount} is over {LARGE_AMOUNT_MULTIPLIER:.0f}x the user's typical "
                        f"Rs.{typical_transaction_amount}"
                    ),
                    detector="rule",
                )
            )

    if payee_vpa and known_payee_vpas is not None and payee_vpa not in known_payee_vpas:
        signals.append(
            ThreatSignal(
                name="qr_newly_seen_payee",
                category=ThreatCategory.malicious_qr,
                weight=12,
                evidence=f"Payee VPA '{payee_vpa}' has not been paid before",
                detector="rule",
            )
        )

    return QrAnalysis(is_upi=True, payee_vpa=payee_vpa, payee_name=payee_name, amount=amount, signals=signals)
