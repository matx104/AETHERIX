"""
Tests for LTP Convergence Layer (RFC 5326).

Validates LTP segmentation, reassembly, session tracking, report
generation, gap detection, retransmission, and timeout detection.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.bundle import Bundle
from routing.ltp import (
    LTPOpcode,
    LTPSegment,
    LTPSegmentKind,
    LTPSession,
    LTPSessionEngine,
    LTPReport,
)


def _make_bundle(payload_size: int = 5000) -> Bundle:
    return Bundle(payload=b"X" * payload_size, payload_size_bytes=payload_size)


class TestLTPOpcodes(unittest.TestCase):

    def test_data_opcode(self):
        seg = LTPSegment(session_id="s1", kind=LTPSegmentKind.RED, payload=b"data")
        self.assertEqual(seg.opcode, LTPOpcode.DATA)

    def test_checkpoint_opcode(self):
        seg = LTPSegment(
            session_id="s1", kind=LTPSegmentKind.RED, payload=b"data",
            is_checkpoint=True,
        )
        self.assertEqual(seg.opcode, LTPOpcode.CHECKPOINT)

    def test_all_opcodes_exist(self):
        self.assertEqual(len(LTPOpcode), 7)

    def test_segment_kinds(self):
        self.assertEqual(len(LTPSegmentKind), 2)


class TestLTPSegment(unittest.TestCase):

    def setUp(self):
        self.seg = LTPSegment(
            session_id="session-abc123def456",
            kind=LTPSegmentKind.RED,
            payload=b"hello world",
            offset=0,
            is_checkpoint=True,
            is_eors=False,
        )

    def test_length(self):
        self.assertEqual(self.seg.length, 11)

    def test_opcode_for_checkpoint(self):
        self.assertEqual(self.seg.opcode, LTPOpcode.CHECKPOINT)

    def test_opcode_for_data(self):
        seg = LTPSegment(session_id="s", kind=LTPSegmentKind.GREEN, payload=b"x")
        self.assertEqual(seg.opcode, LTPOpcode.DATA)

    def test_to_dict(self):
        d = self.seg.to_dict()
        self.assertEqual(d["session_id"], "session-abc123def456")
        self.assertEqual(d["kind"], "RED")
        self.assertEqual(d["offset"], 0)
        self.assertTrue(d["is_checkpoint"])

    def test_str(self):
        s = str(self.seg)
        self.assertIn("LTPSegment", s)
        self.assertIn("RED", s)
        self.assertIn("CP", s)


class TestLTPReport(unittest.TestCase):

    def setUp(self):
        self.report = LTPReport(
            session_id="s1",
            report_serial=1,
            checkpoint_serial=0,
            reception_claims=[(0, 100), (200, 50)],
        )

    def test_total_received_bytes(self):
        self.assertEqual(self.report.total_received_bytes, 150)

    def test_has_gaps_true(self):
        self.assertTrue(self.report.has_gaps(500))

    def test_has_gaps_false(self):
        self.assertFalse(self.report.has_gaps(150))

    def test_str(self):
        s = str(self.report)
        self.assertIn("LTPReport", s)
        self.assertIn("claims=2", s)


class TestLTPSession(unittest.TestCase):

    def setUp(self):
        self.session = LTPSession(
            session_id="s1",
            source="mars.areo.alpha",
            destination="earth.dsn.goldstone",
            total_bytes=10000,
            red_bytes=8000,
            green_bytes=2000,
        )

    def test_initial_progress(self):
        p = self.session.progress
        self.assertGreaterEqual(p, 0.0)
        self.assertLessEqual(p, 1.0)

    def test_progress_increases_with_acks(self):
        self.session.segments_sent = 10
        self.session.segments_acked = 5
        p1 = self.session.progress
        self.session.segments_acked = 10
        p2 = self.session.progress
        self.assertGreater(p2, p1)

    def test_zero_total_bytes_progress_is_one(self):
        s = LTPSession(session_id="x", source="a", destination="b",
                       total_bytes=0, red_bytes=0, green_bytes=0)
        self.assertEqual(s.progress, 1.0)

    def test_age_seconds_positive(self):
        self.assertGreater(self.session.age_seconds, 0)

    def test_str_active(self):
        self.assertIn("ACTIVE", str(self.session))

    def test_str_complete(self):
        self.session.complete = True
        self.assertIn("COMPLETE", str(self.session))


class TestLTPSessionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = LTPSessionEngine(node_id="test-node", mtu_bytes=1400)

    def test_segment_bundle_basic(self):
        bundle = _make_bundle(5000)
        segments = self.engine.segment_bundle(bundle)
        self.assertEqual(len(segments), 4)  # 1400 + 1400 + 1400 + 800

    def test_segment_bundle_first_is_checkpoint(self):
        bundle = _make_bundle(5000)
        segments = self.engine.segment_bundle(bundle)
        self.assertTrue(segments[0].is_checkpoint)

    def test_segment_bundle_last_is_eors(self):
        bundle = _make_bundle(5000)
        segments = self.engine.segment_bundle(bundle)
        self.assertTrue(segments[-1].is_eors)

    def test_segment_bundle_all_red(self):
        bundle = _make_bundle(5000)
        segments = self.engine.segment_bundle(bundle)
        for seg in segments:
            self.assertEqual(seg.kind, LTPSegmentKind.RED)

    def test_segment_offsets_contiguous(self):
        bundle = _make_bundle(5000)
        segments = self.engine.segment_bundle(bundle)
        offsets = [s.offset for s in segments]
        self.assertEqual(offsets, [0, 1400, 2800, 4200])

    def test_segment_empty_payload(self):
        bundle = Bundle(payload=b"", payload_size_bytes=0)
        segments = self.engine.segment_bundle(bundle)
        self.assertEqual(len(segments), 0)

    def test_segment_exact_mtu_multiple(self):
        bundle = _make_bundle(2800)
        segments = self.engine.segment_bundle(bundle)
        self.assertEqual(len(segments), 2)

    def test_reconstruct_bundle(self):
        bundle = _make_bundle(5000)
        segments = self.engine.segment_bundle(bundle)
        reconstructed = self.engine.reconstruct_bundle(segments)
        self.assertEqual(reconstructed.payload, bundle.payload)

    def test_reconstruct_out_of_order(self):
        bundle = _make_bundle(5000)
        segments = self.engine.segment_bundle(bundle)
        reversed_segs = list(reversed(segments))
        reconstructed = self.engine.reconstruct_bundle(reversed_segs)
        self.assertEqual(reconstructed.payload, bundle.payload)

    def test_reconstruct_empty_raises(self):
        with self.assertRaises(ValueError):
            self.engine.reconstruct_bundle([])

    def test_create_session(self):
        session = self.engine.create_session(
            source="a", destination="b",
            total_bytes=10000, red_bytes=8000,
        )
        self.assertEqual(session.total_bytes, 10000)
        self.assertEqual(session.red_bytes, 8000)
        self.assertEqual(session.green_bytes, 2000)
        self.assertFalse(session.complete)

    def test_mark_session_complete(self):
        session = self.engine.create_session(
            source="a", destination="b",
            total_bytes=100, red_bytes=100,
        )
        self.engine.mark_session_complete(session.session_id)
        self.assertTrue(session.complete)

    def test_mark_unknown_session_complete(self):
        self.engine.mark_session_complete("nonexistent")
        # Should not raise

    def test_get_session(self):
        session = self.engine.create_session(
            source="a", destination="b",
            total_bytes=100, red_bytes=100,
        )
        found = self.engine.get_session(session.session_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.session_id, session.session_id)

    def test_get_session_unknown(self):
        self.assertIsNone(self.engine.get_session("nonexistent"))

    def test_generate_report(self):
        session = self.engine.create_session(
            source="a", destination="b",
            total_bytes=5000, red_bytes=5000,
        )
        report = self.engine.generate_report(
            session.session_id,
            [(0, 1400), (2800, 1400)],
        )
        self.assertEqual(report.session_id, session.session_id)
        self.assertEqual(len(report.reception_claims), 2)

    def test_process_report_no_gaps(self):
        session = self.engine.create_session(
            source="a", destination="b",
            total_bytes=5000, red_bytes=5000,
        )
        report = self.engine.generate_report(
            session.session_id,
            [(0, 5000)],
        )
        retransmit = self.engine.process_report(report)
        self.assertEqual(len(retransmit), 0)

    def test_process_report_with_gaps(self):
        session = self.engine.create_session(
            source="a", destination="b",
            total_bytes=5000, red_bytes=5000,
        )
        session.segments_sent = 4
        report = self.engine.generate_report(
            session.session_id,
            [(0, 1400), (2800, 1400)],
        )
        retransmit = self.engine.process_report(report)
        self.assertGreater(len(retransmit), 0)
        self.assertGreater(session.retransmissions, 0)

    def test_process_report_unknown_session(self):
        report = LTPReport(
            session_id="nonexistent",
            report_serial=0,
            checkpoint_serial=0,
            reception_claims=[(0, 100)],
        )
        retransmit = self.engine.process_report(report)
        self.assertEqual(len(retransmit), 0)

    def test_check_timeouts(self):
        session = self.engine.create_session(
            source="a", destination="b",
            total_bytes=100, red_bytes=100,
        )
        session.created_time = time.time() - 2000  # 2000s ago
        timed_out = self.engine.check_timeouts(time.time(), timeout_seconds=1800)
        self.assertIn(session.session_id, timed_out)

    def test_check_timeouts_completed_not_timed_out(self):
        session = self.engine.create_session(
            source="a", destination="b",
            total_bytes=100, red_bytes=100,
        )
        session.created_time = time.time() - 2000
        session.complete = True
        timed_out = self.engine.check_timeouts(time.time(), timeout_seconds=1800)
        self.assertNotIn(session.session_id, timed_out)

    def test_get_stats(self):
        self.engine.create_session(
            source="a", destination="b",
            total_bytes=100, red_bytes=100,
        )
        stats = self.engine.get_stats()
        self.assertEqual(stats["sessions_created"], 1)
        self.assertEqual(stats["completed"], 0)

    def test_compute_gaps_no_claims(self):
        gaps = LTPSessionEngine._compute_gaps([], 1000)
        self.assertEqual(gaps, [(0, 1000)])

    def test_compute_gaps_full_coverage(self):
        gaps = LTPSessionEngine._compute_gaps([(0, 1000)], 1000)
        self.assertEqual(gaps, [])

    def test_compute_gaps_middle_gap(self):
        gaps = LTPSessionEngine._compute_gaps([(0, 100), (200, 100)], 300)
        self.assertEqual(gaps, [(100, 100)])

    def test_compute_gaps_trailing_gap(self):
        gaps = LTPSessionEngine._compute_gaps([(0, 100)], 300)
        self.assertEqual(gaps, [(100, 200)])


if __name__ == "__main__":
    unittest.main()
