"""
Tests for AETHERIX Policy Engine.

Validates declarative routing policies, rule matching, congestion
control, deep-space store logic, and default policy loading.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simulation.policy_engine import (
    PolicyDecision,
    PolicyEngine,
    PolicyRule,
    RoutingPolicy,
)


class TestPolicyEngine(unittest.TestCase):
    """Test cases for PolicyEngine rule-based routing."""

    def setUp(self) -> None:
        self.engine: PolicyEngine = PolicyEngine()

    def test_add_remove_policy(self) -> None:
        policy = RoutingPolicy(
            name="test-policy",
            description="test",
            rules=[PolicyRule(
                condition_field="priority", operator="eq",
                value=0, action="forward",
            )],
        )
        self.engine.add_policy(policy)
        self.assertEqual(len(self.engine.get_policies()), 1)
        self.engine.remove_policy("test-policy")
        self.assertEqual(len(self.engine.get_policies()), 0)

    def test_evaluate_matching_rule(self) -> None:
        self.engine.add_policy(RoutingPolicy(
            name="emergency-rule",
            description="Forward emergency bundles",
            rules=[PolicyRule(
                condition_field="priority", operator="lte",
                value=1, action="forward", target="best_link",
            )],
            priority=100,
        ))
        decision = self.engine.evaluate({"priority": 0})
        self.assertEqual(decision.action, "forward")

    def test_evaluate_no_match(self) -> None:
        decision = self.engine.evaluate({"priority": 5})
        self.assertEqual(decision.action, "store")

    def test_load_default_policies(self) -> None:
        self.engine.load_default_policies()
        self.assertEqual(len(self.engine.get_policies()), 5)

    def test_congestion_control(self) -> None:
        self.engine.load_default_policies()
        decision = self.engine.evaluate({
            "buffer_occupancy": 0.95,
            "priority": 3,
        })
        self.assertEqual(decision.action, "drop")

    def test_deep_space_store(self) -> None:
        self.engine.load_default_policies()
        decision = self.engine.evaluate({
            "link_quality": 0.1,
        })
        self.assertEqual(decision.action, "store")


if __name__ == '__main__':
    unittest.main()
