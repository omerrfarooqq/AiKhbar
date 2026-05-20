"""Story clustering.

Groups articles that cover the same real-world event so they can share one
unified summary, opinion set and timeline.

Approach: embed article headlines+leads, then agglomerative clustering with a
cosine-distance threshold. Headlines are short and discriminative, making this
robust across BBC/Geo/Jang phrasing differences. Clustering runs per category
to avoid cross-topic merges.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
from loguru import logger
from sklearn.cluster import AgglomerativeClustering
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.cluster import StoryCluster
from app.services.embeddings import get_embedding_service

# Cosine-distance threshold; lower = stricter (fewer, tighter clusters).
_DISTANCE_THRESHOLD = 0.45


def _cluster_indices(vectors: np.ndarray) -> list[int]:
    """Return a cluster label per row. Single items get their own label."""
    if len(vectors) == 1:
        return [0]
    model = AgglomerativeClustering(
        n_clusters=None,
        metric="cosine",
        linkage="average",
        distance_threshold=_DISTANCE_THRESHOLD,
    )
    return model.fit_predict(vectors).tolist()


async def cluster_recent_articles(db: AsyncSession, lookback: int = 200) -> int:
    """Cluster the most recent unclustered articles. Returns clusters created."""
    rows = await db.execute(
        select(Article)
        .where(Article.cluster_id.is_(None))
        .order_by(Article.created_at.desc())
        .limit(lookback)
    )
    articles = list(rows.scalars().all())
    if not articles:
        return 0

    embedder = get_embedding_service()
    clusters_created = 0

    # Cluster within each category independently.
    by_category: dict[str, list[Article]] = defaultdict(list)
    for art in articles:
        by_category[art.category].append(art)

    for category, group in by_category.items():
        if not group:
            continue
        texts = [f"{a.headline}. {a.body[:240]}" for a in group]
        vectors = await asyncio.to_thread(embedder.embed_documents, texts)
        labels = _cluster_indices(vectors)

        grouped: dict[int, list[int]] = defaultdict(list)
        for idx, label in enumerate(labels):
            grouped[label].append(idx)

        for member_indices in grouped.values():
            members = [group[i] for i in member_indices]
            member_vecs = vectors[member_indices]
            centroid = member_vecs.mean(axis=0)

            now = datetime.now(timezone.utc)
            cluster = StoryCluster(
                title=members[0].headline,
                category=category,
                centroid=centroid.tolist(),
                article_count=len(members),
                first_seen_at=min(
                    (m.published_at or m.created_at for m in members), default=now
                ),
                last_updated_at=now,
                keywords=_top_keywords(members),
            )
            db.add(cluster)
            await db.flush()
            for m in members:
                m.cluster_id = cluster.id
            clusters_created += 1

    logger.info("Clustering created {} clusters", clusters_created)
    return clusters_created


def _top_keywords(articles: list[Article], limit: int = 8) -> list[str]:
    """Aggregate the most common tags across a cluster's articles."""
    counts: dict[str, int] = defaultdict(int)
    for art in articles:
        for tag in art.tags or []:
            counts[tag] += 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [tag for tag, _ in ranked[:limit]]
