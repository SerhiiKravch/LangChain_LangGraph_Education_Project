"""Graph node for resuming workflow execution after human review."""

from __future__ import annotations

from support_agent.schemas import HumanReviewDecision, TicketState, WorkflowStatus


def resume_after_review_node(state: TicketState) -> TicketState:
    """Apply an approved or edited review decision before continuing workflow execution."""
    if state.draft is None:
        raise ValueError("Cannot resume review workflow before draft generation.")

    if state.review is None or state.review.action is None:
        raise ValueError("Cannot resume review workflow without a completed review action.")

    action = state.review.action
    if action.decision == HumanReviewDecision.APPROVE:
        return state.model_copy(update={"status": WorkflowStatus.REVIEWED})

    if action.decision == HumanReviewDecision.EDIT:
        reviewed_draft = state.draft.model_copy(update={"message": action.edited_message})
        return state.model_copy(
            update={
                "draft": reviewed_draft,
                "status": WorkflowStatus.REVIEWED,
            }
        )

    raise ValueError("Only approved or edited reviews can resume toward sending.")
