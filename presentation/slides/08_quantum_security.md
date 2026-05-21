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

### AETHERIX Quantum Deployment Roadmap

| Phase | Link Segment | Protocol | Range | Key Rate | Status |
|-------|-------------|----------|-------|----------|--------|
| 1 | Earth ↔ LEO | BB84 | < 2,000 km | 1-10 kbps | Demonstrated (Micius satellite) |
| 2 | Earth ↔ GEO | BB84/E91 | ~36,000 km | 100-1000 bps | In development |
| 3 | Earth ↔ Mars | E91 + Repeaters | 54-401 M km | 1-10 bps | Future (AETHERIX proposal) |

### Quantum Repeaters at Lagrange Points

```
Earth ←── Entangled Photons ──→ ES-L4 ←── Entanglement Swapping ──→ ES-L5 ←── Entangled Photons ──→ Mars
                                    ↑                                       ↑
                              Quantum Repeater                       Quantum Repeater
```

- **Problem**: Photon loss limits direct QKD to ~500 km
- **Solution**: Quantum repeaters perform entanglement swapping
- **Locations**: ES-L4 and ES-L5 (stable Lagrange points, 60° from Earth)
- **Result**: End-to-end entanglement across 225 M km

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
