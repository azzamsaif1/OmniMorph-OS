/**
 * DigitalTwin — Portable Engineering Mind Clone (Feature 11).
 *
 * Visualizes the user's skill fingerprint, allows export/import
 * of the digital soul, and shows predicted behaviors.
 */

import { useState, useEffect } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function DigitalTwin() {
  const [fingerprint, setFingerprint] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [exportedSoul, setExportedSoul] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/api/twin/fingerprint/default").then((r) => r.json()),
      fetch("/api/twin/predict/default").then((r) => r.json()),
    ])
      .then(([fp, pred]) => {
        setFingerprint(fp);
        setPrediction(pred);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const exportSoul = async () => {
    try {
      const resp = await fetch("/api/twin/export/default", { method: "POST" });
      const data = await resp.json();
      setExportedSoul(data);
    } catch (err) {
      console.error("Export failed:", err);
    }
  };

  const captureActivity = async () => {
    try {
      await fetch("/api/twin/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "default",
          language: "python",
          framework: "fastapi",
          pattern_type: "design_choice",
          pattern_desc: "Using async/await for I/O-bound operations",
          context: "backend development",
        }),
      });
      const resp = await fetch("/api/twin/fingerprint/default");
      const fp = await resp.json();
      setFingerprint(fp);
    } catch (err) {
      console.error("Capture failed:", err);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Digital Twin
      </h1>

      {loading ? (
        <p style={{ color: "#a6adc8" }}>Loading twin data...</p>
      ) : (
        <>
          {/* Fingerprint */}
          <section style={sectionStyle}>
            <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
              Skill Fingerprint
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem" }}>
              <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Sessions</div>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#89b4fa" }}>
                  {fingerprint?.total_sessions || 0}
                </div>
              </div>
              <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Patterns</div>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#a6e3a1" }}>
                  {fingerprint?.pattern_count || 0}
                </div>
              </div>
              <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Learning Velocity</div>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#f9e2af" }}>
                  {((fingerprint?.learning_velocity || 0.5) * 100).toFixed(0)}%
                </div>
              </div>
              <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Decision Style</div>
                <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "#cba6f7" }}>
                  {fingerprint?.decision_style || "balanced"}
                </div>
              </div>
            </div>

            {/* Languages */}
            {fingerprint?.languages && Object.keys(fingerprint.languages).length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <div style={{ fontSize: "0.85rem", marginBottom: "0.5rem", color: "#a6adc8" }}>
                  Languages
                </div>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  {Object.entries(fingerprint.languages).map(([lang, val]) => (
                    <span key={lang} style={{
                      padding: "0.25rem 0.75rem",
                      borderRadius: "12px",
                      background: "#45475a",
                      fontSize: "0.8rem",
                    }}>
                      {lang}: {typeof val === 'number' ? val.toFixed(1) : val}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Strengths */}
            {fingerprint?.strengths?.length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <div style={{ fontSize: "0.85rem", marginBottom: "0.5rem", color: "#a6adc8" }}>
                  Strengths
                </div>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                  {fingerprint.strengths.map((s, i) => (
                    <span key={i} style={{
                      padding: "0.25rem 0.75rem",
                      borderRadius: "12px",
                      background: "#2d4a2d",
                      fontSize: "0.8rem",
                      color: "#a6e3a1",
                    }}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* Prediction */}
          {prediction && (
            <section style={sectionStyle}>
              <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
                Behavioral Prediction
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div>
                  <div style={{ fontSize: "0.8rem", color: "#a6adc8" }}>Predicted Language</div>
                  <div style={{ fontWeight: 600, color: "#89b4fa" }}>
                    {prediction.predicted_language}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: "0.8rem", color: "#a6adc8" }}>Predicted Framework</div>
                  <div style={{ fontWeight: 600, color: "#a6e3a1" }}>
                    {prediction.predicted_framework}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: "0.8rem", color: "#a6adc8" }}>Confidence</div>
                  <div style={{ fontWeight: 600, color: "#f9e2af" }}>
                    {(prediction.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Actions */}
          <section style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            <button
              onClick={captureActivity}
              style={{
                padding: "0.75rem 1.5rem",
                borderRadius: "6px",
                background: "#89b4fa",
                color: "#1e1e2e",
                border: "none",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Capture Activity
            </button>
            <button
              onClick={exportSoul}
              style={{
                padding: "0.75rem 1.5rem",
                borderRadius: "6px",
                background: "#a6e3a1",
                color: "#1e1e2e",
                border: "none",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Export Digital Soul
            </button>
          </section>

          {/* Exported Soul */}
          {exportedSoul && (
            <section style={{ ...sectionStyle, marginTop: "1.5rem" }}>
              <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
                Exported Soul
              </h2>
              <pre style={{
                background: "#313244",
                padding: "1rem",
                borderRadius: "6px",
                fontSize: "0.75rem",
                overflow: "auto",
                maxHeight: "300px",
              }}>
                {JSON.stringify(exportedSoul, null, 2)}
              </pre>
            </section>
          )}
        </>
      )}
    </div>
  );
}
