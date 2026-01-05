#!/usr/bin/env python3
"""
AETHERIX Visualization Generator
Generates charts and diagrams for the presentation.

Requirements:
    pip install matplotlib numpy
"""

import sys
import os

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: matplotlib not installed. Install with: pip install matplotlib numpy")


def generate_link_budget_chart(output_dir: str):
    """Generate chart showing data rate vs distance."""
    if not HAS_MATPLOTLIB:
        print("Skipping link budget chart (matplotlib not installed)")
        return

    # Data
    distances_km = [54.6e6, 100e6, 150e6, 200e6, 250e6, 300e6, 350e6, 401e6]
    distances_labels = ['55', '100', '150', '200', '250', '300', '350', '401']

    # Data rates (approximate inverse square relationship)
    min_distance = 54.6e6
    max_rate = 200  # Mbps at minimum distance
    optical_rates = [max(2, max_rate * (min_distance / d) ** 2) for d in distances_km]

    # Current RF system (MRO-like)
    rf_rates = [6, 5, 4, 3.5, 3, 2.5, 2, 1.5]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(distances_labels, optical_rates, 'b-o', linewidth=2, markersize=8, label='AETHERIX (Optical)')
    ax.plot(distances_labels, rf_rates, 'r--s', linewidth=2, markersize=8, label='Current RF (MRO)')

    ax.set_xlabel('Earth-Mars Distance (Million km)', fontsize=12)
    ax.set_ylabel('Data Rate (Mbps)', fontsize=12)
    ax.set_title('AETHERIX vs Current Systems: Data Rate vs Distance', fontsize=14, fontweight='bold')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=11)

    # Add annotations
    ax.annotate('10-100x\nimprovement', xy=(1, 80), fontsize=10, color='green',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'data_rate_vs_distance.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/data_rate_vs_distance.png")


def generate_performance_comparison(output_dir: str):
    """Generate bar chart comparing AETHERIX vs current systems."""
    if not HAS_MATPLOTLIB:
        print("Skipping performance comparison chart (matplotlib not installed)")
        return

    categories = ['Downlink\n(Mbps)', 'Daily Data\n(GB)', 'Availability\n(%)', 'Scalability\n(nodes)']
    current = [6, 10, 75, 10]
    aetherix = [200, 100, 95, 100]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, current, width, label='Current (MRO)', color='#ff6b6b')
    bars2 = ax.bar(x + width/2, aetherix, width, label='AETHERIX', color='#4ecdc4')

    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Performance Comparison: AETHERIX vs Current Mars Systems', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=11)
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar, val in zip(bars1, current):
        ax.annotate(f'{val}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha='center', va='bottom', fontsize=9)
    for bar, val in zip(bars2, aetherix):
        ax.annotate(f'{val}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'performance_comparison.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/performance_comparison.png")


def generate_distance_over_time(output_dir: str):
    """Generate chart showing Earth-Mars distance over synodic period."""
    if not HAS_MATPLOTLIB:
        print("Skipping distance chart (matplotlib not installed)")
        return

    # Simplified model of Earth-Mars distance over synodic period
    days = np.linspace(0, 780, 100)

    # Model: opposition at day 0, conjunction at day 390
    # Using simplified sinusoidal approximation
    min_dist = 54.6  # Million km
    max_dist = 401   # Million km
    avg_dist = (min_dist + max_dist) / 2
    amplitude = (max_dist - min_dist) / 2

    distances = avg_dist + amplitude * np.cos(2 * np.pi * days / 780)

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(days, distances, 'b-', linewidth=2)
    ax.fill_between(days, distances, alpha=0.3)

    # Mark key points
    ax.axhline(y=min_dist, color='g', linestyle='--', alpha=0.7, label='Minimum (Opposition)')
    ax.axhline(y=max_dist, color='r', linestyle='--', alpha=0.7, label='Maximum (Conjunction)')

    # Mark opposition and conjunction
    ax.annotate('Opposition\n(Best comms)', xy=(0, min_dist), xytext=(50, 100),
                fontsize=10, arrowprops=dict(arrowstyle='->', color='green'))
    ax.annotate('Conjunction\n(Blackout)', xy=(390, max_dist), xytext=(320, 350),
                fontsize=10, arrowprops=dict(arrowstyle='->', color='red'))

    ax.set_xlabel('Days from Opposition', fontsize=12)
    ax.set_ylabel('Earth-Mars Distance (Million km)', fontsize=12)
    ax.set_title('Earth-Mars Distance Over Synodic Period (780 days)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 780)
    ax.set_ylim(0, 450)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'distance_over_time.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/distance_over_time.png")


def generate_network_topology_text(output_dir: str):
    """Generate text-based network topology diagram."""
    topology = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                      AETHERIX 5-TIER NETWORK TOPOLOGY                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │ TIER 1: EARTH GROUND (6 nodes)                                      │    ║
║  │   [DSN Goldstone] ◄──► [DSN Madrid] ◄──► [DSN Canberra]            │    ║
║  │         │                   │                   │                   │    ║
║  │         └───────────────────┼───────────────────┘                   │    ║
║  │                             │                                       │    ║
║  └─────────────────────────────┼───────────────────────────────────────┘    ║
║                                │ Optical/RF                                  ║
║  ┌─────────────────────────────┼───────────────────────────────────────┐    ║
║  │ TIER 2: EARTH ORBITAL (51 nodes)                                    │    ║
║  │   [GEO Atlantic]──[GEO Pacific]──[GEO Indian]                      │    ║
║  │         │              │              │                             │    ║
║  │   ┌─────┴──────────────┴──────────────┴─────┐                      │    ║
║  │   │     LEO Laser Constellation (48 sats)   │                      │    ║
║  │   └──────────────────────┬──────────────────┘                      │    ║
║  └──────────────────────────┼──────────────────────────────────────────┘    ║
║                             │ Optical (12.5 min light-time)                  ║
║  ┌──────────────────────────┼──────────────────────────────────────────┐    ║
║  │ TIER 3: DEEP SPACE TRANSIT (4 nodes)                                │    ║
║  │                          │                                          │    ║
║  │   [ES-L4 Relay] ◄────────┼────────► [ES-L5 Relay]                  │    ║
║  │         │                │                │                         │    ║
║  │         │         [Transfer Relays]       │                         │    ║
║  │         └────────────────┼────────────────┘                         │    ║
║  └──────────────────────────┼──────────────────────────────────────────┘    ║
║                             │ Optical                                        ║
║  ┌──────────────────────────┼──────────────────────────────────────────┐    ║
║  │ TIER 4: MARS ORBITAL (4 nodes)                                      │    ║
║  │         │                │                │                         │    ║
║  │   [MRS-Alpha] ◄──────────┼──────────► [MRS-Beta]                   │    ║
║  │   (Areostat)        ◄────┼────►      (Areostat)                    │    ║
║  │         │          [MRS-Gamma]            │                         │    ║
║  │         │           (Polar)               │                         │    ║
║  │         └────────────────┼────────────────┘                         │    ║
║  └──────────────────────────┼──────────────────────────────────────────┘    ║
║                             │ UHF/Optical                                    ║
║  ┌──────────────────────────┼──────────────────────────────────────────┐    ║
║  │ TIER 5: MARS SURFACE (167 nodes)                                    │    ║
║  │                          │                                          │    ║
║  │   [Base-α]───[Base-β]───[Rovers]───[Drones]───[Sensors]            │    ║
║  │      │          │          │          │          │                  │    ║
║  │      └──────────┴──────────┴──────────┴──────────┘                  │    ║
║  │            Distributed Sensor Network (UHF Mesh)                    │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    filepath = os.path.join(output_dir, 'network_topology.txt')
    with open(filepath, 'w') as f:
        f.write(topology)
    print(f"Generated: {filepath}")


def generate_protocol_stack_text(output_dir: str):
    """Generate text-based protocol stack diagram."""
    stack = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        AETHERIX PROTOCOL STACK                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌────────────────────────────────────────────────────────────────────┐     ║
║  │                    APPLICATION LAYER                                │     ║
║  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │     ║
║  │  │ Science Data │ │   Commands   │ │  Telemetry   │                │     ║
║  │  └──────────────┘ └──────────────┘ └──────────────┘                │     ║
║  └────────────────────────────────────────────────────────────────────┘     ║
║                                  │                                           ║
║                                  ▼                                           ║
║  ┌────────────────────────────────────────────────────────────────────┐     ║
║  │           BUNDLE PROTOCOL v7 (RFC 9171 / CCSDS 735.1)              │     ║
║  │  ┌────────────────────────────────────────────────────────────┐    │     ║
║  │  │ • Store-and-Forward       • Custody Transfer               │    │     ║
║  │  │ • Priority Scheduling     • Bundle Fragmentation           │    │     ║
║  │  │ • RL-Enhanced Routing     • Lifetime Management            │    │     ║
║  │  └────────────────────────────────────────────────────────────┘    │     ║
║  └────────────────────────────────────────────────────────────────────┘     ║
║                                  │                                           ║
║            ┌─────────────────────┼─────────────────────┐                    ║
║            ▼                     ▼                     ▼                    ║
║  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐            ║
║  │  LTP (RFC 5326)  │ │ TCPCL (RFC 7242) │ │     UDP-CL       │            ║
║  │                  │ │                  │ │                  │            ║
║  │ • Deep space     │ │ • Earth segment  │ │ • Optical ISL    │            ║
║  │ • Link-layer RTX │ │ • Reliable conn  │ │ • Low overhead   │            ║
║  │ • Red/Green data │ │ • Standard TCP   │ │ • Best effort    │            ║
║  └──────────────────┘ └──────────────────┘ └──────────────────┘            ║
║            │                     │                     │                    ║
║            └─────────────────────┼─────────────────────┘                    ║
║                                  ▼                                           ║
║  ┌────────────────────────────────────────────────────────────────────┐     ║
║  │                    PHYSICAL / DATA LINK LAYER                       │     ║
║  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐          │     ║
║  │  │ Optical 1550nm │ │  RF Ka-band    │ │    RF UHF      │          │     ║
║  │  │ 2-200 Mbps     │ │ 500k-10 Mbps   │ │ 128k-2 Mbps    │          │     ║
║  │  │ Primary link   │ │ Backup link    │ │ Surface links  │          │     ║
║  │  └────────────────┘ └────────────────┘ └────────────────┘          │     ║
║  └────────────────────────────────────────────────────────────────────┘     ║
║                                                                              ║
║  STANDARDS: CCSDS 734.2-B-1 (DTN), CCSDS 141.0-B-1 (Optical),              ║
║             CCSDS 142.0-B-2 (LNIS v5), RFC 9171 (BPv7)                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    filepath = os.path.join(output_dir, 'protocol_stack.txt')
    with open(filepath, 'w') as f:
        f.write(stack)
    print(f"Generated: {filepath}")


def main():
    """Generate all visualizations."""
    # Determine output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    charts_dir = os.path.join(script_dir, '..', 'charts')
    diagrams_dir = os.path.join(script_dir, '..', 'diagrams')

    # Create directories
    os.makedirs(charts_dir, exist_ok=True)
    os.makedirs(diagrams_dir, exist_ok=True)

    print("=" * 60)
    print("AETHERIX Visualization Generator")
    print("=" * 60)

    # Generate charts (require matplotlib)
    generate_link_budget_chart(charts_dir)
    generate_performance_comparison(charts_dir)
    generate_distance_over_time(charts_dir)

    # Generate text diagrams (no dependencies)
    generate_network_topology_text(diagrams_dir)
    generate_protocol_stack_text(diagrams_dir)

    print("\n" + "=" * 60)
    print("Visualization generation complete!")
    print("=" * 60)

    if not HAS_MATPLOTLIB:
        print("\nTo generate PNG charts, install matplotlib:")
        print("  pip install matplotlib numpy")


if __name__ == "__main__":
    main()
