"""Graph node for risk assessment."""

from __future__ import annotations

from support_agent.schemas import TicketState, WorkflowStatus
from support_agent.services import assess_risk


def assess_risk_node(state: TicketState) -> TicketState:
    """Assess workflow risk and update the ticket state."""
    if state.classification is None:
        raise ValueError("Cannot assess risk before ticket classification.")

    if state.draft is None:
        raise ValueError("Cannot assess risk before draft generation.")

    risk_assessment = assess_risk(
        classification=state.classification,
        draft=state.draft,
    )
    return state.model_copy(
        update={
            "risk_assessment": risk_assessment,
            "status": WorkflowStatus.RISK_ASSESSED,
        }
    )
