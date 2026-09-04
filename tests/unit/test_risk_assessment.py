"""Unit tests for risk assessment routing decisions."""

import pytest

from support_agent.schemas import (
    DraftCitation,
    DraftResponse,
    RiskLevel,
    RoutingDecision,
    TicketCategory,
    TicketClassification,
)
from support_agent.services import assess_risk


def test_assess_risk_routes_empty_context_to_insufficient_context() -> None:
    assessment = assess_risk(
        classification=_classification(TicketCategory.TECHNICAL, confidence=0.95),
        draft=DraftResponse(message="I need more context.", needs_more_context=True),
    )

    assert assessment.risk_level == RiskLevel.MEDIUM
    assert assessment.decision == RoutingDecision.INSUFFICIENT_CONTEXT
    assert assessment.requires_human_review is True


def test_assess_risk_routes_missing_citations_to_insufficient_context() -> None:
    assessment = assess_risk(
        classification=_classification(TicketCategory.PRICING, confidence=0.95),
        draft=DraftResponse(message="Pricing answer without sources."),
    )

    assert assessment.risk_level == RiskLevel.MEDIUM
    assert assessment.decision == RoutingDecision.INSUFFICIENT_CONTEXT
    assert assessment.requires_human_review is True


@pytest.mark.parametrize(
    "category",
    [
        TicketCategory.ACCOUNT,
        TicketCategory.BILLING,
        TicketCategory.REFUND,
    ],
)
def test_assess_risk_routes_high_risk_categories_to_human_review(
    category: TicketCategory,
) -> None:
    assessment = assess_risk(
        classification=_classification(category, confidence=0.95),
        draft=_grounded_draft(),
    )

    assert assessment.risk_level == RiskLevel.HIGH
    assert assessment.decision == RoutingDecision.NEEDS_HUMAN_REVIEW
    assert assessment.requires_human_review is True


@pytest.mark.parametrize(
    "category",
    [
        TicketCategory.PRICING,
        TicketCategory.TECHNICAL,
    ],
)
def test_assess_risk_allows_low_risk_high_confidence_auto_send(
    category: TicketCategory,
) -> None:
    assessment = assess_risk(
        classification=_classification(category, confidence=0.9),
        draft=_grounded_draft(),
    )

    assert assessment.risk_level == RiskLevel.LOW
    assert assessment.decision == RoutingDecision.LOW_RISK_AUTO_SEND
    assert assessment.requires_human_review is False


def test_assess_risk_routes_low_confidence_low_risk_category_to_review() -> None:
    assessment = assess_risk(
        classification=_classification(TicketCategory.PRICING, confidence=0.6),
        draft=_grounded_draft(),
    )

    assert assessment.risk_level == RiskLevel.MEDIUM
    assert assessment.decision == RoutingDecision.NEEDS_HUMAN_REVIEW
    assert assessment.requires_human_review is True


def test_assess_risk_routes_other_category_to_review() -> None:
    assessment = assess_risk(
        classification=_classification(TicketCategory.OTHER, confidence=0.9),
        draft=_grounded_draft(),
    )

    assert assessment.risk_level == RiskLevel.MEDIUM
    assert assessment.decision == RoutingDecision.NEEDS_HUMAN_REVIEW
    assert assessment.requires_human_review is True


def _classification(
    category: TicketCategory,
    *,
    confidence: float,
) -> TicketClassification:
    return TicketClassification(
        category=category,
        confidence=confidence,
        reasoning=f"Fixture classification for {category.value}.",
    )


def _grounded_draft() -> DraftResponse:
    return DraftResponse(
        message="Grounded draft response.",
        citations=[
            DraftCitation(
                document_id="pricing",
                title="Pricing Plans",
            )
        ],
    )
