"""
Tests for orbital celestial body database and Doppler calculations.
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbital.bodies import (
    AU_KM,
    BODIES,
    GRAVITATIONAL_PARAMETER_SUN,
    SPEED_OF_LIGHT,
    CelestialBodyData,
    get_body,
    get_orbital_velocity,
)
from orbital.doppler import (
    KA_BAND_FREQ_HZ,
    MAX_EARTH_MARS_RELATIVE_VELOCITY,
    OPTICAL_CARRIER_FREQ_HZ,
    UHF_FREQ_HZ,
    DopplerResult,
    calculate_classical_doppler,
    calculate_doppler_with_result,
    calculate_relativistic_doppler,
)


class TestCelestialBodies(unittest.TestCase):

    def test_bodies_dict_has_four_entries(self):
        self.assertEqual(len(BODIES), 4)

    def test_earth_data(self):
        earth = get_body("earth")
        self.assertAlmostEqual(earth.semi_major_axis_au, 1.0, places=2)
        self.assertAlmostEqual(earth.orbital_period_days, 365.25, places=0)
        self.assertAlmostEqual(earth.eccentricity, 0.0167, places=2)

    def test_mars_data(self):
        mars = get_body("mars")
        self.assertAlmostEqual(mars.semi_major_axis_au, 1.524, places=2)
        self.assertAlmostEqual(mars.orbital_period_days, 687, places=0)
        self.assertGreater(mars.eccentricity, 0.05)

    def test_sun_data(self):
        sun = get_body("sun")
        self.assertEqual(sun.mass_kg, 1.989e30)
        self.assertEqual(sun.radius_km, 696340.0)

    def test_moon_data(self):
        moon = get_body("moon")
        self.assertAlmostEqual(moon.orbital_period_days, 27.32, places=1)

    def test_get_body_case_insensitive(self):
        earth = get_body("Earth")
        self.assertEqual(earth.name, "Earth")
        earth2 = get_body("EARTH")
        self.assertEqual(earth2.name, "Earth")

    def test_get_body_unknown_raises(self):
        with self.assertRaises(KeyError):
            get_body("jupiter")

    def test_get_body_error_lists_available(self):
        try:
            get_body("jupiter")
        except KeyError as exc:
            self.assertIn("earth", str(exc))
            self.assertIn("mars", str(exc))

    def test_earth_orbital_velocity(self):
        v = get_orbital_velocity("earth")
        self.assertGreater(v, 0)
        self.assertAlmostEqual(v, 29.78, places=0)

    def test_mars_orbital_velocity(self):
        v = get_orbital_velocity("mars")
        self.assertGreater(v, 0)
        self.assertLess(v, get_orbital_velocity("earth"))

    def test_sun_orbital_velocity_zero(self):
        v = get_orbital_velocity("sun")
        self.assertEqual(v, 0.0)

    def test_physical_constants(self):
        self.assertAlmostEqual(SPEED_OF_LIGHT.value, 299792.458)
        self.assertAlmostEqual(AU_KM.value, 149597870.7)
        self.assertGreater(GRAVITATIONAL_PARAMETER_SUN.value, 1e10)


class TestDopplerClassical(unittest.TestCase):

    def test_zero_velocity_zero_shift(self):
        shift = calculate_classical_doppler(0.0, 26.5e9)
        self.assertEqual(shift, 0.0)

    def test_receding_redshift(self):
        shift = calculate_classical_doppler(10.0, 26.5e9)
        self.assertLess(shift, 0)

    def test_approaching_blueshift(self):
        shift = calculate_classical_doppler(-10.0, 26.5e9)
        self.assertGreater(shift, 0)

    def test_magnitude_proportional_to_velocity(self):
        s1 = calculate_classical_doppler(5.0, 26.5e9)
        s2 = calculate_classical_doppler(10.0, 26.5e9)
        self.assertAlmostEqual(s2, 2 * s1, places=2)

    def test_proportional_to_frequency(self):
        optical = calculate_classical_doppler(10.0, OPTICAL_CARRIER_FREQ_HZ)
        ka = calculate_classical_doppler(10.0, KA_BAND_FREQ_HZ)
        ratio = optical / ka
        self.assertAlmostEqual(ratio, OPTICAL_CARRIER_FREQ_HZ / KA_BAND_FREQ_HZ, places=2)


class TestDopplerRelativistic(unittest.TestCase):

    def test_zero_velocity_zero_shift(self):
        shift = calculate_relativistic_doppler(0.0, 26.5e9)
        self.assertEqual(shift, 0.0)

    def test_receding_redshift(self):
        shift = calculate_relativistic_doppler(10.0, 26.5e9)
        self.assertLess(shift, 0)

    def test_approaching_blueshift(self):
        shift = calculate_relativistic_doppler(-10.0, 26.5e9)
        self.assertGreater(shift, 0)

    def test_relativistic_correction_small_at_low_velocity(self):
        classical = calculate_classical_doppler(1.0, 26.5e9)
        relativistic = calculate_relativistic_doppler(1.0, 26.5e9)
        correction = abs(relativistic - classical)
        self.assertLess(correction, abs(classical) * 0.01)

    def test_relativistic_correction_grows_with_velocity(self):
        correction_low = abs(
            calculate_relativistic_doppler(5.0, 26.5e9)
            - calculate_classical_doppler(5.0, 26.5e9)
        )
        correction_high = abs(
            calculate_relativistic_doppler(20.0, 26.5e9)
            - calculate_classical_doppler(20.0, 26.5e9)
        )
        self.assertGreater(correction_high, correction_low)


class TestDopplerResult(unittest.TestCase):

    def test_result_has_all_fields(self):
        result = calculate_doppler_with_result(15.0, 26.5e9)
        self.assertIsInstance(result, DopplerResult)
        self.assertTrue(math.isfinite(result.frequency_shift_hz))
        self.assertTrue(math.isfinite(result.shifted_frequency_hz))
        self.assertEqual(result.velocity_km_s, 15.0)
        self.assertTrue(math.isfinite(result.relativistic_correction))

    def test_shifted_frequency(self):
        result = calculate_doppler_with_result(10.0, 26.5e9)
        expected = 26.5e9 + result.frequency_shift_hz
        self.assertAlmostEqual(result.shifted_frequency_hz, expected, places=0)

    def test_max_relative_velocity_is_reasonable(self):
        self.assertGreater(MAX_EARTH_MARS_RELATIVE_VELOCITY, 10.0)
        self.assertLess(MAX_EARTH_MARS_RELATIVE_VELOCITY, 50.0)

    def test_optical_doppler_larger_than_rf(self):
        v = 10.0
        optical_shift = abs(calculate_relativistic_doppler(v, OPTICAL_CARRIER_FREQ_HZ))
        ka_shift = abs(calculate_relativistic_doppler(v, KA_BAND_FREQ_HZ))
        uhf_shift = abs(calculate_relativistic_doppler(v, UHF_FREQ_HZ))
        self.assertGreater(optical_shift, ka_shift)
        self.assertGreater(ka_shift, uhf_shift)


if __name__ == "__main__":
    unittest.main()
