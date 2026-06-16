/**
 * useSensing — captures keyboard / mouse / scroll events and streams
 * them to the backend via WebSocket, returning the latest mental state.
 */

import { useCallback, useEffect, useRef, useState } from "react";

const WS_URL =
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
  window.location.host +
  "/ws/guidance";

export function useSensing() {
  const [mentalState, setMentalState] = useState(null);
  const [directive, setDirective] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === "state") setMentalState(msg);
        if (msg.type === "directive") setDirective(msg);
      } catch {
        /* ignore */
      }
    };

    ws.onclose = () => {
      // Reconnect after 2 s
      setTimeout(() => {
        wsRef.current = new WebSocket(WS_URL);
      }, 2000);
    };

    // -- Keyboard listener --
    const onKey = (e) => {
      ws.readyState === WebSocket.OPEN &&
        ws.send(
          JSON.stringify({
            type: "behavior",
            event_type: "keystroke",
            key: e.key,
          })
        );
    };

    // -- Mouse listener --
    let lastMove = 0;
    const onMouse = (e) => {
      const now = Date.now();
      if (now - lastMove < 100) return; // throttle to 10 Hz
      lastMove = now;
      ws.readyState === WebSocket.OPEN &&
        ws.send(
          JSON.stringify({
            type: "behavior",
            event_type: "mouse_move",
            x: e.clientX,
            y: e.clientY,
          })
        );
    };

    // -- Scroll listener --
    const onScroll = () => {
      ws.readyState === WebSocket.OPEN &&
        ws.send(JSON.stringify({ type: "behavior", event_type: "scroll" }));
    };

    // -- Click listener --
    const onClick = () => {
      ws.readyState === WebSocket.OPEN &&
        ws.send(JSON.stringify({ type: "behavior", event_type: "click" }));
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
      ws.close();
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
