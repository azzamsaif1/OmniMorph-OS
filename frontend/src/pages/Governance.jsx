/**
 * Governance — Ethical Constitution & Audit Trail (Feature 14).
 *
 * Shows constitutional rules, audit log, privacy budget status,
 * and governance controls.
 */

import { useState, useEffect } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function Governance() {
  const [rules, setRules] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [privacyBudget, setPrivacyBudget] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/governance/constitution").then((r) => r.json()),
      fetch("/api/governance/audit?limit=20").then((r) => r.json()),
      fetch("/api/governance/privacy/budget/default").then((r) => r.json()),
    ])
      .then(([c, a, p]) => {
        setRules(c.rules || []);
        setAuditLog(a.entries || []);
        setPrivacyBudget(p);
      })
      .catch(() => {});
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Governance & Ethics
      </h1>

      {/* Privacy Budget */}
      {privacyBudget && (
        <section style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}>
          <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px", textAlign: "center" }}>
            <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#a6e3a1" }}>
              {privacyBudget.epsilon_remaining?.toFixed(2)}
            </div>
            <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Privacy Budget Left</div>
          </div>
          <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px", textAlign: "center" }}>
            <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#f9e2af" }}>
              {privacyBudget.epsilon_spent?.toFixed(4)}
            </div>
            <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Epsilon Spent</div>
          </div>
          <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px", textAlign: "center" }}>
            <div style={{ fontSize: "1.5rem", fontWeight: 700, color: privacyBudget.exhausted ? "#f38ba8" : "#89b4fa" }}>
              {privacyBudget.exhausted ? "Exhausted" : "Active"}
            </div>
            <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Status</div>
          </div>
        </section>
      )}

      {/* Constitutional Rules */}
      <section style={sectionStyle}>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          Ethical Constitution ({rules.length} rules)
        </h2>
        <div style={{ display: "grid", gap: "0.5rem" }}>
          {rules.map((r, i) => (
            <div key={i} style={{
              background: "#313244",
              padding: "0.75rem",
              borderRadius: "6px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>{r.name}</div>
                <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>{r.description}</div>
              </div>
              <span style={{
                padding: "0.15rem 0.5rem",
                borderRadius: "10px",
                fontSize: "0.7rem",
                background: r.severity === "critical" ? "#4a2d2d" : "#2d3a4a",
                color: r.severity === "critical" ? "#f38ba8" : "#89b4fa",
              }}>
                {r.severity}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Audit Log */}
      <section style={sectionStyle}>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          Audit Trail
        </h2>
        {auditLog.length > 0 ? (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
            <thead>
              <tr style={{ color: "#a6adc8" }}>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Time</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Category</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Actor</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Action</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Outcome</th>
              </tr>
            </thead>
            <tbody>
              {auditLog.map((entry, i) => (
                <tr key={i} style={{ borderTop: "1px solid #313244" }}>
                  <td style={{ padding: "0.5rem", color: "#585b70" }}>
                    {entry.timestamp?.slice(11, 19) || "—"}
                  </td>
                  <td style={{ padding: "0.5rem", color: "#89b4fa" }}>
                    {entry.category}
                  </td>
                  <td style={{ padding: "0.5rem", color: "#cba6f7" }}>
                    {entry.actor}
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    {entry.action}
                  </td>
                  <td style={{ padding: "0.5rem", color: entry.outcome === "success" ? "#a6e3a1" : "#f38ba8" }}>
                    {entry.outcome}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "#a6adc8" }}>No audit entries yet</p>
        )}
      </section>
    </div>
  );
}
