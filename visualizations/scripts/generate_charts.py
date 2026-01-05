#!/usr/bin/env python3
"""
AETHERIX Visualization Generator
Generates charts and diagrams for the presentation.

Requirements:
    pip install matplotlib numpy
"""

import sys
import os
import math

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


def generate_light_time_delay_chart(output_dir: str):
    """Generate chart showing one-way light time delay vs distance."""
    if not HAS_MATPLOTLIB:
        print("Skipping light time delay chart (matplotlib not installed)")
        return

    # Speed of light in km/s
    c = 299792.458

    # Distance range from minimum to maximum Earth-Mars distance
    distances_km = np.linspace(54.6e6, 401e6, 100)
    light_times_min = (distances_km / c) / 60  # Convert to minutes

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(distances_km / 1e6, light_times_min, 'purple', linewidth=2.5)
    ax.fill_between(distances_km / 1e6, light_times_min, alpha=0.2, color='purple')

    # Mark key distances
    key_distances = [54.6, 225, 401]  # Million km
    key_names = ['Opposition\n(Closest)', 'Average', 'Conjunction\n(Farthest)']
    for dist, name in zip(key_distances, key_names):
        lt = (dist * 1e6 / c) / 60
        ax.axvline(x=dist, color='gray', linestyle='--', alpha=0.5)
        ax.scatter([dist], [lt], s=100, zorder=5, color='red')
        ax.annotate(f'{name}\n{lt:.1f} min', xy=(dist, lt),
                    xytext=(dist + 20, lt + 1), fontsize=9,
                    arrowprops=dict(arrowstyle='->', color='gray', alpha=0.7))

    ax.set_xlabel('Earth-Mars Distance (Million km)', fontsize=12)
    ax.set_ylabel('One-Way Light Time (minutes)', fontsize=12)
    ax.set_title('Communication Delay: Light Time vs Distance', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(50, 420)
    ax.set_ylim(0, 25)

    # Add RTT annotation
    ax.text(300, 5, 'Note: Round-trip time = 2× one-way delay\n'
                    'Commands take 6-44 minutes for response',
            fontsize=9, style='italic',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'light_time_delay.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/light_time_delay.png")


def generate_link_budget_breakdown_chart(output_dir: str):
    """Generate waterfall chart showing link budget components."""
    if not HAS_MATPLOTLIB:
        print("Skipping link budget breakdown chart (matplotlib not installed)")
        return

    # Link budget components (at 225 million km average distance)
    components = [
        'Tx Power\n(5W laser)', 'Tx Antenna\nGain', 'Tx Losses',
        'Free Space\nLoss', 'Atm Loss',
        'Rx Antenna\nGain', 'Rx Losses', 'Link\nMargin'
    ]
    values = [37.0, 108.5, -3.0, -375.3, -3.0, 123.4, -4.5, 3.1]

    # Calculate running total for waterfall
    running_total = []
    total = 0
    for v in values[:-1]:  # Exclude link margin
        total += v
        running_total.append(total)
    running_total.append(values[-1])  # Add link margin as separate

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#2ecc71' if v > 0 else '#e74c3c' for v in values]
    colors[-1] = '#3498db'  # Link margin in blue

    x = np.arange(len(components))
    bars = ax.bar(x, values, color=colors, edgecolor='black', linewidth=0.5)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        label_y = height / 2 if height > 0 else height / 2
        ax.annotate(f'{val:+.1f} dB',
                    xy=(bar.get_x() + bar.get_width() / 2, label_y),
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    color='white' if abs(height) > 20 else 'black')

    ax.set_xticks(x)
    ax.set_xticklabels(components, fontsize=10)
    ax.set_ylabel('Power Level (dB/dBm)', fontsize=12)
    ax.set_title('AETHERIX Optical Link Budget Breakdown (225M km)', fontsize=14, fontweight='bold')
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.grid(True, alpha=0.3, axis='y')

    # Add legend
    legend_elements = [
        mpatches.Patch(color='#2ecc71', label='Gain (+dB)'),
        mpatches.Patch(color='#e74c3c', label='Loss (-dB)'),
        mpatches.Patch(color='#3498db', label='Link Margin')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'link_budget_breakdown.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/link_budget_breakdown.png")


def generate_qkd_performance_chart(output_dir: str):
    """Generate chart showing QKD key rate vs distance."""
    if not HAS_MATPLOTLIB:
        print("Skipping QKD performance chart (matplotlib not installed)")
        return

    # Distance ranges (in km)
    distances_leo = np.linspace(400, 2000, 20)  # LEO satellites
    distances_geo = np.linspace(2000, 40000, 20)  # GEO range
    distances_deep = np.linspace(40000, 400000, 20)  # Cislunar/beyond

    def key_rate(distance_km):
        """Simplified QKD key rate model."""
        base_rate = 10000  # bps at 500 km
        attenuation = 0.0001  # per km
        if distance_km < 2000:
            return base_rate * math.exp(-attenuation * distance_km)
        elif distance_km < 40000:
            return base_rate * math.exp(-attenuation * distance_km) / 10
        else:
            return max(1, base_rate * math.exp(-attenuation * 40000) / 100)

    rates_leo = [key_rate(d) for d in distances_leo]
    rates_geo = [key_rate(d) for d in distances_geo]
    rates_deep = [key_rate(d) for d in distances_deep]

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.semilogy(distances_leo / 1000, rates_leo, 'g-', linewidth=2, label='LEO Range')
    ax.semilogy(distances_geo / 1000, rates_geo, 'b-', linewidth=2, label='GEO Range')
    ax.semilogy(distances_deep / 1000, rates_deep, 'r--', linewidth=2, label='Deep Space (w/ Repeaters)')

    # Mark key milestones
    milestones = [
        (0.5, 'LEO\n(500 km)', 'green'),
        (36, 'GEO\n(36,000 km)', 'blue'),
        (380, 'Moon\n(380,000 km)', 'red')
    ]
    for dist, name, color in milestones:
        rate = key_rate(dist * 1000)
        ax.scatter([dist], [rate], s=100, c=color, zorder=5, edgecolor='black')
        ax.annotate(name, xy=(dist, rate), xytext=(dist * 1.1, rate * 2),
                    fontsize=9, arrowprops=dict(arrowstyle='->', color=color))

    ax.set_xlabel('Distance (× 1000 km)', fontsize=12)
    ax.set_ylabel('Key Rate (bits/second)', fontsize=12)
    ax.set_title('QKD Key Generation Rate vs Distance', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(loc='upper right', fontsize=10)

    # Add security threshold annotation
    ax.axhline(y=100, color='orange', linestyle=':', alpha=0.7)
    ax.text(200, 130, 'Minimum practical rate (100 bps)', fontsize=9, color='orange')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'qkd_key_rate.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/qkd_key_rate.png")


def generate_network_tier_distribution(output_dir: str):
    """Generate pie/donut chart showing network node distribution across tiers."""
    if not HAS_MATPLOTLIB:
        print("Skipping network tier distribution chart (matplotlib not installed)")
        return

    # Node counts per tier (from AETHERIX architecture)
    tiers = ['Tier 1:\nEarth Ground', 'Tier 2:\nEarth Orbital',
             'Tier 3:\nDeep Space', 'Tier 4:\nMars Orbital', 'Tier 5:\nMars Surface']
    nodes = [6, 51, 4, 4, 167]
    colors = ['#3498db', '#2ecc71', '#9b59b6', '#e74c3c', '#f39c12']
    explode = (0.02, 0.02, 0.05, 0.02, 0.02)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Pie chart
    wedges, texts, autotexts = ax1.pie(nodes, labels=tiers, autopct='%1.1f%%',
                                        colors=colors, explode=explode,
                                        startangle=90, pctdistance=0.75)
    ax1.set_title('AETHERIX Network Node Distribution', fontsize=14, fontweight='bold')

    # Bar chart for absolute numbers
    x = np.arange(len(tiers))
    bars = ax2.bar(x, nodes, color=colors, edgecolor='black', linewidth=0.5)

    # Add value labels
    for bar, n in zip(bars, nodes):
        ax2.annotate(f'{n}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax2.set_xticks(x)
    ax2.set_xticklabels([t.replace('\n', ' ') for t in tiers], fontsize=9, rotation=15)
    ax2.set_ylabel('Number of Nodes', fontsize=12)
    ax2.set_title(f'Total Network: {sum(nodes)} Nodes', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'network_tier_distribution.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/network_tier_distribution.png")


def generate_contact_windows_chart(output_dir: str):
    """Generate chart showing contact window availability over synodic period."""
    if not HAS_MATPLOTLIB:
        print("Skipping contact windows chart (matplotlib not installed)")
        return

    # Simulate contact windows over synodic period (780 days)
    days = np.arange(0, 780, 1)

    # Model distance variation
    min_dist = 54.6  # Million km
    max_dist = 401   # Million km
    avg_dist = (min_dist + max_dist) / 2
    amplitude = (max_dist - min_dist) / 2
    distances = avg_dist + amplitude * np.cos(2 * np.pi * days / 780)

    # Model data rate (inverse square)
    max_rate = 200  # Mbps at min distance
    data_rates = np.array([max(2, max_rate * (min_dist / d) ** 2) for d in distances])

    # Model contact duration (hours/day) - affected by geometry
    phase = 2 * np.pi * days / 780
    base_duration = 8  # hours
    # Reduced during conjunction (around day 390)
    conjunction_effect = np.clip(np.abs(np.sin(phase)), 0.1, 1.0)
    contact_duration = base_duration * conjunction_effect

    # Solar conjunction blackout (~14 days centered around day 390)
    blackout_mask = (days >= 383) & (days <= 397)
    contact_duration[blackout_mask] = 0
    data_rates[blackout_mask] = 0

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Plot 1: Distance
    ax1.plot(days, distances, 'b-', linewidth=1.5)
    ax1.fill_between(days, distances, alpha=0.3)
    ax1.axvspan(383, 397, alpha=0.3, color='red', label='Solar Conjunction Blackout')
    ax1.set_ylabel('Distance\n(Million km)', fontsize=11)
    ax1.set_title('Earth-Mars Communication Windows Over Synodic Period', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Data Rate
    ax2.plot(days, data_rates, 'g-', linewidth=1.5)
    ax2.fill_between(days, data_rates, alpha=0.3, color='green')
    ax2.axvspan(383, 397, alpha=0.3, color='red')
    ax2.set_ylabel('Max Data Rate\n(Mbps)', fontsize=11)
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)

    # Plot 3: Contact Duration
    ax3.bar(days, contact_duration, width=1, color='purple', alpha=0.7)
    ax3.axvspan(383, 397, alpha=0.3, color='red')
    ax3.set_xlabel('Days from Opposition', fontsize=12)
    ax3.set_ylabel('Contact Duration\n(hours/day)', fontsize=11)
    ax3.set_ylim(0, 10)
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'contact_windows.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/contact_windows.png")


def generate_rl_routing_heatmap(output_dir: str):
    """Generate heatmap showing RL routing decisions based on network state."""
    if not HAS_MATPLOTLIB:
        print("Skipping RL routing heatmap (matplotlib not installed)")
        return

    # Simulated Q-values for routing decisions
    # Rows: Buffer occupancy levels (Low, Medium, High)
    # Columns: Link quality levels (Poor, Fair, Good, Excellent)
    buffer_levels = ['Low\n(0-30%)', 'Medium\n(30-70%)', 'High\n(70-100%)']
    link_quality = ['Poor\n(<0.3)', 'Fair\n(0.3-0.5)', 'Good\n(0.5-0.8)', 'Excellent\n(>0.8)']

    # Q-values for "Forward" action (higher = better)
    forward_q = np.array([
        [0.2, 0.5, 0.8, 0.95],  # Low buffer
        [0.15, 0.4, 0.7, 0.9],  # Medium buffer
        [0.1, 0.3, 0.5, 0.7]    # High buffer
    ])

    # Q-values for "Store" action
    store_q = np.array([
        [0.7, 0.4, 0.2, 0.1],  # Low buffer - more room to store
        [0.6, 0.5, 0.3, 0.15],  # Medium buffer
        [0.3, 0.4, 0.45, 0.25]  # High buffer - less room
    ])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Forward action heatmap
    im1 = axes[0].imshow(forward_q, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    axes[0].set_xticks(np.arange(len(link_quality)))
    axes[0].set_yticks(np.arange(len(buffer_levels)))
    axes[0].set_xticklabels(link_quality, fontsize=10)
    axes[0].set_yticklabels(buffer_levels, fontsize=10)
    axes[0].set_xlabel('Link Quality', fontsize=12)
    axes[0].set_ylabel('Buffer Occupancy', fontsize=12)
    axes[0].set_title('Q-Values: FORWARD Action', fontsize=13, fontweight='bold')

    # Add text annotations
    for i in range(len(buffer_levels)):
        for j in range(len(link_quality)):
            text = axes[0].text(j, i, f'{forward_q[i, j]:.2f}',
                               ha='center', va='center', color='black', fontsize=11, fontweight='bold')

    # Store action heatmap
    im2 = axes[1].imshow(store_q, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    axes[1].set_xticks(np.arange(len(link_quality)))
    axes[1].set_yticks(np.arange(len(buffer_levels)))
    axes[1].set_xticklabels(link_quality, fontsize=10)
    axes[1].set_yticklabels(buffer_levels, fontsize=10)
    axes[1].set_xlabel('Link Quality', fontsize=12)
    axes[1].set_ylabel('Buffer Occupancy', fontsize=12)
    axes[1].set_title('Q-Values: STORE Action', fontsize=13, fontweight='bold')

    for i in range(len(buffer_levels)):
        for j in range(len(link_quality)):
            text = axes[1].text(j, i, f'{store_q[i, j]:.2f}',
                               ha='center', va='center', color='black', fontsize=11, fontweight='bold')

    # Add colorbars
    fig.colorbar(im1, ax=axes[0], shrink=0.8, label='Q-Value')
    fig.colorbar(im2, ax=axes[1], shrink=0.8, label='Q-Value')

    fig.suptitle('AETHERIX RL Routing Agent: Decision Heatmaps', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rl_routing_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_dir}/rl_routing_heatmap.png")


def generate_bundle_priority_chart(output_dir: str):
    """Generate chart showing bundle priority classes and their characteristics."""
    if not HAS_MATPLOTLIB:
        print("Skipping bundle priority chart (matplotlib not installed)")
        return

    priorities = ['P0\nEMERGENCY', 'P1\nEXPEDITED', 'P2\nNORMAL', 'P3\nBULK', 'P4\nBEST_EFFORT']
    latency_tolerance = [5, 30, 120, 480, 1440]  # minutes
    delivery_guarantee = [99.99, 99.9, 99, 95, 90]  # percent
    example_data = ['Crew safety alerts', 'Science commands', 'Telemetry', 'Science data', 'Software updates']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    x = np.arange(len(priorities))
    colors = ['#e74c3c', '#e67e22', '#3498db', '#2ecc71', '#95a5a6']

    # Latency tolerance
    bars1 = ax1.bar(x, latency_tolerance, color=colors, edgecolor='black', linewidth=0.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(priorities, fontsize=10)
    ax1.set_ylabel('Max Latency Tolerance (minutes)', fontsize=12)
    ax1.set_title('BPv7 Bundle Priority: Latency Requirements', fontsize=13, fontweight='bold')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar, val, ex in zip(bars1, latency_tolerance, example_data):
        ax1.annotate(f'{val} min\n({ex})', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom', fontsize=8, rotation=0)

    # Delivery guarantee
    bars2 = ax2.bar(x, delivery_guarantee, color=colors, edgecolor='black', linewidth=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(priorities, fontsize=10)
    ax2.set_ylabel('Delivery Guarantee (%)', fontsize=12)
    ax2.set_title('BPv7 Bundle Priority: Reliability Requirements', fontsize=13, fontweight='bold')
    ax2.set_ylim(85, 101)
    ax2.grid(True, alpha=0.3, axis='y')

    # Add value labels
    for bar, val in zip(bars2, delivery_guarantee):
        ax2.annotate(f'{val}%', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bundle_priority_classes.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/bundle_priority_classes.png")


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


def generate_optical_vs_rf_comparison(output_dir: str):
    """Generate radar/spider chart comparing optical vs RF systems."""
    if not HAS_MATPLOTLIB:
        print("Skipping optical vs RF comparison chart (matplotlib not installed)")
        return

    categories = ['Data Rate', 'Power Efficiency', 'Pointing Accuracy',
                  'Weather Resilience', 'Heritage', 'Cost']
    
    # Scores out of 10
    optical_scores = [10, 9, 4, 3, 4, 5]
    rf_scores = [3, 5, 8, 9, 10, 7]
    
    # Number of variables
    N = len(categories)
    
    # Compute angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the loop
    
    optical_scores += optical_scores[:1]
    rf_scores += rf_scores[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    ax.plot(angles, optical_scores, 'b-', linewidth=2, label='Optical (1550nm)')
    ax.fill(angles, optical_scores, 'b', alpha=0.25)
    
    ax.plot(angles, rf_scores, 'r-', linewidth=2, label='RF (Ka-band)')
    ax.fill(angles, rf_scores, 'r', alpha=0.25)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 10)
    ax.set_title('Optical vs RF Communication Comparison', fontsize=14, fontweight='bold', y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'optical_vs_rf_radar.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_dir}/optical_vs_rf_radar.png")


def generate_mission_timeline_chart(output_dir: str):
    """Generate Gantt-style chart showing AETHERIX deployment phases."""
    if not HAS_MATPLOTLIB:
        print("Skipping mission timeline chart (matplotlib not installed)")
        return

    phases = [
        ('Phase 1: Earth Infrastructure', 2025, 2027, '#3498db'),
        ('Phase 2: Deep Space Relay', 2027, 2029, '#9b59b6'),
        ('Phase 3: Mars Orbital', 2029, 2031, '#e74c3c'),
        ('Phase 4: Mars Surface', 2031, 2033, '#f39c12'),
        ('Phase 5: Full Operations', 2033, 2040, '#2ecc71'),
    ]
    
    milestones = [
        (2026, 'First optical relay\nlaunch'),
        (2028, 'L4/L5 relay\noperational'),
        (2030, 'Mars orbit\ninsertion'),
        (2032, 'Surface mesh\ncomplete'),
        (2035, '100+ Mbps\nachieved'),
    ]

    fig, ax = plt.subplots(figsize=(14, 6))

    for i, (name, start, end, color) in enumerate(phases):
        ax.barh(i, end - start, left=start, height=0.6, color=color, 
                edgecolor='black', linewidth=0.5, label=name)
        ax.text(start + (end - start) / 2, i, name.split(':')[1].strip(), 
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')

    # Add milestones
    for year, label in milestones:
        ax.axvline(x=year, color='gray', linestyle='--', alpha=0.5)
        ax.annotate(label, xy=(year, len(phases) - 0.5), xytext=(year, len(phases) + 0.3),
                    ha='center', fontsize=8, arrowprops=dict(arrowstyle='->', color='gray'))

    ax.set_yticks(range(len(phases)))
    ax.set_yticklabels([p[0].split(':')[0] for p in phases], fontsize=10)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_title('AETHERIX Deployment Timeline', fontsize=14, fontweight='bold')
    ax.set_xlim(2024, 2041)
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mission_timeline.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/mission_timeline.png")


def generate_dsn_coverage_chart(output_dir: str):
    """Generate chart showing DSN ground station coverage."""
    if not HAS_MATPLOTLIB:
        print("Skipping DSN coverage chart (matplotlib not installed)")
        return

    # DSN station longitudes and coverage windows
    stations = {
        'Goldstone (USA)': {'lon': -117, 'color': '#3498db'},
        'Madrid (Spain)': {'lon': -4, 'color': '#e74c3c'},
        'Canberra (Australia)': {'lon': 149, 'color': '#2ecc71'}
    }
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    
    # Top: World map style coverage
    hours = np.arange(0, 24, 0.1)
    
    for name, info in stations.items():
        # Each station has ~8-10 hour visibility window
        center_hour = (info['lon'] + 180) / 15  # Convert longitude to hour
        visibility = np.exp(-0.5 * ((hours - center_hour) / 3) ** 2) * 100
        visibility = np.maximum(visibility, np.exp(-0.5 * ((hours - center_hour + 24) / 3) ** 2) * 100)
        visibility = np.maximum(visibility, np.exp(-0.5 * ((hours - center_hour - 24) / 3) ** 2) * 100)
        
        ax1.fill_between(hours, visibility, alpha=0.4, color=info['color'], label=name)
        ax1.plot(hours, visibility, color=info['color'], linewidth=2)
    
    ax1.set_xlabel('UTC Hour', fontsize=12)
    ax1.set_ylabel('Visibility (%)', fontsize=12)
    ax1.set_title('Deep Space Network Station Coverage (24-hour cycle)', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 24)
    ax1.set_ylim(0, 110)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(range(0, 25, 2))
    
    # Bottom: Combined coverage showing overlap
    combined = np.zeros_like(hours)
    for name, info in stations.items():
        center_hour = (info['lon'] + 180) / 15
        visibility = np.exp(-0.5 * ((hours - center_hour) / 3) ** 2)
        visibility = np.maximum(visibility, np.exp(-0.5 * ((hours - center_hour + 24) / 3) ** 2))
        visibility = np.maximum(visibility, np.exp(-0.5 * ((hours - center_hour - 24) / 3) ** 2))
        combined += visibility
    
    ax2.fill_between(hours, combined, alpha=0.6, color='purple')
    ax2.plot(hours, combined, 'purple', linewidth=2)
    ax2.axhline(y=1, color='orange', linestyle='--', label='Single station coverage')
    ax2.axhline(y=2, color='red', linestyle='--', label='Dual station overlap')
    
    ax2.set_xlabel('UTC Hour', fontsize=12)
    ax2.set_ylabel('Station Overlap', fontsize=12)
    ax2.set_title('Combined DSN Coverage (Overlap indicates redundancy)', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 24)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(range(0, 25, 2))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'dsn_coverage.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/dsn_coverage.png")


def generate_qber_security_chart(output_dir: str):
    """Generate chart showing QBER vs security for QKD protocols."""
    if not HAS_MATPLOTLIB:
        print("Skipping QBER security chart (matplotlib not installed)")
        return

    qber_values = np.linspace(0, 0.20, 100)
    
    # Security margin decreases as QBER increases
    # At 11% QBER, security is compromised
    security_margin = np.maximum(0, 1 - qber_values / 0.11)
    
    # Key rate also decreases
    key_rate_factor = np.maximum(0, 1 - 2 * qber_values)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Security margin plot
    ax1.fill_between(qber_values * 100, security_margin * 100, alpha=0.3, color='green',
                     where=(qber_values < 0.11))
    ax1.fill_between(qber_values * 100, security_margin * 100, alpha=0.3, color='red',
                     where=(qber_values >= 0.11))
    ax1.plot(qber_values * 100, security_margin * 100, 'b-', linewidth=2)
    ax1.axvline(x=11, color='red', linestyle='--', linewidth=2, label='Security Threshold (11%)')
    ax1.axvspan(11, 20, alpha=0.2, color='red')
    
    ax1.set_xlabel('Quantum Bit Error Rate (QBER) %', fontsize=12)
    ax1.set_ylabel('Security Margin (%)', fontsize=12)
    ax1.set_title('QKD Security vs QBER', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 20)
    ax1.set_ylim(0, 105)
    
    # Add annotations
    ax1.annotate('SECURE\nZONE', xy=(5, 50), fontsize=14, color='green', fontweight='bold', ha='center')
    ax1.annotate('INSECURE\n(Eavesdropper\ndetected)', xy=(15, 30), fontsize=11, color='red', 
                 fontweight='bold', ha='center')
    
    # Simulated QBER scenarios
    scenarios = ['Ideal\nChannel', 'LEO\nSatellite', 'GEO\nSatellite', 'With\nEavesdropper']
    qber_scenario = [1, 3, 7, 25]
    colors = ['green', 'lightgreen', 'orange', 'red']
    
    bars = ax2.bar(scenarios, qber_scenario, color=colors, edgecolor='black', linewidth=0.5)
    ax2.axhline(y=11, color='red', linestyle='--', linewidth=2, label='Security Threshold')
    
    for bar, val in zip(bars, qber_scenario):
        ax2.annotate(f'{val}%', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_ylabel('QBER (%)', fontsize=12)
    ax2.set_title('QBER by Channel Scenario', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 30)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'qkd_security.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/qkd_security.png")


def generate_latency_comparison_chart(output_dir: str):
    """Generate chart comparing latency across different space communication scenarios."""
    if not HAS_MATPLOTLIB:
        print("Skipping latency comparison chart (matplotlib not installed)")
        return

    scenarios = ['Earth\nSurface', 'LEO\nSatellite', 'GEO\nSatellite', 'Moon', 
                 'Mars\n(Closest)', 'Mars\n(Farthest)']
    distances_km = [0, 550, 36000, 384400, 54.6e6, 401e6]
    
    # Calculate round-trip times in seconds
    c = 299792.458  # km/s
    rtt_seconds = [2 * d / c for d in distances_km]
    rtt_seconds[0] = 0.001  # Set Earth surface to 1ms for visualization
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#2ecc71', '#3498db', '#9b59b6', '#f39c12', '#e74c3c', '#c0392b']
    bars = ax.bar(scenarios, rtt_seconds, color=colors, edgecolor='black', linewidth=0.5)
    
    ax.set_yscale('log')
    ax.set_ylabel('Round-Trip Time (seconds)', fontsize=12)
    ax.set_title('Communication Latency Across Space Distances', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, rtt in zip(bars, rtt_seconds):
        if rtt < 1:
            label = f'{rtt*1000:.0f} ms'
        elif rtt < 60:
            label = f'{rtt:.1f} s'
        else:
            label = f'{rtt/60:.0f} min'
        ax.annotate(label, xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add reference lines
    ax.axhline(y=1, color='gray', linestyle=':', alpha=0.7)
    ax.text(5.5, 1.3, '1 second', fontsize=9, color='gray')
    ax.axhline(y=60, color='gray', linestyle=':', alpha=0.7)
    ax.text(5.5, 75, '1 minute', fontsize=9, color='gray')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'latency_comparison.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/latency_comparison.png")


def generate_bandwidth_evolution_chart(output_dir: str):
    """Generate chart showing evolution of Mars communication bandwidth over time."""
    if not HAS_MATPLOTLIB:
        print("Skipping bandwidth evolution chart (matplotlib not installed)")
        return

    # Historical and projected data rates
    missions = ['Viking\n(1976)', 'MGS\n(1997)', 'MRO\n(2006)', 'MAVEN\n(2014)', 
                'AETHERIX\nPhase 1\n(2028)', 'AETHERIX\nPhase 2\n(2032)', 'AETHERIX\nFull\n(2035)']
    years = [1976, 1997, 2006, 2014, 2028, 2032, 2035]
    data_rates_kbps = [16, 85, 6000, 10000, 50000, 100000, 200000]  # in kbps
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot historical vs projected
    historical = [r for r, y in zip(data_rates_kbps, years) if y <= 2024]
    projected = [r for r, y in zip(data_rates_kbps, years) if y > 2024]
    
    # All points
    ax.scatter(years[:4], data_rates_kbps[:4], s=150, c='#3498db', zorder=5, 
               edgecolor='black', label='Historical (RF)')
    ax.scatter(years[4:], data_rates_kbps[4:], s=150, c='#e74c3c', zorder=5, 
               edgecolor='black', marker='s', label='Projected (AETHERIX Optical)')
    
    # Connect with lines
    ax.plot(years[:4], data_rates_kbps[:4], 'b--', alpha=0.5)
    ax.plot(years[4:], data_rates_kbps[4:], 'r--', alpha=0.5)
    ax.plot([years[3], years[4]], [data_rates_kbps[3], data_rates_kbps[4]], 'g--', alpha=0.5)
    
    ax.set_yscale('log')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Maximum Data Rate (kbps)', fontsize=12)
    ax.set_title('Evolution of Mars Communication Bandwidth', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Add mission labels
    for mission, year, rate in zip(missions, years, data_rates_kbps):
        if rate < 10000:
            label = f'{rate} kbps'
        else:
            label = f'{rate/1000:.0f} Mbps'
        ax.annotate(f'{mission}\n{label}', xy=(year, rate), xytext=(year, rate * 2),
                    ha='center', fontsize=8, arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))
    
    # Highlight improvement factor
    ax.annotate('', xy=(2035, 200000), xytext=(2006, 6000),
                arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    ax.text(2020, 30000, '33× improvement\n(optical vs best RF)', 
            fontsize=10, color='green', fontweight='bold', ha='center',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bandwidth_evolution.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/bandwidth_evolution.png")


def generate_energy_efficiency_chart(output_dir: str):
    """Generate chart comparing energy efficiency of different communication technologies."""
    if not HAS_MATPLOTLIB:
        print("Skipping energy efficiency chart (matplotlib not installed)")
        return

    technologies = ['UHF Radio\n(400 MHz)', 'S-band\n(2 GHz)', 'X-band\n(8 GHz)', 
                    'Ka-band\n(32 GHz)', 'Optical\n(1550 nm)']
    # bits per Joule (approximate values at similar distances)
    efficiency_bpj = [100, 500, 2000, 10000, 50000]
    
    colors = ['#95a5a6', '#3498db', '#9b59b6', '#e74c3c', '#2ecc71']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar chart
    bars = ax1.bar(technologies, efficiency_bpj, color=colors, edgecolor='black', linewidth=0.5)
    ax1.set_yscale('log')
    ax1.set_ylabel('Energy Efficiency (bits/Joule)', fontsize=12)
    ax1.set_title('Communication Energy Efficiency by Technology', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar, eff in zip(bars, efficiency_bpj):
        ax1.annotate(f'{eff:,}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Power required to transmit 1 GB at Mars distance
    power_1gb_wh = [1e6 / e * 8 * 1e9 / 3600 for e in efficiency_bpj]  # Watt-hours
    
    bars2 = ax2.bar(technologies, power_1gb_wh, color=colors, edgecolor='black', linewidth=0.5)
    ax2.set_yscale('log')
    ax2.set_ylabel('Energy to Transmit 1 GB (Wh)', fontsize=12)
    ax2.set_title('Energy Required per Gigabyte (lower is better)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar, pwr in zip(bars2, power_1gb_wh):
        if pwr > 1000:
            label = f'{pwr/1000:.0f} kWh'
        else:
            label = f'{pwr:.0f} Wh'
        ax2.annotate(label, xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'energy_efficiency.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/energy_efficiency.png")


def generate_orbital_positions_chart(output_dir: str):
    """Generate chart showing Earth-Mars orbital positions."""
    if not HAS_MATPLOTLIB:
        print("Skipping orbital positions chart (matplotlib not installed)")
        return

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Create orbital paths
    theta = np.linspace(0, 2 * np.pi, 100)
    earth_r = 1.0  # AU
    mars_r = 1.52  # AU
    
    scenarios = [
        ('Opposition (Closest)', 0, np.pi),
        ('Quadrature', 0, np.pi/2),
        ('Conjunction (Farthest)', 0, 0)
    ]
    
    for ax, (title, earth_angle, mars_angle) in zip(axes, scenarios):
        # Draw Sun
        ax.scatter([0], [0], s=300, c='yellow', edgecolor='orange', linewidth=2, zorder=10, label='Sun')
        
        # Draw orbits
        ax.plot(earth_r * np.cos(theta), earth_r * np.sin(theta), 'b--', alpha=0.3, linewidth=1)
        ax.plot(mars_r * np.cos(theta), mars_r * np.sin(theta), 'r--', alpha=0.3, linewidth=1)
        
        # Draw planets
        earth_x, earth_y = earth_r * np.cos(earth_angle), earth_r * np.sin(earth_angle)
        mars_x, mars_y = mars_r * np.cos(mars_angle), mars_r * np.sin(mars_angle)
        
        ax.scatter([earth_x], [earth_y], s=150, c='blue', edgecolor='black', zorder=10, label='Earth')
        ax.scatter([mars_x], [mars_y], s=120, c='red', edgecolor='black', zorder=10, label='Mars')
        
        # Draw communication link
        ax.plot([earth_x, mars_x], [earth_y, mars_y], 'g-', linewidth=2, alpha=0.7, label='Comm Link')
        
        # Calculate distance
        distance = np.sqrt((mars_x - earth_x)**2 + (mars_y - earth_y)**2)
        
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect('equal')
        ax.set_title(f'{title}\n(Distance: {distance:.2f} AU)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if ax == axes[0]:
            ax.legend(loc='upper right', fontsize=8)
    
    fig.suptitle('Earth-Mars Orbital Configurations', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'orbital_positions.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Generated: {output_dir}/orbital_positions.png")


def generate_data_volume_chart(output_dir: str):
    """Generate chart showing daily data volume capabilities."""
    if not HAS_MATPLOTLIB:
        print("Skipping data volume chart (matplotlib not installed)")
        return

    # Data types and their typical sizes
    data_types = ['Housekeeping\nTelemetry', 'Science\nImages', 'Spectroscopy\nData', 
                  'Video\nStreaming', 'Software\nUpdates']
    
    # Daily volume in GB for different systems
    mro_volume = [0.1, 5, 2, 0, 0.5]  # Current MRO capabilities
    aetherix_volume = [1, 50, 20, 10, 5]  # AETHERIX capabilities
    
    x = np.arange(len(data_types))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars1 = ax.bar(x - width/2, mro_volume, width, label='Current (MRO)', color='#e74c3c')
    bars2 = ax.bar(x + width/2, aetherix_volume, width, label='AETHERIX', color='#2ecc71')
    
    ax.set_ylabel('Daily Data Volume (GB)', fontsize=12)
    ax.set_title('Daily Data Transfer Capability by Data Type', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(data_types, fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, val in zip(bars1, mro_volume):
        if val > 0:
            ax.annotate(f'{val}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        ha='center', va='bottom', fontsize=9)
    for bar, val in zip(bars2, aetherix_volume):
        ax.annotate(f'{val}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha='center', va='bottom', fontsize=9)
    
    # Add total comparison
    ax.text(0.02, 0.98, f'Total Daily: MRO={sum(mro_volume):.1f} GB, AETHERIX={sum(aetherix_volume)} GB',
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'data_volume.png'), dpi=150)
    plt.close()
    print(f"Generated: {output_dir}/data_volume.png")


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

    # Generate original charts (require matplotlib)
    print("\n--- Original Charts ---")
    generate_link_budget_chart(charts_dir)
    generate_performance_comparison(charts_dir)
    generate_distance_over_time(charts_dir)

    # Generate new charts
    print("\n--- Communication & Link Budget Charts ---")
    generate_light_time_delay_chart(charts_dir)
    generate_link_budget_breakdown_chart(charts_dir)
    generate_optical_vs_rf_comparison(charts_dir)
    generate_latency_comparison_chart(charts_dir)
    generate_bandwidth_evolution_chart(charts_dir)
    generate_energy_efficiency_chart(charts_dir)
    
    print("\n--- Network & Protocol Charts ---")
    generate_network_tier_distribution(charts_dir)
    generate_bundle_priority_chart(charts_dir)
    generate_dsn_coverage_chart(charts_dir)
    
    print("\n--- Security & QKD Charts ---")
    generate_qkd_performance_chart(charts_dir)
    generate_qber_security_chart(charts_dir)
    
    print("\n--- Orbital & Contact Charts ---")
    generate_contact_windows_chart(charts_dir)
    generate_orbital_positions_chart(charts_dir)
    
    print("\n--- RL Routing & Data Charts ---")
    generate_rl_routing_heatmap(charts_dir)
    generate_data_volume_chart(charts_dir)
    
    print("\n--- Mission Planning Charts ---")
    generate_mission_timeline_chart(charts_dir)

    # Generate text diagrams (no dependencies)
    print("\n--- Text Diagrams ---")
    generate_network_topology_text(diagrams_dir)
    generate_protocol_stack_text(diagrams_dir)

    print("\n" + "=" * 60)
    print("Visualization generation complete!")
    print(f"Generated charts in: {os.path.abspath(charts_dir)}")
    print(f"Generated diagrams in: {os.path.abspath(diagrams_dir)}")
    print("=" * 60)

    if not HAS_MATPLOTLIB:
        print("\nTo generate PNG charts, install matplotlib:")
        print("  pip install matplotlib numpy")


if __name__ == "__main__":
    main()
