import { useState } from "react";
import { api, type RoutingDecision } from "../api/client";

const DEFAULT_STATE = {
  current_node: "earth_dsn_goldstone",
  neighbors: ["earth_dsn_madrid", "earth_orbit_geo_1", "deep_space_es_l4"],
  link_qualities: { "earth_dsn_madrid": 0.85, "earth_orbit_geo_1": 0.92, "deep_space_es_l4": 0.65 },
  buffer_occupancy: 0.4,
  bundle_priority: 2,
  bundle_size_mb: 10.5,
  bundle_deadline_hours: 48.0,
  destination_node: "mars_surface_base_olympus",
};

export function RoutingPage() {
  const [state, setState] = useState(DEFAULT_STATE);
  const [decision, setDecision] = useState<RoutingDecision | null>(null);
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);

  const decide = async () => {
    setLoading(true);
    try {
      const res = await api.routingDecide(state);
      setDecision(res);
      loadHistory();
    } catch {}
    setLoading(false);
  };

  const loadHistory = async () => {
    try {
      setHistory(await api.routingDecisions());
    } catch {}
  };

  return (
    <>
      <div className="page-header">
        <h2>RL Routing Agent</h2>
        <p>Reinforcement learning-based routing decisions for DTN bundles</p>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header"><h3>Network State</h3></div>
          <div className="form-group">
            <label>Current Node</label>
            <input value={state.current_node} onChange={(e) => setState({ ...state, current_node: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Neighbors (comma-separated)</label>
            <input value={state.neighbors.join(", ")} onChange={(e) => setState({ ...state, neighbors: e.target.value.split(",").map((s) => s.trim()) })} />
          </div>
          <div className="form-group">
            <label>Buffer Occupancy (0-1)</label>
            <input type="number" min="0" max="1" step="0.1" value={state.buffer_occupancy} onChange={(e) => setState({ ...state, buffer_occupancy: parseFloat(e.target.value) })} />
          </div>
          <div className="form-group">
            <label>Bundle Priority (0=Bulk, 4=Emergency)</label>
            <input type="number" min="0" max="4" value={state.bundle_priority} onChange={(e) => setState({ ...state, bundle_priority: parseInt(e.target.value) })} />
          </div>
          <div className="form-group">
            <label>Destination Node</label>
            <input value={state.destination_node} onChange={(e) => setState({ ...state, destination_node: e.target.value })} />
          </div>
          <button className="btn btn-primary" onClick={decide} disabled={loading}>
            {loading ? "Deciding..." : "Get Routing Decision"}
          </button>
        </div>

        {decision && (
          <div className="card">
            <div className="card-header"><h3>Routing Decision</h3></div>
            <div className="grid grid-2 gap-4">
              <div className="stat-card">
                <div className="label">Action</div>
                <div className="value accent" style={{ fontSize: 20 }}>{decision.action.toUpperCase()}</div>
              </div>
              <div className="stat-card">
                <div className="label">Next Hop</div>
                <div className="value info" style={{ fontSize: 16 }}>{decision.next_hop ?? "N/A"}</div>
              </div>
              <div className="stat-card">
                <div className="label">Confidence</div>
                <div className={`value ${decision.confidence > 0.5 ? "success" : "warning"}`} style={{ fontSize: 20 }}>
                  {(decision.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="stat-card">
                <div className="label">Reasoning</div>
                <div className="value" style={{ fontSize: 13 }}>{decision.reasoning}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h3>Decision History</h3>
          <button className="btn btn-secondary btn-sm" onClick={loadHistory}>Refresh</button>
        </div>
        {history.length > 0 ? (
          <table>
            <thead><tr><th>Node</th><th>Action</th><th>Next Hop</th><th>Confidence</th></tr></thead>
            <tbody>
              {history.slice(0, 20).map((h, i) => (
                <tr key={i}>
                  <td>{String(h.current_node)}</td>
                  <td>{String(h.action)}</td>
                  <td>{String(h.next_hop ?? "N/A")}</td>
                  <td>{String((Number(h.confidence) * 100).toFixed(1))}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>No decisions yet. Click "Get Routing Decision" above.</p>
        )}
      </div>
    </>
  );
}
