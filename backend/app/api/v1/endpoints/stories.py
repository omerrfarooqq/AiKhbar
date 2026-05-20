"""Story cluster endpoints — clusters, summaries, opinions, timeline, analysis."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.media_analysis import analyze_article
from app.core.constants import Category
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.rag.opinion_aggregator import aggregate_opinions
from app.rag.timeline_builder import build_timeline
from app.schemas.story import (
    ClusterDetail,
    ClusterRead,
    OpinionRead,
    SummarizeRequest,
    SummaryRead,
    TimelineEventRead,
)
from app.services import cluster_repository
from app.summarization.summarizer import summarize_cluster

router = APIRouter()


@router.get("", response_model=list[ClusterRead], summary="List story clusters")
async def list_stories(
    category: Category | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[ClusterRead]:
    clusters = await cluster_repository.list_clusters(
        db, category=category.value if category else None, limit=limit
    )
    return [ClusterRead.model_validate(c) for c in clusters]


@router.get("/top", response_model=list[ClusterRead], summary="Top stories now")
async def top_stories(
    limit: int = Query(6, ge=1, le=15),
    category: Category | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[ClusterRead]:
    clusters = await cluster_repository.top_clusters(
        db, limit=limit, category=category.value if category else None
    )
    return [ClusterRead.model_validate(c) for c in clusters]


@router.get("/{cluster_id}", response_model=ClusterDetail, summary="Story detail")
async def get_story(
    cluster_id: str, db: AsyncSession = Depends(get_db)
) -> ClusterDetail:
    cluster = await cluster_repository.get_with_relations(db, cluster_id)
    if cluster is None:
        raise NotFoundError(f"Story cluster {cluster_id} not found")
    return ClusterDetail.model_validate(cluster)


@router.post(
    "/{cluster_id}/summary", response_model=SummaryRead, summary="Generate summary"
)
async def generate_summary(
    cluster_id: str,
    req: SummarizeRequest,
    db: AsyncSession = Depends(get_db),
) -> SummaryRead:
    summary = await summarize_cluster(
        db, cluster_id, mode=req.mode, language=req.language
    )
    return SummaryRead.model_validate(summary)


@router.post(
    "/{cluster_id}/opinions",
    response_model=list[OpinionRead],
    summary="Aggregate opinions (RAG)",
)
async def generate_opinions(
    cluster_id: str,
    force: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> list[OpinionRead]:
    opinions = await aggregate_opinions(db, cluster_id, force=force)
    return [OpinionRead.model_validate(o) for o in opinions]


@router.post(
    "/{cluster_id}/timeline",
    response_model=list[TimelineEventRead],
    summary="Build historical timeline",
)
async def generate_timeline(
    cluster_id: str,
    force: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> list[TimelineEventRead]:
    events = await build_timeline(db, cluster_id, force=force)
    return [TimelineEventRead.model_validate(e) for e in events]


@router.post("/articles/{article_id}/analyze", summary="Media analysis of an article")
async def analyze(article_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    analysis = await analyze_article(db, article_id)
    return {
        "article_id": article_id,
        "tone": analysis.tone,
        "political_leaning": analysis.political_leaning,
        "sentiment_score": analysis.sentiment_score,
        "propaganda_indicators": analysis.propaganda_indicators,
        "reasoning": analysis.reasoning,
    }
