"""
AETHERIX Simulation Engine
Full DTN simulation framework for Earth-Mars communication.

Drives the 5-tier network topology, generates bundles, orchestrates
the per-node forwarding engines, and accumulates delivery metrics.
"""

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from orbital.topology import NetworkTopology, create_default_topology
from routing.bundle import (Bundle, BundlePriority, EndpointID,
                            create_science_bundle)
from routing.forwarding_engine import (ForwardingEngine, ForwardingEvent,
                                       create_forwarding_engine)
from routing.node import DTNNode, NodeCapabilities, NodeStatus, NodeType


class SimulationState(Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SimulationConfig:
    name: str = "earth-mars-baseline"
    duration_hours: float = 720.0
    time_step_seconds: float = 60.0
    seed: int = 42
    earth_mars_distance_km: float = 225e6
    num_nodes: int = 10
    optical_data_rate_mbps: float = 50.0
    rf_data_rate_mbps: float = 2.0
    bundle_generation_rate_per_hour: float = 10.0


@dataclass
class SimulationEvent:
    timestamp: float
    event_type: str
    source: str
    target: str
    data: Dict = field(default_factory=dict)


@dataclass
class SimulationResult:
    config: SimulationConfig
    total_bundles: int = 0
    delivered_bundles: int = 0
    dropped_bundles: int = 0
    stored_bundles: int = 0
    expired_bundles: int = 0
    forwarded_bundles: int = 0
    average_delay_seconds: float = 0.0
    average_hops: float = 0.0
    delivery_ratio: float = 0.0
    throughput_mb: float = 0.0
    events: List[SimulationEvent] = field(default_factory=list)
    per_priority_stats: Dict[str, Dict] = field(default_factory=dict)
    per_node_stats: Dict[str, Dict] = field(default_factory=dict)


class Simulator:
    """
    Full DTN simulation engine.

    Orchestrates the AETHERIX 5-tier network: builds the topology,
    seeds per-node forwarding engines, generates bundles from Mars-side
    sources, and steps the simulation clock collecting delivery metrics.
    """

    _SOURCE_TIERS = (4, 5)
    _DEST_TIERS = (1, 2)
    _PRIORITY_WEIGHTS = [0.05, 0.10, 0.50, 0.20, 0.15]
    _MIN_BUNDLE_SIZE_MB = 1.0
    _MAX_BUNDLE_SIZE_MB = 1000.0

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._state = SimulationState.INITIALIZED
        self._topology: Optional[NetworkTopology] = None
        self._engines: Dict[str, ForwardingEngine] = {}
        self._events: List[SimulationEvent] = []
        self._current_time: float = 0.0
        self._total_steps: int = 0
        self._completed_steps: int = 0
        self._bundles_generated: int = 0
        self._rng: random.Random = random.Random(config.seed)
        self._delivered_bundles: List[Tuple[Bundle, float]] = []
        self._dropped_bundles: List[Bundle] = []
        self._expired_bundles: List[Bundle] = []
        self._result: Optional[SimulationResult] = None

    def setup(self) -> None:
        """
        Build topology, create forwarding engines, seed RNG.

        Must be called before :meth:`run` or manual stepping.
        """
        self._topology = create_default_topology()
        self._engines.clear()

        for node_id, node in self._topology._nodes.items():
            engine = create_forwarding_engine(
                node_id=node.node_id,
                tier=node.tier,
                node_type=node.node_type,
            )
            self._engines[node_id] = engine

        self._rng = random.Random(self.config.seed)
        self._total_steps = int(
            (self.config.duration_hours * 3600.0) / self.config.time_step_seconds
        )
        self._completed_steps = 0
        self._current_time = 0.0
        self._events.clear()
        self._bundles_generated = 0
        self._delivered_bundles.clear()
        self._dropped_bundles.clear()
        self._expired_bundles.clear()
        self._state = SimulationState.INITIALIZED

    def generate_bundle(self, time_step: int) -> Optional[Bundle]:
        """
        Probabilistically generate a new bundle for this time step.

        Probability per step = ``bundle_generation_rate_per_hour *
        time_step_seconds / 3600``.  Source is chosen from tiers 4-5
        (Mars Orbital / Surface), destination from tiers 1-2 (Earth
        Ground / Orbital).  Priority is sampled from a weighted
        distribution favouring STANDARD; size is uniform 1-1000 MB.
        """
        prob = (
            self.config.bundle_generation_rate_per_hour
            * self.config.time_step_seconds
            / 3600.0
        )
        if self._rng.random() >= prob:
            return None

        source_nodes: List[DTNNode] = []
        dest_nodes: List[DTNNode] = []
        for node in self._topology._nodes.values():
            if node.tier in self._SOURCE_TIERS:
                source_nodes.append(node)
            if node.tier in self._DEST_TIERS:
                dest_nodes.append(node)

        if not source_nodes or not dest_nodes:
            return None

        source = self._rng.choice(source_nodes)
        dest = self._rng.choice(dest_nodes)
        priority = self._rng.choices(
            list(BundlePriority), weights=self._PRIORITY_WEIGHTS, k=1
        )[0]
        size_mb = self._rng.uniform(self._MIN_BUNDLE_SIZE_MB, self._MAX_BUNDLE_SIZE_MB)

        bundle = create_science_bundle(
            source_node=source.node_id,
            destination_node=dest.node_id,
            data_mb=size_mb,
            priority=priority,
        )
        bundle.creation_time = self._current_time
        self._bundles_generated += 1
        return bundle

    def inject_bundle(
        self, bundle: Bundle, source_node_id: str
    ) -> Optional[SimulationEvent]:
        """
        Deliver *bundle* to its source node's forwarding engine.

        Returns a :class:`SimulationEvent` or ``None`` if the source
        node has no engine (should not happen after :meth:`setup`).
        """
        engine = self._engines.get(source_node_id)
        if engine is None:
            return None

        fwd_event = engine.receive_bundle(bundle, "simulation_injector")

        sim_event = SimulationEvent(
            timestamp=self._current_time,
            event_type=fwd_event.event_type,
            source=source_node_id,
            target=fwd_event.dest_node,
            data={
                "bundle_id": bundle.bundle_id,
                "priority": bundle.priority.name,
                "size_mb": bundle.payload_size_bytes / (1024.0 * 1024.0),
                "next_hop": fwd_event.next_hop,
                "details": fwd_event.details,
            },
        )
        self._events.append(sim_event)
        return sim_event

    def step(self, current_time: float) -> List[SimulationEvent]:
        """
        Execute one simulation time step.

        1. Attempt to generate a new bundle.
        2. Inject any generated bundle into its source engine.
        3. For every engine, build a neighbour dict and call
           :meth:`ForwardingEngine.tick`.
        4. Convert forwarding events to simulation events and
           accumulate delivery / drop / expire statistics.
        """
        self._current_time = current_time
        step_events: List[SimulationEvent] = []

        bundle = self.generate_bundle(self._completed_steps)
        if bundle is not None:
            inject_event = self.inject_bundle(bundle, bundle.source.node_id)
            if inject_event is not None:
                step_events.append(inject_event)

                if inject_event.event_type == "delivered":
                    self._delivered_bundles.append((bundle, current_time))

        for node_id, engine in self._engines.items():
            neighbor_ids = self._topology.get_neighbors(node_id)
            neighbors: Dict[str, DTNNode] = {}
            for nid in neighbor_ids:
                node = self._topology.get_node(nid)
                if node is not None:
                    neighbors[nid] = node

            fwd_events = engine.tick(current_time, neighbors)

            for fwd_ev in fwd_events:
                sim_ev = SimulationEvent(
                    timestamp=current_time,
                    event_type=fwd_ev.event_type,
                    source=fwd_ev.source_node,
                    target=fwd_ev.dest_node,
                    data={
                        "bundle_id": fwd_ev.bundle_id,
                        "next_hop": fwd_ev.next_hop,
                        "details": fwd_ev.details,
                    },
                )
                step_events.append(sim_ev)
                self._events.append(sim_ev)

                self._accumulate_bundle_stats(fwd_ev, current_time)

        self._completed_steps += 1
        return step_events

    def _accumulate_bundle_stats(
        self, fwd_ev: ForwardingEvent, current_time: float
    ) -> None:
        """Track delivered / dropped / expired bundles from forwarding events."""
        if fwd_ev.event_type == "delivered":
            bundle = self._find_tracked_bundle(fwd_ev.bundle_id)
            if bundle is not None:
                self._delivered_bundles.append((bundle, current_time))

        elif fwd_ev.event_type == "dropped":
            bundle = self._find_tracked_bundle(fwd_ev.bundle_id)
            if bundle is not None:
                self._dropped_bundles.append(bundle)

        elif fwd_ev.event_type == "expired":
            pass

    def _find_tracked_bundle(self, bundle_id: str) -> Optional[Bundle]:
        for engine in self._engines.values():
            for b in engine.queue.bundles:
                if b.bundle_id == bundle_id:
                    return b
            history = engine.get_forwarding_history(bundle_id)
            if history:
                for b in engine.queue.bundles:
                    if b.bundle_id == bundle_id:
                        return b
        return None

    def run(self) -> SimulationResult:
        """
        Execute the full simulation loop.

        Calls :meth:`setup`, then steps from *t = 0* to *t = duration*
        in ``time_step_seconds`` increments.  Accumulates all events and
        computes final delivery metrics.
        """
        try:
            self.setup()
            self._state = SimulationState.RUNNING

            duration_s = self.config.duration_hours * 3600.0
            t = 0.0

            while t < duration_s:
                self.step(t)
                t += self.config.time_step_seconds

            self._state = SimulationState.COMPLETED
            self._result = self._build_result()

        except Exception as exc:
            self._state = SimulationState.FAILED
            self._result = SimulationResult(config=self.config)
            self._result.events = list(self._events)

        return self._result

    def _build_result(self) -> SimulationResult:
        total = self._bundles_generated
        delivered = len(self._delivered_bundles)
        dropped = len(self._dropped_bundles)
        expired = sum(
            1 for eng in self._engines.values()
            for ev in eng.get_forwarding_history("")
            if ev.event_type == "expired"
        )

        delays: List[float] = []
        hop_counts: List[int] = []
        throughput_bytes = 0

        for bundle, deliver_time in self._delivered_bundles:
            delay = deliver_time - bundle.creation_time
            if delay >= 0:
                delays.append(delay)
            hop_counts.append(len(bundle.hops))
            throughput_bytes += bundle.payload_size_bytes

        avg_delay = (sum(delays) / len(delays)) if delays else 0.0
        avg_hops = (sum(hop_counts) / len(hop_counts)) if hop_counts else 0.0
        delivery_ratio = (delivered / total) if total > 0 else 0.0
        throughput_mb = throughput_bytes / (1024.0 * 1024.0)

        per_priority: Dict[str, Dict] = {}
        for prio in BundlePriority:
            prio_delivered = [
                (b, t) for b, t in self._delivered_bundles
                if b.priority == prio
            ]
            prio_dropped = [
                b for b in self._dropped_bundles if b.priority == prio
            ]
            prio_delays = [
                t - b.creation_time for b, t in prio_delivered if t >= b.creation_time
            ]
            per_priority[prio.name] = {
                "delivered": len(prio_delivered),
                "dropped": len(prio_dropped),
                "avg_delay": (sum(prio_delays) / len(prio_delays)) if prio_delays else 0.0,
            }

        per_node: Dict[str, Dict] = {}
        for node_id, engine in self._engines.items():
            stats = engine.get_queue_stats()
            per_node[node_id] = {
                "queue_size": stats["queue_size"],
                "bundles_forwarded": engine.local_node.total_bundles_forwarded,
                "bundles_stored": engine.local_node.total_bundles_stored,
                "buffer_utilization": engine.local_node.buffer_utilization(),
            }

        return SimulationResult(
            config=self.config,
            total_bundles=total,
            delivered_bundles=delivered,
            dropped_bundles=dropped,
            expired_bundles=expired,
            stored_bundles=sum(
                s["queue_size"] for s in per_node.values()
            ),
            forwarded_bundles=sum(
                s["bundles_forwarded"] for s in per_node.values()
            ),
            average_delay_seconds=avg_delay,
            average_hops=avg_hops,
            delivery_ratio=delivery_ratio,
            throughput_mb=throughput_mb,
            events=list(self._events),
            per_priority_stats=per_priority,
            per_node_stats=per_node,
        )

    def get_progress(self) -> float:
        """Return simulation progress as 0.0 – 1.0."""
        if self._total_steps <= 0:
            return 0.0
        return min(1.0, self._completed_steps / self._total_steps)

    def get_intermediate_results(self) -> SimulationResult:
        """Return a snapshot of the current simulation state as partial results."""
        if self._state in (SimulationState.COMPLETED,) and self._result is not None:
            return self._result
        return self._build_result()

    def get_state(self) -> SimulationState:
        return self._state

    def reset(self) -> None:
        self._state = SimulationState.INITIALIZED
        self._topology = None
        self._engines.clear()
        self._events.clear()
        self._current_time = 0.0
        self._completed_steps = 0
        self._total_steps = 0
        self._bundles_generated = 0
        self._delivered_bundles.clear()
        self._dropped_bundles.clear()
        self._expired_bundles.clear()
        self._result = None
