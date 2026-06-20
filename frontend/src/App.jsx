import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import AdaptiveLayout from "./layouts/AdaptiveLayout.jsx";
import { useSensing } from "./hooks/useSensing.js";
import { useAdaptation } from "./hooks/useAdaptation.js";
import Dashboard from "./pages/Dashboard.jsx";
import Training from "./pages/Training.jsx";
import Career from "./pages/Career.jsx";
import Enterprise from "./pages/Enterprise.jsx";
import Research from "./pages/Research.jsx";
import DigitalTwin from "./pages/DigitalTwin.jsx";
import Compete from "./pages/Compete.jsx";
import Billing from "./pages/Billing.jsx";
import Settings from "./pages/Settings.jsx";
import Governance from "./pages/Governance.jsx";

const navStyle = {
  display: "flex",
  gap: 4,
  padding: "8px 24px",
  borderBottom: "1px solid #1a1a2e",
  background: "#0d0d14",
  flexWrap: "wrap",
};

const linkStyle = {
  padding: "6px 12px",
  fontSize: "0.8rem",
  color: "#888",
  textDecoration: "none",
  borderRadius: 4,
  transition: "all 0.2s",
};

const activeLinkStyle = {
  ...linkStyle,
  color: "#e0e0ff",
  background: "#1a1a2e",
};

function NavBar({ mentalState, uiMode }) {
  return (
    <>
      <header
        style={{
          padding: "10px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #1a1a2e",
          background: "#0a0a0f",
        }}
      >
        <NavLink
          to="/"
          style={{ textDecoration: "none", color: "inherit" }}
        >
          <h1
            style={{ fontSize: "1.1rem", fontWeight: 600, letterSpacing: 1 }}
          >
            UCSK
          </h1>
        </NavLink>
        <div style={{ fontSize: "0.8rem", opacity: 0.7 }}>
          State: <strong>{mentalState?.state || "idle"}</strong> &middot;
          Mode: <strong>{uiMode}</strong>
        </div>
      </header>
      <nav style={navStyle}>
        {[
          { to: "/", label: "Workspace" },
          { to: "/dashboard", label: "Dashboard" },
          { to: "/training", label: "Training" },
          { to: "/compete", label: "Compete" },
          { to: "/twin", label: "Digital Twin" },
          { to: "/career", label: "Career" },
          { to: "/enterprise", label: "Enterprise" },
          { to: "/research", label: "Research" },
          { to: "/governance", label: "Governance" },
          { to: "/billing", label: "Billing" },
          { to: "/settings", label: "Settings" },
        ].map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            style={({ isActive }) => (isActive ? activeLinkStyle : linkStyle)}
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </>
  );
}

function WorkspaceView({ uiMode, directive, mentalState, sendBehavior }) {
  return (
    <AdaptiveLayout
      uiMode={uiMode}
      directive={directive}
      mentalState={mentalState}
      onBehavior={sendBehavior}
    />
  );
}

function AppContent() {
  const { mentalState, directive: wsDirective, sendBehavior } = useSensing();
  const { directive, uiMode } = useAdaptation(mentalState, wsDirective);

  return (
    <div
      className="ucsk-app"
      style={{ minHeight: "100vh", background: "var(--bg, #0a0a0f)", color: "#cdd6f4" }}
    >
      <NavBar mentalState={mentalState} uiMode={uiMode} />
      <Routes>
        <Route
          path="/"
          element={
            <WorkspaceView
              uiMode={uiMode}
              directive={directive}
              mentalState={mentalState}
              sendBehavior={sendBehavior}
            />
          }
        />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/training" element={<Training />} />
        <Route path="/compete" element={<Compete />} />
        <Route path="/twin" element={<DigitalTwin />} />
        <Route path="/career" element={<Career />} />
        <Route path="/enterprise" element={<Enterprise />} />
        <Route path="/research" element={<Research />} />
        <Route path="/governance" element={<Governance />} />
        <Route path="/billing" element={<Billing />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
