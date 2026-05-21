"""Celestial body data for the AETHERIX Earth-Mars DTN simulation."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PhysicalConstants:
    name: str
    value: float
    unit: str
    description: str


SPEED_OF_LIGHT = PhysicalConstants("speed_of_light", 299792.458, "km/s", "Speed of light in vacuum")
AU_KM = PhysicalConstants("astronomical_unit", 149597870.7, "km", "1 AU")
GRAVITATIONAL_PARAMETER_SUN = PhysicalConstants("mu_sun", 1.32712440018e11, "km^3/s^2", "Sun gravitational parameter")


@dataclass(frozen=True)
class CelestialBodyData:
    name: str
    mass_kg: float
    radius_km: float
    semi_major_axis_au: float
    orbital_period_days: float
    eccentricity: float
    inclination_deg: float
    mean_anomaly_at_epoch_deg: float


BODIES: dict[str, CelestialBodyData] = {
    "sun": CelestialBodyData(
        name="Sun",
        mass_kg=1.989e30,
        radius_km=696340.0,
        semi_major_axis_au=0.0,
        orbital_period_days=0.0,
        eccentricity=0.0,
        inclination_deg=0.0,
        mean_anomaly_at_epoch_deg=0.0,
    ),
    "earth": CelestialBodyData(
        name="Earth",
        mass_kg=5.972e24,
        radius_km=6371.0,
        semi_major_axis_au=1.00000261,
        orbital_period_days=365.25,
        eccentricity=0.01671123,
        inclination_deg=0.00005,
        mean_anomaly_at_epoch_deg=100.46435,
    ),
    "mars": CelestialBodyData(
        name="Mars",
        mass_kg=6.417e23,
        radius_km=3389.5,
        semi_major_axis_au=1.52371034,
        orbital_period_days=686.98,
        eccentricity=0.09339410,
        inclination_deg=1.84969142,
        mean_anomaly_at_epoch_deg=355.45332,
    ),
    "moon": CelestialBodyData(
        name="Moon",
        mass_kg=7.342e22,
        radius_km=1737.4,
        semi_major_axis_au=0.00257,
        orbital_period_days=27.32,
        eccentricity=0.0549,
        inclination_deg=5.145,
        mean_anomaly_at_epoch_deg=0.0,
    ),
}


def get_body(name: str) -> CelestialBodyData:
    key = name.lower()
    if key not in BODIES:
        available = ", ".join(sorted(BODIES.keys()))
        raise KeyError(f"Unknown body '{name}'. Available bodies: {available}")
    return BODIES[key]


def get_orbital_velocity(body_name: str) -> float:
    body = get_body(body_name)
    if body.semi_major_axis_au == 0.0:
        return 0.0
    a_km = body.semi_major_axis_au * AU_KM.value
    return math.sqrt(GRAVITATIONAL_PARAMETER_SUN.value / a_km)
