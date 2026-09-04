"""Draft response generation from retrieved knowledge-base context."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

from support_agent.schemas import DraftCitation, DraftResponse, SourceSnippet, TicketCategory

DraftInput = Mapping[str, object]


def build_draft_response_chain() -> RunnableLambda:
    """Build the local draft-response chain."""
    return RunnableLambda(_draft_response_from_mapping)


def draft_response(
    *,
    message: str,
    category: TicketCategory | str,
    retrieved_context: Iterable[Document],
) -> DraftResponse:
    """Create a grounded support response draft from retrieved context."""
    context_documents = list(retrieved_context)
    normalized_category = _normalize_category(category)

    if not context_documents:
        return DraftResponse(
            message=(
                "Thanks for reaching out. I do not have enough knowledge-base context "
                "to answer this confidently yet, so this should be reviewed by support."
            ),
            needs_more_context=True,
            safety_notes="No retrieved context was provided for draft generation.",
        )

    context_summary = _summarize_context(context_documents)
    citations = _build_citations(context_documents)
    source_snippets = _build_source_snippets(context_documents)

    return DraftResponse(
        message=(
            "Thanks for reaching out. Based on the available support documentation, "
            f"this looks like a {normalized_category.value} request.\n\n"
            f"{context_summary}\n\n"
            "Our support team can review the case details before any "
            "account-specific action is taken."
        ),
        citations=citations,
        source_snippets=source_snippets,
        needs_more_context=False,
    )


def _draft_response_from_mapping(payload: DraftInput) -> DraftResponse:
    """Adapter used by RunnableLambda."""
    message = payload.get("message")
    category = payload.get("category")
    retrieved_context = payload.get("retrieved_context", [])

    if not isinstance(message, str):
        raise TypeError("draft payload must include a string message")
    if not isinstance(category, TicketCategory | str):
        raise TypeError("draft payload must include a category string or TicketCategory")
    if not isinstance(retrieved_context, Iterable):
        raise TypeError("draft payload retrieved_context must be iterable")

    return draft_response(
        message=message,
        category=category,
        retrieved_context=retrieved_context,
    )


def _normalize_category(category: TicketCategory | str) -> TicketCategory:
    """Normalize supported category inputs to TicketCategory."""
    if isinstance(category, TicketCategory):
        return category

    return TicketCategory(category)


def _build_citations(documents: list[Document]) -> list[DraftCitation]:
    """Build unique citations from retrieved document metadata."""
    citations: list[DraftCitation] = []
    seen: set[tuple[str, str | None]] = set()

    for document in documents:
        document_id = str(document.metadata.get("document_id", "")).strip()
        title = str(document.metadata.get("title", "")).strip()
        section_title = document.metadata.get("section_title")
        source = document.metadata.get("source")

        if not document_id or not title:
            continue

        key = (document_id, str(section_title) if section_title is not None else None)
        if key in seen:
            continue

        seen.add(key)
        citations.append(
            DraftCitation(
                document_id=document_id,
                title=title,
                section_title=str(section_title) if section_title is not None else None,
                source=str(source) if source is not None else None,
            )
        )

    return citations


def _build_source_snippets(documents: list[Document]) -> list[SourceSnippet]:
    """Build serializable source snippets from retrieved document chunks."""
    snippets: list[SourceSnippet] = []

    for document in documents:
        content = document.page_content.strip()
        document_id = str(document.metadata.get("document_id", "")).strip()
        title = str(document.metadata.get("title", "")).strip()

        if not content or not document_id or not title:
            continue

        section_title = document.metadata.get("section_title")
        source = document.metadata.get("source")
        section_index = _optional_int(document.metadata.get("section_index"))
        chunk_index = _optional_int(document.metadata.get("chunk_index"))

        snippets.append(
            SourceSnippet(
                content=content,
                document_id=document_id,
                title=title,
                section_title=str(section_title) if section_title is not None else None,
                source=str(source) if source is not None else None,
                section_index=section_index,
                chunk_index=chunk_index,
            )
        )

    return snippets


def _summarize_context(documents: list[Document]) -> str:
    """Create a compact deterministic summary from retrieved chunks."""
    snippets = [_first_content_line(document.page_content) for document in documents]
    useful_snippets = [snippet for snippet in snippets if snippet]

    if not useful_snippets:
        return "The retrieved context exists, but it does not contain enough readable content."

    bullets = "\n".join(f"- {snippet}" for snippet in useful_snippets[:3])
    return f"Relevant documentation says:\n{bullets}"


def _first_content_line(text: str) -> str:
    """Return the first non-heading content line from a retrieved chunk."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped.removeprefix("- ").strip()

    return ""


def _optional_int(value: object) -> int | None:
    """Convert optional metadata values to integers when available."""
    if value is None:
        return None

    return int(value)
