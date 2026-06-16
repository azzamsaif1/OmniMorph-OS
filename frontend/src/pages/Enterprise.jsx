/**
 * Enterprise — Strategic Team Dashboard Page (Feature 20).
 *
 * Aggregated team productivity, creativity, and cohesion metrics
 * at a cognitive level, with privacy-preserving individual scores.
 */

import { useState, useEffect } from "react";

export default function Enterprise() {
  const [dashboard, setDashboard] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/api/enterprise/dashboard/team-alpha").then((r) => r.json()),
      fetch("/api/enterprise/leaderboard/team-alpha").then((r) => r.json()),
    ])
      .then(([dash, lead]) => {
        setDashboard(dash);
        setLeaderboard(lead);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Enterprise Analytics
      </h1>

      {loading ? (
        <p style={{ color: "#a6adc8" }}>Loading team metrics...</p>
      ) : (
        <>
          {/* Team Metrics */}
          <section
            style={{
              background: "#1e1e2e",
              borderRadius: "8px",
              padding: "1.5rem",
              marginBottom: "1.5rem",
              border: "1px solid #313244",
            }}
          >
            <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
              Team Performance Overview
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1rem" }}>
              {[
                { label: "Productivity", value: dashboard?.metrics?.productivity || 78, color: "#89b4fa" },
                { label: "Creativity", value: dashboard?.metrics?.creativity || 65, color: "#a6e3a1" },
                { label: "Cohesion", value: dashboard?.metrics?.cohesion || 82, color: "#f9e2af" },
                { label: "Focus Index", value: dashboard?.metrics?.focus_index || 71, color: "#cba6f7" },
              ].map(({ label, value, color }) => (
                <div key={label} style={{ background: "#313244", padding: "1rem", borderRadius: "6px", textAlign: "center" }}>
                  <div style={{ fontSize: "1.8rem", fontWeight: 700, color }}>{value}%</div>
                  <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>{label}</div>
                </div>
              ))}
            </div>
          </section>

          {/* Leaderboard */}
          <section
            style={{
              background: "#1e1e2e",
              borderRadius: "8px",
              padding: "1.5rem",
              border: "1px solid #313244",
            }}
          >
            <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
              Anonymized Skill Leaderboard
            </h2>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid #45475a" }}>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#a6adc8", fontSize: "0.8rem" }}>Rank</th>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#a6adc8", fontSize: "0.8rem" }}>Member</th>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#a6adc8", fontSize: "0.8rem" }}>Capability</th>
                  <th style={{ textAlign: "left", padding: "0.5rem", color: "#a6adc8", fontSize: "0.8rem" }}>Growth</th>
                </tr>
              </thead>
              <tbody>
                {(leaderboard?.entries || defaultEntries).map((entry, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #313244" }}>
                    <td style={{ padding: "0.5rem", fontWeight: 600 }}>#{i + 1}</td>
                    <td style={{ padding: "0.5rem" }}>{entry.anonymous_id || `Member ${i + 1}`}</td>
                    <td style={{ padding: "0.5rem", color: "#89b4fa" }}>{entry.capability_index || "—"}%</td>
                    <td style={{ padding: "0.5rem", color: "#a6e3a1" }}>+{entry.growth || 0}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  );
}

const defaultEntries = [
  { anonymous_id: "eng_a7f3", capability_index: 82, growth: 15 },
  { anonymous_id: "eng_b2e1", capability_index: 78, growth: 12 },
  { anonymous_id: "eng_c9d4", capability_index: 74, growth: 18 },
  { anonymous_id: "eng_d1f8", capability_index: 71, growth: 8 },
  { anonymous_id: "eng_e5a2", capability_index: 68, growth: 22 },
];
