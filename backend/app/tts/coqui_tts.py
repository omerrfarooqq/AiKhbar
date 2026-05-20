"""Coqui TTS provider (open-source fallback).

Uses the Coqui XTTS-v2 multilingual model, which supports Urdu. The model is
heavy (torch + multi-GB weights), so the `TTS` package is an optional install
and the model is loaded lazily on first use.

Install: pip install TTS    (see requirements/base.txt — currently commented).
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from loguru import logger

from app.core.config import settings
from app.core.constants import NarrationMode
from app.core.exceptions import ConfigurationError
from app.tts.base import TTSProvider

# SSML-style markers are not understood by Coqui — strip them before synthesis.
_SSML_TOKENS = ("<break", "<emphasis", "</emphasis>", '"/>', "level=", "time=")


def _strip_ssml(text: str) -> str:
    cleaned = text
    for token in _SSML_TOKENS:
        cleaned = cleaned.replace(token, " ")
    return " ".join(cleaned.split())


class CoquiTTSProvider(TTSProvider):
    name = "coqui"

    def __init__(self) -> None:
        self._model = None

    def _load_model(self):  # noqa: ANN202
        if self._model is None:
            try:
                from TTS.api import TTS  # type: ignore
            except ImportError as exc:  # pragma: no cover
                raise ConfigurationError(
                    "Coqui TTS is not installed. Run `pip install TTS` to enable "
                    "the open-source TTS fallback."
                ) from exc
            logger.info("Loading Coqui model: {}", settings.coqui_model)
            self._model = TTS(settings.coqui_model)
        return self._model

    async def is_available(self) -> bool:
        try:
            import importlib.util

            return importlib.util.find_spec("TTS") is not None
        except Exception:  # noqa: BLE001
            return False

    async def synthesize(
        self,
        text: str,
        output_path: Path,
        narration_mode: NarrationMode = NarrationMode.NEUTRAL,
        voice: str | None = None,
    ) -> Path:
        clean = _strip_ssml(text)

        def _run() -> None:
            model = self._load_model()
            model.tts_to_file(
                text=clean,
                language="ur",
                file_path=str(output_path),
                speaker=voice,
            )

        # XTTS inference is CPU/GPU-bound and blocking.
        await asyncio.to_thread(_run)
        logger.info("Coqui synthesised -> {}", output_path.name)
        return output_path
