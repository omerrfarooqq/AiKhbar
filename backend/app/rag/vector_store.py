"""FAISS-backed vector store.

A thin, persistent wrapper around a FAISS index plus a parallel JSON metadata
list. Vectors are L2-normalised, so an inner-product index (IndexFlatIP) yields
cosine similarity. The index is loaded once and persisted to disk after writes.

This is intentionally simple (flat index) — correct and fast enough for an MVP.
For large-scale corpora swap IndexFlatIP for an IVF/HNSW index behind the same
interface.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from loguru import logger

from app.core.config import settings


class FaissVectorStore:
    """Persistent FAISS index with id-aligned metadata."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self._index_path = Path(settings.faiss_index_path)
        self._meta_path = Path(settings.faiss_meta_path)
        self._lock = threading.Lock()
        self._index: faiss.Index
        self._meta: list[dict[str, Any]] = []
        self._load_or_create()

    def _load_or_create(self) -> None:
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        if self._index_path.exists() and self._meta_path.exists():
            self._index = faiss.read_index(str(self._index_path))
            self._meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
            logger.info("FAISS index loaded | vectors={}", self._index.ntotal)
        else:
            # IndexIDMap lets us attach stable integer ids to vectors.
            self._index = faiss.IndexIDMap(faiss.IndexFlatIP(self.dimension))
            self._meta = []
            logger.info("FAISS index created | dim={}", self.dimension)

    def _persist(self) -> None:
        faiss.write_index(self._index, str(self._index_path))
        self._meta_path.write_text(
            json.dumps(self._meta, ensure_ascii=False), encoding="utf-8"
        )

    @property
    def size(self) -> int:
        return int(self._index.ntotal)

    def add(self, vectors: np.ndarray, metadatas: list[dict[str, Any]]) -> None:
        """Add vectors with aligned metadata. Each metadata dict is one chunk."""
        if len(vectors) == 0:
            return
        with self._lock:
            start_id = len(self._meta)
            ids = np.arange(start_id, start_id + len(vectors), dtype="int64")
            self._index.add_with_ids(vectors.astype("float32"), ids)
            self._meta.extend(metadatas)
            self._persist()
        logger.info("FAISS add | +{} | total={}", len(vectors), self.size)

    def search(
        self, query_vector: np.ndarray, k: int = 5, category: str | None = None
    ) -> list[tuple[dict[str, Any], float]]:
        """Return up to k (metadata, score) pairs ranked by cosine similarity.

        `category` applies a post-filter; we over-fetch to compensate.
        """
        if self.size == 0:
            return []
        fetch_k = k * 5 if category else k
        scores, ids = self._index.search(
            query_vector.astype("float32"), min(fetch_k, self.size)
        )
        results: list[tuple[dict[str, Any], float]] = []
        for idx, score in zip(ids[0], scores[0], strict=True):
            if idx == -1:
                continue
            meta = self._meta[int(idx)]
            if category and meta.get("category") != category:
                continue
            results.append((meta, float(score)))
            if len(results) >= k:
                break
        return results


_store: FaissVectorStore | None = None


def get_vector_store() -> FaissVectorStore:
    """Singleton vector store. Lazily loads the embedding model for its dim."""
    global _store
    if _store is None:
        from app.services.embeddings import get_embedding_service

        _store = FaissVectorStore(get_embedding_service().dimension)
    return _store
