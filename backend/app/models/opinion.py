"""Opinion model — an aggregated viewpoint about a story cluster (RAG output)."""
from __future__ import annotations

from uuid import uuid4

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Opinion(Base, TimestampMixin):
    """A clustered viewpoint produced by the RAG opinion-aggregation pipeline.

    `perspective` is a free-form label such as 'public sentiment',
    'pro-government', 'opposition', 'expert', 'international reaction'.
    """

    __tablename__ = "opinions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                    default=lambda: str(uuid4()))
    cluster_id: Mapped[str] = mapped_column(
        ForeignKey("story_clusters.id", ondelete="CASCADE"), index=True
    )
    perspective: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    stance: Mapped[str | None] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source_article_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    cluster: Mapped["StoryCluster"] = relationship(back_populates="opinions")  # noqa: F821
