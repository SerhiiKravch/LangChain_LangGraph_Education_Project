"""Mock send-response tool used to isolate workflow side effects."""

from __future__ import annotations

from hashlib import blake2b

from support_agent.schemas import DraftResponse, SendResponseResult, SupportTicket
from support_agent.storage import OutboxStore

DEFAULT_RECIPIENT = "customer"


def send_response(
    *,
    ticket: SupportTicket,
    draft: DraftResponse,
    recipient: str | None = None,
    outbox_store: OutboxStore | None = None,
) -> SendResponseResult:
    """Record a mocked customer response send operation."""
    target_recipient = (recipient or ticket.customer_id or DEFAULT_RECIPIENT).strip()
    if not target_recipient:
        raise ValueError("recipient cannot be blank")

    message = draft.message.strip()
    if not message:
        raise ValueError("draft message cannot be blank")

    result = SendResponseResult(
        ticket_id=ticket.ticket_id,
        message_id=_message_id(ticket_id=ticket.ticket_id, message=message),
        recipient=target_recipient,
        message=message,
    )
    return (outbox_store or OutboxStore()).append_once(result)


def _message_id(*, ticket_id: str, message: str) -> str:
    """Create a stable mock message id for deterministic tests."""
    digest = blake2b(f"{ticket_id}:{message}".encode("utf-8"), digest_size=8).hexdigest()
    return f"mock-msg-{digest}"
