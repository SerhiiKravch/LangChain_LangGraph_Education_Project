"""Unit tests for file-backed storage adapters."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from support_agent.schemas import SendResponseResult
from support_agent.storage import AuditEvent, AuditLogStore, OutboxStore


def test_outbox_store_appends_and_reads_sent_responses(tmp_path) -> None:
    store = OutboxStore(tmp_path / "outbox" / "messages.jsonl")
    result = _send_result(ticket_id="ticket-1")

    stored_result = store.append(result)

    assert stored_result == result
    assert store.list() == [result]


def test_outbox_store_append_once_returns_existing_ticket_result(tmp_path) -> None:
    store = OutboxStore(tmp_path / "outbox" / "messages.jsonl")
    first = _send_result(ticket_id="ticket-1", message_id="mock-msg-1")
    second = _send_result(ticket_id="ticket-1", message_id="mock-msg-2")

    assert store.append_once(first) == first
    assert store.append_once(second) == first
    assert store.list() == [first]


def test_outbox_store_returns_empty_list_when_file_is_missing(tmp_path) -> None:
    store = OutboxStore(tmp_path / "missing" / "messages.jsonl")

    assert store.list() == []


def test_outbox_store_finds_first_result_by_ticket_id(tmp_path) -> None:
    store = OutboxStore(tmp_path / "outbox" / "messages.jsonl")
    first = _send_result(ticket_id="ticket-1", message_id="mock-msg-1")
    second = _send_result(ticket_id="ticket-2", message_id="mock-msg-2")
    store.append(first)
    store.append(second)

    assert store.find_by_ticket_id(" ticket-1 ") == first
    assert store.find_by_ticket_id("ticket-missing") is None


def test_outbox_store_rejects_blank_ticket_lookup(tmp_path) -> None:
    store = OutboxStore(tmp_path / "outbox" / "messages.jsonl")

    with pytest.raises(ValueError, match="ticket_id cannot be blank"):
        store.find_by_ticket_id("   ")


def test_audit_log_store_records_and_reads_events(tmp_path) -> None:
    store = AuditLogStore(tmp_path / "logs" / "audit.jsonl")

    event = store.record(
        event_type="response_sent",
        ticket_id="ticket-1",
        details={"message_id": "mock-msg-1"},
    )

    assert event.event_type == "response_sent"
    assert event.ticket_id == "ticket-1"
    assert event.details == {"message_id": "mock-msg-1"}
    assert store.list() == [event]


def test_audit_log_store_appends_existing_event(tmp_path) -> None:
    store = AuditLogStore(tmp_path / "logs" / "audit.jsonl")
    event = AuditEvent(
        event_id="audit-test",
        event_type="workflow_started",
        ticket_id="ticket-1",
        details={"status": "new"},
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert store.append(event) == event
    assert store.list() == [event]


def test_audit_log_store_returns_empty_list_when_file_is_missing(tmp_path) -> None:
    store = AuditLogStore(tmp_path / "missing" / "audit.jsonl")

    assert store.list() == []


def _send_result(
    *,
    ticket_id: str,
    message_id: str = "mock-msg-test",
) -> SendResponseResult:
    return SendResponseResult(
        ticket_id=ticket_id,
        message_id=message_id,
        recipient="customer",
        message="Stored response.",
        sent_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
