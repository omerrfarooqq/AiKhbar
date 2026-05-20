"""TTS orchestration service.

Selects the configured primary provider, transparently falls back to the
open-source provider on failure, and caches synthesised audio on disk keyed by
content hash so identical text is never re-synthesised.
"""
from __future__ import annotations

from pathlib import Path

from loguru import logger

from app.core.config import settings
from app.core.constants import NarrationMode
from app.core.exceptions import ExternalServiceError
from app.schemas.tts import TTSResponse
from app.tts.base import TTSProvider, audio_cache_key, audio_path_for
from app.tts.coqui_tts import CoquiTTSProvider
from app.tts.urdu_orator import UrduOratorProvider


class TTSService:
    """Provider-agnostic Urdu speech synthesis with caching and fallback."""

    def __init__(self) -> None:
        self._primary: TTSProvider
        self._fallback: TTSProvider
        if settings.tts_primary == "coqui":
            self._primary = CoquiTTSProvider()
            self._fallback = UrduOratorProvider()
        else:
            self._primary = UrduOratorProvider()
            self._fallback = CoquiTTSProvider()

    async def synthesize(
        self,
        text: str,
        narration_mode: NarrationMode = NarrationMode.NEUTRAL,
        voice: str | None = None,
    ) -> TTSResponse:
        """Synthesise text to Urdu speech, returning a cache-aware response."""
        key = audio_cache_key(text, narration_mode, voice)
        path = audio_path_for(key)

        if path.exists() and path.stat().st_size > 0:
            logger.debug("TTS cache hit: {}", path.name)
            return TTSResponse(
                audio_path=str(path),
                audio_url=f"/static/audio/{path.name}",
                provider="cache",
                cached=True,
            )

        provider = await self._select_provider()
        try:
            await provider.synthesize(text, path, narration_mode, voice)
        except ExternalServiceError:
            # Primary failed at request time — try fallback once.
            if provider is self._primary:
                logger.warning("Primary TTS failed mid-request, using fallback")
                await self._fallback.synthesize(text, path, narration_mode, voice)
                provider = self._fallback
            else:
                raise

        return TTSResponse(
            audio_path=str(path),
            audio_url=f"/static/audio/{path.name}",
            provider=provider.name,
            cached=False,
        )

    async def _select_provider(self) -> TTSProvider:
        """Pick the primary if available, else the fallback."""
        if await self._primary.is_available():
            return self._primary
        logger.warning(
            "Primary TTS provider '{}' unavailable, switching to fallback '{}'",
            self._primary.name, self._fallback.name,
        )
        if await self._fallback.is_available():
            return self._fallback
        raise ExternalServiceError(
            "No TTS provider is available. Configure URDU_ORATOR_API_KEY or "
            "install Coqui TTS (`pip install TTS`)."
        )


_service: TTSService | None = None


def get_tts_service() -> TTSService:
    global _service
    if _service is None:
        _service = TTSService()
    return _service
