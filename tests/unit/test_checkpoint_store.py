"""Unit tests for graph checkpoint storage."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from support_agent.schemas import SupportTicket, TicketState, WorkflowStatus
from support_agent.storage import CheckpointStore, StateCheckpoint


def test_checkpoint_store_saves_and_reads_state_snapshots(tmp_path) -> None:
    store = CheckpointStore(tmp_path / "traces" / "checkpoints.jsonl")
    state = _state(ticket_id="ticket-1", status=WorkflowStatus.CLASSIFIED)

    checkpoint = store.save(state)

    assert checkpoint.checkpoint_id.startswith("checkpoint-")
    assert checkpoint.ticket_id == "ticket-1"
    assert checkpoint.status == WorkflowStatus.CLASSIFIED
    assert checkpoint.state == state
    assert store.list() == [checkpoint]


def test_checkpoint_store_loads_latest_state_for_ticket(tmp_path) -> None:
    store = CheckpointStore(tmp_path / "traces" / "checkpoints.jsonl")
    first = store.save(_state(ticket_id="ticket-1", status=WorkflowStatus.NEW))
    second = store.save(_state(ticket_id="ticket-1", status=WorkflowStatus.DRAFTED))
    store.save(_state(ticket_id="ticket-2", status=WorkflowStatus.CLASSIFIED))

    assert store.latest("ticket-1") == second
    assert store.load_latest("ticket-1") == second.state
    assert store.load_latest("ticket-1") != first.state


def test_checkpoint_store_filters_by_ticket_id(tmp_path) -> None:
    store = CheckpointStore(tmp_path / "traces" / "checkpoints.jsonl")
    ticket_one_checkpoint = store.save(_state(ticket_id="ticket-1"))
    store.save(_state(ticket_id="ticket-2"))

    assert store.list(ticket_id=" ticket-1 ") == [ticket_one_checkpoint]
    assert store.list(ticket_id="ticket-missing") == []


def test_checkpoint_store_returns_empty_values_when_file_is_missing(tmp_path) -> None:
    store = CheckpointStore(tmp_path / "missing" / "checkpoints.jsonl")

    assert store.list() == []
    assert store.latest("ticket-1") is None
    assert store.load_latest("ticket-1") is None


def test_checkpoint_store_rejects_blank_ticket_lookup(tmp_path) -> None:
    store = CheckpointStore(tmp_path / "traces" / "checkpoints.jsonl")

    with pytest.raises(ValueError, match="ticket_id cannot be blank"):
        store.list(ticket_id="   ")


def test_checkpoint_store_appends_existing_checkpoint(tmp_path) -> None:
    store = CheckpointStore(tmp_path / "traces" / "checkpoints.jsonl")
    checkpoint = StateCheckpoint(
        checkpoint_id="checkpoint-test",
        ticket_id="ticket-1",
        status=WorkflowStatus.NEW,
        state=_state(ticket_id="ticket-1"),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert store.append(checkpoint) == checkpoint
    assert store.list() == [checkpoint]


def _state(
    *,
    ticket_id: str,
    status: WorkflowStatus = WorkflowStatus.NEW,
) -> TicketState:
    return TicketState(
        ticket=SupportTicket(
            ticket_id=ticket_id,
            message="Can you help with my support request?",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
        status=status,
    )
