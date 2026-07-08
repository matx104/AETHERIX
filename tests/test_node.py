"""
Tests for DTN Node Model.

Validates node types, capabilities, buffer management,
reachability, and store/forward operations.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.node import (
    NETWORK_TIER_NAMES,
    DTNNode,
    NodeCapabilities,
    NodeStatus,
    NodeType,
    create_dsn_station,
    create_lagrange_relay,
)


def _make_caps(
    buffer_gb: float = 100.0,
    optical: bool = True,
    rf: bool = True,
    rate: float = 50.0,
) -> NodeCapabilities:
    return NodeCapabilities(
        max_buffer_gb=buffer_gb,
        supported_bands=["Ka-band", "optical"],
        optical_capable=optical,
        rf_capable=rf,
        qkd_capable=False,
        max_data_rate_mbps=rate,
        processing_power_mips=10000.0,
    )


class TestNodeEnums(unittest.TestCase):

    def test_node_types(self):
        self.assertEqual(len(NodeType), 6)

    def test_node_statuses(self):
        self.assertEqual(len(NodeStatus), 4)

    def test_tier_names(self):
        self.assertEqual(NETWORK_TIER_NAMES[1], "Earth Ground")
        self.assertEqual(NETWORK_TIER_NAMES[5], "Mars Surface")
        self.assertEqual(len(NETWORK_TIER_NAMES), 5)


class TestDTNNode(unittest.TestCase):

    def setUp(self):
        self.node = DTNNode(
            node_id="test-node",
            node_type=NodeType.GEO_RELAY,
            tier=2,
            capabilities=_make_caps(buffer_gb=100.0),
        )

    def test_defaults(self):
        self.assertEqual(self.node.status, NodeStatus.ACTIVE)
        self.assertEqual(self.node.current_buffer_gb, 0.0)
        self.assertEqual(self.node.total_bundles_forwarded, 0)
        self.assertEqual(self.node.total_bundles_stored, 0)
        self.assertEqual(self.node.connected_neighbors, [])

    def test_buffer_utilization_empty(self):
        self.assertAlmostEqual(self.node.buffer_utilization(), 0.0)

    def test_buffer_utilization_half(self):
        self.node.current_buffer_gb = 50.0
        self.assertAlmostEqual(self.node.buffer_utilization(), 0.5)

    def test_buffer_utilization_full(self):
        self.node.current_buffer_gb = 100.0
        self.assertAlmostEqual(self.node.buffer_utilization(), 1.0)

    def test_buffer_utilization_overflows_caps_at_one(self):
        self.node.current_buffer_gb = 200.0
        self.assertAlmostEqual(self.node.buffer_utilization(), 1.0)

    def test_buffer_utilization_zero_capacity(self):
        node = DTNNode(
            node_id="zero-cap",
            node_type=NodeType.SURFACE_NODE,
            tier=5,
            capabilities=_make_caps(buffer_gb=0.0),
        )
        self.assertEqual(node.buffer_utilization(), 0.0)

    def test_can_accept_bundle_when_empty(self):
        self.assertTrue(self.node.can_accept_bundle(50 * 1024))  # 50 GB in MB

    def test_cannot_accept_when_full(self):
        self.node.current_buffer_gb = 99.0
        self.assertFalse(self.node.can_accept_bundle(2 * 1024))  # 2 GB > 1 GB remaining

    def test_can_accept_bundle_offline(self):
        self.node.status = NodeStatus.OFFLINE
        self.assertFalse(self.node.can_accept_bundle(10))

    def test_store_bundle_success(self):
        result = self.node.store_bundle(10 * 1024)  # 10 GB
        self.assertTrue(result)
        self.assertAlmostEqual(self.node.current_buffer_gb, 10.0)
        self.assertEqual(self.node.total_bundles_stored, 1)

    def test_store_bundle_overflow(self):
        result = self.node.store_bundle(200 * 1024)  # 200 GB > 100 GB cap
        self.assertFalse(result)
        self.assertAlmostEqual(self.node.current_buffer_gb, 0.0)

    def test_store_bundle_offline(self):
        self.node.status = NodeStatus.OFFLINE
        result = self.node.store_bundle(10)
        self.assertFalse(result)

    def test_forward_bundle(self):
        self.node.forward_bundle(100)
        self.assertEqual(self.node.total_bundles_forwarded, 1)
        self.node.forward_bundle(100)
        self.assertEqual(self.node.total_bundles_forwarded, 2)

    def test_is_reachable_active(self):
        self.assertTrue(self.node.is_reachable())

    def test_is_reachable_degraded(self):
        self.node.status = NodeStatus.DEGRADED
        self.assertTrue(self.node.is_reachable())

    def test_is_reachable_offline(self):
        self.node.status = NodeStatus.OFFLINE
        self.assertFalse(self.node.is_reachable())

    def test_is_reachable_maintenance(self):
        self.node.status = NodeStatus.MAINTENANCE
        self.assertFalse(self.node.is_reachable())


class TestFactoryFunctions(unittest.TestCase):

    def test_create_dsn_station(self):
        node = create_dsn_station("Goldstone")
        self.assertEqual(node.node_id, "dsn_goldstone")
        self.assertEqual(node.node_type, NodeType.GROUND_STATION)
        self.assertEqual(node.tier, 1)
        self.assertTrue(node.capabilities.optical_capable)
        self.assertTrue(node.capabilities.rf_capable)
        self.assertFalse(node.capabilities.qkd_capable)
        self.assertEqual(node.capabilities.max_data_rate_mbps, 200.0)

    def test_create_dsn_station_case(self):
        node = create_dsn_station("Madrid")
        self.assertEqual(node.node_id, "dsn_madrid")

    def test_create_lagrange_relay(self):
        node = create_lagrange_relay("L4")
        self.assertEqual(node.node_id, "lagrange_l4")
        self.assertEqual(node.node_type, NodeType.LAGRANGE_RELAY)
        self.assertEqual(node.tier, 3)
        self.assertTrue(node.capabilities.optical_capable)
        self.assertTrue(node.capabilities.rf_capable)
        self.assertTrue(node.capabilities.qkd_capable)
        self.assertEqual(node.capabilities.max_data_rate_mbps, 150.0)

    def test_dsn_has_large_buffer(self):
        node = create_dsn_station("Canberra")
        self.assertGreater(node.capabilities.max_buffer_gb, 1000)

    def test_lagrange_has_qkd(self):
        node = create_lagrange_relay("L5")
        self.assertTrue(node.capabilities.qkd_capable)


if __name__ == "__main__":
    unittest.main()
