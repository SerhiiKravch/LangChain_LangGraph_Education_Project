"""Utilities for loading markdown knowledge-base documents."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document


def load_markdown_documents(kb_dir: str | Path) -> list[Document]:
    """Load markdown documents from the knowledge-base directory."""
    kb_path = Path(kb_dir).expanduser().resolve()
    if not kb_path.exists():
        msg = f"Knowledge base directory does not exist: {kb_path}"
        raise FileNotFoundError(msg)

    if not kb_path.is_dir():
        msg = f"Knowledge base path is not a directory: {kb_path}"
        raise NotADirectoryError(msg)

    documents: list[Document] = []
    for file_path in sorted(kb_path.glob("*.md")):
        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "filename": file_path.name,
                    "document_id": file_path.stem,
                    "title": _extract_title(content, file_path.stem),
                },
            )
        )

    return documents


def _extract_title(content: str, fallback: str) -> str:
    """Extract the first markdown heading or fall back to the file stem."""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback

    return fallback
