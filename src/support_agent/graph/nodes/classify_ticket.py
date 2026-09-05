"""Graph node for ticket classification."""

from __future__ import annotations

from support_agent.llm import classify_ticket
from support_agent.schemas import TicketState, WorkflowStatus


def classify_ticket_node(state: TicketState) -> TicketState:
    """Classify the current ticket and update workflow state."""
    classification = classify_ticket(state.ticket)
    return state.model_copy(
        update={
            "classification": classification,
            "status": WorkflowStatus.CLASSIFIED,
        }
    )
