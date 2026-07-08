"""
Tests for AETHERIX Simulation Engine

Validates the DTN simulation engine: topology setup, bundle generation,
forwarding propagation, delivery metrics, and state transitions.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.bundle import Bundle, BundlePriority, create_science_bundle
from simulation.simulator import (
    SimulationConfig,
    SimulationResult,
    SimulationState,
    Simulator,
)


class TestSimulationConfig(unittest.TestCase):

    def test_default_config(self):
        cfg = SimulationConfig()
        self.assertEqual(cfg.name, "earth-mars-baseline")
        self.assertEqual(cfg.duration_hours, 720.0)
        self.assertEqual(cfg.time_step_seconds, 60.0)
        self.assertEqual(cfg.seed, 42)
        self.assertEqual(cfg.bundle_generation_rate_per_hour, 10.0)

    def test_custom_config(self):
        cfg = SimulationConfig(
            name="test-scenario",
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=99,
            bundle_generation_rate_per_hour=100.0,
        )
        self.assertEqual(cfg.name, "test-scenario")
        self.assertEqual(cfg.duration_hours, 1.0)
        self.assertEqual(cfg.seed, 99)


class TestSimulatorSetup(unittest.TestCase):

    def setUp(self):
        self.config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
        )
        self.sim = Simulator(self.config)

    def test_initial_state_is_initialized(self):
        self.assertEqual(self.sim.get_state(), SimulationState.INITIALIZED)

    def test_setup_creates_topology(self):
        self.sim.setup()
        self.assertIsNotNone(self.sim._topology)

    def test_setup_creates_engines_for_all_nodes(self):
        self.sim.setup()
        self.assertGreater(len(self.sim._engines), 0)

    def test_setup_resets_counters(self):
        self.sim.setup()
        self.assertEqual(self.sim._completed_steps, 0)
        self.assertEqual(self.sim._bundles_generated, 0)
        self.assertEqual(len(self.sim._events), 0)

    def test_setup_calculates_total_steps(self):
        self.sim.setup()
        # 1 hour / 60 seconds = 60 steps
        self.assertEqual(self.sim._total_steps, 60)

    def test_reset_clears_state(self):
        self.sim.setup()
        self.sim.reset()
        self.assertEqual(self.sim.get_state(), SimulationState.INITIALIZED)
        self.assertIsNone(self.sim._topology)
        self.assertEqual(len(self.sim._engines), 0)


class TestBundleGeneration(unittest.TestCase):

    def setUp(self):
        self.config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=1000.0,
        )
        self.sim = Simulator(self.config)
        self.sim.setup()

    def test_high_rate_generates_bundles(self):
        bundle = self.sim.generate_bundle(0)
        self.assertIsNotNone(bundle)
        self.assertIsInstance(bundle, Bundle)

    def test_generated_bundle_source_is_tier_4_or_5(self):
        bundle = self.sim.generate_bundle(0)
        if bundle is not None:
            source_node = self.sim._topology.get_node(bundle.source.node_id)
            self.assertIn(source_node.tier, (4, 5))

    def test_generated_bundle_dest_is_tier_1_or_2(self):
        bundle = self.sim.generate_bundle(0)
        if bundle is not None:
            dest_node = self.sim._topology.get_node(bundle.destination.node_id)
            self.assertIn(dest_node.tier, (1, 2))

    def test_generated_bundle_tracked_in_active_set(self):
        bundle = self.sim.generate_bundle(0)
        if bundle is not None:
            self.assertIn(bundle.bundle_id, self.sim._active_bundles)

    def test_generated_bundle_has_sim_birth_time(self):
        bundle = self.sim.generate_bundle(0)
        if bundle is not None:
            self.assertIn(bundle.bundle_id, self.sim._bundle_sim_birth)

    def test_zero_rate_never_generates(self):
        config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=0.0,
        )
        sim = Simulator(config)
        sim.setup()
        bundle = sim.generate_bundle(0)
        self.assertIsNone(bundle)


class TestSimulationStep(unittest.TestCase):

    def setUp(self):
        self.config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=1000.0,
        )
        self.sim = Simulator(self.config)
        self.sim.setup()

    def test_step_returns_list_of_events(self):
        events = self.sim.step(0.0)
        self.assertIsInstance(events, list)

    def test_step_increments_completed_steps(self):
        self.sim.step(0.0)
        self.assertEqual(self.sim._completed_steps, 1)
        self.sim.step(60.0)
        self.assertEqual(self.sim._completed_steps, 2)

    def test_step_updates_current_time(self):
        self.sim.step(120.0)
        self.assertEqual(self.sim._current_time, 120.0)


class TestSimulatorRun(unittest.TestCase):

    def test_short_run_completes(self):
        config = SimulationConfig(
            name="short-test",
            duration_hours=0.1,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=100.0,
        )
        sim = Simulator(config)
        result = sim.run()
        self.assertEqual(sim.get_state(), SimulationState.COMPLETED)
        self.assertIsInstance(result, SimulationResult)

    def test_run_returns_result_with_config(self):
        config = SimulationConfig(
            name="config-check",
            duration_hours=0.1,
            time_step_seconds=60.0,
            seed=7,
        )
        sim = Simulator(config)
        result = sim.run()
        self.assertEqual(result.config.name, "config-check")
        self.assertEqual(result.config.seed, 7)

    def test_run_generates_bundles(self):
        config = SimulationConfig(
            name="gen-test",
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=100.0,
        )
        sim = Simulator(config)
        result = sim.run()
        self.assertGreater(result.total_bundles, 0)

    def test_delivery_ratio_in_range(self):
        config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=50.0,
        )
        sim = Simulator(config)
        result = sim.run()
        self.assertGreaterEqual(result.delivery_ratio, 0.0)
        self.assertLessEqual(result.delivery_ratio, 1.0)

    def test_deterministic_with_same_seed(self):
        config1 = SimulationConfig(
            duration_hours=0.5,
            time_step_seconds=60.0,
            seed=123,
            bundle_generation_rate_per_hour=100.0,
        )
        config2 = SimulationConfig(
            duration_hours=0.5,
            time_step_seconds=60.0,
            seed=123,
            bundle_generation_rate_per_hour=100.0,
        )
        sim1 = Simulator(config1)
        sim2 = Simulator(config2)
        r1 = sim1.run()
        r2 = sim2.run()
        self.assertEqual(r1.total_bundles, r2.total_bundles)

    def test_different_seeds_may_differ(self):
        config1 = SimulationConfig(
            duration_hours=0.5,
            time_step_seconds=60.0,
            seed=1,
            bundle_generation_rate_per_hour=200.0,
        )
        config2 = SimulationConfig(
            duration_hours=0.5,
            time_step_seconds=60.0,
            seed=999,
            bundle_generation_rate_per_hour=200.0,
        )
        sim1 = Simulator(config1)
        sim2 = Simulator(config2)
        r1 = sim1.run()
        r2 = sim2.run()
        # Not guaranteed to differ, but with 200/hour rate and different
        # seeds, the bundle counts should differ most of the time
        # (we accept either outcome but log if identical)
        if r1.total_bundles == r2.total_bundles:
            pass  # acceptable rare coincidence

    def test_run_populates_per_priority_stats(self):
        config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=100.0,
        )
        sim = Simulator(config)
        result = sim.run()
        self.assertGreater(len(result.per_priority_stats), 0)
        for prio_name, stats in result.per_priority_stats.items():
            self.assertIn("delivered", stats)
            self.assertIn("dropped", stats)

    def test_run_populates_per_node_stats(self):
        config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=100.0,
        )
        sim = Simulator(config)
        result = sim.run()
        self.assertGreater(len(result.per_node_stats), 0)
        for node_id, stats in result.per_node_stats.items():
            self.assertIn("queue_size", stats)
            self.assertIn("buffer_utilization", stats)

    def test_run_events_list_populated(self):
        config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
            bundle_generation_rate_per_hour=100.0,
        )
        sim = Simulator(config)
        result = sim.run()
        self.assertGreater(len(result.events), 0)


class TestSimulatorProgress(unittest.TestCase):

    def test_progress_zero_before_setup(self):
        sim = Simulator(SimulationConfig(duration_hours=1.0))
        self.assertEqual(sim.get_progress(), 0.0)

    def test_progress_after_setup(self):
        config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
        )
        sim = Simulator(config)
        sim.setup()
        self.assertAlmostEqual(sim.get_progress(), 0.0)

    def test_progress_after_partial_run(self):
        config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
        )
        sim = Simulator(config)
        sim.setup()
        sim.step(0.0)
        sim.step(60.0)
        # 2 steps out of 60 = 0.0333...
        self.assertAlmostEqual(sim.get_progress(), 2 / 60, places=3)

    def test_progress_caps_at_one(self):
        config = SimulationConfig(
            duration_hours=0.05,
            time_step_seconds=60.0,
        )
        sim = Simulator(config)
        sim.setup()
        sim.step(0.0)
        sim.step(60.0)
        sim.step(120.0)
        self.assertLessEqual(sim.get_progress(), 1.0)

    def test_intermediate_results(self):
        config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
        )
        sim = Simulator(config)
        sim.setup()
        sim.step(0.0)
        result = sim.get_intermediate_results()
        self.assertIsInstance(result, SimulationResult)


class TestSimulatorInjectBundle(unittest.TestCase):

    def setUp(self):
        self.config = SimulationConfig(
            duration_hours=1.0,
            time_step_seconds=60.0,
            seed=42,
        )
        self.sim = Simulator(self.config)
        self.sim.setup()

    def test_inject_returns_event(self):
        source_nodes = [
            n for n in self.sim._topology._nodes.values()
            if n.tier in (4, 5)
        ]
        dest_nodes = [
            n for n in self.sim._topology._nodes.values()
            if n.tier in (1, 2)
        ]
        bundle = create_science_bundle(
            source_node=source_nodes[0].node_id,
            destination_node=dest_nodes[0].node_id,
            data_mb=10.0,
            priority=BundlePriority.STANDARD,
        )
        event = self.sim.inject_bundle(bundle, source_nodes[0].node_id)
        self.assertIsNotNone(event)
        self.assertEqual(event.source, source_nodes[0].node_id)

    def test_inject_unknown_node_returns_none(self):
        source_nodes = [
            n for n in self.sim._topology._nodes.values()
            if n.tier in (4, 5)
        ]
        dest_nodes = [
            n for n in self.sim._topology._nodes.values()
            if n.tier in (1, 2)
        ]
        bundle = create_science_bundle(
            source_node=source_nodes[0].node_id,
            destination_node=dest_nodes[0].node_id,
            data_mb=10.0,
        )
        event = self.sim.inject_bundle(bundle, "nonexistent-node-id")
        self.assertIsNone(event)


class TestSimulatorFailureRecovery(unittest.TestCase):

    def test_failed_state_on_exception(self):
        sim = Simulator(SimulationConfig(duration_hours=0.1, seed=42))

        original_step = sim.step

        def bomb(*args, **kwargs):
            raise RuntimeError("injected failure")

        sim.step = bomb
        result = sim.run()
        self.assertEqual(sim.get_state(), SimulationState.FAILED)
        self.assertIsInstance(result, SimulationResult)


if __name__ == "__main__":
    unittest.main()
