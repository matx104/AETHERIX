from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SimulationRunCreate(BaseModel):
    name: str
    scenario: str
    config: dict[str, Any] | None = None
    seed: int | None = None


class SimulationRunResponse(BaseModel):
    id: str
    name: str
    scenario: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    result: dict[str, Any] | None = None
    seed: int | None = None

    model_config = {"from_attributes": True}


class LinkBudgetRequest(BaseModel):
    distance_km: float | None = None
    scenario: str = "average"
    tx_power_dbm: float | None = None
    tx_gain_db: float | None = None
    data_rate_mbps: float | None = None


class LinkBudgetResponse(BaseModel):
    id: str
    link_type: str
    scenario: str
    distance_km: float
    free_space_loss_db: float
    eirp_dbm: float
    received_power_dbm: float
    link_margin_db: float
    data_rate_mbps: float
    created_at: datetime

    model_config = {"from_attributes": True}


class RoutingRequest(BaseModel):
    current_node: str
    neighbors: list[str]
    link_qualities: dict[str, float]
    buffer_occupancy: float = Field(ge=0.0, le=1.0)
    bundle_priority: int = Field(ge=0, le=4)
    bundle_size_mb: float
    bundle_deadline_hours: float
    destination_node: str


class RoutingResponse(BaseModel):
    action: str
    next_hop: str | None = None
    confidence: float
    reasoning: str


class QKDRequest(BaseModel):
    protocol: str = "bb84"
    num_qubits: int = Field(default=1000, ge=1, le=100000)
    channel_error: float = Field(default=0.0, ge=0.0, le=1.0)
    eavesdropper: bool = False


class QKDResponse(BaseModel):
    id: str
    protocol: str
    num_qubits: int
    channel_error: float
    eavesdropper: bool
    qber: float | None = None
    secure: bool | None = None
    sifted_key_length: int | None = None
    efficiency: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactWindowRequest(BaseModel):
    start_date: str | None = None
    duration_days: float = Field(default=365.0, ge=1, le=3650)
    min_elevation_deg: float = Field(default=10.0, ge=0.0, le=90.0)
    window_type: str = "all"


class ContactWindowResponse(BaseModel):
    id: str
    start_time_jd: float
    end_time_jd: float
    duration_hours: float
    max_elevation_deg: float
    average_distance_km: float
    max_data_rate_mbps: float
    window_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DistanceTimelineResponse(BaseModel):
    distances: list[dict[str, Any]]
    min_distance_km: float
    max_distance_km: float
    avg_distance_km: float


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    uptime_seconds: float
