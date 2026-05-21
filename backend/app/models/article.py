"""Article model — a single scraped news article with structured metadata."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import Category, ToneLabel
from app.db.base import Base, TimestampMixin


class Article(Base, TimestampMixin):
    __tablename__ = "articles"
    __table_args__ = (
        Index("ix_articles_category_published", "category", "published_at"),
        Index("ix_articles_source", "source"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                    default=lambda: str(uuid4()))

    # --- Core content ---
    headline: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(1024), unique=True, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1024))

    # --- Provenance ---
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    author: Mapped[str | None] = mapped_column(String(256))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # --- Classification / enrichment ---
    category: Mapped[str] = mapped_column(String(32), default=Category.GENERAL.value)
    category_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    region: Mapped[str | None] = mapped_column(String(64))
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    language: Mapped[str] = mapped_column(String(8), default="ur")

    # --- Deduplication ---
    content_hash: Mapped[str] = mapped_column(String(64), index=True)

    # --- Media analysis (populated by analytics service) ---
    tone: Mapped[str | None] = mapped_column(String(32))
    political_leaning: Mapped[str | None] = mapped_column(String(32))
    sentiment_score: Mapped[float | None] = mapped_column(Float)

    # --- RAG ---
    is_indexed: Mapped[bool] = mapped_column(default=False)

    # --- Clustering ---
    cluster_id: Mapped[str | None] = mapped_column(
        ForeignKey("story_clusters.id", ondelete="SET NULL")
    )
    cluster: Mapped["StoryCluster | None"] = relationship(back_populates="articles")  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Article {self.id} {self.source} '{self.headline[:40]}'>"
