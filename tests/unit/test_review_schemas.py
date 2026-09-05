"""Unit tests for human review schemas."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from support_agent.schemas import (
    HumanReviewAction,
    HumanReviewDecision,
    HumanReviewState,
    HumanReviewStatus,
)


def test_human_review_state_defaults_to_pending() -> None:
    review = HumanReviewState(reason="Billing tickets require manual approval.")

    assert review.status == HumanReviewStatus.PENDING
    assert review.reason == "Billing tickets require manual approval."
    assert review.action is None
    assert isinstance(review.requested_at, datetime)


def test_human_review_action_allows_approve_without_extra_details() -> None:
    action = HumanReviewAction(
        decision=HumanReviewDecision.APPROVE,
        reviewer_id="agent-123",
    )

    assert action.decision == HumanReviewDecision.APPROVE
    assert action.reviewer_id == "agent-123"
    assert isinstance(action.reviewed_at, datetime)


def test_human_review_action_requires_edited_message_for_edit() -> None:
    with pytest.raises(ValidationError, match="edited_message is required"):
        HumanReviewAction(
            decision=HumanReviewDecision.EDIT,
            reviewer_id="agent-123",
        )


@pytest.mark.parametrize(
    "decision",
    [
        HumanReviewDecision.REJECT,
        HumanReviewDecision.REQUEST_MORE_CONTEXT,
    ],
)
def test_human_review_action_requires_feedback_for_blocking_decisions(
    decision: HumanReviewDecision,
) -> None:
    with pytest.raises(ValidationError, match="feedback is required"):
        HumanReviewAction(
            decision=decision,
            reviewer_id="agent-123",
        )


def test_human_review_state_can_store_completed_action() -> None:
    action = HumanReviewAction(
        decision=HumanReviewDecision.EDIT,
        reviewer_id="agent-123",
        edited_message="Updated response approved by support.",
    )
    review = HumanReviewState(
        status=HumanReviewStatus.EDITED,
        reason="Refund request needs approval.",
        action=action,
    )

    assert review.status == HumanReviewStatus.EDITED
    assert review.action == action
