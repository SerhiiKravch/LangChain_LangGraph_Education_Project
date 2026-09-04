"""Structured output schemas for grounded draft responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DraftCitation(BaseModel):
    """Reference to a knowledge-base chunk used in a draft response."""

    model_config = ConfigDict(str_strip_whitespace=True)

    document_id: str = Field(min_length=1, description="Knowledge-base document identifier.")
    title: str = Field(min_length=1, description="Human-readable source title.")
    section_title: str | None = Field(default=None, description="Optional source section title.")
    source: str | None = Field(default=None, description="Optional source path or URI.")


class DraftResponse(BaseModel):
    """Grounded response draft prepared from retrieved context."""

    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, description="Customer-facing draft response.")
    citations: list[DraftCitation] = Field(
        default_factory=list,
        description="Knowledge-base sources used to prepare the draft.",
    )
    needs_more_context: bool = Field(
        default=False,
        description="Whether the available context is insufficient for a confident answer.",
    )
    safety_notes: str | None = Field(
        default=None,
        description="Internal note about missing context, uncertainty, or sensitive actions.",
    )
