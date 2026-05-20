"""API v1 aggregate router — mounts every endpoint module."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    briefs,
    chat,
    health,
    news,
    stories,
    tts,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(briefs.router, prefix="/briefs", tags=["briefs"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(tts.router, prefix="/tts", tags=["tts"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
