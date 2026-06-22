/**
 * SystemMonitoring — Real-time observability dashboard.
 *
 * Shows agent health, performance analysis, self-healing status,
 * request metrics, and system events timeline.
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
};

const statusColors = {
  healthy: "#a6e3a1",
  degraded: "#f9e2af",
  error: "#f38ba8",
  critical: "#f38ba8",
  offline: "#585b70",
  warning: "#fab387",
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

function StatusBadge({ status }) {
  const color = statusColors[status] || "#585b70";
  return <span style={S.tag(color)}>{status}</span>;
}

export default function SystemMonitoring() {
  const [data, setData] = useState(null);
  const [healing, setHealing] = useState(false);

  const fetchData = useCallback(() => {
    fetch("/api/monitoring/dashboard").then(r => r.json()).then(setData).catch(() => {});
  }, []);

  useEffect(() => { fetchData(); const t = setInterval(fetchData, 5000); return () => clearInterval(t); }, [fetchData]);

  const runHealing = async () => {
    setHealing(true);
    try {
      await fetch("/api/monitoring/heal", { method: "POST" });
      fetchData();
    } finally {
      setHealing(false);
    }
  };

  const sys = data?.system || {};
  const health = sys.health || {};
  const perf = data?.performance || {};
  const heal = data?.healing || {};
  const domains = sys.domains || {};
  const events = sys.recent_events || [];
  const requests = sys.requests || {};
  const trends = perf.trends?.trends || {};
  const recommendations = perf.recommendations || [];
  const perfHealth = perf.health || {};

  return (
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h2 style={{ fontSize: "1.4rem", marginBottom: "0.25rem" }}>System Monitoring</h2>
          <p style={{ color: "#a6adc8", fontSize: "0.85rem" }}>
            Real-time observability, performance analysis, and self-healing
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button onClick={runHealing} disabled={healing} style={S.btn(healing ? "#585b70" : "#a6e3a1")}>
            {healing ? "Healing..." : "Run Self-Heal"}
          </button>
          <button onClick={fetchData} style={S.btn("#89b4fa")}>Refresh</button>
        </div>
      </div>

      {/* Health Overview */}
      <div style={{ ...S.grid4, marginBottom: "1.5rem" }}>
        <MetricCard
          label="System Status"
          value={health.overall_status?.toUpperCase() || "—"}
          color={statusColors[health.overall_status] || "#585b70"}
        />
        <MetricCard label="Total Agents" value={health.total_agents ?? 0} color="#89b4fa" sub={`${health.healthy ?? 0} healthy`} />
        <MetricCard label="Total Requests" value={health.total_requests ?? 0} color="#cba6f7" />
        <MetricCard
          label="Error Rate"
          value={((health.global_error_rate ?? 0) * 100).toFixed(2) + "%"}
          color={(health.global_error_rate ?? 0) > 0.05 ? "#f38ba8" : "#a6e3a1"}
        />
      </div>

      <div style={S.grid2}>
        {/* Domain Health */}
        <div style={S.section}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Domain Health</h3>
          {Object.entries(domains).map(([domain, info]) => (
            <div
              key={domain}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "8px",
                background: "#11111b",
                borderRadius: "4px",
                marginBottom: "4px",
                fontSize: "0.8rem",
              }}
            >
              <div>
                <strong style={{ color: "#cdd6f4" }}>{domain}</strong>
                <span style={{ color: "#585b70", marginLeft: "8px" }}>{info.agents} agents</span>
              </div>
              <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                <span style={{ color: "#a6adc8" }}>{info.total_requests} req</span>
                <span style={{ color: info.error_rate > 0.05 ? "#f38ba8" : "#a6adc8" }}>
                  {(info.error_rate * 100).toFixed(1)}% err
                </span>
                <StatusBadge status={info.healthy === info.agents ? "healthy" : "degraded"} />
              </div>
            </div>
          ))}
        </div>

        {/* Performance Issues */}
        <div style={S.section}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
            Performance Issues ({perfHealth.open_issues ?? 0})
          </h3>
          <div style={{
            fontSize: "0.85rem",
            marginBottom: "1rem",
            padding: "8px",
            background: "#11111b",
            borderRadius: "6px",
          }}>
            Health: <StatusBadge status={perfHealth.overall_health || "healthy"} />
            <span style={{ color: "#585b70", marginLeft: "8px" }}>
              {perfHealth.metrics_tracked ?? 0} metrics tracked
            </span>
          </div>
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            {(perfHealth.issues || []).map((issue) => (
              <div
                key={issue.id}
                style={{
                  background: "#11111b",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  marginBottom: "4px",
                  fontSize: "0.75rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "#cdd6f4" }}>{issue.metric}</span>
                  <StatusBadge status={issue.severity} />
                </div>
                <div style={{ color: "#585b70", marginTop: 2 }}>{issue.description}</div>
                {issue.auto_fixable && (
                  <span style={S.tag("#a6e3a1")}>auto-fixable</span>
                )}
              </div>
            ))}
            {(perfHealth.issues || []).length === 0 && (
              <div style={{ color: "#585b70", fontSize: "0.8rem", textAlign: "center", padding: "1rem" }}>
                No issues detected
              </div>
            )}
          </div>
        </div>
      </div>

      <div style={S.grid2}>
        {/* Self-Healing */}
        <div style={S.section}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Self-Healing Engine</h3>
          <div style={S.grid2}>
            <MetricCard label="Total Actions" value={heal.total_actions ?? 0} color="#89b4fa" />
            <MetricCard label="Applied" value={heal.applied ?? 0} color="#a6e3a1" />
          </div>
          <h4 style={{ fontSize: "0.85rem", color: "#a6adc8", marginTop: "1rem", marginBottom: "0.5rem" }}>
            Tunable Parameters
          </h4>
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            {Object.entries(heal.tunable_params || {}).map(([key, param]) => (
              <div
                key={key}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "6px 8px",
                  background: "#11111b",
                  borderRadius: "4px",
                  marginBottom: "2px",
                  fontSize: "0.75rem",
                }}
              >
                <span style={{ color: "#a6adc8" }}>{key}</span>
                <span style={{ color: "#cdd6f4", fontFamily: "monospace" }}>
                  {param.current} <span style={{ color: "#585b70" }}>({param.min}–{param.max})</span>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Request Metrics */}
        <div style={S.section}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Request Metrics (5min)</h3>
          <div style={S.grid2}>
            <MetricCard label="Total Requests" value={requests.total_requests ?? 0} color="#89b4fa" />
            <MetricCard
              label="Avg Response"
              value={(requests.avg_response_time_ms ?? 0).toFixed(0) + "ms"}
              color={(requests.avg_response_time_ms ?? 0) > 200 ? "#f9e2af" : "#a6e3a1"}
            />
          </div>
          {requests.top_endpoints && (
            <>
              <h4 style={{ fontSize: "0.85rem", color: "#a6adc8", marginTop: "1rem", marginBottom: "0.5rem" }}>
                Top Endpoints
              </h4>
              {Object.entries(requests.top_endpoints).map(([ep, info]) => (
                <div
                  key={ep}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    padding: "4px 8px",
                    fontSize: "0.75rem",
                    color: "#a6adc8",
                  }}
                >
                  <span style={{ fontFamily: "monospace" }}>{ep}</span>
                  <span>{info.count}x · {info.avg_ms.toFixed(0)}ms</span>
                </div>
              ))}
            </>
          )}
        </div>
      </div>

      {/* Improvement Recommendations */}
      {recommendations.length > 0 && (
        <div style={S.section}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Improvement Recommendations</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
            {recommendations.slice(0, 6).map((rec, i) => (
              <div
                key={i}
                style={{
                  background: "#11111b",
                  padding: "0.75rem",
                  borderRadius: "6px",
                  fontSize: "0.8rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <strong style={{ color: "#cdd6f4" }}>{rec.domain}: {rec.metric}</strong>
                  <StatusBadge status={rec.priority} />
                </div>
                <div style={{ color: "#585b70", marginTop: 4 }}>
                  {rec.direction} from {typeof rec.current === "number" ? rec.current.toFixed(3) : rec.current}{" "}
                  → target {typeof rec.target === "number" ? rec.target.toFixed(3) : rec.target}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Trends */}
      {Object.keys(trends).length > 0 && (
        <div style={S.section}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Performance Trends</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: "0.5rem" }}>
            {Object.entries(trends).slice(0, 12).map(([key, trend]) => (
              <div
                key={key}
                style={{
                  background: "#11111b",
                  padding: "0.75rem",
                  borderRadius: "6px",
                  fontSize: "0.8rem",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "#cdd6f4", fontFamily: "monospace", fontSize: "0.75rem" }}>{key}</span>
                  <span style={{
                    color: trend.direction === "improving" ? "#a6e3a1" :
                           trend.direction === "degrading" ? "#f38ba8" : "#585b70",
                    fontWeight: 600,
                  }}>
                    {trend.direction} ({trend.change_pct > 0 ? "+" : ""}{trend.change_pct}%)
                  </span>
                </div>
                <div style={{ color: "#585b70", marginTop: 2 }}>
                  Current: {trend.current_avg} · {trend.data_points} points
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Event Timeline */}
      <div style={S.section}>
        <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Event Timeline</h3>
        <div style={{ maxHeight: "300px", overflowY: "auto" }}>
          {events.length === 0 && (
            <div style={{ color: "#585b70", fontSize: "0.8rem", textAlign: "center", padding: "1rem" }}>
              No events recorded yet
            </div>
          )}
          {events.map((evt, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                gap: "0.75rem",
                padding: "6px 0",
                borderBottom: "1px solid #313244",
                fontSize: "0.8rem",
              }}
            >
              <span style={{ color: "#585b70", fontFamily: "monospace", fontSize: "0.7rem", minWidth: "60px" }}>
                {new Date(evt.timestamp * 1000).toLocaleTimeString()}
              </span>
              <StatusBadge status={evt.event_type} />
              <span style={{ color: "#a6adc8" }}>{evt.source}</span>
              <span style={{ color: "#cdd6f4" }}>{evt.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
