"""Unit tests for resuming workflow execution after human review."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from support_agent.graph import resume_after_review_node
from support_agent.schemas import (
    DraftCitation,
    DraftResponse,
    HumanReviewAction,
    HumanReviewDecision,
    HumanReviewState,
    HumanReviewStatus,
    SupportTicket,
    TicketState,
    WorkflowStatus,
)


def test_resume_after_review_keeps_approved_draft() -> None:
    state = _reviewed_state(
        action=HumanReviewAction(
            decision=HumanReviewDecision.APPROVE,
            reviewer_id="agent-123",
        ),
        status=HumanReviewStatus.APPROVED,
    )

    updated_state = resume_after_review_node(state)

    assert updated_state.status == WorkflowStatus.REVIEWED
    assert updated_state.draft == state.draft


def test_resume_after_review_applies_edited_message_to_draft() -> None:
    edited_message = "Reviewer-approved edited response."
    state = _reviewed_state(
        action=HumanReviewAction(
            decision=HumanReviewDecision.EDIT,
            reviewer_id="agent-123",
            edited_message=edited_message,
        ),
        status=HumanReviewStatus.EDITED,
    )

    updated_state = resume_after_review_node(state)

    assert updated_state.status == WorkflowStatus.REVIEWED
    assert updated_state.draft is not None
    assert updated_state.draft.message == edited_message
    assert updated_state.draft.citations == state.draft.citations


@pytest.mark.parametrize(
    ("action", "status"),
    [
        (
            HumanReviewAction(
                decision=HumanReviewDecision.REJECT,
                reviewer_id="agent-123",
                feedback="Do not send this response.",
            ),
            HumanReviewStatus.REJECTED,
        ),
        (
            HumanReviewAction(
                decision=HumanReviewDecision.REQUEST_MORE_CONTEXT,
                reviewer_id="agent-123",
                feedback="Retrieve more account policy context.",
            ),
            HumanReviewStatus.NEEDS_MORE_CONTEXT,
        ),
    ],
)
def test_resume_after_review_rejects_non_sendable_decisions(
    action: HumanReviewAction,
    status: HumanReviewStatus,
) -> None:
    with pytest.raises(ValueError, match="approved or edited"):
        resume_after_review_node(_reviewed_state(action=action, status=status))


def test_resume_after_review_requires_draft_and_completed_review() -> None:
    state = _reviewed_state(
        action=HumanReviewAction(
            decision=HumanReviewDecision.APPROVE,
            reviewer_id="agent-123",
        ),
        status=HumanReviewStatus.APPROVED,
    )

    with pytest.raises(ValueError, match="before draft generation"):
        resume_after_review_node(state.model_copy(update={"draft": None}))

    with pytest.raises(ValueError, match="completed review action"):
        resume_after_review_node(state.model_copy(update={"review": None}))

    with pytest.raises(ValueError, match="completed review action"):
        resume_after_review_node(
            state.model_copy(update={"review": HumanReviewState(reason="Needs review.")})
        )


def _reviewed_state(
    *,
    action: HumanReviewAction,
    status: HumanReviewStatus,
) -> TicketState:
    return TicketState(
        ticket=SupportTicket(
            ticket_id="ticket-review",
            message="Please review this draft.",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
        draft=DraftResponse(
            message="Original drafted response.",
            citations=[
                DraftCitation(
                    document_id="pricing",
                    title="Pricing Plans",
                )
            ],
        ),
        review=HumanReviewState(
            status=status,
            reason="Risk policy requires human review.",
            action=action,
        ),
        status=WorkflowStatus.WAITING_FOR_REVIEW,
    )
