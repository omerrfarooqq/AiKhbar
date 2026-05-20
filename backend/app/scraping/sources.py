"""Registry of news sources.

Each source is RSS-first (reliable, low-load, ToS-friendly). The full article
body is then fetched and extracted from the article URL with trafilatura.
Category hints from the feed are advisory only — the AI classifier has the
final say.
"""
from dataclasses import dataclass, field

from app.core.constants import Category


@dataclass(frozen=True)
class NewsSource:
    key: str
    name: str
    language: str
    # feed_url -> advisory category hint
    feeds: dict[str, Category] = field(default_factory=dict)


SOURCES: dict[str, NewsSource] = {
    "bbc_urdu": NewsSource(
        key="bbc_urdu",
        name="BBC Urdu",
        language="ur",
        feeds={
            "https://feeds.bbci.co.uk/urdu/rss.xml": Category.GENERAL,
            "https://feeds.bbci.co.uk/urdu/pakistan/rss.xml": Category.POLITICS,
            "https://feeds.bbci.co.uk/urdu/world/rss.xml": Category.INTERNATIONAL,
            "https://feeds.bbci.co.uk/urdu/sport/rss.xml": Category.SPORTS,
            "https://feeds.bbci.co.uk/urdu/science/rss.xml": Category.TECHNOLOGY,
        },
    ),
    "geo_urdu": NewsSource(
        key="geo_urdu",
        name="Geo News Urdu",
        language="ur",
        feeds={
            "https://urdu.geo.tv/rss/1/1": Category.GENERAL,
            "https://urdu.geo.tv/rss/1/53": Category.POLITICS,
            "https://urdu.geo.tv/rss/1/57": Category.SPORTS,
            "https://urdu.geo.tv/rss/1/55": Category.INTERNATIONAL,
        },
    ),
    "jang": NewsSource(
        key="jang",
        name="Daily Jang",
        language="ur",
        feeds={
            "https://jang.com.pk/rss/1/0": Category.GENERAL,
        },
    ),
}


def get_source(key: str) -> NewsSource | None:
    return SOURCES.get(key)


def all_sources() -> list[NewsSource]:
    return list(SOURCES.values())
