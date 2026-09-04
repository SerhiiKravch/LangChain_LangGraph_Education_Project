"""Structured schemas for risk assessment and routing decisions."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(StrEnum):
    """Supported risk levels for support workflow decisions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RoutingDecision(StrEnum):
    """Supported routing decisions after risk assessment."""

    LOW_RISK_AUTO_SEND = "low_risk_auto_send"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    INSUFFICIENT_CONTEXT = "insufficient_context"


class RiskAssessment(BaseModel):
    """Structured result of a support-ticket risk assessment."""

    model_config = ConfigDict(str_strip_whitespace=True)

    risk_level: RiskLevel = Field(description="Overall risk level for the current ticket.")
    decision: RoutingDecision = Field(description="Workflow routing decision.")
    requires_human_review: bool = Field(
        description="Whether the workflow must pause for human review."
    )
    reasoning: str = Field(
        min_length=1,
        description="Short explanation of the risk decision.",
    )
