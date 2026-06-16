/**
 * AdaptiveLayout — the engine that automatically switches UI modes
 * based on the user's mental state and backend directives.
 *
 * Modes: visual | audio | haptic | mixed | zero
 */

import React, { useMemo } from "react";
import VisualInterface from "../components/VisualInterface.jsx";
import VoiceInterface from "../components/VoiceInterface.jsx";
import HapticInterface from "../components/HapticInterface.jsx";
import MixedInterface from "../components/MixedInterface.jsx";
import ZeroInterface from "../components/ZeroInterface.jsx";

const MODES = {
  visual: VisualInterface,
  audio: VoiceInterface,
  haptic: HapticInterface,
  mixed: MixedInterface,
  zero: ZeroInterface,
};

export default function AdaptiveLayout({
  uiMode,
  directive,
  mentalState,
  onBehavior,
}) {
  const ActiveComponent = useMemo(
    () => MODES[uiMode] || MODES.visual,
    [uiMode]
  );

  return (
    <div
      style={{
        transition: "opacity 0.4s ease, filter 0.4s ease",
        opacity: uiMode === "zero" ? 0.3 : 1,
      }}
    >
      <ActiveComponent
        mentalState={mentalState}
        directive={directive}
        onBehavior={onBehavior}
      />
    </div>
  );
}
