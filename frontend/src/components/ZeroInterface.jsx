/**
 * ZeroInterface — Background-only mode.
 *
 * Shown during flow state or idle; nearly invisible so the user
 * is not distracted.  Agents run silently in the background.
 */

import React from "react";

const containerStyle = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "calc(100vh - 56px)",
  padding: 32,
};

export default function ZeroInterface({ mentalState }) {
  const state = mentalState || {};
  const isFlow = state.state === "flow";

  return (
    <div style={containerStyle}>
      <div
        style={{
          width: 16,
          height: 16,
          borderRadius: "50%",
          background: isFlow ? "#22c55e" : "#374151",
          boxShadow: isFlow ? "0 0 24px #22c55e55" : "none",
          transition: "all 0.6s ease",
          marginBottom: 24,
        }}
      />
      <p style={{ fontSize: "0.8rem", opacity: 0.25 }}>
        {isFlow
          ? "Flow state detected — agents running silently."
          : "Idle — UCSK is resting with you."}
      </p>
    </div>
  );
}
