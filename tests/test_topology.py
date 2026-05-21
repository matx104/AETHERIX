"""
Tests for AETHERIX Network Topology.

Validates 5-tier DTN topology construction, node registration,
inter-tier link creation, BFS routing, and contact graph generation.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orbital.topology import NetworkTopology, create_default_topology


class TestNetworkTopology(unittest.TestCase):
    """Test cases for NetworkTopology class."""

    def setUp(self) -> None:
        self.topo: NetworkTopology = create_default_topology()

    def test_create_default_topology(self) -> None:
        self.assertEqual(self.topo.get_node_count(), 241)

    def test_tier_summary(self) -> None:
        expected = {1: 5, 2: 51, 3: 4, 4: 4, 5: 177}
        self.assertEqual(self.topo.get_tier_summary(), expected)

    def test_get_node(self) -> None:
        node = self.topo.get_node("dsn-goldstone")
        self.assertIsNotNone(node)
        self.assertEqual(node.node_id, "dsn-goldstone")
        missing = self.topo.get_node("nonexistent-node")
        self.assertIsNone(missing)

    def test_get_nodes_by_tier(self) -> None:
        tier1 = self.topo.get_nodes_by_tier(1)
        self.assertEqual(len(tier1), 5)

    def test_inter_tier_links_exist(self) -> None:
        links = self.topo.get_inter_tier_links()
        self.assertGreater(len(links), 0)

    def test_find_route(self) -> None:
        path = self.topo.find_route("sensor-001", "dsn-goldstone")
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], "sensor-001")

    def test_contact_graph(self) -> None:
        cg = self.topo.get_contact_graph()
        self.assertIsNotNone(cg)
        self.assertGreater(len(cg.get_contacts_from("dsn-goldstone")), 0)

    def test_get_neighbors(self) -> None:
        neighbors = self.topo.get_neighbors("dsn-goldstone")
        self.assertGreater(len(neighbors), 0)


if __name__ == '__main__':
    unittest.main()
