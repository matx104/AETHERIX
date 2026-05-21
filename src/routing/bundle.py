"""
AETHERIX Bundle Module
Implementation of Bundle Protocol v7 data structures.

Reference: RFC 9171, CCSDS 735.1-B-1
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional


class BundlePriority(IntEnum):
    """Bundle priority levels per AETHERIX QoS specification."""
    EMERGENCY = 0       # Spacecraft health, safety alerts
    HIGH_SCIENCE = 1    # Time-sensitive observations
    STANDARD = 2        # Regular telemetry and data
    HOUSEKEEPING = 3    # Status updates, logs
    BULK = 4            # Archived datasets, software updates


class BundleFlags(IntEnum):
    """Bundle processing control flags (RFC 9171)."""
    IS_FRAGMENT = 0x01
    PAYLOAD_IS_ADMIN = 0x02
    NO_FRAGMENT = 0x04
    CUSTODY_REQUESTED = 0x08
    DEST_IS_SINGLETON = 0x10
    ACK_REQUESTED = 0x20
    STATUS_REQUESTED = 0x40


@dataclass
class EndpointID:
    """
    Bundle Protocol Endpoint Identifier.

    Format: scheme:ssp (e.g., "dtn://mars.surface.rover-01/science")

    AETHERIX uses LNIS v5 compliant identifiers:
    - Earth: earth.dsn.goldstone, earth.control.moc
    - Mars: mars.surface.rover-01, mars.areo.alpha
    - Transit: transit.esl4.relay
    """
    scheme: str = "dtn"
    node_id: str = ""
    service_id: str = ""

    @classmethod
    def from_string(cls, eid_string: str) -> 'EndpointID':
        """Parse an EID from string format."""
        if "://" in eid_string:
            scheme, rest = eid_string.split("://", 1)
            if "/" in rest:
                node_id, service_id = rest.split("/", 1)
            else:
                node_id, service_id = rest, ""
        else:
            scheme, node_id, service_id = "dtn", eid_string, ""
        return cls(scheme=scheme, node_id=node_id, service_id=service_id)

    def __str__(self) -> str:
        if self.service_id:
            return f"{self.scheme}://{self.node_id}/{self.service_id}"
        return f"{self.scheme}://{self.node_id}"


@dataclass
class Bundle:
    """
    Bundle Protocol v7 Bundle implementation.

    A bundle is the fundamental data unit in DTN. It consists of:
    - Primary block: routing and lifetime information
    - Payload block: application data
    - Extension blocks: optional metadata

    Reference: RFC 9171 Section 4
    """
    # Primary block fields
    bundle_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    source: EndpointID = field(default_factory=EndpointID)
    destination: EndpointID = field(default_factory=EndpointID)
    report_to: Optional[EndpointID] = None

    # Timing
    creation_time: float = field(default_factory=time.time)
    lifetime_seconds: int = 86400 * 7  # Default: 7 days

    # Priority and flags
    priority: BundlePriority = BundlePriority.STANDARD
    flags: int = BundleFlags.DEST_IS_SINGLETON

    # Payload
    payload: bytes = b""
    payload_size_bytes: int = 0

    # Tracking
    hops: List[Dict[str, Any]] = field(default_factory=list)
    custody_holders: List[str] = field(default_factory=list)

    # Fragment info (if fragmented)
    is_fragment: bool = False
    fragment_offset: int = 0
    total_adu_length: int = 0

    def __post_init__(self):
        """Calculate payload size if not set."""
        if self.payload_size_bytes == 0 and self.payload:
            self.payload_size_bytes = len(self.payload)

    @property
    def is_expired(self) -> bool:
        """Check if bundle has exceeded its lifetime."""
        return time.time() > (self.creation_time + self.lifetime_seconds)

    @property
    def remaining_lifetime(self) -> float:
        """Get remaining lifetime in seconds."""
        return max(0, (self.creation_time + self.lifetime_seconds) - time.time())

    @property
    def age_seconds(self) -> float:
        """Get bundle age in seconds."""
        return time.time() - self.creation_time

    def add_hop(self, node_id: str, action: str, timestamp: Optional[float] = None):
        """Record a forwarding hop."""
        self.hops.append({
            'node': node_id,
            'action': action,
            'timestamp': timestamp or time.time(),
            'hop_number': len(self.hops) + 1
        })

    def accept_custody(self, node_id: str):
        """Accept custody of the bundle."""
        self.custody_holders.append(node_id)
        self.add_hop(node_id, "CUSTODY_ACCEPTED")

    def release_custody(self, node_id: str):
        """Release custody after successful forward."""
        if node_id in self.custody_holders:
            self.custody_holders.remove(node_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize bundle to dictionary."""
        return {
            'bundle_id': self.bundle_id,
            'source': str(self.source),
            'destination': str(self.destination),
            'priority': self.priority.name,
            'creation_time': self.creation_time,
            'lifetime_seconds': self.lifetime_seconds,
            'payload_size_bytes': self.payload_size_bytes,
            'hops': self.hops,
            'custody_holders': self.custody_holders,
        }

    def __str__(self) -> str:
        return (f"Bundle[{self.bundle_id}] "
                f"{self.source.node_id} -> {self.destination.node_id} "
                f"P{self.priority.value} {self.payload_size_bytes}B")


def create_science_bundle(source_node: str, destination_node: str,
                          data_mb: float, priority: BundlePriority = BundlePriority.STANDARD) -> Bundle:
    """
    Factory function to create a science data bundle.

    Args:
        source_node: Source node ID (e.g., "mars.surface.rover-01")
        destination_node: Destination node ID (e.g., "earth.control.moc")
        data_mb: Payload size in megabytes
        priority: Bundle priority level

    Returns:
        Configured Bundle instance
    """
    return Bundle(
        source=EndpointID.from_string(f"dtn://{source_node}/science"),
        destination=EndpointID.from_string(f"dtn://{destination_node}/science"),
        priority=priority,
        payload_size_bytes=int(data_mb * 1024 * 1024),
        lifetime_seconds=86400 * 7,  # 7 days for science data
    )


# Example usage
if __name__ == "__main__":
    # Create a science data bundle
    bundle = create_science_bundle(
        source_node="mars.surface.rover-01",
        destination_node="earth.control.moc",
        data_mb=500.0,
        priority=BundlePriority.STANDARD
    )

    print(f"Created: {bundle}")
    print(f"Details: {bundle.to_dict()}")
