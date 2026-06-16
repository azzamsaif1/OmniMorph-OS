/**
 * Career — Professional Evolution Simulator Page (Feature 19).
 *
 * Simulates career paths based on measured capabilities and
 * suggests optimal educational/professional opportunities.
 */

import { useState, useEffect } from "react";

export default function Career() {
  const [careerData, setCareerData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/enterprise/career/default")
      .then((r) => r.json())
      .then(setCareerData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Career Evolution Simulator
      </h1>

      {loading ? (
        <p style={{ color: "#a6adc8" }}>Loading career simulation...</p>
      ) : (
        <>
          {/* Current Position */}
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
              Current Position Assessment
            </h2>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
              <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Estimated Level</div>
                <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "#a6e3a1" }}>
                  {careerData?.current_level || "Mid-Senior"}
                </div>
              </div>
              <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Strongest Domain</div>
                <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "#89b4fa" }}>
                  {careerData?.strongest_domain || "Backend Systems"}
                </div>
              </div>
              <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px" }}>
                <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Growth Velocity</div>
                <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "#f9e2af" }}>
                  {careerData?.growth_velocity || "+12%/quarter"}
                </div>
              </div>
            </div>
          </section>

          {/* Recommended Paths */}
          <section
            style={{
              background: "#1e1e2e",
              borderRadius: "8px",
              padding: "1.5rem",
              border: "1px solid #313244",
            }}
          >
            <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
              Recommended Career Paths
            </h2>
            <div style={{ display: "grid", gap: "1rem" }}>
              {(careerData?.paths || defaultPaths).map((path, i) => (
                <div
                  key={i}
                  style={{
                    background: "#313244",
                    padding: "1rem",
                    borderRadius: "6px",
                    borderLeft: `3px solid ${["#89b4fa", "#a6e3a1", "#f9e2af"][i % 3]}`,
                  }}
                >
                  <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>
                    {path.title}
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "#a6adc8", marginBottom: "0.5rem" }}>
                    {path.description}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "#585b70" }}>
                    Timeline: {path.timeline} • Fit Score: {path.fit_score}%
                  </div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

const defaultPaths = [
  {
    title: "Staff Engineer — Distributed Systems",
    description: "Deep specialization in large-scale distributed architectures. Focus on consensus, sharding, and fault tolerance.",
    timeline: "18-24 months",
    fit_score: 87,
  },
  {
    title: "Engineering Manager — Platform",
    description: "Transition to people leadership while maintaining technical depth in developer tooling and infrastructure.",
    timeline: "12-18 months",
    fit_score: 72,
  },
  {
    title: "Principal Engineer — Full Stack",
    description: "Broad technical leadership across frontend and backend, driving architectural decisions org-wide.",
    timeline: "24-36 months",
    fit_score: 65,
  },
];
