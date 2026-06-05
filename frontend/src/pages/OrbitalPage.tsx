import { useEffect, useState } from "react";
import { api, type DistanceTimeline, type DistancePoint } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { FieldInfo } from "../components/FieldInfo";
import { PresetSelect } from "../components/PresetSelect";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

const ANOMALY_PRESETS = [
  { label: "0° — Perihelion (closest approach)", value: "0" },
  { label: "30° — Early orbit", value: "30" },
  { label: "60° — First quarter", value: "60" },
  { label: "90° — Quadrature", value: "90" },
  { label: "120° — Approaching opposition", value: "120" },
  { label: "150° — Pre-conjunction", value: "150" },
  { label: "180° — Aphelion (farthest / conjunction)", value: "180" },
  { label: "210° — Post-conjunction", value: "210" },
  { label: "240° — Late orbit", value: "240" },
  { label: "270° — Third quarter", value: "270" },
  { label: "300° — Approaching perihelion", value: "300" },
  { label: "330° — Near opposition", value: "330" },
  { label: "360° — Back to perihelion", value: "360" },
];

const RESOURCES = [
  { type: "Tool", title: "JPL Horizons — Precise Ephemeris System", url: "https://ssd.jpl.nasa.gov/horizons/app.html", badge: "MUST USE" },
  { type: "Tool", title: "NASA Eyes on the Solar System — 3D Visualization", url: "https://eyes.nasa.gov/", badge: "INTERACTIVE" },
  { type: "Tool", title: "GMAT — NASA General Mission Analysis Tool (Free)", url: "https://software.nasa.gov/software/GSFC-54099", badge: "SOFTWARE" },
  { type: "Video", title: "CrashCourse — 'Orbital Mechanics' Full Course", url: "https://www.youtube.com/watch?v=J1lRLElluEQ", badge: "YOUTUBE" },
  { type: "Course", title: "CU Boulder — Spacecraft Dynamics (Coursera)", url: "https://www.coursera.org/learn/spacecraft-dynamics-kinetics", badge: "FREE AUDIT" },
];

export function OrbitalPage() {
  const [timeline, setTimeline] = useState<DistanceTimeline | null>(null);
  const [distance, setDistance] = useState<{ distance_km: number; light_time_minutes: number } | null>(null);
  const [anomaly, setAnomaly] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    api.timeline().then(setTimeline).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    api.distance(anomaly).then(setDistance).catch(() => {});
  }, [anomaly]);

  const maxDist = timeline?.max_distance_km ?? 401e6;

  return (
    <>
      <div className="page-header">
        <h2>Orbital Mechanics</h2>
        <p>Earth–Mars distance calculations, contact windows, and light-time delay</p>
      </div>

      <InfoBubble title="Why Orbital Mechanics Matters for Space Communication" learnMoreUrl={`${SHOWCASE_URL}/#orbital`}>
        <p>
          Mars and Earth both orbit the Sun at different speeds — Earth in{" "}
          <strong>365 days</strong>, Mars in <strong>687 days</strong>. The distance
          between them is constantly changing, from as close as{" "}
          <strong>55 million km</strong> (opposition) to as far as{" "}
          <strong>401 million km</strong> (conjunction). That is a{" "}
          <strong>7× difference</strong> over the synodic period (~780 days).
        </p>
        <p style={{ marginTop: 8 }}>
          All electromagnetic radiation travels at the speed of light (~300,000 km/s).
          This is the absolute speed limit of the universe. No amount of engineering
          can make data travel faster. At opposition, one-way delay is{" "}
          <strong>~3 minutes</strong>. At conjunction, it is{" "}
          <strong>~22 minutes</strong> — with a <strong>2-week blackout</strong>{" "}
          when Mars is behind the Sun.
        </p>
        <p style={{ marginTop: 8 }}>
          <strong>Thought experiment:</strong> An astronaut on Mars sends a message
          at T+0. It arrives at Earth at T+12 min. Earth replies immediately. The
          astronaut receives it at T+24 min. <strong>25 minutes</strong> for a simple
          back-and-forth. Real-time conversation is impossible — Mars systems must be
          autonomous.
        </p>
      </InfoBubble>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-4 mb-4">
        <div className="stat-card">
          <div className="label-row">
            <div className="label">Current Distance</div>
            <FieldInfo>
              The <strong>real-time slant range</strong> between Earth and Mars based on
              the selected true anomaly angle. This is calculated from Keplerian orbital
              mechanics using semi-major axes and eccentricities of both planets.
            </FieldInfo>
          </div>
          <div className="value info">
            {distance ? `${(distance.distance_km / 1e6).toFixed(1)}M km` : "..."}
          </div>
        </div>
        <div className="stat-card">
          <div className="label-row">
            <div className="label">Light-Time Delay</div>
            <FieldInfo>
              The <strong>one-way signal propagation time</strong> at the speed of light
              (299,792 km/s). This is the absolute minimum latency — no engineering can
              reduce it. Round-trip time (RTT) is double this value. At average distance,
              RTT is ~25 minutes.
            </FieldInfo>
          </div>
          <div className="value warning">
            {distance ? `${distance.light_time_minutes.toFixed(1)} min` : "..."}
          </div>
        </div>
        <div className="stat-card">
          <div className="label-row">
            <div className="label">Min Distance</div>
            <FieldInfo>
              The <strong>closest approach</strong> (perihelion opposition) at ~54.6 million km.
              This occurs roughly every <strong>26 months</strong> during opposition, when Earth
              "laps" Mars in its orbit. This is the optimal launch window for Mars missions.
            </FieldInfo>
          </div>
          <div className="value success">54.6M km</div>
        </div>
        <div className="stat-card">
          <div className="label-row">
            <div className="label">Max Distance</div>
            <FieldInfo>
              The <strong>farthest separation</strong> (aphelion conjunction) at ~401 million km.
              Mars is on the opposite side of the Sun from Earth. The Sun blocks direct
              communication for ~2 weeks — this is the <strong>solar conjunction blackout</strong>.
            </FieldInfo>
          </div>
          <div className="value danger">401.0M km</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Distance Explorer</h3>
          <div className="flex items-center gap-2">
            <FieldInfo>
              Set the <strong>true anomaly angle</strong> (0°–360°) —
              the angular position of Mars in its elliptical orbit relative to perihelion.
              The distance and light-time delay update in real-time. At 0° = closest,
              180° = farthest. Use the dropdown for key orbital positions or the slider
              for fine-grained control.
            </FieldInfo>
            <span className="mono" style={{ color: "var(--text-muted)", fontSize: 13 }}>
              True Anomaly: {anomaly}°
            </span>
          </div>
        </div>
        <div className="form-group">
          <label>
            Orbital Position
            <FieldInfo>
              Select a <strong>key orbital position</strong> from the dropdown, or choose "Custom"
              to enter any angle. 0° is perihelion (closest), 180° is aphelion (farthest).
            </FieldInfo>
          </label>
          <PresetSelect
            options={ANOMALY_PRESETS}
            value={String(anomaly)}
            onChange={(v) => setAnomaly(parseInt(v) || 0)}
            placeholder="Select orbital position..."
            customPlaceholder="Enter angle 0–360"
            type="number"
          />
        </div>
        <div className="form-group">
          <label>
            Fine Control (slider)
            <FieldInfo>
              Drag the slider for <strong>continuous control</strong> over the true anomaly angle.
              This gives you fine-grained exploration of how distance varies across the entire orbit.
            </FieldInfo>
          </label>
          <input
            type="range" min="0" max="360" value={anomaly}
            onChange={(e) => setAnomaly(parseInt(e.target.value))}
            style={{ width: "100%" }}
          />
        </div>
        {distance && (
          <div className="grid grid-2 gap-4">
            <div className="stat-card">
              <div className="label-row">
                <div className="label">Distance at {anomaly}°</div>
                <FieldInfo>
                  The computed <strong>Earth–Mars distance</strong> at this true anomaly.
                  Mars's orbit has eccentricity ~0.093 (quite elliptical), so distance varies
                  non-linearly with anomaly angle. This directly impacts link budget and data rate.
                </FieldInfo>
              </div>
              <div className="value accent">{(distance.distance_km / 1e6).toFixed(2)}M km</div>
            </div>
            <div className="stat-card">
              <div className="label-row">
                <div className="label">One-Way Delay</div>
                <FieldInfo>
                  <strong>One-way light time</strong> at this distance. Data sent now arrives
                  this many minutes later. For a two-way handshake (e.g., "did you receive this?"),
                  double this value. Autonomous protocols are essential when delay exceeds 10 minutes.
                </FieldInfo>
              </div>
              <div className="value warning">{distance.light_time_minutes.toFixed(2)} min</div>
            </div>
          </div>
        )}
      </div>

      {timeline && (
        <div className="card mt-4">
          <div className="card-header">
            <h3>Synodic Period Timeline (780 days)</h3>
            <FieldInfo>
              A <strong>bar chart</strong> showing Earth–Mars distance over one synodic period
              (~780 days / ~26 months). Colors indicate distance: <strong>green</strong> (&lt; 100M km, excellent
              link), <strong>yellow</strong> (100–300M km, degraded), <strong>red</strong> (&ge; 300M km, poor or
              blackout). The synodic period is the time between successive oppositions.
            </FieldInfo>
          </div>
          <div style={{ overflowX: "auto" }}>
            <div style={{ display: "flex", alignItems: "flex-end", height: 160, gap: 2, padding: "8px 0" }}>
              {timeline.distances.filter((_, i) => i % 5 === 0).map((d: DistancePoint, i: number) => {
                const pct = ((d.distance_km / maxDist) * 100);
                const color = d.distance_km < 100e6 ? "var(--success)" : d.distance_km < 300e6 ? "var(--warning)" : "var(--danger)";
                return (
                  <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <div style={{ width: "100%", height: `${pct}%`, background: color, borderRadius: "2px 2px 0 0", minHeight: 2 }} />
                    <span style={{ fontSize: 9, color: "var(--text-muted)" }}>{Math.round(d.day)}</span>
                  </div>
                );
              })}
            </div>
          </div>
          <div className="flex gap-4 mt-4" style={{ fontSize: 12, color: "var(--text-muted)" }}>
            <span>Day 0 = Perihelion opposition</span>
            <span>~{Math.round(timeline.distances.length / 2)} days = Aphelion conjunction</span>
            <span>Period = 780 days</span>
          </div>
        </div>
      )}

      <div style={{ marginTop: 16 }}>
        <ResourcesCard title="Orbital Mechanics Resources" links={RESOURCES} />
      </div>
    </>
  );
}
