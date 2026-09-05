"""Graph node for ticket ingestion."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from support_agent.schemas import SupportTicket, TicketInput, TicketState, WorkflowStatus


def ingest_ticket_node(ticket_input: TicketInput | str | dict[str, object]) -> TicketState:
    """Create the initial workflow state from raw ticket input."""
    normalized_input = _normalize_ticket_input(ticket_input)
    ticket = SupportTicket(
        ticket_id=f"ticket-{uuid4().hex}",
        message=normalized_input.message,
        customer_id=normalized_input.customer_id,
        created_at=datetime.now(UTC),
    )
    return TicketState(ticket=ticket, status=WorkflowStatus.NEW)


def _normalize_ticket_input(ticket_input: TicketInput | str | dict[str, object]) -> TicketInput:
    """Normalize supported ingestion payloads into TicketInput."""
    if isinstance(ticket_input, TicketInput):
        return ticket_input

    if isinstance(ticket_input, str):
        return TicketInput(message=ticket_input)

    return TicketInput.model_validate(ticket_input)
