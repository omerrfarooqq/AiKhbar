"""RAG indexer.

Turns stored articles into chunked, embedded vectors in the FAISS store, then
marks them indexed. Idempotent: only indexes articles where `is_indexed` is
False.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.rag.chunker import chunk_text
from app.rag.vector_store import get_vector_store
from app.services.embeddings import get_embedding_service


async def index_pending_articles(db: AsyncSession, limit: int = 200) -> int:
    """Index all not-yet-indexed articles. Returns the count of articles indexed."""
    rows = await db.execute(
        select(Article).where(Article.is_indexed.is_(False)).limit(limit)
    )
    articles = list(rows.scalars().all())
    if not articles:
        return 0

    embedder = get_embedding_service()
    store = get_vector_store()

    all_chunks: list[str] = []
    all_meta: list[dict] = []
    for art in articles:
        chunks = chunk_text(art.body)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_meta.append(
                {
                    "article_id": art.id,
                    "chunk_index": i,
                    "headline": art.headline,
                    "source": art.source,
                    "category": art.category,
                    "url": art.url,
                    "text": chunk,
                }
            )

    if not all_chunks:
        return 0

    # Embedding is CPU-bound — run off the event loop.
    import asyncio

    vectors = await asyncio.to_thread(embedder.embed_documents, all_chunks)
    await asyncio.to_thread(store.add, vectors, all_meta)

    ids = [a.id for a in articles]
    await db.execute(
        update(Article).where(Article.id.in_(ids)).values(is_indexed=True)
    )
    logger.info("Indexed {} articles -> {} chunks", len(articles), len(all_chunks))
    return len(articles)
