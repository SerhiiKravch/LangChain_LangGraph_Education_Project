"""Unit tests for the human review interrupt node."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from support_agent.graph import human_review_node
from support_agent.schemas import (
    DraftCitation,
    DraftResponse,
    HumanReviewDecision,
    HumanReviewStatus,
    RiskAssessment,
    RiskLevel,
    RoutingDecision,
    SupportTicket,
    TicketCategory,
    TicketClassification,
    TicketState,
    WorkflowStatus,
)


def test_human_review_node_pauses_and_stores_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_payload: dict[str, Any] = {}

    def fake_interrupt(payload: dict[str, Any]) -> dict[str, str]:
        captured_payload.update(payload)
        return {
            "decision": "approve",
            "reviewer_id": "agent-123",
        }

    monkeypatch.setattr("support_agent.graph.nodes.human_review.interrupt", fake_interrupt)

    updated_state = human_review_node(_reviewable_state())

    assert updated_state.status == WorkflowStatus.WAITING_FOR_REVIEW
    assert updated_state.review is not None
    assert updated_state.review.status == HumanReviewStatus.APPROVED
    assert updated_state.review.action is not None
    assert updated_state.review.action.decision == HumanReviewDecision.APPROVE
    assert captured_payload["ticket"]["ticket_id"] == "ticket-review"
    assert captured_payload["risk_assessment"]["decision"] == "needs_human_review"


def test_human_review_node_stores_edited_decision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "support_agent.graph.nodes.human_review.interrupt",
        lambda _payload: {
            "decision": "edit",
            "reviewer_id": "agent-123",
            "edited_message": "Reviewer-approved edited response.",
        },
    )

    updated_state = human_review_node(_reviewable_state())

    assert updated_state.review is not None
    assert updated_state.review.status == HumanReviewStatus.EDITED
    assert updated_state.review.action is not None
    assert updated_state.review.action.edited_message == "Reviewer-approved edited response."


def test_human_review_node_requires_draft_and_risk_assessment() -> None:
    state = _reviewable_state()

    with pytest.raises(ValueError, match="before draft generation"):
        human_review_node(state.model_copy(update={"draft": None}))

    with pytest.raises(ValueError, match="before risk assessment"):
        human_review_node(state.model_copy(update={"risk_assessment": None}))


def _reviewable_state() -> TicketState:
    return TicketState(
        ticket=SupportTicket(
            ticket_id="ticket-review",
            message="I was charged twice and need help.",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
        classification=TicketClassification(
            category=TicketCategory.BILLING,
            confidence=0.95,
            reasoning="Matched billing keywords.",
        ),
        draft=DraftResponse(
            message="Grounded billing response.",
            citations=[
                DraftCitation(
                    document_id="billing",
                    title="Billing Help",
                )
            ],
        ),
        risk_assessment=RiskAssessment(
            risk_level=RiskLevel.HIGH,
            decision=RoutingDecision.NEEDS_HUMAN_REVIEW,
            requires_human_review=True,
            reasoning="Billing requests require human review.",
        ),
    )
