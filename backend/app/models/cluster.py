"""StoryCluster model — a group of articles covering the same real-world story."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class StoryCluster(Base, TimestampMixin):
    """Multiple articles about one event are grouped into a cluster.

    The cluster owns the unified multi-document summary, opinion aggregation
    and timeline for the underlying story.
    """

    __tablename__ = "story_clusters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                    default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    category: Mapped[str] = mapped_column(String(32), index=True)
    centroid: Mapped[list[float] | None] = mapped_column(JSON)
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list)
    unified_summary: Mapped[str | None] = mapped_column(Text)

    articles: Mapped[list["Article"]] = relationship(  # noqa: F821
        back_populates="cluster"
    )
    summaries: Mapped[list["Summary"]] = relationship(  # noqa: F821
        back_populates="cluster", cascade="all, delete-orphan"
    )
    opinions: Mapped[list["Opinion"]] = relationship(  # noqa: F821
        back_populates="cluster", cascade="all, delete-orphan"
    )
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(  # noqa: F821
        back_populates="cluster", cascade="all, delete-orphan"
    )
