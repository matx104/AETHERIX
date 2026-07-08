# AETHERIX API Reference

The FastAPI backend exposes a REST API under `/api`. Interactive docs are
available at `http://localhost:8000/docs` (Swagger) and
`http://localhost:8000/redoc` (ReDoc) when the server is running.

## Base URL

| Environment | Base URL |
|-------------|----------|
| Local (PM2) | `http://localhost:8000/api` |
| Docker | `http://localhost:8000/api` |

---

## Health

### `GET /api/health`

Health check with database connectivity probe.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "database": "connected",
  "uptime_seconds": 127.4
}
```

---

## Simulations

### `GET /api/simulations/`

List all simulation runs, most recent first.

**Response 200:** `SimulationRunResponse[]`

### `POST /api/simulations/`

Create a new simulation run record.

**Request body:**
```json
{
  "name": "baseline-30day",
  "scenario": "earth-mars-baseline",
  "config": { "duration_hours": 720 },
  "seed": 42
}
```

**Response 201:** `SimulationRunResponse`

### `GET /api/simulations/{run_id}`

Retrieve a specific simulation run by ID.

**Response 200:** `SimulationRunResponse`
**Response 404:** `{ "detail": "Simulation run not found" }`

### `DELETE /api/simulations/{run_id}`

Delete a simulation run.

**Response 204:** (no content)
**Response 404:** `{ "detail": "Simulation run not found" }`

---

## Link Budget

### `POST /api/link-budget/optical`

Calculate an optical (1550 nm) link budget.

**Request body:**
```json
{
  "distance_km": 225000000,
  "scenario": "average"
}
```

Provide `distance_km` for a custom distance, or omit it and use `scenario`
(`"minimum"`, `"average"`, `"maximum"`) for standard Earth-Mars distances.

**Response 200:** `LinkBudgetResponse`

| Field | Description |
|-------|-------------|
| `free_space_loss_db` | Free-space path loss (negative) |
| `eirp_dbm` | Effective isotropic radiated power |
| `received_power_dbm` | Signal power at receiver |
| `link_margin_db` | Margin above required threshold |
| `data_rate_mbps` | Data rate used in calculation |

### `POST /api/link-budget/rf/{band}`

Calculate an RF link budget for the specified band.

**Path parameter:** `band` — one of `ka`, `x`, `s`, `uhf`

**Request body:** same as optical.

**Response 200:** `LinkBudgetResponse`

**Response 400:** `{ "detail": "Band must be one of ('ka', 'x', 's', 'uhf')" }`

| Band | Frequency | Typical Use |
|------|-----------|-------------|
| Ka | 26.5 GHz | High-rate downlink (primary) |
| X | 8.4 GHz | Deep-space telemetry (conjunction fallback) |
| S | 2.3 GHz | Telemetry, tracking, command |
| UHF | 401 MHz | Mars surface-to-orbiter relay |

### `GET /api/link-budget/history?limit=50`

Retrieve stored link budget calculations.

**Query parameter:** `limit` (default 50, max 1000)

**Response 200:** `LinkBudgetResponse[]`

---

## Routing

### `POST /api/routing/decide`

Make a single routing decision using the RL agent.

**Request body:**
```json
{
  "current_node": "mars.areo.alpha",
  "neighbors": ["mars.polar.gamma", "transit.esl4.relay"],
  "link_qualities": { "mars.polar.gamma": 0.8, "transit.esl4.relay": 0.4 },
  "buffer_occupancy": 0.65,
  "bundle_priority": 2,
  "bundle_size_mb": 250,
  "bundle_deadline_hours": 12,
  "destination_node": "earth.dsn.goldstone"
}
```

**Response 200:** `RoutingResponse`

| Field | Description |
|-------|-------------|
| `action` | `forward`, `store`, `drop`, or `split` |
| `next_hop` | Selected neighbor node ID (null if store/drop) |
| `confidence` | 0.0–1.0 confidence in decision |
| `reasoning` | Human-readable explanation |

### `GET /api/routing/decisions?limit=100`

Retrieve logged routing decisions.

**Response 200:** Array of decision logs.

### `POST /api/routing/train/step?episodes=100&epsilon=0.1`

Run a short RL training session.

**Query parameters:**
- `episodes` (default 100)
- `epsilon` (default 0.1)

**Response 200:**
```json
{
  "episodes": 100,
  "results": { ... TrainingMetrics ... }
}
```

---

## Orbital

### `GET /api/orbital/distance?true_anomaly_deg=0.0`

Calculate Earth-Mars distance and one-way light time for a given true anomaly.

**Response 200:**
```json
{
  "true_anomaly_deg": 0.0,
  "distance_km": 54600000,
  "light_time_seconds": 182.2,
  "light_time_minutes": 3.0
}
```

### `GET /api/orbital/timeline?num_points=780`

Get the synodic-period distance timeline (780 points = ~26 months).

**Response 200:** `DistanceTimelineResponse`

### `POST /api/orbital/contact-windows`

Predict communication contact windows.

**Request body:**
```json
{
  "duration_days": 365,
  "min_elevation_deg": 10.0,
  "window_type": "all"
}
```

**Response 200:** `ContactWindowResponse[]`

### `GET /api/orbital/contact-windows/history?limit=50`

Retrieve stored contact window predictions.

---

## Security (QKD)

### `POST /api/security/qkd`

Run a Quantum Key Distribution simulation.

**Request body:**
```json
{
  "protocol": "bb84",
  "num_qubits": 1000,
  "channel_error": 0.03,
  "eavesdropper": false
}
```

| Parameter | Default | Range |
|-----------|---------|-------|
| `protocol` | `"bb84"` | `"bb84"` or `"e91"` |
| `num_qubits` | 1000 | 1–100000 |
| `channel_error` | 0.0 | 0.0–1.0 |
| `eavesdropper` | false | boolean |

**Response 200:** `QKDResponse`

| Field | Description |
|-------|-------------|
| `qber` | Quantum Bit Error Rate (0.0–1.0) |
| `secure` | True if QBER < 11% (BB84 threshold) |
| `sifted_key_length` | Length of the sifted key |
| `efficiency` | Ratio of sifted bits to transmitted qubits |

### `GET /api/security/qkd/sessions?limit=50`

Retrieve stored QKD session results.

---

## Command Catalog

### `GET /api/cmd/catalog`

Retrieve the read-only catalog of available CLI commands and scripts.

**Response 200:**
```json
[
  {
    "id": "run-sim",
    "label": "Run End-to-End Simulation",
    "cmd": "python run_simulation.py",
    "description": "Runs all six AETHERIX modules...",
    "expected": "Module banners, computed metrics, QBER, TMR gain..."
  }
]
```

### `GET /api/cmd/catalog/{command_id}`

Retrieve a single command by ID.

---

## Data Models

### SimulationRunResponse
```typescript
{
  id: string;
  name: string;
  scenario: string;
  status: string;          // "pending" | "running" | "completed" | "failed"
  created_at: string;      // ISO 8601
  completed_at: string | null;
  result: Record<string, any> | null;
  seed: number | null;
}
```

### LinkBudgetResponse
```typescript
{
  id: string;
  link_type: string;       // "optical" | "rf_ka" | "rf_x" | "rf_s" | "rf_uhf"
  scenario: string;
  distance_km: number;
  free_space_loss_db: number;
  eirp_dbm: number;
  received_power_dbm: number;
  link_margin_db: number;
  data_rate_mbps: number;
  created_at: string;
}
```

### RoutingResponse
```typescript
{
  action: string;          // "forward" | "store" | "drop" | "split"
  next_hop: string | null;
  confidence: number;
  reasoning: string;
}
```

### QKDResponse
```typescript
{
  id: string;
  protocol: string;
  num_qubits: number;
  channel_error: number;
  eavesdropper: boolean;
  qber: number | null;
  secure: boolean | null;
  sifted_key_length: number | null;
  efficiency: number | null;
  created_at: string;
}
```

### ContactWindowResponse
```typescript
{
  id: string;
  start_time_jd: number;    // Julian Date
  end_time_jd: number;
  duration_hours: number;
  max_elevation_deg: number;
  average_distance_km: number;
  max_data_rate_mbps: number;
  window_type: string;
  created_at: string;
}
```
