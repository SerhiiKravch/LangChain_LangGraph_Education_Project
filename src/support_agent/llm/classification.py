"""Ticket classification chain."""

from __future__ import annotations

from collections.abc import Mapping

from langchain_core.runnables import RunnableLambda

from support_agent.schemas import SupportTicket, TicketCategory, TicketClassification, TicketInput

TicketLike = str | TicketInput | SupportTicket | Mapping[str, object]

CATEGORY_KEYWORDS: dict[TicketCategory, tuple[str, ...]] = {
    TicketCategory.REFUND: (
        "refund",
        "chargeback",
        "money back",
        "duplicate charge",
        "accidental renewal",
    ),
    TicketCategory.ACCOUNT: (
        "delete my account",
        "remove my account",
        "close my account",
        "account deletion",
        "personal data",
    ),
    TicketCategory.BILLING: (
        "invoice",
        "billing",
        "payment",
        "charged",
        "tax",
        "receipt",
    ),
    TicketCategory.TECHNICAL: (
        "api",
        "error",
        "rate limit",
        "bug",
        "integration",
        "timeout",
    ),
    TicketCategory.PRICING: (
        "pricing",
        "price",
        "plan",
        "pro",
        "team",
        "upgrade",
        "downgrade",
    ),
}


def build_ticket_classification_chain() -> RunnableLambda:
    """Build the local ticket classification chain."""
    return RunnableLambda(classify_ticket)


def classify_ticket(ticket: TicketLike) -> TicketClassification:
    """Classify a ticket into a fixed support category."""
    message = _extract_message(ticket)
    normalized_message = message.lower()

    category_scores = {
        category: sum(keyword in normalized_message for keyword in keywords)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    category, score = max(category_scores.items(), key=lambda item: item[1])

    if score == 0:
        return TicketClassification(
            category=TicketCategory.OTHER,
            confidence=0.35,
            reasoning="No known support category keywords were found in the ticket.",
        )

    confidence = round(min(0.95, 0.55 + score * 0.15), 2)
    return TicketClassification(
        category=category,
        confidence=confidence,
        reasoning=f"Matched {score} keyword signal(s) for the {category.value} category.",
    )


def _extract_message(ticket: TicketLike) -> str:
    """Extract the customer message from supported ticket input shapes."""
    if isinstance(ticket, str):
        return ticket.strip()

    if isinstance(ticket, TicketInput | SupportTicket):
        return ticket.message

    if isinstance(ticket, Mapping):
        raw_message = ticket.get("message")
        if isinstance(raw_message, str):
            return raw_message.strip()

    raise TypeError("ticket must be a string, TicketInput, SupportTicket, or mapping with message")
