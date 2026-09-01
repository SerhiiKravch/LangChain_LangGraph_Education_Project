"""Vector store setup for retrieval experiments."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import sqrt

from langchain_core.documents import Document

from support_agent.retrieval.embeddings import get_embeddings


@dataclass(slots=True)
class SimpleInMemoryVectorStore:
    """A lightweight in-memory vector store for local retrieval experiments."""

    documents: list[Document]
    vectors: list[list[float]]

    def similarity_search(self, query: str, *, k: int = 4) -> list[Document]:
        """Return the top-k documents by cosine similarity."""
        if k <= 0:
            return []

        query_vector = get_embeddings().embed_query(query)
        scored_documents = [
            (document, _cosine_similarity(query_vector, vector))
            for document, vector in zip(self.documents, self.vectors, strict=True)
        ]
        scored_documents.sort(key=lambda item: item[1], reverse=True)
        return [document for document, _score in scored_documents[:k]]


def build_in_memory_vectorstore(documents: Iterable[Document]) -> SimpleInMemoryVectorStore:
    """Create an in-memory vector store from chunked documents."""
    materialized_documents = list(documents)
    embedding_model = get_embeddings()
    vectors = embedding_model.embed_documents([document.page_content for document in materialized_documents])
    return SimpleInMemoryVectorStore(documents=materialized_documents, vectors=vectors)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    """Compute cosine similarity without requiring external numeric packages."""
    numerator = sum(left_value * right_value for left_value, right_value in zip(left, right, strict=True))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    return numerator / (left_norm * right_norm)
