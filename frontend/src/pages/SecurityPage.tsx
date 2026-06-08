import { useState } from "react";
import { api, type QKDResult } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { FieldInfo } from "../components/FieldInfo";
import { PresetSelect } from "../components/PresetSelect";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const QUBIT_PRESETS = [
  { label: "100 — Quick test", value: "100" },
  { label: "500 — Short run", value: "500" },
  { label: "1,000 — Standard (default)", value: "1000" },
  { label: "2,500 — Extended", value: "2500" },
  { label: "5,000 — High precision", value: "5000" },
  { label: "10,000 — Research grade", value: "10000" },
];

const ERROR_PRESETS = [
  { label: "0.00 — Perfect channel (lab conditions)", value: "0" },
  { label: "0.02 — Low noise (space-to-ground)", value: "0.02" },
  { label: "0.05 — Moderate noise (atmospheric)", value: "0.05" },
  { label: "0.08 — High noise (degraded link)", value: "0.08" },
  { label: "0.10 — Near threshold (barely secure)", value: "0.10" },
  { label: "0.15 — Above threshold (insecure)", value: "0.15" },
  { label: "0.25 — Heavy noise / strong eavesdropper", value: "0.25" },
  { label: "0.50 — Worst case (50% error)", value: "0.50" },
];

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
    try { setSessions(await api.qkdSessions()); } catch (e) { setError(e instanceof Error ? e.message : "Failed to load sessions"); }
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
          <div className="card-header">
            <h3>Protocol Parameters</h3>
            <FieldInfo>
              Configure the QKD protocol simulation. These parameters control the quantum
              key exchange process between Alice and Bob. The simulation models photon
              transmission, measurement, sifting, and eavesdropping detection.
            </FieldInfo>
          </div>
          <div className="form-group">
            <label>
              Protocol
              <FieldInfo>
                Choose the <strong>quantum key distribution protocol</strong>:
                <ul>
                  <li><strong>BB84</strong> — Bennett-Brassard (1984): Alice sends photons in random bases,
                  Bob measures. They sift matching bases to extract a shared key. Simpler, more practical.</li>
                  <li><strong>E91</strong> — Ekert (1991): Uses <strong>entangled photon pairs</strong>.
                  Security is verified via Bell inequality tests. More theoretically elegant but harder
                  to implement physically.</li>
                </ul>
              </FieldInfo>
            </label>
            <select value={protocol} onChange={(e) => setProtocol(e.target.value)}>
              <option value="bb84">BB84 (Bennett-Brassard 1984)</option>
              <option value="e91">E91 (Ekert 1991)</option>
            </select>
          </div>
          <div className="form-group">
            <label>
              Number of Qubits
              <FieldInfo>
                The total number of <strong>qubits (photons)</strong> Alice sends in the protocol.
                More qubits = longer final key but more transmission time. After sifting (keeping only
                matching bases), roughly <strong>50%</strong> of qubits are kept. After error correction
                and privacy amplification, the final key is even shorter. 1000 qubits typically yields
                ~200-400 secure key bits.
              </FieldInfo>
            </label>
            <PresetSelect
              options={QUBIT_PRESETS}
              value={String(numQubits)}
              onChange={(v) => setNumQubits(parseInt(v) || 100)}
              placeholder="Select qubit count..."
              customPlaceholder="Enter custom number of qubits"
              type="number"
            />
          </div>
          <div className="form-group">
            <label>
              Channel Error Rate
              <FieldInfo>
                The <strong>natural error rate</strong> of the quantum channel (0–1), before any
                eavesdropper. Real channels have noise from detector dark counts, photon loss,
                and atmospheric turbulence. For satellite-to-ground links, typical error rates are
                1–5%. This is separate from eavesdropper-induced errors.
              </FieldInfo>
            </label>
            <PresetSelect
              options={ERROR_PRESETS}
              value={String(channelError)}
              onChange={(v) => setChannelError(parseFloat(v) || 0)}
              placeholder="Select error rate..."
              customPlaceholder="Enter 0.0 to 1.0"
              type="number"
            />
          </div>
          <div className="form-group">
            <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
              <input type="checkbox" checked={eavesdropper} onChange={(e) => setEavesdropper(e.target.checked)} />
              Simulate Eavesdropper (Eve)
              <FieldInfo>
                When enabled, <strong>Eve intercepts and measures</strong> a fraction of the photons
                in transit between Alice and Bob. By the <strong>measurement disturbance principle</strong>,
                this introduces detectable errors (raises QBER). If QBER exceeds <strong>11%</strong>,
                Alice and Bob know the channel is compromised and discard the key. Try running with
                and without Eve to see the difference in QBER.
              </FieldInfo>
            </label>
          </div>
          <button className="btn btn-primary" onClick={runQKD} disabled={loading}>
            {loading ? "Running..." : `Run ${protocol.toUpperCase()} Protocol`}
          </button>
        </div>

        {result && (
          <div className="card">
            <div className="card-header">
              <h3>QKD Result</h3>
              <FieldInfo>
                The results of the quantum key distribution protocol run. The key metrics are
                <strong> QBER</strong> (should be below 11%) and whether the key is <strong>secure</strong>.
                The sifted key length shows how many usable bits were extracted after the sifting process.
              </FieldInfo>
            </div>
            <div className="grid grid-2 gap-4">
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">QBER</div>
                  <FieldInfo>
                    <strong>Quantum Bit Error Rate</strong> — the fraction of mismatched bits between
                    Alice and Bob after sifting. Below <strong>11%</strong> (green) = secure key can be
                    extracted. Above 11% (red) = too many errors, either from channel noise or
                    eavesdropping. The 11% threshold comes from the Csiszár–Körner theorem.
                  </FieldInfo>
                </div>
                <div className={`value ${result.qber !== null && result.qber < 0.11 ? "success" : "danger"}`} style={{ fontSize: 22 }}>
                  {result.qber !== null ? `${(result.qber * 100).toFixed(2)}%` : "N/A"}
                </div>
                <div className="sub">Threshold: 11%</div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Secure</div>
                  <FieldInfo>
                    Whether the protocol produced a <strong>provably secure key</strong>. This requires
                    QBER &lt; 11%. If secure, Alice and Bob can proceed with privacy amplification to
                    generate a final key that is information-theoretically secure — meaning even a
                    quantum computer cannot crack it.
                  </FieldInfo>
                </div>
                <div className={`value ${result.secure ? "success" : "danger"}`} style={{ fontSize: 22 }}>
                  {result.secure ? "YES" : "NO"}
                </div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Sifted Key Length</div>
                  <FieldInfo>
                    The number of bits remaining after <strong>sifting</strong> — the process where
                    Alice and Bob keep only the bits where they used the same measurement basis.
                    Roughly 50% of original qubits survive sifting. This is before error correction
                    and privacy amplification, which further reduce the final key length.
                  </FieldInfo>
                </div>
                <div className="value accent" style={{ fontSize: 22 }}>{result.sifted_key_length ?? "N/A"}</div>
              </div>
              <div className="stat-card">
                <div className="label-row">
                  <div className="label">Efficiency</div>
                  <FieldInfo>
                    The ratio of <strong>sifted key bits to total qubits sent</strong>. Theoretical
                    maximum is 50% (only matching bases are kept). Real-world efficiency is lower
                    due to photon loss, detector inefficiency, and channel errors.
                  </FieldInfo>
                </div>
                <div className="value info" style={{ fontSize: 22 }}>
                  {result.efficiency !== null ? `${(result.efficiency * 100).toFixed(1)}%` : "N/A"}
                </div>
              </div>
            </div>
            {result.alice_key && (
              <div style={{ marginTop: 16 }}>
                <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>
                  Alice's Key (first 32 bits)
                  <FieldInfo>
                    A sample of the first 32 bits of <strong>Alice's raw key</strong> after sifting.
                    Each bit corresponds to a photon measurement where Alice and Bob used the same basis.
                    In a real QKD system, this would be followed by error correction and privacy
                    amplification to produce the final shared secret key.
                  </FieldInfo>
                </p>
                <code style={{ fontSize: 13, color: "var(--accent)" }}>[{result.alice_key.join(", ")}]</code>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h3>Session History</h3>
          <div className="flex items-center gap-2">
            <FieldInfo>
              A log of all QKD protocol sessions. Each entry records the protocol used,
              number of qubits, resulting QBER, security status, and key length. Compare
              sessions with and without eavesdroppers to see how Eve's interception
              raises the error rate.
            </FieldInfo>
            <button className="btn btn-secondary btn-sm" onClick={loadSessions}>Refresh</button>
          </div>
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
