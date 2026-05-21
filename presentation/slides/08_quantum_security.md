# Quantum Security — Future-Proof Protection

## Quantum Key Distribution (QKD)

### Why Quantum Security?

| Classical Cryptography | Quantum Cryptography |
|----------------------|---------------------|
| Security based on computational hardness (factoring, discrete log) | Security based on laws of physics |
| Vulnerable to quantum computers (Shor's algorithm) | Immune to quantum computer attacks |
| Keys exchanged mathematically | Keys generated from quantum states |
| Eavesdropping undetectable | Eavesdropping fundamentally detectable |
| Relies on trusted third parties | No trusted third party needed |

**QKD provides information-theoretically secure key exchange.**

### BB84 Protocol (Bennett-Brassard, 1984)

```
Alice                                          Bob
  │                                              │
  │  ── Qubits in random bases (|↔⟩,|↗⟩) ──────► │
  │                                              │
  │  ◄──── Basis comparison (classical) ──────────│
  │                                              │
  │  ── Keep matching bits (~50% sifted) ────────►│
  │                                              │
  │  ◄──── QBER estimation (sample bits) ──────── │
  │                                              │
  │  QBER < 11% → SECURE                         │
  │  QBER ≥ 11% → ABORT (eavesdropper detected)  │
  │                                              │
  │  ── Error reconciliation (CASCADE) ──────────►│
  │                                              │
  │  ── Privacy amplification ──────────────────► │
  │                                              │
  │     ← Final shared secret key →              │
```

### E91 Protocol (Ekert, 1991) — Entanglement-Based

1. **Source** generates entangled photon pairs (Bell state)
2. **One photon → Alice, one photon → Bob** (distributed over channel)
3. Both measure in **random bases**
4. **Bell inequality test** — Violation proves entanglement intact
5. **Correlated measurements** become shared key
6. Any eavesdropping **breaks entanglement** (detected via Bell test)

### Full Post-Processing Pipeline — Implemented

| Stage | Algorithm | Purpose |
|-------|-----------|---------|
| **Sifting** | Basis reconciliation | Discard mismatched measurement bases (~50% retained) |
| **Error reconciliation** | CASCADE protocol | Correct bit errors without leaking key information |
| **Privacy amplification** | Csiszár-Körner bound | Compress key to eliminate any eavesdropper knowledge |
| **Authentication** | Classical MAC | Prevent man-in-the-middle on classical channel |

#### CASCADE Error Reconciliation

- **Binary + parity-check based** — Corrects errors in sifted key bit-by-bit
- **Multi-pass** — Iterates until error rate drops below threshold
- **Information leakage tracked** — Revealed parity bits accounted for in privacy amplification

#### Privacy Amplification (Csiszár-Körner)

- **Universal hash functions** — Randomly selected compression function
- **Compression ratio** — Determined by Csiszár-Körner bound: l = n − leak − δ
- **Security parameter δ** — Exponentially small probability of eavesdropper knowledge
- **Result** — Final key is information-theoretically secure

### Multi-Hop Quantum Repeater Chains — Implemented

```
Earth ◄──► ES-L4 ◄──► ES-L5 ◄──► Mars
  Repeater    Repeater    Repeater
  Chain 1     Chain 2     Chain 3
```

| Feature | Implementation |
|---------|---------------|
| **Entanglement swapping** | Multi-hop Bell state measurement at each repeater |
| **Purification** | Fidelity improvement using multiple noisy entangled pairs |
| **Nesting** | Hierarchical swapping for arbitrary distances |
| **Fidelity tracking** | Per-link and end-to-end entanglement fidelity monitored |
| **Threshold management** | Minimum fidelity per hop before accepting swap |

### AETHERIX Quantum Deployment Roadmap

| Phase | Link Segment | Protocol | Range | Key Rate | Status |
|-------|-------------|----------|-------|----------|--------|
| 1 | Earth ↔ LEO | BB84 | < 2,000 km | 1-10 kbps | Demonstrated (Micius satellite) |
| 2 | Earth ↔ GEO | BB84/E91 | ~36,000 km | 100-1000 bps | In development |
| 3 | Earth ↔ Mars | E91 + Multi-hop Repeaters | 54-401 M km | 1-10 bps | **Simulated (AETHERIX)** |

### Security Threshold

```
QBER < 11%  →  Key is SECURE (no eavesdropper)
QBER ≥ 11%  →  ABORT key exchange (eavesdropper likely detected)
```

The 11% threshold comes from the Shor-Preskill proof: any higher error rate means an eavesdropper could have intercepted without detection.

### Post-Quantum Cryptography (Complementary)

AETHERIX uses a **defense-in-depth** approach:
- **QKD** — Key exchange (information-theoretic security)
- **CRYSTALS-Kyber** — Key encapsulation (NIST PQC standard, lattice-based)
- **CRYSTALS-Dilithium** — Digital signatures (NIST PQC standard)

### Standards

- **ETSI QKD** — Quantum key distribution standards series
- **CCSDS 735.2-B-1** — Bundle Protocol Security (BPSec)
- **NIST FIPS 203** — CRYSTALS-Kyber (ML-KEM)
- **NIST FIPS 204** — CRYSTALS-Dilithium (ML-DSA)

### Demo

> **Launch demo**: [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/) → "QKD" tab

The web demo simulates BB84 and E91 protocols with adjustable eavesdropper probability and shows real-time QBER calculation.
