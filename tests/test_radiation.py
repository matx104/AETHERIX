"""
Tests for AETHERIX Radiation-Hardened Computing Module
Validates SEU rate model, TMR voting, SECDED ECC, scrubbing, FDIR, and the
Earth-Mars transit simulation.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from computing.radiation import (
    ECCMemory,
    ENVIRONMENTS,
    FDIRController,
    FDIRState,
    MemoryScrubber,
    RadiationEffect,
    RadiationEnvironment,
    TMRVoter,
    seu_rate_per_bit_day,
    simulate_transit,
)


class TestRadiationEffect(unittest.TestCase):

    def test_seu_is_recoverable(self):
        self.assertTrue(RadiationEffect.SEU.is_recoverable)
        self.assertFalse(RadiationEffect.SEU.is_destructive)

    def test_latchup_is_destructive(self):
        self.assertTrue(RadiationEffect.SEL.is_destructive)
        self.assertFalse(RadiationEffect.SEL.is_recoverable)


class TestEnvironment(unittest.TestCase):

    def test_solar_event_is_most_intense(self):
        spe = ENVIRONMENTS["solar_particle_event"]
        interp = ENVIRONMENTS["interplanetary"]
        self.assertGreater(spe.particle_flux, interp.particle_flux)

    def test_tid_accumulates_with_time(self):
        env = ENVIRONMENTS["interplanetary"]
        self.assertAlmostEqual(env.tid_after(365.25), env.tid_rate_krad_yr, places=6)
        self.assertGreater(env.tid_after(730), env.tid_after(365))

    def test_rad750_has_margin_on_mars_surface(self):
        mars = ENVIRONMENTS["mars_surface"]
        # RAD750 tolerates ~200 krad; Mars surface dose over 687 d is tiny.
        self.assertGreater(mars.margin_against(200.0, 687), 1.0)


class TestSEURate(unittest.TestCase):

    def test_rate_scales_with_flux(self):
        low = seu_rate_per_bit_day(1.0)
        high = seu_rate_per_bit_day(10.0)
        self.assertAlmostEqual(high, 10.0 * low, places=12)

    def test_hardened_part_has_lower_rate(self):
        commercial = seu_rate_per_bit_day(4.0, 1e-12)
        hardened = seu_rate_per_bit_day(4.0, 1e-14)
        self.assertLess(hardened, commercial)
        self.assertAlmostEqual(commercial / hardened, 100.0, places=4)


class TestTMRVoter(unittest.TestCase):

    def test_unanimous_no_fault(self):
        v = TMRVoter()
        result, masked = v.vote(1, 1, 1)
        self.assertEqual(result, 1)
        self.assertFalse(masked)
        self.assertEqual(v.corrected, 0)

    def test_single_fault_masked(self):
        v = TMRVoter()
        result, masked = v.vote(1, 1, 0)
        self.assertEqual(result, 1)
        self.assertTrue(masked)
        self.assertEqual(v.corrected, 1)

    def test_all_differ_uncorrectable(self):
        v = TMRVoter()
        result, masked = v.vote(1, 2, 3)
        self.assertFalse(masked)
        self.assertEqual(v.uncorrectable, 1)

    def test_system_error_probability_small_p(self):
        # ~3 p^2 for small p
        p = 1e-4
        self.assertAlmostEqual(TMRVoter.system_error_probability(p), 3 * p * p, places=10)

    def test_reliability_gain_positive(self):
        self.assertGreater(TMRVoter.reliability_gain(1e-4), 1.0)


class TestECCMemory(unittest.TestCase):

    def test_secded_overhead_32bit(self):
        # (39,32) SECDED: 7 check bits over 32 data bits.
        ecc = ECCMemory(data_bits=32)
        self.assertEqual(ecc.parity_bits, 7)
        self.assertAlmostEqual(ecc.overhead_percent, 100.0 * 7 / 32, places=4)

    def test_single_error_corrected(self):
        ecc = ECCMemory()
        status, valid = ecc.read_word(1)
        self.assertEqual(status, "CORRECTED")
        self.assertTrue(valid)
        self.assertEqual(ecc.corrected, 1)

    def test_double_error_detected_not_corrected(self):
        ecc = ECCMemory()
        status, valid = ecc.read_word(2)
        self.assertEqual(status, "DETECTED_UNCORRECTABLE")
        self.assertFalse(valid)

    def test_no_error_ok(self):
        ecc = ECCMemory()
        status, valid = ecc.read_word(0)
        self.assertEqual(status, "OK")
        self.assertTrue(valid)


class TestMemoryScrubber(unittest.TestCase):

    def test_faster_scrub_lowers_uncorrectable_prob(self):
        rate = seu_rate_per_bit_day(50.0, 1e-12)  # harsh environment
        slow = MemoryScrubber(scrub_interval_s=3600)
        fast = MemoryScrubber(scrub_interval_s=10)
        self.assertGreater(slow.uncorrectable_probability(rate),
                           fast.uncorrectable_probability(rate))

    def test_uncorrectable_probability_bounded(self):
        rate = seu_rate_per_bit_day(4.0)
        p = MemoryScrubber().uncorrectable_probability(rate)
        self.assertGreaterEqual(p, 0.0)
        self.assertLessEqual(p, 1.0)


class TestFDIR(unittest.TestCase):

    def test_nominal_when_healthy_and_kicked(self):
        fdir = FDIRController()
        fdir.kick_watchdog(1.0)
        self.assertEqual(fdir.detect(1.0, healthy=True), FDIRState.NOMINAL)

    def test_unhealthy_triggers_recovery(self):
        fdir = FDIRController(max_recovery_attempts=3)
        fdir.kick_watchdog(0.0)
        state = fdir.detect(1.0, healthy=False)
        self.assertIn(state, (FDIRState.RECOVERING, FDIRState.ISOLATED))

    def test_watchdog_timeout_triggers_recovery(self):
        fdir = FDIRController(watchdog_timeout_s=5.0)
        fdir.kick_watchdog(0.0)
        # 10s with no kick -> watchdog expired even though 'healthy'
        state = fdir.detect(10.0, healthy=True)
        self.assertNotEqual(state, FDIRState.NOMINAL)

    def test_exhausted_budget_goes_safe_mode(self):
        fdir = FDIRController(watchdog_timeout_s=5.0, max_recovery_attempts=2)
        fdir.kick_watchdog(0.0)
        for t in (6, 12, 18, 24):
            fdir.detect(t, healthy=False)
        self.assertEqual(fdir.state, FDIRState.SAFE_MODE)


class TestTransitSimulation(unittest.TestCase):

    def test_protection_reduces_errors(self):
        r = simulate_transit()
        self.assertGreater(r.raw_upsets_unprotected, r.residual_errors_protected)
        self.assertGreater(r.protection_factor, 1.0)

    def test_deterministic_with_seed(self):
        a = simulate_transit(seed=7)
        b = simulate_transit(seed=7)
        self.assertEqual(a.raw_upsets_unprotected, b.raw_upsets_unprotected)
        self.assertEqual(a.residual_errors_protected, b.residual_errors_protected)

    def test_harsher_environment_more_upsets(self):
        calm = simulate_transit(environment="mars_surface")
        harsh = simulate_transit(environment="van_allen")
        self.assertGreater(harsh.raw_upsets_unprotected, calm.raw_upsets_unprotected)


if __name__ == "__main__":
    unittest.main()
