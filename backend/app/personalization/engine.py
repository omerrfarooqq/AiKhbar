"""Personalization engine.

Learns per-user category affinity from tracked interactions and uses it to rank
a personalized feed. The model is intentionally simple and explainable: a
time-decayed, action-weighted score per category. It can be swapped for a
collaborative-filtering or embedding-based recommender behind the same API.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import Category
from app.core.exceptions import NotFoundError
from app.models.article import Article
from app.models.user import User, UserInteraction

# Relative importance of each action type when learning interest.
_ACTION_WEIGHTS = {"view": 1.0, "read": 2.5, "listen": 3.0, "save": 4.0, "chat": 3.5}
# Affinity halves roughly every ~10 days.
_DECAY_LAMBDA = 0.069


def _decay(age_days: float) -> float:
    return math.exp(-_DECAY_LAMBDA * max(0.0, age_days))


async def recompute_affinity(db: AsyncSession, user_id: str) -> dict[str, float]:
    """Recompute and persist a user's category affinity from their interactions."""
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")

    rows = await db.execute(
        select(UserInteraction).where(UserInteraction.user_id == user_id)
    )
    interactions = list(rows.scalars().all())

    now = datetime.now(timezone.utc)
    scores: dict[str, float] = defaultdict(float)
    for it in interactions:
        if not it.category:
            continue
        age_days = (now - it.created_at).total_seconds() / 86400.0
        weight = _ACTION_WEIGHTS.get(it.action, 1.0)
        # Listening/reading duration adds a mild bonus.
        duration_bonus = min(it.duration_seconds / 120.0, 2.0)
        scores[it.category] += (weight + duration_bonus) * _decay(age_days)

    # Normalise to 0..1 for a stable, comparable affinity profile.
    total = sum(scores.values()) or 1.0
    affinity = {cat: round(val / total, 4) for cat, val in scores.items()}

    user.category_affinity = affinity
    await db.flush()
    logger.info("Recomputed affinity for user {}: {}", user_id, affinity)
    return affinity


async def personalized_feed(
    db: AsyncSession, user_id: str, limit: int = 20
) -> list[Article]:
    """Return a feed of recent articles ranked by the user's category affinity."""
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")

    affinity = user.category_affinity or {}
    # Seed cold-start users with their explicitly preferred categories.
    if not affinity and user.preferred_categories:
        affinity = {c: 1.0 for c in user.preferred_categories}

    rows = await db.execute(
        select(Article).order_by(Article.created_at.desc()).limit(limit * 4)
    )
    articles = list(rows.scalars().all())

    now = datetime.now(timezone.utc)

    def _rank(article: Article) -> float:
        cat_score = affinity.get(article.category, 0.05)
        age_days = (now - (article.published_at or article.created_at)).total_seconds() / 86400.0
        recency = _decay(age_days)
        return cat_score * 0.7 + recency * 0.3

    ranked = sorted(articles, key=_rank, reverse=True)
    return ranked[:limit]


def default_categories() -> list[str]:
    return [Category.POLITICS.value, Category.INTERNATIONAL.value,
            Category.ECONOMY.value]
