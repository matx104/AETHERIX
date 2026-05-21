"""
Tests for AETHERIX QKD Module
Validates BB84 and E91 protocol simulations, quantum repeaters, and key rate estimation.
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from security.qkd import (Basis, BB84Protocol, E91Protocol, QKDResult,
                          QuantumRepeater, Qubit, calculate_key_rate)


class TestBB84Protocol(unittest.TestCase):

    def test_secure_channel_zero_error(self):
        bb84 = BB84Protocol(num_qubits=10000, channel_error=0.0)
        result = bb84.execute()
        self.assertIsInstance(result, QKDResult)
        self.assertTrue(result.secure)
        self.assertLess(result.qber, 0.05)
        self.assertEqual(result.raw_key_length, 10000)

    def test_eavesdropper_detected(self):
        bb84 = BB84Protocol(num_qubits=10000, channel_error=0.25)
        result = bb84.execute()
        self.assertFalse(result.secure)
        self.assertGreater(result.qber, 0.11)

    def test_qber_threshold_at_boundary(self):
        bb84 = BB84Protocol(num_qubits=10000, channel_error=0.10)
        result = bb84.execute()
        self.assertEqual(bb84.SECURITY_THRESHOLD, 0.11)

    def test_sifted_key_length_approximately_half(self):
        bb84 = BB84Protocol(num_qubits=10000, channel_error=0.0)
        result = bb84.execute()
        expected_range = (0.45, 0.55)
        self.assertGreater(result.efficiency, expected_range[0])
        self.assertLess(result.efficiency, expected_range[1])

    def test_alice_and_bob_keys_same_length(self):
        bb84 = BB84Protocol(num_qubits=5000, channel_error=0.0)
        result = bb84.execute()
        self.assertEqual(len(result.alice_key), len(result.bob_key))
        self.assertEqual(len(result.alice_key), result.sifted_key_length)

    def test_efficiency_calculation(self):
        bb84 = BB84Protocol(num_qubits=2000, channel_error=0.0)
        result = bb84.execute()
        expected_efficiency = result.sifted_key_length / result.raw_key_length
        self.assertAlmostEqual(result.efficiency, expected_efficiency, places=5)

    def test_zero_qubits(self):
        bb84 = BB84Protocol(num_qubits=0, channel_error=0.0)
        result = bb84.execute()
        self.assertEqual(result.sifted_key_length, 0)
        self.assertEqual(result.qber, 1.0)

    def test_small_sample(self):
        bb84 = BB84Protocol(num_qubits=10, channel_error=0.0)
        result = bb84.execute()
        self.assertGreater(result.sifted_key_length, 0)
        self.assertLessEqual(result.sifted_key_length, 10)


class TestE91Protocol(unittest.TestCase):

    def test_secure_entangled_channel(self):
        e91 = E91Protocol(num_pairs=10000, channel_error=0.0)
        result = e91.execute()
        self.assertTrue(result.secure)
        self.assertLess(result.qber, 0.05)

    def test_eavesdropper_on_entangled_channel(self):
        e91 = E91Protocol(num_pairs=10000, channel_error=0.25)
        result = e91.execute()
        self.assertFalse(result.secure)
        self.assertGreater(result.qber, 0.11)

    def test_bell_violation_constants(self):
        self.assertEqual(E91Protocol.BELL_VIOLATION_THRESHOLD, 2.0)
        self.assertAlmostEqual(E91Protocol.BELL_QUANTUM_MAX, 2 * math.sqrt(2), places=3)

    def test_sifted_key_length(self):
        e91 = E91Protocol(num_pairs=5000, channel_error=0.0)
        result = e91.execute()
        self.assertGreater(result.sifted_key_length, 0)
        self.assertLessEqual(result.sifted_key_length, 5000)

    def test_alice_bob_keys_correlated_no_error(self):
        e91 = E91Protocol(num_pairs=5000, channel_error=0.0)
        result = e91.execute()
        matches = sum(1 for a, b in zip(result.alice_key, result.bob_key) if a == b)
        correlation = matches / max(len(result.alice_key), 1)
        self.assertGreater(correlation, 0.9)


class TestQuantumRepeater(unittest.TestCase):

    def test_repeater_creation(self):
        repeater = QuantumRepeater(
            location="ES-L4",
            input_link_a="earth.leo.constellation",
            input_link_b="mars.areo.alpha",
            success_rate=0.5,
        )
        self.assertEqual(repeater.location, "ES-L4")
        self.assertEqual(repeater.success_rate, 0.5)

    def test_entanglement_swapping_probability(self):
        repeater = QuantumRepeater(location="test", input_link_a="a", input_link_b="b", success_rate=0.8)
        successes = sum(1 for _ in range(1000) if repeater.swap_entanglement())
        self.assertGreater(successes, 700)
        self.assertLess(successes, 900)

    def test_zero_success_repeater(self):
        repeater = QuantumRepeater(location="test", input_link_a="a", input_link_b="b", success_rate=0.0)
        self.assertFalse(repeater.swap_entanglement())

    def test_perfect_repeater(self):
        repeater = QuantumRepeater(location="test", input_link_a="a", input_link_b="b", success_rate=1.0)
        self.assertTrue(repeater.swap_entanglement())


class TestKeyRateCalculation(unittest.TestCase):

    def test_leo_key_rate(self):
        rate = calculate_key_rate(500)
        self.assertGreater(rate, 1000)

    def test_geo_key_rate(self):
        rate = calculate_key_rate(36000)
        self.assertGreater(rate, 0)

    def test_mars_key_rate_minimum(self):
        rate = calculate_key_rate(225_000_000)
        self.assertGreaterEqual(rate, 1.0)

    def test_key_rate_decreases_with_distance(self):
        rate_leo = calculate_key_rate(500)
        rate_geo = calculate_key_rate(36000)
        rate_mars = calculate_key_rate(225_000_000)
        self.assertGreater(rate_leo, rate_geo)
        self.assertGreater(rate_geo, rate_mars)


class TestQubit(unittest.TestCase):

    def test_rectilinear_states(self):
        q0 = Qubit(bit=0, basis=Basis.RECTILINEAR)
        self.assertEqual(q0.state, "|0⟩")
        q1 = Qubit(bit=1, basis=Basis.RECTILINEAR)
        self.assertEqual(q1.state, "|1⟩")

    def test_diagonal_states(self):
        q0 = Qubit(bit=0, basis=Basis.DIAGONAL)
        self.assertEqual(q0.state, "|+⟩")
        q1 = Qubit(bit=1, basis=Basis.DIAGONAL)
        self.assertEqual(q1.state, "|-⟩")


if __name__ == "__main__":
    unittest.main()
