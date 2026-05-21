"""Registry of news sources.

Each source is RSS-first (reliable, low-load, ToS-friendly). The full article
body is then fetched and extracted from the article URL with trafilatura.
Category hints from the feed are advisory only; the AI classifier has the
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
    "humsub": NewsSource(
        key="humsub",
        name="Hum Sub",
        language="ur",
        feeds={
            "https://www.humsub.com.pk/feed/": Category.GENERAL,
        },
    ),
    "jang": NewsSource(
        key="jang",
        name="Daily Jang",
        language="ur",
        feeds={
            "https://jang.com.pk/rss/1/0": Category.GENERAL,
            "https://jang.com.pk/rss/1/7": Category.GENERAL,
            "https://jang.com.pk/rss/1/78": Category.GENERAL,
            "https://jang.com.pk/rss/1/79": Category.GENERAL,
        },
    ),
    "express_urdu": NewsSource(
        key="express_urdu",
        name="Express News Urdu",
        language="ur",
        feeds={
            "https://www.express.pk/feed/": Category.GENERAL,
        },
    ),
    "ary_urdu": NewsSource(
        key="ary_urdu",
        name="ARY News Urdu",
        language="ur",
        feeds={
            "https://urdu.arynews.tv/feed/": Category.GENERAL,
        },
    ),
}


def get_source(key: str) -> NewsSource | None:
    return SOURCES.get(key)


def all_sources() -> list[NewsSource]:
    return list(SOURCES.values())
