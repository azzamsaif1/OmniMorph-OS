/**
 * useSensing — captures keyboard / mouse / scroll events and streams
 * them to the backend via WebSocket, returning the latest mental state.
 */

import { useCallback, useEffect, useRef, useState } from "react";

const WS_URL =
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
  window.location.host +
  "/ws/guidance";

const INITIAL_RECONNECT_MS = 2000;
const MAX_RECONNECT_MS = 30000;

export function useSensing() {
  const [mentalState, setMentalState] = useState(null);
  const [directive, setDirective] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const reconnectDelay = useRef(INITIAL_RECONNECT_MS);

  useEffect(() => {
    function createSocket() {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectDelay.current = INITIAL_RECONNECT_MS;
      };

      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          if (msg.type === "state") setMentalState(msg);
          if (msg.type === "directive") setDirective(msg);
        } catch {
          /* ignore malformed frames */
        }
      };

      ws.onclose = () => {
        reconnectTimer.current = setTimeout(createSocket, reconnectDelay.current);
        reconnectDelay.current = Math.min(
          reconnectDelay.current * 2,
          MAX_RECONNECT_MS
        );
      };

      ws.onerror = () => {
        ws.close();
      };

      return ws;
    }

    createSocket();

    // All event handlers read from wsRef.current so they survive reconnects
    const send = (payload) => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(payload));
      }
    };

    const onKey = (e) => {
      send({ type: "behavior", event_type: "keystroke", key: e.key });
    };

    let lastMove = 0;
    const onMouse = (e) => {
      const now = Date.now();
      if (now - lastMove < 100) return;
      lastMove = now;
      send({
        type: "behavior",
        event_type: "mouse_move",
        x: e.clientX,
        y: e.clientY,
      });
    };

    const onScroll = () => {
      send({ type: "behavior", event_type: "scroll" });
    };

    const onClick = () => {
      send({ type: "behavior", event_type: "click" });
    };

    window.addEventListener("keydown", onKey);
    window.addEventListener("mousemove", onMouse);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("click", onClick);

    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("mousemove", onMouse);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("click", onClick);
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, []);

  const sendBehavior = useCallback(
    (eventType, payload = {}) => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({ type: "behavior", event_type: eventType, ...payload })
        );
      }
    },
    []
  );

  return { mentalState, directive, sendBehavior };
}
