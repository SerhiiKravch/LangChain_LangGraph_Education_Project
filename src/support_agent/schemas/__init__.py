"""State and structured output schemas."""

from support_agent.schemas.classification import TicketClassification
from support_agent.schemas.draft import DraftCitation, DraftResponse
from support_agent.schemas.ticket import SupportTicket, TicketCategory, TicketInput

__all__ = [
    "DraftCitation",
    "DraftResponse",
    "SupportTicket",
    "TicketCategory",
    "TicketClassification",
    "TicketInput",
]
