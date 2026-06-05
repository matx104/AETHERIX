import { useEffect, useState } from "react";
import { api, type DistanceTimeline, type DistancePoint } from "../api/client";

export function OrbitalPage() {
  const [timeline, setTimeline] = useState<DistanceTimeline | null>(null);
  const [distance, setDistance] = useState<{ distance_km: number; light_time_minutes: number } | null>(null);
  const [anomaly, setAnomaly] = useState(0);

  useEffect(() => {
    api.timeline().then(setTimeline).catch(() => {});
  }, []);

  useEffect(() => {
    api.distance(anomaly).then(setDistance).catch(() => {});
  }, [anomaly]);

  const maxDist = timeline?.max_distance_km ?? 401e6;

  return (
    <>
      <div className="page-header">
        <h2>Orbital Mechanics</h2>
        <p>Earth-Mars distance calculations, contact windows, and light-time delay</p>
      </div>

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
          <div className="value success">{(54.6).toFixed(1)}M km</div>
        </div>
        <div className="stat-card">
          <div className="label">Max Distance</div>
          <div className="value danger">{(401.0).toFixed(1)}M km</div>
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
          <div className="card-header"><h3>Synodic Period Timeline</h3></div>
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
    </>
  );
}
