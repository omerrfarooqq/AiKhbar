"""TTS request/response schemas."""
from pydantic import BaseModel, Field

from app.core.constants import NarrationMode


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    narration_mode: NarrationMode = NarrationMode.NEUTRAL
    voice: str | None = None


class TTSResponse(BaseModel):
    audio_path: str
    audio_url: str
    duration_seconds: float | None = None
    provider: str
    cached: bool = False
