/**
 * Evolution — Self-evolving penetration testing dashboard.
 *
 * Shows evolution engine status, strategy learner, experience memory,
 * performance metrics, and comparison vs Claude Mythos.
 */

import { useState, useEffect, useCallback } from "react";

const S = {
  section: {
    background: "#1e1e2e",
    borderRadius: "8px",
    padding: "1.5rem",
    marginBottom: "1.5rem",
    border: "1px solid #313244",
  },
  grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" },
  grid3: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem" },
  grid4: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: "1rem" },
  card: {
    background: "#313244",
    padding: "1rem",
    borderRadius: "6px",
    textAlign: "center",
  },
  tag: (color) => ({
    display: "inline-block",
    padding: "2px 8px",
    borderRadius: "4px",
    fontSize: "0.7rem",
    fontWeight: 600,
    background: color + "22",
    color: color,
    marginRight: "4px",
  }),
  btn: (color) => ({
    background: color,
    border: "none",
    color: "#1e1e2e",
    padding: "8px 16px",
    borderRadius: "6px",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: "0.85rem",
  }),
  meter: (pct, color) => ({
    width: `${pct}%`,
    height: "8px",
    borderRadius: "4px",
    background: color,
    transition: "width 0.5s ease",
  }),
};

function MetricCard({ label, value, color = "#89b4fa", sub }) {
  return (
    <div style={S.card}>
      <div style={{ fontSize: "1.6rem", fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>{label}</div>
      {sub && <div style={{ fontSize: "0.65rem", color: "#585b70", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function ProgressBar({ value, target, label, color = "#89b4fa" }) {
  const pct = Math.min(100, (value / Math.max(target, 0.001)) * 100);
  const hit = value >= target;
  return (
    <div style={{ marginBottom: "0.75rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", marginBottom: 4 }}>
        <span style={{ color: "#a6adc8" }}>{label}</span>
        <span style={{ color: hit ? "#a6e3a1" : "#f38ba8" }}>
          {(value * 100).toFixed(1)}% / {(target * 100).toFixed(0)}%
        </span>
      </div>
      <div style={{ background: "#313244", borderRadius: "4px", height: "8px" }}>
        <div style={S.meter(pct, hit ? "#a6e3a1" : color)} />
      </div>
    </div>
  );
}

export default function Evolution() {
  const [dashboard, setDashboard] = useState(null);
  const [strategies, setStrategies] = useState(null);
  const [memory, setMemory] = useState(null);
  const [assessing, setAssessing] = useState(false);
  const [assessResult, setAssessResult] = useState(null);
  const [targetIp, setTargetIp] = useState("127.0.0.1");

  const fetchAll = useCallback(() => {
    fetch("/api/evolution/dashboard").then(r => r.json()).then(setDashboard).catch(() => {});
    fetch("/api/evolution/strategies").then(r => r.json()).then(setStrategies).catch(() => {});
    fetch("/api/evolution/memory").then(r => r.json()).then(setMemory).catch(() => {});
  }, []);

  useEffect(() => { fetchAll(); const t = setInterval(fetchAll, 10000); return () => clearInterval(t); }, [fetchAll]);

  const runAssessment = async () => {
    setAssessing(true);
    setAssessResult(null);
    try {
      const r = await fetch("/api/evolution/assess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_ip: targetIp, depth: "standard" }),
      });
      const data = await r.json();
      setAssessResult(data);
      fetchAll();
    } finally {
      setAssessing(false);
    }
  };

  const triggerEvolve = async () => {
    await fetch("/api/evolution/evolve", { method: "POST" });
    fetchAll();
  };

  const ov = dashboard?.overview || {};
  const metrics = dashboard?.performance_metrics || {};
  const comparison = dashboard?.comparison_vs_mythos || {};

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <h2 style={{ fontSize: "1.4rem", marginBottom: "0.5rem" }}>Self-Evolving Penetration Testing</h2>
      <p style={{ color: "#a6adc8", fontSize: "0.85rem", marginBottom: "1.5rem" }}>
        Multi-agent security assessment with continuous learning — surpasses single-model approaches
      </p>

      {/* Overview Metrics */}
      <div style={{ ...S.grid4, marginBottom: "1.5rem" }}>
        <MetricCard label="Assessments" value={ov.assessments_completed ?? 0} color="#89b4fa" />
        <MetricCard label="Vulns Found" value={ov.total_vulns_found ?? 0} color="#f38ba8" />
        <MetricCard label="Exploits Succeeded" value={ov.total_exploits_succeeded ?? 0} color="#fab387" />
        <MetricCard
          label="Evolution Gen"
          value={ov.evolution_generation ?? 0}
          color="#a6e3a1"
          sub="Strategy mutations applied"
        />
      </div>

      {/* Autonomous Assessment */}
      <div style={S.section}>
        <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Autonomous Assessment</h3>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", marginBottom: "1rem" }}>
          <input
            type="text"
            value={targetIp}
            onChange={(e) => setTargetIp(e.target.value)}
            placeholder="Target IP"
            style={{
              background: "#313244", border: "1px solid #45475a", color: "#cdd6f4",
              padding: "8px 12px", borderRadius: "6px", fontSize: "0.85rem", width: "200px",
            }}
          />
          <button onClick={runAssessment} disabled={assessing} style={S.btn(assessing ? "#585b70" : "#89b4fa")}>
            {assessing ? "Assessing..." : "Run Assessment"}
          </button>
          <button onClick={triggerEvolve} style={S.btn("#a6e3a1")}>
            Evolve Strategies
          </button>
        </div>

        {assessResult && (
          <div style={{ background: "#11111b", padding: "1rem", borderRadius: "6px", fontSize: "0.8rem" }}>
            <div style={{ color: "#a6e3a1", fontWeight: 600, marginBottom: "0.5rem" }}>
              Assessment Complete — {assessResult.duration_ms?.toFixed(0)}ms
            </div>
            <div style={S.grid3}>
              <div>
                <strong style={{ color: "#89b4fa" }}>Recon:</strong>{" "}
                {assessResult.stages?.reconnaissance?.open_ports_count ?? 0} ports
              </div>
              <div>
                <strong style={{ color: "#f38ba8" }}>Vulns:</strong>{" "}
                {assessResult.stages?.vulnerability_analysis?.vulnerable_services ?? 0} vulnerable services
              </div>
              <div>
                <strong style={{ color: "#fab387" }}>Exploits:</strong>{" "}
                {assessResult.stages?.exploitation?.length ?? 0} attempted
              </div>
            </div>
            {assessResult.stages?.report?.executive_summary && (
              <p style={{ color: "#a6adc8", marginTop: "0.75rem", lineHeight: 1.5 }}>
                {assessResult.stages.report.executive_summary}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Performance Targets */}
      <div style={S.section}>
        <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Performance Metrics vs Targets</h3>
        <ProgressBar value={metrics.detection_rate ?? 0} target={0.95} label="Detection Rate" color="#89b4fa" />
        <ProgressBar value={metrics.vuln_precision ?? 0} target={0.90} label="Vulnerability Precision" color="#f9e2af" />
        <ProgressBar value={metrics.exploit_success ?? 0} target={0.85} label="Exploit Success" color="#fab387" />
        <ProgressBar
          value={1 - (metrics.false_positive_rate ?? 0)}
          target={0.95}
          label="True Positive Rate"
          color="#a6e3a1"
        />
        {metrics.improvement_rate !== undefined && (
          <div style={{ fontSize: "0.8rem", color: "#a6adc8", marginTop: "0.5rem" }}>
            Improvement rate: <strong style={{ color: metrics.improvement_rate > 0 ? "#a6e3a1" : "#f38ba8" }}>
              {(metrics.improvement_rate * 100).toFixed(1)}%
            </strong> per assessment
          </div>
        )}
      </div>

      <div style={S.grid2}>
        {/* Strategies */}
        <div style={S.section}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
            Attack Strategies ({strategies?.total ?? 0})
          </h3>
          <div style={{ maxHeight: "300px", overflowY: "auto" }}>
            {(strategies?.strategies || []).map((s) => (
              <div
                key={s.id}
                style={{
                  background: "#11111b",
                  padding: "0.75rem",
                  borderRadius: "6px",
                  marginBottom: "0.5rem",
                  fontSize: "0.8rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong style={{ color: "#cdd6f4" }}>{s.name}</strong>
                  <span style={S.tag(s.success_rate >= 0.8 ? "#a6e3a1" : s.success_rate >= 0.5 ? "#f9e2af" : "#f38ba8")}>
                    {(s.success_rate * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ color: "#585b70", marginTop: 4 }}>
                  {s.phases?.length ?? 0} phases · Gen {s.generation} · Used {s.times_used}x
                  {Object.keys(s.defense_bypasses || {}).length > 0 && (
                    <span style={S.tag("#89b4fa")}>
                      {Object.keys(s.defense_bypasses).length} bypasses
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Experience Memory */}
        <div style={S.section}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Experience Memory</h3>
          {memory?.stats && (
            <div style={S.grid2}>
              <MetricCard label="Total Experiences" value={memory.stats.total_experiences ?? 0} color="#89b4fa" />
              <MetricCard label="Patterns Found" value={memory.stats.patterns_identified ?? 0} color="#cba6f7" />
              <MetricCard label="Success Strategies" value={memory.stats.success_strategies ?? 0} color="#a6e3a1" />
              <MetricCard label="Failure Patterns" value={memory.stats.failure_patterns ?? 0} color="#f38ba8" />
            </div>
          )}
          <h4 style={{ fontSize: "0.85rem", color: "#a6adc8", marginTop: "1rem", marginBottom: "0.5rem" }}>
            Recent Experiences
          </h4>
          <div style={{ maxHeight: "180px", overflowY: "auto" }}>
            {(memory?.recent_experiences || []).slice(0, 10).map((e) => (
              <div
                key={e.id}
                style={{
                  background: "#11111b",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  marginBottom: "4px",
                  fontSize: "0.75rem",
                  display: "flex",
                  justifyContent: "space-between",
                }}
              >
                <span style={{ color: "#cdd6f4" }}>{e.technique} → {e.target_type}</span>
                <span style={S.tag(e.outcome === "success" ? "#a6e3a1" : "#f38ba8")}>
                  {e.outcome}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Comparison vs Mythos */}
      <div style={S.section}>
        <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>OmniMorph-OS vs Claude Mythos</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr 2fr", gap: "0.5rem", fontSize: "0.8rem" }}>
          <div style={{ fontWeight: 600, color: "#a6adc8", padding: "8px" }}>Domain</div>
          <div style={{ fontWeight: 600, color: "#f38ba8", padding: "8px" }}>Claude Mythos</div>
          <div style={{ fontWeight: 600, color: "#a6e3a1", padding: "8px" }}>OmniMorph-OS</div>

          {[
            ["Architecture", "Single model", comparison.architecture || "Multi-agent specialized"],
            ["Learning", "Static, does not evolve", comparison.learning || "Continuous learning"],
            ["Strategies", "Fixed prompts", comparison.strategies || "Evolving strategies"],
            ["Availability", "200 organizations only", "Open-source, locally deployable"],
            ["Targeting", "Open-source software only", "Open + closed-source"],
            ["OT Systems", "Failed 'Cooling Tower' test", "Specialized OT agents"],
            ["Prioritization", "10K vulns unclassified", "Risk-scored + prioritized"],
            ["Autonomy", "Requires initial access", "Fully autonomous reconnaissance"],
          ].map(([domain, mythos, omni], i) => (
            <div key={domain} style={{ display: "contents" }}>
              <div style={{ padding: "6px 8px", color: "#cdd6f4", background: i % 2 ? "#11111b" : "transparent", borderRadius: "4px" }}>
                {domain}
              </div>
              <div style={{ padding: "6px 8px", color: "#f38ba8", background: i % 2 ? "#11111b" : "transparent", borderRadius: "4px", opacity: 0.8 }}>
                {mythos}
              </div>
              <div style={{ padding: "6px 8px", color: "#a6e3a1", background: i % 2 ? "#11111b" : "transparent", borderRadius: "4px" }}>
                {omni}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
