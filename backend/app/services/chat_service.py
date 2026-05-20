"""Conversational news chat service.

RAG-grounded Q&A with conversational memory. Retrieval is scoped to a story
cluster when one is supplied, otherwise it searches the whole corpus. The
retrieved context is injected into the system turn and prior history is
preserved for follow-up questions.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cluster import StoryCluster
from app.rag.retriever import format_context, retrieve
from app.schemas.chat import ChatRequest, ChatResponse, RetrievedChunk
from app.services import prompts
from app.services.nvidia_client import get_llm_client

# History turns kept for context — bounds prompt size on long conversations.
_MAX_HISTORY_TURNS = 6


async def answer_question(db: AsyncSession, req: ChatRequest) -> ChatResponse:
    """Answer a conversational news question using RAG + chat history."""
    # Bias retrieval with the cluster title when the chat is story-scoped.
    query = req.question
    category: str | None = None
    if req.cluster_id:
        result = await db.execute(
            select(StoryCluster).where(StoryCluster.id == req.cluster_id)
        )
        cluster = result.scalar_one_or_none()
        if cluster:
            query = f"{cluster.title} {req.question}"
            category = cluster.category

    chunks = await retrieve(query, k=6, category=category)
    context = format_context(chunks)

    # Build the message list: system + grounded turn + recent history + question.
    messages: list[dict[str, str]] = [{"role": "system", "content": prompts.CHAT_SYSTEM}]
    for turn in req.history[-_MAX_HISTORY_TURNS:]:
        messages.append({"role": turn.role, "content": turn.content})
    messages.append(
        {"role": "user", "content": prompts.chat_user(req.question, context, req.language)}
    )

    llm = get_llm_client()
    answer = await llm.complete_chat(messages, temperature=0.4)

    logger.info("Chat answered | cluster={} | sources={}", req.cluster_id, len(chunks))
    return ChatResponse(
        answer=answer,
        cluster_id=req.cluster_id,
        sources=[
            RetrievedChunk(
                article_id=c.article_id,
                headline=c.headline,
                source=c.source,
                snippet=c.text[:240],
                score=c.score,
            )
            for c in chunks
        ],
    )
