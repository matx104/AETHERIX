import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)


class LinkBudgetResult(Base):
    __tablename__ = "link_budget_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    simulation_run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("simulation_runs.id"), nullable=True, index=True
    )
    link_type: Mapped[str] = mapped_column(String(20), nullable=False)
    scenario: Mapped[str] = mapped_column(String(50), nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    free_space_loss_db: Mapped[float] = mapped_column(Float, nullable=False)
    eirp_dbm: Mapped[float] = mapped_column(Float, nullable=False)
    received_power_dbm: Mapped[float] = mapped_column(Float, nullable=False)
    link_margin_db: Mapped[float] = mapped_column(Float, nullable=False)
    data_rate_mbps: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class RoutingDecisionLog(Base):
    __tablename__ = "routing_decision_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    simulation_run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("simulation_runs.id"), nullable=True, index=True
    )
    current_node: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    next_hop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    reward: Mapped[float] = mapped_column(Float, default=0.0)
    bundle_priority: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class QKDSession(Base):
    __tablename__ = "qkd_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    protocol: Mapped[str] = mapped_column(String(10), nullable=False)
    num_qubits: Mapped[int] = mapped_column(Integer, nullable=False)
    channel_error: Mapped[float] = mapped_column(Float, default=0.0)
    eavesdropper: Mapped[bool] = mapped_column(Boolean, default=False)
    qber: Mapped[float] = mapped_column(Float, nullable=True)
    secure: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    sifted_key_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    efficiency: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ContactWindowRecord(Base):
    __tablename__ = "contact_window_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    simulation_run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("simulation_runs.id"), nullable=True, index=True
    )
    start_time_jd: Mapped[float] = mapped_column(Float, nullable=False)
    end_time_jd: Mapped[float] = mapped_column(Float, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    max_elevation_deg: Mapped[float] = mapped_column(Float, nullable=False)
    average_distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    max_data_rate_mbps: Mapped[float] = mapped_column(Float, nullable=False)
    window_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
