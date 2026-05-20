"""TimelineEvent model — a historical event linked to a story cluster."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class TimelineEvent(Base, TimestampMixin):
    """A single dated event in the historical context of a story."""

    __tablename__ = "timeline_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                    default=lambda: str(uuid4()))
    cluster_id: Mapped[str] = mapped_column(
        ForeignKey("story_clusters.id", ondelete="CASCADE"), index=True
    )
    event_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Free-text date label for when an exact date is unknown ("early 2023").
    date_label: Mapped[str | None] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ordering: Mapped[int] = mapped_column(Integer, default=0)

    cluster: Mapped["StoryCluster"] = relationship(  # noqa: F821
        back_populates="timeline_events"
    )
