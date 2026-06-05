import { useEffect, useState } from "react";
import { api, type HealthResponse } from "../api/client";

export function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.health().then(setHealth).catch(() => setError("Backend unreachable"));
  }, []);

  return (
    <>
      <div className="page-header">
        <h2>Mission Control</h2>
        <p>AETHERIX Interplanetary DTN Platform v{health?.version ?? "..."}</p>
      </div>

      <div className="grid grid-4">
        <div className="stat-card">
          <div className="label">API Status</div>
          <div className={`value ${health?.status === "ok" ? "success" : "warning"}`}>
            {health?.status ?? "..."}
          </div>
          <div className="sub">{error || `Uptime: ${health?.uptime_seconds ?? 0}s`}</div>
        </div>
        <div className="stat-card">
          <div className="label">Database</div>
          <div className={`value ${health?.database === "connected" ? "success" : "danger"}`}>
            {health?.database ?? "..."}
          </div>
          <div className="sub">SQLite local / PostgreSQL docker</div>
        </div>
        <div className="stat-card">
          <div className="label">Earth-Mars Range</div>
          <div className="value info">54.6-401M km</div>
          <div className="sub">3-22 min light delay</div>
        </div>
        <div className="stat-card">
          <div className="label">Network Tiers</div>
          <div className="value accent">5</div>
          <div className="sub">241 nodes total</div>
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
              Navigate to each module using the sidebar to run calculations, simulations, and protocol demos.
            </p>
            <div className="grid grid-2">
              <div className="stat-card">
                <div className="label">Optical Link</div>
                <div className="value accent" style={{ fontSize: 20 }}>1550 nm</div>
                <div className="sub">Near-IR wavelength</div>
              </div>
              <div className="stat-card">
                <div className="label">QKD Protocol</div>
                <div className="value success" style={{ fontSize: 20 }}>BB84</div>
                <div className="sub">QBER {"<"} 11%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
