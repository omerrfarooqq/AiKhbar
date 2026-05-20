"""Story cluster data-access layer."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cluster import StoryCluster


async def get_with_relations(
    db: AsyncSession, cluster_id: str
) -> StoryCluster | None:
    """Load a cluster with its summaries, opinions and timeline eagerly."""
    result = await db.execute(
        select(StoryCluster)
        .where(StoryCluster.id == cluster_id)
        .options(
            selectinload(StoryCluster.summaries),
            selectinload(StoryCluster.opinions),
            selectinload(StoryCluster.timeline_events),
            selectinload(StoryCluster.articles),
        )
    )
    return result.scalar_one_or_none()


async def list_clusters(
    db: AsyncSession,
    *,
    category: str | None = None,
    limit: int = 20,
) -> list[StoryCluster]:
    """List recent story clusters, optionally filtered by category."""
    stmt = select(StoryCluster).order_by(StoryCluster.last_updated_at.desc())
    if category:
        stmt = stmt.where(StoryCluster.category == category)
    rows = await db.execute(stmt.limit(limit))
    return list(rows.scalars().all())


async def top_clusters(
    db: AsyncSession, limit: int = 6, category: str | None = None
) -> list[StoryCluster]:
    """Top clusters by article volume — the 'top stories' of the moment."""
    stmt = select(StoryCluster).order_by(
        StoryCluster.article_count.desc(), StoryCluster.last_updated_at.desc()
    )
    if category:
        stmt = stmt.where(StoryCluster.category == category)
    rows = await db.execute(stmt.limit(limit))
    return list(rows.scalars().all())
