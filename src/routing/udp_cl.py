"""
AETHERIX UDP Convergence Layer
UDPCL protocol for optical inter-satellite links (best-effort, low overhead).

Designed for high-throughput laser crosslinks between relay satellites
where low protocol overhead outweighs the need for guaranteed delivery.
Bundle Protocol v7 reliability mechanisms handle retransmission.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from routing.bundle import Bundle


@dataclass
class UDPCLDatagram:
    """
    UDP Convergence Layer datagram.

    Carries a fragment of a bundle payload across a single optical
    inter-satellite link hop. Includes fragmentation metadata for
    reassembly at the receiving node.
    """
    source: str
    destination: str
    payload: bytes
    sequence_number: int = 0
    bundle_id: str = ""
    is_fragment: bool = False
    fragment_offset: int = 0
    total_length: int = 0


@dataclass
class UDPCLStats:
    """Aggregate statistics for a UDP convergence layer instance."""
    datagrams_sent: int = 0
    datagrams_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    datagrams_lost: int = 0


class UDPConvergenceLayer:
    """
    UDP Convergence Layer for optical inter-satellite links.

    Provides best-effort, low-overhead transport for bundle fragments
    over laser crosslinks between relay satellites. Fragmentation and
    reassembly are handled at this layer; reliability is delegated to
    the Bundle Protocol v7 custody transfer mechanism above.
    """

    def __init__(self, node_id: str, mtu_bytes: int = 1472, loss_rate: float = 0.0):
        self.node_id: str = node_id
        self.mtu_bytes: int = mtu_bytes
        self.loss_rate: float = loss_rate
        self._stats: UDPCLStats = UDPCLStats()
        self._pending_fragments: Dict[str, List[UDPCLDatagram]] = {}

    def fragment_bundle(self, bundle: Bundle) -> List[UDPCLDatagram]:
        """
        Split a bundle into MTU-sized datagrams for transmission.

        Each datagram carries up to mtu_bytes of payload along with
        fragmentation metadata (offset, total length, sequence number)
        for reassembly at the receiver.
        """
        payload = bundle.payload
        total_length = len(payload)
        if total_length == 0:
            return [UDPCLDatagram(
                source=str(bundle.source),
                destination=str(bundle.destination),
                payload=b"",
                sequence_number=0,
                bundle_id=bundle.bundle_id,
                is_fragment=False,
                fragment_offset=0,
                total_length=0,
            )]

        datagrams: List[UDPCLDatagram] = []
        offset = 0
        seq = 0

        while offset < total_length:
            chunk = payload[offset:offset + self.mtu_bytes]
            is_fragment = (total_length > self.mtu_bytes)
            datagrams.append(UDPCLDatagram(
                source=str(bundle.source),
                destination=str(bundle.destination),
                payload=chunk,
                sequence_number=seq,
                bundle_id=bundle.bundle_id,
                is_fragment=is_fragment,
                fragment_offset=offset,
                total_length=total_length,
            ))
            offset += self.mtu_bytes
            seq += 1

        return datagrams

    def reconstruct_bundle(self, datagrams: List[UDPCLDatagram]) -> Optional[Bundle]:
        """
        Reassemble a bundle from received datagrams.

        Returns None if the set of datagrams is incomplete (missing
        fragments) or empty.
        """
        if not datagrams:
            return None

        first = datagrams[0]
        total_length = first.total_length
        bundle_id = first.bundle_id

        if total_length == 0:
            return Bundle(
                bundle_id=bundle_id,
                payload=b"",
                payload_size_bytes=0,
            )

        sorted_datagrams = sorted(datagrams, key=lambda d: d.sequence_number)

        expected_bytes = set(range(0, total_length, self.mtu_bytes))
        received_offsets = {d.fragment_offset for d in sorted_datagrams}
        if not expected_bytes.issubset(received_offsets):
            return None

        reassembled = bytearray(total_length)
        for d in sorted_datagrams:
            reassembled[d.fragment_offset:d.fragment_offset + len(d.payload)] = d.payload

        return Bundle(
            bundle_id=bundle_id,
            payload=bytes(reassembled),
            payload_size_bytes=len(reassembled),
        )

    def send_datagram(self, datagram: UDPCLDatagram) -> bool:
        """
        Simulate sending a datagram over an optical inter-satellite link.

        Returns False if the datagram is lost due to simulated
        link conditions (loss_rate probability of failure).
        """
        if random.random() < self.loss_rate:
            self._stats.datagrams_lost += 1
            return False

        self._stats.datagrams_sent += 1
        self._stats.bytes_sent += len(datagram.payload)
        return True

    def receive_datagram(self, datagram: UDPCLDatagram) -> bool:
        """
        Simulate receiving a datagram at this node.

        Buffers fragments for later reassembly when all fragments
        for a bundle have arrived.
        """
        self._stats.datagrams_received += 1
        self._stats.bytes_received += len(datagram.payload)

        if datagram.is_fragment and datagram.bundle_id:
            fragments = self._pending_fragments.setdefault(datagram.bundle_id, [])
            existing_offsets = {d.fragment_offset for d in fragments}
            if datagram.fragment_offset not in existing_offsets:
                fragments.append(datagram)

        return True

    def get_stats(self) -> UDPCLStats:
        """Return a snapshot of UDPCL throughput and loss statistics."""
        return UDPCLStats(
            datagrams_sent=self._stats.datagrams_sent,
            datagrams_received=self._stats.datagrams_received,
            bytes_sent=self._stats.bytes_sent,
            bytes_received=self._stats.bytes_received,
            datagrams_lost=self._stats.datagrams_lost,
        )
