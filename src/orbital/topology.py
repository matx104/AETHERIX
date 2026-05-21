"""AETHERIX 5-tier DTN network topology — all nodes and inter-tier links.

Tiers:
    1 — Earth Ground (DSN stations, control centres)
    2 — Earth Orbital (GEO relays, LEO laser constellation)
    3 — Deep Space Transit (Lagrange relays, transfer-orbit relays)
    4 — Mars Orbital (areostationary, polar, orbiter)
    5 — Mars Surface (bases, rovers, drones, sensor mesh)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from routing.contact_graph import Contact, ContactGraph, ContactState
from routing.node import DTNNode, NodeCapabilities, NodeStatus, NodeType


@dataclass
class InterTierLink:
    link_id: str
    source_tier: int
    dest_tier: int
    link_type: str
    data_rate_mbps: float
    latency_seconds: float
    availability: float

    def __post_init__(self) -> None:
        if self.link_type not in ("optical", "rf", "hybrid"):
            raise ValueError(f"Invalid link_type '{self.link_type}'")
        if not 0.0 <= self.availability <= 1.0:
            raise ValueError(f"availability must be in [0, 1], got {self.availability}")


_DSN_CAPS = NodeCapabilities(
    max_buffer_gb=10240.0,
    supported_bands=["S-band", "X-band", "Ka-band", "optical"],
    optical_capable=True,
    rf_capable=True,
    qkd_capable=False,
    max_data_rate_mbps=200.0,
    processing_power_mips=50000.0,
)

_GEO_CAPS = NodeCapabilities(
    max_buffer_gb=5120.0,
    supported_bands=["Ka-band", "optical"],
    optical_capable=True,
    rf_capable=True,
    qkd_capable=False,
    max_data_rate_mbps=150.0,
    processing_power_mips=30000.0,
)

_LEO_CAPS = NodeCapabilities(
    max_buffer_gb=1024.0,
    supported_bands=["optical"],
    optical_capable=True,
    rf_capable=False,
    qkd_capable=False,
    max_data_rate_mbps=100.0,
    processing_power_mips=10000.0,
)

_LAGRANGE_CAPS = NodeCapabilities(
    max_buffer_gb=5120.0,
    supported_bands=["Ka-band", "optical"],
    optical_capable=True,
    rf_capable=True,
    qkd_capable=True,
    max_data_rate_mbps=150.0,
    processing_power_mips=30000.0,
)

_AREO_CAPS = NodeCapabilities(
    max_buffer_gb=2048.0,
    supported_bands=["UHF", "Ka-band", "optical"],
    optical_capable=True,
    rf_capable=True,
    qkd_capable=True,
    max_data_rate_mbps=100.0,
    processing_power_mips=20000.0,
)

_BASE_CAPS = NodeCapabilities(
    max_buffer_gb=2048.0,
    supported_bands=["UHF", "X-band"],
    optical_capable=False,
    rf_capable=True,
    qkd_capable=False,
    max_data_rate_mbps=10.0,
    processing_power_mips=20000.0,
)

_ROVER_CAPS = NodeCapabilities(
    max_buffer_gb=100.0,
    supported_bands=["UHF"],
    optical_capable=False,
    rf_capable=True,
    qkd_capable=False,
    max_data_rate_mbps=2.0,
    processing_power_mips=5000.0,
)

_DRONE_CAPS = NodeCapabilities(
    max_buffer_gb=50.0,
    supported_bands=["UHF"],
    optical_capable=False,
    rf_capable=True,
    qkd_capable=False,
    max_data_rate_mbps=5.0,
    processing_power_mips=3000.0,
)

_SENSOR_CAPS = NodeCapabilities(
    max_buffer_gb=10.0,
    supported_bands=["UHF"],
    optical_capable=False,
    rf_capable=True,
    qkd_capable=False,
    max_data_rate_mbps=0.5,
    processing_power_mips=500.0,
)


class NetworkTopology:
    """Complete AETHERIX 5-tier delay-tolerant network topology."""

    def __init__(self) -> None:
        self._nodes: Dict[str, DTNNode] = {}
        self._contact_graph: Optional[ContactGraph] = None
        self._inter_tier_links: List[InterTierLink] = []
        self._adjacency: Dict[str, Set[str]] = {}

    def register_node(self, node: DTNNode) -> None:
        self._nodes[node.node_id] = node
        self._adjacency.setdefault(node.node_id, set())

    def get_node(self, node_id: str) -> Optional[DTNNode]:
        return self._nodes.get(node_id)

    def get_nodes_by_tier(self, tier: int) -> List[DTNNode]:
        return [n for n in self._nodes.values() if n.tier == tier]

    def get_nodes_by_type(self, node_type: NodeType) -> List[DTNNode]:
        return [n for n in self._nodes.values() if n.node_type == node_type]

    def add_inter_tier_link(self, link: InterTierLink) -> None:
        self._inter_tier_links.append(link)

    def _link(self, a: str, b: str) -> None:
        self._adjacency.setdefault(a, set()).add(b)
        self._adjacency.setdefault(b, set()).add(a)

    def get_inter_tier_links(self) -> List[InterTierLink]:
        return list(self._inter_tier_links)

    def build_inter_tier_links(self) -> None:
        seq = 0

        def _lid(prefix: str) -> str:
            nonlocal seq
            lid = f"{prefix}-{seq:04d}"
            seq += 1
            return lid

        dsn_ids = [n.node_id for n in self.get_nodes_by_type(NodeType.GROUND_STATION)]
        geo_ids = [n.node_id for n in self.get_nodes_by_type(NodeType.GEO_RELAY)]
        leo_ids = [n.node_id for n in self.get_nodes_by_type(NodeType.LEO_SATELLITE)]
        lag_ids = [n.node_id for n in self.get_nodes_by_type(NodeType.LAGRANGE_RELAY)]
        areo_ids = [n.node_id for n in self.get_nodes_by_type(NodeType.AREO_RELAY)]
        base_ids = [n.node_id for n in self.get_nodes_by_tier(5)
                     if n.node_id.startswith("base-")]
        rover_ids = [n.node_id for n in self.get_nodes_by_tier(5)
                      if n.node_id.startswith("rover-")]
        drone_ids = [n.node_id for n in self.get_nodes_by_tier(5)
                      if n.node_id.startswith("drone-")]
        sensor_ids = [n.node_id for n in self.get_nodes_by_tier(5)
                       if n.node_id.startswith("sensor-")]

        for dsn in dsn_ids:
            for geo in geo_ids:
                self.add_inter_tier_link(InterTierLink(
                    link_id=_lid("l12"), source_tier=1, dest_tier=2,
                    link_type="rf", data_rate_mbps=10.0,
                    latency_seconds=0.01, availability=0.995,
                ))
                self._link(dsn, geo)

        for geo in geo_ids:
            for lag in lag_ids:
                self.add_inter_tier_link(InterTierLink(
                    link_id=_lid("l23"), source_tier=2, dest_tier=3,
                    link_type="optical", data_rate_mbps=100.0,
                    latency_seconds=1.0, availability=0.97,
                ))
                self._link(geo, lag)

        for leo in leo_ids[::12]:
            for lag in lag_ids:
                self.add_inter_tier_link(InterTierLink(
                    link_id=_lid("l23"), source_tier=2, dest_tier=3,
                    link_type="optical", data_rate_mbps=80.0,
                    latency_seconds=1.2, availability=0.92,
                ))
                self._link(leo, lag)

        for lag in lag_ids:
            for areo in areo_ids:
                self.add_inter_tier_link(InterTierLink(
                    link_id=_lid("l34"), source_tier=3, dest_tier=4,
                    link_type="optical", data_rate_mbps=50.0,
                    latency_seconds=600.0, availability=0.90,
                ))
                self._link(lag, areo)

        mars_orbital = areo_ids
        for mo in mars_orbital:
            for base in base_ids:
                self.add_inter_tier_link(InterTierLink(
                    link_id=_lid("l45"), source_tier=4, dest_tier=5,
                    link_type="rf", data_rate_mbps=2.0,
                    latency_seconds=0.001, availability=0.98,
                ))
                self._link(mo, base)

        self._link(geo_ids[0], geo_ids[1])
        self._link(geo_ids[1], geo_ids[2])
        self._link(geo_ids[2], geo_ids[0])

        for i in range(len(leo_ids)):
            self._link(leo_ids[i], leo_ids[(i + 1) % len(leo_ids)])

        for i in range(len(lag_ids)):
            for j in range(i + 1, len(lag_ids)):
                self._link(lag_ids[i], lag_ids[j])

        for i in range(len(mars_orbital)):
            for j in range(i + 1, len(mars_orbital)):
                self._link(mars_orbital[i], mars_orbital[j])

        self._link(base_ids[0], base_ids[1])
        for i, rover in enumerate(rover_ids):
            self._link(base_ids[i % len(base_ids)], rover)
        for i, drone in enumerate(drone_ids):
            self._link(base_ids[i % len(base_ids)], drone)
        for i, sensor in enumerate(sensor_ids):
            self._link(drone_ids[i % len(drone_ids)], sensor)

    def get_contact_graph(self) -> ContactGraph:
        graph = ContactGraph()
        cid = 0
        seen: Set[frozenset] = set()

        for node_a, neighbors in self._adjacency.items():
            for node_b in neighbors:
                pair = frozenset((node_a, node_b))
                if pair in seen:
                    continue
                seen.add(pair)
                a_node = self._nodes[node_a]
                rate = self._link_rate(a_node, self._nodes[node_b])
                graph.add_contact(Contact(
                    contact_id=f"ct-{cid:06d}",
                    source_node=node_a,
                    dest_node=node_b,
                    start_time=0.0,
                    end_time=float("inf"),
                    data_rate_mbps=rate,
                    delay_seconds=self._link_delay(a_node, self._nodes[node_b]),
                ))
                graph.add_contact(Contact(
                    contact_id=f"ct-{cid + 1:06d}",
                    source_node=node_b,
                    dest_node=node_a,
                    start_time=0.0,
                    end_time=float("inf"),
                    data_rate_mbps=rate,
                    delay_seconds=self._link_delay(self._nodes[node_b], a_node),
                ))
                cid += 2

        self._contact_graph = graph
        return graph

    def _link_rate(self, a: DTNNode, b: DTNNode) -> float:
        if a.tier != b.tier:
            lo, hi = min(a.tier, b.tier), max(a.tier, b.tier)
            for link in self._inter_tier_links:
                if link.source_tier == lo and link.dest_tier == hi:
                    return link.data_rate_mbps
        return min(a.capabilities.max_data_rate_mbps, b.capabilities.max_data_rate_mbps)

    def _link_delay(self, a: DTNNode, b: DTNNode) -> float:
        if a.tier != b.tier:
            lo, hi = min(a.tier, b.tier), max(a.tier, b.tier)
            for link in self._inter_tier_links:
                if link.source_tier == lo and link.dest_tier == hi:
                    return link.latency_seconds
        return 0.001

    def get_node_count(self) -> int:
        return len(self._nodes)

    def get_tier_summary(self) -> Dict[int, int]:
        summary: Dict[int, int] = {}
        for node in self._nodes.values():
            summary[node.tier] = summary.get(node.tier, 0) + 1
        return dict(sorted(summary.items()))

    def find_route(self, source_id: str, dest_id: str) -> List[str]:
        if source_id not in self._nodes or dest_id not in self._nodes:
            return []
        if source_id == dest_id:
            return [source_id]

        visited: Set[str] = {source_id}
        queue: deque = deque([(source_id, [source_id])])

        while queue:
            current, path = queue.popleft()
            for neighbor in self._adjacency.get(current, set()):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                new_path = path + [neighbor]
                if neighbor == dest_id:
                    return new_path
                queue.append((neighbor, new_path))

        return []

    def get_neighbors(self, node_id: str) -> Set[str]:
        return self._adjacency.get(node_id, set())

    def build_default_topology(self) -> None:
        self._build_tier1()
        self._build_tier2()
        self._build_tier3()
        self._build_tier4()
        self._build_tier5()

    def _build_tier1(self) -> None:
        for node_id in ("dsn-goldstone", "dsn-madrid", "dsn-canberra"):
            self.register_node(DTNNode(
                node_id=node_id,
                node_type=NodeType.GROUND_STATION,
                tier=1,
                capabilities=_DSN_CAPS,
            ))

        for node_id in ("earth-moc", "earth-soc"):
            caps = NodeCapabilities(
                max_buffer_gb=10240.0,
                supported_bands=["X-band", "Ka-band"],
                optical_capable=False,
                rf_capable=True,
                qkd_capable=False,
                max_data_rate_mbps=200.0,
                processing_power_mips=50000.0,
            )
            self.register_node(DTNNode(
                node_id=node_id,
                node_type=NodeType.GROUND_STATION,
                tier=1,
                capabilities=caps,
            ))

    def _build_tier2(self) -> None:
        for node_id in ("geo-atlantic", "geo-pacific", "geo-indian"):
            self.register_node(DTNNode(
                node_id=node_id,
                node_type=NodeType.GEO_RELAY,
                tier=2,
                capabilities=_GEO_CAPS,
            ))

        for i in range(1, 49):
            self.register_node(DTNNode(
                node_id=f"leo-{i:02d}",
                node_type=NodeType.LEO_SATELLITE,
                tier=2,
                capabilities=_LEO_CAPS,
            ))

    def _build_tier3(self) -> None:
        for node_id in ("es-l4", "es-l5"):
            self.register_node(DTNNode(
                node_id=node_id,
                node_type=NodeType.LAGRANGE_RELAY,
                tier=3,
                capabilities=_LAGRANGE_CAPS,
            ))

        for i in range(1, 3):
            self.register_node(DTNNode(
                node_id=f"transfer-{i:02d}",
                node_type=NodeType.LAGRANGE_RELAY,
                tier=3,
                capabilities=_LAGRANGE_CAPS,
            ))

    def _build_tier4(self) -> None:
        for node_id in ("areo-alpha", "areo-beta"):
            self.register_node(DTNNode(
                node_id=node_id,
                node_type=NodeType.AREO_RELAY,
                tier=4,
                capabilities=_AREO_CAPS,
            ))

        self.register_node(DTNNode(
            node_id="polar-gamma",
            node_type=NodeType.AREO_RELAY,
            tier=4,
            capabilities=_AREO_CAPS,
        ))

        self.register_node(DTNNode(
            node_id="mars-orbiter",
            node_type=NodeType.AREO_RELAY,
            tier=4,
            capabilities=_AREO_CAPS,
        ))

    def _build_tier5(self) -> None:
        for node_id in ("base-jezero", "base-oxia"):
            self.register_node(DTNNode(
                node_id=node_id,
                node_type=NodeType.SURFACE_NODE,
                tier=5,
                capabilities=_BASE_CAPS,
            ))

        for i in range(1, 6):
            self.register_node(DTNNode(
                node_id=f"rover-{i:02d}",
                node_type=NodeType.SURFACE_NODE,
                tier=5,
                capabilities=_ROVER_CAPS,
            ))

        for i in range(1, 11):
            self.register_node(DTNNode(
                node_id=f"drone-{i:02d}",
                node_type=NodeType.SURFACE_NODE,
                tier=5,
                capabilities=_DRONE_CAPS,
            ))

        for i in range(1, 161):
            self.register_node(DTNNode(
                node_id=f"sensor-{i:03d}",
                node_type=NodeType.SURFACE_NODE,
                tier=5,
                capabilities=_SENSOR_CAPS,
            ))


def create_default_topology() -> NetworkTopology:
    topology = NetworkTopology()
    topology.build_default_topology()
    topology.build_inter_tier_links()
    return topology
