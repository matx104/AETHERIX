"""
Tests for the AETHERIX end-to-end simulation driver (run_simulation.py).

Validates that every module runs without error, returns well-formed
result dicts, and that the failure-and-recovery scenario makes the
expected routing decision (Ka-band RF fallback during solar conjunction).
"""

import os
import sys
import unittest

# Make the repo root importable so `import run_simulation` works, and
# src/ importable for the module's internal sys.path manipulation.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "src"))

import run_simulation  # noqa: E402


class TestBaselineSimulation(unittest.TestCase):
    def test_returns_expected_keys(self):
        result = run_simulation.run_baseline_simulation(seed=7, quiet=True)
        for key in ("total_bundles", "delivered_bundles", "stored_bundles",
                    "delivery_ratio", "average_hops"):
            self.assertIn(key, result)
        self.assertGreater(result["total_bundles"], 0)

    def test_deterministic_with_seed(self):
        a = run_simulation.run_baseline_simulation(seed=42, quiet=True)
        b = run_simulation.run_baseline_simulation(seed=42, quiet=True)
        self.assertEqual(a["total_bundles"], b["total_bundles"])


class TestLinkBudgetComparison(unittest.TestCase):
    def test_three_scenarios(self):
        result = run_simulation.run_link_budget_comparison(quiet=True)
        rows = result["rows"]
        self.assertEqual(len(rows), 3)
        scenarios = {r["scenario"] for r in rows}
        self.assertEqual(scenarios, {"minimum", "average", "maximum"})


class TestRLTrainingDemo(unittest.TestCase):
    def test_epsilon_decay(self):
        result = run_simulation.run_rl_training_demo(seed=42, quiet=True)
        self.assertAlmostEqual(result["epsilon_decay"], 0.995)
        self.assertLess(result["epsilon_end"], result["epsilon_start"])
        self.assertGreaterEqual(result["epsilon_end"], 0.01)
        self.assertGreater(result["episodes"], 0)


class TestFailureRecovery(unittest.TestCase):
    """The centerpiece: solar conjunction -> optical fails -> Ka-band RF."""

    def test_p0_routed_via_ka_band_relay(self):
        result = run_simulation.run_failure_recovery(quiet=True)
        # The RL agent must FORWARD (not store) the P0 bundle.
        self.assertEqual(result["agent_action"], "forward")
        # The chosen next hop must be a Lagrange relay (Ka-band path).
        self.assertIn("esl4", result["agent_next_hop"])
        # The direct optical path must be flagged CLOSED during conjunction.
        eval_rows = {r["path"]: r for r in result["eval_rows"]}
        self.assertEqual(eval_rows["direct_optical"]["status"], "CLOSED")
        # The Ka-band relay paths must be OPEN.
        self.assertEqual(eval_rows["via_es_l4"]["status"], "OPEN")
        self.assertEqual(eval_rows["via_es_l5"]["status"], "OPEN")
        # Policy engine: P0 forwarded, bulk deferred (stored).
        self.assertEqual(result["p0_policy"], "forward")
        self.assertEqual(result["bulk_policy"], "store")

    def test_optical_reward_drops_below_relay(self):
        result = run_simulation.run_failure_recovery(quiet=True)
        rows = {r["path"]: r for r in result["eval_rows"]}
        optical_conj = rows["direct_optical"]["conjunction_reward"]
        relay_conj = rows["via_es_l4"]["conjunction_reward"]
        self.assertLess(optical_conj, relay_conj)


class TestQKDSecurity(unittest.TestCase):
    def test_clean_channel_secure(self):
        result = run_simulation.run_qkd_security(seed=42, quiet=True)
        self.assertAlmostEqual(result["threshold"], 0.11)
        self.assertTrue(result["clean_secure"])
        self.assertLess(result["clean_qber"], result["threshold"])

    def test_eavesdropper_detected(self):
        result = run_simulation.run_qkd_security(seed=42, quiet=True)
        self.assertFalse(result["tapped_secure"])
        self.assertGreater(result["tapped_qber"], result["threshold"])


class TestRadiationDemo(unittest.TestCase):
    def test_protection_factor(self):
        result = run_simulation.run_radiation_demo(quiet=True)
        self.assertGreater(result["raw_upsets"], result["residual_errors"])
        self.assertGreater(result["protection_factor"], 1.0)
        self.assertGreater(result["tmr_gain"], 1.0)


class TestDriverCLI(unittest.TestCase):
    def test_run_all_returns_combined_results(self):
        combined = run_simulation.run_all(seed=42, quiet=True)
        self.assertEqual(len(combined), 6)
        for name, res in combined.items():
            self.assertIsInstance(res, dict, f"{name} did not return a dict")
            self.assertNotIn("error", res, f"{name} errored: {res.get('error')}")

    def test_main_returns_zero(self):
        self.assertEqual(run_simulation.main(["--quiet", "--seed", "1"]), 0)

    def test_main_single_module(self):
        self.assertEqual(run_simulation.main(["-m", "4", "--quiet"]), 0)

    def test_invalid_module_rejected(self):
        with self.assertRaises(SystemExit):
            run_simulation.main(["-m", "99"])


if __name__ == "__main__":
    unittest.main()
