"""Schemas for controlled response sending side effects."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SendStatus(StrEnum):
    """Supported statuses for a send-response operation."""

    SENT = "sent"


class SendResponseResult(BaseModel):
    """Result returned after a response is sent through a tool boundary."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ticket_id: str = Field(min_length=1, description="Ticket identifier used for sending.")
    message_id: str = Field(min_length=1, description="Generated outbound message identifier.")
    recipient: str = Field(min_length=1, description="Target recipient identifier.")
    message: str = Field(min_length=1, description="Customer-facing message that was sent.")
    status: SendStatus = Field(default=SendStatus.SENT, description="Send operation status.")
    sent_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the send operation was recorded.",
    )
