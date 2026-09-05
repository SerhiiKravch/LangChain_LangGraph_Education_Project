"""Integration tests for the low-risk support workflow path."""

from __future__ import annotations

import json
from pathlib import Path

from support_agent.graph import (
    SEND_RESPONSE_NODE,
    assess_risk_node,
    classify_ticket_node,
    draft_response_node,
    ingest_ticket_node,
    retrieve_context_node,
    route_after_risk_assessment,
)
from support_agent.schemas import RiskLevel, RoutingDecision, TicketCategory, WorkflowStatus

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOW_RISK_FIXTURE = PROJECT_ROOT / "data" / "fixtures" / "low_risk_ticket.json"
KB_DIR = PROJECT_ROOT / "data" / "kb"


def test_low_risk_ticket_reaches_auto_send_route() -> None:
    fixture = json.loads(LOW_RISK_FIXTURE.read_text(encoding="utf-8"))

    state = ingest_ticket_node(fixture)
    assert state.status == WorkflowStatus.NEW
    assert state.ticket.message == fixture["message"]

    state = classify_ticket_node(state)
    assert state.status == WorkflowStatus.CLASSIFIED
    assert state.classification is not None
    assert state.classification.category == TicketCategory.PRICING

    state = retrieve_context_node(state, kb_dir=KB_DIR, k=3)
    assert state.status == WorkflowStatus.CONTEXT_RETRIEVED
    assert len(state.retrieved_context) == 3
    assert all(snippet.document_id for snippet in state.retrieved_context)

    state = draft_response_node(state)
    assert state.status == WorkflowStatus.DRAFTED
    assert state.draft is not None
    assert state.draft.needs_more_context is False
    assert state.draft.citations

    state = assess_risk_node(state)
    assert state.status == WorkflowStatus.RISK_ASSESSED
    assert state.risk_assessment is not None
    assert state.risk_assessment.risk_level == RiskLevel.LOW
    assert state.risk_assessment.decision == RoutingDecision.LOW_RISK_AUTO_SEND

    assert route_after_risk_assessment(state) == SEND_RESPONSE_NODE
