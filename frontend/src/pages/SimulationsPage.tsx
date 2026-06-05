import { useEffect, useState } from "react";
import { api, type SimulationRun } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const RESOURCES = [
  { type: "Paper", title: "Fall — 'A Delay-Tolerant Network Architecture' (2003)", url: "https://dl.acm.org/doi/10.1145/863955.863960", badge: "FOUNDATIONAL" },
  { type: "Paper", title: "Burleigh et al. — 'DTN: An Approach to Interplanetary Internet' (2003)", url: "https://doi.org/10.1109/MCOM.2003.1204759", badge: "FOUNDATIONAL" },
  { type: "RFC", title: "RFC 9171 — Bundle Protocol Version 7", url: "https://www.rfc-editor.org/rfc/rfc9171", badge: "MUST READ" },
  { type: "Standard", title: "CCSDS 734.2-B-1 — DTN Architecture (Blue Book)", url: "https://public.ccsds.org/Pubs/734x2b1.pdf", badge: "CCSDS" },
];

export function SimulationsPage() {
  const [runs, setRuns] = useState<SimulationRun[]>([]);
  const [name, setName] = useState("");
  const [scenario, setScenario] = useState("earth-mars-baseline");
  const [seed, setSeed] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    try { setRuns(await api.listSimulations()); } catch {}
  };

  useEffect(() => { load(); }, []);

  const create = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      await api.createSimulation({ name, scenario, seed: seed ? parseInt(seed) : undefined });
      setName("");
      load();
    } catch {}
    setLoading(false);
  };

  const remove = async (id: string) => {
    try { await api.deleteSimulation(id); load(); } catch {}
  };

  return (
    <>
      <div className="page-header">
        <h2>Simulations</h2>
        <p>Create and manage simulation runs with reproducible seeds</p>
      </div>

      <InfoBubble title="Simulation Engine" learnMoreUrl={`${SHOWCASE_URL}/#simulation`}>
        <p>
          AETHERIX integrates a full simulation engine that models the{" "}
          <strong>5-tier network topology (241 nodes)</strong>, bundle generation,
          store-and-forward forwarding, RL routing decisions, and link budget
          calculations — all driven by reproducible configuration and seeds.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Reproducibility:</strong> Every simulation run records its seed and
          config so results can be independently verified. Scientific claims must cite
          the sample/run, the seed, and the simulation config — no mocked physics, no
          fabricated latency numbers.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Scenarios:</strong> Baseline (Earth–Mars average conditions),
          Conjunction Blackout (2-week communication blackout), Relay Chain
          (multi-hop via Lagrange relays), and Emergency Priority (life-critical
          traffic routing).
        </p>
      </InfoBubble>

      <div className="card">
        <div className="card-header"><h3>New Simulation Run</h3></div>
        <div className="grid grid-3 gap-4">
          <div className="form-group">
            <label>Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Baseline Run #1" />
          </div>
          <div className="form-group">
            <label>Scenario</label>
            <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
              <option value="earth-mars-baseline">Earth–Mars Baseline</option>
              <option value="conjunction-blackout">Conjunction Blackout</option>
              <option value="relay-chain">Relay Chain</option>
              <option value="emergency-priority">Emergency Priority</option>
            </select>
          </div>
          <div className="form-group">
            <label>Seed (optional)</label>
            <input value={seed} onChange={(e) => setSeed(e.target.value)} placeholder="e.g. 42" />
          </div>
        </div>
        <button className="btn btn-primary" onClick={create} disabled={loading || !name.trim()}>
          {loading ? "Creating..." : "Create Run"}
        </button>
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h3>Simulation Runs ({runs.length})</h3>
          <button className="btn btn-secondary btn-sm" onClick={load}>Refresh</button>
        </div>
        {runs.length > 0 ? (
          <table>
            <thead><tr><th>Name</th><th>Scenario</th><th>Status</th><th>Seed</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.id}>
                  <td>{r.name}</td>
                  <td>{r.scenario}</td>
                  <td>
                    <span className={`badge ${r.status === "completed" ? "badge-success" : r.status === "pending" ? "badge-warning" : "badge-info"}`}>
                      {r.status}
                    </span>
                  </td>
                  <td>{r.seed ?? "–"}</td>
                  <td>{new Date(r.created_at).toLocaleString()}</td>
                  <td><button className="btn btn-danger btn-sm" onClick={() => remove(r.id)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>No simulation runs yet. Create one above.</p>
        )}
      </div>

      <div style={{ marginTop: 16 }}>
        <ResourcesCard title="DTN &amp; Simulation Resources" links={RESOURCES} />
      </div>
    </>
  );
}
