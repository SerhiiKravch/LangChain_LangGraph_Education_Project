"""Unit tests for the retrieval foundation."""

from pathlib import Path

import pytest
from langchain_core.documents import Document

from support_agent.retrieval import (
    DEFAULT_EMBEDDING_DIMENSIONS,
    LocalHashEmbeddings,
    build_in_memory_vectorstore,
    build_kb_retriever,
    chunk_documents,
    load_markdown_documents,
    retrieve_relevant_chunks,
    split_markdown_sections,
)


def test_load_markdown_documents_reads_kb_metadata() -> None:
    documents = load_markdown_documents("data/kb")

    assert len(documents) == 5
    assert {document.metadata["document_id"] for document in documents} == {
        "account_deletion",
        "pricing",
        "rate_limits",
        "refunds",
        "subscriptions",
    }
    assert all(document.page_content for document in documents)
    assert all(Path(document.metadata["source"]).suffix == ".md" for document in documents)


def test_load_markdown_documents_rejects_missing_directory(tmp_path: Path) -> None:
    missing_dir = tmp_path / "missing-kb"

    with pytest.raises(FileNotFoundError):
        load_markdown_documents(missing_dir)


def test_split_markdown_sections_preserves_preface_and_headings() -> None:
    content = """
Preface before the first heading.

# First

First section content.

## Second

Second section content.
"""

    sections = split_markdown_sections(content)

    assert sections == [
        "Preface before the first heading.",
        "# First\n\nFirst section content.",
        "## Second\n\nSecond section content.",
    ]


def test_chunk_documents_adds_section_and_chunk_metadata() -> None:
    document = Document(
        page_content="# Policy\n\nAlpha beta gamma.\n\n## Details\n\nDelta epsilon zeta.",
        metadata={"document_id": "policy", "title": "Policy", "source": "policy.md"},
    )

    chunks = chunk_documents([document], chunk_size=40, chunk_overlap=8)

    assert chunks
    assert chunks[0].metadata["document_id"] == "policy"
    assert chunks[0].metadata["section_index"] == 0
    assert chunks[0].metadata["section_title"] == "Policy"
    assert chunks[0].metadata["chunk_index"] == 0


@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [
        (0, 0),
        (10, -1),
        (10, 10),
    ],
)
def test_chunk_documents_validates_chunk_parameters(
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    with pytest.raises(ValueError):
        chunk_documents([], chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def test_local_hash_embeddings_are_deterministic() -> None:
    embeddings = LocalHashEmbeddings(size=8)

    first = embeddings.embed_query("refund policy")
    second = embeddings.embed_query("refund policy")

    assert first == second
    assert len(first) == 8
    assert all(-1 <= value <= 1 for value in first)


def test_default_fake_embedding_dimensions(monkeypatch: pytest.MonkeyPatch) -> None:
    
    monkeypatch.delenv("EMBEDDINGS_PROVIDER", raising=False)
    monkeypatch.delenv("FAKE_EMBEDDING_DIMENSIONS", raising=False)

    embeddings = LocalHashEmbeddings(size=DEFAULT_EMBEDDING_DIMENSIONS)

    assert len(embeddings.embed_query("pricing")) == DEFAULT_EMBEDDING_DIMENSIONS


def test_in_memory_vectorstore_returns_top_k_documents() -> None:
    documents = [
        Document(page_content="Pricing and plans", metadata={"document_id": "pricing"}),
        Document(page_content="Refund policy", metadata={"document_id": "refunds"}),
        Document(page_content="Rate limit guidance", metadata={"document_id": "rate_limits"}),
    ]
    vectorstore = build_in_memory_vectorstore(documents)

    results = vectorstore.similarity_search("pricing", k=2)

    assert len(results) == 2
    assert all(isinstance(result, Document) for result in results)


def test_kb_retriever_handles_empty_query() -> None:
    retriever = build_kb_retriever()

    assert retriever.search("   ") == []


def test_retrieve_relevant_chunks_runs_full_pipeline() -> None:
    results = retrieve_relevant_chunks("How do API rate limits work?", k=3)

    assert len(results) == 3
    assert all(result.page_content for result in results)
    assert all("document_id" in result.metadata for result in results)
