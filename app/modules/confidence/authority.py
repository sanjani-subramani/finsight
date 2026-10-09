"""Source authority ranking — how much we trust a data source by default."""

from __future__ import annotations

from app.contracts.events import DataSource

SOURCE_AUTHORITY: dict[DataSource, float] = {
    DataSource.bank_csv: 0.95,  # bank's own record, highest external authority
    DataSource.sms: 0.90,  # bank-generated but can be truncated/delayed
    DataSource.manual: 1.00,  # user asserting their own finances
    DataSource.receipt_ocr: 0.75,  # OCR errors are common
    DataSource.simulated: 0.50,  # demo data, never authoritative
    DataSource.system: 0.85,  # derived by FinSentinel
}

# Manual entry is normally the MOST authoritative source — the user knows
# their own finances better than any automated read. But when a bank
# record DIRECTLY contradicts a manual entry, the bank wins: banks don't
# typo amounts on their own settled ledger, but users routinely
# misremember, fat-finger, or round numbers when entering things by hand.
# This penalty applies ONLY to manual entries, and ONLY when the specific
# contradicting source is a bank record — every other source keeps its
# normal authority even when contradicted.
CONTRADICTION_PENALTY: dict[DataSource, float] = {
    DataSource.manual: 0.70,
}


def resolve_authority(source: DataSource, is_contradicted_by_bank: bool) -> float:
    if is_contradicted_by_bank and source in CONTRADICTION_PENALTY:
        return CONTRADICTION_PENALTY[source]
    return SOURCE_AUTHORITY[source]
