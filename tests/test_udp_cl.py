"""
Tests for UDP Convergence Layer (optical ISL).

Validates fragmentation, reassembly, loss simulation, and statistics.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.bundle import Bundle
from routing.udp_cl import (
    UDPCLDatagram,
    UDPCLStats,
    UDPConvergenceLayer,
)


def _make_bundle(size: int = 5000, bid: str = "bundle-1") -> Bundle:
    return Bundle(
        bundle_id=bid,
        payload=b"X" * size,
        payload_size_bytes=size,
    )


class TestUDPCLDatagram(unittest.TestCase):

    def test_defaults(self):
        dg = UDPCLDatagram(source="a", destination="b", payload=b"data")
        self.assertEqual(dg.sequence_number, 0)
        self.assertEqual(dg.bundle_id, "")
        self.assertFalse(dg.is_fragment)
        self.assertEqual(dg.fragment_offset, 0)
        self.assertEqual(dg.total_length, 0)


class TestUDPCLStats(unittest.TestCase):

    def test_defaults(self):
        stats = UDPCLStats()
        self.assertEqual(stats.datagrams_sent, 0)
        self.assertEqual(stats.datagrams_received, 0)
        self.assertEqual(stats.datagrams_lost, 0)


class TestFragmentation(unittest.TestCase):

    def setUp(self):
        self.cl = UDPConvergenceLayer(node_id="test", mtu_bytes=1472, loss_rate=0.0)

    def test_fragment_small_bundle(self):
        bundle = _make_bundle(500)
        datagrams = self.cl.fragment_bundle(bundle)
        self.assertEqual(len(datagrams), 1)
        self.assertFalse(datagrams[0].is_fragment)

    def test_fragment_large_bundle(self):
        bundle = _make_bundle(5000)
        datagrams = self.cl.fragment_bundle(bundle)
        self.assertEqual(len(datagrams), 4)  # ceil(5000/1472) = 4
        for dg in datagrams:
            self.assertTrue(dg.is_fragment)

    def test_fragment_exact_mtu(self):
        bundle = _make_bundle(1472)
        datagrams = self.cl.fragment_bundle(bundle)
        self.assertEqual(len(datagrams), 1)
        self.assertFalse(datagrams[0].is_fragment)

    def test_fragment_empty_bundle(self):
        bundle = Bundle(bundle_id="empty", payload=b"", payload_size_bytes=0)
        datagrams = self.cl.fragment_bundle(bundle)
        self.assertEqual(len(datagrams), 1)
        self.assertFalse(datagrams[0].is_fragment)

    def test_fragment_sequence_numbers(self):
        bundle = _make_bundle(5000)
        datagrams = self.cl.fragment_bundle(bundle)
        seqs = [d.sequence_number for d in datagrams]
        self.assertEqual(seqs, list(range(len(datagrams))))

    def test_fragment_offsets(self):
        bundle = _make_bundle(5000)
        datagrams = self.cl.fragment_bundle(bundle)
        offsets = [d.fragment_offset for d in datagrams]
        self.assertEqual(offsets[0], 0)
        for i in range(1, len(offsets)):
            self.assertGreater(offsets[i], offsets[i - 1])

    def test_fragment_total_length_set(self):
        bundle = _make_bundle(5000)
        datagrams = self.cl.fragment_bundle(bundle)
        for dg in datagrams:
            self.assertEqual(dg.total_length, 5000)


class TestReassembly(unittest.TestCase):

    def setUp(self):
        self.cl = UDPConvergenceLayer(node_id="test", mtu_bytes=1472)

    def test_reconstruct_complete(self):
        bundle = _make_bundle(5000)
        datagrams = self.cl.fragment_bundle(bundle)
        result = self.cl.reconstruct_bundle(datagrams)
        self.assertIsNotNone(result)
        self.assertEqual(result.payload, bundle.payload)

    def test_reconstruct_out_of_order(self):
        bundle = _make_bundle(5000)
        datagrams = self.cl.fragment_bundle(bundle)
        reversed_dg = list(reversed(datagrams))
        result = self.cl.reconstruct_bundle(reversed_dg)
        self.assertIsNotNone(result)
        self.assertEqual(result.payload, bundle.payload)

    def test_reconstruct_missing_fragment(self):
        bundle = _make_bundle(5000)
        datagrams = self.cl.fragment_bundle(bundle)
        incomplete = datagrams[:-1]  # drop last fragment
        result = self.cl.reconstruct_bundle(incomplete)
        self.assertIsNone(result)

    def test_reconstruct_empty_list(self):
        result = self.cl.reconstruct_bundle([])
        self.assertIsNone(result)

    def test_reconstruct_single_datagram(self):
        bundle = _make_bundle(500)
        datagrams = self.cl.fragment_bundle(bundle)
        result = self.cl.reconstruct_bundle(datagrams)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.payload), 500)

    def test_reconstruct_empty_payload(self):
        bundle = Bundle(bundle_id="empty", payload=b"", payload_size_bytes=0)
        datagrams = self.cl.fragment_bundle(bundle)
        result = self.cl.reconstruct_bundle(datagrams)
        self.assertIsNotNone(result)
        self.assertEqual(result.payload, b"")


class TestSendReceive(unittest.TestCase):

    def setUp(self):
        self.cl = UDPConvergenceLayer(node_id="test", mtu_bytes=1472, loss_rate=0.0)

    def test_send_datagram_success(self):
        dg = UDPCLDatagram(source="a", destination="b", payload=b"data")
        result = self.cl.send_datagram(dg)
        self.assertTrue(result)

    def test_send_datagram_updates_stats(self):
        dg = UDPCLDatagram(source="a", destination="b", payload=b"data")
        self.cl.send_datagram(dg)
        stats = self.cl.get_stats()
        self.assertEqual(stats.datagrams_sent, 1)
        self.assertEqual(stats.bytes_sent, 4)

    def test_receive_datagram_updates_stats(self):
        dg = UDPCLDatagram(source="a", destination="b", payload=b"data")
        self.cl.receive_datagram(dg)
        stats = self.cl.get_stats()
        self.assertEqual(stats.datagrams_received, 1)
        self.assertEqual(stats.bytes_received, 4)

    def test_receive_fragment_buffers(self):
        dg = UDPCLDatagram(
            source="a", destination="b", payload=b"data",
            bundle_id="b1", is_fragment=True, fragment_offset=0,
            total_length=1000,
        )
        self.cl.receive_datagram(dg)
        self.assertIn("b1", self.cl._pending_fragments)

    def test_receive_duplicate_fragment_ignored(self):
        dg = UDPCLDatagram(
            source="a", destination="b", payload=b"data",
            bundle_id="b1", is_fragment=True, fragment_offset=0,
            total_length=1000,
        )
        self.cl.receive_datagram(dg)
        self.cl.receive_datagram(dg)
        self.assertEqual(len(self.cl._pending_fragments["b1"]), 1)

    def test_loss_rate_causes_lost(self):
        cl = UDPConvergenceLayer(node_id="test", loss_rate=1.0)
        dg = UDPCLDatagram(source="a", destination="b", payload=b"data")
        result = cl.send_datagram(dg)
        self.assertFalse(result)
        stats = cl.get_stats()
        self.assertEqual(stats.datagrams_lost, 1)

    def test_zero_loss_rate_never_lost(self):
        cl = UDPConvergenceLayer(node_id="test", loss_rate=0.0)
        for _ in range(100):
            dg = UDPCLDatagram(source="a", destination="b", payload=b"x")
            self.assertTrue(cl.send_datagram(dg))
        stats = cl.get_stats()
        self.assertEqual(stats.datagrams_lost, 0)

    def test_get_stats_snapshot(self):
        dg = UDPCLDatagram(source="a", destination="b", payload=b"xxxx")
        self.cl.send_datagram(dg)
        self.cl.receive_datagram(dg)
        stats = self.cl.get_stats()
        self.assertEqual(stats.datagrams_sent, 1)
        self.assertEqual(stats.datagrams_received, 1)
        self.assertEqual(stats.bytes_sent, 4)
        self.assertEqual(stats.bytes_received, 4)


if __name__ == "__main__":
    unittest.main()
