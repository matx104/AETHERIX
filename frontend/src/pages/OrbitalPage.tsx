import { useEffect, useState } from "react";
import { api, type DistanceTimeline, type DistancePoint } from "../api/client";
import { InfoBubble } from "../components/InfoBubble";
import { ResourcesCard } from "../components/ResourcesCard";
import { SHOWCASE_URL } from "../components/ResourcesCard";

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
          <div className="label">Current Distance</div>
          <div className="value info">
            {distance ? `${(distance.distance_km / 1e6).toFixed(1)}M km` : "..."}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Light-Time Delay</div>
          <div className="value warning">
            {distance ? `${distance.light_time_minutes.toFixed(1)} min` : "..."}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Min Distance</div>
          <div className="value success">54.6M km</div>
        </div>
        <div className="stat-card">
          <div className="label">Max Distance</div>
          <div className="value danger">401.0M km</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Distance Explorer</h3>
          <span className="mono" style={{ color: "var(--text-muted)", fontSize: 13 }}>
            True Anomaly: {anomaly}°
          </span>
        </div>
        <div className="form-group">
          <input
            type="range" min="0" max="360" value={anomaly}
            onChange={(e) => setAnomaly(parseInt(e.target.value))}
            style={{ width: "100%" }}
          />
        </div>
        {distance && (
          <div className="grid grid-2 gap-4">
            <div className="stat-card">
              <div className="label">Distance at {anomaly}°</div>
              <div className="value accent">{(distance.distance_km / 1e6).toFixed(2)}M km</div>
            </div>
            <div className="stat-card">
              <div className="label">One-Way Delay</div>
              <div className="value warning">{distance.light_time_minutes.toFixed(2)} min</div>
            </div>
          </div>
        )}
      </div>

      {timeline && (
        <div className="card mt-4">
          <div className="card-header"><h3>Synodic Period Timeline (780 days)</h3></div>
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
