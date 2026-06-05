"""
Tests for AETHERIX Data Prioritization Module
Validates the 4-tier data classification, compression model, deadline-aware
priority scheduler (with BPv7 fragmentation), and emergency preemption.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from routing.bundle import BundlePriority
from routing.prioritization import (
    COMPRESSION_PROFILES,
    Compressor,
    DataCategory,
    EmergencyProtocol,
    QoSScheduler,
    TrafficItem,
    make_bundle,
    simulate_downlink,
)


class TestDataCategory(unittest.TestCase):

    def test_emergency_maps_to_bundle_emergency(self):
        self.assertEqual(DataCategory.EMERGENCY_SAFETY.bundle_priority,
                         BundlePriority.EMERGENCY)

    def test_ranks_are_ordered(self):
        self.assertLess(DataCategory.EMERGENCY_SAFETY.rank,
                        DataCategory.MISSION_CRITICAL.rank)
        self.assertLess(DataCategory.MISSION_CRITICAL.rank,
                        DataCategory.HIGH_PRIORITY.rank)
        self.assertLess(DataCategory.HIGH_PRIORITY.rank,
                        DataCategory.LOW_PRIORITY.rank)

    def test_only_emergency_is_preemptive(self):
        self.assertTrue(DataCategory.EMERGENCY_SAFETY.preemptive)
        self.assertFalse(DataCategory.MISSION_CRITICAL.preemptive)


class TestCompressor(unittest.TestCase):

    def test_lossless_telemetry_ratio(self):
        c = Compressor()
        r = c.compress(3_000_000, "telemetry")
        self.assertTrue(r.profile.lossless)
        self.assertAlmostEqual(r.ratio, 3.0, places=4)
        self.assertEqual(r.compressed_bytes, 1_000_000)

    def test_lossy_image_higher_ratio(self):
        c = Compressor()
        lossless = c.compress(1_000_000, "image_lossless")
        lossy = c.compress(1_000_000, "image_lossy")
        self.assertGreater(lossy.ratio, lossless.ratio)
        self.assertFalse(lossy.profile.lossless)

    def test_raw_is_no_op(self):
        c = Compressor()
        r = c.compress(500, "raw")
        self.assertEqual(r.compressed_bytes, 500)
        self.assertEqual(r.ratio, 1.0)

    def test_reduction_percent(self):
        self.assertAlmostEqual(COMPRESSION_PROFILES["telemetry"].reduction_percent,
                               100.0 * (1 - 1 / 3.0), places=4)


class TestQoSScheduler(unittest.TestCase):

    def test_priority_order_emergency_first(self):
        items = [
            TrafficItem("bulk", DataCategory.LOW_PRIORITY, 1_000_000, 100),
            TrafficItem("alert", DataCategory.EMERGENCY_SAFETY, 1_000, 100),
        ]
        sched = QoSScheduler(link_rate_bps=1e6, contact_duration_s=100)
        result = sched.schedule(items)
        # emergency item should start at t=0 (sent first)
        alert_entry = next(e for e in result.entries if e.item.name == "alert")
        self.assertEqual(alert_entry.start_s, 0.0)
        self.assertTrue(alert_entry.delivered)

    def test_oversubscribed_link_defers_low_priority(self):
        result = simulate_downlink()
        names_dropped = [e.item.name for e in result.entries if not e.delivered]
        # the bulk software archive (lowest priority) is not fully delivered
        self.assertIn("software-update-archive", names_dropped)
        # all emergency/mission/high items are fully delivered
        for e in result.entries:
            if e.item.category in (DataCategory.EMERGENCY_SAFETY,
                                   DataCategory.MISSION_CRITICAL,
                                   DataCategory.HIGH_PRIORITY):
                self.assertTrue(e.delivered, f"{e.item.name} should be delivered")

    def test_fragmentation_fills_link(self):
        result = simulate_downlink()
        # with a fragmentable bulk item, the link should be ~fully utilized
        self.assertGreaterEqual(result.utilization_percent, 99.0)
        partials = [e for e in result.entries if e.partial]
        self.assertTrue(partials, "expected a fragmented (partial) transfer")

    def test_no_fragment_item_deferred_whole(self):
        big = TrafficItem("nofrag", DataCategory.LOW_PRIORITY, 100_000_000, 999,
                          fragmentable=False)
        sched = QoSScheduler(link_rate_bps=1e6, contact_duration_s=10)
        result = sched.schedule([big])
        entry = result.entries[0]
        self.assertFalse(entry.delivered)
        self.assertEqual(entry.bytes_sent, 0)

    def test_deadline_miss_deferred(self):
        # item fits the window but cannot meet a tight deadline behind a big one
        items = [
            TrafficItem("big-high", DataCategory.HIGH_PRIORITY, 9_000_000, 100),
            TrafficItem("late-low", DataCategory.LOW_PRIORITY, 1_000_000, 5,
                        fragmentable=False),
        ]
        sched = QoSScheduler(link_rate_bps=1e6, contact_duration_s=100)
        result = sched.schedule(items)
        late = next(e for e in result.entries if e.item.name == "late-low")
        self.assertFalse(late.delivered)
        self.assertIn("deadline", late.reason)


class TestEmergencyProtocol(unittest.TestCase):

    def test_preempts_lower_priority(self):
        proto = EmergencyProtocol()
        in_progress = TrafficItem("img", DataCategory.HIGH_PRIORITY, 10_000_000, 900)
        emergency = TrafficItem("alert", DataCategory.EMERGENCY_SAFETY, 1_000, 5)
        action = proto.preempt(in_progress, emergency)
        self.assertTrue(action["preempted"])
        self.assertTrue(action["emergency_sent"])

    def test_does_not_preempt_equal_or_higher(self):
        proto = EmergencyProtocol()
        in_progress = TrafficItem("alert1", DataCategory.EMERGENCY_SAFETY, 1_000, 5)
        emergency = TrafficItem("alert2", DataCategory.EMERGENCY_SAFETY, 1_000, 5)
        action = proto.preempt(in_progress, emergency)
        self.assertFalse(action["preempted"])


class TestBundleBridge(unittest.TestCase):

    def test_make_bundle_maps_priority(self):
        item = TrafficItem("t", DataCategory.MISSION_CRITICAL, 1000, 60)
        bundle = make_bundle(item, "mars.rover", "earth.moc")
        self.assertEqual(bundle.priority, BundlePriority.HIGH_SCIENCE)
        self.assertEqual(bundle.payload_size_bytes, 1000)


if __name__ == "__main__":
    unittest.main()
