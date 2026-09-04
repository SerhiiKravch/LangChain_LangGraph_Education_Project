"""Utilities for splitting knowledge-base documents into chunks."""

from __future__ import annotations

import re
from collections.abc import Iterable

from langchain_core.documents import Document

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120
HEADING_PATTERN = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)


def chunk_documents(
    documents: Iterable[Document],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """Split loaded knowledge-base documents into overlapping chunks."""
    _validate_chunk_params(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks: list[Document] = []
    for document in documents:
        sections = split_markdown_sections(document.page_content)
        for section_index, section in enumerate(sections):
            section_title = _extract_section_title(section) or document.metadata.get(
                "title",
                "Untitled",
            )
            for chunk_index, chunk_text in enumerate(
                _chunk_text(section, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            ):
                metadata = {
                    **document.metadata,
                    "section_index": section_index,
                    "section_title": section_title,
                    "chunk_index": chunk_index,
                }
                chunks.append(Document(page_content=chunk_text, metadata=metadata))

    return chunks


def split_markdown_sections(content: str) -> list[str]:
    """Split a markdown document into sections keyed by headings."""
    stripped_content = content.strip()
    if not stripped_content:
        return []

    matches = list(HEADING_PATTERN.finditer(stripped_content))
    if not matches:
        return [stripped_content]

    sections: list[str] = []
    first_match = matches[0]
    if first_match.start() > 0:
        preface = stripped_content[: first_match.start()].strip()
        if preface:
            sections.append(preface)

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(stripped_content)
        section = stripped_content[start:end].strip()
        if section:
            sections.append(section)

    return sections


def _chunk_text(text: str, *, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into overlapping character chunks."""
    normalized = text.strip()
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    text_length = len(normalized)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length:
            split_at = normalized.rfind("\n\n", start, end)
            if split_at == -1 or split_at <= start:
                split_at = normalized.rfind("\n", start, end)
            if split_at != -1 and split_at > start:
                end = split_at

        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(end - chunk_overlap, start + 1)

    return chunks


def _extract_section_title(section: str) -> str | None:
    """Return the first heading line from a section, if present."""
    first_line = section.splitlines()[0].strip()
    if first_line.startswith("#"):
        return first_line.lstrip("#").strip() or None

    return None


def _validate_chunk_params(*, chunk_size: int, chunk_overlap: int) -> None:
    """Validate chunking parameters before processing documents."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
