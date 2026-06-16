/**
 * useWebSocket — Generic WebSocket hook for live data streams.
 *
 * Provides a reusable WebSocket connection with auto-reconnect,
 * message parsing, and connection state tracking.
 */

import { useEffect, useRef, useState, useCallback } from "react";

const RECONNECT_DELAY = 2000;

/**
 * @param {string} url - WebSocket endpoint URL
 * @param {object} options
 * @param {function} options.onMessage - Callback for incoming messages
 * @param {boolean} options.autoConnect - Connect automatically (default: true)
 * @returns {{ send, isConnected, lastMessage, connect, disconnect }}
 */
export function useWebSocket(url, { onMessage, autoConnect = true } = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const shouldReconnect = useRef(autoConnect);
  const onMessageRef = useRef(onMessage);

  useEffect(() => {
    onMessageRef.current = onMessage;
  });

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        setLastMessage(data);
        if (onMessageRef.current) onMessageRef.current(data);
      } catch {
        /* ignore malformed frames */
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      if (shouldReconnect.current) {
        reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [url]);

  const disconnect = useCallback(() => {
    shouldReconnect.current = false;
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const payload = typeof data === "string" ? data : JSON.stringify(data);
      wsRef.current.send(payload);
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      shouldReconnect.current = true;
      connect();
    }
    return () => {
      shouldReconnect.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [autoConnect, connect]);

  return { send, isConnected, lastMessage, connect, disconnect };
}
