import { useEffect, useState } from "react";
import { api, type HealthResponse } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const SHOWCASE_LINKS = [
  { route: "welcome", label: "Welcome", icon: "🎭", desc: "Project overview & walkthrough" },
  { route: "what-is-dtn", label: "What is DTN?", icon: "📡", desc: "Delay-tolerant networking explained" },
  { route: "how-it-works", label: "How It Works", icon: "⚙", desc: "Architecture deep-dive" },
  { route: "the-network", label: "The Network", icon: "🌐", desc: "5-tier topology (241 nodes)" },
  { route: "journey-to-mars", label: "Journey to Mars", icon: "🚀", desc: "The communication challenge" },
  { route: "why-it-matters", label: "Why It Matters", icon: "🎯", desc: "Real-world significance" },
  { route: "study", label: "Resources", icon: "📚", desc: "64+ academic references" },
  { route: "glossary", label: "Glossary", icon: "📖", desc: "Key terms & definitions" },
  { route: "quiz", label: "Quiz", icon: "✓", desc: "Test your knowledge" },
];

const DASHBOARD_RESOURCES = [
  { type: "RFC", title: "RFC 9171 — Bundle Protocol v7", url: "https://www.rfc-editor.org/rfc/rfc9171", badge: "MUST READ" },
  { type: "RFC", title: "RFC 4838 — DTN Architecture", url: "https://www.rfc-editor.org/rfc/rfc4838", badge: "ESSENTIAL" },
  { type: "Paper", title: "Fall — 'A Delay-Tolerant Network Architecture' (2003)", url: "https://dl.acm.org/doi/10.1145/863955.863960", badge: "FOUNDATIONAL" },
  { type: "Software", title: "ION-DTN — Reference BPv7 Implementation", url: "https://sourceforge.net/projects/ion-dtn/", badge: "HANDS-ON" },
  { type: "Standard", title: "CCSDS 734.2-B-1 — DTN Architecture (Blue Book)", url: "https://public.ccsds.org/Pubs/734x2b1.pdf", badge: "CCSDS" },
];

export function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.health().then(setHealth).catch(() => setError("Backend unreachable — start with ./scripts/dev.sh start"));
  }, []);

  return (
    <>
      <div className="page-header">
        <h2>Mission Control</h2>
        <p>
          AETHERIX Interplanetary DTN Platform v{health?.version ?? "..."}
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <InfoBubble title="What is AETHERIX?" learnMoreUrl={`${SHOWCASE_URL}/#welcome`}>
        <p>
          AETHERIX (Autonomous Extraterrestrial High-throughput Enhancing Routing
          and Inter-planetary eXchange) is an architecture for{" "}
          <strong>delay-tolerant networking (DTN)</strong> between Earth and Mars.
        </p>
        <p style={{ marginTop: 8 }}>
          A round-trip to Mars takes <strong>6 to 44 minutes</strong>. During
          solar conjunction, there is a <strong>2-week complete blackout</strong>.
          TCP/IP was designed for Earth, where computers are always connected and
          signals travel in milliseconds. Space has none of those luxuries — so
          AETHERIX embraces delay and disconnection as normal operating conditions,
          using <strong>Bundle Protocol v7</strong> (RFC 9171),{" "}
          <strong>reinforcement learning routing</strong>,{" "}
          <strong>quantum key distribution</strong>, and{" "}
          <strong>hybrid optical/RF communications</strong>.
        </p>
        <p style={{ marginTop: 8 }}>
          The 5-tier network spans <strong>241 nodes</strong>: Earth ground stations
          (DSN), Earth orbital relays, deep-space Lagrange-point relays, Mars
          orbital relays, and Mars surface assets. Navigate to each module page
          using the sidebar.
        </p>
      </InfoBubble>

      <div className="grid grid-4">
        <div className="stat-card">
          <div className="label">API Status</div>
          <div
            className={`value ${
              health?.status === "ok" ? "success" : error ? "danger" : "warning"
            }`}
          >
            {health?.status ?? (error ? "down" : "...")}
          </div>
          <div className="sub">
            {error
              ? "Start the backend"
              : `Uptime: ${health?.uptime_seconds ?? 0}s`}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Database</div>
          <div
            className={`value ${
              health?.database === "connected" ? "success" : "warning"
            }`}
          >
            {health?.database ?? "..."}
          </div>
          <div className="sub">SQLite local / PostgreSQL docker</div>
        </div>
        <div className="stat-card">
          <div className="label">Earth–Mars Range</div>
          <div className="value info">54.6–401M km</div>
          <div className="sub">3–22 min one-way light delay</div>
        </div>
        <div className="stat-card">
          <div className="label">Network Tiers</div>
          <div className="value accent">5</div>
          <div className="sub">241 nodes across 5 tiers</div>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <div className="card">
          <div className="card-header">
            <h3>Platform Modules</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Module</th>
                <th>Path</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Link Budget</td><td>/link-budget</td><td><span className="badge badge-success">Active</span></td></tr>
              <tr><td>RL Routing</td><td>/routing</td><td><span className="badge badge-success">Active</span></td></tr>
              <tr><td>Orbital</td><td>/orbital</td><td><span className="badge badge-success">Active</span></td></tr>
              <tr><td>QKD Security</td><td>/security</td><td><span className="badge badge-success">Active</span></td></tr>
              <tr><td>Bundle Protocol</td><td>/routing</td><td><span className="badge badge-info">Demo</span></td></tr>
            </tbody>
          </table>
        </div>
        <div className="card">
          <div className="card-header">
            <h3>Quick Actions</h3>
          </div>
          <div className="flex flex-col gap-4">
            <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
              Navigate to each module using the sidebar to run calculations,
              simulations, and protocol demos.
            </p>
            <div className="grid grid-2">
              <div className="stat-card">
                <div className="label">Optical Link</div>
                <div className="value accent" style={{ fontSize: 22 }}>1550 nm</div>
                <div className="sub">Near-IR wavelength</div>
              </div>
              <div className="stat-card">
                <div className="label">QKD Protocol</div>
                <div className="value success" style={{ fontSize: 22 }}>BB84</div>
                <div className="sub">QBER &lt; 11%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <div className="card-header">
          <h3>Showcase &amp; Learning</h3>
          <a
            href={SHOWCASE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary btn-sm"
          >
            Open Full Showcase &rarr;
          </a>
        </div>
        <p style={{ color: "var(--text-secondary)", fontSize: 13, marginBottom: 16 }}>
          Explore the interactive showcase site for in-depth explanations, visual demos, quizzes, and all 64+ academic references.
        </p>
        <div className="showcase-links-grid">
          {SHOWCASE_LINKS.map((link) => (
            <a
              key={link.route}
              href={`${SHOWCASE_URL}/#${link.route}`}
              target="_blank"
              rel="noopener noreferrer"
              className="showcase-link-card"
            >
              <span className="showcase-link-icon">{link.icon}</span>
              <span className="showcase-link-label">{link.label}</span>
              <span className="showcase-link-desc">{link.desc}</span>
            </a>
          ))}
        </div>
      </div>

      <ResourcesCard title="Key DTN Resources" links={DASHBOARD_RESOURCES} />
    </>
  );
}
