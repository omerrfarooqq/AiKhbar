"""News ingestion pipeline orchestrator.

End-to-end run:
    scrape -> deduplicate -> classify -> persist -> RAG index -> cluster

This is the single orchestration entry point used by both the scheduler and the
manual "trigger scrape" API endpoint. Each stage is isolated so a failure in
one (e.g. classification) does not abort the whole run.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from loguru import logger

from app.classification.classifier import classify_article
from app.db.session import AsyncSessionLocal
from app.rag.indexer import index_pending_articles
from app.scraping.dedup import filter_new_articles
from app.scraping.rss_scraper import scrape_all
from app.services import article_repository
from app.summarization.clustering import cluster_recent_articles

# Bound concurrent classification calls to respect NVIDIA rate limits.
_CLASSIFY_CONCURRENCY = 4


@dataclass
class IngestionReport:
    scraped: int = 0
    new: int = 0
    classified: int = 0
    indexed: int = 0
    clusters_created: int = 0
    errors: list[str] = field(default_factory=list)


async def _classify_all(items) -> None:  # noqa: ANN001
    """Classify ArticleCreate items in place, with bounded concurrency."""
    sem = asyncio.Semaphore(_CLASSIFY_CONCURRENCY)

    async def _one(item) -> None:  # noqa: ANN001
        async with sem:
            result = await classify_article(item.headline, item.body)
        item.category = result.category.value
        item.tags = result.tags
        if result.region:
            item.region = result.region

    await asyncio.gather(*(_one(i) for i in items), return_exceptions=True)


async def run_ingestion() -> IngestionReport:
    """Run the full ingestion pipeline once. Safe to call concurrently-bounded."""
    report = IngestionReport()
    logger.info("=== Ingestion pipeline started ===")

    # 1. Scrape.
    try:
        candidates = await scrape_all()
        report.scraped = len(candidates)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Scraping stage failed")
        report.errors.append(f"scrape: {exc}")
        return report

    if not candidates:
        logger.info("No articles scraped; pipeline ends early.")
        return report

    # 2. Deduplicate against the database.
    async with AsyncSessionLocal() as db:
        try:
            fresh = await filter_new_articles(db, candidates)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Dedup stage failed")
            report.errors.append(f"dedup: {exc}")
            return report
    report.new = len(fresh)

    if not fresh:
        logger.info("No new articles after dedup; pipeline ends.")
        return report

    # 3. Classify (LLM zero-shot).
    try:
        await _classify_all(fresh)
        report.classified = len(fresh)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Classification stage failed")
        report.errors.append(f"classify: {exc}")

    # 4. Persist.
    async with AsyncSessionLocal() as db:
        try:
            await article_repository.bulk_create(db, fresh)
            await db.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Persist stage failed")
            report.errors.append(f"persist: {exc}")
            return report

    # 5. RAG indexing.
    async with AsyncSessionLocal() as db:
        try:
            report.indexed = await index_pending_articles(db)
            await db.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Indexing stage failed")
            report.errors.append(f"index: {exc}")

    # 6. Clustering.
    async with AsyncSessionLocal() as db:
        try:
            report.clusters_created = await cluster_recent_articles(db)
            await db.commit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Clustering stage failed")
            report.errors.append(f"cluster: {exc}")

    logger.info(
        "=== Ingestion done | scraped={} new={} indexed={} clusters={} errors={} ===",
        report.scraped, report.new, report.indexed,
        report.clusters_created, len(report.errors),
    )
    return report
