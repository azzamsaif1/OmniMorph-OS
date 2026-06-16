/**
 * Training — Real-World Scenario Generator Page.
 *
 * Allows users to generate engineering training projects
 * with dynamic difficulty based on their capability profile.
 */

import { useState } from "react";

const DOMAINS = ["backend", "frontend", "devops", "security", "distributed", "ml"];
const DIFFICULTIES = ["auto", "easy", "medium", "hard", "expert"];

export default function Training() {
  const [domain, setDomain] = useState("backend");
  const [difficulty, setDifficulty] = useState("auto");
  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    setLoading(true);
    try {
      const resp = await fetch("/api/training/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain, difficulty, user_id: "default" }),
      });
      const data = await resp.json();
      setScenario(data);
    } catch (err) {
      console.error("Failed to generate scenario:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Training Scenario Generator
      </h1>

      {/* Controls */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", flexWrap: "wrap" }}>
        <select
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          style={{ padding: "0.5rem", borderRadius: "4px", background: "#313244", color: "#cdd6f4", border: "1px solid #45475a" }}
        >
          {DOMAINS.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>

        <select
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          style={{ padding: "0.5rem", borderRadius: "4px", background: "#313244", color: "#cdd6f4", border: "1px solid #45475a" }}
        >
          {DIFFICULTIES.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>

        <button
          onClick={generate}
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
      </div>

      {/* Generated Scenario */}
      {scenario && (
        <div
          style={{
            background: "#1e1e2e",
            borderRadius: "8px",
            padding: "1.5rem",
            border: "1px solid #313244",
          }}
        >
          <h2 style={{ fontSize: "1.2rem", marginBottom: "0.5rem", color: "#89b4fa" }}>
            {scenario.title}
          </h2>
          <p style={{ color: "#a6adc8", marginBottom: "1rem" }}>
            {scenario.description}
          </p>

          <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", flexWrap: "wrap" }}>
            <span style={{ background: "#313244", padding: "0.25rem 0.75rem", borderRadius: "12px", fontSize: "0.8rem" }}>
              {scenario.difficulty}
            </span>
            <span style={{ background: "#313244", padding: "0.25rem 0.75rem", borderRadius: "12px", fontSize: "0.8rem" }}>
              ~{scenario.estimated_hours}h
            </span>
            {(scenario.skills_targeted || []).map((s) => (
              <span
                key={s}
                style={{ background: "#45475a", padding: "0.25rem 0.75rem", borderRadius: "12px", fontSize: "0.75rem" }}
              >
                {s}
              </span>
            ))}
          </div>

          <h3 style={{ fontSize: "0.9rem", marginBottom: "0.5rem" }}>Milestones</h3>
          <ol style={{ paddingLeft: "1.5rem", color: "#a6adc8" }}>
            {(scenario.milestones || []).map((m, i) => (
              <li key={i} style={{ marginBottom: "0.25rem" }}>{m}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
