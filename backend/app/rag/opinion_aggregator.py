"""RAG-based opinion aggregation.

For a story cluster, retrieves related articles/editorials/discussions from the
vector store, then asks the LLM to identify and summarise the distinct
viewpoints (public sentiment, pro-government, opposition, expert, international).
Results are persisted as Opinion rows on the cluster.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.cluster import StoryCluster
from app.models.opinion import Opinion
from app.rag.retriever import format_context, retrieve
from app.services import prompts
from app.services.nvidia_client import get_llm_client


async def aggregate_opinions(
    db: AsyncSession, cluster_id: str, force: bool = False
) -> list[Opinion]:
    """Build and persist aggregated opinions for a story cluster."""
    result = await db.execute(
        select(StoryCluster).where(StoryCluster.id == cluster_id)
    )
    cluster = result.scalar_one_or_none()
    if cluster is None:
        raise NotFoundError(f"Story cluster {cluster_id} not found")

    if not force:
        existing = await db.execute(
            select(Opinion).where(Opinion.cluster_id == cluster_id)
        )
        rows = list(existing.scalars().all())
        if rows:
            return rows

    # Retrieve broad context around the story for viewpoint diversity.
    chunks = await retrieve(cluster.title, k=10, category=cluster.category)
    context = format_context(chunks, max_chars=7000)

    llm = get_llm_client()
    data = await llm.complete_json(
        system=prompts.OPINION_SYSTEM,
        user=prompts.opinion_user(cluster.title, context),
        # Fast model keeps the brief within the free-tier rate limit.
        model=settings.nvidia_llm_model_fast,
    )

    # Replace any stale opinions for this cluster.
    await db.execute(delete(Opinion).where(Opinion.cluster_id == cluster_id))

    source_ids = list({c.article_id for c in chunks})
    opinions: list[Opinion] = []
    for item in data.get("perspectives", []):
        opinion = Opinion(
            cluster_id=cluster_id,
            perspective=str(item.get("perspective", "general"))[:64],
            summary=str(item.get("summary", "")),
            stance=str(item.get("stance", "")) or None,
            confidence=float(item.get("confidence", 0.0) or 0.0),
            source_article_ids=source_ids,
        )
        db.add(opinion)
        opinions.append(opinion)

    await db.flush()
    logger.info("Aggregated {} opinions for cluster {}", len(opinions), cluster_id)
    return opinions
