from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import fakeredis.aioredis as fakeredis
import httpx
import pytest

from app.contracts.events import ContextualIntervention, Severity
from app.models.tables import Obligation, User
from app.modules.decision.service import DecisionService
from app.modules.decision.trace import TraceBuilder
from app.modules.explain.grounding import extract_facts, validate_narration
from app.modules.explain.narrator import Narrator
from app.modules.explain.templates import classify_intervention_type, render_template
from app.platform.config import get_settings

# ---------------------------------------------------------------------------
# Shared test helpers
# ---------------------------------------------------------------------------


class _FakeGroqClient:
    def __init__(self, content: str | None = None, raise_exc: Exception | None = None) -> None:
        self.content = content
        self.raise_exc = raise_exc

    async def post(self, url, json=None, headers=None):
        if self.raise_exc is not None:
            raise self.raise_exc
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": self.content}}]},
            request=httpx.Request("POST", url),
        )

    async def aclose(self) -> None:
        pass


def _llm_settings_with_key():
    return get_settings().model_copy(update={"GROQ_API_KEY": "test-key-not-real"})


def _make_trace_and_intervention(prob_pct: int = 41, amount: Decimal = Decimal("15000")):
    builder = TraceBuilder()
    builder.add("event", "Risk assessment triggered.", {})
    builder.add("state_change", f"Cash available Rs.{amount:,.2f}.", {"cash_available": str(amount)})
    builder.add(
        "simulation",
        f"Simulated shortfall probability: {prob_pct}%.",
        {"shortfall_probability_pct": prob_pct},
    )
    trace = builder.build()

    intervention = ContextualIntervention(
        user_id=uuid4(),
        severity=Severity.notify,
        headline=f"NOTIFY: shortfall risk at {prob_pct}%",
        body=f"Cash available Rs.{amount:,.2f}. Shortfall risk is {prob_pct}%.",
        severity_raw=0.5,
        probability=prob_pct / 100,
        urgency_score=0.5,
        data_confidence=0.9,
        decision_trace=trace,
    )
    return trace, intervention


# ---------------------------------------------------------------------------
# GROUNDING (the critical tests)
# ---------------------------------------------------------------------------


def test_narration_with_only_trace_numbers_is_valid():
    trace, intervention = _make_trace_and_intervention(prob_pct=41, amount=Decimal("15000"))
    facts = extract_facts(trace, intervention)
    narration = "Your shortfall risk is 41%, based on cash of Rs.15,000.00."
    assert validate_narration(narration, facts).valid is True


def test_narration_with_invented_number_is_invalid():
    trace, intervention = _make_trace_and_intervention(prob_pct=41, amount=Decimal("15000"))
    facts = extract_facts(trace, intervention)
    result = validate_narration("Your shortfall risk is 58%.", facts)
    assert result.valid is False
    assert any("58" in v for v in result.violations)


def test_narration_with_invented_amount_is_invalid():
    trace, intervention = _make_trace_and_intervention(prob_pct=41, amount=Decimal("15000"))
    facts = extract_facts(trace, intervention)
    result = validate_narration("You have Rs.99,000.00 available.", facts)
    assert result.valid is False


def test_narration_with_guarantee_language_is_invalid():
    trace, intervention = _make_trace_and_intervention()
    facts = extract_facts(trace, intervention)
    assert validate_narration("You will definitely be fine next month.", facts).valid is False
    assert validate_narration("This outcome is guaranteed.", facts).valid is False


def test_formatting_variance_is_accepted():
    trace, intervention = _make_trace_and_intervention(prob_pct=41, amount=Decimal("15000"))
    facts = extract_facts(trace, intervention)
    assert validate_narration("Cash available is Rs.15,000.", facts).valid is True
    assert validate_narration("Your risk is 41%.", facts).valid is True


# ---------------------------------------------------------------------------
# FALLBACK
# ---------------------------------------------------------------------------


async def test_no_llm_key_returns_template_narration():
    trace, intervention = _make_trace_and_intervention()
    settings = get_settings().model_copy(update={"GROQ_API_KEY": ""})
    narrator = Narrator(settings=settings)

    result = await narrator.narrate(trace, intervention)

    assert result.source == "template_fallback"
    assert result.validation_passed is True
    assert result.text  # genuinely non-empty, readable text


async def test_llm_exception_falls_back_to_template_without_crashing():
    trace, intervention = _make_trace_and_intervention()
    narrator = Narrator(settings=_llm_settings_with_key(), http_client=_FakeGroqClient(raise_exc=RuntimeError("boom")))

    result = await narrator.narrate(trace, intervention)

    assert result.source == "template_fallback"
    assert result.text


async def test_llm_invalid_json_output_falls_back_to_template_with_violations_logged():
    trace, intervention = _make_trace_and_intervention()
    narrator = Narrator(settings=_llm_settings_with_key(), http_client=_FakeGroqClient(content="not valid json at all"))

    result = await narrator.narrate(trace, intervention)

    assert result.source == "template_fallback"
    assert result.validation_passed is False
    assert result.violations


async def test_llm_returning_hallucinated_number_falls_back_to_template():
    trace, intervention = _make_trace_and_intervention(prob_pct=41)
    fake_content = '{"narration": "Your shortfall risk is 58% and rising fast."}'
    narrator = Narrator(settings=_llm_settings_with_key(), http_client=_FakeGroqClient(content=fake_content))

    result = await narrator.narrate(trace, intervention)

    assert result.source == "template_fallback"
    assert result.validation_passed is False
    assert any("58" in v for v in result.violations)


async def test_llm_timeout_falls_back_to_template():
    trace, intervention = _make_trace_and_intervention()
    narrator = Narrator(
        settings=_llm_settings_with_key(), http_client=_FakeGroqClient(raise_exc=httpx.TimeoutException("timed out"))
    )

    result = await narrator.narrate(trace, intervention)

    assert result.source == "template_fallback"


async def test_valid_llm_output_is_used_as_is():
    trace, intervention = _make_trace_and_intervention(prob_pct=41, amount=Decimal("15000"))
    fake_content = '{"narration": "Your shortfall risk is 41% given cash of Rs.15,000."}'
    narrator = Narrator(settings=_llm_settings_with_key(), http_client=_FakeGroqClient(content=fake_content))

    result = await narrator.narrate(trace, intervention)

    assert result.source == "llm"
    assert result.validation_passed is True
    assert "41%" in result.text


# ---------------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------------


def _base_intervention(trace, **overrides) -> ContextualIntervention:
    defaults: dict = dict(
        user_id=uuid4(),
        severity=Severity.notify,
        headline="NOTIFY: shortfall risk at 40%",
        body="Cash available Rs.5,000.00 is below what's needed. Shortfall risk is 40%.",
        severity_raw=0.5,
        probability=0.4,
        urgency_score=0.5,
        data_confidence=0.9,
        decision_trace=trace,
    )
    defaults.update(overrides)
    return ContextualIntervention(**defaults)


def test_every_intervention_type_has_a_template():
    # collision
    collision_builder = TraceBuilder()
    collision_builder.add("event", "x", {})
    collision_builder.add(
        "collision", "Collision detected.", {"joint_probability_pct": 45, "baseline_probability_pct": 5}
    )
    collision_trace = collision_builder.build()
    collision_intervention = _base_intervention(collision_trace)
    assert classify_intervention_type(collision_trace, collision_intervention) == "collision"
    collision_text = render_template(collision_trace, collision_intervention)
    assert collision_text and "{" not in collision_text

    # threat
    threat_builder = TraceBuilder()
    threat_builder.add("event", "x", {})
    threat_trace = threat_builder.build()
    threat_intervention = _base_intervention(threat_trace, triggered_by_threat_id=uuid4())
    assert classify_intervention_type(threat_trace, threat_intervention) == "threat"
    threat_text = render_template(threat_trace, threat_intervention)
    assert threat_text and "{" not in threat_text

    # goal_conflict
    goal_builder = TraceBuilder()
    goal_builder.add("event", "x", {})
    goal_builder.add(
        "rule_findings", "1 risk rule(s) triggered.", {"goal_conflicts_obligation.cash_available": "5000"}
    )
    goal_trace = goal_builder.build()
    goal_intervention = _base_intervention(goal_trace)
    assert classify_intervention_type(goal_trace, goal_intervention) == "goal_conflict"
    goal_text = render_template(goal_trace, goal_intervention)
    assert goal_text and "{" not in goal_text

    # weather_change
    weather_builder = TraceBuilder()
    weather_builder.add("event", "x", {})
    weather_trace = weather_builder.build()
    weather_intervention = _base_intervention(weather_trace, headline="WEATHER: outlook worsened")
    assert classify_intervention_type(weather_trace, weather_intervention) == "weather_change"
    weather_text = render_template(weather_trace, weather_intervention)
    assert weather_text and "{" not in weather_text

    # safe_to_spend (default fallback)
    safe_builder = TraceBuilder()
    safe_builder.add("event", "x", {})
    safe_trace = safe_builder.build()
    safe_intervention = _base_intervention(safe_trace)
    assert classify_intervention_type(safe_trace, safe_intervention) == "safe_to_spend"
    safe_text = render_template(safe_trace, safe_intervention)
    assert safe_text and "{" not in safe_text


def test_templates_contain_real_values_never_unfilled_placeholders():
    trace, intervention = _make_trace_and_intervention(prob_pct=41, amount=Decimal("15000"))
    text = render_template(trace, intervention)
    assert "41%" in text or "15,000" in text
    assert "{" not in text and "}" not in text


# ---------------------------------------------------------------------------
# DELETABILITY (the architectural test)
# ---------------------------------------------------------------------------


async def test_core_decision_flow_never_depends_on_explain_module():
    import inspect

    import app.modules.decision.service as decision_service_module

    source = inspect.getsource(decision_service_module)
    assert "app.modules.explain" not in source
    assert "app.modules.explain" not in decision_service_module.__doc__


async def test_intervention_flow_completes_with_readable_text_even_if_narrator_is_unavailable(db_session):
    # Simulates "app.modules.explain was deleted": Narrator itself is
    # unusable, yet the actual intervention-producing flow
    # (DecisionService.decide, which never imports app.modules.explain)
    # must complete normally and return fully readable, template-based
    # headline/body text.
    with patch("app.modules.explain.narrator.Narrator.__init__", side_effect=ImportError("module deleted")):
        with pytest.raises(ImportError):
            from app.modules.explain.narrator import Narrator as NarratorClass

            NarratorClass()

        user_id = uuid4()
        db_session.add(User(id=user_id, email=f"{user_id}@example.com", password_hash="hash"))
        db_session.add(
            Obligation(
                user_id=user_id,
                label="Rent",
                amount=Decimal("50000"),
                due_date=date.today() + timedelta(days=3),
                category="rent",
                is_fixed=True,
                is_paid=False,
                data_source="manual",
                confidence_score=0.9,
            )
        )
        from app.models.tables import FinancialEvent

        db_session.add(
            FinancialEvent(
                id=uuid4(),
                user_id=user_id,
                schema_version=1,
                event_type="income_received",
                amount=Decimal("500"),
                currency="INR",
                occurred_at=datetime.now(timezone.utc),
                data_source="manual",
                confidence_score=0.9,
            )
        )
        await db_session.commit()

        import app.modules.simulation.service as simulation_service_module
        import app.modules.twin.snapshot as twin_snapshot_module

        twin_snapshot_module._default_redis_client = None
        simulation_service_module._default_redis_client = None
        fake_redis = fakeredis.FakeRedis(decode_responses=True)

        with patch("redis.asyncio.from_url", return_value=fake_redis):
            intervention = await DecisionService().decide(db_session, user_id)

        assert intervention is not None
        assert intervention.headline
        assert intervention.body
        assert len(intervention.body) > 0


# ---------------------------------------------------------------------------
# CACHING
# ---------------------------------------------------------------------------


async def test_same_trace_produces_same_narration_on_repeated_calls():
    trace, intervention = _make_trace_and_intervention(prob_pct=41, amount=Decimal("15000"))
    fake_redis = fakeredis.FakeRedis(decode_responses=True)

    call_count = 0

    class _CountingGroqClient(_FakeGroqClient):
        async def post(self, url, json=None, headers=None):
            nonlocal call_count
            call_count += 1
            # A DIFFERENT narration each call, to prove a repeat call
            # returns the CACHED first result rather than calling the LLM again.
            content = f'{{"narration": "Call number {call_count}: shortfall risk is 41% on Rs.15,000."}}'
            return httpx.Response(
                200, json={"choices": [{"message": {"content": content}}]}, request=httpx.Request("POST", url)
            )

    narrator = Narrator(redis_client=fake_redis, settings=_llm_settings_with_key(), http_client=_CountingGroqClient())

    first = await narrator.narrate(trace, intervention)
    second = await narrator.narrate(trace, intervention)

    assert first.text == second.text
    assert second.cached is True
    assert call_count == 1  # the LLM was only actually invoked once
