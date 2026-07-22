# Day 10: Quantum Communication Primer for Space

## 📅 August 1, 2026

## 🎯 Learning Objective
Understand the foundational quantum mechanics principles that make Quantum Key Distribution (QKD) possible, and why these matter for securing interplanetary communications. Maps to exam objective **b. Quantum Communication and Cryptography**.

---

## 📖 The Core Concept

Classical cryptography — AES, RSA, even ECC — relies on computational hardness: "this problem is too expensive for a computer to solve." The threat? A sufficiently powerful quantum computer running Shor's algorithm breaks RSA and ECC in polynomial time. The promise of quantum communication is fundamentally different: **security guaranteed not by computational difficulty, but by the laws of physics.**

### The Four Pillars You Must Understand

**1. Superposition**
A classical bit is 0 or 1. A quantum bit (qubit) can exist in a superposition — simultaneously 0 and 1 — until measured. Think of it like a spinning coin: while spinning, it's neither heads nor tails. The moment you look (measure), it collapses to one state.

In AETHERIX, the `Qubit` class represents this:
- Rectilinear basis (Z): `|0⟩` and `|1⟩`
- Diagonal basis (X): `|+⟩` and `|−⟩`

**2. The No-Cloning Theorem**
This is the bedrock of QKD security. Quantum mechanics proves that it is impossible to create an identical copy of an unknown quantum state. Unlike classical bits — which can be freely copied, intercepted, and retransmitted — a qubit cannot be perfectly copied.

**Why this matters:** If an eavesdropper (Eve) tries to intercept quantum key material, she must measure the qubits. But measuring disturbs them. She can't copy and forward — she must guess a measurement basis, and half the time she'll be wrong, introducing detectable errors.

**3. Measurement Disturbance**
When you measure a qubit in the wrong basis, you get a random result and you've collapsed the state. This is irreversible. It's like trying to read a letter by burning it and analyzing the smoke — you get information, but you've destroyed the original.

**4. Entanglement** (covered in depth on Day 12)
Two qubits can be entangled — correlated in a way that has no classical analogue. Measuring one instantly determines the outcome of the other, regardless of distance. Einstein called it "spooky action at a distance." For QKD, entanglement enables protocols like E91 where security is guaranteed by Bell inequality violation.

### Why Space QKD?

QKD over fiber is limited to ~100-500 km due to photon absorption. Free-space optical links extend this dramatically — the Micius satellite demonstrated QKD from LEO (1200 km) to ground in 2017. For interplanetary distances, free-space is the only option, and even then, quantum repeaters are needed (Day 13).

AETHERIX envisions QKD for the **command link** — the most security-critical channel. Command bundles sent from Earth to Mars assets must be authenticated beyond any doubt. QKD provides information-theoretic security: no computer, quantum or classical, can break it.

---

## 🔬 In AETHERIX

The quantum security module lives in `src/security/qkd.py`. Key classes:

- **`Basis`** (Enum): `RECTILINEAR` ("R", Z basis) and `DIAGONAL` ("D", X basis)
- **`Qubit`** (dataclass): Stores `bit` (0 or 1), `basis`, and a visual state string (`|0⟩`, `|1⟩`, `|+⟩`, `|−⟩`)
- **`QKDResult`** (dataclass): Captures `alice_key`, `bob_key`, `sifted_key_length`, `qber`, `secure`, `raw_key_length`, `efficiency`

The module defines two protocols — `BB84Protocol` and `E91Protocol` — plus a `QuantumRepeater` class and a `calculate_key_rate()` utility function.

Supporting files:
- `src/security/repeater_chain.py` — Multi-hop quantum repeater chain with entanglement purification
- `src/security/privacy_amplification.py` — CASCADE reconciliation and universal hashing

The simulation's Module 5 demonstrates: 2048 qubits exchanged, clean channel QBER = 0.0%, eavesdropped channel QBER = 24.7%, key discarded.

---

## 📐 Key Numbers & Formulas

- **QBER security threshold:** < 11% (Shor-Preskill threshold)
- **BB84 key rate (LEO):** 1-10 kbps
- **BB84 key rate (GEO):** 100-1000 bps
- **Earth-Mars key rate:** ~1-10 bps (extremely low — needs repeaters)
- **Sifting efficiency:** ~50% (half the qubits are discarded when bases don't match)
- **Eavesdropper detection rate:** ~25% QBER for intercept-resend attack

---

## 🔗 Standards & References

- [BB84 Original Paper — Bennett & Brassard (1984)](https://www.scirp.org/reference/referencespapers?referenceid=3040259)
- [Ekert 1991 — E91 Protocol](https://link.aps.org/doi/10.1103/PhysRevLett.67.661)
- [Micius Satellite QKD Experiment (2017)](https://www.science.org/doi/10.1126/science.aan3211)
- [Nielsen & Chuang — Quantum Computation and Quantum Information](https://www.cambridge.org/highereducation/books/quantum-computation-and-quantum-information/01D10122C9F4A2A6C9A0D9A6C9A0D9A6)
- [NIST Post-Quantum Cryptography Project](https://csrc.nist.gov/projects/post-quantum-cryptography)

---

## 💡 How the Examiner Will Probe This

**Q: "What makes quantum key distribution fundamentally different from classical cryptography?"**
→ Classical crypto relies on computational hardness (RSA = factoring is hard). QKD relies on the laws of physics — specifically, the no-cloning theorem means an eavesdropper cannot copy quantum states without disturbing them. The security is information-theoretic, not computational.

**Q: "If a quantum computer can break RSA, why not just use AES-256?"**
→ AES-256 is still considered quantum-resistant (Grover's algorithm halves the effective key length to 128 bits, which is still secure). The issue is key exchange — RSA and ECC for sharing AES keys are broken by Shor's algorithm. QKD replaces key exchange with a physics-guaranteed method.

**Q: "What's the practical limitation of QKD in space?"**
→ Key rate. At Earth-Mars distance, the key rate is ~1-10 bps due to photon loss across 54.6-401 million km. This limits QKD to high-value links (command authentication), not bulk data encryption.

---

## ✅ Self-Check Questions

1. Explain the no-cloning theorem in your own words and why it's the foundation of QKD security.
2. What happens when Eve measures a qubit in the wrong basis? What observable effect does this create?
3. Why is QKD limited to key exchange rather than bulk data encryption?
4. What is the QBER threshold and what does it represent physically?
5. How does the Micius satellite experiment validate the feasibility of space-based QKD?

---

## 📂 Deep Dive Resources

- **Source code:** `src/security/qkd.py` — Read the `Basis`, `Qubit`, and `QKDResult` classes
- **Topic summary:** `interview_prep/topic_summaries/quantum_basics.md`
- **Live demo:** [QKD Interactive Demo](https://matx104.github.io/AETHERIX/#qkd)
- **Learn page:** [Science Behind QKD](https://matx104.github.io/AETHERIX/#qkd-science)
- **Cheat sheet:** `interview_prep/cheat_sheets/constants.md` — quantum thresholds
