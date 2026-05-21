"""
Tests for AETHERIX Quantum Repeater Chain and Privacy Amplification.

Validates multi-hop entanglement generation, purification,
CASCADE error reconciliation, binary entropy, and QKD post-processing.
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from security.privacy_amplification import (
    binary_entropy,
    information_reconciliation,
    post_process_qkd_result,
    privacy_amplification,
)
from security.repeater_chain import EntanglementPair, RepeaterChain, create_earth_mars_chain


class TestRepeaterChain(unittest.TestCase):
    """Test cases for RepeaterChain multi-hop quantum link."""

    def test_create_chain(self) -> None:
        chain = create_earth_mars_chain()
        self.assertEqual(chain.get_total_hops(), 3)

    def test_generate_pairs(self) -> None:
        chain = create_earth_mars_chain()
        pairs = chain.generate_entanglement_pairs()
        self.assertEqual(len(pairs), chain.get_total_hops())

    def test_purify_pair(self) -> None:
        chain = create_earth_mars_chain()
        pair = EntanglementPair(
            id="test-pair",
            node_a="Earth",
            node_b="ES-L4",
            fidelity=0.9,
        )
        result = chain.purify_pair(pair, target_fidelity=0.95)
        self.assertGreaterEqual(pair.fidelity, result.initial_fidelity)


class TestPrivacyAmplification(unittest.TestCase):
    """Test cases for privacy amplification and error reconciliation."""

    def test_binary_entropy(self) -> None:
        self.assertAlmostEqual(binary_entropy(0.5), 1.0, places=5)
        self.assertAlmostEqual(binary_entropy(0.0), 0.0, places=5)
        self.assertAlmostEqual(binary_entropy(1.0), 0.0, places=5)

    def test_information_reconciliation(self) -> None:
        alice = [0, 1, 0, 1, 1, 0, 1, 0, 0, 1]
        bob = [0, 1, 0, 1, 1, 0, 0, 0, 0, 1]
        a_out, b_out, errors = information_reconciliation(alice, bob, 0.1)
        self.assertEqual(a_out, b_out)
        self.assertGreaterEqual(errors, 1)

    def test_privacy_amplification(self) -> None:
        key = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0]
        amplified = privacy_amplification(key, security_parameter=1)
        self.assertLess(len(amplified), len(key))

    def test_post_process(self) -> None:
        alice = [0, 1] * 512
        bob = list(alice)
        final_key, secure = post_process_qkd_result(alice, bob, qber=0.0)
        self.assertTrue(secure)
        self.assertGreaterEqual(len(final_key), 128)

    def test_post_process_high_qber(self) -> None:
        alice = [0, 1] * 256
        bob = [1, 0] * 256
        final_key, secure = post_process_qkd_result(alice, bob, qber=0.5)
        self.assertFalse(secure)


if __name__ == '__main__':
    unittest.main()
