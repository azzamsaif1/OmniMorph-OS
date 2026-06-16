/**
 * useAdaptation — consumes the mental-state stream and backend directives,
 * returns the current UI mode with hysteresis to prevent flicker.
 */

import { useEffect, useRef, useState } from "react";

const MODE_COOLDOWN_MS = 2000; // Minimum time between mode switches

export function useAdaptation(mentalState, backendDirective) {
  const [uiMode, setUiMode] = useState("visual");
  const lastSwitch = useRef(0);

  // Derive mode from mental state
  useEffect(() => {
    if (!mentalState) return;

    const stateToMode = {
      focused: "visual",
      flow: "zero",
      distracted: "mixed",
      fatigued: "audio",
      frustrated: "audio",
      idle: "zero",
    };

    const newMode = stateToMode[mentalState.state] || "visual";
    const now = Date.now();

    if (newMode !== uiMode && now - lastSwitch.current > MODE_COOLDOWN_MS) {
      lastSwitch.current = now;
      setUiMode(newMode);
    }
  }, [mentalState, uiMode]);

  // Accept explicit directives from the backend WebSocket
  useEffect(() => {
    if (!backendDirective) return;
    if (backendDirective.ui_mode && backendDirective.ui_mode !== uiMode) {
      const now = Date.now();
      if (now - lastSwitch.current > MODE_COOLDOWN_MS) {
        lastSwitch.current = now;
        setUiMode(backendDirective.ui_mode);
      }
    }
  }, [backendDirective, uiMode]);

  return { uiMode, directive: backendDirective };
}
