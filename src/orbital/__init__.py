"""
AETHERIX Orbital Mechanics Module

Provides orbital mechanics calculations including:
- Earth-Mars distance calculations
- Contact window prediction
- Light time and Doppler calculations
"""

from .contact_windows import (
    calculate_earth_mars_distance,
    calculate_light_time,
    calculate_doppler_shift,
    estimate_data_rate,
    predict_contact_windows,
    get_distance_timeline,
    CelestialBody,
    ContactWindow,
    LinkGeometry,
)

__all__ = [
    'calculate_earth_mars_distance',
    'calculate_light_time',
    'calculate_doppler_shift',
    'estimate_data_rate',
    'predict_contact_windows',
    'get_distance_timeline',
    'CelestialBody',
    'ContactWindow',
    'LinkGeometry',
]
