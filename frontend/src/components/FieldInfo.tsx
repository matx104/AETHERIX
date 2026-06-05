import { useState, useRef, useEffect } from "react";

interface FieldInfoProps {
  children: React.ReactNode;
}

export function FieldInfo({ children }: FieldInfoProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <span className="field-info-wrapper" ref={ref}>
      <button
        className="field-info-trigger"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setOpen(!open);
        }}
        type="button"
        aria-label="More information"
      >
        i
      </button>
      {open && (
        <div className="field-info-popover" onClick={(e) => e.stopPropagation()}>
          <div className="field-info-content">{children}</div>
        </div>
      )}
    </span>
  );
}
