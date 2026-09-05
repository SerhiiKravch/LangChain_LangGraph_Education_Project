"""Graph node for grounded draft response generation."""

from __future__ import annotations

from langchain_core.documents import Document

from support_agent.llm import draft_response
from support_agent.schemas import SourceSnippet, TicketCategory, TicketState, WorkflowStatus


def draft_response_node(state: TicketState) -> TicketState:
    """Generate a draft response from classification and retrieved context."""
    category = state.classification.category if state.classification else TicketCategory.OTHER
    draft = draft_response(
        message=state.ticket.message,
        category=category,
        retrieved_context=_source_snippets_to_documents(state.retrieved_context),
    )
    return state.model_copy(
        update={
            "draft": draft,
            "status": WorkflowStatus.DRAFTED,
        }
    )


def _source_snippets_to_documents(snippets: list[SourceSnippet]) -> list[Document]:
    """Convert stored source snippets back to LangChain documents for drafting."""
    return [
        Document(
            page_content=snippet.content,
            metadata={
                "document_id": snippet.document_id,
                "title": snippet.title,
                "section_title": snippet.section_title,
                "source": snippet.source,
                "section_index": snippet.section_index,
                "chunk_index": snippet.chunk_index,
            },
        )
        for snippet in snippets
    ]
