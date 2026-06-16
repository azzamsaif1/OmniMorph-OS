/**
 * MixedInterface — combined Visual + Audio mode.
 *
 * Shown when the user is distracted: presents an editor with
 * proactive voice-guided suggestions to re-engage focus.
 */

import React, { Suspense, lazy, useState } from "react";

const MonacoEditor = lazy(() =>
  import("@monaco-editor/react").then((m) => ({ default: m.default }))
);

const containerStyle = {
  display: "grid",
  gridTemplateColumns: "1fr 320px",
  gap: 12,
  padding: 16,
  height: "calc(100vh - 56px)",
};

const panelStyle = {
  background: "#12121e",
  borderRadius: 8,
  overflow: "hidden",
};

export default function MixedInterface({ mentalState }) {
  const [guidanceText, setGuidanceText] = useState(
    "You seem a bit distracted. Try focusing on the function you were editing."
  );
  const state = mentalState || {};

  const speak = (text) => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div style={containerStyle}>
      {/* Editor */}
      <div style={panelStyle}>
        <Suspense
          fallback={
            <div style={{ padding: 24, opacity: 0.4 }}>Loading editor...</div>
          }
        >
          <MonacoEditor
            height="100%"
            defaultLanguage="python"
            defaultValue="# Mixed mode — editor + voice guidance\n"
            theme="vs-dark"
            options={{
              fontSize: 14,
              minimap: { enabled: false },
              wordWrap: "on",
            }}
          />
        </Suspense>
      </div>

      {/* Guidance panel */}
      <div style={{ ...panelStyle, padding: 16 }}>
        <h3 style={{ fontSize: "0.9rem", marginBottom: 12, opacity: 0.8 }}>
          🔊 Voice Guidance
        </h3>

        <p style={{ fontSize: "0.85rem", lineHeight: 1.6, opacity: 0.7 }}>
          {guidanceText}
        </p>

        <button
          onClick={() => speak(guidanceText)}
          style={{
            marginTop: 16,
            padding: "8px 16px",
            background: "#6366f1",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            fontSize: "0.8rem",
          }}
        >
          🔊 Read Aloud
        </button>

        <div style={{ marginTop: 24, fontSize: "0.75rem", opacity: 0.3 }}>
          State: {state.state || "idle"} · Frustration:{" "}
          {((state.frustration || 0) * 100).toFixed(0)}%
        </div>
      </div>
    </div>
  );
}
