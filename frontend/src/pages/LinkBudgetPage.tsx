import { useState } from "react";
import { api, type LinkBudgetResult } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const SCENARIOS = ["minimum", "average", "maximum"];

const RESOURCES = [
  { type: "Standard", title: "CCSDS 141.0-B-1 — Optical Communications Physical Layer", url: "https://public.ccsds.org/Pubs/141x0b1.pdf", badge: "CCSDS" },
  { type: "Paper", title: "Boroson et al. — 'LLCD Overview and Results' (2014)", url: "https://doi.org/10.1117/12.2045508", badge: "HIGH" },
  { type: "Paper", title: "Biswas et al. — 'DSOC' (2018)", url: "https://doi.org/10.1117/12.2296426", badge: "HIGH" },
  { type: "Doc", title: "NASA DSN Telecommunications Link Design Handbook (810-005)", url: "https://deepspace.jpl.nasa.gov/dsndocs/810-005/", badge: "DSN BIBLE" },
  { type: "Video", title: "NASA — Deep Space Optical Communications (DSOC)", url: "https://www.youtube.com/results?search_query=deep+space+optical+communications+NASA", badge: "YOUTUBE" },
];

export function LinkBudgetPage() {
  const [scenario, setScenario] = useState("average");
  const [distance, setDistance] = useState("");
  const [result, setResult] = useState<LinkBudgetResult | null>(null);
  const [history, setHistory] = useState<LinkBudgetResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runOptical = async () => {
    setLoading(true);
    setError("");
    try {
      const data: Record<string, unknown> = { scenario };
      if (distance) data.distance_km = parseFloat(distance);
      const res = await api.opticalLinkBudget(data as { scenario: string; distance_km?: number });
      setResult(res);
      loadHistory();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try { setHistory(await api.linkBudgetHistory()); } catch {}
  };

  return (
    <>
      <div className="page-header">
        <h2>Link Budget Calculator</h2>
        <p>Optical and RF link budget analysis for Earth–Mars communications</p>
      </div>

      <InfoBubble title="What is a Link Budget?" learnMoreUrl={`${SHOWCASE_URL}/#optical-comms`}>
        <p>
          A link budget determines whether a communication link can successfully
          deliver data. It accounts for <strong>every source of signal loss</strong>{" "}
          (distance, atmosphere, pointing errors) and{" "}
          <strong>gain</strong> (telescope size, laser power) to calculate the{" "}
          <strong>link margin</strong> — the safety buffer between what you have
          and what you need. A <em>positive</em> margin means the link works.
        </p>
        <p style={{ marginTop: 8 }}>
          Instead of radio waves, AETHERIX uses <strong>infrared lasers at 1550 nm</strong>{" "}
          — the same wavelength used in fiber optic networks on Earth. Where Mars
          Reconnaissance Orbiter sends 0.5–6 Mbps via radio, AETHERIX achieves{" "}
          <strong>2–200 Mbps</strong> via laser — enough for high-definition video
          from Mars.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>The challenge:</strong> pointing a laser at a receiver 400 million
          km away, with beam divergence of only ~5 microradians — equivalent to
          hitting a coin from 4 km away. Signal strength drops with the{" "}
          <em>square of the distance</em> (doubling = 4× less signal).
        </p>
      </InfoBubble>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header"><h3>Optical Link Parameters</h3></div>
          <div className="form-group">
            <label>Scenario</label>
            <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
              {SCENARIOS.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Distance (km) — leave empty for scenario default</label>
            <input value={distance} onChange={(e) => setDistance(e.target.value)} placeholder="e.g. 225000000" />
          </div>
          <button className="btn btn-primary" onClick={runOptical} disabled={loading}>
            {loading ? "Calculating..." : "Calculate Optical Link"}
          </button>
        </div>

        {result && (
          <div className="card">
            <div className="card-header"><h3>Results</h3></div>
            <div className="grid grid-2 gap-4">
              <div className="stat-card">
                <div className="label">Distance</div>
                <div className="value info" style={{ fontSize: 20 }}>
                  {(result.distance_km / 1e6).toFixed(1)}M km
                </div>
              </div>
              <div className="stat-card">
                <div className="label">Link Margin</div>
                <div className={`value ${result.link_margin_db > 0 ? "success" : "danger"}`} style={{ fontSize: 20 }}>
                  {result.link_margin_db.toFixed(2)} dB
                </div>
              </div>
              <div className="stat-card">
                <div className="label">EIRP</div>
                <div className="value accent" style={{ fontSize: 20 }}>{result.eirp_dbm.toFixed(2)} dBm</div>
              </div>
              <div className="stat-card">
                <div className="label">Data Rate</div>
                <div className="value warning" style={{ fontSize: 20 }}>{result.data_rate_mbps.toFixed(1)} Mbps</div>
              </div>
              <div className="stat-card">
                <div className="label">Free Space Loss</div>
                <div className="value danger" style={{ fontSize: 20 }}>{result.free_space_loss_db.toFixed(2)} dB</div>
              </div>
              <div className="stat-card">
                <div className="label">Received Power</div>
                <div className="value" style={{ fontSize: 20 }}>{result.received_power_dbm.toFixed(2)} dBm</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h3>History</h3>
          <button className="btn btn-secondary btn-sm" onClick={loadHistory}>Refresh</button>
        </div>
        {history.length > 0 ? (
          <table>
            <thead><tr><th>Type</th><th>Scenario</th><th>Distance</th><th>Margin</th><th>Data Rate</th></tr></thead>
            <tbody>
              {history.slice(0, 20).map((h) => (
                <tr key={h.id}>
                  <td>{h.link_type}</td>
                  <td>{h.scenario}</td>
                  <td>{(h.distance_km / 1e6).toFixed(1)}M km</td>
                  <td className={h.link_margin_db > 0 ? "success" : "danger"}>{h.link_margin_db.toFixed(2)} dB</td>
                  <td>{h.data_rate_mbps.toFixed(1)} Mbps</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>No history yet. Run a calculation above.</p>
        )}
      </div>

      <div style={{ marginTop: 16 }}>
        <ResourcesCard title="Optical Communications Resources" links={RESOURCES} />
      </div>
    </>
  );
}
