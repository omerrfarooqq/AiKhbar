"""Article data-access layer.

Keeps SQLAlchemy query construction out of API routes and pipeline code.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.schemas.article import ArticleCreate


async def bulk_create(db: AsyncSession, items: list[ArticleCreate]) -> list[Article]:
    """Insert a batch of new articles. Caller is responsible for dedup."""
    articles = [Article(**item.model_dump()) for item in items]
    db.add_all(articles)
    await db.flush()
    return articles


async def get_by_id(db: AsyncSession, article_id: str) -> Article | None:
    return await db.get(Article, article_id)


async def list_articles(
    db: AsyncSession,
    *,
    category: str | None = None,
    source: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Article], int]:
    """Filtered, paginated article listing. Returns (items, total_count)."""
    stmt = select(Article)
    count_stmt = select(func.count()).select_from(Article)

    filters = []
    if category:
        filters.append(Article.category == category)
    if source:
        filters.append(Article.source == source)
    if date_from:
        filters.append(Article.published_at >= date_from)
    if date_to:
        filters.append(Article.published_at <= date_to)

    for f in filters:
        stmt = stmt.where(f)
        count_stmt = count_stmt.where(f)

    total = (await db.execute(count_stmt)).scalar_one()
    stmt = (
        stmt.order_by(Article.published_at.desc().nullslast(),
                      Article.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = await db.execute(stmt)
    return list(rows.scalars().all()), int(total)


async def latest_articles(db: AsyncSession, limit: int = 30) -> list[Article]:
    rows = await db.execute(
        select(Article).order_by(Article.created_at.desc()).limit(limit)
    )
    return list(rows.scalars().all())


async def category_counts(db: AsyncSession) -> dict[str, int]:
    """Article count grouped by category — used for dashboard chips."""
    rows = await db.execute(
        select(Article.category, func.count()).group_by(Article.category)
    )
    return {cat: int(n) for cat, n in rows.all()}
