"""
Tests for AETHERIX RL Routing Agent
Validates Q-learning routing decisions, reward calculation, and state handling.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.rl_agent import (NetworkState, RLRoutingAgent, RoutingAction,
                              RoutingDecision)


class TestRoutingAgent(unittest.TestCase):

    def setUp(self):
        self.agent = RLRoutingAgent(node_id="mars.areo.alpha", epsilon=0.0)
        self.state = NetworkState(
            current_node="mars.areo.alpha",
            neighbors=["mars.polar.gamma", "transit.esl4.relay", "mars.surface.rover-01"],
            link_qualities={
                "mars.polar.gamma": 0.85,
                "transit.esl4.relay": 0.72,
                "mars.surface.rover-01": 0.95,
            },
            buffer_occupancy=0.35,
            bundle_priority=2,
            bundle_size_mb=500.0,
            bundle_deadline_hours=24.0,
            destination_node="earth.control.moc",
        )

    def test_forward_when_destination_is_neighbor(self):
        state = NetworkState(
            current_node="mars.polar.gamma",
            neighbors=["earth.control.moc"],
            link_qualities={"earth.control.moc": 0.8},
            buffer_occupancy=0.1,
            bundle_priority=2,
            bundle_size_mb=100.0,
            bundle_deadline_hours=24.0,
            destination_node="earth.control.moc",
        )
        decision = self.agent.select_action(state)
        self.assertEqual(decision.action, RoutingAction.FORWARD)
        self.assertEqual(decision.next_hop, "earth.control.moc")
        self.assertGreater(decision.confidence, 0.9)

    def test_store_when_no_neighbors(self):
        state = NetworkState(
            current_node="mars.surface.rover-01",
            neighbors=[],
            link_qualities={},
            buffer_occupancy=0.5,
            bundle_priority=2,
            bundle_size_mb=500.0,
            bundle_deadline_hours=24.0,
            destination_node="earth.control.moc",
        )
        decision = self.agent.select_action(state)
        self.assertEqual(decision.action, RoutingAction.STORE)

    def test_drop_low_priority_high_buffer(self):
        state = NetworkState(
            current_node="mars.areo.alpha",
            neighbors=["mars.polar.gamma"],
            link_qualities={"mars.polar.gamma": 0.2},
            buffer_occupancy=0.95,
            bundle_priority=4,
            bundle_size_mb=1000.0,
            bundle_deadline_hours=720.0,
            destination_node="earth.control.moc",
        )
        decision = self.agent.select_action(state)
        self.assertEqual(decision.action, RoutingAction.DROP)

    def test_urgent_uses_best_link(self):
        state = NetworkState(
            current_node="mars.areo.alpha",
            neighbors=["transit.esl4.relay", "mars.polar.gamma"],
            link_qualities={"transit.esl4.relay": 0.9, "mars.polar.gamma": 0.5},
            buffer_occupancy=0.3,
            bundle_priority=0,
            bundle_size_mb=10.0,
            bundle_deadline_hours=1.0,
            destination_node="earth.control.moc",
        )
        decision = self.agent.select_action(state)
        self.assertEqual(decision.action, RoutingAction.FORWARD)
        self.assertEqual(decision.next_hop, "transit.esl4.relay")

    def test_reward_calculation_delivered(self):
        reward = self.agent.calculate_reward(
            delivered=True, delay_seconds=750, hops=5, dropped=False, energy_wh=2.0
        )
        self.assertAlmostEqual(reward, 1.0 - 0.001 * 750 - 0.1 * 5 - 0.01 * 2.0, places=4)
        self.assertGreater(reward, -1.0)

    def test_reward_calculation_dropped(self):
        reward = self.agent.calculate_reward(
            delivered=False, delay_seconds=500, hops=3, dropped=True, energy_wh=1.0
        )
        self.assertLess(reward, -10.0)

    def test_reward_weights(self):
        self.assertEqual(self.agent.ALPHA_DELIVERY, 1.0)
        self.assertEqual(self.agent.BETA_DELAY, 0.001)
        self.assertEqual(self.agent.GAMMA_HOPS, 0.1)
        self.assertEqual(self.agent.DELTA_DROPS, 10.0)
        self.assertEqual(self.agent.EPSILON_ENERGY, 0.01)

    def test_state_key_generation(self):
        key = self.agent.get_state_key(self.state)
        self.assertIn("mars.areo.alpha", key)
        self.assertIn("low", key)
        self.assertIn("good", key)
        self.assertIn("normal", key)

    def test_state_key_high_buffer(self):
        state = NetworkState(
            current_node="node1", neighbors=["n2"],
            link_qualities={"n2": 0.2}, buffer_occupancy=0.9,
            bundle_priority=0, bundle_size_mb=1.0,
            bundle_deadline_hours=1.0, destination_node="dest",
        )
        key = self.agent.get_state_key(state)
        self.assertIn("high", key)
        self.assertIn("poor", key)
        self.assertIn("urgent", key)

    def test_q_table_update(self):
        self.agent.update(self.state, RoutingAction.FORWARD, 0.5, None)
        state_key = self.agent.get_state_key(self.state)
        self.assertIn(state_key, self.agent.q_table)
        self.assertIn("forward", self.agent.q_table[state_key])

    def test_exploration_mode(self):
        explore_agent = RLRoutingAgent(node_id="test", epsilon=1.0)
        actions = set()
        for _ in range(50):
            decision = explore_agent.select_action(self.state)
            actions.add(decision.action)
        self.assertIn(RoutingAction.STORE, actions)

    def test_confidence_always_between_0_and_1(self):
        for _ in range(20):
            decision = self.agent.select_action(self.state)
            self.assertGreaterEqual(decision.confidence, 0.0)
            self.assertLessEqual(decision.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
