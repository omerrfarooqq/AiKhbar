"""Summary model — an LLM-generated summary of a story cluster at a given depth."""
from __future__ import annotations

from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import BriefMode
from app.db.base import Base, TimestampMixin


class Summary(Base, TimestampMixin):
    __tablename__ = "summaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                    default=lambda: str(uuid4()))
    cluster_id: Mapped[str] = mapped_column(
        ForeignKey("story_clusters.id", ondelete="CASCADE"), index=True
    )
    mode: Mapped[str] = mapped_column(String(32), default=BriefMode.SHORT.value)
    language: Mapped[str] = mapped_column(String(8), default="ur")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(String(128))

    # Path to the generated TTS audio file, if any.
    audio_path: Mapped[str | None] = mapped_column(String(512))

    cluster: Mapped["StoryCluster"] = relationship(back_populates="summaries")  # noqa: F821
