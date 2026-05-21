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
