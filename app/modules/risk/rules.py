"""Declarative rules as DATA, not code.

Every rule is a pure function over a RuleContext, registered in
RULE_REGISTRY as data (name, category, severity, the function itself).
This is what keeps the runtime risk path fully deterministic and
re-derivable: no rule here ever calls an LLM or touches a clock beyond
what's already baked into the context it's given.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from app.contracts.events import FinancialStateSnapshot
from app.models.tables import FinancialEvent
from app.modules.simulation.engine import SimulationResult


@dataclass(frozen=True)
class RuleContext:
    snapshot: FinancialStateSnapshot
    simulation_result: SimulationResult | None
    recent_events: list[FinancialEvent]
    # Precomputed contextual data the rules need beyond what the frozen
    # snapshot itself carries (per-income-source timing baselines,
    # spending baselines, the historical expense distribution, ...).
    # Despite the name, this is a general "context bag," not literally
    # just averages — see RiskService for exactly what it populates and
    # why (mostly: some rules need per-income-source detail the
    # aggregated IncomeForecast contract doesn't carry).
    historical_averages: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuleFinding:
    rule_id: str
    triggered: bool
    severity: int
    evidence: dict[str, Any]
    human_statement: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    description: str
    category: str  # liquidity | timing | behaviour | goal
    evaluate: Callable[[RuleContext], RuleFinding | None]
    base_severity: int  # 1-5
    is_active: bool = True


def _obligations_due_within(snapshot: FinancialStateSnapshot, days: int) -> Decimal:
    horizon = date.today() + timedelta(days=days)
    return sum(
        (o.amount for o in snapshot.obligations if not o.is_paid and o.due_date <= horizon),
        Decimal("0"),
    )


# ---------------------------------------------------------------------------
# LIQUIDITY
# ---------------------------------------------------------------------------

# 1.5x is a common personal-finance rule of thumb for a minimum liquidity
# margin: enough to absorb a few days' income-timing slip without missing
# an obligation, without demanding the unrealistic "keep 3x on hand."
LOW_BUFFER_MULTIPLIER = Decimal("1.5")
LOW_BUFFER_SEVERITY = 3


def _evaluate_low_buffer(ctx: RuleContext) -> RuleFinding | None:
    obligations_30d = _obligations_due_within(ctx.snapshot, 30)
    threshold = obligations_30d * LOW_BUFFER_MULTIPLIER
    cash = ctx.snapshot.cash_available
    if cash >= threshold:
        return None
    evidence = {
        "cash_available": str(cash),
        "obligations_due_30d": str(obligations_30d),
        "threshold": str(threshold),
        "multiplier": str(LOW_BUFFER_MULTIPLIER),
        # The statement's "30 days" is a literal constant, not derived
        # from any other evidence value — it must be its own entry so
        # app.modules.decision.trace's completeness check can find it.
        "window_days": "30",
    }
    statement = (
        f"Your available cash (Rs.{cash:,.2f}) is below 1.5x your obligations due in the "
        f"next 30 days (Rs.{obligations_30d:,.2f})."
    )
    return RuleFinding(
        rule_id="low_buffer", triggered=True, severity=LOW_BUFFER_SEVERITY, evidence=evidence, human_statement=statement
    )


# Below what's due in just the next TWO WEEKS is not "a margin problem,"
# it's already a coverage gap — hence a higher severity than low_buffer.
CRITICAL_BUFFER_SEVERITY = 5


def _evaluate_critical_buffer(ctx: RuleContext) -> RuleFinding | None:
    obligations_14d = _obligations_due_within(ctx.snapshot, 14)
    cash = ctx.snapshot.cash_available
    if cash >= obligations_14d:
        return None
    evidence = {
        "cash_available": str(cash),
        "obligations_due_14d": str(obligations_14d),
        # See low_buffer's identical comment: the "14 days" in the
        # statement is a literal constant, not derivable from another
        # evidence value, so it needs its own entry.
        "window_days": "14",
    }
    statement = (
        f"Your available cash (Rs.{cash:,.2f}) is already less than what's due in the "
        f"next 14 days (Rs.{obligations_14d:,.2f})."
    )
    return RuleFinding(
        rule_id="critical_buffer",
        triggered=True,
        severity=CRITICAL_BUFFER_SEVERITY,
        evidence=evidence,
        human_statement=statement,
    )


EMERGENCY_FUND_DEPLETED_SEVERITY = 3


def _evaluate_emergency_fund_depleted(ctx: RuleContext) -> RuleFinding | None:
    # total_fixed_obligations sums currently-unpaid FIXED obligations on
    # record — a reasonable proxy for "one month's fixed costs" since
    # obligations are populated on roughly a monthly cadence (rent, EMI,
    # subscriptions).
    monthly_fixed = ctx.snapshot.total_fixed_obligations
    fund = ctx.snapshot.emergency_fund
    if monthly_fixed <= 0 or fund >= monthly_fixed:
        return None
    evidence = {"emergency_fund": str(fund), "monthly_fixed_obligations": str(monthly_fixed)}
    statement = (
        f"Your emergency fund (Rs.{fund:,.2f}) covers less than one month of fixed "
        f"obligations (Rs.{monthly_fixed:,.2f})."
    )
    return RuleFinding(
        rule_id="emergency_fund_depleted",
        triggered=True,
        severity=EMERGENCY_FUND_DEPLETED_SEVERITY,
        evidence=evidence,
        human_statement=statement,
    )


NEGATIVE_PROJECTION_SEVERITY = 4


def _evaluate_negative_projection(ctx: RuleContext) -> RuleFinding | None:
    if ctx.simulation_result is None or ctx.simulation_result.min_balance_p50 >= 0:
        return None
    balance = ctx.simulation_result.min_balance_p50
    evidence = {"min_balance_p50": str(balance)}
    statement = (
        f"In the median simulated scenario, your balance is projected to go negative "
        f"(Rs.{balance:,.2f})."
    )
    return RuleFinding(
        rule_id="negative_projection",
        triggered=True,
        severity=NEGATIVE_PROJECTION_SEVERITY,
        evidence=evidence,
        human_statement=statement,
    )


# ---------------------------------------------------------------------------
# TIMING
# ---------------------------------------------------------------------------

INCOME_DELAYED_SEVERITY = 3


def _evaluate_income_delayed(ctx: RuleContext) -> RuleFinding | None:
    # RiskService precomputes, per income source, the CURRENTLY expected
    # arrival (which reflects any real INCOME_DELAYED event folded into
    # the Twin) against the STATISTICAL baseline arrival
    # (last_received + declared_frequency_days + observed_delay_mean) —
    # both as ISO date strings, which sort identically to their
    # chronological order.
    sources = ctx.historical_averages.get("income_sources") or []
    for src in sources:
        expected_arrival = src.get("expected_arrival")
        baseline_arrival = src.get("baseline_arrival")
        if expected_arrival is None or baseline_arrival is None:
            continue
        if expected_arrival <= baseline_arrival:
            continue
        days_late = (date.fromisoformat(expected_arrival) - date.fromisoformat(baseline_arrival)).days
        evidence = {
            "income_source": src.get("label"),
            "expected_arrival": expected_arrival,
            "baseline_arrival": baseline_arrival,
            "days_late": days_late,
        }
        statement = (
            f"{src.get('label')} is now expected on {expected_arrival}, {days_late} day(s) "
            f"later than its usual pattern ({baseline_arrival})."
        )
        return RuleFinding(
            rule_id="income_delayed",
            triggered=True,
            severity=INCOME_DELAYED_SEVERITY,
            evidence=evidence,
            human_statement=statement,
        )
    return None


# A 10-day window is roughly a third of a typical monthly pay cycle — two
# or more fixed bills landing this close together materially concentrates
# cash-out risk even if each is individually affordable on its own.
OBLIGATION_CLUSTER_WINDOW_DAYS = 10
OBLIGATION_CLUSTER_MIN_COUNT = 2
OBLIGATION_CLUSTER_SEVERITY = 3


def _evaluate_obligation_cluster(ctx: RuleContext) -> RuleFinding | None:
    fixed = sorted(
        (o for o in ctx.snapshot.obligations if o.is_fixed and not o.is_paid), key=lambda o: o.due_date
    )
    for i, anchor in enumerate(fixed):
        window_end = anchor.due_date + timedelta(days=OBLIGATION_CLUSTER_WINDOW_DAYS)
        cluster = [o for o in fixed[i:] if o.due_date <= window_end]
        if len(cluster) < OBLIGATION_CLUSTER_MIN_COUNT:
            continue
        total = sum((o.amount for o in cluster), Decimal("0"))
        evidence = {
            "obligations": [
                {"label": o.label, "amount": str(o.amount), "due_date": o.due_date.isoformat()} for o in cluster
            ],
            # The human_statement below leads with this count ("N fixed
            # obligations...") -- it must be recorded here too, or
            # validate_trace_completeness (app.modules.decision.trace)
            # rejects the intervention for asserting an untraceable "2".
            "obligation_count": len(cluster),
            "window_days": OBLIGATION_CLUSTER_WINDOW_DAYS,
            "total_amount": str(total),
        }
        labels = ", ".join(f"{o.label} (Rs.{o.amount:,.2f}) on {o.due_date.isoformat()}" for o in cluster)
        statement = (
            f"{len(cluster)} fixed obligations totalling Rs.{total:,.2f} are due within "
            f"{OBLIGATION_CLUSTER_WINDOW_DAYS} days of each other: {labels}."
        )
        return RuleFinding(
            rule_id="obligation_cluster",
            triggered=True,
            severity=OBLIGATION_CLUSTER_SEVERITY,
            evidence=evidence,
            human_statement=statement,
        )
    return None


INCOME_AFTER_OBLIGATION_SEVERITY = 4


def _evaluate_income_after_obligation(ctx: RuleContext) -> RuleFinding | None:
    forecast = ctx.snapshot.income_forecast
    if forecast.expected_arrival is None:
        return None
    unpaid = sorted((o for o in ctx.snapshot.obligations if not o.is_paid), key=lambda o: o.due_date)
    if not unpaid:
        return None
    next_obligation = unpaid[0]
    if forecast.expected_arrival <= next_obligation.due_date:
        return None
    # THE CLASSIC FREELANCER TRAP: obligations run on a fixed calendar
    # (rent is due the 1st no matter what), but income does not — a
    # client "paying on schedule" by their own standards can still
    # routinely land AFTER the bill it was meant to cover. This is
    # exactly the gap ingestion-derived timing evidence (arrival date +
    # delay stats) exists to catch before it becomes a missed payment.
    gap_days = (forecast.expected_arrival - next_obligation.due_date).days
    evidence = {
        "next_obligation": next_obligation.label,
        "obligation_due_date": next_obligation.due_date.isoformat(),
        "obligation_amount": str(next_obligation.amount),
        "expected_income_arrival": forecast.expected_arrival.isoformat(),
        "gap_days": gap_days,
    }
    statement = (
        f"Your next expected income arrives on {forecast.expected_arrival.isoformat()}, "
        f"{gap_days} day(s) AFTER {next_obligation.label} (Rs.{next_obligation.amount:,.2f}) "
        f"is due on {next_obligation.due_date.isoformat()}."
    )
    return RuleFinding(
        rule_id="income_after_obligation",
        triggered=True,
        severity=INCOME_AFTER_OBLIGATION_SEVERITY,
        evidence=evidence,
        human_statement=statement,
    )


# ---------------------------------------------------------------------------
# BEHAVIOUR
# ---------------------------------------------------------------------------

# A 40%+ jump over the 60-day baseline is well outside typical
# week-to-week noise (which usually stays within ~20-25% for most
# spending patterns), making it a genuinely actionable early-warning
# signal rather than routine variation.
HIGH_BURN_THRESHOLD_PCT = 0.40
HIGH_BURN_SEVERITY = 2


def _evaluate_high_burn(ctx: RuleContext) -> RuleFinding | None:
    recent_7d_total = ctx.historical_averages.get("discretionary_7d_total")
    baseline_daily_mean = ctx.historical_averages.get("discretionary_60d_daily_mean")
    if recent_7d_total is None or not baseline_daily_mean:
        return None
    recent_daily_mean = recent_7d_total / 7
    pct_above = (recent_daily_mean - baseline_daily_mean) / baseline_daily_mean
    if pct_above < HIGH_BURN_THRESHOLD_PCT:
        return None
    # Rounded to 2dp HERE (not just at display time below): dividing by 7
    # produces arbitrary float precision (e.g. 9785.714285714286), but the
    # statement only ever shows 2 decimal places -- storing the unrounded
    # value would make the evidence and the displayed figure two DIFFERENT
    # decimals, which validate_trace_completeness then rejects.
    recent_daily_mean_r = round(recent_daily_mean, 2)
    baseline_daily_mean_r = round(baseline_daily_mean, 2)
    evidence = {
        "recent_7d_daily_mean": recent_daily_mean_r,
        "baseline_60d_daily_mean": baseline_daily_mean_r,
        "pct_above_baseline": pct_above,
        # The statement below also embeds "7" and "60" as literal
        # window-day constants, and shows pct_above as a WHOLE PERCENT
        # (":.0%") -- neither the bare day counts nor that rounded
        # whole-percent form exist elsewhere in this dict
        # (pct_above_baseline above is the raw 0-1 fraction), so they'd be
        # rejected the same way. Same convention as _pct() in
        # app.modules.decision.service: record the number AS DISPLAYED.
        "recent_window_days": 7,
        "baseline_window_days": 60,
        "pct_above_baseline_pct": round(pct_above * 100),
    }
    statement = (
        f"Discretionary spending over the last 7 days (Rs.{recent_daily_mean_r:,.2f}/day) is "
        f"{pct_above:.0%} above your 60-day average (Rs.{baseline_daily_mean_r:,.2f}/day)."
    )
    return RuleFinding(
        rule_id="high_burn", triggered=True, severity=HIGH_BURN_SEVERITY, evidence=evidence, human_statement=statement
    )


# 3x the user's OWN historical p95 is an outlier of an outlier — p95
# alone would flag routine "big" purchases (a laptop, a flight);
# requiring 3x that targets genuinely exceptional single transactions.
UNUSUAL_EXPENSE_MULTIPLIER = 3.0
UNUSUAL_EXPENSE_SEVERITY = 2


def _evaluate_unusual_large_expense(ctx: RuleContext) -> RuleFinding | None:
    p95 = ctx.historical_averages.get("expense_p95")
    if not p95:
        return None
    threshold = p95 * UNUSUAL_EXPENSE_MULTIPLIER
    for event in ctx.recent_events:
        if event.event_type != "expense" or event.amount is None:
            continue
        amount = float(event.amount)
        if amount <= threshold:
            continue
        # Rounded to 2dp HERE, not just at display time below: p95/threshold
        # come from a numpy percentile and carry arbitrary float precision
        # (e.g. 9785.714285714286), but the statement below only ever shows
        # 2 decimal places. Recording the unrounded value would make the
        # evidence and the displayed figure two DIFFERENT decimals, which
        # validate_trace_completeness (app.modules.decision.trace) then
        # rejects as an unsupported number the moment this finding's own
        # human_statement is the one that reaches an intervention body.
        amount_r = round(amount, 2)
        p95_r = round(p95, 2)
        threshold_r = round(threshold, 2)
        evidence = {
            "event_id": str(event.id),
            "amount": amount_r,
            "historical_p95": p95_r,
            "threshold": threshold_r,
            "counterparty": event.counterparty,
            # The statement's "3x" is UNUSUAL_EXPENSE_MULTIPLIER, a
            # literal constant not derivable from the other evidence
            # values — see low_buffer's identical comment.
            "multiplier": UNUSUAL_EXPENSE_MULTIPLIER,
        }
        statement = (
            f"A Rs.{amount_r:,.2f} expense to {event.counterparty or 'an unknown merchant'} is "
            f"over 3x your typical large-expense level (Rs.{p95_r:,.2f})."
        )
        return RuleFinding(
            rule_id="unusual_large_expense",
            triggered=True,
            severity=UNUSUAL_EXPENSE_SEVERITY,
            evidence=evidence,
            human_statement=statement,
        )
    return None


# ---------------------------------------------------------------------------
# GOAL
# ---------------------------------------------------------------------------

GOAL_AT_RISK_WINDOW_DAYS = 30
# 80% completion with less than a month left means the remaining 20%+
# has to happen in a compressed window — worth flagging before it
# becomes mathematically impossible, not after.
GOAL_AT_RISK_COMPLETION_PCT = Decimal("0.80")
GOAL_AT_RISK_SEVERITY = 2


def _evaluate_goal_at_risk(ctx: RuleContext) -> RuleFinding | None:
    today = date.today()
    window_end = today + timedelta(days=GOAL_AT_RISK_WINDOW_DAYS)
    for goal in ctx.snapshot.goals:
        if goal.target_date is None or not (today <= goal.target_date <= window_end):
            continue
        if goal.target_amount <= 0:
            continue
        completion = goal.saved_amount / goal.target_amount
        if completion >= GOAL_AT_RISK_COMPLETION_PCT:
            continue
        days_remaining = (goal.target_date - today).days
        evidence = {
            "goal": goal.label,
            "target_amount": str(goal.target_amount),
            "saved_amount": str(goal.saved_amount),
            "completion_pct": float(completion),
            "target_date": goal.target_date.isoformat(),
            "days_remaining": days_remaining,
        }
        statement = (
            f"Goal '{goal.label}' is {float(completion):.0%} funded "
            f"(Rs.{goal.saved_amount:,.2f} of Rs.{goal.target_amount:,.2f}) with only "
            f"{days_remaining} day(s) left."
        )
        return RuleFinding(
            rule_id="goal_at_risk",
            triggered=True,
            severity=GOAL_AT_RISK_SEVERITY,
            evidence=evidence,
            human_statement=statement,
        )
    return None


GOAL_CONFLICTS_OBLIGATION_SEVERITY = 3


def _evaluate_goal_conflicts_obligation(ctx: RuleContext) -> RuleFinding | None:
    today = date.today()
    total_contribution = Decimal("0")
    for goal in ctx.snapshot.goals:
        if goal.target_date is not None and goal.target_date < today:
            continue
        remaining = max(Decimal("0"), goal.target_amount - goal.saved_amount)
        if remaining <= 0:
            continue
        months_left = 1
        if goal.target_date is not None:
            months_left = max(1, (goal.target_date - today).days // 30)
        total_contribution += remaining / months_left

    if total_contribution <= 0:
        return None

    obligations_30d = _obligations_due_within(ctx.snapshot, 30)
    projected_cash = ctx.snapshot.cash_available - total_contribution
    if projected_cash >= obligations_30d:
        return None

    evidence = {
        "projected_goal_contributions": str(total_contribution),
        "cash_available": str(ctx.snapshot.cash_available),
        "projected_cash_after_contributions": str(projected_cash),
        "obligations_due_30d": str(obligations_30d),
    }
    statement = (
        f"Contributing Rs.{total_contribution:,.2f} to your goals this month would leave "
        f"Rs.{projected_cash:,.2f} — below the Rs.{obligations_30d:,.2f} due in obligations."
    )
    return RuleFinding(
        rule_id="goal_conflicts_obligation",
        triggered=True,
        severity=GOAL_CONFLICTS_OBLIGATION_SEVERITY,
        evidence=evidence,
        human_statement=statement,
    )


RULE_REGISTRY: dict[str, Rule] = {
    "low_buffer": Rule(
        rule_id="low_buffer",
        name="Low Cash Buffer",
        description="Available cash is below 1.5x obligations due in the next 30 days.",
        category="liquidity",
        evaluate=_evaluate_low_buffer,
        base_severity=LOW_BUFFER_SEVERITY,
    ),
    "critical_buffer": Rule(
        rule_id="critical_buffer",
        name="Critical Cash Buffer",
        description="Available cash is below obligations due in the next 14 days.",
        category="liquidity",
        evaluate=_evaluate_critical_buffer,
        base_severity=CRITICAL_BUFFER_SEVERITY,
    ),
    "emergency_fund_depleted": Rule(
        rule_id="emergency_fund_depleted",
        name="Emergency Fund Depleted",
        description="Emergency fund covers less than one month of fixed obligations.",
        category="liquidity",
        evaluate=_evaluate_emergency_fund_depleted,
        base_severity=EMERGENCY_FUND_DEPLETED_SEVERITY,
    ),
    "negative_projection": Rule(
        rule_id="negative_projection",
        name="Negative Median Projection",
        description="The median simulated scenario shows a negative balance.",
        category="liquidity",
        evaluate=_evaluate_negative_projection,
        base_severity=NEGATIVE_PROJECTION_SEVERITY,
    ),
    "income_delayed": Rule(
        rule_id="income_delayed",
        name="Income Delayed",
        description="An income source's expected arrival is later than its historical pattern.",
        category="timing",
        evaluate=_evaluate_income_delayed,
        base_severity=INCOME_DELAYED_SEVERITY,
    ),
    "obligation_cluster": Rule(
        rule_id="obligation_cluster",
        name="Obligation Cluster",
        description="2+ fixed obligations are due within a 10-day window.",
        category="timing",
        evaluate=_evaluate_obligation_cluster,
        base_severity=OBLIGATION_CLUSTER_SEVERITY,
    ),
    "income_after_obligation": Rule(
        rule_id="income_after_obligation",
        name="Income After Obligation",
        description="The next expected income arrives after the next major obligation is due.",
        category="timing",
        evaluate=_evaluate_income_after_obligation,
        base_severity=INCOME_AFTER_OBLIGATION_SEVERITY,
    ),
    "high_burn": Rule(
        rule_id="high_burn",
        name="High Burn Rate",
        description="Discretionary spending over the last 7 days is 40%+ above the 60-day average.",
        category="behaviour",
        evaluate=_evaluate_high_burn,
        base_severity=HIGH_BURN_SEVERITY,
    ),
    "unusual_large_expense": Rule(
        rule_id="unusual_large_expense",
        name="Unusual Large Expense",
        description="A single expense exceeds 3x the user's historical p95 expense.",
        category="behaviour",
        evaluate=_evaluate_unusual_large_expense,
        base_severity=UNUSUAL_EXPENSE_SEVERITY,
    ),
    "goal_at_risk": Rule(
        rule_id="goal_at_risk",
        name="Goal At Risk",
        description="A goal's target date is within 30 days and it is under 80% funded.",
        category="goal",
        evaluate=_evaluate_goal_at_risk,
        base_severity=GOAL_AT_RISK_SEVERITY,
    ),
    "goal_conflicts_obligation": Rule(
        rule_id="goal_conflicts_obligation",
        name="Goal Conflicts With Obligations",
        description="This month's goal contributions would push projected cash below obligations.",
        category="goal",
        evaluate=_evaluate_goal_conflicts_obligation,
        base_severity=GOAL_CONFLICTS_OBLIGATION_SEVERITY,
    ),
}


def evaluate_all_rules(ctx: RuleContext, registry: dict[str, Rule] | None = None) -> list[RuleFinding]:
    registry = RULE_REGISTRY if registry is None else registry
    findings = []
    for rule in registry.values():
        if not rule.is_active:
            continue
        finding = rule.evaluate(ctx)
        if finding is not None and finding.triggered:
            findings.append(finding)
    return findings
