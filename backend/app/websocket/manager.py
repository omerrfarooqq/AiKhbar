"""WebSocket connection manager.

Tracks active connections grouped by channel so the backend can broadcast
events (e.g. 'new stories ingested') to all interested clients.
"""
from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections grouped by named channel."""

    def __init__(self) -> None:
        self._channels: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, channel: str, ws: WebSocket) -> None:
        await ws.accept()
        self._channels[channel].add(ws)
        logger.debug("WS connected | channel={} | total={}",
                     channel, len(self._channels[channel]))

    def disconnect(self, channel: str, ws: WebSocket) -> None:
        self._channels[channel].discard(ws)

    async def broadcast(self, channel: str, message: dict) -> None:
        """Send a JSON message to every connection on a channel."""
        dead: list[WebSocket] = []
        for ws in self._channels.get(channel, set()):
            try:
                await ws.send_json(message)
            except Exception:  # noqa: BLE001
                dead.append(ws)
        for ws in dead:
            self.disconnect(channel, ws)


manager = ConnectionManager()
