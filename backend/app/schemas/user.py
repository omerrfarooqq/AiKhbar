"""User and personalization schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str | None = None
    preferred_categories: list[str] = Field(default_factory=list)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str | None = None
    preferred_categories: list[str] = Field(default_factory=list)
    saved_topics: list[str] = Field(default_factory=list)
    category_affinity: dict[str, float] = Field(default_factory=dict)
    created_at: datetime


class InteractionCreate(BaseModel):
    user_id: str
    article_id: str | None = None
    cluster_id: str | None = None
    action: str = Field(pattern="^(view|read|listen|save|chat)$")
    category: str | None = None
    duration_seconds: float = 0.0
