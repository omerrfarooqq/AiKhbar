"""Urdu Orator TTS provider (primary).

Wraps the Uplift AI Orator REST API, which synthesises Pakistani-language
(Urdu) speech. The 'sk_api_...' developer key authenticates as a bearer token.
The request shape is centralised here so upstream contract changes touch only
this file.
"""
from __future__ import annotations

from pathlib import Path

import httpx
from loguru import logger

from app.core.config import settings
from app.core.constants import NarrationMode
from app.core.exceptions import ConfigurationError, ExternalServiceError
from app.tts.base import TTSProvider


class UrduOratorProvider(TTSProvider):
    """Uplift AI Orator text-to-speech."""

    name = "urdu_orator"

    def __init__(self) -> None:
        self._base_url = settings.urdu_orator_base_url.rstrip("/")
        self._api_key = settings.urdu_orator_api_key
        self._voice_id = settings.urdu_orator_voice_id
        self._output_format = settings.urdu_orator_output_format

    async def is_available(self) -> bool:
        # A configured key is sufficient; transient API failures are handled
        # by the fallback at synthesis time rather than probed here.
        return bool(self._api_key)

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        narration_mode: NarrationMode = NarrationMode.NEUTRAL,
        voice: str | None = None,
    ) -> Path:
        if not self._api_key:
            raise ConfigurationError("URDU_ORATOR_API_KEY is not set")

        payload = {
            "voiceId": voice or self._voice_id,
            "text": text,
            "outputFormat": self._output_format,
        }
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self._base_url}/synthesis/text-to-speech",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=payload,
                )
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Urdu Orator synthesis failed: {}", exc)
            raise ExternalServiceError(f"Urdu Orator TTS failed: {exc}") from exc

        output_path.write_bytes(resp.content)
        logger.info("Urdu Orator synthesised {} bytes -> {}",
                    len(resp.content), output_path.name)
        return output_path
