"""AiKhbar FastAPI application entrypoint.

Wires together configuration, logging, the API router, WebSocket routes, static
audio serving, the background scheduler and exception handling under a single
ASGI app with a managed lifespan.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine
from app.services.scheduler import shutdown_scheduler, start_scheduler
from app.websocket.routes import router as ws_router


@asynccontextmanager
async def lifespan(_: FastAPI):  # noqa: ANN201
    """Startup / shutdown: schema bootstrap, scheduler, graceful teardown."""
    configure_logging()
    logger.info("Starting {} ({})", settings.app_name, settings.app_env)

    # Dev convenience: auto-create tables. Production uses Alembic migrations.
    if not settings.is_production:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema ensured (dev mode)")

    start_scheduler()
    yield

    shutdown_scheduler()
    await engine.dispose()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="AiKhbar API",
        description="Urdu AI-powered news intelligence and audio briefing platform.",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(ws_router)

    # Serve generated TTS audio files.
    audio_dir = Path(settings.audio_cache_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static/audio", StaticFiles(directory=str(audio_dir)), name="audio")

    @app.get("/", tags=["root"], summary="API root")
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": "0.1.0",
            "docs": "/docs",
            "api": settings.api_v1_prefix,
        }

    return app


app = create_app()
