# Quantum Communication Basics — Topic Summary

## BB84 Protocol (Bennett-Brassard 1984)

BB84 is the foundational prepare-and-measure QKD protocol. Steps:

1. **Preparation** — Alice generates a random bit string and a random basis sequence (rectilinear Z-basis: |0⟩/|1⟩, or diagonal X-basis: |+⟩/|−⟩). She encodes each bit as a photon polarised in the chosen basis.
2. **Transmission** — Single photons travel over the quantum channel (optical fibre or free-space).
3. **Measurement** — Bob measures each photon in a randomly chosen basis. If his basis matches Alice's (~50% of the time), he gets the correct bit. If not, the result is random (50/50).
4. **Sifting** — Over a classical authenticated channel, Alice and Bob announce which bases they used (not the bit values). They discard all bits where bases mismatched. ~50% of bits survive.
5. **Error estimation** — They publicly compare a random subset of the sifted key to compute the Quantum Bit Error Rate (QBER). If QBER < 11% (Shor-Preskill threshold), the key is secure.
6. **Error correction** — Cascade or LDPC codes reconcile any remaining bit errors.
7. **Privacy amplification** — A hash function compresses the reconciled key, eliminating any partial information an eavesdropper might have. The final key is information-theoretically secure.

In AETHERIX, BB84 is used for Earth-LEO links (<2,000 km range, key rates 1–10 kbps). The implementation is in `src/security/qkd.py` — `BB84Protocol` class.

## E91 Protocol (Ekert 1991)

E91 uses entangled photon pairs instead of prepared states:

1. **Entanglement source** generates EPR pairs: |Φ⁺⟩ = (|00⟩ + |11⟩)/√2. The source can be placed at a relay node.
2. One photon sent to Alice, one to Bob — each measures in randomly chosen bases.
3. **Bell test** — When both choose the same basis, their results are perfectly correlated. The CHSH inequality violation (S > 2) proves entanglement exists and no eavesdropper has intercepted.
4. Correlated measurements become the raw key. Any eavesdropping attempt breaks entanglement — the Bell inequality is no longer violated, and the protocol aborts.

E91 is preferred for AETHERIX's deep-space links because the entanglement source can be co-located with a quantum repeater at a Lagrange point, extending range beyond direct photon transmission limits.

## No-Cloning Theorem

The no-cloning theorem (Wootters and Zurek, 1982) states: there is no unitary operation that can produce an exact copy of an arbitrary unknown quantum state. This is a direct consequence of the linearity of quantum mechanics.

Implication for QKD: an eavesdropper (Eve) cannot intercept and copy a photon, then forward the original. Any measurement disturbs the photon's quantum state, introducing detectable errors (QBER increase). This is what makes QKD information-theoretically secure — the security proof does not depend on computational assumptions (unlike RSA, which assumes factoring is hard).

## QBER and the 11% Threshold

QBER = (number of errors in sifted key) / (sifted key length).

The Shor-Preskill proof (2000) establishes that BB84 is secure against arbitrary attacks (including coherent attacks with quantum computers) when QBER < 11%. Below this threshold, privacy amplification can distill a perfectly secret key of length `n(1 − h(QBER)) − leak_EC`, where h is the binary entropy function.

At QBER ≥ 11%, even with privacy amplification, no secret key can be extracted — the protocol must abort. In AETHERIX's simulation (`src/security/qkd.py`), the `BB84Protocol.execute()` method computes QBER and sets the `secure` flag accordingly.

## Quantum Repeaters (Entanglement Swapping)

Direct QKD is photon-loss-limited to ~100–500 km (fibre) or ~2,000 km (free-space with telescopes). For Earth-Mars (54–401 million km), quantum repeaters are essential.

Entanglement swapping procedure:
1. Generate entanglement between A–R1 and R1–R2 (short-range links).
2. Perform a Bell-state measurement (BSM) at R1 on the two qubits it holds.
3. The measurement collapses A and R2 into an entangled state, even though they never interacted.
4. Classical communication of the BSM result allows A and R2 to know which entangled state they share.
5. Repeat the chain: A → R1 → R2 → R3 → B extends entanglement across the full distance.

AETHERIX places quantum repeaters at Lagrange points ES-L4 and ES-L5 (60° ahead/behind Earth in its orbit). These are co-located with the relay satellites, reducing dedicated infrastructure. The `QuantumRepeater` class in `src/security/qkd.py` models entanglement fidelity decay with distance.

## Post-Quantum Cryptography (PQC)

QKD provides information-theoretic key exchange, but it has practical limitations: requires dedicated hardware, limited range, low key rates. PQC provides algorithmic security against quantum computers using classical hardware:

| Algorithm | Type | NIST Status | Use in AETHERIX |
|-----------|------|-------------|-----------------|
| **ML-KEM / Kyber** (FIPS 203) | Key encapsulation | Standardised Aug 2024 | Key exchange fallback when QKD unavailable |
| **ML-DSA / Dilithium** (FIPS 204) | Digital signatures | Standardised Aug 2024 | Bundle authentication, custody verification |
| **SLH-DSA / SPHINCS+** (FIPS 205) | Hash-based signatures | Standardised Aug 2024 | Backup signature scheme (no lattice assumption) |

AETHERIX uses a layered approach:
- **Primary**: QKD (BB84 for near-Earth, E91 + repeaters for deep space) for key material.
- **Fallback**: ML-KEM for key exchange when quantum channel is degraded.
- **Always-on**: ML-DSA for bundle authentication — every bundle carries a post-quantum digital signature verifying source and integrity.

This hybrid ensures security even if: (a) quantum channel is unavailable (weather, pointing error), or (b) a breakthrough makes lattice problems tractable (SLH-DSA backup relies on hash security only).

---

## Practice Questions

### Q1. "Why is QKD called 'information-theoretically secure'? Doesn't every system have some vulnerability?"

Information-theoretic security means the proof does not depend on any assumption about the adversary's computational power. The BB84 security proof (Shor-Preskill, 2000) shows that the secret key rate is positive for any attack permitted by quantum mechanics when QBER < 11%. An adversary with unlimited computing power — even a quantum computer — cannot distinguish the key from random. The only vulnerabilities are implementation-side: photon source imperfections, detector blinding attacks, side channels. These are engineering problems, not theoretical weaknesses, and are actively studied in the QKD implementation community.

### Q2. "Walk me through what happens when an eavesdropper tries to intercept a BB84 key exchange."

Eve intercepts photons in transit and measures each in a random basis. Due to the no-cloning theorem, she cannot copy the photon — she must measure and resend. In ~50% of cases, she picks the wrong basis, disturbing the photon's state. When Bob later measures, these disturbed photons produce errors in his result. During the sifting and QBER estimation phase, Alice and Bob detect an elevated error rate. If QBER exceeds 11%, they abort and retry over a different channel. Even if QBER is below 11%, privacy amplification compresses the key by an amount proportional to Eve's potential information, rendering her partial knowledge useless.

### Q3. "How do quantum repeaters actually work, and how many would you need for Earth-Mars?"

Each quantum repeater performs entanglement swapping: it receives one half of an entangled pair from each direction, performs a Bell-state measurement, and announces the result classically. This creates end-to-end entanglement across multiple hops. For Earth-Mars at maximum distance (401M km), with each repeater segment at ~50,000 km (realistic for free-space quantum links with telescope apertures), you would need ~8,000 repeaters — completely impractical. AETHERIX's approach is more modest: quantum repeaters are placed only at Lagrange points (ES-L4, ES-L5 at ~150M km from Earth), extending the range to a few hops. The key rates are very low (1–10 bps Earth-Mars) but sufficient for periodic key refresh. Full continuous QKD to Mars remains a long-term research goal.

### Q4. "Why use both QKD and post-quantum cryptography? Isn't one enough?"

They address different threat models. QKD provides forward secrecy guaranteed by physics — even future quantum computers cannot retroactively break past key exchanges. But QKD requires dedicated hardware, line-of-sight, and has low key rates. PQC (ML-KEM, ML-DSA) runs on classical processors, works over any channel, and provides authentication. However, PQC's security depends on lattice problems being hard — a mathematical assumption that could theoretically be broken. AETHERIX layers both: QKD for key material when available, PQC for authentication always. If the quantum channel degrades, PQC key exchange takes over. If lattice cryptography is compromised, QKD keys are unaffected. The combination is more robust than either alone.

### Q5. "What's the practical key rate for Earth-Mars QKD, and is it actually useful?"

The simulated key rate for Earth-Mars E91 with Lagrange repeaters is 1–10 bits per second (documented in `interview_prep/cheat_sheets/constants.md`). At 10 bps, a 256-bit key takes 25 seconds to generate. For comparison, AES-256 key rotation might be needed every 24 hours for routine telemetry, or every 10 minutes for high-security command links. At 10 bps, even a 10-minute rotation schedule produces 6,000 bits of key material — far more than needed. The practical question is whether the channel is available long enough: a 6-hour contact window produces ~216 kbits, enough for weeks of AES-256 keys. So yes, even these low rates are operationally useful. The trade-off is that this is simulation — real deep-space QKD has not been demonstrated and faces significant engineering challenges (photon loss, background noise, timing synchronisation).

## Multi-Hop Repeater Chains

AETHERIX deploys quantum repeaters in a chain topology for Earth-Mars QKD. The chain architecture extends entanglement across multiple hops:

### Chain Configuration

```
Earth ←→ LEO-01 ←→ ES-L4 ←→ ES-L5 ←→ Mars-Orbital ←→ Mars-Surface
  (1)       (2)       (3)       (4)         (5)
```

Each hop segment is sized to maintain entanglement fidelity above the threshold for useful key extraction:

| Hop | Endpoints | Distance | Channel | Fidelity per Hop |
|-----|-----------|----------|---------|-----------------|
| 1 | Earth GS ↔ LEO-01 | 500–2,000 km | Free-space optical | 0.98 |
| 2 | LEO-01 ↔ ES-L4 | ~150M km | Deep-space optical | 0.75 |
| 3 | ES-L4 ↔ ES-L5 | ~260M km (variable) | Optical crosslink | 0.70 |
| 4 | ES-L5 ↔ Mars Orbital | ~150M km | Deep-space optical | 0.75 |
| 5 | Mars Orbital ↔ Surface | 17,032 km | Free-space optical | 0.95 |

### End-to-End Fidelity

The end-to-end entanglement fidelity degrades multiplicatively across the chain:

```
F_total = F₁ × F₂ × F₃ × F₄ × F₅
```

Without purification, the raw end-to-end fidelity would be approximately `0.98 × 0.75 × 0.70 × 0.75 × 0.95 ≈ 0.367` — below the threshold for useful key extraction. This is why entanglement purification is essential (see below).

### Entanglement Swapping Synchronisation

Each repeater must perform a Bell-state measurement (BSM) only after receiving entangled photons from both adjacent links. The classical BSM result must be communicated to the end nodes before they can use the shared entanglement. This introduces a classical communication latency:

```
t_sync = max(OWLT(R₁→Alice), OWLT(R₁→Bob)) + BSM_processing_time
```

For the Earth-Mars chain, this synchronisation adds ~15–22 minutes of classical communication delay per repeater, making the total key generation round-trip on the order of hours. AETHERIX pipelines the process: while one set of entangled pairs is being measured, the next set is being distributed.

## Entanglement Purification

Entanglement purification distills high-fidelity entangled pairs from multiple low-fidelity pairs. AETHERIX uses the Deutsch et al. (1996) protocol:

### Protocol Steps

1. **Generate two low-fidelity pairs**: Alice and Bob share pairs (A₁, B₁) and (A₂, B₂), each with fidelity F < 1.
2. **Local operations**: Alice applies a CNOT gate with A₁ as control and A₂ as target. Bob does the same with B₁ as control and B₂ as target.
3. **Measurement**: Both parties measure the target qubits (A₂, B₂) in the computational basis.
4. **Classical communication**: Alice and Bob compare their measurement results over the classical channel.
5. **Keep or discard**: If the measurement results agree, the remaining pair (A₁, B₁) has higher fidelity than either original pair. If they disagree, the pair is discarded.

### Fidelity Improvement

Starting with n pairs of fidelity F, one purification round produces ~n/2 pairs of fidelity:

```
F' = F² / (F² + (1−F)²)
```

For example: F = 0.75 → F' = 0.5625 / (0.5625 + 0.0625) = 0.90. Multiple rounds can push fidelity above 0.99, at the cost of consuming exponentially more raw pairs.

### Application in AETHERIX

For the 5-hop Earth-Mars chain, purification is applied at each intermediate node before entanglement swapping:

- **Hops 2, 3, 4** (deep-space segments, F ≈ 0.70–0.75): require 2–3 rounds of purification to achieve F > 0.90 per segment.
- **Hops 1, 5** (near-Earth/near-Mars, F ≈ 0.95–0.98): require 0–1 rounds.
- **End-to-end** after swapping purified segments: F_total ≈ 0.90⁵ ≈ 0.59, still requiring additional end-to-end purification rounds to reach the QBER < 11% threshold (equivalent to F > 0.89).

The purification overhead is significant: each round halves the number of usable pairs. AETHERIX's simulation models this trade-off between purified key rate and fidelity.

## CASCADE Reconciliation Protocol

CASCADE is the error reconciliation protocol used after QKD sifting to correct bit errors between Alice's and Bob's raw keys:

### Protocol Steps

1. **Random permutation**: Alice and Bob apply the same random permutation to their bit strings (agreed via classical channel) to randomise error positions.
2. **Block parity comparison**: The strings are divided into blocks. For each block, Alice and Bob compute and compare parity (XOR of all bits). If parities match, the block is presumed error-free (up to the probability of an even number of errors).
3. **Binary search for errors**: When a block's parity differs, a binary search (bisecting the block repeatedly) locates and corrects the offending bit.
4. **Multiple passes**: The process repeats with different block sizes and permutations. Smaller blocks catch isolated errors; larger blocks catch clustered errors. AETHERIX uses 3 passes with block sizes of {8, 16, 32} bits.
5. **Cascade effect**: Correcting one bit may resolve parity mismatches in previous passes (the "cascade"), so previous passes are rechecked.

### Efficiency

CASCADE's efficiency is measured by the information leaked during reconciliation:

```
leak_EC = (number of parity bits revealed) / (raw key length)
```

For QBER = 5%, CASCADE typically achieves leak_EC ≈ 0.55 (55% overhead). The theoretical minimum (Shannon limit) is h(0.05) ≈ 0.286, so CASCADE is ~2× the minimum. More efficient protocols (LDPC, Polar codes) approach the Shannon limit but are more complex to implement. AETHERIX uses CASCADE for the demo due to its simplicity; production would switch to LDPC for efficiency.

## Privacy Amplification

After reconciliation, Alice and Bob share identical keys, but an eavesdropper may have partial information. Privacy amplification eliminates this:

### Universal Hash Functions

Alice and Bob agree on a universal hash function h: {0,1}ⁿ → {0,1}ᵐ, where m < n. The function is selected randomly from a universal family (e.g., Toeplitz matrices) and announced over the classical channel. The output length m is:

```
m = n × (1 − h(QBER)) − leak_EC − security_parameter
```

Where:
- `n` is the reconciled key length.
- `h(QBER)` is the binary entropy of the QBER (Eve's maximum information from intercepting the quantum channel).
- `leak_EC` is the information leaked during error reconciliation.
- `security_parameter` (typically 2⁻³²) ensures the final key is ε-secure.

### AETHERIX Implementation

In `src/security/qkd.py`, privacy amplification uses a Toeplitz-matrix hash:

```python
# Pseudocode
def privacy_amplify(reconciled_key, m):
    seed = random_bitstring(n + m - 1)  # announced on classical channel
    toeplitz_matrix = construct_toeplitz(seed, n, m)
    final_key = toeplitz_matrix @ reconciled_key  # matrix multiply over GF(2)
    return final_key
```

The final key is information-theoretically secure: even if Eve knows the hash function and the parity information from CASCADE, the compressed output reveals no information about the key bits (up to the security parameter).

## Csiszár-Körner Bound

The Csiszár-Körner bound (1978) provides the theoretical maximum rate at which secret key can be extracted from correlated random variables:

```
S ≤ H(X) − H(X|Y)
```

Or equivalently, for a binary symmetric channel with error probability p (which models BB84 with QBER = p):

```
S ≤ 1 − h(p)
```

Where h(p) = −p log₂(p) − (1−p) log₂(1−p) is the binary entropy function.

### Significance for AETHERIX

- At QBER = 11% (the Shor-Preskill threshold): S = 1 − h(0.11) = 1 − 0.5004 = 0.4996. Positive secret key rate is achievable.
- At QBER = 15%: S = 1 − h(0.15) = 1 − 0.6098 = 0.3902. Still positive — but practical implementations abort at 11% because the security proof requires specific assumptions (single-photon sources, no detector flaws) that become increasingly strained at higher QBER.
- At QBER = 50%: S = 0. No secret key possible — Eve has complete information.

The Csiszár-Körner bound is tighter than the Devetak-Winter bound for finite-key scenarios and is used in AETHERIX's simulation to calculate the theoretical maximum secret key rate for comparison with the simulated rate.

## Post-Processing Pipeline

AETHERIX's complete QKD post-processing pipeline transforms raw detection events into a usable secret key:

```
Raw detections → Sifting → QBER estimation → Reconciliation → Privacy amplification → Secret key
```

### Stage 1: Sifting

Alice and Bob announce bases over the authenticated classical channel. Bits where bases match are retained (~50%). Typical sifted key length for a 6-hour contact: 10,000–100,000 bits at 1–10 bps raw rate.

### Stage 2: QBER Estimation

A random subset (~20%) of the sifted key is publicly compared. If QBER > 11%, the protocol aborts. The sacrificed bits are discarded and cannot be used in the final key. Remaining sifted key after QBER check: ~80% of sifted.

### Stage 3: Reconciliation (CASCADE)

Bit errors between Alice and Bob are corrected using CASCADE (3 passes). Information leaked during reconciliation (parity bits) is tracked for privacy amplification.

### Stage 4: Privacy Amplification

A universal hash function compresses the reconciled key by an amount proportional to Eve's potential information plus the reconciliation leakage. Output: a shorter, information-theoretically secure secret key.

### Stage 5: Key Storage

The final secret key is stored in the node's key cache and used for AES-256 encryption of subsequent DTN bundles. When the key cache runs low (below threshold), a new QKD session is initiated during the next available contact window.

### Pipeline Performance (Simulated)

| Stage | Input | Output | Efficiency |
|-------|-------|--------|-----------|
| Raw detections | 100% | 100% | 1.00 |
| Sifting | 100% | ~50% | 0.50 |
| QBER check | ~50% | ~40% | 0.80 |
| Reconciliation | ~40% | ~40% (corrected) | leak_EC ≈ 0.55 |
| Privacy amplification | ~40% | ~15% | 0.375 |
| **End-to-end** | **100%** | **~15%** | **~0.075** |

A raw detection rate of 10 bps yields approximately 0.75 bps of final secret key material after the full pipeline.
