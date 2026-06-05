import { useState } from "react";

interface InfoBubbleProps {
  title: string;
  children: React.ReactNode;
  learnMoreUrl?: string;
}

export function InfoBubble({ title, children, learnMoreUrl }: InfoBubbleProps) {
  const [open, setOpen] = useState(true);
  return (
    <div
      style={{
        background: "linear-gradient(135deg, rgba(59,130,246,0.06) 0%, rgba(6,182,212,0.04) 100%)",
        border: "1px solid rgba(59,130,246,0.15)",
        borderLeft: "4px solid var(--accent)",
        borderRadius: "var(--radius-lg)",
        padding: open ? "20px 24px" : "12px 24px",
        marginBottom: 20,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          cursor: "pointer",
          userSelect: "none",
        }}
        onClick={() => setOpen(!open)}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 16, color: "var(--accent)" }}>i</span>
          <span
            style={{
              fontSize: 14,
              fontWeight: 600,
              color: "var(--accent)",
            }}
          >
            {title}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {learnMoreUrl && (
            <a
              href={learnMoreUrl}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              style={{ fontSize: 12, color: "var(--accent)", fontWeight: 500 }}
            >
              Learn more &rarr;
            </a>
          )}
          <span
            style={{
              fontSize: 11,
              color: "var(--text-muted)",
              cursor: "pointer",
            }}
          >
            {open ? "Hide" : "Show"}
          </span>
        </div>
      </div>
      {open && (
        <div
          style={{
            marginTop: 14,
            fontSize: 13,
            lineHeight: 1.75,
            color: "var(--text-secondary)",
          }}
        >
          {children}
        </div>
      )}
    </div>
  );
}
