"""PayTrace state machine — the valid transaction lifecycle graph.

This is event sourcing applied to payments: the state of a transaction is
never stored, it is always DERIVED by folding its TransactionEvent rows in
occurred_at order. There is no "current_stage" column anywhere. This means
a point-in-time query ("what did this look like at 12:30:06?") is trivial
-- just fold up to that timestamp instead of the present -- and the full
history (including every anomaly ever observed) is never lost to an
in-place update.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.contracts.events import TransactionEvent, TxnStage

# ---------------------------------------------------------------------------
# The valid transition graph
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[TxnStage, frozenset[TxnStage]] = {
    TxnStage.initiated: frozenset({TxnStage.gateway_accepted, TxnStage.gateway_failed}),
    TxnStage.gateway_accepted: frozenset({TxnStage.bank_accepted, TxnStage.bank_failed}),
    TxnStage.bank_accepted: frozenset({TxnStage.webhook_sent, TxnStage.webhook_failed, TxnStage.settled}),
    TxnStage.webhook_sent: frozenset({TxnStage.settled, TxnStage.settlement_failed}),
    # Settlement can succeed even if the webhook failed -- this is the
    # common case behind "money deducted but merchant says failed."
    TxnStage.webhook_failed: frozenset({TxnStage.settled, TxnStage.settlement_failed}),
    TxnStage.gateway_failed: frozenset({TxnStage.refunded}),
    TxnStage.bank_failed: frozenset({TxnStage.refunded}),
    TxnStage.settlement_failed: frozenset({TxnStage.refunded}),
    TxnStage.settled: frozenset({TxnStage.refunded}),
    TxnStage.refunded: frozenset(),
}

# Stages where the transaction's main lifecycle has concluded. All of the
# failure stages and `settled` are "terminal except for refund" per the
# spec -- refund is a separate follow-up action, not a continuation of the
# original payment flow, so these still count as terminal for monitoring
# purposes (a dashboard showing "in flight" transactions should not include
# them).
TERMINAL_STAGES: frozenset[TxnStage] = frozenset(
    {
        TxnStage.settled,
        TxnStage.gateway_failed,
        TxnStage.bank_failed,
        TxnStage.settlement_failed,
        TxnStage.refunded,
    }
)

# Expected max time (ms) before the NEXT stage should have arrived, keyed by
# the current (last-observed) stage. Absence from this dict means "no
# further stage is expected" (a terminal stage). Used by the classifier's
# STUCK rule and by analytics' SLA-aware reporting.
STAGE_SLA_MS: dict[TxnStage, int] = {
    TxnStage.initiated: 30_000,  # gateway should accept/reject within 30s
    TxnStage.gateway_accepted: 60_000,  # bank should respond within 60s
    TxnStage.bank_accepted: 120_000,  # webhook or settlement within 2 min
    TxnStage.webhook_sent: 300_000,  # settlement within 5 min
    TxnStage.webhook_failed: 300_000,  # settlement can still land within 5 min
}

# A gap between two consecutive events longer than this is flagged as a
# timing anomaly even when the transition itself is valid -- real payment
# lifecycle steps normally complete in seconds; a multi-minute gap between
# adjacent events is itself worth surfacing.
TIMING_GAP_THRESHOLD_MS = 300_000


def validate_transition(from_stage: TxnStage, to_stage: TxnStage) -> bool:
    return to_stage in VALID_TRANSITIONS.get(from_stage, frozenset())


# ---------------------------------------------------------------------------
# Derived state
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TimelineEntry:
    stage: TxnStage
    occurred_at: datetime
    amount: Decimal
    provider: str
    provider_ref: str | None
    error_code: str | None
    latency_ms: int | None
    idempotency_key: str


@dataclass(frozen=True)
class Anomaly:
    kind: str  # "invalid_transition" | "missing_stage" | "timing_gap"
    description: str
    from_stage: TxnStage | None = None
    to_stage: TxnStage | None = None
    occurred_at: datetime | None = None
    gap_ms: int | None = None


@dataclass(frozen=True)
class TransactionState:
    transaction_ref: str | None
    current_stage: TxnStage | None
    timeline: list[TimelineEntry] = field(default_factory=list)
    anomalies: list[Anomaly] = field(default_factory=list)
    # ms spent AT each stage before the next event arrived (or before
    # `up_to`/now for the last stage, if that stage is still non-terminal
    # -- see derive_state below).
    duration_by_stage: dict[TxnStage, int] = field(default_factory=dict)
    total_duration_ms: int | None = None
    is_terminal: bool = False


def _to_ms(delta_seconds: float) -> int:
    return int(round(delta_seconds * 1000))


def derive_state(events: list[TransactionEvent], up_to: datetime | None = None) -> TransactionState:
    """Fold events (in occurred_at order, NOT insertion order) into a
    TransactionState. Passing `up_to` derives the state as of that moment
    -- any event after it is simply not folded in yet, which is the entire
    point of never persisting state: a point-in-time query is just a fold
    with a smaller event list.
    """
    relevant = [e for e in events if up_to is None or e.occurred_at <= up_to]
    if not relevant:
        return TransactionState(transaction_ref=None, current_stage=None)

    ordered = sorted(relevant, key=lambda e: e.occurred_at)
    transaction_ref = ordered[0].transaction_ref

    timeline = [
        TimelineEntry(
            stage=e.stage,
            occurred_at=e.occurred_at,
            amount=e.amount,
            provider=e.provider,
            provider_ref=e.provider_ref,
            error_code=e.error_code,
            latency_ms=e.latency_ms,
            idempotency_key=e.idempotency_key,
        )
        for e in ordered
    ]

    anomalies: list[Anomaly] = []

    if timeline[0].stage != TxnStage.initiated:
        anomalies.append(
            Anomaly(
                kind="missing_stage",
                description=(
                    f"Timeline for {transaction_ref} begins at '{timeline[0].stage.value}', "
                    "not 'initiated' -- earlier events may be missing."
                ),
                to_stage=timeline[0].stage,
                occurred_at=timeline[0].occurred_at,
            )
        )

    for prev, curr in zip(timeline, timeline[1:]):
        if not validate_transition(prev.stage, curr.stage):
            anomalies.append(
                Anomaly(
                    kind="invalid_transition",
                    description=(
                        f"'{prev.stage.value}' -> '{curr.stage.value}' is not a valid transition."
                    ),
                    from_stage=prev.stage,
                    to_stage=curr.stage,
                    occurred_at=curr.occurred_at,
                )
            )

        gap_ms = _to_ms((curr.occurred_at - prev.occurred_at).total_seconds())
        if gap_ms > TIMING_GAP_THRESHOLD_MS:
            anomalies.append(
                Anomaly(
                    kind="timing_gap",
                    description=(
                        f"{gap_ms}ms elapsed between '{prev.stage.value}' and '{curr.stage.value}', "
                        f"exceeding the {TIMING_GAP_THRESHOLD_MS}ms expected gap."
                    ),
                    from_stage=prev.stage,
                    to_stage=curr.stage,
                    occurred_at=curr.occurred_at,
                    gap_ms=gap_ms,
                )
            )

    duration_by_stage: dict[TxnStage, int] = {}
    for prev, curr in zip(timeline, timeline[1:]):
        duration_by_stage[prev.stage] = _to_ms((curr.occurred_at - prev.occurred_at).total_seconds())

    current_stage = timeline[-1].stage
    total_duration_ms = _to_ms((timeline[-1].occurred_at - timeline[0].occurred_at).total_seconds())

    return TransactionState(
        transaction_ref=transaction_ref,
        current_stage=current_stage,
        timeline=timeline,
        anomalies=anomalies,
        duration_by_stage=duration_by_stage,
        total_duration_ms=total_duration_ms,
        is_terminal=current_stage in TERMINAL_STAGES,
    )
