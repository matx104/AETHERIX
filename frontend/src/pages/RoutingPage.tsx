import { useState } from "react";
import { api, type RoutingDecision } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { FieldInfo } from "../components/FieldInfo";
import { PresetSelect } from "../components/PresetSelect";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const NODE_PRESETS = [
  { label: "Tier 1 — DSN Goldstone (Earth)", value: "earth_dsn_goldstone" },
  { label: "Tier 1 — DSN Madrid (Earth)", value: "earth_dsn_madrid" },
  { label: "Tier 1 — DSN Canberra (Earth)", value: "earth_dsn_canberra" },
  { label: "Tier 2 — GEO Relay Atlantic", value: "earth_orbit_geo_atlantic" },
  { label: "Tier 2 — GEO Relay Pacific", value: "earth_orbit_geo_pacific" },
  { label: "Tier 2 — LEO Satellite #01", value: "earth_orbit_leo_01" },
  { label: "Tier 3 — Lagrange ES-L4", value: "deep_space_es_l4" },
  { label: "Tier 3 — Lagrange ES-L5", value: "deep_space_es_l5" },
  { label: "Tier 4 — Areostationary Alpha", value: "mars_orbit_areo_alpha" },
  { label: "Tier 4 — Mars Orbiter", value: "mars_orbit_mars_orbiter" },
  { label: "Tier 5 — Base Jezero (Mars)", value: "mars_surface_base_jezero" },
  { label: "Tier 5 — Base Olympus (Mars)", value: "mars_surface_base_olympus" },
  { label: "Tier 5 — Rover #01 (Mars)", value: "mars_surface_rover_01" },
];

const DEST_PRESETS = [
  { label: "Mars — Base Olympus (Tier 5)", value: "mars_surface_base_olympus" },
  { label: "Mars — Base Jezero (Tier 5)", value: "mars_surface_base_jezero" },
  { label: "Mars — Rover #01 (Tier 5)", value: "mars_surface_rover_01" },
  { label: "Mars Orbit — Areo Alpha (Tier 4)", value: "mars_orbit_areo_alpha" },
  { label: "Mars Orbit — Mars Orbiter (Tier 4)", value: "mars_orbit_mars_orbiter" },
  { label: "Deep Space — ES-L4 (Tier 3)", value: "deep_space_es_l4" },
  { label: "Earth — DSN Goldstone (Tier 1)", value: "earth_dsn_goldstone" },
  { label: "Earth — DSN Madrid (Tier 1)", value: "earth_dsn_madrid" },
  { label: "Earth — DSN Canberra (Tier 1)", value: "earth_dsn_canberra" },
  { label: "Earth — GEO Atlantic (Tier 2)", value: "earth_orbit_geo_atlantic" },
];

const NEIGHBOR_PRESETS = [
  { label: "Standard Earth Hub", value: "earth_dsn_madrid, earth_orbit_geo_1, deep_space_es_l4" },
  { label: "Full DSN + GEO", value: "earth_dsn_madrid, earth_dsn_canberra, earth_orbit_geo_atlantic, earth_orbit_geo_pacific" },
  { label: "Deep Space Relay Chain", value: "deep_space_es_l4, deep_space_es_l5, mars_orbit_areo_alpha" },
  { label: "Mars Orbit Hub", value: "mars_orbit_areo_alpha, mars_orbit_mars_orbiter, mars_surface_base_olympus" },
  { label: "Mars Surface Links", value: "mars_orbit_areo_alpha, mars_surface_rover_01, mars_surface_drone_01" },
  { label: "LEO Constellation (3 sats)", value: "earth_orbit_leo_01, earth_orbit_leo_02, earth_orbit_leo_03" },
  { label: "Minimal — Single Relay", value: "earth_orbit_geo_1" },
  { label: "High Redundancy (6 links)", value: "earth_dsn_madrid, earth_dsn_canberra, earth_orbit_geo_atlantic, earth_orbit_geo_pacific, earth_orbit_leo_01, deep_space_es_l4" },
];

const BUFFER_PRESETS = [
  { label: "Empty (0%) — Fresh node", value: "0" },
  { label: "Low (20%) — Lightly loaded", value: "0.2" },
  { label: "Normal (40%) — Typical load", value: "0.4" },
  { label: "Moderate (60%) — Busy", value: "0.6" },
  { label: "High (80%) — Congested", value: "0.8" },
  { label: "Full (95%) — Nearly at capacity", value: "0.95" },
  { label: "Critical (100%) — No space", value: "1" },
];

const PRIORITY_PRESETS = [
  { label: "0 — Bulk (science data, file transfers)", value: "0" },
  { label: "1 — Normal (routine telemetry)", value: "1" },
  { label: "2 — Expedited (commands, status)", value: "2" },
  { label: "3 — Priority (time-critical data)", value: "3" },
  { label: "4 — Emergency (life-critical, abort signals)", value: "4" },
];

const DEFAULT_STATE = {
  current_node: "earth_dsn_goldstone",
  neighbors: ["earth_dsn_madrid", "earth_orbit_geo_1", "deep_space_es_l4"],
  link_qualities: { earth_dsn_madrid: 0.85, earth_orbit_geo_1: 0.92, deep_space_es_l4: 0.65 },
  buffer_occupancy: 0.4,
  bundle_priority: 2,
  bundle_size_mb: 10.5,
  bundle_deadline_hours: 48.0,
  destination_node: "mars_surface_base_olympus",
};

const RESOURCES = [
  { type: "Book", title: "Sutton & Barto — 'Reinforcement Learning: An Introduction' (FREE)", url: "http://incompleteideas.net/book/the-book.html", badge: "FREE BOOK" },
  { type: "Course", title: "David Silver (UCL) — RL Course (10 Lectures, Free)", url: "https://www.davidsilver.uk/teaching/", badge: "FREE COURSE" },
  { type: "Course", title: "UC Berkeley CS 285 — Deep RL (Free Lectures)", url: "https://rail.eecs.berkeley.edu/deeprlcourse/", badge: "FREE COURSE" },
  { type: "Paper", title: "Mnih et al. — 'Human-Level Control Through Deep RL' (2015)", url: "https://doi.org/10.1038/nature14236", badge: "DQN" },
  { type: "Tool", title: "OpenAI Spinning Up — Educational RL Implementations", url: "https://spinningup.openai.com/", badge: "HANDS-ON" },
  { type: "Video", title: "ML with Phil — 'Q-Learning Explained'", url: "https://www.youtube.com/watch?v=qhRNvCVVJaA", badge: "YOUTUBE" },
];

export function RoutingPage() {
  const [state, setState] = useState(DEFAULT_STATE);
  const [decision, setDecision] = useState<RoutingDecision | null>(null);
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const decide = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.routingDecide(state);
      setDecision(res);
      loadHistory();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Request failed");
    }
    setLoading(false);
  };

  const loadHistory = async () => {
    try { setHistory(await api.routingDecisions()); } catch {}
  };

  return (
    <>
      <div className="page-header">
        <h2>RL Routing Agent</h2>
        <p>Reinforcement learning-based routing decisions for DTN bundles</p>
      </div>

      <InfoBubble title="Why Reinforcement Learning for Space Routing?" learnMoreUrl={`${SHOWCASE_URL}/#reinforcement-learning`}>
        <p>
          Traditional space networks use <strong>Contact Graph Routing (CGR)</strong> —
          fixed routing tables that must be manually updated from Earth. But space
          is unpredictable: solar storms disrupt links, satellites drift, and
          equipment fails. CGR requires updates sent from Earth, which take{" "}
          <strong>20+ minutes</strong> to arrive — by which time conditions may
          have already changed.
        </p>
        <p style={{ marginTop: 8 }}>
          AETHERIX uses a <strong>reinforcement learning agent</strong> that adapts
          in real-time. It learns from experience which paths work best: trying
          different routing decisions and getting <em>rewards</em> for good outcomes
          (fast delivery) and <em>penalties</em> for bad ones (delays, drops). Over
          thousands of episodes, it discovers strategies that outperform static
          routing tables.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>The analogy:</strong> Imagine navigating a new city without a map.
          At first you try random streets — some lead to dead ends, others get you
          closer. Over time, you learn which routes work. The agent is the navigator,
          the actions are street choices, and the learned "map" is the{" "}
          <strong>Q-table</strong>.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Reward function:</strong> R = α(delivery) − β(delay) − γ(hops) −
          δ(drops) − ε(energy). Mission operators can tune these weights to prioritize
          speed for emergency traffic or energy efficiency for bulk science data.
        </p>
      </InfoBubble>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3>Network State</h3>
            <FieldInfo>
              Define the current network state for the RL routing agent. The agent observes
              this state and selects the best routing action based on its learned <strong>Q-table</strong>.
              The state includes the current node position, available neighbors, buffer capacity,
              and bundle metadata. Use the dropdowns to select from realistic network configurations
              across all 5 tiers, or choose "Custom" to enter any value.
            </FieldInfo>
          </div>
          <div className="form-group">
            <label>
              Current Node
              <FieldInfo>
                The <strong>DTN node</strong> currently holding the bundle. This is the node making
                the routing decision. Node IDs follow the pattern: <code>tier_location_name</code>.
                The 5-tier topology spans 241 nodes from Earth ground stations (Tier 1) to Mars
                surface assets (Tier 5). Select a node from any tier to test different routing scenarios.
              </FieldInfo>
            </label>
            <PresetSelect
              options={NODE_PRESETS}
              value={state.current_node}
              onChange={(v) => setState({ ...state, current_node: v })}
              placeholder="Select a node..."
              customPlaceholder="e.g. earth_dsn_goldstone"
            />
          </div>
          <div className="form-group">
            <label>
              Neighbors (comma-separated)
              <FieldInfo>
                <strong>Directly connected nodes</strong> that this node can forward bundles to.
                These are the available next-hop candidates. The agent will choose one of these
                (or decide to store/drop). Link quality to each neighbor is tracked internally.
                Presets model realistic connectivity patterns for different network positions.
              </FieldInfo>
            </label>
            <PresetSelect
              options={NEIGHBOR_PRESETS}
              value={state.neighbors.join(", ")}
              onChange={(v) => setState({ ...state, neighbors: v.split(",").map((s) => s.trim()).filter(Boolean) })}
              placeholder="Select a neighbor set..."
              customPlaceholder="e.g. earth_dsn_madrid, earth_orbit_geo_1"
            />
          </div>
          <div className="form-group">
            <label>
              Buffer Occupancy (0–1)
              <FieldInfo>
                How <strong>full</strong> the node's storage buffer is, from <code>0</code> (empty)
                to <code>1</code> (completely full). High buffer occupancy means the node is congested
                and may need to drop or reroute bundles. The RL agent considers this when deciding
                whether to store a bundle locally or forward it immediately.
              </FieldInfo>
            </label>
            <PresetSelect
              options={BUFFER_PRESETS}
              value={String(state.buffer_occupancy)}
              onChange={(v) => setState({ ...state, buffer_occupancy: parseFloat(v) || 0 })}
              placeholder="Select buffer level..."
              customPlaceholder="Enter value 0.0 to 1.0"
              type="number"
            />
          </div>
          <div className="form-group">
            <label>
              Bundle Priority
              <FieldInfo>
                The <strong>BPv7 priority class</strong> of the bundle being routed.
                Higher priority bundles get preferential routing and buffer space.
                Emergency bundles bypass normal queuing and take the fastest available path.
              </FieldInfo>
            </label>
            <PresetSelect
              options={PRIORITY_PRESETS}
              value={String(state.bundle_priority)}
              onChange={(v) => setState({ ...state, bundle_priority: parseInt(v) || 0 })}
              placeholder="Select priority..."
              customPlaceholder="Enter 0–4"
              type="number"
            />
          </div>
          <div className="form-group">
            <label>
              Destination Node
              <FieldInfo>
                The <strong>final destination</strong> for this bundle. The routing agent plans
                a multi-hop path from the current node to this destination, selecting the best
                next hop at each step. Select any node across all 5 tiers.
              </FieldInfo>
            </label>
            <PresetSelect
              options={DEST_PRESETS}
              value={state.destination_node}
              onChange={(v) => setState({ ...state, destination_node: v })}
              placeholder="Select destination..."
              customPlaceholder="e.g. mars_surface_base_olympus"
            />
          </div>
          <button className="btn btn-primary" onClick={decide} disabled={loading}>
            {loading ? "Deciding..." : "Get Routing Decision"}
          </button>
        </div>

        {decision && (
          <div className="card">
            <div className="card-header">
              <h3>Routing Decision</h3>
              <FieldInfo>
                The RL agent's routing decision based on the provided network state. The agent
                evaluates all possible actions using its learned Q-values and selects the action
                with the highest expected reward. Confidence reflects how certain the agent is
                about this decision.
              </FieldInfo>
            </div>
            <div className="grid grid-2 gap-4">
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Action</div>
                  <FieldInfo>
                    The routing action chosen by the agent:
                    <ul>
                      <li><strong>FORWARD</strong> — send bundle to the selected next hop</li>
                      <li><strong>STORE</strong> — hold bundle locally until a better path opens</li>
                      <li><strong>DROP</strong> — discard bundle (buffer full, TTL expired)</li>
                    </ul>
                    The agent learns when each action is optimal through reward signals.
                  </FieldInfo>
                </div>
                <div className="value accent" style={{ fontSize: 20 }}>{decision.action.toUpperCase()}</div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Next Hop</div>
                  <FieldInfo>
                    The <strong>neighbor node</strong> selected as the next hop for this bundle.
                    The agent considers link quality, buffer occupancy at the neighbor, and
                    remaining distance to the destination. "N/A" means the action is STORE or DROP
                    (no forwarding needed).
                  </FieldInfo>
                </div>
                <div className="value info" style={{ fontSize: 16 }}>{decision.next_hop ?? "N/A"}</div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Confidence</div>
                  <FieldInfo>
                    How <strong>certain</strong> the agent is about its decision, from 0% to 100%.
                    Low confidence means the agent hasn't learned much about this particular state.
                    High confidence means the Q-values strongly favor this action. Confidence &gt; 50%
                    (green) indicates a well-learned decision.
                  </FieldInfo>
                </div>
                <div className={`value ${decision.confidence > 0.5 ? "success" : "warning"}`} style={{ fontSize: 20 }}>
                  {(decision.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Reasoning</div>
                  <FieldInfo>
                    A <strong>human-readable explanation</strong> of why the agent chose this action.
                    This includes the key factors considered (link quality, buffer state, distance
                    to destination, bundle priority) and the trade-offs weighed.
                  </FieldInfo>
                </div>
                <div className="value" style={{ fontSize: 13 }}>{decision.reasoning}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h3>Decision History</h3>
          <div className="flex items-center gap-2">
            <FieldInfo>
              A log of all routing decisions made by the RL agent. Each entry records the network
              state, chosen action, selected next hop, and confidence level. Use this to analyze
              routing patterns and identify edge cases where the agent's confidence is low.
            </FieldInfo>
            <button className="btn btn-secondary btn-sm" onClick={loadHistory}>Refresh</button>
          </div>
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
                  <td>{(Number(h.confidence) * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>No decisions yet. Click "Get Routing Decision" above.</p>
        )}
      </div>

      <div style={{ marginTop: 16 }}>
        <ResourcesCard title="RL &amp; Routing Resources" links={RESOURCES} />
      </div>
    </>
  );
}
