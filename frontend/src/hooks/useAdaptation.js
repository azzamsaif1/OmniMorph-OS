/**
 * useAdaptation — consumes the mental-state stream and returns
 * the current UI mode + adaptation directive with hysteresis.
 */

import { useEffect, useRef, useState } from "react";

const MODE_COOLDOWN_MS = 2000; // Minimum time between mode switches

export function useAdaptation(mentalState) {
  const [uiMode, setUiMode] = useState("visual");
  const [directive, setDirective] = useState(null);
  const lastSwitch = useRef(0);

  useEffect(() => {
    if (!mentalState) return;

    // Derive mode from state if no directive has arrived yet
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

  // Also accept explicit directives from the WebSocket
  useEffect(() => {
    if (!directive) return;
    if (directive.ui_mode && directive.ui_mode !== uiMode) {
      const now = Date.now();
      if (now - lastSwitch.current > MODE_COOLDOWN_MS) {
        lastSwitch.current = now;
        setUiMode(directive.ui_mode);
      }
    }
  }, [directive, uiMode]);

  return { uiMode, directive, setDirective };
}
