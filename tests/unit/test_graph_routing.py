"""Unit tests for graph risk assessment routing."""

from datetime import UTC, datetime

import pytest

from support_agent.graph import (
    HUMAN_REVIEW_NODE,
    SEND_RESPONSE_NODE,
    assess_risk_node,
    route_after_risk_assessment,
)
from support_agent.schemas import (
    DraftCitation,
    DraftResponse,
    RoutingDecision,
    SupportTicket,
    TicketCategory,
    TicketClassification,
    TicketState,
    WorkflowStatus,
)


def test_assess_risk_node_updates_state_for_auto_send() -> None:
    state = TicketState(
        ticket=_ticket(),
        classification=_classification(TicketCategory.PRICING, confidence=0.95),
        draft=_grounded_draft(),
    )

    updated_state = assess_risk_node(state)

    assert updated_state.status == WorkflowStatus.RISK_ASSESSED
    assert updated_state.risk_assessment is not None
    assert updated_state.risk_assessment.decision == RoutingDecision.LOW_RISK_AUTO_SEND
    assert route_after_risk_assessment(updated_state) == SEND_RESPONSE_NODE


def test_route_after_risk_assessment_sends_review_cases_to_human_review() -> None:
    state = TicketState(
        ticket=_ticket(),
        classification=_classification(TicketCategory.BILLING, confidence=0.95),
        draft=_grounded_draft(),
    )

    updated_state = assess_risk_node(state)

    assert updated_state.risk_assessment is not None
    assert updated_state.risk_assessment.decision == RoutingDecision.NEEDS_HUMAN_REVIEW
    assert route_after_risk_assessment(updated_state) == HUMAN_REVIEW_NODE


def test_route_after_risk_assessment_requires_assessment() -> None:
    with pytest.raises(ValueError, match="Cannot route before risk assessment"):
        route_after_risk_assessment(TicketState(ticket=_ticket()))


def test_assess_risk_node_requires_classification_and_draft() -> None:
    with pytest.raises(ValueError, match="before ticket classification"):
        assess_risk_node(TicketState(ticket=_ticket(), draft=_grounded_draft()))

    with pytest.raises(ValueError, match="before draft generation"):
        assess_risk_node(
            TicketState(
                ticket=_ticket(),
                classification=_classification(TicketCategory.PRICING, confidence=0.95),
            )
        )


def _ticket() -> SupportTicket:
    return SupportTicket(
        ticket_id="ticket-test",
        message="Can you explain the Pro pricing plan?",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _classification(
    category: TicketCategory,
    *,
    confidence: float,
) -> TicketClassification:
    return TicketClassification(
        category=category,
        confidence=confidence,
        reasoning=f"Fixture classification for {category.value}.",
    )


def _grounded_draft() -> DraftResponse:
    return DraftResponse(
        message="Grounded response.",
        citations=[
            DraftCitation(
                document_id="pricing",
                title="Pricing Plans",
            )
        ],
    )
