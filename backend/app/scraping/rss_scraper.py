"""RSS-based scraper.

Parses configured RSS feeds, fetches full article bodies and yields
ArticleCreate schemas ready for persistence. Network I/O is concurrent
but politely bounded by a semaphore.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from time import mktime

import feedparser
import httpx
from loguru import logger

from app.core.config import settings
from app.scraping.extractor import fetch_article_body
from app.scraping.hashing import content_hash
from app.scraping.sources import NewsSource, all_sources
from app.schemas.article import ArticleCreate

# Politeness: cap concurrent article fetches per scrape run.
_FETCH_CONCURRENCY = 8


def _parse_published(entry) -> datetime | None:  # noqa: ANN001
    parsed = getattr(entry, "published_parsed", None) or getattr(
        entry, "updated_parsed", None
    )
    if parsed:
        return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
    return None


async def _scrape_feed(
    source: NewsSource,
    feed_url: str,
    category_hint: str,
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
) -> list[ArticleCreate]:
    """Parse one feed and fetch bodies for its entries."""
    # feedparser is blocking — run it off the event loop.
    feed = await asyncio.to_thread(feedparser.parse, feed_url)
    entries = feed.entries[: settings.scrape_max_articles_per_source]
    logger.info("Feed {} -> {} entries", feed_url, len(entries))

    async def _build(entry) -> ArticleCreate | None:  # noqa: ANN001
        url = getattr(entry, "link", None)
        headline = getattr(entry, "title", None)
        if not url or not headline:
            return None
        async with sem:
            body = await fetch_article_body(url, client)
        if not body or len(body) < 150:
            # Fall back to the RSS summary if body extraction was too thin.
            body = getattr(entry, "summary", "") or body or ""
        if len(body) < 80:
            return None
        return ArticleCreate(
            headline=headline.strip(),
            body=body,
            url=url,
            source=source.key,
            author=getattr(entry, "author", None),
            published_at=_parse_published(entry),
            category=category_hint,
            language=source.language,
            content_hash=content_hash(headline, body),
        )

    results = await asyncio.gather(*(_build(e) for e in entries))
    return [a for a in results if a is not None]


async def scrape_source(source: NewsSource) -> list[ArticleCreate]:
    """Scrape every feed of a single source."""
    sem = asyncio.Semaphore(_FETCH_CONCURRENCY)
    headers = {"User-Agent": settings.scraper_user_agent}
    async with httpx.AsyncClient(headers=headers) as client:
        feed_results = await asyncio.gather(
            *(
                _scrape_feed(source, url, hint.value, client, sem)
                for url, hint in source.feeds.items()
            ),
            return_exceptions=True,
        )
    articles: list[ArticleCreate] = []
    for res in feed_results:
        if isinstance(res, Exception):
            logger.error("Feed scrape error for {}: {}", source.key, res)
            continue
        articles.extend(res)
    logger.info("Scraped {} -> {} articles", source.key, len(articles))
    return articles


async def scrape_all() -> list[ArticleCreate]:
    """Scrape every registered source. Entry point for the scheduler/API."""
    batches = await asyncio.gather(
        *(scrape_source(s) for s in all_sources()), return_exceptions=True
    )
    articles: list[ArticleCreate] = []
    for batch in batches:
        if isinstance(batch, Exception):
            logger.error("Source scrape failed: {}", batch)
            continue
        articles.extend(batch)
    logger.info("Scrape run complete | total={}", len(articles))
    return articles
