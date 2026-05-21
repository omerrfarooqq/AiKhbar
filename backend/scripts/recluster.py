"""Rebuild story clusters from scratch.

Clustering runs per category, so clusters formed while articles were still
mislabelled (e.g. all GENERAL after a failed classification run) are stale.
After a bulk re-classification, run this once from the backend/ directory to
rebuild clusters against the corrected categories:

    python -m scripts.recluster
"""
import asyncio

from loguru import logger
from sqlalchemy import delete, update

from app.core.logging import configure_logging
from app.db.session import AsyncSessionLocal, engine
from app.models.article import Article
from app.models.cluster import StoryCluster
from app.models.opinion import Opinion
from app.models.summary import Summary
from app.models.timeline import TimelineEvent
from app.summarization.clustering import cluster_recent_articles


async def main() -> None:
    configure_logging()
    async with AsyncSessionLocal() as db:
        # Drop cluster-derived data, then detach articles from the old clusters.
        await db.execute(delete(Summary))
        await db.execute(delete(Opinion))
        await db.execute(delete(TimelineEvent))
        await db.execute(update(Article).values(cluster_id=None))
        await db.execute(delete(StoryCluster))
        await db.commit()
        logger.info("Cleared stale clusters and derived summaries/opinions")

        created = await cluster_recent_articles(db)
        await db.commit()
        logger.info("Re-clustering complete: {} clusters created", created)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
