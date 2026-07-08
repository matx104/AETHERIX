"""
Tests for TCP Convergence Layer (RFC 7242).

Validates TCPCL endpoint registration, connection management,
bundle transfer sessions, and throughput statistics.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.bundle import Bundle
from routing.tcpcl import (
    TCPCLMessage,
    TCPCLSession,
    TCPConvergenceLayer,
    TCPCLEndpoint,
)


def _make_bundle(size: int = 1024) -> Bundle:
    return Bundle(payload=b"X" * size, payload_size_bytes=size)


class TestTCPCLMessage(unittest.TestCase):

    def test_create_message(self):
        msg = TCPCLMessage(
            message_type="DATA_SEGMENT",
            session_id="abc123",
            payload=b"hello",
        )
        self.assertEqual(msg.message_type, "DATA_SEGMENT")
        self.assertEqual(msg.session_id, "abc123")
        self.assertEqual(msg.flags, 0)

    def test_message_with_flags(self):
        msg = TCPCLMessage(
            message_type="ACK",
            session_id="s1",
            payload=b"",
            flags=1,
        )
        self.assertEqual(msg.flags, 1)


class TestTCPCLEndpoint(unittest.TestCase):

    def test_defaults(self):
        ep = TCPCLEndpoint(endpoint_id="earth.dsn", host="10.0.0.1", port=4556)
        self.assertFalse(ep.is_connected)
        self.assertEqual(ep.bytes_sent, 0)
        self.assertEqual(ep.bytes_received, 0)
        self.assertEqual(ep.sessions_active, 0)


class TestTCPConvergenceLayer(unittest.TestCase):

    def setUp(self):
        self.cl = TCPConvergenceLayer(node_id="test-node")

    def test_register_endpoint(self):
        self.cl.register_endpoint("earth.dsn", "10.0.0.1", 4556)
        ep = self.cl.get_endpoint("earth.dsn")
        self.assertIsNotNone(ep)
        self.assertEqual(ep.host, "10.0.0.1")
        self.assertEqual(ep.port, 4556)

    def test_connect_known_endpoint(self):
        self.cl.register_endpoint("earth.dsn", "10.0.0.1", 4556)
        result = self.cl.connect("earth.dsn")
        self.assertTrue(result)
        ep = self.cl.get_endpoint("earth.dsn")
        self.assertTrue(ep.is_connected)

    def test_connect_unknown_endpoint(self):
        result = self.cl.connect("nonexistent")
        self.assertFalse(result)

    def test_disconnect(self):
        self.cl.register_endpoint("earth.dsn", "10.0.0.1", 4556)
        self.cl.connect("earth.dsn")
        self.cl.disconnect("earth.dsn")
        ep = self.cl.get_endpoint("earth.dsn")
        self.assertFalse(ep.is_connected)

    def test_disconnect_unknown(self):
        self.cl.disconnect("nonexistent")  # should not raise

    def test_send_bundle(self):
        self.cl.register_endpoint("earth.dsn", "10.0.0.1", 4556)
        bundle = _make_bundle(2048)
        session = self.cl.send_bundle("earth.dsn", bundle)
        self.assertTrue(session.is_complete)
        self.assertEqual(session.total_bytes, 2048)
        self.assertEqual(session.bytes_transferred, 2048)

    def test_send_bundle_unknown_endpoint(self):
        bundle = _make_bundle()
        with self.assertRaises(ValueError):
            self.cl.send_bundle("nonexistent", bundle)

    def test_send_bundle_updates_stats(self):
        self.cl.register_endpoint("earth.dsn", "10.0.0.1", 4556)
        bundle = _make_bundle(2048)
        self.cl.send_bundle("earth.dsn", bundle)
        ep = self.cl.get_endpoint("earth.dsn")
        self.assertEqual(ep.bytes_sent, 2048)
        self.assertEqual(ep.sessions_active, 1)

    def test_receive_bundle(self):
        self.cl.register_endpoint("earth.dsn", "10.0.0.1", 4556)
        bundle = _make_bundle(2048)
        session = self.cl.send_bundle("earth.dsn", bundle)
        received = self.cl.receive_bundle(session.session_id)
        self.assertEqual(received.payload_size_bytes, 2048)

    def test_receive_bundle_unknown_session(self):
        with self.assertRaises(ValueError):
            self.cl.receive_bundle("nonexistent")

    def test_get_active_sessions_empty(self):
        self.assertEqual(self.cl.get_active_sessions(), [])

    def test_get_active_sessions_after_incomplete(self):
        session = TCPCLSession(
            session_id="s1",
            source="a",
            destination="b",
            total_bytes=1000,
        )
        self.cl._sessions["s1"] = session
        active = self.cl.get_active_sessions()
        self.assertEqual(len(active), 1)

    def test_get_stats_empty(self):
        stats = self.cl.get_stats()
        self.assertEqual(stats["total_sent"], 0)
        self.assertEqual(stats["total_received"], 0)
        self.assertEqual(stats["active_connections"], 0)

    def test_get_stats_after_transfer(self):
        self.cl.register_endpoint("earth.dsn", "10.0.0.1", 4556)
        self.cl.register_endpoint("earth.moc", "10.0.0.2", 4556)
        self.cl.connect("earth.dsn")
        self.cl.connect("earth.moc")
        self.cl.send_bundle("earth.dsn", _make_bundle(1000))
        stats = self.cl.get_stats()
        self.assertEqual(stats["total_sent"], 1000)
        self.assertEqual(stats["active_connections"], 2)

    def test_get_endpoint_unknown(self):
        self.assertIsNone(self.cl.get_endpoint("nonexistent"))


if __name__ == "__main__":
    unittest.main()
