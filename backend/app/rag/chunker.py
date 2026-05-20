"""Text chunking for RAG indexing.

Articles are split into overlapping word-windowed chunks so retrieval returns
focused, relevant passages rather than whole articles. Word-based windowing
works for both Urdu and English without language-specific tokenizers.
"""
from __future__ import annotations

_DEFAULT_CHUNK_WORDS = 220
_DEFAULT_OVERLAP_WORDS = 40


def chunk_text(
    text: str,
    chunk_words: int = _DEFAULT_CHUNK_WORDS,
    overlap: int = _DEFAULT_OVERLAP_WORDS,
) -> list[str]:
    """Split text into overlapping chunks of roughly `chunk_words` words."""
    words = text.split()
    if not words:
        return []
    if len(words) <= chunk_words:
        return [text.strip()]

    chunks: list[str] = []
    step = max(1, chunk_words - overlap)
    for start in range(0, len(words), step):
        window = words[start : start + chunk_words]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_words >= len(words):
            break
    return chunks
