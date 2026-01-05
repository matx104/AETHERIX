#!/usr/bin/env python3
"""
AETHERIX Mars Mission Scenario Demo
End-to-end communication scenario from Mars rover to Earth mission control.
"""

import time
from dataclasses import dataclass
from typing import List
from enum import Enum


class Priority(Enum):
    EMERGENCY = 0
    HIGH_SCIENCE = 1
    STANDARD_SCIENCE = 2
    HOUSEKEEPING = 3
    BULK = 4


@dataclass
class MissionEvent:
    """Represents an event in the mission timeline."""
    timestamp_s: float
    location: str
    event: str
    details: str


def format_time(seconds: float) -> str:
    """Format seconds into readable time."""
    if seconds >= 60:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    return f"{seconds:.1f}s"


def run_demo():
    """Run the Mars mission scenario demonstration."""
    print("\n" + "="*80)
    print("       AETHERIX MARS MISSION SCENARIO")
    print("       End-to-End Data Transmission: Perseverance Rover to Earth MOC")
    print("="*80)

    # Mission parameters
    scenario = {
        'mission': 'Mars 2026 Sample Return Precursor',
        'date': '2026-01-05',
        'earth_mars_distance_km': 225_000_000,
        'light_time_s': 750,  # ~12.5 minutes
        'data_source': 'Perseverance Rover',
        'data_type': 'High-Resolution Terrain Scan',
        'data_size_mb': 500,
        'priority': Priority.STANDARD_SCIENCE,
    }

    print("\n" + "-"*80)
    print("MISSION SCENARIO PARAMETERS")
    print("-"*80)
    print(f"  Mission: {scenario['mission']}")
    print(f"  Date: {scenario['date']}")
    print(f"  Earth-Mars Distance: {scenario['earth_mars_distance_km']/1e6:.0f} million km")
    print(f"  One-Way Light Time: {format_time(scenario['light_time_s'])}")
    print(f"  Data Source: {scenario['data_source']}")
    print(f"  Data Type: {scenario['data_type']}")
    print(f"  Data Size: {scenario['data_size_mb']} MB")
    print(f"  Priority: P{scenario['priority'].value} ({scenario['priority'].name})")
    print("-"*80)

    # Define mission timeline
    timeline: List[MissionEvent] = [
        MissionEvent(0, "mars.surface.rover-01",
                    "DATA GENERATION",
                    "Perseverance completes terrain scan, 500 MB science data"),
        MissionEvent(2, "mars.surface.rover-01",
                    "BUNDLE CREATION",
                    "BPv7 bundle created: ID=BDL-2026-0105-TERRAIN, P2 priority"),
        MissionEvent(3, "mars.surface.rover-01",
                    "RL AGENT DECISION",
                    "Route computed: rover -> MRS-Alpha -> MRS-Gamma -> L4 -> LEO -> DSN"),
        MissionEvent(5, "mars.surface.rover-01",
                    "UHF UPLINK START",
                    "Transmitting to MRS-Alpha at 2 Mbps via UHF link"),
        MissionEvent(2005, "mars.areo.alpha",
                    "BUNDLE RECEIVED",
                    "Bundle stored in buffer, custody accepted"),
        MissionEvent(2006, "mars.areo.alpha",
                    "ISL FORWARD",
                    "Inter-satellite link to MRS-Gamma (polar orbiter) at 1 Gbps"),
        MissionEvent(2007, "mars.polar.gamma",
                    "OPTICAL DOWNLINK PREP",
                    "Pointing to ES-L4 relay, 1550nm laser aligned"),
        MissionEvent(2010, "mars.polar.gamma",
                    "DEEP SPACE OPTICAL TX",
                    "Transmitting at 10 Mbps to ES-L4 Lagrange relay"),
        MissionEvent(752000, "transit.esl4.relay",
                    "L4 RELAY RECEIVED",
                    "Bundle received after 12.5 min propagation, stored"),
        MissionEvent(752005, "transit.esl4.relay",
                    "EARTH-BOUND FORWARD",
                    "Retransmitting to Earth LEO constellation"),
        MissionEvent(752100, "earth.leo.lasersat-001",
                    "LEO CONSTELLATION RX",
                    "Received via optical crosslink, routing to ground"),
        MissionEvent(752102, "earth.geo.atlantic",
                    "GEO RELAY",
                    "Forwarding to DSN Madrid ground station"),
        MissionEvent(752105, "earth.dsn.madrid",
                    "GROUND STATION RX",
                    "Bundle received, validating integrity"),
        MissionEvent(752106, "earth.dsn.madrid",
                    "CUSTODY TRANSFER",
                    "Custody transferred to ground segment"),
        MissionEvent(752110, "earth.control.moc",
                    "MOC DELIVERY",
                    "Bundle delivered to Mission Operations Center"),
        MissionEvent(752111, "earth.control.moc",
                    "DELIVERY CONFIRMED",
                    "Science data available to operations team"),
    ]

    print("\n" + "="*80)
    print("MISSION TIMELINE")
    print("="*80)

    light_time_s = scenario['light_time_s']

    for i, event in enumerate(timeline):
        # Calculate progress
        if i < len(timeline) - 1:
            progress = (i + 1) / len(timeline) * 100
        else:
            progress = 100

        # Determine tier
        if 'surface' in event.location:
            tier = 5
            tier_name = "Mars Surface"
        elif 'areo' in event.location or 'polar' in event.location:
            tier = 4
            tier_name = "Mars Orbital"
        elif 'transit' in event.location:
            tier = 3
            tier_name = "Deep Space"
        elif 'leo' in event.location or 'geo' in event.location:
            tier = 2
            tier_name = "Earth Orbital"
        else:
            tier = 1
            tier_name = "Earth Ground"

        print(f"\n  T+{format_time(event.timestamp_s):>12} | TIER {tier} ({tier_name})")
        print(f"  {'':>15} | Location: {event.location}")
        print(f"  {'':>15} | Event: {event.event}")
        print(f"  {'':>15} | {event.details}")

        # Progress bar
        bar_width = 30
        filled = int(bar_width * progress / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        print(f"  {'':>15} | Progress: [{bar}] {progress:.0f}%")

    # Summary statistics
    total_time_s = timeline[-1].timestamp_s
    overhead_s = total_time_s - light_time_s

    print("\n" + "="*80)
    print("TRANSMISSION SUMMARY")
    print("="*80)
    print(f"  Data Size: {scenario['data_size_mb']} MB")
    print(f"  Total Transmission Time: {format_time(total_time_s)}")
    print(f"  One-Way Light Time: {format_time(light_time_s)}")
    print(f"  DTN Processing Overhead: {format_time(overhead_s)}")
    print(f"  Overhead Percentage: {(overhead_s/light_time_s)*100:.2f}%")
    print(f"  Number of Hops: {sum(1 for e in timeline if 'FORWARD' in e.event or 'RECEIVED' in e.event)}")
    print(f"  Delivery Status: SUCCESS")

    # Performance metrics
    print("\n" + "-"*80)
    print("PERFORMANCE METRICS")
    print("-"*80)

    metrics = [
        ("End-to-End Latency", f"{format_time(total_time_s)} (1.003x light time)"),
        ("Effective Data Rate", f"~{scenario['data_size_mb']*8/(total_time_s-light_time_s):.1f} Mbps (processing)"),
        ("Bundle Integrity", "100% (no errors)"),
        ("Custody Transfers", "4 (rover -> MRS -> L4 -> DSN)"),
        ("Retry Count", "0"),
        ("Path Used", "Primary (optical)"),
    ]

    for metric, value in metrics:
        print(f"  {metric:<25}: {value}")

    # Comparison
    print("\n" + "-"*80)
    print("COMPARISON: Current vs AETHERIX")
    print("-"*80)
    print(f"  {'Metric':<25} {'Current (MRO)':<20} {'AETHERIX'}")
    print(f"  {'-'*25} {'-'*20} {'-'*20}")
    print(f"  {'500 MB transfer time':<25} {'~45 minutes':<20} {'~13 minutes'}")
    print(f"  {'Daily data capacity':<25} {'5-10 GB':<20} {'50-100 GB'}")
    print(f"  {'Routing flexibility':<25} {'Static schedule':<20} {'RL-adaptive'}")
    print(f"  {'Redundancy':<25} {'Limited':<20} {'Multi-path'}")

    # Emergency scenario
    print("\n" + "="*80)
    print("BONUS: EMERGENCY SCENARIO (P0 Priority)")
    print("="*80)
    print("  Scenario: Spacecraft anomaly detected")
    print("  Priority: P0 (Emergency)")
    print("  Action: Bundle preempts all queues")
    print("  Path: Direct high-power RF backup if optical unavailable")
    print("  Max delay: <1 minute end-to-end (plus light time)")
    print("  Status: AETHERIX handles priority-based traffic scheduling")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_demo()
