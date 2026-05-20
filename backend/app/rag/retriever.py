"""RAG retriever.

Embeds a query and searches the FAISS store for relevant article chunks.
Returns deduplicated, ranked context used by the chat, opinion and timeline
pipelines.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.rag.vector_store import get_vector_store
from app.services.embeddings import get_embedding_service


@dataclass
class RetrievedContext:
    article_id: str
    headline: str
    source: str
    text: str
    score: float


async def retrieve(
    query: str, k: int = 6, category: str | None = None
) -> list[RetrievedContext]:
    """Retrieve the top-k most relevant article chunks for a query."""
    embedder = get_embedding_service()
    store = get_vector_store()

    vec = await asyncio.to_thread(embedder.embed_query, query)
    hits = await asyncio.to_thread(store.search, vec, k, category)

    return [
        RetrievedContext(
            article_id=meta["article_id"],
            headline=meta["headline"],
            source=meta["source"],
            text=meta["text"],
            score=score,
        )
        for meta, score in hits
    ]


def format_context(chunks: list[RetrievedContext], max_chars: int = 6000) -> str:
    """Render retrieved chunks into a numbered context block for an LLM prompt."""
    parts: list[str] = []
    used = 0
    for i, c in enumerate(chunks, start=1):
        block = f"[{i}] ({c.source}) {c.headline}\n{c.text}\n"
        if used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)
    return "\n".join(parts) if parts else "(no relevant context retrieved)"
