"""Retrieval pipeline components."""

from support_agent.retrieval.chunking import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    chunk_documents,
    split_markdown_sections,
)
from support_agent.retrieval.embeddings import (
    DEFAULT_EMBEDDING_DIMENSIONS,
    LocalHashEmbeddings,
    get_embeddings,
)
from support_agent.retrieval.loader import load_markdown_documents
from support_agent.retrieval.retriever import (
    DEFAULT_KB_DIR,
    DEFAULT_TOP_K,
    KnowledgeBaseRetriever,
    build_kb_retriever,
    retrieve_relevant_chunks,
)
from support_agent.retrieval.vectorstore import build_in_memory_vectorstore

__all__ = [
    "DEFAULT_CHUNK_OVERLAP",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_EMBEDDING_DIMENSIONS",
    "DEFAULT_KB_DIR",
    "DEFAULT_TOP_K",
    "KnowledgeBaseRetriever",
    "LocalHashEmbeddings",
    "build_in_memory_vectorstore",
    "build_kb_retriever",
    "chunk_documents",
    "get_embeddings",
    "load_markdown_documents",
    "retrieve_relevant_chunks",
    "split_markdown_sections",
]
