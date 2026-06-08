import { useState } from "react";
import { api, type LinkBudgetResult } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { FieldInfo } from "../components/FieldInfo";
import { PresetSelect } from "../components/PresetSelect";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const SCENARIOS = ["minimum", "average", "maximum"];

const DISTANCE_PRESETS = [
  { label: "Scenario default (leave empty)", value: "" },
  { label: "54,600,000 km — Perihelion opposition (closest)", value: "54600000" },
  { label: "100,000,000 km — Close approach", value: "100000000" },
  { label: "150,000,000 km — 1 AU (~Earth–Sun distance)", value: "150000000" },
  { label: "225,000,000 km — Average distance", value: "225000000" },
  { label: "300,000,000 km — Distant transit", value: "300000000" },
  { label: "350,000,000 km — Near conjunction", value: "350000000" },
  { label: "401,000,000 km — Aphelion conjunction (farthest)", value: "401000000" },
];

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
    try { setHistory(await api.linkBudgetHistory()); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load history"); }
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
          <div className="card-header">
            <h3>Optical Link Parameters</h3>
            <FieldInfo>
              Configure the parameters for the optical link budget calculation.
              The calculator uses the <strong>1550 nm infrared laser</strong> wavelength
              and models free-space path loss, transmitter/receiver gain, pointing losses,
              and atmospheric attenuation to determine whether the link can close.
            </FieldInfo>
          </div>
          <div className="form-group">
            <label>
              Scenario
              <FieldInfo>
                Select a <strong>predefined Earth–Mars distance</strong>:
                <ul>
                  <li><strong>minimum</strong> — 54.6M km (perihelion opposition, closest approach)</li>
                  <li><strong>average</strong> — 225M km (typical distance during transit window)</li>
                  <li><strong>maximum</strong> — 401M km (aphelion conjunction, farthest apart)</li>
                </ul>
                Shorter distances yield higher data rates and better link margins.
              </FieldInfo>
            </label>
            <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
              {SCENARIOS.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>
              Distance (km) — leave empty for scenario default
              <FieldInfo>
                Override the scenario distance with a <strong>custom value in kilometers</strong>.
                For reference: Earth–Mars ranges from <code>54,600,000</code> km (perihelion)
                to <code>401,000,000</code> km (aphelion). Leave this field empty to use the
                scenario default. Signal strength scales with the <strong>inverse square of distance</strong> —
                doubling the distance means 4× less received power (6 dB loss).
              </FieldInfo>
            </label>
            <PresetSelect
              options={DISTANCE_PRESETS}
              value={distance}
              onChange={setDistance}
              placeholder="Select distance..."
              customPlaceholder="Enter custom distance in km"
              type="number"
            />
          </div>
          <button className="btn btn-primary" onClick={runOptical} disabled={loading}>
            {loading ? "Calculating..." : "Calculate Optical Link"}
          </button>
        </div>

        {result && (
          <div className="card">
            <div className="card-header">
              <h3>Results</h3>
              <FieldInfo>
                The link budget results show whether the optical communication link
                can successfully close at the given distance. The most important metric
                is the <strong>link margin</strong> — if positive (green), the link works;
                if negative (red), the received signal is too weak.
              </FieldInfo>
            </div>
            <div className="grid grid-2 gap-4">
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Distance</div>
                  <FieldInfo>
                    The <strong>slant range</strong> between transmitter and receiver in millions of km.
                    This determines the free-space path loss — the dominant loss factor in deep-space
                    communication. At 225M km, the path loss is ~294 dB.
                  </FieldInfo>
                </div>
                <div className="value info" style={{ fontSize: 20 }}>
                  {(result.distance_km / 1e6).toFixed(1)}M km
                </div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Link Margin</div>
                  <FieldInfo>
                    The <strong>safety buffer</strong> between received power and receiver sensitivity,
                    measured in decibels (dB). <strong>Positive</strong> (green) = link works with margin
                    to spare. <strong>Negative</strong> (red) = link cannot close. Each 3 dB = doubling of
                    signal power. A margin of 6 dB means you have 4× the minimum needed signal.
                  </FieldInfo>
                </div>
                <div className={`value ${result.link_margin_db > 0 ? "success" : "danger"}`} style={{ fontSize: 20 }}>
                  {result.link_margin_db.toFixed(2)} dB
                </div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">EIRP</div>
                  <FieldInfo>
                    <strong>Effective Isotropic Radiated Power</strong> — the total power the
                    transmitter appears to radiate if it were an isotropic (omnidirectional) antenna.
                    Measured in dBm. Combines laser power + transmitter telescope gain. AETHERIX uses
                    a 10W laser with a 30cm telescope aperture, producing ~60-70 dBm EIRP.
                  </FieldInfo>
                </div>
                <div className="value accent" style={{ fontSize: 20 }}>{result.eirp_dbm.toFixed(2)} dBm</div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Data Rate</div>
                  <FieldInfo>
                    The achievable <strong>data throughput</strong> in Mbps. This varies dramatically
                    with distance: ~200 Mbps at perihelion (54.6M km), down to ~2 Mbps at aphelion
                    (401M km). Compare this to the Mars Reconnaissance Orbiter's 0.5–6 Mbps radio link.
                  </FieldInfo>
                </div>
                <div className="value warning" style={{ fontSize: 20 }}>{result.data_rate_mbps.toFixed(1)} Mbps</div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Free Space Loss</div>
                  <FieldInfo>
                    The <strong>signal attenuation</strong> caused purely by distance, following the
                    inverse-square law. This is by far the largest loss factor. At 225M km, the path
                    loss is ~294 dB — meaning only ~10⁻³⁰ of transmitted power reaches the receiver.
                    This is why we need powerful lasers and large telescopes.
                  </FieldInfo>
                </div>
                <div className="value danger" style={{ fontSize: 20 }}>{result.free_space_loss_db.toFixed(2)} dB</div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Received Power</div>
                  <FieldInfo>
                    The <strong>actual signal power</strong> arriving at the receiver aperture, measured
                    in dBm. After accounting for all losses (free-space, pointing, atmospheric) and gains
                    (receiver telescope). The receiver has a minimum sensitivity threshold — received
                    power must exceed it for the link to work.
                  </FieldInfo>
                </div>
                <div className="value" style={{ fontSize: 20 }}>{result.received_power_dbm.toFixed(2)} dBm</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h3>History</h3>
          <div className="flex items-center gap-2">
            <FieldInfo>
              A log of all link budget calculations run in this session. Each row records
              the parameters used and the resulting link margin. Useful for comparing different
              scenarios and distances to understand how link performance varies across the synodic period.
            </FieldInfo>
            <button className="btn btn-secondary btn-sm" onClick={loadHistory}>Refresh</button>
          </div>
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
