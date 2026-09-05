"""Workflow state model for LangGraph execution."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from support_agent.schemas.classification import TicketClassification
from support_agent.schemas.draft import DraftResponse, SourceSnippet
from support_agent.schemas.review import HumanReviewState
from support_agent.schemas.risk import RiskAssessment
from support_agent.schemas.ticket import SupportTicket


class WorkflowStatus(StrEnum):
    """Supported lifecycle statuses for a support ticket workflow."""

    NEW = "new"
    CLASSIFIED = "classified"
    CONTEXT_RETRIEVED = "context_retrieved"
    DRAFTED = "drafted"
    RISK_ASSESSED = "risk_assessed"
    WAITING_FOR_REVIEW = "waiting_for_review"
    SENT = "sent"
    CLOSED = "closed"
    FAILED = "failed"


class TicketState(BaseModel):
    """State carried across LangGraph workflow nodes."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    ticket: SupportTicket = Field(description="Normalized ticket being processed.")
    status: WorkflowStatus = Field(
        default=WorkflowStatus.NEW,
        description="Current workflow lifecycle status.",
    )
    classification: TicketClassification | None = Field(
        default=None,
        description="Ticket classification produced by the classification node.",
    )
    retrieved_context: list[SourceSnippet] = Field(
        default_factory=list,
        description="Retrieved source snippets stored for drafting and review.",
    )
    draft: DraftResponse | None = Field(
        default=None,
        description="Grounded draft response prepared from retrieved context.",
    )
    risk_assessment: RiskAssessment | None = Field(
        default=None,
        description="Risk assessment used for routing.",
    )
    review: HumanReviewState | None = Field(
        default=None,
        description="Human review state when workflow execution is paused for review.",
    )
    send_attempts: int = Field(
        default=0,
        ge=0,
        description="Number of attempted send operations.",
    )
    error: str | None = Field(
        default=None,
        description="Latest workflow error, if execution failed.",
    )
