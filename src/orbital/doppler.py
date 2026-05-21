"""Doppler effect calculations for Earth-Mars DTN links."""

from dataclasses import dataclass

from orbital.contact_windows import SPEED_OF_LIGHT_KM_S

OPTICAL_CARRIER_FREQ_HZ = 193.4e12
KA_BAND_FREQ_HZ = 26.5e9
UHF_FREQ_HZ = 401.0e6
MAX_EARTH_MARS_RELATIVE_VELOCITY = 24.0


@dataclass(frozen=True)
class DopplerResult:
    frequency_shift_hz: float
    shifted_frequency_hz: float
    velocity_km_s: float
    relativistic_correction: float


def calculate_classical_doppler(velocity_km_s: float, frequency_hz: float) -> float:
    """Return classical Doppler frequency shift in Hz.

    Positive velocity = receding (redshift / negative shift).
    """
    return -frequency_hz * (velocity_km_s / SPEED_OF_LIGHT_KM_S)


def calculate_relativistic_doppler(velocity_km_s: float, frequency_hz: float) -> float:
    """Return relativistic Doppler frequency shift in Hz.

    Uses f_obs = f * sqrt((1 - beta) / (1 + beta)) where beta = v/c.
    Positive velocity = receding (redshift / negative shift).
    """
    beta = velocity_km_s / SPEED_OF_LIGHT_KM_S
    shifted = frequency_hz * ((1.0 - beta) / (1.0 + beta)) ** 0.5
    return shifted - frequency_hz


def calculate_doppler_with_result(
    velocity_km_s: float, frequency_hz: float
) -> DopplerResult:
    """Return full DopplerResult for the given velocity and carrier frequency."""
    classical_shift = calculate_classical_doppler(velocity_km_s, frequency_hz)
    relativistic_shift = calculate_relativistic_doppler(velocity_km_s, frequency_hz)
    return DopplerResult(
        frequency_shift_hz=relativistic_shift,
        shifted_frequency_hz=frequency_hz + relativistic_shift,
        velocity_km_s=velocity_km_s,
        relativistic_correction=relativistic_shift - classical_shift,
    )
