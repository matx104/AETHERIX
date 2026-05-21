"""
AETHERIX LTP Convergence Layer
Implementation of the Licklider Transmission Protocol for reliable
deep-space data transmission.

LTP provides reliable (red) and unreliable (green) transmission over
extremely long-delay links. It is the primary convergence layer for
BPv7 bundles in interplanetary DTN networks.

Reference: RFC 5326, CCSDS 734.0-B-1
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from routing.bundle import Bundle


class LTPOpcode(Enum):
    """LTP segment opcodes per RFC 5326 Section 2.1."""

    DATA = 0
    REPORT = 1
    REPORT_ACK = 2
    CHECKPOINT = 3
    CHECKPOINT_ACK = 4
    DISMISS = 5
    EXTENSION = 6


class LTPSegmentKind(Enum):
    """LTP data segment reliability class."""

    RED = 0
    GREEN = 1


@dataclass
class LTPSegment:
    """
    LTP data segment.

    Red segments require acknowledgment via checkpoint/retransmission.
    Green segments are fire-and-forget.

    The first segment in a block is marked as a checkpoint to bootstrap
    the acknowledgment cycle. The last red segment carries is_eors to
    signal end of the reliable portion of the session.
    """

    session_id: str
    kind: LTPSegmentKind
    payload: bytes
    offset: int = 0
    is_checkpoint: bool = False
    is_eors: bool = False

    @property
    def opcode(self) -> LTPOpcode:
        """Derive opcode from segment flags."""
        if self.is_checkpoint:
            return LTPOpcode.CHECKPOINT
        return LTPOpcode.DATA

    @property
    def length(self) -> int:
        """Payload length in bytes."""
        return len(self.payload)

    def to_dict(self) -> Dict[str, object]:
        """Serialize segment to dictionary."""
        return {
            "session_id": self.session_id,
            "kind": self.kind.name,
            "offset": self.offset,
            "length": self.length,
            "is_checkpoint": self.is_checkpoint,
            "is_eors": self.is_eors,
        }

    def __str__(self) -> str:
        flags = []
        if self.is_checkpoint:
            flags.append("CP")
        if self.is_eors:
            flags.append("EORS")
        flag_str = f" [{','.join(flags)}]" if flags else ""
        return (f"LTPSegment[{self.session_id[:8]}] "
                f"{self.kind.name}{flag_str} "
                f"off={self.offset} len={self.length}")


@dataclass
class LTPReport:
    """
    LTP reception report (RFC 5326 Section 5.2).

    Carries reception claims indicating which byte ranges of a red
    data block have been successfully received. Gaps in the claims
    trigger retransmission of the missing segments.
    """

    session_id: str
    report_serial: int
    checkpoint_serial: int
    reception_claims: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def total_received_bytes(self) -> int:
        """Sum of all claimed byte ranges."""
        return sum(length for _, length in self.reception_claims)

    def has_gaps(self, total_bytes: int) -> bool:
        """Check whether the claims leave gaps below total_bytes."""
        covered = self.total_received_bytes
        return covered < total_bytes

    def __str__(self) -> str:
        return (f"LTPReport[{self.session_id[:8]}] "
                f"rsn={self.report_serial} "
                f"claims={len(self.reception_claims)} "
                f"bytes={self.total_received_bytes}")


@dataclass
class LTPSession:
    """
    LTP session state tracking.

    A session represents a single block transfer (one or more segments)
    from source to destination. Red-part bytes are tracked for
    acknowledgment; green-part bytes are best-effort.
    """

    session_id: str
    source: str
    destination: str
    total_bytes: int
    red_bytes: int
    green_bytes: int
    segments_sent: int = 0
    segments_acked: int = 0
    retransmissions: int = 0
    complete: bool = False
    created_time: float = 0.0

    def __post_init__(self):
        """Set creation timestamp if not provided."""
        if self.created_time == 0.0:
            self.created_time = time.time()

    @property
    def progress(self) -> float:
        """Transfer progress as a fraction 0.0 – 1.0."""
        if self.total_bytes == 0:
            return 1.0
        ack_ratio = self.segments_acked / max(self.segments_sent, 1)
        red_ratio = self.red_bytes / self.total_bytes if self.total_bytes else 1.0
        return ack_ratio * red_ratio

    @property
    def age_seconds(self) -> float:
        """Seconds since session creation."""
        return time.time() - self.created_time

    def __str__(self) -> str:
        state = "COMPLETE" if self.complete else "ACTIVE"
        return (f"LTPSession[{self.session_id[:8]}] "
                f"{self.source} -> {self.destination} "
                f"{state} progress={self.progress:.0%} "
                f"retx={self.retransmissions}")


class LTPSessionEngine:
    """
    LTP session engine for AETHERIX DTN convergence layer.

    Manages the lifecycle of LTP sessions: segmentation of bundles
    into MTU-sized segments, session tracking, report generation,
    retransmission of missing data, and timeout detection.

    The default MTU of 1400 bytes accommodates standard deep-space
    link framing (CCSDS AOS frames). The default timeout of 1800 s
    (30 minutes) models a conservative Earth-Mars round-trip at
    maximum orbital separation.
    """

    DEFAULT_MTU = 1400

    def __init__(self, node_id: str, mtu_bytes: int = 1400):
        """
        Initialize the LTP session engine.

        Args:
            node_id: Identifier of the local node.
            mtu_bytes: Maximum segment payload size in bytes.
        """
        self.node_id = node_id
        self.mtu_bytes = mtu_bytes

        self._sessions: Dict[str, LTPSession] = {}
        self._sessions_created: int = 0
        self._sessions_completed: int = 0
        self._total_retransmissions: int = 0
        self._total_bytes_sent: int = 0

    def segment_bundle(self, bundle: Bundle) -> List[LTPSegment]:
        """
        Split a bundle payload into MTU-sized LTP segments.

        All segments are RED (reliable) by default. The first segment
        is marked as a checkpoint to initiate the acknowledgment cycle.
        The last segment carries is_eors to signal the end of the
        red-part of the session.

        Args:
            bundle: BPv7 Bundle to segment.

        Returns:
            Ordered list of LTP segments covering the entire payload.
        """
        payload = bundle.payload
        if not payload:
            return []

        session_id = self._generate_session_id()
        segments: List[LTPSegment] = []
        offset = 0
        total_length = len(payload)

        while offset < total_length:
            end = min(offset + self.mtu_bytes, total_length)
            chunk = payload[offset:end]
            is_first = offset == 0
            is_last = end >= total_length

            segments.append(LTPSegment(
                session_id=session_id,
                kind=LTPSegmentKind.RED,
                payload=chunk,
                offset=offset,
                is_checkpoint=is_first,
                is_eors=is_last,
            ))

            offset = end

        return segments

    def reconstruct_bundle(self, segments: List[LTPSegment]) -> Bundle:
        """
        Reassemble a bundle from ordered LTP segments.

        Segments are sorted by offset before reassembly to handle
        out-of-order delivery common in deep-space links.

        Args:
            segments: Collection of LTP segments for one session.

        Returns:
            Reconstructed Bundle with reassembled payload.

        Raises:
            ValueError: If segments list is empty.
        """
        if not segments:
            raise ValueError("Cannot reconstruct bundle from empty segment list")

        ordered = sorted(segments, key=lambda s: s.offset)
        payload = b"".join(s.payload for s in ordered)

        return Bundle(
            payload=payload,
            payload_size_bytes=len(payload),
        )

    def create_session(self, source: str, destination: str,
                       total_bytes: int, red_bytes: int) -> LTPSession:
        """
        Create and register a new LTP session.

        Args:
            source: Source node identifier.
            destination: Destination node identifier.
            total_bytes: Total data size for the session.
            red_bytes: Number of bytes requiring reliable (red) delivery.
                The remainder is treated as green (best-effort).

        Returns:
            The newly created LTPSession.
        """
        session_id = self._generate_session_id()
        green_bytes = total_bytes - red_bytes

        session = LTPSession(
            session_id=session_id,
            source=source,
            destination=destination,
            total_bytes=total_bytes,
            red_bytes=red_bytes,
            green_bytes=green_bytes,
        )

        self._sessions[session_id] = session
        self._sessions_created += 1
        return session

    def mark_session_complete(self, session_id: str) -> None:
        """
        Mark a session as fully completed.

        Args:
            session_id: Session identifier to complete.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return

        session.complete = True
        self._sessions_completed += 1

    def get_session(self, session_id: str) -> Optional[LTPSession]:
        """
        Retrieve a session by identifier.

        Args:
            session_id: Session identifier.

        Returns:
            The matching LTPSession, or None if not found.
        """
        return self._sessions.get(session_id)

    def generate_report(self, session_id: str,
                        received_offsets: List[Tuple[int, int]]) -> LTPReport:
        """
        Generate a reception report for a session.

        The report enumerates the byte ranges that have been
        successfully received so far.

        Args:
            session_id: Session being reported on.
            received_offsets: List of (offset, length) pairs for
                each contiguous byte range received.

        Returns:
            LTPReport ready to be sent back to the data sender.
        """
        return LTPReport(
            session_id=session_id,
            report_serial=self._next_report_serial(),
            checkpoint_serial=0,
            reception_claims=list(received_offsets),
        )

    def process_report(self, report: LTPReport) -> List[LTPSegment]:
        """
        Process a reception report and identify missing data.

        Compares the reception claims against the known data ranges
        to determine which segments must be retransmitted. Each gap
        in the claims produces a new RED segment marked as a
        checkpoint to ensure its delivery.

        Args:
            report: Reception report from the remote peer.

        Returns:
            List of LTP segments that need retransmission.
                Returns an empty list if no gaps are found.
        """
        session = self._sessions.get(report.session_id)
        if session is None:
            return []

        claims = sorted(report.reception_claims, key=lambda c: c[0])
        total_red = session.red_bytes

        gaps = self._compute_gaps(claims, total_red)
        if not gaps:
            session.segments_acked = session.segments_sent
            return []

        session.retransmissions += len(gaps)
        self._total_retransmissions += len(gaps)

        retransmit: List[LTPSegment] = []
        for gap_offset, gap_length in gaps:
            chunk_end = min(gap_offset + gap_length, total_red)
            retransmit.append(LTPSegment(
                session_id=session.session_id,
                kind=LTPSegmentKind.RED,
                payload=b"\x00" * (chunk_end - gap_offset),
                offset=gap_offset,
                is_checkpoint=True,
                is_eors=(chunk_end >= total_red),
            ))

        self._total_bytes_sent += sum(s.length for s in retransmit)
        return retransmit

    def check_timeouts(self, current_time: float,
                       timeout_seconds: float = 1800.0) -> List[str]:
        """
        Identify sessions that have exceeded the retransmission timeout.

        The default timeout of 1800 seconds (30 minutes) corresponds to
        the approximate Earth-Mars round-trip light time at maximum
        orbital separation (~401 Mkm).

        Args:
            current_time: Current simulation or wall-clock time (epoch seconds).
            timeout_seconds: Timeout threshold in seconds.

        Returns:
            List of session IDs that have been waiting beyond the timeout.
        """
        timed_out: List[str] = []
        for session_id, session in self._sessions.items():
            if session.complete:
                continue
            elapsed = current_time - session.created_time
            if elapsed > timeout_seconds:
                timed_out.append(session_id)
        return timed_out

    def get_stats(self) -> Dict[str, int]:
        """
        Return aggregate engine statistics.

        Returns:
            Dictionary with keys: sessions_created, completed,
            retransmissions, total_bytes_sent.
        """
        return {
            "sessions_created": self._sessions_created,
            "completed": self._sessions_completed,
            "retransmissions": self._total_retransmissions,
            "total_bytes_sent": self._total_bytes_sent,
        }

    def _generate_session_id(self) -> str:
        """Create a unique session identifier."""
        return f"ltp-{uuid.uuid4().hex[:12]}"

    def _next_report_serial(self) -> int:
        """Monotonically increasing report serial number."""
        self._report_serial_counter = getattr(self, "_report_serial_counter", 0) + 1
        return self._report_serial_counter

    @staticmethod
    def _compute_gaps(claims: List[Tuple[int, int]],
                      total_bytes: int) -> List[Tuple[int, int]]:
        """
        Compute byte-range gaps not covered by reception claims.

        Walks through sorted, non-overlapping claims and identifies
        any byte ranges in [0, total_bytes) that are not accounted for.

        Args:
            claims: Sorted list of (offset, length) reception claims.
            total_bytes: Total number of red bytes in the session.

        Returns:
            List of (offset, length) pairs for each gap found.
        """
        gaps: List[Tuple[int, int]] = []
        cursor = 0

        for claim_offset, claim_length in claims:
            if claim_offset > cursor:
                gaps.append((cursor, claim_offset - cursor))
            claim_end = claim_offset + claim_length
            if claim_end > cursor:
                cursor = claim_end

        if cursor < total_bytes:
            gaps.append((cursor, total_bytes - cursor))

        return gaps


if __name__ == "__main__":
    engine = LTPSessionEngine(node_id="mars.areo.alpha", mtu_bytes=1400)

    bundle = Bundle(
        source=EndpointID.from_string("dtn://mars.surface.rover-01/science"),
        destination=EndpointID.from_string("dtn://earth.control.moc/science"),
        payload=b"X" * 5000,
    )

    segments = engine.segment_bundle(bundle)
    print(f"Segmented {len(bundle.payload)}B bundle into {len(segments)} segments:")
    for seg in segments:
        print(f"  {seg}")

    session = engine.create_session(
        source="mars.surface.rover-01",
        destination="earth.control.moc",
        total_bytes=5000,
        red_bytes=5000,
    )
    session.segments_sent = len(segments)
    print(f"\n{session}")

    partial_claims = [(0, 1400), (2800, 1400)]
    report = engine.generate_report(session.session_id, partial_claims)
    print(f"\n{report}")

    retransmit = engine.process_report(report)
    print(f"\nRetransmission needed: {len(retransmit)} segment(s)")
    for seg in retransmit:
        print(f"  {seg}")

    print(f"\nStats: {engine.get_stats()}")
