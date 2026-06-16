import React from "react";
import AdaptiveLayout from "./layouts/AdaptiveLayout.jsx";
import { useSensing } from "./hooks/useSensing.js";
import { useAdaptation } from "./hooks/useAdaptation.js";

/**
 * UCSK Root Application.
 *
 * Wires sensing hooks to the adaptive layout, which auto-switches
 * between Visual / Audio / Haptic / Mixed / Zero UI modes.
 */
export default function App() {
  const { mentalState, sendBehavior } = useSensing();
  const { directive, uiMode } = useAdaptation(mentalState);

  return (
    <div
      className="ucsk-app"
      style={{ minHeight: "100vh", background: "var(--bg, #0a0a0f)" }}
    >
      <header
        style={{
          padding: "12px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #1a1a2e",
        }}
      >
        <h1 style={{ fontSize: "1.1rem", fontWeight: 600, letterSpacing: 1 }}>
          UCSK
        </h1>
        <div style={{ fontSize: "0.8rem", opacity: 0.7 }}>
          State: <strong>{mentalState?.state || "idle"}</strong> &middot; Mode:{" "}
          <strong>{uiMode}</strong>
        </div>
      </header>

      <AdaptiveLayout
        uiMode={uiMode}
        directive={directive}
        mentalState={mentalState}
        onBehavior={sendBehavior}
      />
    </div>
  );
}
