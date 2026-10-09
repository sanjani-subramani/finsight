from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.tables import DependencyEdge as DependencyEdgeRow
from app.models.tables import TransactionEvent as TransactionEventRow
from app.modules.org.fingraph.graph_builder import build_graph, detect_cycles, validate_and_build
from app.modules.org.fingraph.graph_management import CycleError, add_edge, add_node
from app.modules.org.fingraph.impact import compute_blast_radius, compute_centrality, what_if_multiple

# ---------------------------------------------------------------------------
# Shared fixture: the architecture-doc KYC example
#
# KYC Provider (service) is depended on by Onboarding (workflow), which is
# in turn depended on by Loans and Cards (workflows). "KYC Provider fails"
# should therefore transitively affect exactly {Onboarding, Loans, Cards}.
# ---------------------------------------------------------------------------


async def _build_kyc_example(db_session, org_id):
    kyc = await add_node(db_session, org_id, "KYC Provider", "service", is_critical=True)
    onboarding = await add_node(db_session, org_id, "Onboarding", "workflow")
    loans = await add_node(db_session, org_id, "Loans", "workflow", is_critical=True)
    cards = await add_node(db_session, org_id, "Cards", "workflow")

    await add_edge(db_session, org_id, "Onboarding", "KYC Provider")
    await add_edge(db_session, org_id, "Loans", "Onboarding")
    await add_edge(db_session, org_id, "Cards", "Onboarding")

    return {"kyc": kyc, "onboarding": onboarding, "loans": loans, "cards": cards}


# ---------------------------------------------------------------------------
# Graph building
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_genuine_cycle_is_flagged_not_silently_accepted(db_session):
    org_id = uuid4()
    a = await add_node(db_session, org_id, "A", "service")
    b = await add_node(db_session, org_id, "B", "service")

    # Inserted directly (bypassing graph_management.add_edge's own guard)
    # to simulate a cycle that already made it into the data some other
    # way -- e.g. a bulk import authored outside this API.
    db_session.add(DependencyEdgeRow(org_id=org_id, from_node_id=a.id, to_node_id=b.id, edge_type="depends_on", weight=1.0))
    db_session.add(DependencyEdgeRow(org_id=org_id, from_node_id=b.id, to_node_id=a.id, edge_type="depends_on", weight=1.0))
    await db_session.commit()

    build_result = await validate_and_build(db_session, org_id)

    assert build_result.warnings != []
    graph = await build_graph(db_session, org_id)
    cycles = detect_cycles(graph)
    assert any(set(c) == {"A", "B"} for c in cycles)


@pytest.mark.asyncio
async def test_adding_an_edge_that_would_create_a_cycle_is_rejected(db_session):
    org_id = uuid4()
    await add_node(db_session, org_id, "A", "service")
    await add_node(db_session, org_id, "B", "service")
    await add_edge(db_session, org_id, "A", "B")

    with pytest.raises(CycleError):
        await add_edge(db_session, org_id, "B", "A")


# ---------------------------------------------------------------------------
# Impact
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_kyc_provider_failure_affects_exactly_onboarding_loans_and_cards(db_session):
    org_id = uuid4()
    await _build_kyc_example(db_session, org_id)
    await db_session.commit()

    result = await compute_blast_radius(db_session, org_id, "KYC Provider")

    assert set(result.affected_workflows) == {"Onboarding", "Loans", "Cards"}
    assert result.affected_services == []


@pytest.mark.asyncio
async def test_leaf_node_failing_affects_nothing(db_session):
    org_id = uuid4()
    await _build_kyc_example(db_session, org_id)
    # Cards is a leaf -- nothing depends on it.
    await db_session.commit()

    result = await compute_blast_radius(db_session, org_id, "Cards")

    assert result.affected_services == []
    assert result.affected_workflows == []


@pytest.mark.asyncio
async def test_root_node_failing_affects_everything(db_session):
    org_id = uuid4()
    await _build_kyc_example(db_session, org_id)
    await db_session.commit()

    result = await compute_blast_radius(db_session, org_id, "KYC Provider")

    total_other_nodes = 3  # Onboarding, Loans, Cards
    assert len(result.affected_services) + len(result.affected_workflows) == total_other_nodes


@pytest.mark.asyncio
async def test_critical_paths_trace_the_dependency_chain(db_session):
    org_id = uuid4()
    await _build_kyc_example(db_session, org_id)
    await db_session.commit()

    result = await compute_blast_radius(db_session, org_id, "KYC Provider")

    # Loans is critical; its chain to the failed node is Loans -> Onboarding -> KYC Provider.
    assert ["Loans", "Onboarding", "KYC Provider"] in result.critical_paths


@pytest.mark.asyncio
async def test_alternative_providers_are_returned(db_session):
    org_id = uuid4()
    nodes = await _build_kyc_example(db_session, org_id)
    await add_node(db_session, org_id, "Backup KYC Provider", "service", alternative_for=nodes["kyc"].id)
    await db_session.commit()

    result = await compute_blast_radius(db_session, org_id, "KYC Provider")

    assert result.alternative_providers == ["Backup KYC Provider"]


# ---------------------------------------------------------------------------
# Centrality
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hub_has_highest_betweenness_in_a_star_graph(db_session):
    org_id = uuid4()
    await add_node(db_session, org_id, "Hub", "service")
    await add_node(db_session, org_id, "Spoke1", "service")
    await add_node(db_session, org_id, "Spoke2", "service")
    await add_node(db_session, org_id, "Spoke3", "service")

    # Spoke1 depends on Hub; Hub depends on Spoke2 and Spoke3 -- every
    # shortest path from Spoke1 to {Spoke2, Spoke3} passes through Hub.
    await add_edge(db_session, org_id, "Spoke1", "Hub")
    await add_edge(db_session, org_id, "Hub", "Spoke2")
    await add_edge(db_session, org_id, "Hub", "Spoke3")
    await db_session.commit()

    centrality = await compute_centrality(db_session, org_id)

    hub_score = centrality["Hub"].betweenness
    assert hub_score > 0
    assert hub_score == max(c.betweenness for c in centrality.values())


@pytest.mark.asyncio
async def test_an_isolated_node_has_zero_centrality(db_session):
    org_id = uuid4()
    await add_node(db_session, org_id, "Hub", "service")
    await add_node(db_session, org_id, "Spoke1", "service")
    await add_edge(db_session, org_id, "Spoke1", "Hub")
    await add_node(db_session, org_id, "Lonely", "service")
    await db_session.commit()

    centrality = await compute_centrality(db_session, org_id)

    assert centrality["Lonely"].betweenness == 0.0


# ---------------------------------------------------------------------------
# Cross-module (PayTrace)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_estimated_transactions_reflects_actual_paytrace_volume(db_session):
    org_id = uuid4()
    await add_node(db_session, org_id, "Razorpay Gateway", "service", metadata={"provider": "razorpay"})
    await db_session.commit()

    now = datetime.now(timezone.utc) - timedelta(hours=1)
    for i in range(7):
        db_session.add(
            TransactionEventRow(
                org_id=org_id,
                transaction_ref=f"TX{i}",
                stage="initiated",
                occurred_at=now,
                amount=Decimal("100.00"),
                provider="razorpay",
                idempotency_key=f"TX{i}-init",
            )
        )
    await db_session.commit()

    result = await compute_blast_radius(db_session, org_id, "Razorpay Gateway")

    assert result.estimated_transactions == 7


# ---------------------------------------------------------------------------
# Multi-failure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_multi_failure_affected_set_is_at_least_as_large_as_either_alone(db_session):
    org_id = uuid4()
    await add_node(db_session, org_id, "KYC Provider", "service")
    await add_node(db_session, org_id, "SMS Provider", "service")
    await add_node(db_session, org_id, "Onboarding", "workflow")
    await add_node(db_session, org_id, "Alerts", "workflow")

    await add_edge(db_session, org_id, "Onboarding", "KYC Provider")
    await add_edge(db_session, org_id, "Alerts", "SMS Provider")
    await db_session.commit()

    kyc_only = await compute_blast_radius(db_session, org_id, "KYC Provider")
    sms_only = await compute_blast_radius(db_session, org_id, "SMS Provider")
    both = await what_if_multiple(db_session, org_id, ["KYC Provider", "SMS Provider"])

    combined_affected = set(both.affected_services) | set(both.affected_workflows)
    kyc_affected = set(kyc_only.affected_services) | set(kyc_only.affected_workflows)
    sms_affected = set(sms_only.affected_services) | set(sms_only.affected_workflows)

    assert combined_affected >= kyc_affected
    assert combined_affected >= sms_affected
    assert len(combined_affected) >= max(len(kyc_affected), len(sms_affected))
    assert combined_affected == {"Onboarding", "Alerts"}
