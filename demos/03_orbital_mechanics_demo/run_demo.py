#!/usr/bin/env python3
"""
AETHERIX Orbital Mechanics Demo
Calculates Earth-Mars distance and communication windows.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


# Constants
AU_KM = 149_597_870.7  # 1 AU in km
SPEED_OF_LIGHT_KM_S = 299_792.458  # km/s
MARS_SEMI_MAJOR_AU = 1.524
MARS_ECCENTRICITY = 0.0934
EARTH_SEMI_MAJOR_AU = 1.0
EARTH_ECCENTRICITY = 0.0167
SYNODIC_PERIOD_DAYS = 779.94


@dataclass
class OrbitalPosition:
    """Position in the orbital plane."""
    distance_from_sun_au: float
    true_anomaly_deg: float
    x_au: float
    y_au: float


def calculate_orbital_radius(semi_major_au: float, eccentricity: float,
                             true_anomaly_deg: float) -> float:
    """Calculate orbital radius at a given true anomaly."""
    theta = math.radians(true_anomaly_deg)
    return semi_major_au * (1 - eccentricity**2) / (1 + eccentricity * math.cos(theta))


def calculate_position(semi_major_au: float, eccentricity: float,
                       true_anomaly_deg: float) -> OrbitalPosition:
    """Calculate position in orbital plane."""
    r = calculate_orbital_radius(semi_major_au, eccentricity, true_anomaly_deg)
    theta = math.radians(true_anomaly_deg)
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return OrbitalPosition(r, true_anomaly_deg, x, y)


def calculate_earth_mars_distance(earth_anomaly_deg: float,
                                   mars_anomaly_deg: float) -> float:
    """Calculate distance between Earth and Mars in km."""
    earth_pos = calculate_position(EARTH_SEMI_MAJOR_AU, EARTH_ECCENTRICITY, earth_anomaly_deg)
    mars_pos = calculate_position(MARS_SEMI_MAJOR_AU, MARS_ECCENTRICITY, mars_anomaly_deg)

    # Distance in AU
    dx = mars_pos.x_au - earth_pos.x_au
    dy = mars_pos.y_au - earth_pos.y_au
    distance_au = math.sqrt(dx**2 + dy**2)

    return distance_au * AU_KM


def calculate_light_time(distance_km: float) -> float:
    """Calculate one-way light time in seconds."""
    return distance_km / SPEED_OF_LIGHT_KM_S


def run_demo():
    """Run the orbital mechanics demonstration."""
    print("\n" + "="*80)
    print("       AETHERIX ORBITAL MECHANICS DEMONSTRATION")
    print("       Earth-Mars Distance and Communication Windows")
    print("="*80)

    print("\n" + "-"*80)
    print("ORBITAL PARAMETERS")
    print("-"*80)
    print(f"  Earth:")
    print(f"    Semi-major axis: {EARTH_SEMI_MAJOR_AU:.3f} AU")
    print(f"    Eccentricity: {EARTH_ECCENTRICITY:.4f}")
    print(f"    Orbital period: 365.25 days")
    print(f"")
    print(f"  Mars:")
    print(f"    Semi-major axis: {MARS_SEMI_MAJOR_AU:.3f} AU")
    print(f"    Eccentricity: {MARS_ECCENTRICITY:.4f}")
    print(f"    Orbital period: 687 days")
    print(f"")
    print(f"  Synodic Period: {SYNODIC_PERIOD_DAYS:.1f} days (Earth-Mars cycle)")
    print("-"*80)

    # Key scenarios
    scenarios = [
        ("Opposition (Closest)", 0, 180),      # Earth between Sun and Mars
        ("Quadrature East", 0, 90),            # Mars 90 degrees ahead
        ("Conjunction (Farthest)", 0, 0),      # Sun between Earth and Mars
        ("Quadrature West", 0, 270),           # Mars 90 degrees behind
        ("Current (Avg)", 45, 120),            # Typical configuration
    ]

    print("\n" + "="*80)
    print("EARTH-MARS DISTANCE SCENARIOS")
    print("="*80)
    print(f"  {'Scenario':<25} {'Distance (M km)':<18} {'Light Time':<15} {'Data Rate':<12}")
    print(f"  {'-'*25} {'-'*18} {'-'*15} {'-'*12}")

    for name, earth_deg, mars_deg in scenarios:
        distance_km = calculate_earth_mars_distance(earth_deg, mars_deg)
        light_time_s = calculate_light_time(distance_km)

        # Estimate data rate (inverse square relationship)
        min_distance = 54_600_000  # km at perihelion opposition
        max_rate = 200  # Mbps at minimum distance
        rate = max_rate * (min_distance / distance_km) ** 2
        rate = max(2, min(200, rate))  # Clamp between 2-200 Mbps

        print(f"  {name:<25} {distance_km/1e6:>15.1f}   {light_time_s/60:>12.1f} min   {rate:>8.1f} Mbps")

    # Calculate distance over synodic period
    print("\n" + "="*80)
    print("DISTANCE VARIATION OVER SYNODIC PERIOD (780 days)")
    print("="*80)

    # Sample at key points
    samples = 13
    print(f"\n  {'Day':<8} {'Earth Pos':<12} {'Mars Pos':<12} {'Distance (M km)':<18} {'Light Time'}")
    print(f"  {'-'*8} {'-'*12} {'-'*12} {'-'*18} {'-'*12}")

    min_dist = float('inf')
    max_dist = 0

    for i in range(samples):
        day = i * (SYNODIC_PERIOD_DAYS / (samples - 1))
        # Simplified: Earth moves ~1 deg/day, Mars moves ~0.524 deg/day
        earth_deg = (day * 0.9856) % 360
        mars_deg = (180 + day * 0.524) % 360  # Start at opposition

        distance_km = calculate_earth_mars_distance(earth_deg, mars_deg)
        light_time_s = calculate_light_time(distance_km)

        min_dist = min(min_dist, distance_km)
        max_dist = max(max_dist, distance_km)

        print(f"  {day:>6.0f}   {earth_deg:>8.1f} deg   {mars_deg:>8.1f} deg   {distance_km/1e6:>14.1f}    {light_time_s/60:>8.1f} min")

    print(f"\n  Distance Range: {min_dist/1e6:.1f} - {max_dist/1e6:.1f} million km")
    print(f"  Light Time Range: {calculate_light_time(min_dist)/60:.1f} - {calculate_light_time(max_dist)/60:.1f} minutes")

    # Contact windows
    print("\n" + "="*80)
    print("COMMUNICATION WINDOW ANALYSIS")
    print("="*80)

    windows = [
        ("Opposition (best)", "8-12 hours/day", "100-200 Mbps", "Excellent"),
        ("Favorable", "6-8 hours/day", "20-50 Mbps", "Good"),
        ("Average", "4-6 hours/day", "10-20 Mbps", "Adequate"),
        ("Poor (quadrature)", "2-4 hours/day", "5-10 Mbps", "Limited"),
        ("Conjunction", "0 hours/day", "N/A (relay only)", "Use L4/L5"),
    ]

    print(f"\n  {'Configuration':<20} {'Contact Time':<18} {'Data Rate':<18} {'Assessment'}")
    print(f"  {'-'*20} {'-'*18} {'-'*18} {'-'*15}")
    for config, contact, rate, assess in windows:
        print(f"  {config:<20} {contact:<18} {rate:<18} {assess}")

    # Doppler shift
    print("\n" + "-"*80)
    print("DOPPLER SHIFT CONSIDERATIONS")
    print("-"*80)
    print("  Maximum relative velocity: ~24 km/s")
    print("  At 1550 nm wavelength:")
    print("    Doppler shift: Δf/f = v/c ≈ 0.008%")
    print("    Frequency offset: ~15 GHz")
    print("  Compensation: Real-time tracking required")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_demo()
