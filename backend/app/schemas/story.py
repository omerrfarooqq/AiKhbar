"""Story cluster, summary, opinion and timeline schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import BriefMode


class SummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    mode: str
    language: str
    content: str
    audio_path: str | None = None
    created_at: datetime


class OpinionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    perspective: str
    summary: str
    stance: str | None = None
    confidence: float
    source_article_ids: list[str] = Field(default_factory=list)


class TimelineEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_date: datetime | None = None
    date_label: str | None = None
    title: str
    description: str
    ordering: int


class ClusterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    category: str
    article_count: int
    keywords: list[str] = Field(default_factory=list)
    unified_summary: str | None = None
    first_seen_at: datetime | None = None
    last_updated_at: datetime | None = None


class ClusterDetail(ClusterRead):
    summaries: list[SummaryRead] = Field(default_factory=list)
    opinions: list[OpinionRead] = Field(default_factory=list)
    timeline_events: list[TimelineEventRead] = Field(default_factory=list)


class SummarizeRequest(BaseModel):
    mode: BriefMode = BriefMode.SHORT
    language: str = "ur"


class DailyBriefRequest(BaseModel):
    user_id: str | None = None
    max_stories: int = Field(default=6, ge=1, le=15)
    mode: BriefMode = BriefMode.MORNING_BRIEF
    include_audio: bool = True
    include_opinions: bool = True
