"""Backfill lead images for articles scraped before image extraction existed.

Fetches each article URL and pulls its social-card image. Run from backend/:
    python -m scripts.backfill_images
"""
import asyncio

import httpx
from loguru import logger
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import AsyncSessionLocal, engine
from app.models.article import Article
from app.scraping.extractor import fetch_article

_CONCURRENCY = 10


async def main() -> None:
    configure_logging()
    async with AsyncSessionLocal() as db:
        rows = list(
            (
                await db.execute(
                    select(Article).where(Article.image_url.is_(None))
                )
            ).scalars().all()
        )
        logger.info("Backfilling images for {} articles", len(rows))

        sem = asyncio.Semaphore(_CONCURRENCY)
        headers = {"User-Agent": settings.scraper_user_agent}
        async with httpx.AsyncClient(headers=headers) as client:

            async def _one(art: Article) -> None:
                async with sem:
                    _, image = await fetch_article(art.url, client)
                if image:
                    art.image_url = image

            await asyncio.gather(
                *(_one(a) for a in rows), return_exceptions=True
            )
        await db.commit()
        filled = sum(1 for a in rows if a.image_url)
        logger.info("Backfill complete: {}/{} articles got an image",
                    filled, len(rows))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
