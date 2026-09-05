"""Unit tests for application-facing ticket state persistence."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from support_agent.schemas import (
    HumanReviewAction,
    HumanReviewDecision,
    HumanReviewState,
    HumanReviewStatus,
    SupportTicket,
    TicketState,
    WorkflowStatus,
)
from support_agent.storage import TicketStateStore


def test_ticket_state_store_saves_and_loads_latest_state(tmp_path) -> None:
    store = TicketStateStore.from_path(tmp_path / "checkpoints.jsonl")
    initial_state = _state(ticket_id="ticket-1", status=WorkflowStatus.NEW)
    reviewed_state = _state(ticket_id="ticket-1", status=WorkflowStatus.REVIEWED)

    store.save(initial_state)
    latest_checkpoint = store.save(reviewed_state)

    assert latest_checkpoint.state == reviewed_state
    assert store.load("ticket-1") == reviewed_state
    assert store.status_for("ticket-1") == WorkflowStatus.REVIEWED


def test_ticket_state_store_persists_pending_review_status(tmp_path) -> None:
    store = TicketStateStore.from_path(tmp_path / "checkpoints.jsonl")
    state = _state(
        ticket_id="ticket-1",
        status=WorkflowStatus.WAITING_FOR_REVIEW,
        review=HumanReviewState(reason="High-risk account request."),
    )

    store.save(state)

    assert store.review_for("ticket-1") == state.review
    assert store.review_status_for("ticket-1") == HumanReviewStatus.PENDING


def test_ticket_state_store_persists_completed_review_status(tmp_path) -> None:
    store = TicketStateStore.from_path(tmp_path / "checkpoints.jsonl")
    review = HumanReviewState(
        status=HumanReviewStatus.APPROVED,
        reason="Billing request needs approval.",
        action=HumanReviewAction(
            decision=HumanReviewDecision.APPROVE,
            reviewer_id="agent-123",
        ),
    )
    state = _state(
        ticket_id="ticket-1",
        status=WorkflowStatus.REVIEWED,
        review=review,
    )

    store.save(state)

    assert store.review_for("ticket-1") == review
    assert store.review_status_for("ticket-1") == HumanReviewStatus.APPROVED


def test_ticket_state_store_returns_none_for_missing_ticket(tmp_path) -> None:
    store = TicketStateStore.from_path(tmp_path / "checkpoints.jsonl")

    assert store.load("ticket-missing") is None
    assert store.status_for("ticket-missing") is None
    assert store.review_for("ticket-missing") is None
    assert store.review_status_for("ticket-missing") is None


def test_ticket_state_store_rejects_blank_ticket_lookup(tmp_path) -> None:
    store = TicketStateStore.from_path(tmp_path / "checkpoints.jsonl")

    with pytest.raises(ValueError, match="ticket_id cannot be blank"):
        store.load("   ")


def _state(
    *,
    ticket_id: str,
    status: WorkflowStatus,
    review: HumanReviewState | None = None,
) -> TicketState:
    return TicketState(
        ticket=SupportTicket(
            ticket_id=ticket_id,
            message="Please help with this ticket.",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
        status=status,
        review=review,
    )
