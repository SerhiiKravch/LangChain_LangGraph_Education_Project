"""Integration tests for the high-risk human review workflow path."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from support_agent.graph import (
    HUMAN_REVIEW_NODE,
    assess_risk_node,
    classify_ticket_node,
    draft_response_node,
    human_review_node,
    ingest_ticket_node,
    resume_after_review_node,
    retrieve_context_node,
    route_after_risk_assessment,
)
from support_agent.schemas import (
    HumanReviewDecision,
    HumanReviewStatus,
    RiskLevel,
    RoutingDecision,
    TicketCategory,
    WorkflowStatus,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HIGH_RISK_FIXTURE = PROJECT_ROOT / "data" / "fixtures" / "high_risk_ticket.json"
KB_DIR = PROJECT_ROOT / "data" / "kb"


def test_high_risk_ticket_pauses_for_review_and_resumes_after_edit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = json.loads(HIGH_RISK_FIXTURE.read_text(encoding="utf-8"))
    edited_message = "Your account deletion request has been reviewed by support."
    captured_payload: dict[str, Any] = {}

    def fake_interrupt(payload: dict[str, Any]) -> dict[str, str]:
        captured_payload.update(payload)
        return {
            "decision": "edit",
            "reviewer_id": "agent-123",
            "edited_message": edited_message,
        }

    monkeypatch.setattr("support_agent.graph.nodes.human_review.interrupt", fake_interrupt)

    state = ingest_ticket_node(fixture)
    assert state.status == WorkflowStatus.NEW
    assert state.ticket.message == fixture["message"]

    state = classify_ticket_node(state)
    assert state.status == WorkflowStatus.CLASSIFIED
    assert state.classification is not None
    assert state.classification.category == TicketCategory.ACCOUNT

    state = retrieve_context_node(state, kb_dir=KB_DIR, k=3)
    assert state.status == WorkflowStatus.CONTEXT_RETRIEVED
    assert state.retrieved_context

    state = draft_response_node(state)
    assert state.status == WorkflowStatus.DRAFTED
    assert state.draft is not None
    assert state.draft.needs_more_context is False
    assert state.draft.citations

    state = assess_risk_node(state)
    assert state.status == WorkflowStatus.RISK_ASSESSED
    assert state.risk_assessment is not None
    assert state.risk_assessment.risk_level == RiskLevel.HIGH
    assert state.risk_assessment.decision == RoutingDecision.NEEDS_HUMAN_REVIEW
    assert route_after_risk_assessment(state) == HUMAN_REVIEW_NODE

    state = human_review_node(state)
    assert state.status == WorkflowStatus.WAITING_FOR_REVIEW
    assert state.review is not None
    assert state.review.status == HumanReviewStatus.EDITED
    assert state.review.action is not None
    assert state.review.action.decision == HumanReviewDecision.EDIT
    assert captured_payload["ticket"]["ticket_id"] == state.ticket.ticket_id
    assert captured_payload["risk_assessment"]["risk_level"] == "high"

    state = resume_after_review_node(state)
    assert state.status == WorkflowStatus.REVIEWED
    assert state.draft is not None
    assert state.draft.message == edited_message
