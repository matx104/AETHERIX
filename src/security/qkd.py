"""
AETHERIX Quantum Key Distribution Module
Implementation of BB84 and E91 QKD protocols for simulation.

Reference:
- Bennett & Brassard (1984) - BB84 Protocol
- Ekert (1991) - E91 Protocol
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum


class Basis(Enum):
    """Measurement basis for QKD."""
    RECTILINEAR = "R"  # |0⟩, |1⟩ (Z basis)
    DIAGONAL = "D"     # |+⟩, |-⟩ (X basis)


@dataclass
class Qubit:
    """Representation of a qubit state."""
    bit: int           # 0 or 1
    basis: Basis       # Preparation basis
    state: str = ""    # Visual representation

    def __post_init__(self):
        if self.basis == Basis.RECTILINEAR:
            self.state = "|0⟩" if self.bit == 0 else "|1⟩"
        else:
            self.state = "|+⟩" if self.bit == 0 else "|-⟩"


@dataclass
class QKDResult:
    """Result of a QKD protocol execution."""
    alice_key: List[int]
    bob_key: List[int]
    sifted_key_length: int
    qber: float  # Quantum Bit Error Rate
    secure: bool
    raw_key_length: int
    efficiency: float


class BB84Protocol:
    """
    BB84 Quantum Key Distribution Protocol.

    The BB84 protocol (Bennett-Brassard 1984) is the first and most
    widely used QKD protocol. It uses two conjugate bases to encode
    random bits as quantum states.

    Security Properties:
    - Information-theoretically secure
    - Eavesdropping detection via QBER
    - No-cloning theorem prevents copying

    Typical Parameters:
    - Earth-LEO: 1-10 kbps key rate
    - Earth-GEO: 100-1000 bps key rate
    - Security threshold: QBER < 11%
    """

    SECURITY_THRESHOLD = 0.11  # 11% QBER threshold

    def __init__(self, num_qubits: int = 1000, channel_error: float = 0.0):
        """
        Initialize BB84 protocol.

        Args:
            num_qubits: Number of qubits to exchange
            channel_error: Simulated channel error rate (0-1)
        """
        self.num_qubits = num_qubits
        self.channel_error = channel_error

    def _generate_random_bits(self, n: int) -> List[int]:
        """Generate n random classical bits."""
        return [random.randint(0, 1) for _ in range(n)]

    def _generate_random_bases(self, n: int) -> List[Basis]:
        """Generate n random measurement bases."""
        return [random.choice([Basis.RECTILINEAR, Basis.DIAGONAL]) for _ in range(n)]

    def _prepare_qubits(self, bits: List[int], bases: List[Basis]) -> List[Qubit]:
        """Prepare qubits in given states."""
        return [Qubit(bit=b, basis=basis) for b, basis in zip(bits, bases)]

    def _measure_qubit(self, qubit: Qubit, basis: Basis) -> int:
        """
        Measure a qubit in a given basis.

        If measurement basis matches preparation basis:
            - Deterministic result (correct bit value)
        If measurement basis differs:
            - Random result (50% probability each)
        """
        if basis == qubit.basis:
            # Correct basis - deterministic measurement
            result = qubit.bit
            # Add channel error
            if random.random() < self.channel_error:
                result = 1 - result
        else:
            # Wrong basis - random measurement
            result = random.randint(0, 1)

        return result

    def execute(self) -> QKDResult:
        """
        Execute the BB84 protocol.

        Protocol Steps:
        1. Alice generates random bits and bases
        2. Alice prepares qubits and sends to Bob
        3. Bob generates random measurement bases
        4. Bob measures each qubit
        5. Alice and Bob publicly compare bases
        6. Keep bits where bases matched (sifted key)
        7. Sample to estimate QBER
        8. If QBER < 11%, key is secure

        Returns:
            QKDResult with keys and security assessment
        """
        # Step 1: Alice generates random bits and bases
        alice_bits = self._generate_random_bits(self.num_qubits)
        alice_bases = self._generate_random_bases(self.num_qubits)

        # Step 2: Alice prepares qubits
        qubits = self._prepare_qubits(alice_bits, alice_bases)

        # Step 3: Bob generates random measurement bases
        bob_bases = self._generate_random_bases(self.num_qubits)

        # Step 4: Bob measures qubits
        bob_measurements = [
            self._measure_qubit(q, bob_basis)
            for q, bob_basis in zip(qubits, bob_bases)
        ]

        # Step 5 & 6: Basis reconciliation and key sifting
        alice_key = []
        bob_key = []

        for i in range(self.num_qubits):
            if alice_bases[i] == bob_bases[i]:
                alice_key.append(alice_bits[i])
                bob_key.append(bob_measurements[i])

        sifted_length = len(alice_key)

        # Step 7: Estimate QBER
        if sifted_length > 0:
            errors = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
            qber = errors / sifted_length
        else:
            qber = 1.0

        # Step 8: Security assessment
        secure = qber < self.SECURITY_THRESHOLD

        efficiency = sifted_length / self.num_qubits if self.num_qubits > 0 else 0

        return QKDResult(
            alice_key=alice_key,
            bob_key=bob_key,
            sifted_key_length=sifted_length,
            qber=qber,
            secure=secure,
            raw_key_length=self.num_qubits,
            efficiency=efficiency
        )


class E91Protocol:
    """
    E91 Entanglement-Based QKD Protocol.

    The E91 protocol (Ekert 1991) uses entangled photon pairs.
    Security is guaranteed by violation of Bell's inequality.

    Key Properties:
    - Uses maximally entangled Bell pairs
    - Security from Bell inequality violation
    - Device-independent security possible
    - Required for Earth-Mars QKD (with quantum repeaters)

    AETHERIX Application:
    - Phase 3: Earth-Mars QKD via Lagrange point repeaters
    - Entanglement swapping extends range
    """

    BELL_VIOLATION_THRESHOLD = 2.0  # Classical limit
    BELL_QUANTUM_MAX = 2.828        # Tsirelson bound (2√2)

    def __init__(self, num_pairs: int = 1000, channel_error: float = 0.0):
        """
        Initialize E91 protocol.

        Args:
            num_pairs: Number of entangled pairs to distribute
            channel_error: Simulated channel error rate
        """
        self.num_pairs = num_pairs
        self.channel_error = channel_error

    def _generate_entangled_pair(self) -> Tuple[int, int]:
        """
        Generate a maximally entangled Bell pair.

        |Φ+⟩ = (|00⟩ + |11⟩)/√2

        Measurements in same basis always give correlated results.
        """
        # Bell state: perfect correlation when measured in same basis
        bit = random.randint(0, 1)
        return (bit, bit)  # Perfectly correlated

    def _measure_with_angle(self, bit: int, angle_deg: float) -> int:
        """
        Measure qubit at specified angle.

        For Bell test, use angles:
        - Alice: 0°, 45°, 90°
        - Bob: 22.5°, 67.5°, 112.5°
        """
        # Simplified: measurement outcome depends on bit and angle
        # In reality, this involves quantum mechanics of spin measurements
        if random.random() < self.channel_error:
            return 1 - bit
        return bit

    def execute(self) -> QKDResult:
        """
        Execute the E91 protocol.

        Protocol Steps:
        1. Source generates entangled pairs
        2. One photon sent to Alice, one to Bob
        3. Each randomly chooses measurement basis
        4. Compare bases publicly
        5. Matching bases → sifted key
        6. Non-matching bases → Bell test
        7. Bell violation → no eavesdropper

        Returns:
            QKDResult with keys and security assessment
        """
        alice_bits = []
        bob_bits = []
        alice_bases = []
        bob_bases = []

        for _ in range(self.num_pairs):
            # Generate entangled pair
            a_bit, b_bit = self._generate_entangled_pair()

            # Random basis choice
            a_basis = random.choice([Basis.RECTILINEAR, Basis.DIAGONAL])
            b_basis = random.choice([Basis.RECTILINEAR, Basis.DIAGONAL])

            # Apply channel error
            if random.random() < self.channel_error:
                b_bit = 1 - b_bit

            alice_bits.append(a_bit)
            bob_bits.append(b_bit)
            alice_bases.append(a_basis)
            bob_bases.append(b_basis)

        # Sift key (matching bases)
        alice_key = []
        bob_key = []

        for i in range(self.num_pairs):
            if alice_bases[i] == bob_bases[i]:
                alice_key.append(alice_bits[i])
                bob_key.append(bob_bits[i])

        sifted_length = len(alice_key)

        # Calculate QBER
        if sifted_length > 0:
            errors = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
            qber = errors / sifted_length
        else:
            qber = 1.0

        # Bell test would be done here on non-matching basis measurements
        # Simplified: secure if QBER is low
        secure = qber < 0.11

        efficiency = sifted_length / self.num_pairs if self.num_pairs > 0 else 0

        return QKDResult(
            alice_key=alice_key,
            bob_key=bob_key,
            sifted_key_length=sifted_length,
            qber=qber,
            secure=secure,
            raw_key_length=self.num_pairs,
            efficiency=efficiency
        )


@dataclass
class QuantumRepeater:
    """
    Quantum Repeater for extending QKD range.

    Quantum repeaters use entanglement swapping to extend
    QKD range beyond direct transmission limits.

    AETHERIX deploys repeaters at Lagrange points (ES-L4, ES-L5)
    to enable Earth-Mars quantum communication.
    """
    location: str
    input_link_a: str
    input_link_b: str
    success_rate: float = 0.5  # Entanglement swapping success rate

    def swap_entanglement(self) -> bool:
        """
        Perform entanglement swapping.

        If A-R and R-B are entangled, Bell measurement at R
        creates A-B entanglement.

        Returns:
            True if swapping succeeded
        """
        return random.random() < self.success_rate


def calculate_key_rate(distance_km: float, protocol: str = "BB84") -> float:
    """
    Estimate QKD key rate based on distance.

    Key rate decreases exponentially with distance due to:
    - Photon loss in fiber/free-space
    - Detector dark counts
    - Protocol overhead

    Args:
        distance_km: Link distance in kilometers
        protocol: "BB84" or "E91"

    Returns:
        Estimated key rate in bits per second
    """
    # Simplified model: exponential decay
    # LEO baseline: 10 kbps at 500 km
    base_rate = 10000  # bps
    base_distance = 500  # km
    attenuation_factor = 0.0001  # per km

    if distance_km < 1000:
        # Near-Earth: relatively high rates
        rate = base_rate * math.exp(-attenuation_factor * distance_km)
    elif distance_km < 40000:
        # GEO range: lower rates
        rate = base_rate * math.exp(-attenuation_factor * distance_km) / 10
    else:
        # Deep space: very low rates, needs repeaters
        rate = base_rate * math.exp(-attenuation_factor * 40000) / 100

    return max(1, rate)  # Minimum 1 bps


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("AETHERIX QKD Simulation")
    print("=" * 60)

    # BB84 without eavesdropper
    print("\nScenario 1: BB84 - Secure Channel")
    bb84 = BB84Protocol(num_qubits=1000, channel_error=0.0)
    result = bb84.execute()

    print(f"  Raw qubits: {result.raw_key_length}")
    print(f"  Sifted key: {result.sifted_key_length} bits")
    print(f"  Efficiency: {result.efficiency:.1%}")
    print(f"  QBER: {result.qber:.2%}")
    print(f"  Secure: {result.secure}")

    # BB84 with eavesdropper (simulated by channel error)
    print("\nScenario 2: BB84 - Eavesdropper Present")
    bb84_eve = BB84Protocol(num_qubits=1000, channel_error=0.25)
    result_eve = bb84_eve.execute()

    print(f"  QBER: {result_eve.qber:.2%}")
    print(f"  Threshold: 11%")
    print(f"  Secure: {result_eve.secure}")
    print(f"  Status: {'ABORT - Eavesdropper detected!' if not result_eve.secure else 'Secure'}")

    # Key rate estimates
    print("\nKey Rate Estimates:")
    for dist, name in [(500, "LEO"), (36000, "GEO"), (400000000, "Mars")]:
        rate = calculate_key_rate(dist)
        print(f"  {name} ({dist/1000:.0f}k km): {rate:.1f} bps")
