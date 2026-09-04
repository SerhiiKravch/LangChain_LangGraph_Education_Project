"""Ticket schemas used as workflow inputs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TicketCategory(StrEnum):
    """Supported high-level support ticket categories."""

    BILLING = "billing"
    REFUND = "refund"
    ACCOUNT = "account"
    TECHNICAL = "technical"
    PRICING = "pricing"
    OTHER = "other"


class TicketInput(BaseModel):
    """Raw user-provided ticket input."""

    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, description="Incoming customer support request.")
    customer_id: str | None = Field(default=None, description="Optional customer identifier.")


class SupportTicket(BaseModel):
    """Normalized support ticket used by the workflow."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ticket_id: str = Field(min_length=1, description="Stable ticket identifier.")
    message: str = Field(min_length=1, description="Incoming customer support request.")
    customer_id: str | None = Field(default=None, description="Optional customer identifier.")
    created_at: datetime = Field(description="Ticket creation timestamp.")
