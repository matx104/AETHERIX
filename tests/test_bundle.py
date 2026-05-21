"""
Tests for AETHERIX Bundle Protocol v7 Module
Validates bundle creation, endpoint IDs, priority, custody transfer, and serialization.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.bundle import (Bundle, BundleFlags, BundlePriority, EndpointID,
                            create_science_bundle)


class TestEndpointID(unittest.TestCase):

    def test_from_string_full(self):
        eid = EndpointID.from_string("dtn://mars.surface.rover-01/science")
        self.assertEqual(eid.scheme, "dtn")
        self.assertEqual(eid.node_id, "mars.surface.rover-01")
        self.assertEqual(eid.service_id, "science")

    def test_from_string_no_service(self):
        eid = EndpointID.from_string("dtn://earth.control.moc")
        self.assertEqual(eid.scheme, "dtn")
        self.assertEqual(eid.node_id, "earth.control.moc")
        self.assertEqual(eid.service_id, "")

    def test_from_string_bare_node(self):
        eid = EndpointID.from_string("mars.areo.alpha")
        self.assertEqual(eid.scheme, "dtn")
        self.assertEqual(eid.node_id, "mars.areo.alpha")

    def test_str_representation_with_service(self):
        eid = EndpointID(scheme="dtn", node_id="mars.surface.rover-01", service_id="science")
        self.assertEqual(str(eid), "dtn://mars.surface.rover-01/science")

    def test_str_representation_without_service(self):
        eid = EndpointID(scheme="dtn", node_id="earth.control.moc")
        self.assertEqual(str(eid), "dtn://earth.control.moc")

    def test_roundtrip(self):
        original = "dtn://transit.esl4.relay/quantum"
        eid = EndpointID.from_string(original)
        self.assertEqual(str(eid), original)


class TestBundlePriority(unittest.TestCase):

    def test_priority_ordering(self):
        self.assertLess(BundlePriority.EMERGENCY, BundlePriority.HIGH_SCIENCE)
        self.assertLess(BundlePriority.HIGH_SCIENCE, BundlePriority.STANDARD)
        self.assertLess(BundlePriority.STANDARD, BundlePriority.HOUSEKEEPING)
        self.assertLess(BundlePriority.HOUSEKEEPING, BundlePriority.BULK)

    def test_priority_values(self):
        self.assertEqual(BundlePriority.EMERGENCY, 0)
        self.assertEqual(BundlePriority.HIGH_SCIENCE, 1)
        self.assertEqual(BundlePriority.STANDARD, 2)
        self.assertEqual(BundlePriority.HOUSEKEEPING, 3)
        self.assertEqual(BundlePriority.BULK, 4)

    def test_is_intenum(self):
        self.assertIsInstance(BundlePriority.STANDARD, int)


class TestBundleCreation(unittest.TestCase):

    def test_default_bundle(self):
        bundle = Bundle()
        self.assertIsNotNone(bundle.bundle_id)
        self.assertEqual(len(bundle.bundle_id), 8)
        self.assertEqual(bundle.priority, BundlePriority.STANDARD)
        self.assertEqual(bundle.lifetime_seconds, 86400 * 7)
        self.assertEqual(bundle.payload, b"")
        self.assertEqual(bundle.hops, [])
        self.assertEqual(bundle.custody_holders, [])

    def test_bundle_unique_ids(self):
        b1 = Bundle()
        b2 = Bundle()
        self.assertNotEqual(b1.bundle_id, b2.bundle_id)

    def test_bundle_with_payload(self):
        bundle = Bundle(payload=b"hello", payload_size_bytes=5)
        self.assertEqual(bundle.payload_size_bytes, 5)

    def test_bundle_post_init_payload_size(self):
        bundle = Bundle(payload=b"test data here")
        self.assertEqual(bundle.payload_size_bytes, len(b"test data here"))


class TestBundleLifetime(unittest.TestCase):

    def test_not_expired_initially(self):
        bundle = Bundle(lifetime_seconds=3600)
        self.assertFalse(bundle.is_expired)

    def test_expired_after_lifetime(self):
        bundle = Bundle(
            creation_time=time.time() - 7200,
            lifetime_seconds=3600,
        )
        self.assertTrue(bundle.is_expired)

    def test_remaining_lifetime_positive(self):
        bundle = Bundle(lifetime_seconds=86400)
        remaining = bundle.remaining_lifetime
        self.assertGreater(remaining, 0)
        self.assertLessEqual(remaining, 86400)

    def test_age_seconds(self):
        bundle = Bundle()
        age = bundle.age_seconds
        self.assertGreaterEqual(age, 0)
        self.assertLess(age, 5)


class TestCustodyTransfer(unittest.TestCase):

    def test_accept_custody(self):
        bundle = Bundle()
        bundle.accept_custody("mars.areo.alpha")
        self.assertIn("mars.areo.alpha", bundle.custody_holders)
        self.assertEqual(len(bundle.hops), 1)
        self.assertEqual(bundle.hops[0]["action"], "CUSTODY_ACCEPTED")

    def test_release_custody(self):
        bundle = Bundle()
        bundle.accept_custody("mars.areo.alpha")
        bundle.release_custody("mars.areo.alpha")
        self.assertNotIn("mars.areo.alpha", bundle.custody_holders)

    def test_multi_hop_custody_chain(self):
        bundle = Bundle()
        bundle.accept_custody("mars.areo.alpha")
        bundle.add_hop("mars.areo.alpha", "FORWARD")
        bundle.accept_custody("transit.esl4.relay")
        self.assertEqual(len(bundle.custody_holders), 2)
        self.assertEqual(len(bundle.hops), 3)


class TestBundleHops(unittest.TestCase):

    def test_add_hop(self):
        bundle = Bundle()
        bundle.add_hop("node_a", "FORWARD")
        self.assertEqual(len(bundle.hops), 1)
        self.assertEqual(bundle.hops[0]["node"], "node_a")
        self.assertEqual(bundle.hops[0]["action"], "FORWARD")
        self.assertEqual(bundle.hops[0]["hop_number"], 1)

    def test_multiple_hops_increment(self):
        bundle = Bundle()
        bundle.add_hop("node_a", "FORWARD")
        bundle.add_hop("node_b", "STORE")
        bundle.add_hop("node_c", "FORWARD")
        self.assertEqual(len(bundle.hops), 3)
        self.assertEqual(bundle.hops[2]["hop_number"], 3)


class TestBundleSerialization(unittest.TestCase):

    def test_to_dict(self):
        bundle = create_science_bundle(
            "mars.surface.rover-01", "earth.control.moc", 500.0
        )
        d = bundle.to_dict()
        self.assertIn("bundle_id", d)
        self.assertIn("source", d)
        self.assertIn("destination", d)
        self.assertIn("priority", d)
        self.assertIn("payload_size_bytes", d)
        self.assertIn("hops", d)

    def test_str_representation(self):
        bundle = create_science_bundle(
            "mars.surface.rover-01", "earth.control.moc", 100.0
        )
        s = str(bundle)
        self.assertIn("Bundle[", s)
        self.assertIn("mars.surface.rover-01", s)
        self.assertIn("earth.control.moc", s)


class TestCreateScienceBundle(unittest.TestCase):

    def test_factory_creates_valid_bundle(self):
        bundle = create_science_bundle(
            source_node="mars.surface.rover-01",
            destination_node="earth.control.moc",
            data_mb=500.0,
            priority=BundlePriority.HIGH_SCIENCE,
        )
        self.assertEqual(bundle.source.node_id, "mars.surface.rover-01")
        self.assertEqual(bundle.source.service_id, "science")
        self.assertEqual(bundle.destination.node_id, "earth.control.moc")
        self.assertEqual(bundle.priority, BundlePriority.HIGH_SCIENCE)
        self.assertEqual(bundle.payload_size_bytes, int(500.0 * 1024 * 1024))
        self.assertEqual(bundle.lifetime_seconds, 86400 * 7)

    def test_default_priority_is_standard(self):
        bundle = create_science_bundle("a", "b", 100.0)
        self.assertEqual(bundle.priority, BundlePriority.STANDARD)


class TestBundleFlags(unittest.TestCase):

    def test_flag_values(self):
        self.assertEqual(BundleFlags.IS_FRAGMENT, 0x01)
        self.assertEqual(BundleFlags.CUSTODY_REQUESTED, 0x08)
        self.assertEqual(BundleFlags.DEST_IS_SINGLETON, 0x10)

    def test_default_flags(self):
        bundle = Bundle()
        self.assertEqual(bundle.flags, BundleFlags.DEST_IS_SINGLETON)


if __name__ == "__main__":
    unittest.main()
