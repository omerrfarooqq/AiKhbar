"""Timeline / historical context engine.

Builds a chronological background timeline for a story cluster by retrieving
related historical coverage from the vector store and asking the LLM to
assemble a factual event sequence. Persisted as TimelineEvent rows.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.cluster import StoryCluster
from app.models.timeline import TimelineEvent
from app.rag.retriever import format_context, retrieve
from app.services import prompts
from app.services.nvidia_client import get_llm_client


async def build_timeline(
    db: AsyncSession, cluster_id: str, force: bool = False
) -> list[TimelineEvent]:
    """Generate and persist a historical timeline for a story cluster."""
    result = await db.execute(
        select(StoryCluster).where(StoryCluster.id == cluster_id)
    )
    cluster = result.scalar_one_or_none()
    if cluster is None:
        raise NotFoundError(f"Story cluster {cluster_id} not found")

    if not force:
        existing = await db.execute(
            select(TimelineEvent)
            .where(TimelineEvent.cluster_id == cluster_id)
            .order_by(TimelineEvent.ordering)
        )
        rows = list(existing.scalars().all())
        if rows:
            return rows

    chunks = await retrieve(f"history background context {cluster.title}", k=8)
    context = format_context(chunks, max_chars=5000)

    llm = get_llm_client()
    data = await llm.complete_json(
        system=prompts.TIMELINE_SYSTEM,
        user=prompts.timeline_user(cluster.title, context),
    )

    await db.execute(
        delete(TimelineEvent).where(TimelineEvent.cluster_id == cluster_id)
    )

    events: list[TimelineEvent] = []
    for order, item in enumerate(data.get("events", [])):
        event = TimelineEvent(
            cluster_id=cluster_id,
            date_label=str(item.get("date_label", "")) or None,
            title=str(item.get("title", "Event"))[:512],
            description=str(item.get("description", "")),
            ordering=order,
        )
        db.add(event)
        events.append(event)

    await db.flush()
    logger.info("Built timeline | cluster={} | events={}", cluster_id, len(events))
    return events
