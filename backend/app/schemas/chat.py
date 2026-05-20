"""Conversational news chat schemas."""
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """A conversational query, optionally scoped to a specific story cluster."""

    question: str
    cluster_id: str | None = None
    article_id: str | None = None
    history: list[ChatMessage] = Field(default_factory=list)
    language: str = "ur"


class RetrievedChunk(BaseModel):
    article_id: str
    headline: str
    source: str
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[RetrievedChunk] = Field(default_factory=list)
    cluster_id: str | None = None
