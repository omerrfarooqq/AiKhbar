"""TTS provider abstraction.

Every concrete provider (Urdu Orator, Coqui) implements `TTSProvider`, so the
service layer can switch primary/fallback without knowing transport details.
"""
from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import settings
from app.core.constants import NarrationMode


class TTSProvider(ABC):
    """Interface for an Urdu-capable speech synthesiser."""

    name: str = "base"

    @abstractmethod
    async def is_available(self) -> bool:
        """Return True if this provider is configured and reachable."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        output_path: Path,
        narration_mode: NarrationMode = NarrationMode.NEUTRAL,
        voice: str | None = None,
    ) -> Path:
        """Synthesise `text` to an audio file at `output_path`. Return the path."""


def audio_cache_key(text: str, mode: NarrationMode, voice: str | None) -> str:
    """Deterministic filename for a given (text, mode, voice) triple."""
    raw = f"{text}|{mode.value}|{voice or 'default'}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def audio_path_for(key: str) -> Path:
    cache_dir = Path(settings.audio_cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{key}.mp3"
