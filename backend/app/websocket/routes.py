"""WebSocket routes — conversational chat over a live socket.

The chat socket lets the frontend hold a stateful conversation: it keeps the
message history server-side per connection and answers each question with the
RAG chat service.
"""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.db.session import AsyncSessionLocal
from app.schemas.chat import ChatMessage, ChatRequest
from app.services.chat_service import answer_question
from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/chat")
async def chat_socket(ws: WebSocket) -> None:
    """Stateful conversational news chat over WebSocket.

    Client sends: {"question": str, "cluster_id"?: str, "language"?: str}
    Server sends: {"answer": str, "sources": [...]}
    """
    await manager.connect("chat", ws)
    history: list[ChatMessage] = []
    try:
        while True:
            payload = await ws.receive_json()
            question = (payload or {}).get("question", "").strip()
            if not question:
                await ws.send_json({"error": "Empty question"})
                continue

            req = ChatRequest(
                question=question,
                cluster_id=payload.get("cluster_id"),
                article_id=payload.get("article_id"),
                language=payload.get("language", "ur"),
                history=history,
            )
            async with AsyncSessionLocal() as db:
                response = await answer_question(db, req)

            history.append(ChatMessage(role="user", content=question))
            history.append(ChatMessage(role="assistant", content=response.answer))
            history[:] = history[-12:]  # bound memory

            await ws.send_json(response.model_dump())
    except WebSocketDisconnect:
        manager.disconnect("chat", ws)
        logger.debug("Chat socket disconnected")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat socket error: {}", exc)
        manager.disconnect("chat", ws)


@router.websocket("/ws/feed")
async def feed_socket(ws: WebSocket) -> None:
    """Receive live notifications when new stories are ingested."""
    await manager.connect("feed", ws)
    try:
        while True:
            # Keep the connection alive; clients only listen here.
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect("feed", ws)
