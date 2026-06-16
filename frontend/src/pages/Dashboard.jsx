/**
 * Dashboard — Main Workspace Page.
 *
 * Central hub showing mental state overview, capability index,
 * recent agent activity, and quick-access navigation to all UCSK features.
 */

import { useState, useEffect } from "react";

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [agentStatus, setAgentStatus] = useState(null);

  useEffect(() => {
    fetch("/api/evaluation/profile/default")
      .then((r) => r.json())
      .then(setProfile)
      .catch(() => {});

    fetch("/api/agents/status")
      .then((r) => r.json())
      .then(setAgentStatus)
      .catch(() => {});
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        UCSK Dashboard
      </h1>

      {/* Capability Index */}
      <section
        style={{
          background: "#1e1e2e",
          borderRadius: "8px",
          padding: "1.5rem",
          marginBottom: "1.5rem",
          color: "#cdd6f4",
        }}
      >
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          Capability Index
        </h2>
        {profile ? (
          <div>
            <div style={{ fontSize: "2rem", fontWeight: 700, color: "#89b4fa" }}>
              {(profile.composite_index * 100).toFixed(1)}%
            </div>
            <div style={{ color: "#a6adc8", marginBottom: "1rem" }}>
              Maturity: {profile.maturity_level}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.5rem" }}>
              {Object.entries(profile.dimensions || {}).map(([name, data]) => (
                <div key={name} style={{ background: "#313244", padding: "0.5rem", borderRadius: "4px" }}>
                  <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>
                    {name.replace(/_/g, " ")}
                  </div>
                  <div style={{ fontWeight: 600 }}>
                    {(data.value * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p style={{ color: "#a6adc8" }}>Loading capability profile...</p>
        )}
      </section>

      {/* Agent Status */}
      <section
        style={{
          background: "#1e1e2e",
          borderRadius: "8px",
          padding: "1.5rem",
          marginBottom: "1.5rem",
          color: "#cdd6f4",
        }}
      >
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          Agent Mesh Status
        </h2>
        {agentStatus ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "0.5rem" }}>
            {(agentStatus.agents || []).map((agent) => (
              <div
                key={agent.name}
                style={{
                  background: "#313244",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  borderLeft: `3px solid ${agent.status === "active" ? "#a6e3a1" : "#f38ba8"}`,
                }}
              >
                <div style={{ fontSize: "0.8rem", fontWeight: 600 }}>
                  {agent.name}
                </div>
                <div style={{ fontSize: "0.7rem", color: "#a6adc8" }}>
                  {agent.role}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: "#a6adc8" }}>Loading agent status...</p>
        )}
      </section>

      {/* Quick Links */}
      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1rem",
        }}
      >
        {[
          { label: "Training Scenarios", href: "#/training", icon: "🎯" },
          { label: "Career Simulation", href: "#/career", icon: "📈" },
          { label: "Enterprise Analytics", href: "#/enterprise", icon: "🏢" },
          { label: "Research Feed", href: "#/research", icon: "🔬" },
        ].map(({ label, href, icon }) => (
          <a
            key={label}
            href={href}
            style={{
              display: "block",
              background: "#1e1e2e",
              borderRadius: "8px",
              padding: "1rem",
              color: "#cdd6f4",
              textDecoration: "none",
              border: "1px solid #313244",
            }}
          >
            <div style={{ fontSize: "1.5rem" }}>{icon}</div>
            <div style={{ marginTop: "0.5rem", fontWeight: 500 }}>{label}</div>
          </a>
        ))}
      </section>
    </div>
  );
}
