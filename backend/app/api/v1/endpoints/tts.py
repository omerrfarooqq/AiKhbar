"""Text-to-speech endpoint — generate Urdu audio from text."""
from fastapi import APIRouter

from app.schemas.tts import TTSRequest, TTSResponse
from app.tts.service import get_tts_service

router = APIRouter()


@router.post("/synthesize", response_model=TTSResponse, summary="Synthesise Urdu audio")
async def synthesize(req: TTSRequest) -> TTSResponse:
    """Convert text to an Urdu audio file (cached, with provider fallback)."""
    service = get_tts_service()
    return await service.synthesize(
        req.text, narration_mode=req.narration_mode, voice=req.voice
    )
