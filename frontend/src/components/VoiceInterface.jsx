/**
 * VoiceInterface — Web Speech API for voice-only interaction.
 *
 * Activated when the user is fatigued or frustrated; presents a calm,
 * minimal screen with voice input/output.
 */

import React, { useCallback, useEffect, useRef, useState } from "react";

const containerStyle = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "calc(100vh - 56px)",
  padding: 32,
  textAlign: "center",
};

const pulseKeyframes = `
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.15); opacity: 1; }
}
`;

export default function VoiceInterface({ mentalState }) {
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState(
    "I'm listening. Speak whenever you're ready."
  );
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const startListening = useCallback(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setResponse("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        interim += event.results[i][0].transcript;
      }
      setTranscript(interim);
    };

    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  }, []);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  useEffect(() => {
    return () => recognitionRef.current?.stop();
  }, []);

  const state = mentalState || {};

  return (
    <div style={containerStyle}>
      <style>{pulseKeyframes}</style>

      <div
        style={{
          width: 120,
          height: 120,
          borderRadius: "50%",
          background: isListening
            ? "radial-gradient(circle, #6366f1, #312e81)"
            : "radial-gradient(circle, #374151, #1f2937)",
          animation: isListening ? "pulse 2s ease-in-out infinite" : "none",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          marginBottom: 32,
        }}
        onClick={isListening ? stopListening : startListening}
        title={isListening ? "Stop listening" : "Start listening"}
      >
        <span style={{ fontSize: 36 }}>{isListening ? "🎙️" : "🔇"}</span>
      </div>

      <p style={{ fontSize: "1.1rem", opacity: 0.8, marginBottom: 16 }}>
        {response}
      </p>

      {transcript && (
        <p
          style={{
            fontSize: "0.9rem",
            opacity: 0.5,
            maxWidth: 500,
            lineHeight: 1.6,
          }}
        >
          <em>"{transcript}"</em>
        </p>
      )}

      <div
        style={{
          marginTop: 32,
          fontSize: "0.75rem",
          opacity: 0.3,
        }}
      >
        State: {state.state || "idle"} · Fatigue:{" "}
        {((state.fatigue || 0) * 100).toFixed(0)}%
      </div>
    </div>
  );
}
