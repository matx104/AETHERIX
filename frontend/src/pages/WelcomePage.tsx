import { SHOWCASE_URL } from "../components/ResourcesCard";

const FEATURES = [
  { icon: "⟡", title: "Link Budget Calculator", desc: "Optical and RF link budget analysis for Earth–Mars communications. Scenario-based calculations with full signal path modelling.", page: "/link-budget", showcase: "link-budget" },
  { icon: "⟳", title: "RL Routing Agent", desc: "Reinforcement learning-based routing for DTN bundles. Q-learning with epsilon-greedy policy and multi-agent federated learning.", page: "/routing", showcase: "routing" },
  { icon: "◎", title: "Orbital Mechanics", desc: "Earth–Mars distance timeline, light-time delay explorer, and synodic period visualization with true anomaly slider.", page: "/orbital", showcase: "orbital" },
  { icon: "⚷", title: "QKD Security", desc: "BB84 and E91 quantum key distribution simulation. QBER analysis, eavesdropper detection, and session history.", page: "/security", showcase: "qkd" },
  { icon: "▶", title: "Simulations", desc: "Create and manage simulation runs with reproducible seeds and scenarios. End-to-end network simulation engine.", page: "/simulations", showcase: "simulation" },
  { icon: "⌘", title: "Command Reference", desc: "Copy-and-run reference for every script and module demo, with what each does and the output to expect.", page: "/cmd", showcase: "cmd-terminal" },
];

const QUICK_LINKS = [
  { label: "What is DTN?", route: "what-is-dtn" },
  { label: "How It Works", route: "how-it-works" },
  { label: "Journey to Mars", route: "journey-to-mars" },
  { label: "The Network", route: "the-network" },
  { label: "Space Security", route: "space-security" },
  { label: "Optical Comms", route: "optical-comms" },
  { label: "QKD Science", route: "qkd-science" },
  { label: "RL Routing", route: "reinforcement-learning" },
  { label: "Radiation", route: "radiation" },
  { label: "Data Priority", route: "prioritization" },
  { label: "Standards", route: "deep-space-standards" },
  { label: "Resources", route: "study" },
];

export function WelcomePage() {
  return (
    <>
      <div className="welcome-hero">
        <img src="/logo.svg" alt="AETHERIX" className="welcome-logo" />
        <h1 className="welcome-title">AETHERIX</h1>
        <p className="welcome-subtitle">
          Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange
        </p>
        <p className="welcome-tagline">
          Delay-tolerant networking between Earth and Mars — powered by RL routing, quantum key distribution, and hybrid optical/RF communications
        </p>
        <div className="welcome-actions">
          <a href="/dashboard" className="btn btn-primary">Open Dashboard &rarr;</a>
          <a href={`${SHOWCASE_URL}/#welcome`} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">Explore Showcase &rarr;</a>
        </div>
      </div>

      <div className="welcome-stats">
        <div className="stat-card">
          <div className="label">Network Nodes</div>
          <div className="value accent">241</div>
          <div className="sub">5-tier topology</div>
        </div>
        <div className="stat-card">
          <div className="label">Unit Tests</div>
          <div className="value success">189</div>
          <div className="sub">10 test modules</div>
        </div>
        <div className="stat-card">
          <div className="label">Earth–Mars Range</div>
          <div className="value info">54.6–401M km</div>
          <div className="sub">3–22 min one-way delay</div>
        </div>
        <div className="stat-card">
          <div className="label">Standards</div>
          <div className="value warning">7</div>
          <div className="sub">CCSDS Blue Books & RFCs</div>
        </div>
        <div className="stat-card">
          <div className="label">Academic Refs</div>
          <div className="value info">64+</div>
          <div className="sub">IEEE format citations</div>
        </div>
      </div>

      <div className="page-header" style={{ marginTop: 32 }}>
        <h2>Modules</h2>
        <p>Each module is a fully interactive tool. Click to start using it, or visit the showcase for the science behind it.</p>
      </div>

      <div className="welcome-features">
        {FEATURES.map((f) => (
          <a key={f.page} href={f.page} className="welcome-feature-card">
            <span className="welcome-feature-icon">{f.icon}</span>
            <span className="welcome-feature-title">{f.title}</span>
            <span className="welcome-feature-desc">{f.desc}</span>
            <span className="welcome-feature-link">
              Open tool &rarr;
            </span>
            <span
              className="welcome-feature-showcase"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                window.open(`${SHOWCASE_URL}/#${f.showcase}`, "_blank");
              }}
            >
              Learn the science &rarr;
            </span>
          </a>
        ))}
      </div>

      <div className="card" style={{ marginTop: 24 }}>
        <div className="card-header">
          <h3>Showcase &amp; Deep-Dives</h3>
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
          The interactive showcase site covers the theory, science, and standards behind every module — with visual demos, quizzes, and 64+ academic references.
        </p>
        <div className="showcase-links-grid">
          {QUICK_LINKS.map((link) => (
            <a
              key={link.route}
              href={`${SHOWCASE_URL}/#${link.route}`}
              target="_blank"
              rel="noopener noreferrer"
              className="showcase-link-card"
            >
              <span className="showcase-link-label">{link.label}</span>
              <span className="showcase-link-desc">Open in showcase &rarr;</span>
            </a>
          ))}
        </div>
      </div>
    </>
  );
}
