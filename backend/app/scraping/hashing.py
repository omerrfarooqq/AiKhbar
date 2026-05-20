"""Content hashing utilities for deduplication.

Kept dependency-free (stdlib only) so it can be imported by lightweight
consumers and tests without pulling in scraping libraries.
"""
from __future__ import annotations

import hashlib
import re

_WS = re.compile(r"\s+")


def content_hash(headline: str, body: str) -> str:
    """Stable SHA-256 over normalised text — used for exact-duplicate detection."""
    norm = _WS.sub(" ", f"{headline} {body}").strip().lower()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()
