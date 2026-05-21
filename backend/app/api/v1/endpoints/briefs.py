"""Daily brief endpoints — the one-click flagship feature."""
from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.story import DailyBriefRequest
from app.services.daily_brief import generate_audio_digest, generate_daily_brief

router = APIRouter()


@router.post("/daily", summary="Generate the one-click daily brief")
async def daily_brief(
    req: DailyBriefRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Produce top stories with unified summaries and opinions.

    Audio is generated separately, on demand: per story via /tts/synthesize,
    or as a combined 2 to 3 minute bulletin via /briefs/audio-digest.
    """
    brief = await generate_daily_brief(db, req)
    return {
        "stories": [asdict(s) for s in brief.stories],
        "narration_text": brief.narration_text,
        "audio_url": brief.audio_url,
        "audio_provider": brief.audio_provider,
        "story_count": len(brief.stories),
    }


@router.post("/audio-digest", summary="2 to 3 minute Urdu audio news brief")
async def audio_digest(db: AsyncSession = Depends(get_db)) -> dict:
    """Generate a concise 2 to 3 minute narrated Urdu bulletin of top stories."""
    return await generate_audio_digest(db)
