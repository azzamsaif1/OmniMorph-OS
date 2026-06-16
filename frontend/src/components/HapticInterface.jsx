/**
 * HapticInterface — Minimal UI with WebHID tactile cues.
 *
 * A stripped-down view with large, touch-friendly controls and
 * haptic feedback when supported by the device.
 */

import React, { useCallback, useState } from "react";

const containerStyle = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "calc(100vh - 56px)",
  padding: 32,
  gap: 24,
};

const cardStyle = {
  background: "#1a1a2e",
  borderRadius: 16,
  padding: "24px 32px",
  width: "100%",
  maxWidth: 400,
  textAlign: "center",
  cursor: "pointer",
  transition: "transform 0.15s, box-shadow 0.15s",
};

export default function HapticInterface({ mentalState }) {
  const [lastAction, setLastAction] = useState(null);

  const triggerHaptic = useCallback((action) => {
    // Vibration API (mobile / supported devices)
    if (navigator.vibrate) {
      navigator.vibrate(50);
    }
    setLastAction(action);
  }, []);

  const state = mentalState || {};

  return (
    <div style={containerStyle}>
      <h2 style={{ fontSize: "1.2rem", fontWeight: 500, opacity: 0.7 }}>
        Haptic Mode
      </h2>

      <div
        style={cardStyle}
        onClick={() => triggerHaptic("suggestion")}
        onMouseDown={(e) =>
          (e.currentTarget.style.transform = "scale(0.97)")
        }
        onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      >
        <p style={{ fontSize: "0.9rem" }}>💡 View Agent Suggestions</p>
      </div>

      <div
        style={cardStyle}
        onClick={() => triggerHaptic("break")}
        onMouseDown={(e) =>
          (e.currentTarget.style.transform = "scale(0.97)")
        }
        onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      >
        <p style={{ fontSize: "0.9rem" }}>☕ Take a Break</p>
      </div>

      <div
        style={cardStyle}
        onClick={() => triggerHaptic("challenge")}
        onMouseDown={(e) =>
          (e.currentTarget.style.transform = "scale(0.97)")
        }
        onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      >
        <p style={{ fontSize: "0.9rem" }}>⚔️ Start a Challenge</p>
      </div>

      {lastAction && (
        <p style={{ fontSize: "0.75rem", opacity: 0.4 }}>
          Last: {lastAction}
        </p>
      )}

      <div style={{ fontSize: "0.75rem", opacity: 0.3, marginTop: 16 }}>
        State: {state.state || "idle"} · Focus:{" "}
        {((state.focus || 0) * 100).toFixed(0)}%
      </div>
    </div>
  );
}
