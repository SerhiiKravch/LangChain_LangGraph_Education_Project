"""Human review schemas for workflow interrupts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HumanReviewStatus(StrEnum):
    """Supported lifecycle states for a human review request."""

    PENDING = "pending"
    APPROVED = "approved"
    EDITED = "edited"
    REJECTED = "rejected"
    NEEDS_MORE_CONTEXT = "needs_more_context"


class HumanReviewDecision(StrEnum):
    """Supported actions a reviewer can take on a drafted response."""

    APPROVE = "approve"
    EDIT = "edit"
    REJECT = "reject"
    REQUEST_MORE_CONTEXT = "request_more_context"


class HumanReviewAction(BaseModel):
    """A reviewer decision captured after a workflow pause."""

    model_config = ConfigDict(str_strip_whitespace=True)

    decision: HumanReviewDecision = Field(description="Reviewer action.")
    reviewer_id: str = Field(min_length=1, description="Identifier for the human reviewer.")
    feedback: str | None = Field(
        default=None,
        description="Optional reviewer feedback or rejection reason.",
    )
    edited_message: str | None = Field(
        default=None,
        description="Reviewer-edited customer response, required for edit decisions.",
    )
    reviewed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the review decision was captured.",
    )

    @model_validator(mode="after")
    def validate_decision_details(self) -> Self:
        """Require the fields needed to safely resume the workflow."""
        if self.decision == HumanReviewDecision.EDIT and not self.edited_message:
            raise ValueError("edited_message is required for edit review decisions")

        if self.decision in {
            HumanReviewDecision.REJECT,
            HumanReviewDecision.REQUEST_MORE_CONTEXT,
        } and not self.feedback:
            raise ValueError("feedback is required for this review decision")

        return self


class HumanReviewState(BaseModel):
    """Human review state stored inside the ticket workflow state."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: HumanReviewStatus = Field(
        default=HumanReviewStatus.PENDING,
        description="Current human review status.",
    )
    reason: str = Field(
        min_length=1,
        description="Why this ticket needs human review.",
    )
    requested_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when human review was requested.",
    )
    action: HumanReviewAction | None = Field(
        default=None,
        description="Reviewer action after review is completed.",
    )
