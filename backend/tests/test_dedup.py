"""Unit tests for content hashing used in deduplication."""
from app.scraping.hashing import content_hash


def test_identical_content_same_hash() -> None:
    a = content_hash("Headline", "Body text here")
    b = content_hash("Headline", "Body text here")
    assert a == b


def test_whitespace_and_case_insensitive() -> None:
    a = content_hash("Big   News", "Some  Body")
    b = content_hash("big news", "some body")
    assert a == b


def test_different_content_different_hash() -> None:
    a = content_hash("Headline A", "Body")
    b = content_hash("Headline B", "Body")
    assert a != b
