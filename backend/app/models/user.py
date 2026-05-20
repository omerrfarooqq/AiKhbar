"""User and UserInteraction models — power the personalization engine."""
from __future__ import annotations

from uuid import uuid4

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                    default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(128))

    # Personalization state.
    preferred_categories: Mapped[list[str]] = mapped_column(JSON, default=list)
    saved_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    # category -> affinity score, updated by the personalization engine.
    category_affinity: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)

    interactions: Mapped[list["UserInteraction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserInteraction(Base, TimestampMixin):
    """A single tracked interaction event used to learn user interest."""

    __tablename__ = "user_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                    default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    article_id: Mapped[str | None] = mapped_column(String(36), index=True)
    cluster_id: Mapped[str | None] = mapped_column(String(36))
    # 'view' | 'read' | 'listen' | 'save' | 'chat'
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str | None] = mapped_column(String(32))
    # Engagement duration in seconds (for read/listen actions).
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    weight: Mapped[int] = mapped_column(Integer, default=1)

    user: Mapped["User"] = relationship(back_populates="interactions")
