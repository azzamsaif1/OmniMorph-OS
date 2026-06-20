/**
 * Dashboard — Cognitive metrics overview.
 *
 * Shows mental state history, agent activity, capability index, and
 * session analytics.
 */

import { useState, useEffect, useRef } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

const MetricCard = ({ label, value, color }) => (
  <div style={{
    background: "#313244",
    padding: "1rem",
    borderRadius: "6px",
    textAlign: "center",
  }}>
    <div style={{ fontSize: "1.8rem", fontWeight: 700, color }}>{value}</div>
    <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>{label}</div>
  </div>
);

function BarChart({ data, maxVal }) {
  const max = maxVal || Math.max(...Object.values(data), 1);
  return (
    <div style={{ display: "grid", gap: "0.5rem" }}>
      {Object.entries(data).map(([label, val]) => (
        <div key={label} style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <span style={{ width: "100px", fontSize: "0.75rem", textAlign: "right", color: "#a6adc8" }}>
            {label}
          </span>
          <div style={{ flex: 1, background: "#313244", borderRadius: "3px", height: "20px" }}>
            <div
              style={{
                width: `${(val / max) * 100}%`,
                height: "100%",
                borderRadius: "3px",
                background: `hsl(${(val / max) * 120}, 70%, 50%)`,
                transition: "width 0.5s ease",
              }}
            />
          </div>
          <span style={{ fontSize: "0.75rem", color: "#cdd6f4", width: "40px" }}>
            {typeof val === "number" ? val.toFixed(1) : val}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [systemInfo, setSystemInfo] = useState(null);
  const [evaluation, setEvaluation] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/system/info").then((r) => r.json()),
      fetch("/api/evaluation/profile/default").then((r) => r.json()),
    ])
      .then(([info, cap]) => {
        setSystemInfo(info);
        setEvaluation(cap);
      })
      .catch(() => {});
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Cognitive Dashboard
      </h1>

      {/* Top Metrics */}
      <section style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
        gap: "1rem",
        marginBottom: "1.5rem",
      }}>
        <MetricCard label="Mental State" value="Focused" color="#a6e3a1" />
        <MetricCard label="Confidence" value="85%" color="#89b4fa" />
        <MetricCard label="UI Mode" value="Visual" color="#cba6f7" />
        <MetricCard
          label="Capability Index"
          value={evaluation ? `${(evaluation.composite_index * 100).toFixed(0)}` : "—"}
          color="#f9e2af"
        />
      </section>

      {/* Capability Profile */}
      {evaluation && (
        <section style={sectionStyle}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
            Capability Profile
          </h2>
          <BarChart
            data={
              evaluation.dimensions
                ? Object.fromEntries(
                    Object.entries(evaluation.dimensions).map(([name, d]) => [
                      name.replace(/_/g, " "),
                      (d.value || 0) * 100,
                    ])
                  )
                : {}
            }
            maxVal={100}
          />
        </section>
      )}

      {/* Architecture */}
      {systemInfo && (
        <section style={sectionStyle}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
            System Architecture
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div>
              <h3 style={{ fontSize: "0.9rem", color: "#89b4fa", marginBottom: "0.5rem" }}>Layers</h3>
              <ul style={{ paddingLeft: "1rem", fontSize: "0.8rem", listStyle: "none" }}>
                {systemInfo.architecture.layers.map((l, i) => (
                  <li key={i} style={{ padding: "0.15rem 0", color: "#a6adc8" }}>{l}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 style={{ fontSize: "0.9rem", color: "#a6e3a1", marginBottom: "0.5rem" }}>Features</h3>
              <ul style={{ paddingLeft: "1rem", fontSize: "0.8rem", listStyle: "none" }}>
                {systemInfo.features.map((f, i) => (
                  <li key={i} style={{ padding: "0.15rem 0", color: "#a6adc8" }}>{f}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
