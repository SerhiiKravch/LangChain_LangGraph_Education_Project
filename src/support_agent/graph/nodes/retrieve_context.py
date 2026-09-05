"""Graph node for knowledge-base retrieval."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from support_agent.retrieval import DEFAULT_TOP_K, retrieve_relevant_chunks
from support_agent.schemas import SourceSnippet, TicketState, WorkflowStatus


def retrieve_context_node(
    state: TicketState,
    *,
    kb_dir: str | Path = "data/kb",
    k: int = DEFAULT_TOP_K,
) -> TicketState:
    """Retrieve relevant KB chunks and store serializable snippets in state."""
    chunks = retrieve_relevant_chunks(state.ticket.message, kb_dir=kb_dir, k=k)
    return state.model_copy(
        update={
            "retrieved_context": _documents_to_source_snippets(chunks),
            "status": WorkflowStatus.CONTEXT_RETRIEVED,
        }
    )


def _documents_to_source_snippets(documents: list[Document]) -> list[SourceSnippet]:
    """Convert retrieved LangChain documents into serializable source snippets."""
    snippets: list[SourceSnippet] = []
    for document in documents:
        content = document.page_content.strip()
        document_id = str(document.metadata.get("document_id", "")).strip()
        title = str(document.metadata.get("title", "")).strip()
        if not content or not document_id or not title:
            continue

        section_title = document.metadata.get("section_title")
        source = document.metadata.get("source")
        snippets.append(
            SourceSnippet(
                content=content,
                document_id=document_id,
                title=title,
                section_title=str(section_title) if section_title is not None else None,
                source=str(source) if source is not None else None,
                section_index=_optional_int(document.metadata.get("section_index")),
                chunk_index=_optional_int(document.metadata.get("chunk_index")),
            )
        )

    return snippets


def _optional_int(value: object) -> int | None:
    """Convert optional metadata values to integers when available."""
    if value is None:
        return None

    return int(value)
