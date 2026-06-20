/**
 * Enterprise — Team Dashboard and Analytics (Feature 20).
 *
 * Displays team cognitive metrics, leaderboard, and organisational
 * analytics in a privacy-preserving manner.
 */

import { useState, useEffect } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function Enterprise() {
  const [teams, setTeams] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState("team-alpha");

  useEffect(() => {
    fetch("/api/enterprise/teams")
      .then((r) => r.json())
      .then((data) => setTeams(data.teams || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedTeam) return;
    Promise.all([
      fetch(`/api/enterprise/dashboard/${selectedTeam}`).then((r) => r.json()),
      fetch(`/api/enterprise/leaderboard/${selectedTeam}`).then((r) => r.json()),
    ])
      .then(([dash, lb]) => {
        setDashboard(dash);
        setLeaderboard(lb);
      })
      .catch(() => {});
  }, [selectedTeam]);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1.5rem", alignItems: "center" }}>
        <h1 style={{ fontSize: "1.5rem" }}>Enterprise Dashboard</h1>
        <select
          value={selectedTeam}
          onChange={(e) => setSelectedTeam(e.target.value)}
          style={{
            padding: "0.5rem 1rem",
            borderRadius: "4px",
            background: "#313244",
            color: "#cdd6f4",
            border: "1px solid #45475a",
          }}
        >
          {teams.map((t) => (
            <option key={t.team_id} value={t.team_id}>
              {t.name} ({t.member_count} members)
            </option>
          ))}
          {teams.length === 0 && <option value="team-alpha">Alpha Team</option>}
        </select>
      </div>

      {/* Team Metrics */}
      {dashboard && (
        <>
          <section style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
            gap: "1rem",
            marginBottom: "1.5rem",
          }}>
            <MetricCard label="Team Size" value={dashboard.total_members} color="#89b4fa" />
            <MetricCard label="Avg Focus" value={`${(dashboard.avg_focus_score * 100).toFixed(0)}%`} color="#a6e3a1" />
            <MetricCard label="Productivity" value={`${(dashboard.avg_productivity * 100).toFixed(0)}%`} color="#f9e2af" />
            <MetricCard label="Cognitive Diversity" value={`${(dashboard.cognitive_diversity * 100).toFixed(0)}%`} color="#cba6f7" />
          </section>

          {/* Detailed Metrics */}
          {dashboard.metrics && (
            <section style={sectionStyle}>
              <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Team Metrics</h2>
              <div style={{ display: "grid", gap: "0.5rem" }}>
                {Object.entries(dashboard.metrics).map(([key, val]) => (
                  <div key={key} style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <span style={{ width: "100px", fontSize: "0.75rem", textAlign: "right", color: "#a6adc8", textTransform: "capitalize" }}>
                      {key.replace(/_/g, " ")}
                    </span>
                    <div style={{ flex: 1, background: "#313244", borderRadius: "3px", height: "20px" }}>
                      <div style={{
                        width: `${val}%`,
                        height: "100%",
                        borderRadius: "3px",
                        background: `hsl(${val * 1.2}, 70%, 50%)`,
                        transition: "width 0.5s ease",
                      }} />
                    </div>
                    <span style={{ fontSize: "0.75rem", color: "#cdd6f4", width: "40px" }}>
                      {typeof val === "number" ? val.toFixed(1) : val}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Top Skills */}
          {dashboard.top_skills?.length > 0 && (
            <section style={sectionStyle}>
              <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Team Strengths</h2>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                {dashboard.top_skills.map((s, i) => (
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
            </section>
          )}
        </>
      )}

      {/* Leaderboard */}
      {leaderboard && (
        <section style={sectionStyle}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
            Skill Progression Leaderboard (Anonymous)
          </h2>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ fontSize: "0.75rem", color: "#a6adc8" }}>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Rank</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>ID</th>
                <th style={{ textAlign: "right", padding: "0.5rem" }}>Capability</th>
                <th style={{ textAlign: "right", padding: "0.5rem" }}>Growth</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Top Skill</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.entries?.map((e, i) => (
                <tr key={i} style={{ borderTop: "1px solid #313244" }}>
                  <td style={{ padding: "0.5rem", fontSize: "0.85rem" }}>#{i + 1}</td>
                  <td style={{ padding: "0.5rem", fontSize: "0.85rem", color: "#89b4fa" }}>{e.anonymous_id}</td>
                  <td style={{ padding: "0.5rem", textAlign: "right", fontSize: "0.85rem", color: "#f9e2af" }}>
                    {e.capability_index}
                  </td>
                  <td style={{ padding: "0.5rem", textAlign: "right", fontSize: "0.85rem", color: "#a6e3a1" }}>
                    +{e.growth}%
                  </td>
                  <td style={{ padding: "0.5rem", fontSize: "0.85rem", color: "#a6adc8" }}>
                    {e.top_dimension}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}

function MetricCard({ label, value, color }) {
  return (
    <div style={{
      background: "#313244",
      padding: "1rem",
      borderRadius: "6px",
      textAlign: "center",
    }}>
      <div style={{ fontSize: "1.5rem", fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>{label}</div>
    </div>
  );
}
