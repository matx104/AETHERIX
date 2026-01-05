#!/usr/bin/env python3
"""
AETHERIX Quantum Key Distribution Demo
Simulates the BB84 quantum key distribution protocol.
"""

import random
from typing import List, Tuple


class BB84Simulator:
    """
    Simulates the BB84 Quantum Key Distribution protocol.

    BB84 uses two conjugate bases (rectilinear and diagonal) to encode bits.
    Security comes from the no-cloning theorem - any eavesdropper disturbs the quantum state.
    """

    # Bases and states
    RECTILINEAR = 'R'  # Basis 0: |0⟩ = 0, |1⟩ = 1
    DIAGONAL = 'D'     # Basis 1: |+⟩ = 0, |-⟩ = 1

    def __init__(self, num_qubits: int = 100, error_rate: float = 0.0):
        self.num_qubits = num_qubits
        self.error_rate = error_rate  # Simulated channel error / eavesdropper

    def generate_random_bits(self, n: int) -> List[int]:
        """Generate n random bits."""
        return [random.randint(0, 1) for _ in range(n)]

    def generate_random_bases(self, n: int) -> List[str]:
        """Generate n random bases (R or D)."""
        return [random.choice([self.RECTILINEAR, self.DIAGONAL]) for _ in range(n)]

    def encode_qubit(self, bit: int, basis: str) -> str:
        """Encode a bit in a given basis."""
        if basis == self.RECTILINEAR:
            return '|0⟩' if bit == 0 else '|1⟩'
        else:
            return '|+⟩' if bit == 0 else '|-⟩'

    def measure_qubit(self, qubit: str, basis: str, original_basis: str) -> int:
        """
        Measure a qubit in a given basis.
        If basis matches, get correct result. If not, random result.
        """
        if basis == original_basis:
            # Correct basis - deterministic result
            if qubit in ['|0⟩', '|+⟩']:
                result = 0
            else:
                result = 1
            # Add error rate (eavesdropper or channel noise)
            if random.random() < self.error_rate:
                result = 1 - result
        else:
            # Wrong basis - random result
            result = random.randint(0, 1)
        return result

    def run_protocol(self) -> Tuple[List[int], List[int], float]:
        """
        Run the BB84 protocol simulation.

        Returns:
            Tuple of (Alice's key, Bob's key, QBER)
        """
        # Step 1: Alice generates random bits and bases
        alice_bits = self.generate_random_bits(self.num_qubits)
        alice_bases = self.generate_random_bases(self.num_qubits)

        # Step 2: Alice encodes and sends qubits
        qubits = [self.encode_qubit(b, basis) for b, basis in zip(alice_bits, alice_bases)]

        # Step 3: Bob generates random measurement bases
        bob_bases = self.generate_random_bases(self.num_qubits)

        # Step 4: Bob measures qubits
        bob_results = [
            self.measure_qubit(q, bob_basis, alice_basis)
            for q, bob_basis, alice_basis in zip(qubits, bob_bases, alice_bases)
        ]

        # Step 5: Basis reconciliation (public discussion)
        # Keep only bits where bases matched
        alice_key = []
        bob_key = []
        matching_indices = []

        for i in range(self.num_qubits):
            if alice_bases[i] == bob_bases[i]:
                alice_key.append(alice_bits[i])
                bob_key.append(bob_results[i])
                matching_indices.append(i)

        # Calculate QBER (Quantum Bit Error Rate)
        errors = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
        qber = errors / len(alice_key) if alice_key else 0

        return alice_key, bob_key, qber, matching_indices, alice_bases, bob_bases


def run_demo():
    """Run the QKD demonstration."""
    print("\n" + "="*80)
    print("       AETHERIX QUANTUM KEY DISTRIBUTION DEMO")
    print("       BB84 Protocol Simulation")
    print("="*80)

    print("\n" + "-"*80)
    print("BB84 PROTOCOL OVERVIEW")
    print("-"*80)
    print("  1. Alice generates random bits and random bases")
    print("  2. Alice encodes bits as quantum states and sends to Bob")
    print("  3. Bob chooses random measurement bases")
    print("  4. Bob measures qubits (results depend on basis choice)")
    print("  5. Alice and Bob publicly compare bases (not bit values)")
    print("  6. Keep only bits where bases matched (sifted key)")
    print("  7. Check QBER - if >11%, eavesdropper detected!")
    print("-"*80)

    # Run simulation without eavesdropper
    print("\n" + "="*80)
    print("SCENARIO 1: SECURE CHANNEL (No Eavesdropper)")
    print("="*80)

    simulator = BB84Simulator(num_qubits=100, error_rate=0.0)
    alice_key, bob_key, qber, matches, alice_bases, bob_bases = simulator.run_protocol()

    print(f"\n  Initial qubits sent: 100")
    print(f"  Matching bases: {len(matches)} ({len(matches)}%)")
    print(f"  Sifted key length: {len(alice_key)} bits")
    print(f"  QBER: {qber*100:.1f}%")
    print(f"  Status: {'SECURE' if qber < 0.11 else 'EAVESDROPPER DETECTED!'}")

    # Show sample of protocol execution
    print(f"\n  Sample (first 10 qubits):")
    print(f"  {'Index':<8} {'Alice Basis':<12} {'Bob Basis':<12} {'Match?':<8} {'Alice Bit':<10} {'Bob Bit'}")
    print(f"  {'-'*8} {'-'*12} {'-'*12} {'-'*8} {'-'*10} {'-'*8}")

    for i in range(min(10, len(alice_bases))):
        alice_basis = alice_bases[i]
        bob_basis = bob_bases[i]
        match = "Yes" if alice_basis == bob_basis else "No"
        # Find if this index is in matches
        if i in matches:
            idx = matches.index(i)
            alice_bit = alice_key[idx]
            bob_bit = bob_key[idx]
            print(f"  {i:<8} {alice_basis:<12} {bob_basis:<12} {match:<8} {alice_bit:<10} {bob_bit}")
        else:
            print(f"  {i:<8} {alice_basis:<12} {bob_basis:<12} {match:<8} {'discarded':<10} {'discarded'}")

    # Show final key (first 20 bits)
    print(f"\n  Final Shared Key (first 20 bits):")
    print(f"  Alice: {''.join(str(b) for b in alice_key[:20])}")
    print(f"  Bob:   {''.join(str(b) for b in bob_key[:20])}")

    # Run simulation with eavesdropper
    print("\n" + "="*80)
    print("SCENARIO 2: EAVESDROPPER PRESENT (Eve intercepts)")
    print("="*80)

    simulator_eve = BB84Simulator(num_qubits=100, error_rate=0.25)  # Eve causes ~25% errors
    alice_key_eve, bob_key_eve, qber_eve, _, _, _ = simulator_eve.run_protocol()

    print(f"\n  Initial qubits sent: 100")
    print(f"  Sifted key length: {len(alice_key_eve)} bits")
    print(f"  QBER: {qber_eve*100:.1f}%")
    print(f"  Security Threshold: 11%")
    print(f"  Status: {'SECURE' if qber_eve < 0.11 else 'EAVESDROPPER DETECTED!'}")

    print("\n  Why Eve is detected:")
    print("  - Eve must measure qubits to read them")
    print("  - Measurement disturbs quantum state (no-cloning theorem)")
    print("  - Wrong basis measurement gives random results")
    print("  - This introduces errors detectable in QBER check")

    # AETHERIX QKD roadmap
    print("\n" + "="*80)
    print("AETHERIX QUANTUM SECURITY ROADMAP")
    print("="*80)
    print(f"\n  {'Phase':<8} {'Link':<20} {'Protocol':<12} {'Key Rate':<15} {'Status'}")
    print(f"  {'-'*8} {'-'*20} {'-'*12} {'-'*15} {'-'*15}")
    print(f"  {'1':<8} {'Earth-LEO':<20} {'BB84':<12} {'1-10 kbps':<15} {'Demonstrated'}")
    print(f"  {'2':<8} {'Earth-GEO':<20} {'BB84/E91':<12} {'100-1000 bps':<15} {'In Development'}")
    print(f"  {'3':<8} {'Earth-Mars':<20} {'E91+Repeaters':<12} {'1-10 bps':<15} {'Future'}")

    print("\n" + "-"*80)
    print("KEY SECURITY PROPERTIES")
    print("-"*80)
    print("  - Information-theoretic security (not computational)")
    print("  - Forward secrecy (past keys remain secure)")
    print("  - Eavesdropping detection built-in")
    print("  - Keys generated on demand")
    print("  - Future-proof against quantum computers")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_demo()
