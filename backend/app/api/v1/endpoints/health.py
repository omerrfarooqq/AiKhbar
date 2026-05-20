"""Health and system status endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.rag.vector_store import get_vector_store

router = APIRouter()


@router.get("/health", summary="Liveness probe")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@router.get("/status", summary="Detailed system status")
async def status(db: AsyncSession = Depends(get_db)) -> dict:
    """Reports connectivity of dependencies — useful for ops dashboards."""
    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        db_ok = False

    vector_count = 0
    try:
        vector_count = get_vector_store().size
    except Exception:  # noqa: BLE001
        pass

    return {
        "app": settings.app_name,
        "env": settings.app_env,
        "database": "ok" if db_ok else "error",
        "vector_store": {"vectors": vector_count},
        "nvidia_configured": bool(settings.nvidia_api_key),
        "tts_primary": settings.tts_primary,
        "scheduler_enabled": settings.scheduler_enabled,
    }
