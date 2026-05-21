"""AETHERIX simulation framework skeleton.

Delay-tolerant networking simulation for Earth-Mars communication.
Future integration with ns-3 or OMNeT++ for full network simulation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


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
    average_delay_seconds: float = 0.0
    average_hops: float = 0.0
    delivery_ratio: float = 0.0
    events: List[SimulationEvent] = field(default_factory=list)


class Simulator:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._state: SimulationState = SimulationState.INITIALIZED
        self._events: List[SimulationEvent] = []
        self._params: Dict = {}

    def initialize(self) -> None:
        self._state = SimulationState.INITIALIZED
        self._events = []
        self._params = {}

    def run(self) -> SimulationResult:
        return SimulationResult(config=self.config)

    def get_state(self) -> SimulationState:
        return self._state

    def reset(self) -> None:
        self._state = SimulationState.INITIALIZED
        self._events = []
        self._params = {}
