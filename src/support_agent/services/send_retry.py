"""Retry policy for send-response side effects."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from support_agent.schemas import (
    DraftResponse,
    SendResponseResult,
    SupportTicket,
    TicketState,
    WorkflowStatus,
)
from support_agent.storage import OutboxStore
from support_agent.tools import send_response

DEFAULT_MAX_SEND_ATTEMPTS = 3


class SendCallable(Protocol):
    """Callable interface for sending support responses."""

    def __call__(
        self,
        *,
        ticket: SupportTicket,
        draft: DraftResponse,
        recipient: str | None = None,
        outbox_store: OutboxStore | None = None,
    ) -> SendResponseResult:
        """Send a drafted support response."""


def send_response_with_retry(
    state: TicketState,
    *,
    max_attempts: int = DEFAULT_MAX_SEND_ATTEMPTS,
    recipient: str | None = None,
    outbox_store: OutboxStore | None = None,
    send_callable: SendCallable = send_response,
    on_failure: Callable[[Exception, int], None] | None = None,
) -> TicketState:
    """Send a drafted response with a bounded retry policy."""
    if max_attempts <= 0:
        raise ValueError("max_attempts must be greater than zero")

    if state.draft is None:
        raise ValueError("Cannot send response before draft generation.")

    attempts = state.send_attempts
    last_error: str | None = None
    for _ in range(max_attempts):
        attempts += 1
        try:
            result = send_callable(
                ticket=state.ticket,
                draft=state.draft,
                recipient=recipient,
                outbox_store=outbox_store,
            )
            return state.model_copy(
                update={
                    "send_attempts": attempts,
                    "send_result": result,
                    "status": WorkflowStatus.SENT,
                    "error": None,
                }
            )
        except Exception as exc:
            last_error = str(exc)
            if on_failure is not None:
                on_failure(exc, attempts)

    return state.model_copy(
        update={
            "send_attempts": attempts,
            "status": WorkflowStatus.FAILED,
            "error": last_error or "Send operation failed.",
        }
    )
