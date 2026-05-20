"""APScheduler-based background scheduler.

Runs the ingestion pipeline periodically. A single AsyncIOScheduler instance is
started/stopped with the FastAPI app lifespan. Jobs are guarded with
`max_instances=1` so a slow run never overlaps the next tick.
"""
from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from app.core.config import settings
from app.services.ingestion_pipeline import run_ingestion

_scheduler: AsyncIOScheduler | None = None


async def _scheduled_ingestion() -> None:
    logger.info("Scheduled ingestion tick")
    try:
        await run_ingestion()
    except Exception:  # noqa: BLE001
        logger.exception("Scheduled ingestion run failed")


def start_scheduler() -> None:
    """Start the background scheduler if enabled in configuration."""
    global _scheduler
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled (SCHEDULER_ENABLED=false)")
        return
    if _scheduler is not None:
        return

    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(
        _scheduled_ingestion,
        trigger=IntervalTrigger(minutes=settings.scrape_interval_minutes),
        id="news_ingestion",
        name="Periodic news ingestion",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started | ingestion every {} min", settings.scrape_interval_minutes
    )


def shutdown_scheduler() -> None:
    """Gracefully stop the scheduler."""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler stopped")
