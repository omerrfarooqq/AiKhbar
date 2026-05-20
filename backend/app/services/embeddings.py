"""Sentence embedding service.

Wraps a multilingual SentenceTransformers model. The default
`intfloat/multilingual-e5-base` handles Urdu and English well, which matters
because scraped articles are Urdu while some editorials/discussions are English.

E5 models expect prefixes: "query: " for search queries and "passage: " for
indexed documents. We apply them automatically.
"""
from __future__ import annotations

import numpy as np
from loguru import logger

from app.core.config import settings

# Imported lazily inside _load() — sentence-transformers + torch are heavy.
_model = None


def _load():  # noqa: ANN202
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        logger.info("Loading embedding model: {}", settings.embedding_model)
        _model = SentenceTransformer(
            settings.embedding_model, device=settings.embedding_device
        )
    return _model


class EmbeddingService:
    """Encodes text into normalised vectors for FAISS similarity search."""

    def __init__(self) -> None:
        self._is_e5 = "e5" in settings.embedding_model.lower()

    @property
    def dimension(self) -> int:
        return _load().get_sentence_embedding_dimension()

    def _prefix(self, texts: list[str], kind: str) -> list[str]:
        if not self._is_e5:
            return texts
        tag = "query: " if kind == "query" else "passage: "
        return [tag + t for t in texts]

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """Embed passages for indexing. Returns an (n, dim) float32 array."""
        prepared = self._prefix(texts, "passage")
        vecs = _load().encode(
            prepared, normalize_embeddings=True, show_progress_bar=False
        )
        return np.asarray(vecs, dtype="float32")

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a single search query. Returns a (1, dim) float32 array."""
        prepared = self._prefix([text], "query")
        vec = _load().encode(
            prepared, normalize_embeddings=True, show_progress_bar=False
        )
        return np.asarray(vec, dtype="float32")


_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service
