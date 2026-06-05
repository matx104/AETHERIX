import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard", icon: "▦" },
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
          <h1>AETHERIX</h1>
          <p>Interplanetary DTN Platform</p>
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
        </nav>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
