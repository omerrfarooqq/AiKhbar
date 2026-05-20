"""Unit tests for narration script assembly."""
from app.core.constants import NarrationMode
from app.tts.narration import PAUSE, build_narration, emphasize_headline


def test_build_narration_inserts_pauses_between_segments() -> None:
    script = build_narration(["story one", "story two"], mode=NarrationMode.NEUTRAL)
    assert PAUSE in script
    assert "story one" in script and "story two" in script


def test_podcast_mode_adds_intro() -> None:
    script = build_narration(["story"], mode=NarrationMode.PODCAST)
    assert script.startswith("آداب")


def test_emphasize_headline_wraps_headline() -> None:
    out = emphasize_headline("Big Story", "Details follow.")
    assert "<emphasis" in out
    assert "Big Story" in out
