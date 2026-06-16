/**
 * VisualInterface — Full Monaco Editor + Three.js visualisation mode.
 *
 * The primary rich interface shown when the user is focused.
 */

import React, { Suspense, lazy } from "react";

// Lazy-load heavy deps
const MonacoEditor = lazy(() =>
  import("@monaco-editor/react").then((m) => ({ default: m.default }))
);

const containerStyle = {
  display: "grid",
  gridTemplateColumns: "1fr 360px",
  gap: 12,
  padding: 16,
  height: "calc(100vh - 56px)",
};

const panelStyle = {
  background: "#12121e",
  borderRadius: 8,
  overflow: "hidden",
};

const statsBar = {
  display: "flex",
  gap: 16,
  padding: "8px 12px",
  fontSize: "0.75rem",
  opacity: 0.6,
};

export default function VisualInterface({ mentalState }) {
  const state = mentalState || {};

  return (
    <div style={containerStyle}>
      {/* Editor panel */}
      <div style={panelStyle}>
        <div style={statsBar}>
          <span>Focus: {((state.focus || 0) * 100).toFixed(0)}%</span>
          <span>Fatigue: {((state.fatigue || 0) * 100).toFixed(0)}%</span>
          <span>Engagement: {((state.engagement || 0) * 100).toFixed(0)}%</span>
        </div>
        <Suspense
          fallback={
            <div style={{ padding: 24, opacity: 0.4 }}>Loading editor...</div>
          }
        >
          <MonacoEditor
            height="calc(100% - 36px)"
            defaultLanguage="python"
            defaultValue="# UCSK — start coding here\n"
            theme="vs-dark"
            options={{
              fontSize: 14,
              minimap: { enabled: false },
              wordWrap: "on",
            }}
          />
        </Suspense>
      </div>

      {/* Sidebar — agent suggestions + 3-D visualisation placeholder */}
      <div style={{ ...panelStyle, padding: 16 }}>
        <h3 style={{ fontSize: "0.9rem", marginBottom: 12, opacity: 0.8 }}>
          Agent Suggestions
        </h3>
        <p style={{ fontSize: "0.8rem", opacity: 0.5, lineHeight: 1.5 }}>
          Agents are analysing your work context. Suggestions will appear here
          when relevant patterns are detected.
        </p>

        <div
          style={{
            marginTop: 24,
            padding: 16,
            background: "#1a1a2e",
            borderRadius: 8,
            textAlign: "center",
            fontSize: "0.75rem",
            opacity: 0.4,
          }}
        >
          Three.js cognitive map placeholder
        </div>
      </div>
    </div>
  );
}
