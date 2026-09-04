"""Application-facing retriever interface for the knowledge base."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document

from support_agent.retrieval.chunking import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    chunk_documents,
)
from support_agent.retrieval.loader import load_markdown_documents
from support_agent.retrieval.vectorstore import (
    SimpleInMemoryVectorStore,
    build_in_memory_vectorstore,
)

DEFAULT_KB_DIR = Path("data/kb")
DEFAULT_TOP_K = 4


@dataclass(slots=True)
class KnowledgeBaseRetriever:
    """Thin retrieval layer wrapping vector search over KB chunks."""

    vectorstore: SimpleInMemoryVectorStore

    @classmethod
    def from_kb_dir(
        cls,
        kb_dir: str | Path = DEFAULT_KB_DIR,
        *,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> KnowledgeBaseRetriever:
        """Build a retriever from markdown knowledge-base documents."""
        documents = load_markdown_documents(kb_dir)
        chunks = chunk_documents(
            documents,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        vectorstore = build_in_memory_vectorstore(chunks)
        return cls(vectorstore=vectorstore)

    def search(self, query: str, *, k: int = DEFAULT_TOP_K) -> list[Document]:
        """Return the top-k most relevant knowledge-base chunks."""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        return self.vectorstore.similarity_search(normalized_query, k=k)


def build_kb_retriever(
    kb_dir: str | Path = DEFAULT_KB_DIR,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> KnowledgeBaseRetriever:
    """Build the default knowledge-base retriever."""
    return KnowledgeBaseRetriever.from_kb_dir(
        kb_dir=kb_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def retrieve_relevant_chunks(
    query: str,
    *,
    kb_dir: str | Path = DEFAULT_KB_DIR,
    k: int = DEFAULT_TOP_K,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """Run the full retrieval pipeline in one call."""
    retriever = build_kb_retriever(
        kb_dir=kb_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return retriever.search(query, k=k)
