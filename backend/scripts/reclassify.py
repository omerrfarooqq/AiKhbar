"""Re-run classification on articles still labelled GENERAL.

Earlier ingestion runs that failed classification (e.g. invalid LLM
credentials) all default to GENERAL. After fixing the NVIDIA key, run this
once from the backend/ directory to back-fill proper categories:

    python -m scripts.reclassify
"""
import asyncio

from loguru import logger
from sqlalchemy import select

from app.classification.classifier import classify_article
from app.core.constants import Category
from app.core.logging import configure_logging
from app.db.session import AsyncSessionLocal, engine
from app.models.article import Article

# Serialise calls and pace them to stay under the NVIDIA free-tier rate limit.
_CONCURRENCY = 1
_PACING_SECONDS = 1.0


async def main() -> None:
    configure_logging()
    async with AsyncSessionLocal() as db:
        rows = (
            await db.execute(
                select(Article).where(Article.category == Category.GENERAL.value)
            )
        ).scalars().all()
        logger.info("Reclassifying {} articles labelled GENERAL", len(rows))
        if not rows:
            return

        sem = asyncio.Semaphore(_CONCURRENCY)

        async def _one(art: Article) -> None:
            async with sem:
                result = await classify_article(art.headline, art.body)
                await asyncio.sleep(_PACING_SECONDS)
            art.category = result.category.value
            art.category_confidence = result.confidence
            art.tags = result.tags
            if result.region:
                art.region = result.region
            logger.info("  {} -> {}", art.headline[:48], art.category)

        await asyncio.gather(*(_one(a) for a in rows), return_exceptions=True)
        await db.commit()
        logger.info("Reclassification complete")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
