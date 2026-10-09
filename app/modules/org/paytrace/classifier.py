"""Deterministic failure-mode classification for a reconstructed transaction.

No AI, no ML -- every rule below is a fixed, explainable check over the
TransactionState's timeline and anomalies. This matters for a payments
dashboard: an ops engineer or auditor needs to trust *why* a transaction
was labelled a certain way, and be able to point at the exact evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

from app.contracts.events import TxnStage
from app.modules.org.paytrace.state_machine import STAGE_SLA_MS, TimelineEntry, TransactionState

# Below this, a gateway_failed is just an ordinary rejection; above it, the
# gateway effectively timed out before it could respond.
GATEWAY_TIMEOUT_LATENCY_MS = 10_000

# "amounts matching within 1%" per the duplicate-attempt spec.
DUPLICATE_AMOUNT_TOLERANCE = Decimal("0.01")
DUPLICATE_WINDOW_SECONDS = 60

# A settlement is "delayed" once it takes more than this multiple of the
# provider's own historical p95 settlement latency.
SETTLEMENT_DELAY_MULTIPLE = 2.0


class FailureMode(str, Enum):
    SUCCESSFUL = "successful"
    GATEWAY_TIMEOUT = "gateway_timeout"
    BANK_DECLINED = "bank_declined"
    WEBHOOK_LOST = "webhook_lost"
    SETTLEMENT_DELAYED = "settlement_delayed"
    DUPLICATE_ATTEMPT = "duplicate_attempt"
    PARTIAL_FAILURE = "partial_failure"
    STUCK = "stuck"
    REVERSED = "reversed"
    # Catch-alls so classify() is total: a terminal failure that doesn't
    # match any of the specific rules above, or a transaction that is
    # simply mid-flight and hasn't breached any SLA yet.
    OTHER_FAILURE = "other_failure"
    IN_PROGRESS = "in_progress"


_RECOMMENDED_ACTIONS: dict[FailureMode, str | None] = {
    FailureMode.SUCCESSFUL: None,
    FailureMode.GATEWAY_TIMEOUT: "Retry with the same or an alternate gateway",
    FailureMode.BANK_DECLINED: "Notify the customer of the decline reason; do not auto-retry",
    FailureMode.WEBHOOK_LOST: "Re-send notification to merchant",
    FailureMode.SETTLEMENT_DELAYED: "Monitor — settlement is in progress",
    FailureMode.DUPLICATE_ATTEMPT: "Refund the duplicate",
    FailureMode.PARTIAL_FAILURE: "Escalate to reconciliation for manual review",
    FailureMode.STUCK: "Query gateway for status update",
    FailureMode.REVERSED: None,
    FailureMode.OTHER_FAILURE: "Investigate manually",
    FailureMode.IN_PROGRESS: None,
}


@dataclass(frozen=True)
class FailureClassification:
    mode: FailureMode
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)
    recommended_action: str | None = None
    human_summary: str = ""


def _find(timeline: list[TimelineEntry], stage: TxnStage) -> TimelineEntry | None:
    return next((e for e in timeline if e.stage == stage), None)


def _contains(timeline: list[TimelineEntry], stage: TxnStage) -> bool:
    return _find(timeline, stage) is not None


class FailureClassifier:
    """Classifies a TransactionState. `provider_p95_settlement_ms` is an
    optional per-provider historical baseline (computed by analytics.py
    across many transactions) used only by the SETTLEMENT_DELAYED rule --
    without it, that rule is simply skipped rather than guessed at.
    """

    def __init__(self, provider_p95_settlement_ms: dict[str, float] | None = None) -> None:
        self._provider_p95_settlement_ms = provider_p95_settlement_ms or {}

    def classify(self, state: TransactionState) -> FailureClassification:
        ref = state.transaction_ref or "this transaction"

        if not state.timeline:
            return FailureClassification(
                mode=FailureMode.IN_PROGRESS,
                confidence=0.0,
                evidence={},
                recommended_action=None,
                human_summary=f"No events recorded yet for {ref}.",
            )

        duplicate = self._check_duplicate_attempt(state, ref)
        if duplicate is not None:
            return duplicate

        if state.current_stage == TxnStage.refunded and _contains(state.timeline, TxnStage.settled):
            settled_entry = _find(state.timeline, TxnStage.settled)
            assert settled_entry is not None
            return FailureClassification(
                mode=FailureMode.REVERSED,
                confidence=0.95,
                evidence={"settled_amount": str(settled_entry.amount)},
                recommended_action=_RECOMMENDED_ACTIONS[FailureMode.REVERSED],
                human_summary=f"{ref} settled for {settled_entry.amount} and was subsequently refunded.",
            )

        if state.current_stage == TxnStage.bank_failed:
            return self._classify_bank_declined(state, ref)

        if state.current_stage == TxnStage.gateway_failed:
            return self._classify_gateway_failed(state, ref)

        if state.current_stage == TxnStage.settled:
            partial = self._check_partial_failure(state, ref)
            if partial is not None:
                return partial

            webhook_lost = self._check_webhook_lost(state, ref)
            if webhook_lost is not None:
                return webhook_lost

            delayed = self._check_settlement_delayed(state, ref)
            if delayed is not None:
                return delayed

            if not state.anomalies:
                return FailureClassification(
                    mode=FailureMode.SUCCESSFUL,
                    confidence=1.0,
                    evidence={"total_duration_ms": state.total_duration_ms},
                    recommended_action=None,
                    human_summary=f"{ref} completed successfully with no anomalies.",
                )

        stuck = self._check_stuck(state, ref)
        if stuck is not None:
            return stuck

        if state.is_terminal:
            return FailureClassification(
                mode=FailureMode.OTHER_FAILURE,
                confidence=0.5,
                evidence={"current_stage": state.current_stage.value if state.current_stage else None},
                recommended_action=_RECOMMENDED_ACTIONS[FailureMode.OTHER_FAILURE],
                human_summary=f"{ref} ended at '{state.current_stage.value if state.current_stage else 'unknown'}' "
                "without matching a more specific failure pattern.",
            )

        return FailureClassification(
            mode=FailureMode.IN_PROGRESS,
            confidence=1.0,
            evidence={"current_stage": state.current_stage.value if state.current_stage else None},
            recommended_action=None,
            human_summary=f"{ref} is progressing normally; currently at "
            f"'{state.current_stage.value if state.current_stage else 'unknown'}'.",
        )

    # -- individual rules ---------------------------------------------------

    def _classify_bank_declined(self, state: TransactionState, ref: str) -> FailureClassification:
        entry = state.timeline[-1]
        return FailureClassification(
            mode=FailureMode.BANK_DECLINED,
            confidence=0.95 if entry.error_code else 0.6,
            evidence={"error_code": entry.error_code, "provider": entry.provider},
            recommended_action=_RECOMMENDED_ACTIONS[FailureMode.BANK_DECLINED],
            human_summary=(
                f"{ref} was declined by the bank with error code '{entry.error_code}'."
                if entry.error_code
                else f"{ref} was declined by the bank with no error code reported."
            ),
        )

    def _classify_gateway_failed(self, state: TransactionState, ref: str) -> FailureClassification:
        entry = state.timeline[-1]
        latency_ms = entry.latency_ms
        if latency_ms is None:
            latency_ms = state.duration_by_stage.get(TxnStage.initiated)

        if latency_ms is not None and latency_ms > GATEWAY_TIMEOUT_LATENCY_MS:
            return FailureClassification(
                mode=FailureMode.GATEWAY_TIMEOUT,
                confidence=0.9,
                evidence={"latency_ms": latency_ms, "threshold_ms": GATEWAY_TIMEOUT_LATENCY_MS},
                recommended_action=_RECOMMENDED_ACTIONS[FailureMode.GATEWAY_TIMEOUT],
                human_summary=f"{ref} timed out at the gateway after {latency_ms}ms "
                f"(threshold {GATEWAY_TIMEOUT_LATENCY_MS}ms).",
            )

        return FailureClassification(
            mode=FailureMode.OTHER_FAILURE,
            confidence=0.6,
            evidence={"error_code": entry.error_code, "latency_ms": latency_ms},
            recommended_action=_RECOMMENDED_ACTIONS[FailureMode.OTHER_FAILURE],
            human_summary=f"{ref} was rejected by the gateway (error code '{entry.error_code}').",
        )

    def _check_partial_failure(self, state: TransactionState, ref: str) -> FailureClassification | None:
        initiated = _find(state.timeline, TxnStage.initiated)
        settled = _find(state.timeline, TxnStage.settled)
        if initiated is None or settled is None or initiated.amount == settled.amount:
            return None
        return FailureClassification(
            mode=FailureMode.PARTIAL_FAILURE,
            confidence=0.9,
            evidence={
                "initiated_amount": str(initiated.amount),
                "settled_amount": str(settled.amount),
            },
            recommended_action=_RECOMMENDED_ACTIONS[FailureMode.PARTIAL_FAILURE],
            human_summary=(
                f"{ref} initiated for {initiated.amount} but settled for {settled.amount} -- "
                "the settled amount does not match the original request."
            ),
        )

    def _check_webhook_lost(self, state: TransactionState, ref: str) -> FailureClassification | None:
        webhook_failed = _find(state.timeline, TxnStage.webhook_failed)
        bank_accepted = _find(state.timeline, TxnStage.bank_accepted)
        if webhook_failed is None or bank_accepted is None:
            return None
        return FailureClassification(
            mode=FailureMode.WEBHOOK_LOST,
            confidence=0.95,
            evidence={
                "bank_accepted_at": bank_accepted.occurred_at.isoformat(),
                "webhook_failed_at": webhook_failed.occurred_at.isoformat(),
            },
            recommended_action=_RECOMMENDED_ACTIONS[FailureMode.WEBHOOK_LOST],
            human_summary=(
                f"{ref} was accepted by the bank and settled, but the merchant webhook failed -- "
                "the merchant's system likely still believes this payment failed."
            ),
        )

    def _check_settlement_delayed(self, state: TransactionState, ref: str) -> FailureClassification | None:
        settled = _find(state.timeline, TxnStage.settled)
        if settled is None:
            return None
        baseline_p95 = self._provider_p95_settlement_ms.get(settled.provider)
        if not baseline_p95 or baseline_p95 <= 0:
            return None

        start = _find(state.timeline, TxnStage.webhook_sent) or _find(state.timeline, TxnStage.webhook_failed)
        start = start or _find(state.timeline, TxnStage.bank_accepted)
        if start is None:
            return None

        settlement_latency_ms = state.duration_by_stage.get(start.stage)
        if settlement_latency_ms is None:
            return None

        threshold = baseline_p95 * SETTLEMENT_DELAY_MULTIPLE
        if settlement_latency_ms <= threshold:
            return None

        return FailureClassification(
            mode=FailureMode.SETTLEMENT_DELAYED,
            confidence=0.8,
            evidence={
                "settlement_latency_ms": settlement_latency_ms,
                "provider_p95_ms": baseline_p95,
                "threshold_ms": threshold,
            },
            recommended_action=_RECOMMENDED_ACTIONS[FailureMode.SETTLEMENT_DELAYED],
            human_summary=(
                f"{ref} settled in {settlement_latency_ms}ms, more than "
                f"{SETTLEMENT_DELAY_MULTIPLE}x {settled.provider}'s normal p95 ({baseline_p95}ms)."
            ),
        )

    def _check_duplicate_attempt(self, state: TransactionState, ref: str) -> FailureClassification | None:
        initiations = [e for e in state.timeline if e.stage == TxnStage.initiated]
        for i, first in enumerate(initiations):
            for second in initiations[i + 1 :]:
                if first.idempotency_key == second.idempotency_key:
                    continue
                gap_seconds = abs((second.occurred_at - first.occurred_at).total_seconds())
                if gap_seconds > DUPLICATE_WINDOW_SECONDS:
                    continue
                if first.amount == 0:
                    continue
                amount_diff_ratio = abs(second.amount - first.amount) / first.amount
                if amount_diff_ratio > DUPLICATE_AMOUNT_TOLERANCE:
                    continue
                return FailureClassification(
                    mode=FailureMode.DUPLICATE_ATTEMPT,
                    confidence=0.9,
                    evidence={
                        "first_idempotency_key": first.idempotency_key,
                        "second_idempotency_key": second.idempotency_key,
                        "gap_seconds": gap_seconds,
                        "first_amount": str(first.amount),
                        "second_amount": str(second.amount),
                    },
                    recommended_action=_RECOMMENDED_ACTIONS[FailureMode.DUPLICATE_ATTEMPT],
                    human_summary=(
                        f"{ref} has two initiation attempts {gap_seconds:.0f}s apart with matching "
                        "amounts but different idempotency keys -- likely a duplicate submission."
                    ),
                )
        return None

    def _check_stuck(self, state: TransactionState, ref: str) -> FailureClassification | None:
        if state.is_terminal:
            return None
        current_stage = state.current_stage
        if current_stage is None:
            return None
        sla_ms = STAGE_SLA_MS.get(current_stage)
        if sla_ms is None:
            return None

        last_event = state.timeline[-1]
        elapsed_ms = int(round((datetime.now(timezone.utc) - last_event.occurred_at).total_seconds() * 1000))
        threshold = sla_ms * 2
        if elapsed_ms <= threshold:
            return None

        return FailureClassification(
            mode=FailureMode.STUCK,
            confidence=0.75,
            evidence={
                "current_stage": current_stage.value,
                "elapsed_ms": elapsed_ms,
                "sla_ms": sla_ms,
                "threshold_ms": threshold,
            },
            recommended_action=_RECOMMENDED_ACTIONS[FailureMode.STUCK],
            human_summary=(
                f"{ref} has been stuck at '{current_stage.value}' for {elapsed_ms}ms, "
                f"more than 2x the expected {sla_ms}ms SLA."
            ),
        )
