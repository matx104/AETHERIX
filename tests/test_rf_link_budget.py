"""
Tests for AETHERIX RF Link Budget Calculator

Validates RF link budget calculations for Ka-band, X-band, S-band,
and UHF links in deep-space and planetary-surface communications.
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infrastructure.rf_link_budget import (
    BOLTZMANN_CONSTANT_W_HZ_K,
    KA_BAND_FREQ_HZ,
    MARS_EARTH_DISTANCES_KM,
    REFERENCE_TEMPERATURE_K,
    RFLinkBudget,
    RFLinkBudgetCalculator,
    S_BAND_FREQ_HZ,
    SPEED_OF_LIGHT_M_S,
    UHF_FREQ_HZ,
    X_BAND_FREQ_HZ,
    create_ka_band_calculator,
    create_uhf_calculator,
)


class TestRFLinkBudgetCalculator(unittest.TestCase):

    def setUp(self):
        self.ka_calc = RFLinkBudgetCalculator(KA_BAND_FREQ_HZ)
        self.uhf_calc = RFLinkBudgetCalculator(UHF_FREQ_HZ)

    # ---- constructor ----

    def test_constructor_stores_frequency(self):
        self.assertEqual(self.ka_calc.frequency_hz, KA_BAND_FREQ_HZ)

    def test_constructor_stores_wavelength(self):
        expected_wl = SPEED_OF_LIGHT_M_S / KA_BAND_FREQ_HZ
        self.assertAlmostEqual(self.ka_calc.wavelength_m, expected_wl, places=6)

    def test_constructor_rejects_zero_frequency(self):
        with self.assertRaises(ValueError):
            RFLinkBudgetCalculator(0)

    def test_constructor_rejects_negative_frequency(self):
        with self.assertRaises(ValueError):
            RFLinkBudgetCalculator(-1.0)

    # ---- free space loss ----

    def test_free_space_loss_is_negative(self):
        fspl = self.ka_calc.calculate_free_space_loss_db(225_000_000)
        self.assertLess(fspl, 0)

    def test_free_space_loss_increases_with_distance(self):
        near = self.ka_calc.calculate_free_space_loss_db(55_000_000)
        far = self.ka_calc.calculate_free_space_loss_db(401_000_000)
        self.assertLess(far, near)

    def test_free_space_loss_6_db_per_octave(self):
        d1 = 100_000_000
        d2 = 200_000_000
        loss1 = self.ka_calc.calculate_free_space_loss_db(d1)
        loss2 = self.ka_calc.calculate_free_space_loss_db(d2)
        self.assertAlmostEqual(loss2 - loss1, -6.0206, places=3)

    def test_free_space_loss_rejects_zero_distance(self):
        with self.assertRaises(ValueError):
            self.ka_calc.calculate_free_space_loss_db(0)

    def test_free_space_loss_rejects_negative_distance(self):
        with self.assertRaises(ValueError):
            self.ka_calc.calculate_free_space_loss_db(-1)

    # ---- antenna gain ----

    def test_antenna_gain_positive(self):
        gain = self.ka_calc.calculate_antenna_gain_dbi(3.0)
        self.assertGreater(gain, 0)

    def test_larger_dish_higher_gain(self):
        small = self.ka_calc.calculate_antenna_gain_dbi(1.0)
        large = self.ka_calc.calculate_antenna_gain_dbi(34.0)
        self.assertGreater(large, small)

    def test_higher_frequency_higher_gain(self):
        ka = self.ka_calc.calculate_antenna_gain_dbi(3.0)
        uhf = self.uhf_calc.calculate_antenna_gain_dbi(3.0)
        self.assertGreater(ka, uhf)

    def test_efficiency_affects_gain(self):
        low_eff = self.ka_calc.calculate_antenna_gain_dbi(3.0, efficiency=0.3)
        high_eff = self.ka_calc.calculate_antenna_gain_dbi(3.0, efficiency=0.7)
        self.assertGreater(high_eff, low_eff)

    def test_antenna_gain_rejects_zero_diameter(self):
        with self.assertRaises(ValueError):
            self.ka_calc.calculate_antenna_gain_dbi(0)

    def test_antenna_gain_rejects_zero_efficiency(self):
        with self.assertRaises(ValueError):
            self.ka_calc.calculate_antenna_gain_dbi(3.0, efficiency=0)

    # ---- power conversions ----

    def test_watts_to_dbm_round_trip(self):
        for watts in [0.001, 0.1, 1.0, 10.0, 100.0]:
            dbm = self.ka_calc.watts_to_dbm(watts)
            back = self.ka_calc.dbm_to_watts(dbm)
            self.assertAlmostEqual(back, watts, places=6)

    def test_watts_to_dbm_known_values(self):
        self.assertAlmostEqual(self.ka_calc.watts_to_dbm(1.0), 30.0, places=1)
        self.assertAlmostEqual(self.ka_calc.watts_to_dbm(0.001), 0.0, places=1)
        self.assertAlmostEqual(self.ka_calc.watts_to_dbm(100.0), 50.0, places=1)

    def test_watts_to_dbm_zero_returns_neg_inf(self):
        self.assertEqual(self.ka_calc.watts_to_dbm(0.0), float('-inf'))

    def test_watts_to_dbm_negative_returns_neg_inf(self):
        self.assertEqual(self.ka_calc.watts_to_dbm(-1.0), float('-inf'))

    # ---- system temperature ----

    def test_system_temperature_default(self):
        ts = self.ka_calc.calculate_system_temperature()
        # Tant=50K + T0*(10^(2/10)-1) = 50 + 290*0.5849 = 50 + 169.6 = 219.6
        self.assertAlmostEqual(ts, 219.6, places=1)

    def test_system_temperature_increases_with_noise_figure(self):
        low_nf = self.ka_calc.calculate_system_temperature(receiver_noise_figure_db=1.0)
        high_nf = self.ka_calc.calculate_system_temperature(receiver_noise_figure_db=5.0)
        self.assertGreater(high_nf, low_nf)

    def test_system_temperature_increases_with_antenna_temp(self):
        low_t = self.ka_calc.calculate_system_temperature(antenna_temp_k=20.0)
        high_t = self.ka_calc.calculate_system_temperature(antenna_temp_k=100.0)
        self.assertGreater(high_t, low_t)

    # ---- noise power ----

    def test_noise_power_is_negative_dbm(self):
        noise = self.ka_calc.calculate_noise_power_dbm(
            system_temp_k=200.0, bandwidth_hz=10e6
        )
        self.assertLess(noise, 0)

    def test_noise_power_increases_with_bandwidth(self):
        n1 = self.ka_calc.calculate_noise_power_dbm(200.0, 1e6)
        n2 = self.ka_calc.calculate_noise_power_dbm(200.0, 100e6)
        self.assertGreater(n2, n1)

    def test_noise_power_increases_with_temperature(self):
        n1 = self.ka_calc.calculate_noise_power_dbm(100.0, 10e6)
        n2 = self.ka_calc.calculate_noise_power_dbm(500.0, 10e6)
        self.assertGreater(n2, n1)

    # ---- full link budget ----

    def test_calculate_rf_link_budget_returns_dataclass(self):
        budget = self.ka_calc.calculate_rf_link_budget(
            distance_km=225_000_000,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
        )
        self.assertIsInstance(budget, RFLinkBudget)

    def test_link_budget_fields_populated(self):
        budget = self.ka_calc.calculate_rf_link_budget(
            distance_km=225_000_000,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
        )
        self.assertLess(budget.free_space_loss_db, 0)
        self.assertGreater(budget.transmitter_gain_dbi, 0)
        self.assertGreater(budget.receiver_gain_dbi, 0)
        self.assertGreater(budget.eirp_dbm, 0)
        self.assertTrue(math.isfinite(budget.received_power_dbm))
        self.assertTrue(math.isfinite(budget.noise_power_dbm))
        self.assertTrue(math.isfinite(budget.cnr_db))
        self.assertTrue(math.isfinite(budget.eb_n0_db))
        self.assertTrue(math.isfinite(budget.link_margin_db))

    def test_eirp_calculation(self):
        budget = self.ka_calc.calculate_rf_link_budget(
            distance_km=225_000_000,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
            tx_line_loss_db=-1.0,
        )
        expected_eirp = (
            self.ka_calc.watts_to_dbm(20.0)
            + self.ka_calc.calculate_antenna_gain_dbi(3.0)
            + (-1.0)
        )
        self.assertAlmostEqual(budget.eirp_dbm, expected_eirp, places=4)

    def test_link_margin_degrades_with_distance(self):
        near = self.ka_calc.calculate_rf_link_budget(
            distance_km=55_000_000,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
        )
        far = self.ka_calc.calculate_rf_link_budget(
            distance_km=401_000_000,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
        )
        self.assertGreater(near.link_margin_db, far.link_margin_db)

    def test_bandwidth_is_1_2x_data_rate(self):
        budget = self.ka_calc.calculate_rf_link_budget(
            distance_km=225_000_000,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
        )
        self.assertAlmostEqual(budget.bandwidth_hz, 12e6, places=1)

    def test_str_representation(self):
        budget = self.ka_calc.calculate_rf_link_budget(
            distance_km=225_000_000,
            tx_power_watts=20.0,
            tx_antenna_diameter_m=3.0,
            rx_antenna_diameter_m=34.0,
            data_rate_bps=10e6,
        )
        s = str(budget)
        self.assertIn("LINK BUDGET", s)
        self.assertIn("LINK MARGIN", s)


class TestMarsEarthScenarios(unittest.TestCase):

    def setUp(self):
        self.ka_calc = create_ka_band_calculator()
        self.uhf_calc = create_uhf_calculator()

    def test_minimum_distance_matches_constant(self):
        self.assertEqual(MARS_EARTH_DISTANCES_KM["minimum"], 55_000_000)

    def test_average_distance_matches_constant(self):
        self.assertEqual(MARS_EARTH_DISTANCES_KM["average"], 225_000_000)

    def test_maximum_distance_matches_constant(self):
        self.assertEqual(MARS_EARTH_DISTANCES_KM["maximum"], 401_000_000)

    def test_ka_minimum_margin_better_than_maximum(self):
        near = self.ka_calc.calculate_mars_earth_link("minimum")
        far = self.ka_calc.calculate_mars_earth_link("maximum")
        self.assertGreater(near.link_margin_db, far.link_margin_db)

    def test_ka_all_three_scenarios_produce_results(self):
        for scenario in ("minimum", "average", "maximum"):
            budget = self.ka_calc.calculate_mars_earth_link(scenario)
            self.assertIsInstance(budget, RFLinkBudget)
            self.assertEqual(budget.distance_km, MARS_EARTH_DISTANCES_KM[scenario])

    def test_uhf_all_three_scenarios_produce_results(self):
        for scenario in ("minimum", "average", "maximum"):
            budget = self.uhf_calc.calculate_mars_earth_link(scenario)
            self.assertIsInstance(budget, RFLinkBudget)
            self.assertEqual(budget.distance_km, MARS_EARTH_DISTANCES_KM[scenario])

    def test_uhf_uses_different_params_than_ka(self):
        ka = self.ka_calc.calculate_mars_earth_link("average")
        uhf = self.uhf_calc.calculate_mars_earth_link("average")
        # UHF has lower data rate
        self.assertLess(uhf.data_rate_bps, ka.data_rate_bps)
        # UHF has smaller antennas
        self.assertLess(uhf.transmitter_gain_dbi, ka.transmitter_gain_dbi)
        self.assertLess(uhf.receiver_gain_dbi, ka.receiver_gain_dbi)

    def test_invalid_scenario_raises(self):
        with self.assertRaises(ValueError):
            self.ka_calc.calculate_mars_earth_link("typical")

    def test_invalid_scenario_error_message_lists_valid_options(self):
        try:
            self.ka_calc.calculate_mars_earth_link("bogus")
        except ValueError as exc:
            self.assertIn("minimum", str(exc))
            self.assertIn("average", str(exc))
            self.assertIn("maximum", str(exc))


class TestFactoryFunctions(unittest.TestCase):

    def test_create_ka_band_calculator_frequency(self):
        calc = create_ka_band_calculator()
        self.assertEqual(calc.frequency_hz, KA_BAND_FREQ_HZ)

    def test_create_uhf_calculator_frequency(self):
        calc = create_uhf_calculator()
        self.assertEqual(calc.frequency_hz, UHF_FREQ_HZ)

    def test_ka_band_freq_value(self):
        self.assertAlmostEqual(KA_BAND_FREQ_HZ, 26.5e9)

    def test_x_band_freq_value(self):
        self.assertAlmostEqual(X_BAND_FREQ_HZ, 8.4e9)

    def test_s_band_freq_value(self):
        self.assertAlmostEqual(S_BAND_FREQ_HZ, 2.3e9)

    def test_uhf_freq_value(self):
        self.assertAlmostEqual(UHF_FREQ_HZ, 401e6)


class TestPhysicalConstants(unittest.TestCase):

    def test_speed_of_light(self):
        self.assertAlmostEqual(SPEED_OF_LIGHT_M_S, 299_792_458)

    def test_boltzmann_constant(self):
        self.assertAlmostEqual(BOLTZMANN_CONSTANT_W_HZ_K, 1.380649e-23)

    def test_reference_temperature(self):
        self.assertAlmostEqual(REFERENCE_TEMPERATURE_K, 290.0)


class TestMultiBandComparison(unittest.TestCase):

    def test_higher_frequency_more_fspl(self):
        ka = RFLinkBudgetCalculator(KA_BAND_FREQ_HZ)
        uhf = RFLinkBudgetCalculator(UHF_FREQ_HZ)
        d = 225_000_000
        ka_loss = ka.calculate_free_space_loss_db(d)
        uhf_loss = uhf.calculate_free_space_loss_db(d)
        self.assertLess(ka_loss, uhf_loss)

    def test_four_bands_all_produce_valid_budgets(self):
        for freq in [KA_BAND_FREQ_HZ, X_BAND_FREQ_HZ, S_BAND_FREQ_HZ, UHF_FREQ_HZ]:
            calc = RFLinkBudgetCalculator(freq)
            budget = calc.calculate_mars_earth_link("average")
            self.assertIsInstance(budget, RFLinkBudget)
            self.assertTrue(math.isfinite(budget.link_margin_db))


if __name__ == "__main__":
    unittest.main()
