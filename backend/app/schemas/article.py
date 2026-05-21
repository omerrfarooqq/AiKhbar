"""Article-related schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import Category


class ArticleBase(BaseModel):
    headline: str
    url: str
    image_url: str | None = None
    source: str
    author: str | None = None
    published_at: datetime | None = None
    category: str = Category.GENERAL.value
    region: str | None = None
    tags: list[str] = Field(default_factory=list)
    language: str = "ur"


class ArticleCreate(ArticleBase):
    body: str
    content_hash: str


class ArticleRead(ArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    body: str
    category_confidence: float = 0.0
    tone: str | None = None
    political_leaning: str | None = None
    sentiment_score: float | None = None
    cluster_id: str | None = None
    created_at: datetime


class ArticleSummaryCard(BaseModel):
    """Lightweight article card for feed/list views (no full body)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    headline: str
    url: str
    image_url: str | None = None
    source: str
    category: str
    region: str | None = None
    published_at: datetime | None = None
    cluster_id: str | None = None
    tags: list[str] = Field(default_factory=list)
