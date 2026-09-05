"""Unit tests for send retry policy."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from support_agent.schemas import (
    DraftResponse,
    SendResponseResult,
    SupportTicket,
    TicketState,
    WorkflowStatus,
)
from support_agent.services import DEFAULT_MAX_SEND_ATTEMPTS, send_response_with_retry
from support_agent.storage import OutboxStore


def test_send_response_with_retry_marks_state_sent_on_success() -> None:
    state = _state()

    updated_state = send_response_with_retry(state, send_callable=_successful_send)

    assert updated_state.status == WorkflowStatus.SENT
    assert updated_state.send_attempts == 1
    assert updated_state.send_result is not None
    assert updated_state.send_result.ticket_id == "ticket-retry"
    assert updated_state.error is None


def test_send_response_with_retry_retries_until_success() -> None:
    state = _state()
    attempts: list[int] = []

    def flaky_send(**_kwargs) -> SendResponseResult:
        attempts.append(len(attempts) + 1)
        if len(attempts) < 3:
            raise RuntimeError("temporary send failure")

        return _send_result()

    updated_state = send_response_with_retry(state, send_callable=flaky_send)

    assert attempts == [1, 2, 3]
    assert updated_state.status == WorkflowStatus.SENT
    assert updated_state.send_attempts == 3
    assert updated_state.error is None


def test_send_response_with_retry_marks_state_failed_after_exhausting_retries() -> None:
    failures: list[tuple[str, int]] = []

    def failing_send(**_kwargs) -> SendResponseResult:
        raise RuntimeError("outbox unavailable")

    updated_state = send_response_with_retry(
        _state(),
        max_attempts=2,
        send_callable=failing_send,
        on_failure=lambda exc, attempt: failures.append((str(exc), attempt)),
    )

    assert failures == [("outbox unavailable", 1), ("outbox unavailable", 2)]
    assert updated_state.status == WorkflowStatus.FAILED
    assert updated_state.send_attempts == 2
    assert updated_state.send_result is None
    assert updated_state.error == "outbox unavailable"


def test_send_response_with_retry_continues_from_existing_attempt_count() -> None:
    state = _state().model_copy(update={"send_attempts": 2})

    updated_state = send_response_with_retry(state, send_callable=_successful_send)

    assert updated_state.status == WorkflowStatus.SENT
    assert updated_state.send_attempts == 3


def test_send_response_with_retry_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="max_attempts must be greater than zero"):
        send_response_with_retry(_state(), max_attempts=0)

    with pytest.raises(ValueError, match="before draft generation"):
        send_response_with_retry(_state().model_copy(update={"draft": None}))


def test_send_response_with_retry_preserves_idempotent_outbox_result(tmp_path) -> None:
    outbox_store = OutboxStore(tmp_path / "outbox.jsonl")
    state = _state()

    first_state = send_response_with_retry(state, outbox_store=outbox_store)
    second_state = send_response_with_retry(
        state.model_copy(
            update={
                "draft": DraftResponse(message="Changed response after first send."),
                "send_attempts": first_state.send_attempts,
            }
        ),
        outbox_store=outbox_store,
    )

    assert first_state.send_result is not None
    assert second_state.send_result == first_state.send_result
    assert second_state.send_attempts == 2
    assert outbox_store.list() == [first_state.send_result]


def test_default_max_send_attempts_is_three() -> None:
    assert DEFAULT_MAX_SEND_ATTEMPTS == 3


def _state() -> TicketState:
    return TicketState(
        ticket=SupportTicket(
            ticket_id="ticket-retry",
            message="Please send this response.",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
        draft=DraftResponse(message="Prepared response."),
    )


def _successful_send(**_kwargs) -> SendResponseResult:
    return _send_result()


def _send_result() -> SendResponseResult:
    return SendResponseResult(
        ticket_id="ticket-retry",
        message_id="mock-msg-retry",
        recipient="customer",
        message="Prepared response.",
        sent_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
