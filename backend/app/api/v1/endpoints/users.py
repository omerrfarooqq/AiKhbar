"""User and personalization endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.models.user import User, UserInteraction
from app.personalization.engine import personalized_feed, recompute_affinity
from app.schemas.article import ArticleSummaryCard
from app.schemas.common import MessageResponse
from app.schemas.user import InteractionCreate, UserCreate, UserRead

router = APIRouter()


@router.post("", response_model=UserRead, summary="Create a user")
async def create_user(
    payload: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserRead:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise ValidationError(f"User with email {payload.email} already exists")
    user = User(
        email=payload.email,
        display_name=payload.display_name,
        preferred_categories=payload.preferred_categories,
    )
    db.add(user)
    await db.flush()
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead, summary="Get a user")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)) -> UserRead:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")
    return UserRead.model_validate(user)


@router.post(
    "/interactions", response_model=MessageResponse, summary="Record an interaction"
)
async def record_interaction(
    payload: InteractionCreate, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Track a user interaction; affinity is recomputed asynchronously."""
    user = await db.get(User, payload.user_id)
    if user is None:
        raise NotFoundError(f"User {payload.user_id} not found")

    db.add(UserInteraction(**payload.model_dump()))
    await db.flush()
    # Cheap enough to recompute inline for an MVP; move to a task at scale.
    await recompute_affinity(db, payload.user_id)
    return MessageResponse(message="Interaction recorded")


@router.get(
    "/{user_id}/feed",
    response_model=list[ArticleSummaryCard],
    summary="Personalized feed",
)
async def get_feed(
    user_id: str,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[ArticleSummaryCard]:
    articles = await personalized_feed(db, user_id, limit=limit)
    return [ArticleSummaryCard.model_validate(a) for a in articles]
