"""DTN network node model for the AETHERIX architecture."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class NodeType(Enum):
    GROUND_STATION = "ground_station"
    GEO_RELAY = "geo_relay"
    LEO_SATELLITE = "leo_satellite"
    LAGRANGE_RELAY = "lagrange_relay"
    AREO_RELAY = "areo_relay"
    SURFACE_NODE = "surface_node"


class NodeStatus(Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


@dataclass
class NodeCapabilities:
    max_buffer_gb: float
    supported_bands: List[str]
    optical_capable: bool
    rf_capable: bool
    qkd_capable: bool
    max_data_rate_mbps: float
    processing_power_mips: float


@dataclass
class DTNNode:
    node_id: str
    node_type: NodeType
    tier: int
    capabilities: NodeCapabilities
    status: NodeStatus = NodeStatus.ACTIVE
    current_buffer_gb: float = 0.0
    connected_neighbors: List[str] = field(default_factory=list)
    last_contact_time: Optional[float] = None
    total_bundles_forwarded: int = 0
    total_bundles_stored: int = 0

    def buffer_utilization(self) -> float:
        if self.capabilities.max_buffer_gb <= 0:
            return 0.0
        return min(self.current_buffer_gb / self.capabilities.max_buffer_gb, 1.0)

    def can_accept_bundle(self, size_mb: float) -> bool:
        size_gb = size_mb / 1024.0
        remaining_gb = self.capabilities.max_buffer_gb - self.current_buffer_gb
        return self.is_reachable() and remaining_gb >= size_gb

    def store_bundle(self, size_mb: float) -> bool:
        if not self.can_accept_bundle(size_mb):
            return False
        self.current_buffer_gb += size_mb / 1024.0
        self.total_bundles_stored += 1
        return True

    def forward_bundle(self, size_mb: float) -> None:
        self.total_bundles_forwarded += 1

    def is_reachable(self) -> bool:
        return self.status in (NodeStatus.ACTIVE, NodeStatus.DEGRADED)


NETWORK_TIER_NAMES: dict[int, str] = {
    1: "Earth Ground",
    2: "Earth Orbital",
    3: "Deep Space Transit",
    4: "Mars Orbital",
    5: "Mars Surface",
}


def create_dsn_station(station_name: str) -> DTNNode:
    return DTNNode(
        node_id=f"dsn_{station_name.lower()}",
        node_type=NodeType.GROUND_STATION,
        tier=1,
        capabilities=NodeCapabilities(
            max_buffer_gb=10240.0,
            supported_bands=["S-band", "X-band", "Ka-band", "optical"],
            optical_capable=True,
            rf_capable=True,
            qkd_capable=False,
            max_data_rate_mbps=200.0,
            processing_power_mips=50000.0,
        ),
    )


def create_lagrange_relay(name: str) -> DTNNode:
    return DTNNode(
        node_id=f"lagrange_{name.lower()}",
        node_type=NodeType.LAGRANGE_RELAY,
        tier=3,
        capabilities=NodeCapabilities(
            max_buffer_gb=5120.0,
            supported_bands=["X-band", "Ka-band", "optical"],
            optical_capable=True,
            rf_capable=True,
            qkd_capable=True,
            max_data_rate_mbps=150.0,
            processing_power_mips=30000.0,
        ),
    )
