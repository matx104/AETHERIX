"""
Tests for AETHERIX Forwarding Engine, LTP, TCPCL, and UDPCL.

Validates bundle queuing, priority ordering, store-and-forward logic,
LTP segmentation/reconstruction, and convergence-layer transports.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.bundle import Bundle, BundlePriority, EndpointID
from routing.forwarding_engine import BundleQueue, ForwardingEngine
from routing.ltp import LTPReport, LTPSessionEngine
from routing.node import DTNNode, NodeCapabilities, NodeType
from routing.rl_agent import RLRoutingAgent
from routing.tcpcl import TCPConvergenceLayer
from routing.udp_cl import UDPConvergenceLayer


def _make_bundle(
    priority: BundlePriority = BundlePriority.STANDARD,
    lifetime_seconds: int = 86400,
    payload: bytes = b"data",
    source: str = "dtn://node-a/svc",
    dest: str = "dtn://node-b/svc",
) -> Bundle:
    return Bundle(
        source=EndpointID.from_string(source),
        destination=EndpointID.from_string(dest),
        priority=priority,
        payload=payload,
        lifetime_seconds=lifetime_seconds,
    )


def _make_node(node_id: str) -> DTNNode:
    return DTNNode(
        node_id=node_id,
        node_type=NodeType.GROUND_STATION,
        tier=1,
        capabilities=NodeCapabilities(
            max_buffer_gb=1024.0,
            supported_bands=["X-band"],
            optical_capable=False,
            rf_capable=True,
            qkd_capable=False,
            max_data_rate_mbps=200.0,
            processing_power_mips=10000.0,
        ),
    )


class TestBundleQueue(unittest.TestCase):
    """Test cases for BundleQueue priority queue."""

    def setUp(self) -> None:
        self.queue: BundleQueue = BundleQueue()

    def test_enqueue_dequeue(self) -> None:
        b1 = _make_bundle(payload=b"aaa")
        b2 = _make_bundle(payload=b"bbb")
        self.queue.enqueue(b1)
        self.queue.enqueue(b2)
        self.assertEqual(self.queue.peek(), b1)
        dequeued = self.queue.dequeue()
        self.assertEqual(dequeued, b1)
        self.assertEqual(self.queue.get_size(), 1)

    def test_priority_ordering(self) -> None:
        standard = _make_bundle(priority=BundlePriority.STANDARD)
        emergency = _make_bundle(priority=BundlePriority.EMERGENCY)
        self.queue.enqueue(standard)
        self.queue.enqueue(emergency)
        first = self.queue.dequeue()
        self.assertEqual(first.priority, BundlePriority.EMERGENCY)

    def test_remove_expired(self) -> None:
        expired = _make_bundle(lifetime_seconds=-1)
        self.queue.enqueue(expired)
        time.sleep(0.01)
        removed = self.queue.remove_expired()
        self.assertEqual(removed, 1)

    def test_get_size(self) -> None:
        for i in range(3):
            self.queue.enqueue(_make_bundle(payload=bytes([i])))
        self.assertEqual(self.queue.get_size(), 3)


class TestForwardingEngine(unittest.TestCase):
    """Test cases for ForwardingEngine store-and-forward logic."""

    def setUp(self) -> None:
        self.local_node = _make_node("node-a")
        self.agent = RLRoutingAgent(node_id="node-a", epsilon=0.0)
        self.engine = ForwardingEngine(
            local_node=self.local_node,
            routing_agent=self.agent,
        )

    def test_receive_bundle(self) -> None:
        bundle = _make_bundle(dest="dtn://node-c/svc")
        event = self.engine.receive_bundle(bundle, from_node="node-b")
        self.assertEqual(event.event_type, "received")

    def test_deliver_to_self(self) -> None:
        bundle = _make_bundle(dest="dtn://node-a/svc")
        event = self.engine.receive_bundle(bundle, from_node="node-b")
        self.assertEqual(event.event_type, "delivered")

    def test_forward_to_neighbor(self) -> None:
        bundle = _make_bundle(
            source="dtn://node-a/svc",
            dest="dtn://node-b/svc",
        )
        self.engine.receive_bundle(bundle, from_node="node-c")
        neighbor_node = _make_node("node-b")
        neighbors = {"node-b": neighbor_node}
        events = self.engine.tick(time.time(), neighbors)
        forwarded = [e for e in events if e.event_type == "forwarded"]
        self.assertGreater(len(forwarded), 0)

    def test_queue_stats(self) -> None:
        self.engine.queue.enqueue(_make_bundle(priority=BundlePriority.EMERGENCY))
        self.engine.queue.enqueue(_make_bundle(priority=BundlePriority.STANDARD))
        self.engine.queue.enqueue(_make_bundle(priority=BundlePriority.BULK))
        stats = self.engine.get_queue_stats()
        self.assertEqual(stats["queue_size"], 3)
        self.assertEqual(stats["emergency_count"], 1)
        self.assertEqual(stats["standard_count"], 1)
        self.assertEqual(stats["bulk_count"], 1)


class TestLTPSessionEngine(unittest.TestCase):
    """Test cases for LTP convergence-layer session engine."""

    def setUp(self) -> None:
        self.engine: LTPSessionEngine = LTPSessionEngine(
            node_id="test-node", mtu_bytes=300,
        )

    def test_segment_bundle(self) -> None:
        bundle = _make_bundle(payload=b"X" * 1000)
        segments = self.engine.segment_bundle(bundle)
        self.assertEqual(len(segments), 4)

    def test_reconstruct_bundle(self) -> None:
        original = _make_bundle(payload=b"AB" * 500)
        segments = self.engine.segment_bundle(original)
        reconstructed = self.engine.reconstruct_bundle(segments)
        self.assertEqual(reconstructed.payload, original.payload)

    def test_create_session(self) -> None:
        session = self.engine.create_session(
            source="a", destination="b", total_bytes=5000, red_bytes=5000,
        )
        retrieved = self.engine.get_session(session.session_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.source, "a")

    def test_process_report_with_gaps(self) -> None:
        session = self.engine.create_session(
            source="a", destination="b", total_bytes=1000, red_bytes=1000,
        )
        session.segments_sent = 4
        report = LTPReport(
            session_id=session.session_id,
            report_serial=1,
            checkpoint_serial=0,
            reception_claims=[(0, 300), (600, 300)],
        )
        retransmit = self.engine.process_report(report)
        self.assertGreater(len(retransmit), 0)


class TestTCPConvergenceLayer(unittest.TestCase):
    """Test cases for TCP convergence layer."""

    def setUp(self) -> None:
        self.tcpcl: TCPConvergenceLayer = TCPConvergenceLayer(node_id="node-a")

    def test_register_endpoint(self) -> None:
        self.tcpcl.register_endpoint("node-b", "192.168.1.10", 4556)
        ep = self.tcpcl.get_endpoint("node-b")
        self.assertIsNotNone(ep)
        self.assertEqual(ep.host, "192.168.1.10")
        self.assertEqual(ep.port, 4556)

    def test_connect_disconnect(self) -> None:
        self.tcpcl.register_endpoint("node-b", "10.0.0.1", 4556)
        self.assertTrue(self.tcpcl.connect("node-b"))
        ep = self.tcpcl.get_endpoint("node-b")
        self.assertTrue(ep.is_connected)
        self.tcpcl.disconnect("node-b")
        self.assertFalse(ep.is_connected)

    def test_send_bundle(self) -> None:
        self.tcpcl.register_endpoint("node-b", "10.0.0.1", 4556)
        self.tcpcl.connect("node-b")
        bundle = _make_bundle(payload=b"hello tcp")
        session = self.tcpcl.send_bundle("node-b", bundle)
        self.assertTrue(session.is_complete)
        self.assertEqual(session.total_bytes, bundle.payload_size_bytes)


class TestUDPConvergenceLayer(unittest.TestCase):
    """Test cases for UDP convergence layer."""

    def setUp(self) -> None:
        self.udpcl: UDPConvergenceLayer = UDPConvergenceLayer(
            node_id="node-a", mtu_bytes=400,
        )

    def test_fragment_bundle(self) -> None:
        bundle = _make_bundle(payload=b"Y" * 1000)
        datagrams = self.udpcl.fragment_bundle(bundle)
        self.assertGreater(len(datagrams), 1)
        for dg in datagrams:
            self.assertTrue(dg.is_fragment)

    def test_reconstruct_bundle(self) -> None:
        bundle = _make_bundle(payload=b"Z" * 1000)
        datagrams = self.udpcl.fragment_bundle(bundle)
        reconstructed = self.udpcl.reconstruct_bundle(datagrams)
        self.assertIsNotNone(reconstructed)
        self.assertEqual(reconstructed.payload, bundle.payload)

    def test_send_with_loss(self) -> None:
        lossy = UDPConvergenceLayer(node_id="node-a", loss_rate=1.0)
        dg = self.udpcl.fragment_bundle(_make_bundle(payload=b"A" * 100))[0]
        self.assertFalse(lossy.send_datagram(dg))


if __name__ == '__main__':
    unittest.main()
