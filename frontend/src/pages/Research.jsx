/**
 * Research — Autonomous Research Intelligence Feed (Feature 6).
 *
 * Displays latest arXiv papers, GitHub trending repos, and
 * auto-generated knowledge insights from the research engine.
 */

import { useState, useEffect } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function Research() {
  const [papers, setPapers] = useState([]);
  const [repos, setRepos] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const searchPapers = async () => {
    if (!searchQuery) return;
    setLoading(true);
    try {
      const resp = await fetch("/api/research/arxiv/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery, max_results: 10 }),
      });
      const data = await resp.json();
      setPapers(data.results || []);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrending = async () => {
    setLoading(true);
    try {
      const resp = await fetch("/api/research/github/trending", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language: "python", min_stars: 100, limit: 10 }),
      });
      const data = await resp.json();
      setRepos(data.results || []);
    } catch (err) {
      console.error("Trending failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrending();
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Research Intelligence
      </h1>

      {/* Search */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem" }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && searchPapers()}
          placeholder="Search arXiv papers..."
          style={{
            flex: 1,
            padding: "0.5rem 1rem",
            borderRadius: "4px",
            background: "#313244",
            color: "#cdd6f4",
            border: "1px solid #45475a",
          }}
        />
        <button
          onClick={searchPapers}
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
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Papers */}
      {papers.length > 0 && (
        <section style={sectionStyle}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
            arXiv Papers
          </h2>
          <div style={{ display: "grid", gap: "0.75rem" }}>
            {papers.map((p, i) => (
              <a
                key={i}
                href={p.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "block",
                  background: "#313244",
                  padding: "1rem",
                  borderRadius: "6px",
                  color: "#cdd6f4",
                  textDecoration: "none",
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: "0.25rem", color: "#89b4fa" }}>
                  {p.title}
                </div>
                <div style={{ fontSize: "0.8rem", color: "#a6adc8" }}>
                  {p.abstract_snippet}
                </div>
                <div style={{ fontSize: "0.7rem", color: "#585b70", marginTop: "0.5rem" }}>
                  {(p.categories || []).join(", ")} | {p.published?.slice(0, 10)}
                </div>
              </a>
            ))}
          </div>
        </section>
      )}

      {/* Trending Repos */}
      <section style={sectionStyle}>
        <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
          Trending GitHub Repositories
        </h2>
        {repos.length > 0 ? (
          <div style={{ display: "grid", gap: "0.75rem" }}>
            {repos.map((r, i) => (
              <a
                key={i}
                href={r.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "block",
                  background: "#313244",
                  padding: "1rem",
                  borderRadius: "6px",
                  color: "#cdd6f4",
                  textDecoration: "none",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <div style={{ fontWeight: 600, color: "#a6e3a1" }}>
                    {r.full_name}
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#f9e2af" }}>
                    {r.stars?.toLocaleString()} stars
                  </div>
                </div>
                <div style={{ fontSize: "0.8rem", color: "#a6adc8", marginTop: "0.25rem" }}>
                  {r.description}
                </div>
                {r.language && (
                  <span style={{
                    display: "inline-block",
                    marginTop: "0.5rem",
                    padding: "0.15rem 0.5rem",
                    borderRadius: "10px",
                    background: "#45475a",
                    fontSize: "0.7rem",
                  }}>
                    {r.language}
                  </span>
                )}
              </a>
            ))}
          </div>
        ) : (
          <p style={{ color: "#a6adc8" }}>Loading trending repos...</p>
        )}
      </section>
    </div>
  );
}
