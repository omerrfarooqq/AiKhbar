"""Shared enums and domain constants."""
from enum import Enum


class Category(str, Enum):
    """Canonical news categories used across classification, filtering and feeds."""

    POLITICS = "politics"
    SPORTS = "sports"
    ECONOMY = "economy"
    CRIME = "crime"
    INTERNATIONAL = "international"
    TECHNOLOGY = "technology"
    ENTERTAINMENT = "entertainment"
    GENERAL = "general"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]


# Human-readable labels (English) fed to zero-shot / LLM classification prompts.
CATEGORY_LABELS: dict[Category, str] = {
    Category.POLITICS: "Politics and government",
    Category.SPORTS: "Sports",
    Category.ECONOMY: "Economy, business and finance",
    Category.CRIME: "Crime and law enforcement",
    Category.INTERNATIONAL: "International and world news",
    Category.TECHNOLOGY: "Technology and science",
    Category.ENTERTAINMENT: "Entertainment, arts and culture",
    Category.GENERAL: "General news",
}


class BriefMode(str, Enum):
    """Summarisation depth / length presets."""

    SHORT = "short"            # 2-3 sentences
    DETAILED = "detailed"      # full paragraph summary
    MORNING_BRIEF = "morning"  # ~5 minute narrated brief
    DEEP_DIVE = "deep_dive"    # ~15 minute narrated analysis


class NarrationMode(str, Enum):
    """TTS narration style presets."""

    NEUTRAL = "neutral"
    PODCAST = "podcast"
    HEADLINE = "headline"


class ToneLabel(str, Enum):
    """Media-analysis tone classification output."""

    NEUTRAL = "neutral"
    EMOTIONAL = "emotional"
    SENSATIONAL = "sensational"
    PRO_GOVERNMENT = "pro_government"
    OPPOSITION_LEANING = "opposition_leaning"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
