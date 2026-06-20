/**
 * Compete — Competitive Engineering Twin (Feature 7).
 *
 * Head-to-head coding challenges against an AI twin calibrated
 * to the user's skill level.
 */

import { useState, useEffect } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function Compete() {
  const [stats, setStats] = useState(null);
  const [challenge, setChallenge] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/twin/compete/stats/default")
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});
  }, []);

  const generateChallenge = async () => {
    setLoading(true);
    setResult(null);
    try {
      const resp = await fetch("/api/twin/compete/challenge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "default", domain: "backend", difficulty: "auto" }),
      });
      const data = await resp.json();
      setChallenge(data);
    } catch (err) {
      console.error("Failed to generate challenge:", err);
    } finally {
      setLoading(false);
    }
  };

  const submitResult = async (score) => {
    if (!challenge) return;
    try {
      const resp = await fetch("/api/twin/compete/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "default",
          challenge_id: challenge.challenge_id,
          user_score: score,
          user_time: Math.random() * challenge.time_limit_sec,
          domain: challenge.domain,
          difficulty: challenge.difficulty,
        }),
      });
      const data = await resp.json();
      setResult(data);
      // Refresh stats
      const statsResp = await fetch("/api/twin/compete/stats/default");
      setStats(await statsResp.json());
    } catch (err) {
      console.error("Submit failed:", err);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Competitive Twin
      </h1>

      {/* Stats */}
      {stats && (
        <section style={sectionStyle}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Your Record</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "1rem" }}>
            <div style={{ background: "#313244", padding: "0.75rem", borderRadius: "6px", textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#a6e3a1" }}>{stats.user_wins}</div>
              <div style={{ fontSize: "0.7rem", color: "#a6adc8" }}>Wins</div>
            </div>
            <div style={{ background: "#313244", padding: "0.75rem", borderRadius: "6px", textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#f38ba8" }}>{stats.twin_wins}</div>
              <div style={{ fontSize: "0.7rem", color: "#a6adc8" }}>Twin Wins</div>
            </div>
            <div style={{ background: "#313244", padding: "0.75rem", borderRadius: "6px", textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#f9e2af" }}>{stats.ties}</div>
              <div style={{ fontSize: "0.7rem", color: "#a6adc8" }}>Ties</div>
            </div>
            <div style={{ background: "#313244", padding: "0.75rem", borderRadius: "6px", textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#89b4fa" }}>
                {(stats.win_rate * 100).toFixed(0)}%
              </div>
              <div style={{ fontSize: "0.7rem", color: "#a6adc8" }}>Win Rate</div>
            </div>
            <div style={{ background: "#313244", padding: "0.75rem", borderRadius: "6px", textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#cba6f7" }}>
                {stats.current_streak > 0 ? `+${stats.current_streak}` : stats.current_streak}
              </div>
              <div style={{ fontSize: "0.7rem", color: "#a6adc8" }}>Streak</div>
            </div>
          </div>
        </section>
      )}

      {/* Challenge */}
      <section style={sectionStyle}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <h2 style={{ fontSize: "1.1rem" }}>Challenge Arena</h2>
          <button
            onClick={generateChallenge}
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
            {loading ? "Generating..." : "New Challenge"}
          </button>
        </div>

        {challenge && (
          <div style={{ background: "#313244", padding: "1.5rem", borderRadius: "6px" }}>
            <h3 style={{ color: "#89b4fa", marginBottom: "0.5rem" }}>{challenge.title}</h3>
            <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", fontSize: "0.8rem" }}>
              <span style={{ color: "#f9e2af" }}>Difficulty: {challenge.difficulty}</span>
              <span style={{ color: "#a6adc8" }}>Time limit: {Math.round(challenge.time_limit_sec / 60)}min</span>
              <span style={{ color: "#cba6f7" }}>Twin level: {challenge.twin_level}</span>
            </div>
            <p style={{ fontSize: "0.85rem", color: "#a6adc8", marginBottom: "1rem", fontStyle: "italic" }}>
              {challenge.twin_message}
            </p>

            {!result && (
              <div style={{ display: "flex", gap: "0.5rem" }}>
                {[0.3, 0.5, 0.7, 0.9, 1.0].map((score) => (
                  <button
                    key={score}
                    onClick={() => submitResult(score)}
                    style={{
                      padding: "0.5rem 1rem",
                      borderRadius: "4px",
                      background: "#45475a",
                      color: "#cdd6f4",
                      border: "none",
                      cursor: "pointer",
                      fontSize: "0.8rem",
                    }}
                  >
                    Score: {(score * 100).toFixed(0)}%
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      {/* Result */}
      {result && (
        <section style={{
          ...sectionStyle,
          borderColor: result.winner === "user" ? "#a6e3a1" : result.winner === "twin" ? "#f38ba8" : "#f9e2af",
        }}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
            Result: {result.winner === "user" ? "You Win!" : result.winner === "twin" ? "Twin Wins" : "Tie!"}
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "0.8rem", color: "#a6adc8" }}>Your Score</div>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#a6e3a1" }}>
                {(result.user_score * 100).toFixed(0)}%
              </div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "0.8rem", color: "#a6adc8" }}>Twin Score</div>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#f38ba8" }}>
                {(result.twin_score * 100).toFixed(0)}%
              </div>
            </div>
          </div>
          <p style={{ fontSize: "0.85rem", color: "#a6adc8" }}>{result.feedback}</p>
        </section>
      )}
    </div>
  );
}
