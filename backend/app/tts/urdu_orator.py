"""Urdu Orator TTS provider (primary).

Talks to the Urdu Orator HTTP API. The exact request shape is centralised here
so that, if the upstream contract changes, only this file needs updating.
"""
from __future__ import annotations

from pathlib import Path

import httpx
from loguru import logger

from app.core.config import settings
from app.core.constants import NarrationMode
from app.core.exceptions import ConfigurationError, ExternalServiceError
from app.tts.base import TTSProvider

# Maps our narration modes to Urdu Orator style identifiers.
_STYLE_MAP = {
    NarrationMode.NEUTRAL: "news",
    NarrationMode.PODCAST: "conversational",
    NarrationMode.HEADLINE: "announcement",
}


class UrduOratorProvider(TTSProvider):
    name = "urdu_orator"

    def __init__(self) -> None:
        self._base_url = settings.urdu_orator_base_url.rstrip("/")
        self._api_key = settings.urdu_orator_api_key

    async def is_available(self) -> bool:
        if not self._api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.get(
                    f"{self._base_url}/health",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
            return resp.status_code == 200
        except httpx.HTTPError as exc:
            logger.warning("Urdu Orator health check failed: {}", exc)
            return False

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
            "text": text,
            "language": "ur",
            "style": _STYLE_MAP.get(narration_mode, "news"),
            "voice": voice or "default",
            "format": "mp3",
        }
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self._base_url}/tts",
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
