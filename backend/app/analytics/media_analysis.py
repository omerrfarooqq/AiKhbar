"""Media analysis engine.

Assesses an article's emotional tone, political leaning, sentiment and
propaganda indicators using the LLM. Results are written back onto the Article
row so the frontend can surface a media-bias badge.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.article import Article
from app.services import prompts
from app.services.nvidia_client import get_llm_client


@dataclass
class MediaAnalysis:
    tone: str = "neutral"
    political_leaning: str = "neutral"
    sentiment_score: float = 0.0
    propaganda_indicators: list[str] = field(default_factory=list)
    reasoning: str = ""


async def analyze_article(db: AsyncSession, article_id: str) -> MediaAnalysis:
    """Run media analysis on an article and persist the result."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if article is None:
        raise NotFoundError(f"Article {article_id} not found")

    llm = get_llm_client()
    data = await llm.complete_json(
        system=prompts.ANALYSIS_SYSTEM,
        user=prompts.analysis_user(article.headline, article.body),
    )

    analysis = MediaAnalysis(
        tone=str(data.get("tone", "neutral")),
        political_leaning=str(data.get("political_leaning", "neutral")),
        sentiment_score=float(data.get("sentiment_score", 0.0) or 0.0),
        propaganda_indicators=[str(x) for x in (data.get("propaganda_indicators") or [])],
        reasoning=str(data.get("reasoning", "")),
    )

    article.tone = analysis.tone
    article.political_leaning = analysis.political_leaning
    article.sentiment_score = analysis.sentiment_score
    await db.flush()

    logger.info("Media analysis done | article={} | tone={}", article_id, analysis.tone)
    return analysis
