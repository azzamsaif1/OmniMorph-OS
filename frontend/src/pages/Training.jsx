/**
 * Training — Real-World Scenario Generator (Feature 18).
 *
 * Generates personalized coding challenges and training scenarios
 * using Gemini, adapting difficulty to the user's skill level.
 */

import { useState } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function Training() {
  const [scenario, setScenario] = useState(null);
  const [domain, setDomain] = useState("backend");
  const [level, setLevel] = useState("intermediate");
  const [loading, setLoading] = useState(false);

  const generateScenario = async () => {
    setLoading(true);
    try {
      const resp = await fetch(
        `/api/enterprise/scenario/generate?skill_level=${level}&domain=${domain}`,
        { method: "POST" }
      );
      const data = await resp.json();
      setScenario(data);
    } catch (err) {
      console.error("Scenario generation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Training Scenarios
      </h1>

      {/* Controls */}
      <section style={{ display: "flex", gap: "1rem", marginBottom: "2rem", flexWrap: "wrap" }}>
        <select
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          style={{
            padding: "0.5rem 1rem",
            borderRadius: "4px",
            background: "#313244",
            color: "#cdd6f4",
            border: "1px solid #45475a",
          }}
        >
          <option value="backend">Backend</option>
          <option value="frontend">Frontend</option>
          <option value="fullstack">Full Stack</option>
          <option value="devops">DevOps</option>
          <option value="security">Security</option>
          <option value="architecture">Architecture</option>
        </select>

        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          style={{
            padding: "0.5rem 1rem",
            borderRadius: "4px",
            background: "#313244",
            color: "#cdd6f4",
            border: "1px solid #45475a",
          }}
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
          <option value="expert">Expert</option>
        </select>

        <button
          onClick={generateScenario}
          disabled={loading}
          style={{
            padding: "0.5rem 1.5rem",
            borderRadius: "4px",
            background: "#89b4fa",
            color: "#1e1e2e",
            border: "none",
            fontWeight: 600,
            cursor: loading ? "wait" : "pointer",
          }}
        >
          {loading ? "Generating..." : "Generate Scenario"}
        </button>
      </section>

      {/* Scenario Display */}
      {scenario && (
        <section style={sectionStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1rem" }}>
            <h2 style={{ fontSize: "1.1rem", color: "#89b4fa" }}>
              {scenario.scenario}
            </h2>
            <span style={{
              padding: "0.25rem 0.75rem",
              borderRadius: "12px",
              background: "#45475a",
              fontSize: "0.75rem",
              color: "#f9e2af",
            }}>
              {scenario.domain} | {scenario.skill_level}
            </span>
          </div>

          <p style={{ fontSize: "0.9rem", color: "#a6adc8", marginBottom: "1rem" }}>
            {scenario.description}
          </p>

          {scenario.objectives?.length > 0 && (
            <div>
              <h3 style={{ fontSize: "0.9rem", marginBottom: "0.5rem" }}>Objectives</h3>
              <ul style={{ paddingLeft: "1.5rem" }}>
                {scenario.objectives.map((obj, i) => (
                  <li key={i} style={{ fontSize: "0.85rem", color: "#a6adc8", padding: "0.15rem 0" }}>
                    {typeof obj === "string" ? obj : obj.title || JSON.stringify(obj)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
