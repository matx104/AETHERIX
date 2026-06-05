import { useState, useEffect, useRef } from "react";

interface PresetOption {
  label: string;
  value: string;
}

interface PresetSelectProps {
  options: PresetOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  customPlaceholder?: string;
  type?: "text" | "number";
}

const CUSTOM_VALUE = "__custom__";

export function PresetSelect({
  options,
  value,
  onChange,
  placeholder = "Select an option",
  customPlaceholder = "Enter custom value...",
  type = "text",
}: PresetSelectProps) {
  const isPreset = options.some((o) => o.value === value);
  const [selected, setSelected] = useState(isPreset ? value : CUSTOM_VALUE);
  const [custom, setCustom] = useState(isPreset ? "" : value);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const match = options.some((o) => o.value === value);
    if (match) {
      setSelected(value);
      setCustom("");
    } else if (value) {
      setSelected(CUSTOM_VALUE);
      setCustom(value);
    }
  }, [value, options]);

  useEffect(() => {
    if (selected === CUSTOM_VALUE && inputRef.current) {
      inputRef.current.focus();
    }
  }, [selected]);

  const handleSelect = (v: string) => {
    setSelected(v);
    if (v === CUSTOM_VALUE) {
      if (custom) onChange(custom);
    } else {
      setCustom("");
      onChange(v);
    }
  };

  const handleCustom = (v: string) => {
    setCustom(v);
    onChange(v);
  };

  return (
    <div>
      <select
        value={selected}
        onChange={(e) => handleSelect(e.target.value)}
        style={{ marginBottom: selected === CUSTOM_VALUE ? 8 : 0 }}
      >
        <option value="" disabled>
          {placeholder}
        </option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
        <option value={CUSTOM_VALUE}>Custom...</option>
      </select>
      {selected === CUSTOM_VALUE && (
        <input
          ref={inputRef}
          type={type}
          value={custom}
          onChange={(e) => handleCustom(e.target.value)}
          placeholder={customPlaceholder}
          style={{
            background: "var(--bg-input)",
            border: "1px solid var(--border)",
            borderTop: "none",
            borderRadius: "0 0 var(--radius) var(--radius)",
            padding: "10px 14px",
            color: "var(--text-primary)",
            fontSize: 14,
            fontFamily: "var(--font-mono)",
            width: "100%",
            outline: "none",
          }}
        />
      )}
    </div>
  );
}
