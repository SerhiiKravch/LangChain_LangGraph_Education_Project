"""Structured output schemas for ticket classification."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from support_agent.schemas.ticket import TicketCategory


class TicketClassification(BaseModel):
    """Structured classification result returned by the classifier."""

    model_config = ConfigDict(str_strip_whitespace=True)

    category: TicketCategory = Field(description="Best matching support request category.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Classifier confidence from 0.0 to 1.0.",
    )
    reasoning: str = Field(
        min_length=1,
        description="Short explanation of why the category was selected.",
    )
