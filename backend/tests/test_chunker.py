"""Unit tests for the RAG text chunker."""
from app.rag.chunker import chunk_text


def test_short_text_is_single_chunk() -> None:
    text = "یہ ایک مختصر خبر ہے۔"
    assert chunk_text(text) == [text]


def test_long_text_is_split_with_overlap() -> None:
    words = " ".join(f"word{i}" for i in range(600))
    chunks = chunk_text(words, chunk_words=200, overlap=40)
    assert len(chunks) > 1
    # Consecutive chunks should share overlapping words.
    first_tail = chunks[0].split()[-40:]
    second_head = chunks[1].split()[:40]
    assert first_tail == second_head


def test_empty_text_returns_empty_list() -> None:
    assert chunk_text("") == []
