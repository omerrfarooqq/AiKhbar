"""News endpoints — article listing, filtering, detail and scrape trigger."""
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import Category
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.schemas.article import ArticleRead, ArticleSummaryCard
from app.schemas.common import JobResponse, Page
from app.services import article_repository
from app.services.ingestion_pipeline import run_ingestion

router = APIRouter()


@router.get("", response_model=Page[ArticleSummaryCard], summary="List / filter news")
async def list_news(
    category: Category | None = Query(None, description="Filter by category"),
    source: str | None = Query(None, description="Filter by source key"),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Page[ArticleSummaryCard]:
    items, total = await article_repository.list_articles(
        db,
        category=category.value if category else None,
        source=source,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return Page(
        items=[ArticleSummaryCard.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/categories", summary="Category list with article counts")
async def categories(db: AsyncSession = Depends(get_db)) -> dict:
    counts = await article_repository.category_counts(db)
    return {
        "categories": [
            {"key": c.value, "count": counts.get(c.value, 0)} for c in Category
        ]
    }


@router.get("/{article_id}", response_model=ArticleRead, summary="Article detail")
async def get_article(
    article_id: str, db: AsyncSession = Depends(get_db)
) -> ArticleRead:
    article = await article_repository.get_by_id(db, article_id)
    if article is None:
        raise NotFoundError(f"Article {article_id} not found")
    return ArticleRead.model_validate(article)


@router.post("/scrape", response_model=JobResponse, summary="Trigger ingestion run")
async def trigger_scrape(background: BackgroundTasks) -> JobResponse:
    """Kick off a full ingestion pipeline run in the background."""
    background.add_task(run_ingestion)
    return JobResponse(
        job_id="ingestion",
        status="accepted",
        message="News ingestion started in the background.",
    )
