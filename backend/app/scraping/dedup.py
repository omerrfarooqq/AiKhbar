"""Article deduplication.

Two layers:
  1. Exact dedup  — identical content_hash (cheap, runs first).
  2. Near dedup   — high cosine similarity between embeddings of recent
     articles, catching the same story rewritten by different outlets.

Near-duplicate articles are NOT discarded: they are valuable signal for
clustering and opinion aggregation. Dedup here only prevents storing the
exact same article twice.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.schemas.article import ArticleCreate


async def filter_new_articles(
    db: AsyncSession, candidates: list[ArticleCreate]
) -> list[ArticleCreate]:
    """Return only candidates not already stored (by URL or content hash)."""
    if not candidates:
        return []

    urls = {c.url for c in candidates}
    hashes = {c.content_hash for c in candidates}

    existing = await db.execute(
        select(Article.url, Article.content_hash).where(
            (Article.url.in_(urls)) | (Article.content_hash.in_(hashes))
        )
    )
    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()
    for url, h in existing.all():
        seen_urls.add(url)
        seen_hashes.add(h)

    fresh: list[ArticleCreate] = []
    batch_urls: set[str] = set()
    batch_hashes: set[str] = set()
    for c in candidates:
        if c.url in seen_urls or c.content_hash in seen_hashes:
            continue
        # Guard against duplicates within the same scrape batch.
        if c.url in batch_urls or c.content_hash in batch_hashes:
            continue
        batch_urls.add(c.url)
        batch_hashes.add(c.content_hash)
        fresh.append(c)

    logger.info(
        "Dedup | candidates={} | new={} | skipped={}",
        len(candidates), len(fresh), len(candidates) - len(fresh),
    )
    return fresh
