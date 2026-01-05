"""
AETHERIX Orbital Mechanics Module
Contact window calculation and orbital dynamics.

Reference:
- Vallado, "Fundamentals of Astrodynamics" (2013)
- JPL Horizons System
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum


# Physical Constants
AU_KM = 149_597_870.7        # 1 AU in km
SPEED_OF_LIGHT_KM_S = 299_792.458  # km/s
EARTH_ORBITAL_PERIOD_DAYS = 365.25
MARS_ORBITAL_PERIOD_DAYS = 686.98
SYNODIC_PERIOD_DAYS = 779.94


class CelestialBody(Enum):
    """Solar system bodies relevant to AETHERIX."""
    SUN = "sun"
    EARTH = "earth"
    MARS = "mars"
    MOON = "moon"


@dataclass
class OrbitalElements:
    """Keplerian orbital elements."""
    semi_major_axis_au: float    # a
    eccentricity: float          # e
    inclination_deg: float       # i
    raan_deg: float              # Ω (right ascension of ascending node)
    arg_periapsis_deg: float     # ω
    mean_anomaly_deg: float      # M (at epoch)
    epoch_jd: float              # Julian date of epoch


# Standard orbital elements for planets
ORBITAL_ELEMENTS = {
    CelestialBody.EARTH: OrbitalElements(
        semi_major_axis_au=1.00000261,
        eccentricity=0.01671123,
        inclination_deg=0.00005,
        raan_deg=-11.26064,
        arg_periapsis_deg=102.94719,
        mean_anomaly_deg=100.46435,
        epoch_jd=2451545.0  # J2000
    ),
    CelestialBody.MARS: OrbitalElements(
        semi_major_axis_au=1.52371034,
        eccentricity=0.09339410,
        inclination_deg=1.84969142,
        raan_deg=49.55953,
        arg_periapsis_deg=286.53650,
        mean_anomaly_deg=355.45332,
        epoch_jd=2451545.0  # J2000
    )
}


@dataclass
class ContactWindow:
    """Represents a communication opportunity window."""
    start_time_jd: float
    end_time_jd: float
    duration_hours: float
    max_elevation_deg: float
    average_distance_km: float
    max_data_rate_mbps: float
    window_type: str  # "direct", "relay", "emergency"


@dataclass
class LinkGeometry:
    """Geometry parameters for a communication link."""
    distance_km: float
    light_time_seconds: float
    elevation_angle_deg: float
    azimuth_deg: float
    doppler_shift_hz: float


def calculate_orbital_radius(elements: OrbitalElements, true_anomaly_deg: float) -> float:
    """
    Calculate orbital radius at a given true anomaly.

    r = a(1-e²) / (1 + e·cos(ν))

    Args:
        elements: Orbital elements
        true_anomaly_deg: True anomaly in degrees

    Returns:
        Orbital radius in AU
    """
    nu = math.radians(true_anomaly_deg)
    a = elements.semi_major_axis_au
    e = elements.eccentricity

    r = a * (1 - e**2) / (1 + e * math.cos(nu))
    return r


def calculate_position_heliocentric(elements: OrbitalElements,
                                     true_anomaly_deg: float) -> Tuple[float, float, float]:
    """
    Calculate heliocentric position in AU.

    Returns (x, y, z) coordinates in the ecliptic plane.
    """
    r = calculate_orbital_radius(elements, true_anomaly_deg)
    nu = math.radians(true_anomaly_deg)
    omega = math.radians(elements.arg_periapsis_deg)
    Omega = math.radians(elements.raan_deg)
    i = math.radians(elements.inclination_deg)

    # Position in orbital plane
    x_orb = r * math.cos(nu)
    y_orb = r * math.sin(nu)

    # Rotate to ecliptic coordinates (simplified for low inclination)
    x = x_orb * (math.cos(omega)*math.cos(Omega) - math.sin(omega)*math.sin(Omega)*math.cos(i))
    y = x_orb * (math.cos(omega)*math.sin(Omega) + math.sin(omega)*math.cos(Omega)*math.cos(i))
    z = x_orb * math.sin(omega) * math.sin(i) + y_orb * math.cos(omega) * math.sin(i)

    return (x, y, z)


def calculate_earth_mars_distance(earth_anomaly_deg: float,
                                   mars_anomaly_deg: float) -> float:
    """
    Calculate distance between Earth and Mars.

    Args:
        earth_anomaly_deg: Earth's true anomaly
        mars_anomaly_deg: Mars's true anomaly

    Returns:
        Distance in km
    """
    earth_elements = ORBITAL_ELEMENTS[CelestialBody.EARTH]
    mars_elements = ORBITAL_ELEMENTS[CelestialBody.MARS]

    earth_pos = calculate_position_heliocentric(earth_elements, earth_anomaly_deg)
    mars_pos = calculate_position_heliocentric(mars_elements, mars_anomaly_deg)

    # Distance in AU
    dx = mars_pos[0] - earth_pos[0]
    dy = mars_pos[1] - earth_pos[1]
    dz = mars_pos[2] - earth_pos[2]
    distance_au = math.sqrt(dx**2 + dy**2 + dz**2)

    return distance_au * AU_KM


def calculate_light_time(distance_km: float) -> float:
    """
    Calculate one-way light time.

    Args:
        distance_km: Distance in km

    Returns:
        Light time in seconds
    """
    return distance_km / SPEED_OF_LIGHT_KM_S


def calculate_doppler_shift(relative_velocity_km_s: float,
                            frequency_hz: float) -> float:
    """
    Calculate Doppler frequency shift.

    Δf/f = v/c

    Args:
        relative_velocity_km_s: Relative velocity (positive = receding)
        frequency_hz: Carrier frequency

    Returns:
        Frequency shift in Hz
    """
    c = SPEED_OF_LIGHT_KM_S
    return frequency_hz * (relative_velocity_km_s / c)


def estimate_data_rate(distance_km: float) -> float:
    """
    Estimate achievable optical data rate based on distance.

    Uses inverse-square law from minimum distance baseline.

    Args:
        distance_km: Earth-Mars distance

    Returns:
        Data rate in Mbps
    """
    min_distance_km = 54.6e6  # Perihelion opposition
    max_rate_mbps = 200.0     # Rate at minimum distance

    # Inverse square relationship
    rate = max_rate_mbps * (min_distance_km / distance_km) ** 2

    # Clamp to reasonable range
    return max(2.0, min(200.0, rate))


def predict_contact_windows(start_day: int, duration_days: int,
                             ground_station: str = "dsn") -> List[ContactWindow]:
    """
    Predict communication windows over a time period.

    Simplified model - in production, use JPL Horizons for precise ephemeris.

    Args:
        start_day: Starting day of synodic period (0 = opposition)
        duration_days: Prediction duration
        ground_station: Ground station type

    Returns:
        List of predicted contact windows
    """
    windows = []

    for day in range(start_day, start_day + duration_days):
        # Simplified orbital position
        earth_anomaly = (day * 360 / EARTH_ORBITAL_PERIOD_DAYS) % 360
        mars_anomaly = (180 + day * 360 / MARS_ORBITAL_PERIOD_DAYS) % 360

        distance_km = calculate_earth_mars_distance(earth_anomaly, mars_anomaly)
        light_time = calculate_light_time(distance_km)

        # Estimate contact duration based on orbital geometry
        # Simplified: longer contacts when Mars is higher in sky
        phase_angle = abs(mars_anomaly - earth_anomaly)
        if phase_angle > 180:
            phase_angle = 360 - phase_angle

        # Near conjunction (phase ~0 or ~360): no direct contact
        if phase_angle < 10:
            continue  # Solar conjunction blackout

        # Contact duration varies with geometry
        base_duration = 8.0  # hours
        duration_factor = math.sin(math.radians(phase_angle))
        duration = base_duration * duration_factor

        if duration < 2:  # Minimum useful contact
            continue

        data_rate = estimate_data_rate(distance_km)

        window = ContactWindow(
            start_time_jd=2460000 + day,  # Simplified JD
            end_time_jd=2460000 + day + duration/24,
            duration_hours=duration,
            max_elevation_deg=45.0 * duration_factor,
            average_distance_km=distance_km,
            max_data_rate_mbps=data_rate,
            window_type="direct"
        )
        windows.append(window)

    return windows


def get_distance_timeline(num_points: int = 780) -> List[Tuple[int, float, float]]:
    """
    Generate Earth-Mars distance over synodic period.

    Returns:
        List of (day, distance_km, light_time_min) tuples
    """
    timeline = []

    for day in range(num_points):
        earth_anomaly = (day * 360 / EARTH_ORBITAL_PERIOD_DAYS) % 360
        mars_anomaly = (180 + day * 360 / MARS_ORBITAL_PERIOD_DAYS) % 360

        distance_km = calculate_earth_mars_distance(earth_anomaly, mars_anomaly)
        light_time_min = calculate_light_time(distance_km) / 60

        timeline.append((day, distance_km, light_time_min))

    return timeline


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("AETHERIX Orbital Mechanics")
    print("=" * 60)

    # Key distances
    print("\nEarth-Mars Distance Scenarios:")
    scenarios = [
        ("Opposition (min)", 0, 180),
        ("Quadrature", 0, 90),
        ("Conjunction (max)", 0, 0),
    ]

    for name, earth_deg, mars_deg in scenarios:
        dist = calculate_earth_mars_distance(earth_deg, mars_deg)
        lt = calculate_light_time(dist)
        rate = estimate_data_rate(dist)

        print(f"  {name}:")
        print(f"    Distance: {dist/1e6:.1f} million km")
        print(f"    Light time: {lt/60:.1f} minutes")
        print(f"    Data rate: {rate:.1f} Mbps")

    # Contact windows
    print("\nContact Window Prediction (next 30 days from opposition):")
    windows = predict_contact_windows(0, 30)
    for i, w in enumerate(windows[:5]):
        print(f"  Window {i+1}: {w.duration_hours:.1f} hrs, "
              f"{w.max_data_rate_mbps:.1f} Mbps, "
              f"Dist: {w.average_distance_km/1e6:.0f}M km")

    # Doppler
    print("\nDoppler Shift Example:")
    optical_freq = 193.4e12  # 1550nm
    velocity = 24.0  # km/s (max relative)
    shift = calculate_doppler_shift(velocity, optical_freq)
    print(f"  At 1550nm, {velocity} km/s relative velocity:")
    print(f"  Doppler shift: {shift/1e9:.2f} GHz")
