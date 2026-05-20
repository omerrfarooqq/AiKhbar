import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * WebSocket hook for the live conversational chat endpoint (/ws/chat).
 * Falls back gracefully: callers can use the REST endpoint if `ready` is false.
 */
export function useChatSocket() {
  const wsRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/chat`);
    wsRef.current = ws;

    ws.onopen = () => setReady(true);
    ws.onclose = () => setReady(false);
    ws.onmessage = (ev) => {
      try {
        setLastMessage(JSON.parse(ev.data));
      } catch {
        /* ignore malformed frames */
      }
    };

    return () => ws.close();
  }, []);

  const send = useCallback((payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    }
  }, []);

  return { ready, lastMessage, send };
}
