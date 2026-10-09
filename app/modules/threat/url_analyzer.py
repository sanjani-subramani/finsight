"""Deterministic URL threat analysis. No LLM anywhere in this module —
every check here is a concrete, explainable rule, which matters because a
malicious link is exactly the kind of untrusted input we should never
feed into a prompt (see llm_analyzer.py's injection defence for the
analogous concern on the text side).
"""

from __future__ import annotations

import asyncio
import ipaddress
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlsplit

import httpx
from rapidfuzz.distance import Levenshtein

from app.contracts.events import ThreatCategory, ThreatSignal
from app.platform.logging import get_logger

logger = get_logger(__name__)

KNOWN_BANK_DOMAINS = (
    "hdfcbank", "sbi", "icicibank", "axisbank", "kotak", "paytm", "phonepe", "gpay",
)
TYPOSQUAT_MAX_DISTANCE = 2
SUSPICIOUS_TLDS = (".tk", ".ml", ".ga", ".cf", ".xyz", ".top")
SHORTENER_DOMAINS = ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "rebrand.ly")
MAX_NORMAL_SUBDOMAINS = 2
REDIRECT_TIMEOUT_SECONDS = 3.0
WHOIS_TIMEOUT_SECONDS = 2.0
NEW_DOMAIN_THRESHOLD_DAYS = 90


@dataclass(frozen=True)
class UrlAnalysis:
    url: str
    signals: list[ThreatSignal] = field(default_factory=list)
    resolved_url: str | None = None


def _extract_host(url: str) -> str | None:
    parsed = urlsplit(url if "://" in url else f"http://{url}")
    host = parsed.hostname
    return host.lower() if host else None


def _registrable_label(host: str) -> str:
    """The second-level label (e.g. "hdfcbank" from "www.hdfcbank.com") --
    a simple last-two-labels split is good enough here since we're only
    comparing against a small, known list of bank/payment domains, not
    doing general public-suffix-list resolution."""
    labels = host.split(".")
    return labels[-2] if len(labels) >= 2 else host


def _check_typosquatting(host: str) -> ThreatSignal | None:
    sld = _registrable_label(host)
    for bank in KNOWN_BANK_DOMAINS:
        if sld == bank:
            return None  # exact match — not typosquatting
        distance = Levenshtein.distance(sld, bank)
        if 1 <= distance <= TYPOSQUAT_MAX_DISTANCE:
            return ThreatSignal(
                name="typosquatted_domain",
                category=ThreatCategory.phishing_link,
                weight=35,
                evidence=f"'{host}' is {distance} edit(s) from known domain '{bank}'",
                detector="rule",
            )
    return None


def _check_suspicious_tld(host: str) -> ThreatSignal | None:
    for tld in SUSPICIOUS_TLDS:
        if host.endswith(tld):
            return ThreatSignal(
                name="suspicious_tld", category=ThreatCategory.phishing_link, weight=20,
                evidence=f"Uses suspicious TLD '{tld}'", detector="rule",
            )
    return None


def _check_ip_host(host: str) -> ThreatSignal | None:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return None
    return ThreatSignal(
        name="ip_address_host", category=ThreatCategory.phishing_link, weight=25,
        evidence=f"URL host is a raw IP address ('{host}')", detector="rule",
    )


def _check_excessive_subdomains(host: str) -> ThreatSignal | None:
    subdomain_count = max(0, len(host.split(".")) - 2)
    if subdomain_count > MAX_NORMAL_SUBDOMAINS:
        return ThreatSignal(
            name="excessive_subdomains", category=ThreatCategory.phishing_link, weight=15,
            evidence=f"{subdomain_count} subdomains in '{host}'", detector="rule",
        )
    return None


def _check_punycode(host: str) -> ThreatSignal | None:
    if "xn--" in host:
        return ThreatSignal(
            name="punycode_homograph", category=ThreatCategory.phishing_link, weight=30,
            evidence=f"Punycode-encoded hostname ('{host}') — possible homograph attack", detector="rule",
        )
    return None


def _check_https_absence(url: str, text_claims_payment: bool) -> ThreatSignal | None:
    if text_claims_payment and url.lower().startswith("http://"):
        return ThreatSignal(
            name="no_https_on_payment_link", category=ThreatCategory.phishing_link, weight=15,
            evidence="Payment-claiming link is not served over HTTPS", detector="rule",
        )
    return None


async def _resolve_shortener(url: str, host: str) -> str | None:
    if host not in SHORTENER_DOMAINS:
        return None
    try:
        async with httpx.AsyncClient(timeout=REDIRECT_TIMEOUT_SECONDS, follow_redirects=False) as client:
            response = await client.head(url)
        return response.headers.get("location")
    except httpx.HTTPError:
        logger.warning("shortener_resolution_failed", url=url)
        return None


async def _check_domain_age(host: str) -> ThreatSignal | None:
    """Best-effort WHOIS lookup — never required, never allowed to block
    the request: the `whois` package's lookup is synchronous, so it runs
    in a thread with a hard timeout; if the package isn't installed, the
    lookup fails, or it times out, this simply contributes no signal.
    """
    try:
        import whois  # type: ignore[import-not-found]
    except ImportError:
        return None

    try:
        record = await asyncio.wait_for(asyncio.to_thread(whois.whois, host), timeout=WHOIS_TIMEOUT_SECONDS)
        creation_date = record.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0] if creation_date else None
        if creation_date is None:
            return None
        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - creation_date).days
        if age_days < NEW_DOMAIN_THRESHOLD_DAYS:
            return ThreatSignal(
                name="newly_registered_domain", category=ThreatCategory.phishing_link, weight=20,
                evidence=f"Domain registered {age_days} day(s) ago", detector="rule",
            )
    except Exception:
        logger.warning("whois_lookup_failed", host=host, exc_info=True)
    return None


async def analyse_url(url: str, *, text_claims_payment: bool = False) -> UrlAnalysis:
    host = _extract_host(url)
    if host is None:
        return UrlAnalysis(url=url, signals=[])

    resolved_url: str | None = None
    effective_host = host
    shortener_target = await _resolve_shortener(url, host)
    if shortener_target:
        resolved_url = shortener_target
        resolved_host = _extract_host(shortener_target)
        if resolved_host:
            effective_host = resolved_host

    checks: list[ThreatSignal | None] = [
        _check_typosquatting(effective_host),
        _check_suspicious_tld(effective_host),
        _check_ip_host(effective_host),
        _check_excessive_subdomains(effective_host),
        _check_punycode(effective_host),
        _check_https_absence(url, text_claims_payment),
        await _check_domain_age(effective_host),
    ]

    if shortener_target:
        checks.append(
            ThreatSignal(
                name="url_shortener", category=ThreatCategory.phishing_link, weight=15,
                evidence=f"URL shortener resolves to '{shortener_target}'", detector="rule",
            )
        )
    elif host in SHORTENER_DOMAINS:
        checks.append(
            ThreatSignal(
                name="url_shortener_unresolved", category=ThreatCategory.phishing_link, weight=10,
                evidence=f"URL shortener '{host}' could not be resolved", detector="rule",
            )
        )

    signals = [signal for signal in checks if signal is not None]
    return UrlAnalysis(url=url, signals=signals, resolved_url=resolved_url)
