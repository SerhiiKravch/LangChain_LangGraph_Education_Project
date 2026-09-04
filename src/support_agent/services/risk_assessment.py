"""Risk assessment policy for support workflow routing."""

from __future__ import annotations

from support_agent.schemas import (
    DraftResponse,
    RiskAssessment,
    RiskLevel,
    RoutingDecision,
    TicketCategory,
    TicketClassification,
)

HIGH_RISK_CATEGORIES = frozenset(
    {
        TicketCategory.ACCOUNT,
        TicketCategory.BILLING,
        TicketCategory.REFUND,
    }
)
LOW_RISK_AUTO_SEND_CATEGORIES = frozenset(
    {
        TicketCategory.PRICING,
        TicketCategory.TECHNICAL,
    }
)
HIGH_CONFIDENCE_THRESHOLD = 0.8


def assess_risk(
    *,
    classification: TicketClassification,
    draft: DraftResponse,
) -> RiskAssessment:
    """Assess whether a drafted response can be sent automatically."""
    if draft.needs_more_context or not draft.citations:
        return RiskAssessment(
            risk_level=RiskLevel.MEDIUM,
            decision=RoutingDecision.INSUFFICIENT_CONTEXT,
            requires_human_review=True,
            reasoning="Draft response does not have enough grounded context for auto-send.",
        )

    if classification.category in HIGH_RISK_CATEGORIES:
        return RiskAssessment(
            risk_level=RiskLevel.HIGH,
            decision=RoutingDecision.NEEDS_HUMAN_REVIEW,
            requires_human_review=True,
            reasoning=(
                f"{classification.category.value} requests may involve sensitive "
                "account or money-related actions."
            ),
        )

    if (
        classification.category in LOW_RISK_AUTO_SEND_CATEGORIES
        and classification.confidence >= HIGH_CONFIDENCE_THRESHOLD
    ):
        return RiskAssessment(
            risk_level=RiskLevel.LOW,
            decision=RoutingDecision.LOW_RISK_AUTO_SEND,
            requires_human_review=False,
            reasoning="Low-risk category with high confidence and grounded draft context.",
        )

    return RiskAssessment(
        risk_level=RiskLevel.MEDIUM,
        decision=RoutingDecision.NEEDS_HUMAN_REVIEW,
        requires_human_review=True,
        reasoning="Ticket is not eligible for auto-send under the current risk policy.",
    )
