/**
 * Settings — User preferences, consent management, and system config.
 */

import { useState, useEffect } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function Settings() {
  const [consent, setConsent] = useState({
    camera: false,
    mic: false,
    keyboard: false,
    sharing: false,
  });
  const [prefConfig, setPrefConfig] = useState(null);

  useEffect(() => {
    fetch("/api/preferences/config/default")
      .then((r) => r.json())
      .then(setPrefConfig)
      .catch(() => {});
  }, []);

  const updateConsent = async (key) => {
    const updated = { ...consent, [key]: !consent[key] };
    setConsent(updated);
    try {
      await fetch("/api/auth/consent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "default",
          consent_camera: updated.camera,
          consent_mic: updated.mic,
          consent_keyboard: updated.keyboard,
          consent_sharing: updated.sharing,
        }),
      });
    } catch (err) {
      console.error("Consent update failed:", err);
    }
  };

  const Toggle = ({ label, checked, onChange }) => (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "0.75rem",
        background: "#313244",
        borderRadius: "6px",
        marginBottom: "0.5rem",
      }}
    >
      <span style={{ fontSize: "0.9rem" }}>{label}</span>
      <button
        onClick={onChange}
        style={{
          width: "48px",
          height: "24px",
          borderRadius: "12px",
          background: checked ? "#89b4fa" : "#45475a",
          border: "none",
          cursor: "pointer",
          position: "relative",
        }}
      >
        <div
          style={{
            width: "20px",
            height: "20px",
            borderRadius: "50%",
            background: "#fff",
            position: "absolute",
            top: "2px",
            left: checked ? "26px" : "2px",
            transition: "left 0.2s",
          }}
        />
      </button>
    </div>
  );

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>Settings</h1>

      {/* Consent */}
      <section style={sectionStyle}>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          Data Collection Consent
        </h2>
        <p style={{ fontSize: "0.8rem", color: "#a6adc8", marginBottom: "1rem" }}>
          UCSK uses multimodal sensing to understand your cognitive state. All data
          is processed locally first and shared only with your explicit consent.
        </p>
        <Toggle label="Camera (Face Mesh Analysis)" checked={consent.camera} onChange={() => updateConsent("camera")} />
        <Toggle label="Microphone (Voice Tone Analysis)" checked={consent.mic} onChange={() => updateConsent("mic")} />
        <Toggle label="Keyboard/Mouse (Behavior Tracking)" checked={consent.keyboard} onChange={() => updateConsent("keyboard")} />
        <Toggle label="Skill Sharing (Federated Learning)" checked={consent.sharing} onChange={() => updateConsent("sharing")} />
      </section>

      {/* Learned Preferences */}
      {prefConfig && (
        <section style={sectionStyle}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
            Learned Preferences
          </h2>
          <p style={{ fontSize: "0.8rem", color: "#a6adc8", marginBottom: "1rem" }}>
            These preferences are automatically learned from your interactions.
          </p>
          <div style={{ display: "grid", gap: "0.5rem" }}>
            {Object.entries(prefConfig).map(([key, val]) => (
              <div key={key} style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "0.5rem 0.75rem",
                background: "#313244",
                borderRadius: "4px",
                fontSize: "0.85rem",
              }}>
                <span style={{ color: "#a6adc8" }}>{key.replace(/_/g, " ")}</span>
                <span style={{ color: "#89b4fa" }}>
                  {typeof val === "number" ? val.toFixed(2) : String(val)}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
