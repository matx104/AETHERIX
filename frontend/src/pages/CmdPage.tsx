import { useEffect, useState } from "react";
import { fetchApi } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";

interface CommandInfo {
  id: string;
  label: string;
  description: string;
  cmd: string;
  expected: string;
  icon: string;
  category: string;
  category_label: string;
}

interface Catalog {
  categories: Record<string, { label: string; commands: CommandInfo[] }>;
  total: number;
}

export function CmdPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [selected, setSelected] = useState<CommandInfo | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchApi<Catalog>("/cmd/catalog")
      .then((cat) => {
        setCatalog(cat);
        const first = Object.values(cat.categories)[0]?.commands[0];
        if (first) setSelected({ ...first });
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load catalog"));
  }, []);

  const copyCmd = async (cmd: string) => {
    try {
      await navigator.clipboard.writeText(cmd);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  if (!catalog) {
    return (
      <>
        <div className="page-header">
          <h2>Command Reference</h2>
        </div>
        <div className="card">
          <p style={{ color: "var(--text-muted)" }}>Loading command catalog...</p>
        </div>
      </>
    );
  }

  const catKeys = Object.keys(catalog.categories);

  return (
    <>
      <div className="page-header">
        <h2>Command Reference</h2>
        <p>Copy any command and run it in your own terminal — with what it does and the output to expect.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <InfoBubble title="Command Reference" learnMoreUrl="https://matx104.github.io/AETHERIX/#cmd-terminal">
        <p>
          A reference for every AETHERIX script and module demo. Pick a command, read
          what it does and what output to expect, then <strong>copy it</strong> and run
          it in a terminal at the project root. Nothing is executed by the browser or
          the server.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Shell Scripts</strong> set up the environment, run the 189-test suite,
          lint, and clean. <strong>Python modules</strong> are stdlib-only, so each demo
          runs with a plain <code>python3 src/...</code> (no extra dependencies).
        </p>
      </InfoBubble>

      <div className="grid" style={{ gridTemplateColumns: "280px 1fr", alignItems: "start" }}>
        {/* Command sidebar */}
        <div style={{ maxHeight: "calc(100vh - 160px)", overflowY: "auto", paddingRight: 8 }}>
          {catKeys.map((catKey) => {
            const cat = catalog.categories[catKey];
            return (
              <div key={catKey} style={{ marginBottom: 12 }}>
                <div style={{ fontWeight: 600, fontSize: 12, padding: "6px 8px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                  {cat.label} ({cat.commands.length})
                </div>
                {cat.commands.map((cmd) => (
                  <button
                    key={cmd.id}
                    className="nav-item"
                    style={{
                      fontSize: 12,
                      padding: "5px 8px 5px 16px",
                      width: "100%",
                      textAlign: "left",
                      background: selected?.id === cmd.id ? "var(--accent-glow)" : "transparent",
                      color: selected?.id === cmd.id ? "var(--accent)" : "var(--text-secondary)",
                    }}
                    onClick={() => setSelected({ ...cmd })}
                  >
                    {cmd.label}
                  </button>
                ))}
              </div>
            );
          })}
        </div>

        {/* Detail panel */}
        <div>
          {selected && (
            <div className="card">
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                <strong style={{ fontSize: 16 }}>{selected.label}</strong>
                <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{selected.category_label}</span>
              </div>

              <p style={{ marginTop: 8, color: "var(--text-secondary)" }}>{selected.description}</p>

              <div style={{ marginTop: 16, fontSize: 12, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                Command
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginTop: 6,
                  background: "var(--bg-input)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius)",
                  padding: "10px 12px",
                }}
              >
                <code style={{ flex: 1, fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--accent)", wordBreak: "break-all" }}>
                  {selected.cmd}
                </code>
                <button className="btn btn-primary btn-sm" onClick={() => copyCmd(selected.cmd)} style={{ flexShrink: 0 }}>
                  {copied ? "Copied!" : "Copy"}
                </button>
              </div>
              <div style={{ marginTop: 6, fontSize: 11, color: "var(--text-muted)" }}>
                Run from the project root.
              </div>

              <div style={{ marginTop: 16, fontSize: 12, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 0.5 }}>
                Expected output
              </div>
              <div
                style={{
                  marginTop: 6,
                  background: "var(--bg-secondary)",
                  border: "1px solid var(--border)",
                  borderLeft: "3px solid var(--success)",
                  borderRadius: "var(--radius)",
                  padding: "10px 12px",
                  color: "var(--text-secondary)",
                  fontSize: 13,
                  lineHeight: 1.6,
                }}
              >
                {selected.expected}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
