/**
 * Career — Professional Evolution Simulator (Feature 19).
 *
 * Simulates potential career paths based on capability profile,
 * provides AI-powered career guidance via Gemini.
 */

import { useState, useEffect } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function Career() {
  const [career, setCareer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/enterprise/career/default")
      .then((r) => r.json())
      .then(setCareer)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Career Simulator
      </h1>

      {loading ? (
        <p style={{ color: "#a6adc8" }}>Analyzing your career trajectory...</p>
      ) : career ? (
        <>
          <section style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "1rem",
            marginBottom: "1.5rem",
          }}>
            <div style={{
              background: "#313244",
              padding: "1rem",
              borderRadius: "6px",
              textAlign: "center",
            }}>
              <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Current Level</div>
              <div style={{ fontSize: "1.3rem", fontWeight: 700, color: "#89b4fa" }}>
                {career.current_level}
              </div>
            </div>
            <div style={{
              background: "#313244",
              padding: "1rem",
              borderRadius: "6px",
              textAlign: "center",
            }}>
              <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Strongest Domain</div>
              <div style={{ fontSize: "1.3rem", fontWeight: 700, color: "#a6e3a1" }}>
                {career.strongest_domain}
              </div>
            </div>
            <div style={{
              background: "#313244",
              padding: "1rem",
              borderRadius: "6px",
              textAlign: "center",
            }}>
              <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Growth Velocity</div>
              <div style={{ fontSize: "1.3rem", fontWeight: 700, color: "#f9e2af" }}>
                {career.growth_velocity}
              </div>
            </div>
          </section>

          {/* Career Paths */}
          {career.paths?.length > 0 && (
            <section style={sectionStyle}>
              <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
                Predicted Career Paths
              </h2>
              <div style={{ display: "grid", gap: "0.75rem" }}>
                {career.paths.map((path, i) => (
                  <div key={i} style={{
                    background: "#313244",
                    padding: "1rem",
                    borderRadius: "6px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}>
                    <div>
                      <div style={{ fontWeight: 600, color: "#cba6f7" }}>
                        {typeof path === "string" ? path : path.title || JSON.stringify(path)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Recommendations */}
          {career.recommendations?.length > 0 && (
            <section style={sectionStyle}>
              <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
                Recommendations
              </h2>
              <ul style={{ paddingLeft: "1.5rem" }}>
                {career.recommendations.map((rec, i) => (
                  <li key={i} style={{
                    fontSize: "0.85rem",
                    color: "#a6adc8",
                    padding: "0.25rem 0",
                  }}>
                    {typeof rec === "string" ? rec : JSON.stringify(rec)}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      ) : (
        <p style={{ color: "#f38ba8" }}>Failed to load career data</p>
      )}
    </div>
  );
}
