import { NavLink, Outlet } from "react-router-dom";
import { SHOWCASE_URL } from "./ResourcesCard";

const navItems = [
  { to: "/", label: "Welcome", icon: "🏠" },
  { to: "/dashboard", label: "Dashboard", icon: "▦" },
  { to: "/link-budget", label: "Link Budget", icon: "⟡" },
  { to: "/routing", label: "RL Routing", icon: "⟳" },
  { to: "/orbital", label: "Orbital", icon: "◎" },
  { to: "/security", label: "QKD Security", icon: "⚷" },
  { to: "/simulations", label: "Simulations", icon: "▶" },
  { to: "/cmd", label: "CMD", icon: "⌘" },
];

export function Layout() {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src="/logo.svg" alt="AETHERIX" className="sidebar-logo" />
          <div className="sidebar-brand-text">
            <h1>AETHERIX</h1>
            <p>Interplanetary DTN Platform</p>
          </div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
          <div style={{ marginTop: 12, marginBottom: 4, paddingLeft: 14 }}>
            <span style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 1, fontWeight: 600 }}>External</span>
          </div>
          <a
            href={`${SHOWCASE_URL}/#welcome`}
            target="_blank"
            rel="noopener noreferrer"
            className="nav-item"
          >
            <span>🌐</span>
            Showcase Site
          </a>
          <a
            href={`${SHOWCASE_URL}/#study`}
            target="_blank"
            rel="noopener noreferrer"
            className="nav-item"
          >
            <span>📚</span>
            Resources
          </a>
          <a
            href={`${SHOWCASE_URL}/#glossary`}
            target="_blank"
            rel="noopener noreferrer"
            className="nav-item"
          >
            <span>📖</span>
            Glossary
          </a>
          <a
            href={`${SHOWCASE_URL}/#quiz`}
            target="_blank"
            rel="noopener noreferrer"
            className="nav-item"
          >
            <span>✓</span>
            Quiz
          </a>
        </nav>
        <div className="sidebar-footer">
          Built by{" "}
          <a
            href="https://github.com/matx104"
            target="_blank"
            rel="noopener noreferrer"
          >
            Muhammad Abdullah Tariq
          </a>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
        <footer className="app-footer">
          <img src="/logo.svg" alt="" className="footer-logo" />
          AETHERIX — Autonomous Extraterrestrial High-throughput Enhancing
          Routing and Inter-planetary eXchange
          <br />
          Designed &amp; built by{" "}
          <span className="author-name">Muhammad Abdullah Tariq</span>{" "}
          &middot;{" "}
          <a href="https://github.com/matx104" target="_blank" rel="noopener noreferrer">GitHub</a>{" "}
          &middot;{" "}
          <a href="https://www.linkedin.com/in/matx104" target="_blank" rel="noopener noreferrer">LinkedIn</a>{" "}
          &middot;{" "}
          <a href="https://matx104.com.pk" target="_blank" rel="noopener noreferrer">Portfolio</a>{" "}
          &middot;{" "}
          <a href="https://matx104.com.pk/assets/Muhammad_Abdullah_Tariq_Resume.pdf" target="_blank" rel="noopener noreferrer">Resume</a>{" "}
          &middot;{" "}
          <a href="https://github.com/matx104/AETHERIX" target="_blank" rel="noopener noreferrer">Repo</a>{" "}
          &middot;{" "}
          <a href={SHOWCASE_URL} target="_blank" rel="noopener noreferrer">Showcase</a>
        </footer>
      </main>
    </div>
  );
}
