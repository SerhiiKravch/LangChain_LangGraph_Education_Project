"""Unit tests for the mock send-response tool."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from support_agent.schemas import DraftResponse, SendStatus, SupportTicket
from support_agent.tools import DEFAULT_RECIPIENT, send_response


def test_send_response_returns_mock_send_result() -> None:
    result = send_response(
        ticket=_ticket(),
        draft=DraftResponse(message="Thanks for contacting support."),
    )

    assert result.ticket_id == "ticket-send"
    assert result.message_id.startswith("mock-msg-")
    assert result.recipient == DEFAULT_RECIPIENT
    assert result.message == "Thanks for contacting support."
    assert result.status == SendStatus.SENT
    assert isinstance(result.sent_at, datetime)


def test_send_response_uses_customer_id_as_recipient() -> None:
    result = send_response(
        ticket=_ticket(customer_id="customer-123"),
        draft=DraftResponse(message="Your answer is ready."),
    )

    assert result.recipient == "customer-123"


def test_send_response_allows_explicit_recipient_override() -> None:
    result = send_response(
        ticket=_ticket(customer_id="customer-123"),
        draft=DraftResponse(message="Your answer is ready."),
        recipient="support-inbox",
    )

    assert result.recipient == "support-inbox"


def test_send_response_generates_stable_message_id() -> None:
    ticket = _ticket()
    draft = DraftResponse(message="Stable response.")

    first = send_response(ticket=ticket, draft=draft)
    second = send_response(ticket=ticket, draft=draft)

    assert first.message_id == second.message_id


def test_send_response_rejects_blank_recipient() -> None:
    with pytest.raises(ValueError, match="recipient cannot be blank"):
        send_response(
            ticket=_ticket(),
            draft=DraftResponse(message="Valid response."),
            recipient="   ",
        )


def test_send_response_schema_rejects_blank_message() -> None:
    with pytest.raises(ValidationError):
        DraftResponse(message="   ")


def _ticket(*, customer_id: str | None = None) -> SupportTicket:
    return SupportTicket(
        ticket_id="ticket-send",
        message="Can you help?",
        customer_id=customer_id,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
