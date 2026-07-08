"""
Tests for AETHERIX Contact Graph

Validates DTN contact graph operations: contact creation, BFS pathfinding,
reachability analysis, and active contact queries.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.contact_graph import Contact, ContactGraph, ContactState


class TestContact(unittest.TestCase):

    def setUp(self):
        self.contact = Contact(
            contact_id="c1",
            source_node="MARS_ORBIT_1",
            dest_node="EM_LAGRANGE_1",
            start_time=1000.0,
            end_time=2000.0,
            data_rate_mbps=50.0,
            delay_seconds=600.0,
        )

    def test_duration_seconds(self):
        self.assertEqual(self.contact.duration_seconds, 1000.0)

    def test_volume_calculation(self):
        vol = self.contact.calculate_volume()
        self.assertAlmostEqual(vol, 50.0 * 1000.0 / 8.0)

    def test_default_state_is_pending(self):
        self.assertEqual(self.contact.state, ContactState.PENDING)

    def test_default_volume_zero(self):
        self.assertEqual(self.contact.volume_megabits, 0.0)


class TestContactGraphCreation(unittest.TestCase):

    def setUp(self):
        self.graph = ContactGraph()
        self.c1 = Contact(
            "c1", "A", "B", 0.0, 100.0, 50.0, 10.0,
        )
        self.c2 = Contact(
            "c2", "B", "C", 50.0, 150.0, 50.0, 20.0,
        )
        self.c3 = Contact(
            "c3", "A", "D", 0.0, 100.0, 50.0, 15.0,
        )

    def test_empty_graph(self):
        g = ContactGraph()
        self.assertEqual(g.get_contacts_from("A"), [])

    def test_add_contact(self):
        self.graph.add_contact(self.c1)
        from_a = self.graph.get_contacts_from("A")
        self.assertEqual(len(from_a), 1)
        self.assertEqual(from_a[0].contact_id, "c1")

    def test_add_multiple_contacts(self):
        self.graph.add_contact(self.c1)
        self.graph.add_contact(self.c2)
        self.graph.add_contact(self.c3)
        from_a = self.graph.get_contacts_from("A")
        self.assertEqual(len(from_a), 2)

    def test_incoming_contacts(self):
        self.graph.add_contact(self.c1)
        to_b = self.graph.get_contacts_to("B")
        self.assertEqual(len(to_b), 1)
        self.assertEqual(to_b[0].contact_id, "c1")


class TestContactGraphPathfinding(unittest.TestCase):

    def setUp(self):
        self.graph = ContactGraph()
        self.graph.add_contact(Contact("e1", "A", "B", 0, 100, 50, 10))
        self.graph.add_contact(Contact("e2", "B", "C", 0, 100, 50, 10))
        self.graph.add_contact(Contact("e3", "C", "D", 0, 100, 50, 10))

    def test_direct_path(self):
        path = self.graph.find_path("A", "B")
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0].source_node, "A")
        self.assertEqual(path[0].dest_node, "B")

    def test_multi_hop_path(self):
        path = self.graph.find_path("A", "D")
        self.assertEqual(len(path), 3)
        self.assertEqual(path[0].source_node, "A")
        self.assertEqual(path[-1].dest_node, "D")

    def test_same_source_dest_returns_empty(self):
        path = self.graph.find_path("A", "A")
        self.assertEqual(path, [])

    def test_no_path_returns_empty(self):
        path = self.graph.find_path("A", "Z")
        self.assertEqual(path, [])

    def test_bfs_finds_shortest_path(self):
        graph = ContactGraph()
        graph.add_contact(Contact("long1", "A", "B", 0, 100, 50, 10))
        graph.add_contact(Contact("long2", "B", "D", 0, 100, 50, 10))
        graph.add_contact(Contact("short", "A", "D", 0, 100, 50, 10))
        path = graph.find_path("A", "D")
        # BFS: A's outgoing contacts are [long1, short]. When iterating,
        # long1 (A->B) is not destination so B is queued; then short
        # (A->D) IS the destination — return immediately (1 hop).
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0].contact_id, "short")

    def test_cyclic_graph_no_infinite_loop(self):
        graph = ContactGraph()
        graph.add_contact(Contact("cyc1", "A", "B", 0, 100, 50, 10))
        graph.add_contact(Contact("cyc2", "B", "A", 0, 100, 50, 10))
        graph.add_contact(Contact("cyc3", "B", "C", 0, 100, 50, 10))
        path = graph.find_path("A", "C")
        self.assertEqual(len(path), 2)


class TestReachableNodes(unittest.TestCase):

    def setUp(self):
        self.graph = ContactGraph()
        self.graph.add_contact(Contact("e1", "A", "B", 0, 100, 50, 10))
        self.graph.add_contact(Contact("e2", "B", "C", 0, 100, 50, 10))
        self.graph.add_contact(Contact("e3", "A", "D", 0, 100, 50, 10))

    def test_reachable_from_source(self):
        reachable = self.graph.get_reachable_nodes("A")
        self.assertIn("B", reachable)
        self.assertIn("C", reachable)
        self.assertIn("D", reachable)
        self.assertNotIn("A", reachable)

    def test_reachable_sorted(self):
        reachable = self.graph.get_reachable_nodes("A")
        self.assertEqual(reachable, sorted(reachable))

    def test_no_reachable_from_isolated(self):
        reachable = self.graph.get_reachable_nodes("Z")
        self.assertEqual(reachable, [])

    def test_reachable_from_leaf(self):
        reachable = self.graph.get_reachable_nodes("C")
        self.assertEqual(reachable, [])


class TestActiveContacts(unittest.TestCase):

    def setUp(self):
        self.graph = ContactGraph()
        self.graph.add_contact(Contact("c1", "A", "B", 0, 100, 50, 10))
        self.graph.add_contact(Contact("c2", "B", "C", 50, 150, 50, 10))
        self.graph.add_contact(Contact("c3", "C", "D", 200, 300, 50, 10))

    def test_active_at_t50(self):
        active = self.graph.get_active_contacts(50.0)
        ids = {c.contact_id for c in active}
        self.assertIn("c1", ids)
        self.assertIn("c2", ids)
        self.assertNotIn("c3", ids)

    def test_active_at_t0(self):
        active = self.graph.get_active_contacts(0.0)
        ids = {c.contact_id for c in active}
        self.assertIn("c1", ids)
        self.assertNotIn("c2", ids)

    def test_active_at_boundary(self):
        active = self.graph.get_active_contacts(100.0)
        ids = {c.contact_id for c in active}
        self.assertIn("c1", ids)
        self.assertIn("c2", ids)

    def test_no_active_in_future(self):
        active = self.graph.get_active_contacts(500.0)
        self.assertEqual(len(active), 0)

    def test_no_active_before_start(self):
        active = self.graph.get_active_contacts(-10.0)
        self.assertEqual(len(active), 0)


class TestContactStateEnum(unittest.TestCase):

    def test_all_states_exist(self):
        states = [s.value for s in ContactState]
        self.assertIn("pending", states)
        self.assertIn("active", states)
        self.assertIn("completed", states)
        self.assertIn("failed", states)
        self.assertIn("cancelled", states)


if __name__ == "__main__":
    unittest.main()
