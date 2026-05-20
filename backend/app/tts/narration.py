"""Narration text preparation.

Converts a plain summary into a script with broadcast structure: an intro,
inter-story pauses and headline emphasis. Pauses use SSML-style break hints
that providers can interpret or strip.
"""
from __future__ import annotations

from app.core.constants import NarrationMode

# Marker the audio joiner / providers treat as a pause between segments.
PAUSE = " <break time=\"700ms\"/> "

_INTROS: dict[NarrationMode, str] = {
    NarrationMode.NEUTRAL: "",
    NarrationMode.PODCAST: "آداب، یہ ہے آپ کا اے آئی خبر بریفنگ۔",
    NarrationMode.HEADLINE: "آج کی اہم خبریں۔",
}


def build_narration(
    segments: list[str], mode: NarrationMode = NarrationMode.NEUTRAL
) -> str:
    """Join story segments into a single narration script.

    `segments` is an ordered list of per-story text blocks.
    """
    parts: list[str] = []
    intro = _INTROS.get(mode, "")
    if intro:
        parts.append(intro)
    parts.extend(s.strip() for s in segments if s.strip())
    return PAUSE.join(parts)


def emphasize_headline(headline: str, body: str) -> str:
    """Prepend an emphasised headline before a story body for narration."""
    return f"<emphasis level=\"strong\">{headline.strip()}</emphasis>.{PAUSE}{body.strip()}"
