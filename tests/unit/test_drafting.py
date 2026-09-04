"""Unit tests for grounded draft response generation."""

import pytest
from langchain_core.documents import Document
from pydantic import ValidationError

from support_agent.llm import build_draft_response_chain, draft_response
from support_agent.schemas import DraftCitation, DraftResponse, SourceSnippet, TicketCategory


def test_draft_response_uses_retrieved_context_and_sources() -> None:
    documents = [
        Document(
            page_content="# Rate Limits\n\nRate limits help protect system stability.",
            metadata={
                "document_id": "rate_limits",
                "title": "API Rate Limits",
                "section_title": "Rate Limits",
                "source": "data/kb/rate_limits.md",
                "section_index": 0,
                "chunk_index": 0,
            },
        )
    ]

    draft = draft_response(
        message="Why do I get rate limit errors?",
        category=TicketCategory.TECHNICAL,
        retrieved_context=documents,
    )

    assert draft.needs_more_context is False
    assert "technical request" in draft.message
    assert "Rate limits help protect system stability." in draft.message
    assert draft.citations == [
        DraftCitation(
            document_id="rate_limits",
            title="API Rate Limits",
            section_title="Rate Limits",
            source="data/kb/rate_limits.md",
        )
    ]
    assert draft.source_snippets == [
        SourceSnippet(
            content="# Rate Limits\n\nRate limits help protect system stability.",
            document_id="rate_limits",
            title="API Rate Limits",
            section_title="Rate Limits",
            source="data/kb/rate_limits.md",
            section_index=0,
            chunk_index=0,
        )
    ]


def test_draft_response_sets_needs_more_context_for_empty_context() -> None:
    draft = draft_response(
        message="Can you confirm my custom enterprise exception?",
        category="other",
        retrieved_context=[],
    )

    assert draft.needs_more_context is True
    assert draft.citations == []
    assert draft.source_snippets == []
    assert draft.safety_notes == "No retrieved context was provided for draft generation."


def test_draft_response_deduplicates_citations_by_document_and_section() -> None:
    documents = [
        Document(
            page_content="First chunk.",
            metadata={
                "document_id": "pricing",
                "title": "Pricing Plans",
                "section_title": "Team Plan",
            },
        ),
        Document(
            page_content="Second chunk.",
            metadata={
                "document_id": "pricing",
                "title": "Pricing Plans",
                "section_title": "Team Plan",
            },
        ),
    ]

    draft = draft_response(
        message="Tell me about Team plan pricing.",
        category="pricing",
        retrieved_context=documents,
    )

    assert len(draft.citations) == 1
    assert len(draft.source_snippets) == 2


def test_draft_response_ignores_sources_without_required_metadata() -> None:
    documents = [
        Document(page_content="Useful content.", metadata={}),
    ]

    draft = draft_response(
        message="What does the policy say?",
        category="other",
        retrieved_context=documents,
    )

    assert draft.citations == []
    assert draft.source_snippets == []
    assert "Useful content." in draft.message


def test_draft_response_chain_invokes_mapping_payload() -> None:
    chain = build_draft_response_chain()
    documents = [
        Document(
            page_content="Customers can cancel from the billing settings page.",
            metadata={
                "document_id": "subscriptions",
                "title": "Subscription Management",
            },
        )
    ]

    draft = chain.invoke(
        {
            "message": "How do I cancel my subscription?",
            "category": "account",
            "retrieved_context": documents,
        }
    )

    assert isinstance(draft, DraftResponse)
    assert draft.needs_more_context is False
    assert draft.citations[0].document_id == "subscriptions"


@pytest.mark.parametrize(
    "payload",
    [
        {"category": "pricing", "retrieved_context": []},
        {"message": "hello", "retrieved_context": []},
        {"message": "hello", "category": "pricing", "retrieved_context": object()},
    ],
)
def test_draft_response_chain_rejects_invalid_payload(payload: dict[str, object]) -> None:
    chain = build_draft_response_chain()

    with pytest.raises(TypeError):
        chain.invoke(payload)


def test_draft_response_rejects_unknown_category() -> None:
    with pytest.raises(ValueError):
        draft_response(
            message="What is this?",
            category="unknown",
            retrieved_context=[],
        )


def test_draft_response_schema_rejects_blank_message() -> None:
    with pytest.raises(ValidationError):
        DraftResponse(message="   ")
