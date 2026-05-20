"""Conversational news chat endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import answer_question

router = APIRouter()


@router.post("", response_model=ChatResponse, summary="Ask a question about the news")
async def chat(
    req: ChatRequest, db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """RAG-grounded conversational answer with cited sources."""
    return await answer_question(db, req)
