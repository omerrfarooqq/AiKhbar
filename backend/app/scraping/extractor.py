"""Article fetching and content extraction.

RSS feeds give headline + URL + summary, but rarely the full body. This module
fetches the article page and extracts both the clean main-content text (via
trafilatura, with a BeautifulSoup fallback) and the lead image.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin

import httpx
import trafilatura
from bs4 import BeautifulSoup
from loguru import logger

from app.core.config import settings
from app.scraping.hashing import content_hash  # noqa: F401  (re-exported)

_WS = re.compile(r"\s+")
# Social-card meta tags, in priority order, that expose the lead image.
_IMAGE_META = ("og:image", "og:image:url", "twitter:image", "twitter:image:src")


def _clean(text: str) -> str:
    return _WS.sub(" ", text or "").strip()


def _extract_image(soup: BeautifulSoup, base_url: str) -> str | None:
    """Pull the lead image from a page's social-card meta tags."""
    for key in _IMAGE_META:
        tag = soup.find("meta", attrs={"property": key}) or soup.find(
            "meta", attrs={"name": key}
        )
        content = tag.get("content") if tag else None
        if content and content.strip():
            return urljoin(base_url, content.strip())
    return None


async def fetch_article(
    url: str, client: httpx.AsyncClient
) -> tuple[str | None, str | None]:
    """Fetch a URL; return (main article text, lead image URL).

    Either element may be None if extraction fails.
    """
    try:
        resp = await client.get(url, follow_redirects=True,
                                timeout=settings.scrape_request_timeout)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Fetch failed for {}: {}", url, exc)
        return None, None

    html = resp.text
    soup = BeautifulSoup(html, "lxml")
    image = _extract_image(soup, str(resp.url))

    # Primary: trafilatura (best-in-class boilerplate removal).
    extracted = trafilatura.extract(
        html, include_comments=False, include_tables=False, favor_recall=True
    )
    if extracted and len(extracted) > 120:
        return _clean(extracted), image

    # Fallback: collect paragraph text directly from the DOM.
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    body = _clean(" ".join(p for p in paragraphs if len(p) > 40))
    return body or None, image
