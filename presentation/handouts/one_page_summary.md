# AETHERIX — One-Page Examiner Handout

## Interplanetary Communication Network for Mars Mission Support

**Student**: Muhammad Abdullah Tariq | **Programme**: EduQual Level 6 Diploma in AI Operations | **Topic 59**

**Live Demo**: [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/) | **Repository**: [github.com/matx104/AETHERIX](https://github.com/matx104/AETHERIX)

---

## The Challenge

| Problem | Impact |
|---------|--------|
| Earth-Mars distance: 54.6M — 401M km | 3 — 22 min one-way light-time |
| Current RF data rates: 0.5 — 6 Mbps | Severely limited science data return |
| Solar conjunction (every 780 days) | 2-week complete communication blackout |
| TCP/IP requires low-latency RTT | Fails at 6 — 44 min round-trip times |

## The Solution: AETHERIX Architecture

### Five-Tier Network (241 nodes)

1. **Earth Ground** (6 nodes) — DSN stations: Goldstone, Madrid, Canberra + control centers
2. **Earth Orbital** (51 nodes) — 3 GEO relays + 48 LEO laser satellites
3. **Deep Space Transit** (8 nodes) — Lagrange point relays (ES-L4, ES-L5) + transfer orbit sats + quantum repeaters
4. **Mars Orbital** (6 nodes) — 2 areostationary + 2 polar orbiters + 2 relay comsats
5. **Mars Surface** (170 nodes) — Bases, rovers, drones, sensor networks

### Core Technologies

| Technology | Function | Standard |
|------------|----------|----------|
| **Bundle Protocol v7** | Store-and-forward delay-tolerant networking | RFC 9171, CCSDS 735.1-B-1 |
| **RL Routing** | Q-learning agents replace static Contact Graph Routing | Custom (demo implementation) |
| **Optical Links** (1550 nm) | 2 — 200 Mbps data rates (10-100× over RF) | CCSDS 141.0-B-1 |
| **QKD Security** | BB84/E91 quantum key distribution + post-quantum crypto | ETSI QKD, NIST FIPS 203/204 |

### Key Innovations

1. **RL-based autonomous routing** — Agents learn optimal forwarding from experience, adapt to link failures in seconds (vs hours for manual replanning)
2. **Lagrange relay constellation** — Maintains 50-70% availability during solar conjunction blackouts
3. **Hybrid optical/RF** — Optical primary for throughput (200 Mbps peak), RF backup for reliability (>99% combined availability)
4. **Quantum-secured links** — QKD for key exchange (information-theoretic security) + CRYSTALS-Kyber/Dilithium for post-quantum signatures

## Performance Comparison

| Metric | Current (MRO) | AETHERIX | Improvement |
|--------|:------------:|:--------:|:-----------:|
| Downlink rate | 0.5 — 6 Mbps | 2 — 200 Mbps | **10-100×** |
| Daily data volume | 5 — 10 GB | 50 — 100 GB | **10-20×** |
| Availability | 60 — 75% | > 95% | **+20-35%** |
| Routing | Static (CGR) | RL-adaptive | **Autonomous** |
| Security | AES-256 (classical) | QKD + PQC | **Future-proof** |
| Cost per MB | ~$0.10 | ~$0.01 | **10×** |

## Key Equations

- **Free-Space Path Loss**: FSPL = 20 × log₁₀(4πd/λ) dB
- **Link Budget**: Pr = Pt + Gt + Gr − FSPL − Latm − Lpoint
- **RL Reward**: R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)
- **QBER Threshold**: QBER < 11% → secure; QBER ≥ 11% → abort

## Standards Compliance

| Standard | Description |
|----------|-------------|
| CCSDS 734.2-B-1 | DTN Architecture |
| CCSDS 735.1-B-1 | Bundle Protocol Specification |
| CCSDS 735.2-B-1 | Bundle Protocol Security (BPSec) |
| CCSDS 141.0-B-1 | Optical Communications Physical Layer |
| CCSDS 142.0-B-2 | Space Link Identification (LNIS v5) |
| RFC 9171 | Bundle Protocol Version 7 |
| RFC 5326 | Licklider Transmission Protocol |

## Implementation Status

| Component | Location | Status |
|-----------|----------|--------|
| Optical Link Budget Calculator | `src/infrastructure/` | Complete |
| Hybrid Optical/RF Link Model | `src/infrastructure/` | Complete |
| Simulation Framework | `src/simulation/` | Complete |
| RL Routing Agent (Q-learning) | `src/routing/` | Complete |
| BPv7 Forwarding Engine (BFS fallback) | `src/routing/` | Complete |
| LTP Convergence Layer | `src/routing/` | Complete |
| Policy Engine | `src/routing/` | Complete |
| BB84/E91 QKD Simulation | `src/security/` | Complete |
| Quantum Repeater Chains | `src/security/` | Complete |
| Privacy Amplification (Toeplitz) | `src/security/` | Complete |
| CASCADE Error Correction | `src/security/` | Complete |
| Orbital Mechanics / Contact Windows | `src/orbital/` | Complete |
| Topology Generator (241 nodes) | `src/orbital/` | Complete |
| Training Pipeline | `src/simulation/` | Complete |
| Multi-Agent Federation | `src/simulation/` | Complete |
| Scenario Runner | `src/simulation/` | Complete |
| Interactive Web Platform | `docs/` | Live |
| Test Suite (480 tests) | `tests/` | Complete |

**27 source modules | 480 tests | 241-node topology | Live web platform**

## References (70+ total, IEEE format)

Full list in `references/REFERENCES.md` — foundational papers include:

1. Burleigh et al. (2003) — DTN for Interplanetary Internet
2. Bennett & Brassard (1984) — BB84 Quantum Key Distribution
3. Boroson et al. (2014) — Lunar Laser Communication Demonstration
4. Mnih et al. (2015) — Deep Q-Network (DQN)
5. Vallado (2013) — Fundamentals of Astrodynamics

---

*70+ academic references | 27 source modules | 480 tests | 12 interactive demos | Live web platform | Docker-ready*
