const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || res.statusText);
  }
  return res.json();
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  uptime_seconds: number;
}

export interface SimulationRun {
  id: string;
  name: string;
  scenario: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  result: Record<string, unknown> | null;
  seed: number | null;
}

export interface LinkBudgetResult {
  id: string;
  link_type: string;
  scenario: string;
  distance_km: number;
  free_space_loss_db: number;
  eirp_dbm: number;
  received_power_dbm: number;
  link_margin_db: number;
  data_rate_mbps: number;
  created_at: string;
}

export interface RoutingDecision {
  action: string;
  next_hop: string | null;
  confidence: number;
  reasoning: string;
}

export interface QKDResult {
  id: string;
  protocol: string;
  num_qubits: number;
  channel_error: number;
  eavesdropper: boolean;
  qber: number | null;
  secure: boolean | null;
  sifted_key_length: number | null;
  efficiency: number | null;
  alice_key: number[] | null;
  bob_key: number[] | null;
  created_at: string;
}

export interface DistancePoint {
  day: number;
  distance_km: number;
  light_time_min: number;
}

export interface DistanceTimeline {
  distances: DistancePoint[];
  min_distance_km: number;
  max_distance_km: number;
  avg_distance_km: number;
}

export interface ContactWindow {
  id: string;
  start_time_jd: number;
  end_time_jd: number;
  duration_hours: number;
  max_elevation_deg: number;
  average_distance_km: number;
  max_data_rate_mbps: number;
  window_type: string;
  created_at: string;
}

export const api = {
  health: () => fetchApi<HealthResponse>("/health"),

  listSimulations: () => fetchApi<SimulationRun[]>("/simulations/"),
  createSimulation: (data: { name: string; scenario: string; seed?: number }) =>
    fetchApi<SimulationRun>("/simulations/", { method: "POST", body: JSON.stringify(data) }),
  deleteSimulation: (id: string) =>
    fetchApi<void>(`/simulations/${id}`, { method: "DELETE" }),

  opticalLinkBudget: (data: { scenario?: string; distance_km?: number }) =>
    fetchApi<LinkBudgetResult>("/link-budget/optical", { method: "POST", body: JSON.stringify(data) }),
  rfLinkBudget: (band: string, data: { scenario?: string; distance_km?: number }) =>
    fetchApi<LinkBudgetResult>(`/link-budget/rf/${band}`, { method: "POST", body: JSON.stringify(data) }),
  linkBudgetHistory: () => fetchApi<LinkBudgetResult[]>("/link-budget/history"),

  routingDecide: (data: {
    current_node: string;
    neighbors: string[];
    link_qualities: Record<string, number>;
    buffer_occupancy: number;
    bundle_priority: number;
    bundle_size_mb: number;
    bundle_deadline_hours: number;
    destination_node: string;
  }) => fetchApi<RoutingDecision>("/routing/decide", { method: "POST", body: JSON.stringify(data) }),
  routingDecisions: () => fetchApi<Record<string, unknown>[]>("/routing/decisions"),

  distance: (anomaly?: number) =>
    fetchApi<{ true_anomaly_deg: number; distance_km: number; light_time_seconds: number; light_time_minutes: number }>(
      `/orbital/distance?true_anomaly_deg=${anomaly ?? 0}`
    ),
  timeline: () => fetchApi<DistanceTimeline>("/orbital/timeline"),
  contactWindows: (data: { duration_days?: number; min_elevation_deg?: number }) =>
    fetchApi<ContactWindow[]>("/orbital/contact-windows", { method: "POST", body: JSON.stringify(data) }),

  runQKD: (data: { protocol?: string; num_qubits?: number; channel_error?: number; eavesdropper?: boolean }) =>
    fetchApi<QKDResult>("/security/qkd", { method: "POST", body: JSON.stringify(data) }),
  qkdSessions: () => fetchApi<QKDResult[]>("/security/qkd/sessions"),
};
