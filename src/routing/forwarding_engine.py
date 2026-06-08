"""
AETHERIX Store-and-Forward Engine
Core runtime that wires bundles, nodes, routing decisions, and
convergence layers into a single DTN forwarding plane.

Reference: RFC 9171 (Bundle Protocol v7), CCSDS 734.2-B-1
"""

import time
from bisect import insort
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from routing.bundle import Bundle, BundlePriority, EndpointID
from routing.contact_graph import Contact, ContactGraph
from routing.node import DTNNode, NodeCapabilities, NodeStatus, NodeType
from routing.rl_agent import (NetworkState, RLRoutingAgent, RoutingAction,
                              RoutingDecision)


@dataclass
class ForwardingEvent:
    """
    Immutable record of a single forwarding-plane event.

    Event types:
        received           – bundle arrived at this node
        forwarded          – bundle sent to next hop
        stored             – bundle buffered for later transmission
        dropped            – bundle discarded (expired, buffer full, etc.)
        delivered          – bundle reached its final destination
        expired            – bundle lifetime exceeded before delivery
        custody_accepted   – node took custody per RFC 9171 §4.5
        custody_released   – node released custody after successful forward
    """
    timestamp: float
    bundle_id: str
    event_type: str
    source_node: str
    dest_node: str
    next_hop: str = ""
    details: str = ""


@dataclass
class BundleQueue:
    """
    Priority-sorted bundle queue.

    Bundles are ordered first by priority (EMERGENCY → BULK) and then
    by remaining lifetime so that the most urgent, soonest-expiring
    bundle is always at the head of the queue.
    """

    bundles: List[Bundle] = field(default_factory=list)

    def _sort_key(self, bundle: Bundle) -> tuple:
        return (bundle.priority.value, bundle.creation_time + bundle.lifetime_seconds)

    def enqueue(self, bundle: Bundle) -> None:
        """
        Insert *bundle* into the queue in priority / deadline order.

        Ordering: lowest ``BundlePriority`` value first (EMERGENCY = 0),
        then earliest absolute deadline.
        """
        insort(self.bundles, bundle, key=self._sort_key)

    def dequeue(self) -> Optional[Bundle]:
        """Remove and return the highest-priority bundle, or ``None``."""
        if self.bundles:
            return self.bundles.pop(0)
        return None

    def peek(self) -> Optional[Bundle]:
        """Return the highest-priority bundle without removing it."""
        if self.bundles:
            return self.bundles[0]
        return None

    def remove_expired(self) -> int:
        """
        Purge all expired bundles from the queue.

        Returns:
            Number of bundles removed.
        """
        before = len(self.bundles)
        self.bundles = [b for b in self.bundles if not b.is_expired]
        return before - len(self.bundles)

    def get_size(self) -> int:
        return len(self.bundles)

    def get_size_mb(self) -> float:
        return sum(b.payload_size_bytes for b in self.bundles) / (1024.0 * 1024.0)


class ForwardingEngine:
    """
    DTN store-and-forward engine.

    Each engine instance is bound to a single local node.  It owns a
    priority queue, consults the RL routing agent for every dequeue
    cycle, and emits ``ForwardingEvent`` records for telemetry and
    auditing.
    """

    _VALID_EVENT_TYPES = frozenset({
        "received", "forwarded", "stored", "dropped",
        "delivered", "expired", "custody_accepted", "custody_released",
    })

    def __init__(
        self,
        local_node: DTNNode,
        routing_agent: RLRoutingAgent,
        contact_graph: Optional[ContactGraph] = None,
    ) -> None:
        self.local_node = local_node
        self.routing_agent = routing_agent
        self.contact_graph = contact_graph
        self.queue = BundleQueue()
        self._history: Dict[str, List[ForwardingEvent]] = {}
        self._custody_bundles: Dict[str, Bundle] = {}

    def _record(self, event: ForwardingEvent) -> None:
        self._history.setdefault(event.bundle_id, []).append(event)

    def _make_event(
        self,
        bundle: Bundle,
        event_type: str,
        next_hop: str = "",
        details: str = "",
    ) -> ForwardingEvent:
        return ForwardingEvent(
            timestamp=time.time(),
            bundle_id=bundle.bundle_id,
            event_type=event_type,
            source_node=bundle.source.node_id,
            dest_node=bundle.destination.node_id,
            next_hop=next_hop,
            details=details,
        )

    def receive_bundle(self, bundle: Bundle, from_node: str) -> ForwardingEvent:
        """
        Accept a bundle into the local queue.

        If this node is the final destination the bundle is marked
        *delivered* and **not** enqueued.
        """
        bundle.add_hop(self.local_node.node_id, "RECEIVED")

        if self._is_destination(bundle):
            event = self._make_event(bundle, "delivered", details="Final destination reached")
            self._record(event)
            self.local_node.forward_bundle(bundle.payload_size_bytes / (1024.0 * 1024.0))
            return event

        self.queue.enqueue(bundle)
        event = self._make_event(bundle, "received", details=f"Accepted from {from_node}")
        self._record(event)
        return event

    def process_queue(self, neighbors: Dict[str, DTNNode]) -> List[ForwardingEvent]:
        """
        Drain the queue: for every bundle build a ``NetworkState``,
        query the routing agent, and execute the chosen action.
        """
        events: List[ForwardingEvent] = []

        while self.queue.get_size() > 0:
            bundle = self.queue.peek()
            if bundle is None:
                break

            if bundle.is_expired:
                self.queue.dequeue()
                event = self._make_event(bundle, "expired", details="Lifetime exceeded")
                self._record(event)
                events.append(event)
                continue

            bundle = self.queue.dequeue()
            if bundle is None:
                break

            state = self._build_network_state(bundle, neighbors)
            decision = self.routing_agent.select_action(state)
            event = self._execute_decision(bundle, decision, neighbors)
            self._record(event)
            events.append(event)

        return events

    def _build_network_state(
        self, bundle: Bundle, neighbors: Dict[str, DTNNode]
    ) -> NetworkState:
        neighbor_ids = list(neighbors.keys())
        link_qualities: Dict[str, float] = {}
        for nid, node in neighbors.items():
            if node.is_reachable():
                quality = 1.0 - node.buffer_utilization()
                link_qualities[nid] = round(max(0.0, min(1.0, quality)), 3)

        return NetworkState(
            current_node=self.local_node.node_id,
            neighbors=neighbor_ids,
            link_qualities=link_qualities,
            buffer_occupancy=self.local_node.buffer_utilization(),
            bundle_priority=bundle.priority.value,
            bundle_size_mb=bundle.payload_size_bytes / (1024.0 * 1024.0),
            bundle_deadline_hours=bundle.remaining_lifetime / 3600.0,
            destination_node=bundle.destination.node_id,
        )

    def _execute_decision(
        self,
        bundle: Bundle,
        decision: RoutingDecision,
        neighbors: Dict[str, DTNNode],
    ) -> ForwardingEvent:
        action = decision.action

        if action == RoutingAction.FORWARD:
            next_hop = decision.next_hop or ""
            neighbor = neighbors.get(next_hop)
            if neighbor is None:
                return self._execute_drop(bundle, details=f"Unknown next hop: {next_hop}")
            return self._execute_forward(bundle, next_hop, neighbor)

        if action == RoutingAction.STORE:
            return self._execute_store(bundle)

        if action == RoutingAction.DROP:
            return self._execute_drop(bundle, details=decision.reasoning)

        if action == RoutingAction.SPLIT:
            return self._execute_store(bundle)

        return self._execute_drop(bundle, details=f"Unsupported action: {action}")

    def _execute_forward(
        self, bundle: Bundle, next_hop: str, neighbor: DTNNode
    ) -> ForwardingEvent:
        size_mb = bundle.payload_size_bytes / (1024.0 * 1024.0)

        if not neighbor.can_accept_bundle(size_mb):
            self.queue.enqueue(bundle)
            return self._make_event(
                bundle, "stored",
                details=f"Neighbor {next_hop} buffer full, re-queued",
            )

        if not neighbor.is_reachable():
            self.queue.enqueue(bundle)
            return self._make_event(
                bundle, "stored",
                details=f"Neighbor {next_hop} unreachable, re-queued",
            )

        neighbor.store_bundle(size_mb)
        self.local_node.forward_bundle(size_mb)
        bundle.add_hop(self.local_node.node_id, "FORWARDED", time.time())

        if bundle.bundle_id in self._custody_bundles:
            self.release_custody(bundle, next_hop)

        return self._make_event(
            bundle, "forwarded", next_hop=next_hop,
            details=f"Forwarded to {next_hop}",
        )

    def _execute_store(self, bundle: Bundle) -> ForwardingEvent:
        size_mb = bundle.payload_size_bytes / (1024.0 * 1024.0)
        stored = self.local_node.store_bundle(size_mb)

        if not stored:
            return self._execute_drop(
                bundle, details="Local buffer full, cannot store",
            )

        self.queue.enqueue(bundle)
        bundle.add_hop(self.local_node.node_id, "STORED", time.time())
        return self._make_event(bundle, "stored", details="Stored for deferred transmission")

    def _execute_drop(self, bundle: Bundle, details: str = "") -> ForwardingEvent:
        size_mb = bundle.payload_size_bytes / (1024.0 * 1024.0)
        size_gb = size_mb / 1024.0
        self.local_node.current_buffer_gb = max(0.0, self.local_node.current_buffer_gb - size_gb)

        bundle.add_hop(self.local_node.node_id, "DROPPED", time.time())
        return self._make_event(bundle, "dropped", details=details)

    def _is_destination(self, bundle: Bundle) -> bool:
        dest = bundle.destination.node_id
        local = self.local_node.node_id
        return dest == local

    def accept_custody(self, bundle: Bundle) -> ForwardingEvent:
        """
        Accept custodial responsibility for *bundle* (RFC 9171 §4.5).

        The bundle is retained in ``_custody_bundles`` so the engine
        can release custody automatically on the next successful
        forward.
        """
        bundle.accept_custody(self.local_node.node_id)
        self._custody_bundles[bundle.bundle_id] = bundle
        event = self._make_event(
            bundle, "custody_accepted",
            details=f"Custody accepted by {self.local_node.node_id}",
        )
        self._record(event)
        return event

    def release_custody(self, bundle: Bundle, next_hop: str) -> ForwardingEvent:
        """
        Release custodial responsibility after confirming *bundle*
        was forwarded to *next_hop*.
        """
        bundle.release_custody(self.local_node.node_id)
        self._custody_bundles.pop(bundle.bundle_id, None)
        event = self._make_event(
            bundle, "custody_released", next_hop=next_hop,
            details=f"Custody released to {next_hop}",
        )
        self._record(event)
        return event

    def get_queue_stats(self) -> Dict[str, int]:
        """
        Snapshot of queue occupancy grouped by priority tier.

        Returns:
            ``queue_size``, ``emergency_count``, ``standard_count``,
            ``bulk_count``.
        """
        emergency = sum(
            1 for b in self.queue.bundles
            if b.priority in (BundlePriority.EMERGENCY, BundlePriority.HIGH_SCIENCE)
        )
        standard = sum(
            1 for b in self.queue.bundles
            if b.priority in (BundlePriority.STANDARD, BundlePriority.HOUSEKEEPING)
        )
        bulk = sum(
            1 for b in self.queue.bundles if b.priority == BundlePriority.BULK
        )
        return {
            "queue_size": self.queue.get_size(),
            "emergency_count": emergency,
            "standard_count": standard,
            "bulk_count": bulk,
        }

    def get_forwarding_history(self, bundle_id: str) -> List[ForwardingEvent]:
        """Return every ``ForwardingEvent`` recorded for *bundle_id*."""
        return list(self._history.get(bundle_id, []))

    def tick(
        self, current_time: float, neighbors: Dict[str, DTNNode]
    ) -> List[ForwardingEvent]:
        """
        Execute one engine time-step.

        Order of operations:
        1. Purge expired bundles from the queue.
        2. Drain the queue via the RL routing agent.

        Returns:
            All ``ForwardingEvent`` records produced this tick.
        """
        events: List[ForwardingEvent] = []

        expired_count = self.queue.remove_expired()
        if expired_count > 0:
            events.append(ForwardingEvent(
                timestamp=current_time,
                bundle_id="",
                event_type="expired",
                source_node=self.local_node.node_id,
                dest_node="",
                details=f"Purged {expired_count} expired bundle(s)",
            ))

        events.extend(self.process_queue(neighbors))
        return events


def _default_capabilities(node_type: NodeType) -> NodeCapabilities:
    """
    Sensible default capabilities per node type for demo / testing use.
    """
    defaults: Dict[NodeType, NodeCapabilities] = {
        NodeType.GROUND_STATION: NodeCapabilities(
            max_buffer_gb=10240.0,
            supported_bands=["S-band", "X-band", "Ka-band", "optical"],
            optical_capable=True,
            rf_capable=True,
            qkd_capable=False,
            max_data_rate_mbps=200.0,
            processing_power_mips=50000.0,
        ),
        NodeType.GEO_RELAY: NodeCapabilities(
            max_buffer_gb=8192.0,
            supported_bands=["Ka-band", "optical"],
            optical_capable=True,
            rf_capable=True,
            qkd_capable=True,
            max_data_rate_mbps=150.0,
            processing_power_mips=30000.0,
        ),
        NodeType.LEO_SATELLITE: NodeCapabilities(
            max_buffer_gb=512.0,
            supported_bands=["optical"],
            optical_capable=True,
            rf_capable=False,
            qkd_capable=False,
            max_data_rate_mbps=100.0,
            processing_power_mips=10000.0,
        ),
        NodeType.LAGRANGE_RELAY: NodeCapabilities(
            max_buffer_gb=5120.0,
            supported_bands=["X-band", "Ka-band", "optical"],
            optical_capable=True,
            rf_capable=True,
            qkd_capable=True,
            max_data_rate_mbps=150.0,
            processing_power_mips=30000.0,
        ),
        NodeType.AREO_RELAY: NodeCapabilities(
            max_buffer_gb=4096.0,
            supported_bands=["X-band", "Ka-band", "optical"],
            optical_capable=True,
            rf_capable=True,
            qkd_capable=True,
            max_data_rate_mbps=100.0,
            processing_power_mips=20000.0,
        ),
        NodeType.SURFACE_NODE: NodeCapabilities(
            max_buffer_gb=1024.0,
            supported_bands=["X-band", "UHF"],
            optical_capable=False,
            rf_capable=True,
            qkd_capable=False,
            max_data_rate_mbps=50.0,
            processing_power_mips=5000.0,
        ),
    }
    return defaults.get(node_type, NodeCapabilities(
        max_buffer_gb=2048.0,
        supported_bands=["X-band"],
        optical_capable=False,
        rf_capable=True,
        qkd_capable=False,
        max_data_rate_mbps=50.0,
        processing_power_mips=10000.0,
    ))


def create_forwarding_engine(
    node_id: str, tier: int, node_type: NodeType
) -> ForwardingEngine:
    """
    Factory that wires up a ``DTNNode``, ``RLRoutingAgent``, and
    ``ForwardingEngine`` ready for immediate use.

    Args:
        node_id: Unique node identifier (e.g. ``"mars.areo.alpha"``).
        tier: Network tier (1–5).
        node_type: The kind of node to create.

    Returns:
        A fully initialised ``ForwardingEngine``.
    """
    node = DTNNode(
        node_id=node_id,
        node_type=node_type,
        tier=tier,
        capabilities=_default_capabilities(node_type),
    )
    agent = RLRoutingAgent(node_id=node_id)
    return ForwardingEngine(local_node=node, routing_agent=agent)
