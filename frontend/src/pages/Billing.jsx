/**
 * Billing — Subscription plans and payment management.
 */

import { useState, useEffect } from "react";

const sectionStyle = {
  background: "#1e1e2e",
  borderRadius: "8px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
  border: "1px solid #313244",
};

export default function Billing() {
  const [plans, setPlans] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [revenue, setRevenue] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/billing/plans").then((r) => r.json()),
      fetch("/api/billing/subscription/default").then((r) => r.json()),
      fetch("/api/billing/revenue").then((r) => r.json()),
    ])
      .then(([p, sub, rev]) => {
        setPlans(p.plans || {});
        setSubscription(sub);
        setRevenue(rev);
      })
      .catch(() => {});
  }, []);

  const subscribe = async (plan) => {
    try {
      const resp = await fetch("/api/billing/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "default", plan }),
      });
      const data = await resp.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        setSubscription(data);
      }
    } catch (err) {
      console.error("Subscribe failed:", err);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "system-ui, sans-serif", color: "#cdd6f4" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>Billing</h1>

      {/* Current Subscription */}
      {subscription && (
        <section style={sectionStyle}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Current Plan</h2>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <span style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              background: "#45475a",
              fontWeight: 600,
              textTransform: "capitalize",
              color: "#89b4fa",
            }}>
              {subscription.plan}
            </span>
            <span style={{
              padding: "0.25rem 0.75rem",
              borderRadius: "12px",
              background: subscription.status === "active" ? "#2d4a2d" : "#4a2d2d",
              fontSize: "0.8rem",
              color: subscription.status === "active" ? "#a6e3a1" : "#f38ba8",
            }}>
              {subscription.status}
            </span>
          </div>
        </section>
      )}

      {/* Plans */}
      {plans && (
        <section style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}>
          {Object.entries(plans).map(([key, plan]) => (
            <div key={key} style={{
              background: "#1e1e2e",
              borderRadius: "8px",
              padding: "1.5rem",
              border: key === "pro" ? "2px solid #89b4fa" : "1px solid #313244",
            }}>
              <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem", color: "#cdd6f4" }}>
                {plan.name}
              </h3>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#f9e2af", marginBottom: "1rem" }}>
                ${(plan.price_monthly_cents / 100).toFixed(0)}
                <span style={{ fontSize: "0.8rem", fontWeight: 400, color: "#a6adc8" }}>/mo</span>
              </div>
              <ul style={{ paddingLeft: "1rem", marginBottom: "1rem" }}>
                {plan.features.map((f, i) => (
                  <li key={i} style={{ fontSize: "0.8rem", color: "#a6adc8", padding: "0.15rem 0" }}>
                    {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => subscribe(key)}
                disabled={subscription?.plan === key}
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  background: subscription?.plan === key ? "#45475a" : "#89b4fa",
                  color: subscription?.plan === key ? "#a6adc8" : "#1e1e2e",
                  border: "none",
                  fontWeight: 600,
                  cursor: subscription?.plan === key ? "default" : "pointer",
                }}
              >
                {subscription?.plan === key ? "Current Plan" : "Subscribe"}
              </button>
            </div>
          ))}
        </section>
      )}

      {/* Revenue Summary */}
      {revenue && (
        <section style={sectionStyle}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>Revenue Summary</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1rem" }}>
            <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px", textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#a6e3a1" }}>
                ${revenue.mrr_dollars?.toFixed(2)}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>MRR</div>
            </div>
            <div style={{ background: "#313244", padding: "1rem", borderRadius: "6px", textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#89b4fa" }}>
                {revenue.active_subscriptions}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#a6adc8" }}>Active Subs</div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
