"""Unit tests for the mock send-response tool."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from support_agent.schemas import DraftResponse, SendStatus, SupportTicket
from support_agent.storage import OutboxStore
from support_agent.tools import DEFAULT_RECIPIENT, send_response


def test_send_response_returns_mock_send_result(tmp_path) -> None:
    result = send_response(
        ticket=_ticket(),
        draft=DraftResponse(message="Thanks for contacting support."),
        outbox_store=OutboxStore(tmp_path / "outbox.jsonl"),
    )

    assert result.ticket_id == "ticket-send"
    assert result.message_id.startswith("mock-msg-")
    assert result.recipient == DEFAULT_RECIPIENT
    assert result.message == "Thanks for contacting support."
    assert result.status == SendStatus.SENT
    assert isinstance(result.sent_at, datetime)


def test_send_response_uses_customer_id_as_recipient(tmp_path) -> None:
    result = send_response(
        ticket=_ticket(customer_id="customer-123"),
        draft=DraftResponse(message="Your answer is ready."),
        outbox_store=OutboxStore(tmp_path / "outbox.jsonl"),
    )

    assert result.recipient == "customer-123"


def test_send_response_allows_explicit_recipient_override(tmp_path) -> None:
    result = send_response(
        ticket=_ticket(customer_id="customer-123"),
        draft=DraftResponse(message="Your answer is ready."),
        recipient="support-inbox",
        outbox_store=OutboxStore(tmp_path / "outbox.jsonl"),
    )

    assert result.recipient == "support-inbox"


def test_send_response_generates_stable_message_id(tmp_path) -> None:
    ticket = _ticket()
    draft = DraftResponse(message="Stable response.")
    outbox_store = OutboxStore(tmp_path / "outbox.jsonl")

    first = send_response(ticket=ticket, draft=draft, outbox_store=outbox_store)
    second = send_response(ticket=ticket, draft=draft, outbox_store=outbox_store)

    assert first.message_id == second.message_id


def test_send_response_is_idempotent_by_ticket_id(tmp_path) -> None:
    ticket = _ticket()
    outbox_store = OutboxStore(tmp_path / "outbox.jsonl")

    first = send_response(
        ticket=ticket,
        draft=DraftResponse(message="First response."),
        outbox_store=outbox_store,
    )
    second = send_response(
        ticket=ticket,
        draft=DraftResponse(message="Changed response that should not be sent."),
        outbox_store=outbox_store,
    )

    assert second == first
    assert second.message == "First response."
    assert outbox_store.list() == [first]


def test_repeated_send_keeps_original_recipient_and_message(tmp_path) -> None:
    ticket = _ticket(customer_id="customer-123")
    outbox_store = OutboxStore(tmp_path / "outbox.jsonl")

    first = send_response(
        ticket=ticket,
        draft=DraftResponse(message="Approved response."),
        outbox_store=outbox_store,
    )
    second = send_response(
        ticket=ticket,
        draft=DraftResponse(message="Edited after send."),
        recipient="alternate-recipient",
        outbox_store=outbox_store,
    )

    assert second == first
    assert second.recipient == "customer-123"
    assert second.message == "Approved response."
    assert len(outbox_store.list()) == 1


def test_send_response_rejects_blank_recipient(tmp_path) -> None:
    outbox_store = OutboxStore(tmp_path / "outbox.jsonl")

    with pytest.raises(ValueError, match="recipient cannot be blank"):
        send_response(
            ticket=_ticket(),
            draft=DraftResponse(message="Valid response."),
            recipient="   ",
            outbox_store=outbox_store,
        )

    assert outbox_store.list() == []


def test_send_response_schema_rejects_blank_message() -> None:
    with pytest.raises(ValidationError):
        DraftResponse(message="   ")


def test_send_response_propagates_outbox_failures(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    outbox_store = OutboxStore(tmp_path / "outbox.jsonl")

    def raise_storage_error(_result) -> None:
        raise RuntimeError("outbox unavailable")

    monkeypatch.setattr(outbox_store, "append_once", raise_storage_error)

    with pytest.raises(RuntimeError, match="outbox unavailable"):
        send_response(
            ticket=_ticket(),
            draft=DraftResponse(message="Valid response."),
            outbox_store=outbox_store,
        )

    assert outbox_store.list() == []


def _ticket(*, customer_id: str | None = None) -> SupportTicket:
    return SupportTicket(
        ticket_id="ticket-send",
        message="Can you help?",
        customer_id=customer_id,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
