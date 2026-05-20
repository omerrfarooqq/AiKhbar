"""Article fetching and content extraction.

RSS feeds give headline + URL + summary, but rarely the full body. This module
fetches the article page and extracts clean main-content text using trafilatura,
falling back to a BeautifulSoup heuristic if extraction fails.
"""
from __future__ import annotations

import re

import httpx
import trafilatura
from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import settings
from app.scraping.hashing import content_hash  # noqa: F401  (re-exported)

_WS = re.compile(r"\s+")


def _clean(text: str) -> str:
    return _WS.sub(" ", text or "").strip()


async def fetch_article_body(url: str, client: httpx.AsyncClient) -> str | None:
    """Fetch a URL and return extracted main article text, or None on failure."""
    try:
        resp = await client.get(url, follow_redirects=True,
                                timeout=settings.scrape_request_timeout)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Fetch failed for {}: {}", url, exc)
        return None

    html = resp.text

    # Primary: trafilatura (best-in-class boilerplate removal).
    extracted = trafilatura.extract(
        html, include_comments=False, include_tables=False, favor_recall=True
    )
    if extracted and len(extracted) > 120:
        return _clean(extracted)

    # Fallback: collect paragraph text.
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    body = _clean(" ".join(p for p in paragraphs if len(p) > 40))
    return body or None
