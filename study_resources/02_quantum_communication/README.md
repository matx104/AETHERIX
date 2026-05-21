# Learning Objective 2: Quantum Communication & QKD

## Free Online Courses & Certificates

### University Courses (Free)
- **[Quantum Computing — Brilliant.org](https://brilliant.org/courses/quantum-computing/)** — Interactive quantum fundamentals (free tier available)
- **[Quantum Mechanics for Scientists and Engineers — Stanford (edX)](https://www.edx.org/course/quantum-mechanics-for-scientists-and-engineers)** — Free audit
- **[The Quantum Internet and Quantum Computers — TU Delft (edX)](https://www.edx.org/course/quantum-internet-and-quantum-computers-how-will-they-change-the-world)** — FREE, covers QKD, entanglement, quantum repeaters
- **[Understanding Quantum Computers — Keio University (edX/FutureLearn)](https://www.edx.org/course/understanding-quantum-computers-and-quantum-internet-keio)** — Free audit
- **[Quantum Cryptography — Caltech (edX)](https://www.edx.org/course/quantum-cryptography)** — Free audit, highly relevant

### Official Documentation (Free)
- **[ETSI QKD Standards](https://www.etsi.org/committee/1434-quantum-key-distribution)** — European QKD standards (free downloads)
- **[NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)** — PQC standardization results
- **[NIST FIPS 203 — ML-KEM (CRYSTALS-Kyber)](https://csrc.nist.gov/pubs/fips/203/final)** — Official standard
- **[NIST FIPS 204 — ML-DSA (CRYSTALS-Dilithium)](https://csrc.nist.gov/pubs/fips/204/final)** — Official standard
- **[Original BB84 Paper](https://www.researchgate.net/publication/215639057_quantum_cryptography_public_key_distribution_and_coin_tossing)** — Bennett & Brassard 1984

### YouTube Videos (Free)

#### Must-Watch (QKD Specific)
| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [Quantum Key Distribution Explained](https://www.youtube.com/watch?v=UIwKjGrjXfg) | PBS Space Time | ~15 min | Best visual explanation of QKD |
| [BB84 Protocol Step by Step](https://www.youtube.com/results?search_query=BB84+protocol+explained) | Various | ~20 min | Walk through each phase |
| [Quantum Entanglement Explained](https://www.youtube.com/watch?v=ZuvK-occemc) | Looking Glass Universe | ~15 min | Foundation for E91 |
| [Bell's Theorem and EPR Paradox](https://www.youtube.com/watch?v=ZuvK-occemc) | Sixty Symbols | ~15 min | Understand entanglement |
| [How Quantum Computers Break Encryption](https://www.youtube.com/watch?v=6TdUUriY3DA) | Veritasium | ~15 min | Why QKD matters |
| [Quantum Repeaters Explained](https://www.youtube.com/results?search_query=quantum+repeater+explained) | Various | ~15 min | Long-distance QKD |

#### Quantum Fundamentals
| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [Quantum Mechanics — Full Course](https://www.youtube.com/watch?v=ffeuOmExxbw) | MIT OpenCourseWare | ~8 hrs | Deep understanding if time allows |
| [Stern-Gerlach Experiment](https://www.youtube.com/watch?v=rg4FF0sM2Uw) | Looking Glass Universe | ~10 min | Quantum measurement basics |
| [No-Cloning Theorem](https://www.youtube.com/results?search_query=no+cloning+theorem+explained) | Various | ~10 min | Why QKD is secure |
| [Heisenberg Uncertainty Principle](https://www.youtube.com/watch?v=D1yb1adU2v8) | PBS Space Time | ~15 min | Measurement disturbance |

#### China's Micius Satellite (Real QKD in Space)
| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [China's Quantum Satellite](https://www.youtube.com/results?search_query=micius+satellite+quantum) | Various | ~10 min | Real-world satellite QKD |
| [Satellite-to-Ground QKD](https://www.nature.com/articles/nature23655) | Nature Paper | — | Liao et al. 2017 (the key paper) |

### Academic Papers (Free / Open Access)

| Paper | Authors | Year | Link | Priority |
|-------|---------|------|------|:--------:|
| "Quantum Cryptography: Public Key Distribution and Coin Tossing" | Bennett & Brassard | 1984 | [ResearchGate](https://www.researchgate.net/publication/215639057) | MUST READ |
| "Quantum Cryptography Based on Bell's Theorem" | A.K. Ekert | 1991 | [PRL](https://doi.org/10.1103/PhysRevLett.67.661) | MUST READ |
| "Satellite-to-Ground Quantum Key Distribution" | Liao et al. | 2017 | [Nature](https://doi.org/10.1038/nature23655) | HIGH |
| "Progress in Satellite Quantum Key Distribution" | Bedington et al. | 2017 | [npj QI](https://doi.org/10.1038/s41534-017-0031-5) | HIGH |
| "Quantum Repeaters" | Briegel et al. | 1998 | [PRL](https://doi.org/10.1103/PhysRevLett.81.5932) | MEDIUM |
| "Quantum Internet: A Vision for the Road Ahead" | Wehner et al. | 2018 | [Science](https://doi.org/10.1126/science.aam9288) | MEDIUM |

### Blogs & Articles (Free)

- **[Quantum Computing Report](https://quantumcomputingreport.com/)** — Industry news
- **[IBM Quantum Blog](https://www.ibm.com/quantum/blog)** — IBM's quantum updates
- **[Quantum Magazine](https://www.quantamagazine.org/tag/quantum-computing/)** — Excellent science journalism
- **[NIST PQC FAQ](https://csrc.nist.gov/projects/post-quantum-cryptography/faqs)** — Understand the standardization
- **[QKD Security Proofs — Wikipedia](https://en.wikipedia.org/wiki/Quantum_key_distribution)** — Good overview
- **[Micius Satellite — Nature Collection](https://www.nature.com/collections/jbcbhfifjg)** — All Micius papers

### Key Concepts to Master

1. **BB84 Protocol** — 4 phases: send, measure, sift, verify. Know each step.
2. **QBER Threshold** — 11% is the magic number (Shor-Preskill bound). Know WHY.
3. **No-Cloning Theorem** — Why you can't copy quantum states. Core security principle.
4. **E91 Protocol** — Entanglement-based. Bell inequality violation proves security.
5. **Quantum Repeaters** — Entanglement swapping extends range. Know the mechanism.
6. **Post-Quantum Crypto** — CRYSTALS-Kyber (encryption), CRYSTALS-Dilithium (signatures). Complementary to QKD.
7. **Why "information-theoretically secure"** — Not computational hardness. Laws of physics.

### Practice Questions

1. Walk through BB84 step by step (2 minutes)
2. Why is QBER < 11% the threshold? What happens at 12%? (1 minute)
3. Explain entanglement swapping for quantum repeaters (1 minute)
4. What's the difference between QKD and post-quantum cryptography? (30 seconds)
5. How does Micius satellite demonstrate satellite QKD? (1 minute)
