"""Internal dataclasses for the classification pipeline."""
from dataclasses import dataclass, field

from app.core.constants import Category


@dataclass
class ClassificationResult:
    category: Category
    confidence: float = 0.0
    tags: list[str] = field(default_factory=list)
    region: str | None = None
