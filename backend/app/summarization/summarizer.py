"""Multi-document summarization service.

Given a story cluster (one or more articles about the same event), produces a
single unified Urdu summary at the requested depth (short / detailed / morning
brief / deep dive). Summaries are persisted and reused.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.constants import BriefMode
from app.core.exceptions import NotFoundError
from app.models.cluster import StoryCluster
from app.models.summary import Summary
from app.services import prompts
from app.services.nvidia_client import get_llm_client

# Cap source text per article so deep clusters stay within the context window.
_MAX_CHARS_PER_ARTICLE = 2200
_MAX_ARTICLES = 6


def _assemble_sources(cluster: StoryCluster) -> str:
    parts: list[str] = []
    for i, art in enumerate(cluster.articles[:_MAX_ARTICLES], start=1):
        body = art.body[:_MAX_CHARS_PER_ARTICLE]
        parts.append(f"--- Article {i} | {art.source} ---\n{art.headline}\n{body}")
    return "\n\n".join(parts)


async def summarize_cluster(
    db: AsyncSession,
    cluster_id: str,
    mode: BriefMode = BriefMode.SHORT,
    language: str = "ur",
    force: bool = False,
) -> Summary:
    """Generate (or return cached) a unified summary for a cluster."""
    result = await db.execute(
        select(StoryCluster)
        .where(StoryCluster.id == cluster_id)
        .options(selectinload(StoryCluster.articles))
    )
    cluster = result.scalar_one_or_none()
    if cluster is None:
        raise NotFoundError(f"Story cluster {cluster_id} not found")

    if not force:
        cached = await db.execute(
            select(Summary).where(
                Summary.cluster_id == cluster_id,
                Summary.mode == mode.value,
                Summary.language == language,
            )
        )
        existing = cached.scalar_one_or_none()
        if existing:
            logger.debug("Returning cached {} summary for cluster {}", mode, cluster_id)
            return existing

    llm = get_llm_client()
    sources = _assemble_sources(cluster)
    # The fast 8B model is used so the daily brief's burst of summary calls
    # stays within the NVIDIA free-tier rate limit; the 70B model 429s hard.
    model = settings.nvidia_llm_model_fast
    content = await llm.complete(
        system=prompts.SUMMARIZE_SYSTEM,
        user=prompts.summarize_user(mode, sources),
        model=model,
        temperature=0.3,
        max_tokens=2500 if mode == BriefMode.DEEP_DIVE else 1200,
    )

    summary = Summary(
        cluster_id=cluster_id,
        mode=mode.value,
        language=language,
        content=content,
        model=model,
    )
    db.add(summary)

    # Keep a copy of the short summary on the cluster for quick feed rendering.
    if mode == BriefMode.SHORT:
        cluster.unified_summary = content

    await db.flush()
    logger.info("Generated {} summary for cluster {}", mode.value, cluster_id)
    return summary
