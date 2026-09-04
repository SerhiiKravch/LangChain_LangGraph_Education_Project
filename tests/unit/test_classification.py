"""Unit tests for ticket classification schemas and chain."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from support_agent.llm import build_ticket_classification_chain, classify_ticket
from support_agent.schemas import SupportTicket, TicketCategory, TicketClassification, TicketInput


def test_ticket_input_strips_message_whitespace() -> None:
    ticket = TicketInput(message="  How do I cancel my subscription?  ")

    assert ticket.message == "How do I cancel my subscription?"


def test_ticket_input_rejects_blank_message() -> None:
    with pytest.raises(ValidationError):
        TicketInput(message="   ")


def test_support_ticket_requires_ticket_id_and_created_at() -> None:
    ticket = SupportTicket(
        ticket_id="ticket-123",
        message="Why does your API return rate limit errors?",
        created_at=datetime(2026, 9, 4, tzinfo=UTC),
    )

    assert ticket.ticket_id == "ticket-123"
    assert ticket.customer_id is None


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_ticket_classification_rejects_confidence_outside_range(confidence: float) -> None:
    with pytest.raises(ValidationError):
        TicketClassification(
            category=TicketCategory.PRICING,
            confidence=confidence,
            reasoning="Pricing question.",
        )


@pytest.mark.parametrize(
    ("message", "expected_category"),
    [
        ("I want a refund for the last payment.", TicketCategory.REFUND),
        ("Why does your API return rate limit errors?", TicketCategory.TECHNICAL),
        ("Can you explain the Pro and Team plans?", TicketCategory.PRICING),
        ("Please delete my account immediately.", TicketCategory.ACCOUNT),
        ("Where can I find my invoice?", TicketCategory.BILLING),
        ("Can you help with something unusual?", TicketCategory.OTHER),
    ],
)
def test_classify_ticket_returns_expected_category(
    message: str,
    expected_category: TicketCategory,
) -> None:
    result = classify_ticket(message)

    assert result.category == expected_category
    assert 0.0 <= result.confidence <= 1.0
    assert result.reasoning


def test_classify_ticket_accepts_ticket_input_model() -> None:
    ticket = TicketInput(message="I need the receipt for my last payment.")

    result = classify_ticket(ticket)

    assert result.category == TicketCategory.BILLING


def test_classify_ticket_accepts_support_ticket_model() -> None:
    ticket = SupportTicket(
        ticket_id="ticket-456",
        message="The API times out during integration testing.",
        created_at=datetime(2026, 9, 4, tzinfo=UTC),
    )

    result = classify_ticket(ticket)

    assert result.category == TicketCategory.TECHNICAL


def test_classify_ticket_accepts_mapping_with_message() -> None:
    result = classify_ticket({"message": "How much does the Pro plan cost?"})

    assert result.category == TicketCategory.PRICING


def test_classify_ticket_rejects_unsupported_input() -> None:
    with pytest.raises(TypeError):
        classify_ticket(object())


def test_ticket_classification_chain_invokes_classifier() -> None:
    chain = build_ticket_classification_chain()

    result = chain.invoke({"message": "I was charged twice and need help."})

    assert result.category == TicketCategory.BILLING
    assert result.confidence > 0
