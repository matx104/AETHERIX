import { useState } from "react";
import { api, type QKDResult } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const RESOURCES = [
  { type: "Paper", title: "Bennett & Brassard — 'Quantum Cryptography' (1984)", url: "https://www.researchgate.net/publication/215639057", badge: "MUST READ" },
  { type: "Paper", title: "Ekert — 'Quantum Cryptography Based on Bell's Theorem' (1991)", url: "https://doi.org/10.1103/PhysRevLett.67.661", badge: "MUST READ" },
  { type: "Paper", title: "Liao et al. — 'Satellite-to-Ground QKD' — Nature (2017)", url: "https://doi.org/10.1038/nature23655", badge: "HIGH" },
  { type: "Standard", title: "NIST FIPS 203 — ML-KEM (CRYSTALS-Kyber)", url: "https://csrc.nist.gov/pubs/fips/203/final", badge: "NIST" },
  { type: "Course", title: "TU Delft — 'Quantum Internet & Quantum Computers' (edX)", url: "https://www.edx.org/course/quantum-internet-and-quantum-computers-how-will-they-change-the-world", badge: "FREE COURSE" },
  { type: "Tool", title: "IBM Quantum — Free Quantum Computer Access", url: "https://quantum.ibm.com/", badge: "HANDS-ON" },
];

export function SecurityPage() {
  const [protocol, setProtocol] = useState("bb84");
  const [numQubits, setNumQubits] = useState(1000);
  const [channelError, setChannelError] = useState(0);
  const [eavesdropper, setEavesdropper] = useState(false);
  const [result, setResult] = useState<QKDResult | null>(null);
  const [sessions, setSessions] = useState<QKDResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runQKD = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.runQKD({ protocol, num_qubits: numQubits, channel_error: channelError, eavesdropper });
      setResult(res);
      loadSessions();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Request failed");
    }
    setLoading(false);
  };

  const loadSessions = async () => {
    try { setSessions(await api.qkdSessions()); } catch {}
  };

  return (
    <>
      <div className="page-header">
        <h2>QKD Security</h2>
        <p>Quantum Key Distribution — BB84 and E91 protocol simulation</p>
      </div>

      <InfoBubble title="Why Quantum Key Distribution for Interplanetary Security?" learnMoreUrl={`${SHOWCASE_URL}/#qkd-science`}>
        <p>
          Current encryption (like AES-256) relies on the difficulty of mathematical
          problems. But quantum computers will eventually break these. For a Mars
          mission planned decades in advance, we need security that holds up{" "}
          <strong>not just today, but in 20–30 years</strong>. An adversary could{" "}
          <em>record encrypted Mars communications today</em> and decrypt them later —
          a "harvest now, decrypt later" attack.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Quantum Key Distribution (QKD)</strong> solves this. It is secured
          by the <strong>fundamental laws of physics</strong>, not computational
          difficulty. Even a future quantum computer cannot break it. The security
          rests on three quantum principles:
        </p>
        <ul style={{ marginTop: 6, marginLeft: 20 }}>
          <li><strong>No-Cloning Theorem:</strong> It is physically impossible to make an identical copy of an unknown quantum state.</li>
          <li><strong>Measurement Disturbance:</strong> Measuring a quantum system changes it irreversibly — any eavesdropper is revealed.</li>
          <li><strong>Superposition:</strong> A qubit does not have a definite value until measured — like a coin spinning in the air.</li>
        </ul>
        <p style={{ marginTop: 8 }}>
          <strong>BB84 Protocol:</strong> Alice sends photons in random orientations.
          Bob measures them. They compare which orientations they used (not the bits).
          Where they agree, they keep those bits as a shared key. If the error rate
          (QBER) exceeds <strong>11%</strong>, an eavesdropper was detected.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Why 11%?</strong> Below this threshold, privacy amplification can
          extract a perfectly secure key (Csiszár–Körner theorem, 1978). Above it,
          too much information has leaked to the eavesdropper.
        </p>
      </InfoBubble>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header"><h3>Protocol Parameters</h3></div>
          <div className="form-group">
            <label>Protocol</label>
            <select value={protocol} onChange={(e) => setProtocol(e.target.value)}>
              <option value="bb84">BB84 (Bennett-Brassard 1984)</option>
              <option value="e91">E91 (Ekert 1991)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Number of Qubits</label>
            <input type="number" value={numQubits} onChange={(e) => setNumQubits(parseInt(e.target.value) || 100)} />
          </div>
          <div className="form-group">
            <label>Channel Error Rate</label>
            <input type="number" min="0" max="1" step="0.01" value={channelError} onChange={(e) => setChannelError(parseFloat(e.target.value))} />
          </div>
          <div className="form-group">
            <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
              <input type="checkbox" checked={eavesdropper} onChange={(e) => setEavesdropper(e.target.checked)} />
              Simulate Eavesdropper (Eve)
            </label>
          </div>
          <button className="btn btn-primary" onClick={runQKD} disabled={loading}>
            {loading ? "Running..." : `Run ${protocol.toUpperCase()} Protocol`}
          </button>
        </div>

        {result && (
          <div className="card">
            <div className="card-header"><h3>QKD Result</h3></div>
            <div className="grid grid-2 gap-4">
              <div className="stat-card">
                <div className="label">QBER</div>
                <div className={`value ${result.qber !== null && result.qber < 0.11 ? "success" : "danger"}`} style={{ fontSize: 22 }}>
                  {result.qber !== null ? `${(result.qber * 100).toFixed(2)}%` : "N/A"}
                </div>
                <div className="sub">Threshold: 11%</div>
              </div>
              <div className="stat-card">
                <div className="label">Secure</div>
                <div className={`value ${result.secure ? "success" : "danger"}`} style={{ fontSize: 22 }}>
                  {result.secure ? "YES" : "NO"}
                </div>
              </div>
              <div className="stat-card">
                <div className="label">Sifted Key Length</div>
                <div className="value accent" style={{ fontSize: 22 }}>{result.sifted_key_length ?? "N/A"}</div>
              </div>
              <div className="stat-card">
                <div className="label">Efficiency</div>
                <div className="value info" style={{ fontSize: 22 }}>
                  {result.efficiency !== null ? `${(result.efficiency * 100).toFixed(1)}%` : "N/A"}
                </div>
              </div>
            </div>
            {result.alice_key && (
              <div style={{ marginTop: 16 }}>
                <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>Alice's Key (first 32 bits)</p>
                <code style={{ fontSize: 13, color: "var(--accent)" }}>[{result.alice_key.join(", ")}]</code>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h3>Session History</h3>
          <button className="btn btn-secondary btn-sm" onClick={loadSessions}>Refresh</button>
        </div>
        {sessions.length > 0 ? (
          <table>
            <thead><tr><th>Protocol</th><th>Qubits</th><th>QBER</th><th>Secure</th><th>Key Length</th></tr></thead>
            <tbody>
              {sessions.slice(0, 20).map((s) => (
                <tr key={s.id}>
                  <td>{s.protocol.toUpperCase()}</td>
                  <td>{s.num_qubits}</td>
                  <td>{s.qber !== null ? `${(s.qber * 100).toFixed(2)}%` : "–"}</td>
                  <td>{s.secure ? <span className="badge badge-success">Yes</span> : <span className="badge badge-danger">No</span>}</td>
                  <td>{s.sifted_key_length ?? "–"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>No sessions yet. Run a protocol above.</p>
        )}
      </div>

      <div style={{ marginTop: 16 }}>
        <ResourcesCard title="Quantum &amp; QKD Resources" links={RESOURCES} />
      </div>
    </>
  );
}
