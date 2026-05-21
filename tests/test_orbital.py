"""
Tests for AETHERIX Orbital Mechanics Module
Validates distance calculations, light time, contact windows, Doppler shift, and data rate estimation.
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbital.contact_windows import (AU_KM, ORBITAL_ELEMENTS,
                                     SPEED_OF_LIGHT_KM_S, SYNODIC_PERIOD_DAYS,
                                     CelestialBody, calculate_doppler_shift,
                                     calculate_earth_mars_distance,
                                     calculate_light_time,
                                     calculate_orbital_radius,
                                     estimate_data_rate, get_distance_timeline,
                                     predict_contact_windows)


class TestOrbitalRadius(unittest.TestCase):

    def test_earth_at_perihelion(self):
        earth = ORBITAL_ELEMENTS[CelestialBody.EARTH]
        r = calculate_orbital_radius(earth, 0)
        expected = earth.semi_major_axis_au * (1 - earth.eccentricity)
        self.assertAlmostEqual(r, expected, places=5)

    def test_earth_at_aphelion(self):
        earth = ORBITAL_ELEMENTS[CelestialBody.EARTH]
        r = calculate_orbital_radius(earth, 180)
        expected = earth.semi_major_axis_au * (1 + earth.eccentricity)
        self.assertAlmostEqual(r, expected, places=5)

    def test_mars_semi_major_axis(self):
        mars = ORBITAL_ELEMENTS[CelestialBody.MARS]
        r = calculate_orbital_radius(mars, 90)
        a = mars.semi_major_axis_au
        e = mars.eccentricity
        expected = a * (1 - e ** 2) / (1 + e * math.cos(math.radians(90)))
        self.assertAlmostEqual(r, expected, places=5)


class TestEarthMarsDistance(unittest.TestCase):

    def test_opposition_minimum(self):
        dist = calculate_earth_mars_distance(0, 180)
        dist_mkm = dist / 1e6
        self.assertLess(dist_mkm, 400)
        self.assertGreater(dist_mkm, 30)

    def test_conjunction_maximum(self):
        dist = calculate_earth_mars_distance(0, 0)
        dist_mkm = dist / 1e6
        self.assertGreater(dist_mkm, 300)

    def test_distance_in_km(self):
        dist = calculate_earth_mars_distance(0, 180)
        self.assertGreater(dist, 1e6)

    def test_distance_positive(self):
        for e_deg in range(0, 360, 45):
            for m_deg in range(0, 360, 45):
                dist = calculate_earth_mars_distance(e_deg, m_deg)
                self.assertGreater(dist, 0)


class TestLightTime(unittest.TestCase):

    def test_minimum_light_time(self):
        dist = 54.6e6
        lt = calculate_light_time(dist)
        self.assertAlmostEqual(lt, dist / SPEED_OF_LIGHT_KM_S, places=1)
        self.assertGreater(lt, 170)
        self.assertLess(lt, 200)

    def test_average_light_time(self):
        dist = 225e6
        lt = calculate_light_time(dist)
        lt_min = lt / 60
        self.assertGreater(lt_min, 10)
        self.assertLess(lt_min, 15)

    def test_maximum_light_time(self):
        dist = 401e6
        lt = calculate_light_time(dist)
        lt_min = lt / 60
        self.assertGreater(lt_min, 20)
        self.assertLess(lt_min, 25)

    def test_zero_distance(self):
        self.assertEqual(calculate_light_time(0), 0)


class TestDopplerShift(unittest.TestCase):

    def test_optical_doppler(self):
        optical_freq = 193.4e12
        velocity = 24.0
        shift = calculate_doppler_shift(velocity, optical_freq)
        expected = optical_freq * (velocity / SPEED_OF_LIGHT_KM_S)
        self.assertAlmostEqual(shift, expected, places=0)
        self.assertGreater(shift, 10e9)

    def test_zero_velocity(self):
        self.assertEqual(calculate_doppler_shift(0, 193.4e12), 0)

    def test_approaching_vs_receding(self):
        freq = 193.4e12
        v = 10.0
        shift_recede = calculate_doppler_shift(v, freq)
        shift_approach = calculate_doppler_shift(-v, freq)
        self.assertGreater(shift_recede, 0)
        self.assertLess(shift_approach, 0)


class TestDataRate(unittest.TestCase):

    def test_minimum_distance_max_rate(self):
        rate = estimate_data_rate(54.6e6)
        self.assertGreater(rate, 100)

    def test_maximum_distance_min_rate(self):
        rate = estimate_data_rate(401e6)
        self.assertGreaterEqual(rate, 2.0)

    def test_rate_clamped_at_200(self):
        rate = estimate_data_rate(10e6)
        self.assertLessEqual(rate, 200.0)

    def test_rate_clamped_at_2_minimum(self):
        rate = estimate_data_rate(1e9)
        self.assertGreaterEqual(rate, 2.0)

    def test_rate_decreases_with_distance(self):
        rate_near = estimate_data_rate(100e6)
        rate_far = estimate_data_rate(300e6)
        self.assertGreater(rate_near, rate_far)


class TestContactWindows(unittest.TestCase):

    def test_windows_at_opposition(self):
        windows = predict_contact_windows(100, 30)
        self.assertGreater(len(windows), 0)
        for w in windows:
            self.assertGreater(w.duration_hours, 0)
            self.assertGreater(w.max_data_rate_mbps, 0)

    def test_window_has_valid_fields(self):
        windows = predict_contact_windows(0, 5)
        if windows:
            w = windows[0]
            self.assertGreater(w.duration_hours, 0)
            self.assertGreater(w.max_elevation_deg, 0)
            self.assertGreater(w.average_distance_km, 0)

    def test_conjunction_blackout(self):
        windows = predict_contact_windows(389, 5)
        self.assertEqual(len(windows), 0)

    def test_zero_duration(self):
        windows = predict_contact_windows(0, 0)
        self.assertEqual(len(windows), 0)


class TestDistanceTimeline(unittest.TestCase):

    def test_timeline_length(self):
        timeline = get_distance_timeline(100)
        self.assertEqual(len(timeline), 100)

    def test_timeline_full_synodic(self):
        timeline = get_distance_timeline(780)
        self.assertEqual(len(timeline), 780)

    def test_timeline_values_valid(self):
        timeline = get_distance_timeline(50)
        for day, dist, lt_min in timeline:
            self.assertGreater(dist, 0)
            self.assertGreater(lt_min, 0)


class TestConstants(unittest.TestCase):

    def test_speed_of_light(self):
        self.assertAlmostEqual(SPEED_OF_LIGHT_KM_S, 299792.458, places=1)

    def test_au_in_km(self):
        self.assertAlmostEqual(AU_KM / 1e6, 149.598, places=1)

    def test_synodic_period(self):
        self.assertAlmostEqual(SYNODIC_PERIOD_DAYS, 779.94, places=1)

    def test_mars_orbital_period(self):
        from orbital.contact_windows import MARS_ORBITAL_PERIOD_DAYS
        self.assertAlmostEqual(MARS_ORBITAL_PERIOD_DAYS, 686.98, places=1)


if __name__ == "__main__":
    unittest.main()
