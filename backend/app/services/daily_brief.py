"""One-click daily brief orchestrator.

Composes the flagship feature: selects top stories (personalized if a user is
given), generates unified summaries, optionally aggregates opinions, builds a
single narrated Urdu script and synthesises it to audio.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import BriefMode, NarrationMode
from app.models.user import User
from app.personalization.engine import personalized_feed
from app.rag.opinion_aggregator import aggregate_opinions
from app.schemas.story import DailyBriefRequest
from app.services import cluster_repository, prompts
from app.services.nvidia_client import get_llm_client
from app.summarization.summarizer import summarize_cluster
from app.tts.narration import build_narration, emphasize_headline
from app.tts.service import get_tts_service


@dataclass
class BriefStory:
    cluster_id: str
    title: str
    category: str
    summary: str
    opinions: list[dict] = field(default_factory=list)


@dataclass
class DailyBrief:
    stories: list[BriefStory] = field(default_factory=list)
    narration_text: str = ""
    audio_url: str | None = None
    audio_provider: str | None = None


async def _select_clusters(db: AsyncSession, req: DailyBriefRequest):  # noqa: ANN202
    """Pick the clusters for the brief — personalized when a user is supplied."""
    if not req.user_id:
        return await cluster_repository.top_clusters(db, limit=req.max_stories)

    user = await db.get(User, req.user_id)
    if user is None:
        return await cluster_repository.top_clusters(db, limit=req.max_stories)

    # Rank recent personalized articles, then take their distinct clusters.
    articles = await personalized_feed(db, req.user_id, limit=req.max_stories * 5)
    seen: set[str] = set()
    cluster_ids: list[str] = []
    for art in articles:
        if art.cluster_id and art.cluster_id not in seen:
            seen.add(art.cluster_id)
            cluster_ids.append(art.cluster_id)
        if len(cluster_ids) >= req.max_stories:
            break

    clusters = []
    for cid in cluster_ids:
        cluster = await cluster_repository.get_with_relations(db, cid)
        if cluster:
            clusters.append(cluster)
    return clusters or await cluster_repository.top_clusters(db, limit=req.max_stories)


async def generate_daily_brief(
    db: AsyncSession, req: DailyBriefRequest
) -> DailyBrief:
    """Build the complete daily brief (summaries + opinions + Urdu audio)."""
    logger.info("Generating daily brief | user={} | stories={}",
                req.user_id, req.max_stories)

    clusters = await _select_clusters(db, req)
    brief = DailyBrief()
    narration_segments: list[str] = []

    for cluster in clusters:
        summary = await summarize_cluster(db, cluster.id, mode=req.mode)

        opinions_payload: list[dict] = []
        if req.include_opinions:
            try:
                opinions = await aggregate_opinions(db, cluster.id)
                opinions_payload = [
                    {"perspective": o.perspective, "stance": o.stance,
                     "summary": o.summary}
                    for o in opinions
                ]
            except Exception as exc:  # noqa: BLE001
                logger.warning("Opinion aggregation skipped for {}: {}",
                               cluster.id, exc)

        brief.stories.append(
            BriefStory(
                cluster_id=cluster.id,
                title=cluster.title,
                category=cluster.category,
                summary=summary.content,
                opinions=opinions_payload,
            )
        )
        narration_segments.append(
            emphasize_headline(cluster.title, summary.content)
        )

    brief.narration_text = build_narration(
        narration_segments, mode=NarrationMode.PODCAST
    )

    if req.include_audio and brief.narration_text:
        try:
            tts = get_tts_service()
            audio = await tts.synthesize(
                brief.narration_text, narration_mode=NarrationMode.PODCAST
            )
            brief.audio_url = audio.audio_url
            brief.audio_provider = audio.provider

            # Cache audio path against the first story's short summary.
            if brief.stories:
                first_summary = await summarize_cluster(
                    db, brief.stories[0].cluster_id, mode=req.mode
                )
                first_summary.audio_path = audio.audio_path
        except Exception as exc:  # noqa: BLE001
            logger.warning("Daily brief audio generation failed: {}", exc)

    await db.flush()
    logger.info("Daily brief ready | stories={} | audio={}",
                len(brief.stories), bool(brief.audio_url))
    return brief


async def generate_audio_digest(db: AsyncSession, max_stories: int = 6) -> dict:
    """Build a concise 2 to 3 minute Urdu audio bulletin of the top stories.

    Unlike per-story narration, this condenses the most important stories into
    a single short script and synthesises one audio file.
    """
    clusters = await cluster_repository.top_clusters(db, limit=max_stories)
    if not clusters:
        return {"audio_url": None, "audio_provider": None,
                "narration_text": "", "story_count": 0}

    summaries: list[str] = []
    for cluster in clusters:
        summary = await summarize_cluster(db, cluster.id, mode=BriefMode.SHORT)
        summaries.append(f"{cluster.title}\n{summary.content}")
    await db.flush()

    llm = get_llm_client()
    script = await llm.complete(
        system=prompts.DIGEST_SYSTEM,
        user=prompts.digest_user(summaries),
        model=settings.nvidia_llm_model_fast,
        temperature=0.3,
        max_tokens=900,
    )

    audio_url: str | None = None
    audio_provider: str | None = None
    try:
        audio = await get_tts_service().synthesize(
            script, narration_mode=NarrationMode.PODCAST
        )
        audio_url = audio.audio_url
        audio_provider = audio.provider
    except Exception as exc:  # noqa: BLE001
        logger.warning("Audio digest TTS failed: {}", exc)

    logger.info("Audio digest ready | stories={} | audio={}",
                len(clusters), bool(audio_url))
    return {
        "audio_url": audio_url,
        "audio_provider": audio_provider,
        "narration_text": script,
        "story_count": len(clusters),
    }
