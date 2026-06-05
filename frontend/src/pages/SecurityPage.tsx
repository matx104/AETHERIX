import { useState } from "react";
import { api, type QKDResult } from "../api/client";

export function SecurityPage() {
  const [protocol, setProtocol] = useState("bb84");
  const [numQubits, setNumQubits] = useState(1000);
  const [channelError, setChannelError] = useState(0);
  const [eavesdropper, setEavesdropper] = useState(false);
  const [result, setResult] = useState<QKDResult | null>(null);
  const [sessions, setSessions] = useState<QKDResult[]>([]);
  const [loading, setLoading] = useState(false);

  const runQKD = async () => {
    setLoading(true);
    try {
      const res = await api.runQKD({ protocol, num_qubits: numQubits, channel_error: channelError, eavesdropper });
      setResult(res);
      loadSessions();
    } catch {}
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
            <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
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
                <div className={`value ${result.qber !== null && result.qber < 0.11 ? "success" : "danger"}`} style={{ fontSize: 20 }}>
                  {result.qber !== null ? `${(result.qber * 100).toFixed(2)}%` : "N/A"}
                </div>
                <div className="sub">Threshold: 11%</div>
              </div>
              <div className="stat-card">
                <div className="label">Secure</div>
                <div className={`value ${result.secure ? "success" : "danger"}`} style={{ fontSize: 20 }}>
                  {result.secure ? "YES" : "NO"}
                </div>
              </div>
              <div className="stat-card">
                <div className="label">Sifted Key Length</div>
                <div className="value accent" style={{ fontSize: 20 }}>{result.sifted_key_length ?? "N/A"}</div>
              </div>
              <div className="stat-card">
                <div className="label">Efficiency</div>
                <div className="value info" style={{ fontSize: 20 }}>
                  {result.efficiency !== null ? `${(result.efficiency * 100).toFixed(1)}%` : "N/A"}
                </div>
              </div>
            </div>
            {result.alice_key && (
              <div style={{ marginTop: 16 }}>
                <p style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>Alice's Key (first 32 bits)</p>
                <code style={{ fontSize: 13, color: "var(--accent)" }}>
                  [{result.alice_key.join(", ")}]
                </code>
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
                  <td>{s.qber !== null ? `${(s.qber * 100).toFixed(2)}%` : "-"}</td>
                  <td>{s.secure ? <span className="badge badge-success">Yes</span> : <span className="badge badge-danger">No</span>}</td>
                  <td>{s.sifted_key_length ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>No sessions yet. Run a protocol above.</p>
        )}
      </div>
    </>
  );
}
