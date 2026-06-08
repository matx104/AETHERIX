import { useEffect, useState } from "react";
import { api, type SimulationRun } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { FieldInfo } from "../components/FieldInfo";
import { PresetSelect } from "../components/PresetSelect";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const SEED_PRESETS = [
  { label: "Random (no seed)", value: "" },
  { label: "42 — The answer to everything", value: "42" },
  { label: "7 — Lucky number", value: "7" },
  { label: "123 — Sequential", value: "123" },
  { label: "314 — Pi approximation", value: "314" },
  { label: "1337 — Leet", value: "1337" },
  { label: "9999 — High entropy", value: "9999" },
  { label: "1 — Minimal seed", value: "1" },
];

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
  const [error, setError] = useState("");

  const load = async () => {
    try { setRuns(await api.listSimulations()); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load simulations"); }
  };

  useEffect(() => { load(); }, []);

  const create = async () => {
    if (!name.trim()) return;
    setLoading(true);
    setError("");
    try {
      await api.createSimulation({ name, scenario, seed: seed ? parseInt(seed) : undefined });
      setName("");
      load();
    } catch (e) { setError(e instanceof Error ? e.message : "Failed to create simulation"); }
    setLoading(false);
  };

  const remove = async (id: string) => {
    if (!window.confirm("Delete this simulation run?")) return;
    try { await api.deleteSimulation(id); load(); } catch (e) { setError(e instanceof Error ? e.message : "Failed to delete simulation"); }
  };

  return (
    <>
      <div className="page-header">
        <h2>Simulations</h2>
        <p>Create and manage simulation runs with reproducible seeds</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

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
        <div className="card-header">
          <h3>New Simulation Run</h3>
          <FieldInfo>
            Create a new simulation run by specifying a name, scenario, and optional seed.
            The simulation engine will model the full 5-tier network topology (241 nodes),
            generate bundles, apply RL routing decisions, and calculate link budgets for
            each hop. Results are stored for later analysis and comparison.
          </FieldInfo>
        </div>
        <div className="grid grid-3 gap-4">
          <div className="form-group">
            <label>
              Name
              <FieldInfo>
                A <strong>human-readable identifier</strong> for this simulation run.
                Use descriptive names like "Baseline Run #1" or "Conjunction Test v2"
                to easily find and compare results later. This is stored with the run metadata.
              </FieldInfo>
            </label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Baseline Run #1" />
          </div>
          <div className="form-group">
            <label>
              Scenario
              <FieldInfo>
                The <strong>predefined network scenario</strong> to simulate:
                <ul>
                  <li><strong>Earth–Mars Baseline</strong> — Average distance (225M km), normal operations</li>
                  <li><strong>Conjunction Blackout</strong> — Solar conjunction, 2-week communication blackout</li>
                  <li><strong>Relay Chain</strong> — Multi-hop path via Lagrange point relays (ES-L4, ES-L5)</li>
                  <li><strong>Emergency Priority</strong> — Life-critical traffic with priority routing</li>
                </ul>
              </FieldInfo>
            </label>
            <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
              <option value="earth-mars-baseline">Earth–Mars Baseline</option>
              <option value="conjunction-blackout">Conjunction Blackout</option>
              <option value="relay-chain">Relay Chain</option>
              <option value="emergency-priority">Emergency Priority</option>
            </select>
          </div>
          <div className="form-group">
            <label>
              Seed (optional)
              <FieldInfo>
                A <strong>random seed</strong> for reproducibility. Using the same seed with the same
                scenario produces identical results every time — essential for scientific reproducibility.
                Leave empty for a random seed. Record the seed when publishing results so others can
                verify them.
              </FieldInfo>
            </label>
            <PresetSelect
              options={SEED_PRESETS}
              value={seed}
              onChange={setSeed}
              placeholder="Select seed..."
              customPlaceholder="Enter custom seed number"
              type="number"
            />
          </div>
        </div>
        <button className="btn btn-primary" onClick={create} disabled={loading || !name.trim()}>
          {loading ? "Creating..." : "Create Run"}
        </button>
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h3>Simulation Runs ({runs.length})</h3>
          <div className="flex items-center gap-2">
            <FieldInfo>
              All simulation runs, showing their scenario, status, seed, and creation time.
              Status values: <strong>pending</strong> (queued), <strong>running</strong> (in progress),
              <strong> completed</strong> (finished successfully). Use the same seed to reproduce
              any run's results exactly.
            </FieldInfo>
            <button className="btn btn-secondary btn-sm" onClick={load}>Refresh</button>
          </div>
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
