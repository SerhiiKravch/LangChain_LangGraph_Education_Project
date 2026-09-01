"""Embedding model setup for retrieval experiments."""

from __future__ import annotations

from hashlib import blake2b
import os

from langchain_core.embeddings import Embeddings

DEFAULT_EMBEDDING_DIMENSIONS = 256


def get_embeddings() -> Embeddings:
    """Return the configured embeddings implementation.

    Falls back to deterministic fake embeddings for local development when
    OpenAI embeddings are not available.
    """
    provider = os.getenv("EMBEDDINGS_PROVIDER", "fake").strip().lower()
    if provider == "openai":
        return _build_openai_embeddings()
    if provider == "fake":
        return LocalHashEmbeddings(size=_get_embedding_dimensions())

    msg = (
        "Unsupported EMBEDDINGS_PROVIDER value. "
        "Use 'fake' for local development or 'openai' for API-backed embeddings."
    )
    raise ValueError(msg)


def _build_openai_embeddings() -> Embeddings:
    """Create an OpenAI embeddings client when the optional dependency exists."""
    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError as exc:
        msg = (
            "OpenAI embeddings require the optional 'langchain-openai' package. "
            "Install it or set EMBEDDINGS_PROVIDER=fake."
        )
        raise RuntimeError(msg) from exc

    model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip()
    return OpenAIEmbeddings(model=model_name)


def _get_embedding_dimensions() -> int:
    """Return the fake-embedding dimensionality for local development."""
    raw_value = os.getenv("FAKE_EMBEDDING_DIMENSIONS", str(DEFAULT_EMBEDDING_DIMENSIONS)).strip()
    try:
        dimensions = int(raw_value)
    except ValueError as exc:
        raise ValueError("FAKE_EMBEDDING_DIMENSIONS must be an integer") from exc

    if dimensions <= 0:
        raise ValueError("FAKE_EMBEDDING_DIMENSIONS must be greater than zero")

    return dimensions


class LocalHashEmbeddings(Embeddings):
    """Deterministic lightweight embeddings for local development and tests."""

    def __init__(self, *, size: int) -> None:
        self.size = size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents with a stable hash-based projection."""
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query with the same projection as documents."""
        return self._embed_text(text)

    def _embed_text(self, text: str) -> list[float]:
        values: list[float] = []
        for index in range(self.size):
            digest = blake2b(f"{index}:{text}".encode("utf-8"), digest_size=8).digest()
            integer = int.from_bytes(digest, byteorder="big", signed=False)
            values.append((integer / ((1 << 64) - 1)) * 2 - 1)

        return values
