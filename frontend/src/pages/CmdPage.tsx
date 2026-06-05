import { useEffect, useRef, useState } from "react";
import { InfoBubble } from "../components/InfoBubble";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

interface CommandInfo {
  id: string;
  label: string;
  description: string;
  cmd: string;
  icon: string;
  category: string;
  category_label: string;
}

interface Catalog {
  categories: Record<
    string,
    { label: string; commands: CommandInfo[] }
  >;
  total: number;
}

interface OutputLine {
  type: string;
  text?: string;
  exit_code?: number;
}

export function CmdPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [selected, setSelected] = useState<CommandInfo | null>(null);
  const [output, setOutput] = useState<OutputLine[]>([]);
  const [running, setRunning] = useState(false);
  const [customArgs, setCustomArgs] = useState("");
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const termRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/cmd/catalog`)
      .then((r) => r.json())
      .then(setCatalog)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (termRef.current) {
      termRef.current.scrollTop = termRef.current.scrollHeight;
    }
  }, [output]);

  const run = async (cmd: CommandInfo) => {
    if (running) return;
    setSelected(cmd);
    setOutput([{ type: "meta", text: `$ ${cmd.cmd}${customArgs ? " " + customArgs : ""}` }]);
    setRunning(true);

    const abort = new AbortController();
    abortRef.current = abort;

    try {
      const qs = customArgs ? `?args=${encodeURIComponent(customArgs)}` : "";
      const res = await fetch(`${API_BASE}/cmd/run/${cmd.id}${qs}`, {
        signal: abort.signal,
      });
      const reader = res.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const evt = JSON.parse(line.slice(6));
              setOutput((prev) => [...prev, evt]);
            } catch {}
          }
        }
      }
    } catch (e: unknown) {
      if (e instanceof DOMException && e.name === "AbortError") {
        setOutput((prev) => [...prev, { type: "error", text: "Aborted" }]);
      } else {
        setOutput((prev) => [...prev, { type: "error", text: String(e) }]);
      }
    } finally {
      setRunning(false);
      abortRef.current = null;
    }
  };

  const stop = () => {
    abortRef.current?.abort();
  };

  const clearOutput = () => {
    setOutput([]);
    setSelected(null);
  };

  const lineColor = (line: OutputLine) => {
    if (line.type === "error") return "var(--danger)";
    if (line.type === "done" && line.exit_code === 0) return "var(--success)";
    if (line.type === "done" && line.exit_code !== 0) return "var(--danger)";
    if (line.type === "meta") return "var(--accent)";
    return "var(--text-secondary)";
  };

  const linePrefix = (line: OutputLine) => {
    if (line.type === "error") return "✗ ";
    if (line.type === "done" && line.exit_code === 0) return "✓ ";
    if (line.type === "done") return `✗ (exit ${line.exit_code}) `;
    if (line.type === "meta") return "";
    return "  ";
  };

  if (!catalog) {
    return (
      <>
        <div className="page-header">
          <h2>Command Terminal</h2>
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
        <h2>Command Terminal</h2>
        <p>Run scripts, tests, modules, and utilities from the web interface</p>
      </div>

      <InfoBubble title="Command Terminal" learnMoreUrl="https://matx104.github.io/AETHERIX/#cmd-terminal">
        <p>
          This terminal connects to the AETHERIX backend API and executes commands
          server-side, streaming output in real-time via{" "}
          <strong>Server-Sent Events (SSE)</strong>. It gives you full access to the
          project's utility scripts and Python module demos without leaving the browser.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Shell Scripts:</strong> Initialize environments, run the 189-test
          suite, lint code, and clean artifacts — the same scripts used in CI/CD.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Python Modules:</strong> Run all 16 module demos (optical/RF link
          budgets, RL routing, QKD protocols, orbital mechanics, topology, radiation
          simulation, and more) and see their output instantly.
        </p>
      </InfoBubble>

      <div className="grid" style={{ gridTemplateColumns: "280px 1fr" }}>
        {/* Command sidebar */}
        <div
          style={{
            maxHeight: "calc(100vh - 160px)",
            overflowY: "auto",
            paddingRight: 8,
          }}
        >
          {catKeys.map((catKey) => {
            const cat = catalog.categories[catKey];
            const isOpen = activeCategory === catKey || activeCategory === null;
            return (
              <div key={catKey} style={{ marginBottom: 8 }}>
                <button
                  className="nav-item"
                  style={{ fontWeight: 600, fontSize: 12, padding: "6px 8px" }}
                  onClick={() =>
                    setActiveCategory(activeCategory === catKey ? null : catKey)
                  }
                >
                  {cat.label} ({cat.commands.length})
                </button>
                {isOpen &&
                  cat.commands.map((cmd) => (
                    <button
                      key={cmd.id}
                      className="nav-item"
                      style={{
                        fontSize: 12,
                        padding: "5px 8px 5px 16px",
                        background:
                          selected?.id === cmd.id
                            ? "var(--accent-glow)"
                            : "transparent",
                        color:
                          selected?.id === cmd.id
                            ? "var(--accent)"
                            : "var(--text-secondary)",
                      }}
                      onClick={() => {
                        setSelected(cmd);
                        setCustomArgs("");
                      }}
                      disabled={running}
                    >
                      {cmd.label}
                    </button>
                  ))}
              </div>
            );
          })}
        </div>

        {/* Terminal area */}
        <div>
          {selected && (
            <div className="card" style={{ marginBottom: 12, padding: 12 }}>
              <div className="flex items-center justify-between">
                <div>
                  <strong>{selected.label}</strong>
                  <span
                    style={{
                      marginLeft: 8,
                      fontSize: 11,
                      color: "var(--text-muted)",
                    }}
                  >
                    {selected.description}
                  </span>
                </div>
                <div className="flex gap-2">
                  <input
                    value={customArgs}
                    onChange={(e) => setCustomArgs(e.target.value)}
                    placeholder="extra args..."
                    style={{
                      background: "var(--bg-input)",
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius)",
                      color: "var(--text-primary)",
                      padding: "4px 8px",
                      fontSize: 12,
                      fontFamily: "var(--font-mono)",
                      width: 200,
                    }}
                    disabled={running}
                  />
                  {running ? (
                    <button className="btn btn-danger btn-sm" onClick={stop}>
                      Stop
                    </button>
                  ) : (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => run(selected)}
                    >
                      Run
                    </button>
                  )}
                  <button className="btn btn-secondary btn-sm" onClick={clearOutput}>
                    Clear
                  </button>
                </div>
              </div>
              <code
                style={{
                  display: "block",
                  marginTop: 8,
                  fontSize: 12,
                  color: "var(--text-muted)",
                }}
              >
                $ {selected.cmd}
                {customArgs ? ` ${customArgs}` : ""}
              </code>
            </div>
          )}

          <div
            ref={termRef}
            style={{
              background: "var(--bg-input)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-lg)",
              padding: 16,
              minHeight: 400,
              maxHeight: "calc(100vh - 340px)",
              overflowY: "auto",
              fontFamily: "var(--font-mono)",
              fontSize: 13,
              lineHeight: 1.6,
            }}
          >
            {output.length === 0 ? (
              <span style={{ color: "var(--text-muted)" }}>
                Select a command from the sidebar and click Run.
                {"\n"}
                Output will stream here in real-time.
              </span>
            ) : (
              output.map((line, i) => (
                <div key={i} style={{ color: lineColor(line) }}>
                  {line.type === "done"
                    ? line.exit_code === 0
                      ? "Process finished with exit code 0"
                      : `Process exited with code ${line.exit_code}`
                    : `${linePrefix(line)}${line.text || ""}`}
                </div>
              ))
            )}
            {running && (
              <span style={{ color: "var(--accent)" }}>▌</span>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
