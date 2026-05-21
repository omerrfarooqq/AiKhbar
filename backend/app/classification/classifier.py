"""News classification service.

Uses the NVIDIA LLM as a zero-shot classifier. An LLM is a deliberate choice
over a fine-tuned transformer here: it handles Urdu well with no training data,
returns confidence + tags + region in one call, and the MVP volume is modest.
A dedicated transformer classifier can replace this later behind the same
`classify_article` interface.
"""
from __future__ import annotations

from loguru import logger

from app.classification.schemas import ClassificationResult
from app.core.config import settings
from app.core.constants import Category
from app.services import prompts
from app.services.nvidia_client import get_llm_client


def _coerce_category(value: str) -> Category:
    value = (value or "").strip().lower()
    for cat in Category:
        if cat.value == value:
            return cat
    return Category.GENERAL


async def classify_article(headline: str, body: str) -> ClassificationResult:
    """Classify a single article into a canonical category with metadata."""
    llm = get_llm_client()
    try:
        data = await llm.complete_json(
            system=prompts.CLASSIFY_SYSTEM,
            user=prompts.classify_user(headline, body),
            # The fast 8B model is enough for classification and has far more
            # headroom on the NVIDIA free-tier rate limit than the 70B model.
            model=settings.nvidia_llm_model_fast,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Classification failed, defaulting to GENERAL: {}", exc)
        return ClassificationResult(category=Category.GENERAL, confidence=0.0)

    return ClassificationResult(
        category=_coerce_category(data.get("category", "")),
        confidence=float(data.get("confidence", 0.0) or 0.0),
        tags=[str(t) for t in (data.get("tags") or [])][:8],
        region=data.get("region") or None,
    )
