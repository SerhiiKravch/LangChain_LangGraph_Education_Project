"""Integration tests for retry and resume persistence flows."""

from __future__ import annotations

from datetime import UTC, datetime

from support_agent.schemas import (
    DraftCitation,
    DraftResponse,
    HumanReviewAction,
    HumanReviewDecision,
    HumanReviewState,
    HumanReviewStatus,
    SendResponseResult,
    SupportTicket,
    TicketState,
    WorkflowStatus,
)
from support_agent.services import send_response_with_retry
from support_agent.storage import OutboxStore, TicketStateStore


def test_retry_send_flow_persists_successful_state_after_transient_failure(tmp_path) -> None:
    state_store = TicketStateStore.from_path(tmp_path / "checkpoints.jsonl")
    outbox_store = OutboxStore(tmp_path / "outbox.jsonl")
    state_store.save(_state(status=WorkflowStatus.REVIEWED))
    failures: list[int] = []

    def flaky_send(**kwargs) -> SendResponseResult:
        if not failures:
            failures.append(1)
            raise RuntimeError("temporary send failure")

        return _send_result(message=kwargs["draft"].message)

    restored_state = state_store.load("ticket-integration")
    assert restored_state is not None

    sent_state = send_response_with_retry(
        restored_state,
        outbox_store=outbox_store,
        send_callable=flaky_send,
    )
    state_store.save(sent_state)

    assert failures == [1]
    assert sent_state.status == WorkflowStatus.SENT
    assert sent_state.send_attempts == 2
    assert sent_state.send_result is not None
    assert state_store.status_for("ticket-integration") == WorkflowStatus.SENT
    assert state_store.load("ticket-integration") == sent_state


def test_resume_review_flow_persists_review_status_before_send_retry(tmp_path) -> None:
    state_store = TicketStateStore.from_path(tmp_path / "checkpoints.jsonl")
    outbox_store = OutboxStore(tmp_path / "outbox.jsonl")
    reviewed_state = _state(
        status=WorkflowStatus.REVIEWED,
        review=HumanReviewState(
            status=HumanReviewStatus.APPROVED,
            reason="High-risk ticket needs approval before sending.",
            action=HumanReviewAction(
                decision=HumanReviewDecision.APPROVE,
                reviewer_id="agent-123",
            ),
        ),
    )

    state_store.save(reviewed_state)

    assert state_store.review_status_for("ticket-integration") == HumanReviewStatus.APPROVED

    restored_state = state_store.load("ticket-integration")
    assert restored_state == reviewed_state

    sent_state = send_response_with_retry(restored_state, outbox_store=outbox_store)
    state_store.save(sent_state)

    assert sent_state.status == WorkflowStatus.SENT
    assert sent_state.review == reviewed_state.review
    assert sent_state.send_result is not None
    assert outbox_store.find_by_ticket_id("ticket-integration") == sent_state.send_result
    assert state_store.review_status_for("ticket-integration") == HumanReviewStatus.APPROVED


def _state(
    *,
    status: WorkflowStatus,
    review: HumanReviewState | None = None,
) -> TicketState:
    return TicketState(
        ticket=SupportTicket(
            ticket_id="ticket-integration",
            message="Please review and send this response.",
            customer_id="customer-123",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
        draft=DraftResponse(
            message="Prepared response for the customer.",
            citations=[
                DraftCitation(
                    document_id="pricing",
                    title="Pricing Plans",
                )
            ],
        ),
        review=review,
        status=status,
    )


def _send_result(*, message: str) -> SendResponseResult:
    return SendResponseResult(
        ticket_id="ticket-integration",
        message_id="mock-msg-integration",
        recipient="customer-123",
        message=message,
        sent_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
