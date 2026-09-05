"""Graph node for human-in-the-loop review interrupts."""

from __future__ import annotations

from typing import Any

from langgraph.types import interrupt

from support_agent.schemas import (
    HumanReviewAction,
    HumanReviewDecision,
    HumanReviewState,
    HumanReviewStatus,
    TicketState,
    WorkflowStatus,
)


def human_review_node(state: TicketState) -> TicketState:
    """Pause workflow execution until a human reviewer returns a decision."""
    if state.draft is None:
        raise ValueError("Cannot request human review before draft generation.")

    if state.risk_assessment is None:
        raise ValueError("Cannot request human review before risk assessment.")

    pending_review = HumanReviewState(reason=state.risk_assessment.reasoning)
    waiting_state = state.model_copy(
        update={
            "review": pending_review,
            "status": WorkflowStatus.WAITING_FOR_REVIEW,
        }
    )
    action_payload = interrupt(_build_review_interrupt_payload(waiting_state))
    action = HumanReviewAction.model_validate(action_payload)
    completed_review = pending_review.model_copy(
        update={
            "status": _review_status_from_decision(action.decision),
            "action": action,
        }
    )

    return waiting_state.model_copy(update={"review": completed_review})


def _build_review_interrupt_payload(state: TicketState) -> dict[str, Any]:
    """Build the serializable payload shown to a human reviewer."""
    return {
        "ticket": state.ticket.model_dump(mode="json"),
        "classification": (
            state.classification.model_dump(mode="json") if state.classification else None
        ),
        "draft": state.draft.model_dump(mode="json") if state.draft else None,
        "risk_assessment": (
            state.risk_assessment.model_dump(mode="json") if state.risk_assessment else None
        ),
        "review": state.review.model_dump(mode="json") if state.review else None,
    }


def _review_status_from_decision(decision: HumanReviewDecision) -> HumanReviewStatus:
    """Map reviewer decisions to stored review status."""
    if decision == HumanReviewDecision.APPROVE:
        return HumanReviewStatus.APPROVED

    if decision == HumanReviewDecision.EDIT:
        return HumanReviewStatus.EDITED

    if decision == HumanReviewDecision.REJECT:
        return HumanReviewStatus.REJECTED

    return HumanReviewStatus.NEEDS_MORE_CONTEXT
