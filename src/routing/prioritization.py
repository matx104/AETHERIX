"""
AETHERIX Mission-Critical Data Prioritization Module
====================================================

Implements the data-management layer that decides *what* gets sent *when* over
a bandwidth-starved, intermittently-connected interplanetary link:

    DataCategory      - the 4-tier mission data classification (Topic 59 (f))
    Compressor        - lossless / lossy compression ratio model (CCSDS 121/122)
    QoSScheduler      - deadline-aware, strictly-priority, preemptive downlink
                        scheduler over a finite contact window
    EmergencyProtocol - safe-mode activation + preemption of in-progress traffic

Builds directly on the Bundle Protocol v7 types in ``bundle.py`` so the four
mission tiers map onto the existing ``BundlePriority`` levels.

Reference standards:
- RFC 9171            : BPv7 bundle priority / processing flags
- CCSDS 121.0-B-3     : Lossless Data Compression (Rice / adaptive)
- CCSDS 122.0-B-2     : Image Data Compression (wavelet)
- CCSDS 734.2-B-1     : DTN architecture (QoS, custody)

MODELLING HONESTY: compression ratios are *representative* figures from the
CCSDS standards and the data-compression literature, applied analytically to a
declared payload size. No bytes are actually compressed. The scheduler is a
discrete event-free analytic model; stochastic demos use a fixed seed.

Reference: AETHERIX Topic 59, learning objective (f).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from .bundle import Bundle, BundlePriority, EndpointID


class DataCategory(Enum):
    """
    Mission data classification (Topic 59 (f)), highest urgency first.

    Each tier maps onto a BPv7 ``BundlePriority`` so the classification flows
    through the existing bundle/forwarding machinery unchanged.
    """
    EMERGENCY_SAFETY = ("Emergency / Safety-critical",
                        "Real-time health telemetry, collision avoidance, faults",
                        BundlePriority.EMERGENCY)
    MISSION_CRITICAL = ("Mission-critical",
                        "Command acknowledgements, time-sensitive science events",
                        BundlePriority.HIGH_SCIENCE)
    HIGH_PRIORITY = ("High-priority",
                     "Routine telemetry, scheduled science observations",
                     BundlePriority.STANDARD)
    LOW_PRIORITY = ("Low-priority",
                    "Housekeeping logs, bulk file transfers, software images",
                    BundlePriority.BULK)

    def __init__(self, label: str, examples: str, bundle_priority: BundlePriority):
        self.label = label
        self.examples = examples
        self.bundle_priority = bundle_priority

    @property
    def rank(self) -> int:
        """0 = most urgent. Matches the underlying BundlePriority value order."""
        return int(self.bundle_priority.value)

    @property
    def preemptive(self) -> bool:
        """Emergency traffic may preempt in-progress lower-priority transfers."""
        return self is DataCategory.EMERGENCY_SAFETY


# --- Compression -------------------------------------------------------------

@dataclass(frozen=True)
class CompressionProfile:
    """A compression method and its representative ratio for a data type."""
    name: str
    standard: str
    ratio: float          # original_size / compressed_size
    lossless: bool

    @property
    def reduction_percent(self) -> float:
        """Percentage of bytes removed (e.g. ratio 4.0 -> 75%)."""
        return 100.0 * (1.0 - 1.0 / self.ratio)


# Representative profiles keyed by payload data type.
COMPRESSION_PROFILES: Dict[str, CompressionProfile] = {
    "telemetry": CompressionProfile("Rice / adaptive", "CCSDS 121.0-B-3", 3.0, True),
    "housekeeping": CompressionProfile("LZMA", "ISO LZMA", 4.0, True),
    "text": CompressionProfile("zstd", "RFC 8878", 5.0, True),
    "image_lossless": CompressionProfile("Wavelet lossless", "CCSDS 122.0-B-2", 2.0, True),
    "image_lossy": CompressionProfile("Wavelet lossy", "CCSDS 122.0-B-2", 10.0, False),
    "video": CompressionProfile("HEVC-class", "ITU-T H.265", 50.0, False),
    "raw": CompressionProfile("none", "-", 1.0, True),
}


@dataclass
class CompressionResult:
    """Outcome of applying a compression profile to a payload."""
    data_type: str
    original_bytes: int
    compressed_bytes: int
    profile: CompressionProfile

    @property
    def ratio(self) -> float:
        if self.compressed_bytes == 0:
            return float("inf")
        return self.original_bytes / self.compressed_bytes

    @property
    def saved_bytes(self) -> int:
        return self.original_bytes - self.compressed_bytes


class Compressor:
    """Analytic compressor that applies representative CCSDS-class ratios."""

    def compress(self, size_bytes: int, data_type: str = "telemetry") -> CompressionResult:
        profile = COMPRESSION_PROFILES.get(data_type, COMPRESSION_PROFILES["raw"])
        compressed = int(round(size_bytes / profile.ratio))
        return CompressionResult(data_type, size_bytes, compressed, profile)


# --- QoS / deadline-aware scheduler -----------------------------------------

@dataclass
class TrafficItem:
    """A unit of data competing for the downlink."""
    name: str
    category: DataCategory
    size_bytes: int
    deadline_s: float                  # must be delivered within this window
    data_type: str = "telemetry"
    compressed_bytes: Optional[int] = None
    fragmentable: bool = True          # BPv7: clear for NO_FRAGMENT bundles

    def effective_bytes(self) -> int:
        """Bytes actually transmitted (compressed if compression was applied)."""
        return self.compressed_bytes if self.compressed_bytes is not None else self.size_bytes


@dataclass
class ScheduleEntry:
    item: TrafficItem
    start_s: float
    end_s: float
    delivered: bool
    reason: str = ""
    bytes_sent: int = 0                # for partial (fragmented) transfers

    @property
    def partial(self) -> bool:
        return self.bytes_sent > 0 and not self.delivered


@dataclass
class ScheduleResult:
    entries: List[ScheduleEntry]
    contact_duration_s: float
    link_rate_bps: float

    @property
    def delivered(self) -> List[ScheduleEntry]:
        return [e for e in self.entries if e.delivered]

    @property
    def dropped(self) -> List[ScheduleEntry]:
        return [e for e in self.entries if not e.delivered]

    @property
    def bytes_sent_total(self) -> int:
        """All bytes pushed over the link this contact (full + partial)."""
        return sum(e.bytes_sent for e in self.entries)

    @property
    def utilization_percent(self) -> float:
        capacity = self.link_rate_bps / 8.0 * self.contact_duration_s
        if capacity <= 0:
            return 0.0
        return 100.0 * self.bytes_sent_total / capacity

    def summary(self) -> str:
        lines = [
            f"Contact: {self.contact_duration_s:.0f}s @ "
            f"{self.link_rate_bps / 1e6:.1f} Mbps "
            f"(capacity {self.link_rate_bps / 8.0 * self.contact_duration_s / 1e6:.1f} MB)",
            f"Fully delivered {len(self.delivered)}/{len(self.entries)} items, "
            f"{self.bytes_sent_total / 1e6:.1f} MB sent, "
            f"link utilization {self.utilization_percent:.0f}%",
        ]
        for e in self.entries:
            mark = "OK  " if e.delivered else ("PART" if e.partial else "DROP")
            window = f"{e.start_s:6.1f}-{e.end_s:6.1f}s" if e.bytes_sent else "       --     "
            lines.append(
                f"  [{mark}] P{e.item.category.rank} {e.item.name:<24} "
                f"{e.bytes_sent / 1e6:7.1f}/{e.item.effective_bytes() / 1e6:<7.1f} MB  "
                f"{window}  {e.reason}")
        return "\n".join(lines)


class QoSScheduler:
    """
    Strict-priority, deadline-aware scheduler over a single finite contact.

    Policy:
      1. Sort by category rank (0 = emergency first), then by earliest deadline.
      2. Transmit in order; an item is delivered only if it both fits in the
         remaining contact time AND completes before its deadline.
      3. Items that cannot meet their deadline (or do not fit) are deferred to
         the next contact (reported as dropped from *this* contact).
    """

    def __init__(self, link_rate_bps: float, contact_duration_s: float):
        self.link_rate_bps = link_rate_bps
        self.contact_duration_s = contact_duration_s

    def _tx_time(self, item: TrafficItem) -> float:
        return (item.effective_bytes() * 8.0) / self.link_rate_bps

    def schedule(self, items: List[TrafficItem]) -> ScheduleResult:
        ordered = sorted(items, key=lambda i: (i.category.rank, i.deadline_s))
        t = 0.0
        entries: List[ScheduleEntry] = []
        for item in ordered:
            remaining = self.contact_duration_s - t
            if remaining <= 1e-9:
                entries.append(ScheduleEntry(item, t, t, False, "deferred: contact ended"))
                continue
            dur = self._tx_time(item)
            finish = t + dur
            if finish <= self.contact_duration_s and finish <= item.deadline_s:
                # fits fully and meets its deadline
                entries.append(ScheduleEntry(item, t, finish, True, "on time",
                                             bytes_sent=item.effective_bytes()))
                t = finish
            elif finish > item.deadline_s and dur <= remaining:
                # would fit in the window but misses its own deadline -> defer
                entries.append(ScheduleEntry(item, t, finish, False,
                                             "deferred: would miss deadline"))
            elif item.fragmentable:
                # BPv7 fragmentation: send what fits, defer the remainder
                sent = int(remaining * self.link_rate_bps / 8.0)
                entries.append(ScheduleEntry(item, t, self.contact_duration_s, False,
                                             f"fragmented: "
                                             f"{100.0 * sent / item.effective_bytes():.0f}% "
                                             f"this contact, remainder next contact",
                                             bytes_sent=sent))
                t = self.contact_duration_s
            else:
                entries.append(ScheduleEntry(item, t, finish, False,
                                             "deferred: NO_FRAGMENT, exceeds window"))
        # restore original submission order for readability
        order = {id(i): n for n, i in enumerate(items)}
        entries.sort(key=lambda e: order[id(e.item)])
        return ScheduleResult(entries, self.contact_duration_s, self.link_rate_bps)


# --- Emergency protocol ------------------------------------------------------

@dataclass
class EmergencyProtocol:
    """
    Emergency communication handling: an emergency/safety bundle preempts the
    in-progress transmission, is sent immediately (optionally via a low-rate
    direct-to-Earth backup link), after which normal QoS scheduling resumes.
    """
    direct_to_earth_rate_bps: float = 1.0e4   # 10 kbps emergency beacon backup
    log: List[str] = field(default_factory=list)

    def preempt(self, in_progress: Optional[TrafficItem],
                emergency: TrafficItem) -> Dict[str, object]:
        """
        Preempt the current transfer with an emergency bundle.

        Returns a dict describing the action taken.
        """
        if in_progress is not None and in_progress.category.rank <= emergency.category.rank:
            # current item is equal/higher urgency -> do not preempt
            self.log.append(
                f"no preemption: {in_progress.name} already >= emergency urgency")
            return {"preempted": False, "emergency_sent": False}

        if in_progress is not None:
            self.log.append(
                f"PREEMPT {in_progress.name} (rank {in_progress.category.rank}) "
                f"for {emergency.name} (rank {emergency.category.rank})")
        tx_s = (emergency.effective_bytes() * 8.0) / self.direct_to_earth_rate_bps
        self.log.append(
            f"emergency {emergency.name} sent via direct-to-Earth backup "
            f"({self.direct_to_earth_rate_bps / 1e3:.0f} kbps) in {tx_s:.2f}s")
        if in_progress is not None:
            self.log.append(f"resume {in_progress.name} after emergency clears")
        return {"preempted": in_progress is not None,
                "emergency_sent": True,
                "emergency_tx_s": tx_s}


def make_bundle(item: TrafficItem, source: str, dest: str) -> Bundle:
    """Convenience: turn a TrafficItem into a BPv7 Bundle with mapped priority."""
    return Bundle(
        source=EndpointID.from_string(f"dtn://{source}/data"),
        destination=EndpointID.from_string(f"dtn://{dest}/data"),
        priority=item.category.bundle_priority,
        payload_size_bytes=item.effective_bytes(),
        lifetime_seconds=int(max(60, item.deadline_s)),
    )


# --- Demo --------------------------------------------------------------------

def simulate_downlink(seed: int = 42) -> ScheduleResult:
    """Constrained Mars->Earth downlink with mixed-priority traffic + emergency."""
    compressor = Compressor()

    raw_items = [
        ("rover-health-telemetry", DataCategory.EMERGENCY_SAFETY, 2_000_000, 60, "telemetry"),
        ("command-acknowledgements", DataCategory.MISSION_CRITICAL, 5_000_000, 120, "telemetry"),
        ("seismic-event-capture", DataCategory.MISSION_CRITICAL, 40_000_000, 300, "telemetry"),
        ("daily-panorama-imagery", DataCategory.HIGH_PRIORITY, 8_000_000_000, 900, "image_lossy"),
        ("housekeeping-logs", DataCategory.LOW_PRIORITY, 400_000_000, 1200, "housekeeping"),
        ("software-update-archive", DataCategory.LOW_PRIORITY, 6_000_000_000, 1800, "raw"),
    ]

    items: List[TrafficItem] = []
    for name, cat, size, deadline, dtype in raw_items:
        comp = compressor.compress(size, dtype)
        items.append(TrafficItem(name, cat, size, deadline, dtype, comp.compressed_bytes))

    # 30 Mbps optical downlink, 15-minute (900 s) contact window.
    scheduler = QoSScheduler(link_rate_bps=30e6, contact_duration_s=900)
    return scheduler.schedule(items)


if __name__ == "__main__":
    print("=" * 70)
    print("AETHERIX Data Prioritization — Constrained Mars Downlink")
    print("=" * 70)

    comp = Compressor()
    print("\nCompression profiles (representative CCSDS-class ratios):")
    for dtype in ("telemetry", "image_lossy", "video", "housekeeping"):
        r = comp.compress(1_000_000_000, dtype)
        print(f"  {dtype:<14} {r.profile.standard:<16} "
              f"{r.ratio:5.1f}x  ({r.profile.reduction_percent:4.1f}% smaller, "
              f"{'lossless' if r.profile.lossless else 'lossy'})")

    print("\nPrioritized, deadline-aware schedule:")
    result = simulate_downlink()
    print(result.summary())

    print("\nEmergency preemption event:")
    emergency = TrafficItem("collision-avoidance-alert", DataCategory.EMERGENCY_SAFETY,
                            50_000, 5, "telemetry")
    in_progress = TrafficItem("daily-panorama-imagery", DataCategory.HIGH_PRIORITY,
                              80_000_000, 900, "image_lossy")
    proto = EmergencyProtocol()
    proto.preempt(in_progress, emergency)
    for line in proto.log:
        print(f"  {line}")
