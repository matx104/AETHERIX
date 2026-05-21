"""
AETHERIX QKD Post-Processing: Privacy Amplification & Information Reconciliation

After raw key sifting in BB84/E91, Alice and Bob must:
    1.  Correct errors (information reconciliation / CASCADE)
    2.  Estimate Eve's information from QBER
    3.  Shorten the key (privacy amplification) to eliminate leakage

References:
    - Brassard, Salvail (1994) — CASCADE error reconciliation
    - Bennett, Brassard, Crépeau, Maurer (1995) — privacy amplification
    - Csiszár, Körner (1978) — secrecy capacity bound
"""

import math
from typing import List, Tuple


def universal_hash(data: bytes, key: bytes) -> bytes:
    """
    Simple universal hash for privacy amplification.

    XORs *data* with *key* (truncated to the shorter of the two).

    Args:
        data: raw key material
        key:  random hash key

    Returns:
        Hash result as bytes.
    """
    length = min(len(data), len(key))
    return bytes(d ^ key[i] for i, d in enumerate(data[:length]))


def information_reconciliation(
    alice_key: List[int],
    bob_key: List[int],
    error_rate: float,
) -> Tuple[List[int], List[int], int]:
    """
    CASCADE-style error correction.

    1.  Split keys into blocks of size ``max(1, int(1/error_rate))``.
    2.  For each block, compare parities.
    3.  When parities differ, binary-search for the error bit and flip it
        in Bob's key.
    4.  Repeat once more (second CASCADE pass) to catch residual errors.

    Args:
        alice_key:   Alice's sifted key
        bob_key:     Bob's sifted key
        error_rate:  estimated QBER

    Returns:
        ``(corrected_alice, corrected_bob, errors_corrected)``
    """
    alice = list(alice_key)
    bob = list(bob_key)
    errors_corrected = 0

    if not alice or not bob:
        return (alice, bob, errors_corrected)

    block_size = max(1, int(1 / error_rate)) if error_rate > 0 else len(alice)
    n = min(len(alice), len(bob))

    def _parity(bits: List[int], start: int, end: int) -> int:
        return sum(bits[start:end]) % 2

    for _pass in range(2):
        for block_start in range(0, n, block_size):
            block_end = min(block_start + block_size, n)

            if _parity(alice, block_start, block_end) == _parity(
                bob, block_start, block_end
            ):
                continue

            lo, hi = block_start, block_end - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if _parity(alice, lo, mid + 1) != _parity(bob, lo, mid + 1):
                    hi = mid
                else:
                    lo = mid + 1

            bob[lo] = 1 - bob[lo]
            errors_corrected += 1

    return (alice, bob, errors_corrected)


def privacy_amplification(key: List[int], security_parameter: int) -> List[int]:
    """
    Shorten the key to eliminate partial eavesdropper knowledge.

    Consecutive pairs of bits are XOR-ed together.  The resulting key is
    ``⌊len(key)/2⌋`` bits long.

    Args:
        key:                reconciled key
        security_parameter: number of bits to drop (drives number of
                            XOR-compression rounds)

    Returns:
        Shortened (amplified) key.
    """
    result = list(key)

    for _ in range(security_parameter):
        if len(result) < 2:
            break
        compressed: List[int] = []
        for i in range(0, len(result) - 1, 2):
            compressed.append(result[i] ^ result[i + 1])
        result = compressed

    return result


def binary_entropy(p: float) -> float:
    """
    Binary entropy function  h(p) = −p log₂ p − (1−p) log₂(1−p).

    Returns 0 for *p* = 0 or *p* = 1.
    """
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


def estimate_eve_information(qber: float, key_length: int) -> float:
    """
    Estimate bits known to Eve using the Csiszár-Körner bound.

    I_Eve ≈ key_length × h(QBER)

    where *h* is binary entropy.
    """
    return key_length * binary_entropy(qber)


def post_process_qkd_result(
    alice_key: List[int],
    bob_key: List[int],
    qber: float,
) -> Tuple[List[int], bool]:
    """
    Full QKD post-processing pipeline.

    1.  Information reconciliation (CASCADE)
    2.  Estimate Eve's information from QBER
    3.  Privacy amplification with security parameter
        ``⌈estimated_eve_info × 2⌉``

    Returns ``(final_key, is_secure)`` where *is_secure* is ``True``
    when the final key is at least 128 bits long.
    """
    corrected_alice, corrected_bob, _ = information_reconciliation(
        alice_key, bob_key, qber
    )

    eve_bits = estimate_eve_information(qber, len(corrected_alice))
    security_param = math.ceil(eve_bits * 2)

    final_key = privacy_amplification(corrected_alice, security_param)
    is_secure = len(final_key) >= 128

    return (final_key, is_secure)
