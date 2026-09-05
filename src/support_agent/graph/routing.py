"""Routing helpers for LangGraph conditional edges."""

from __future__ import annotations

from support_agent.schemas import RoutingDecision, TicketState

SEND_RESPONSE_NODE = "send_response"
HUMAN_REVIEW_NODE = "human_review"


def route_after_risk_assessment(state: TicketState) -> str:
    """Route workflow execution after the risk assessment node."""
    if state.risk_assessment is None:
        raise ValueError("Cannot route before risk assessment.")

    if state.risk_assessment.decision == RoutingDecision.LOW_RISK_AUTO_SEND:
        return SEND_RESPONSE_NODE

    return HUMAN_REVIEW_NODE
