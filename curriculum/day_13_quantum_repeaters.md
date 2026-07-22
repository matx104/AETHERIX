# Day 13: Quantum Repeaters & Entanglement Swapping

## 📅 August 4, 2026

## 🎯 Learning Objective
Understand quantum repeaters, entanglement swapping, entanglement purification, and how AETHERIX places repeater nodes at the Earth-Sun Lagrange points (ES-L4 and ES-L5) to enable interplanetary QKD. Maps to exam objective **b. Quantum Communication and Cryptography**.

---

## 📖 The Core Concept

### The Problem: Photon Loss Over Distance

Direct QKD over free space is limited by photon loss. Even with perfect pointing and no atmospheric interference, the inverse-square law means photon density drops with the square of distance. At Earth-Mars distance (54.6-401 million km), the fraction of photons received is vanishingly small — roughly 10⁻¹⁷ at average distance.

For classical communication, this is solved with **repeaters**: amplifiers that boost signal strength along the path. But quantum mechanics forbids this approach — the **no-cloning theorem** means you cannot copy or amplify a quantum state. A classical repeater doesn't work for quantum signals.

### The Solution: Quantum Repeaters

Quantum repeaters solve this through **entanglement swapping** — a technique proposed by Briegel, Dür, Cirac, and Zoller in 1998. Instead of sending a single photon across the entire distance, you break the journey into segments:

**1. Segment-level entanglement**
Create entangled pairs within each segment. Alice↔Repeater-1 are entangled. Repeater-1↔Repeater-2 are entangled. Repeater-2↔Bob are entangled.

**2. Entanglement swapping**
At each repeater node, perform a **Bell-state measurement** on the two qubits it holds (one from each adjacent segment). This measurement *projects* Alice and the next repeater into an entangled state — even though they never directly interacted.

**3. Cascading**
Repeat the process at each repeater. After all swaps, Alice and Bob are entangled end-to-end, as if they shared a direct quantum link.

### Entanglement Purification

Real-world entangled pairs aren't perfect — channel noise degrades fidelity. Before swapping, repeaters perform **entanglement purification** (Deutsch et al., 1996):

1. Take two noisy entangled pairs
2. Perform specific joint measurements
3. Keep the higher-fidelity pair, discard the other
4. Repeat until fidelity exceeds the threshold for successful swapping

This is essential because entanglement swapping compounds errors — if each segment has fidelity 0.9, the end-to-end fidelity after N hops would be 0.9^N without purification.

### Where AETHERIX Places Repeaters

AETHERIX places quantum repeaters at the **Earth-Sun Lagrange points ES-L4 and ES-L5** — gravitationally stable points 60° ahead and behind Earth in its orbit around the Sun, approximately 150 million km from Earth.

```
Earth ──hop0── [ES-L4] ──hop1── [ES-L5] ──hop2── Mars
```

**Why Lagrange points?**
- **Gravitational stability:** Spacecraft at L4/L5 require minimal station-keeping fuel — they're gravitationally trapped
- **Conjunction coverage:** They're positioned to maintain line-of-sight during solar conjunction, when direct Earth-Mars links are blocked
- **Distance splitting:** They break the Earth-Mars link into manageable segments (~150M km each instead of 225M+ km direct)

### The Honest Assessment

Interplanetary QKD has **never been demonstrated**. AETHERIX's simulation proves the *protocol layer* is sound — the quantum mechanics is correct, the security proofs hold, the repeater architecture is physically valid. But the hardware challenges are enormous:

- Generating and detecting entangled photons across 150M km
- Maintaining pointing accuracy to arcsecond precision
- Dealing with solar radiation pressure on optical components
- Achieving usable key rates despite extreme photon loss

Be honest about this in the exam. The simulation validates the theory and architecture; deployment is a future engineering challenge.

---

## 🔬 In AETHERIX

**`src/security/repeater_chain.py`** implements the multi-hop repeater chain:

```
Architecture: Earth ──hop0── [ES-L4] ──hop1── [ES-L5] ──hop2── Mars
```

Key classes:
- **`EntanglementPair`** (dataclass): Stores `node_a`, `node_b`, `fidelity` (0.0-1.0), `is_purified` flag
- **`PurificationResult`**: Outcome of a purification round — success/failure and resulting fidelity
- **`QuantumRepeaterChain`**: Orchestrates entanglement generation, purification, and cascading Bell-state measurements across all hops

**`src/security/qkd.py`** also contains the `QuantumRepeater` class:
- `perform_entanglement_swapping()` — Simulates Bell measurement at repeater node
- `success_rate` parameter — models the probabilistic nature of swapping (real Bell measurements succeed only ~50% of the time)

**References cited in code:**
- Briegel, Dür, Cirac, Zoller (1998) — quantum repeaters
- Deutsch et al. (1996) — entanglement purification

---

## 📐 Key Numbers & Formulas

- **Direct QKD range (fiber):** ~100-500 km
- **Direct QKD range (free-space):** ~2,000 km
- **ES-L4/ES-L5 distance from Earth:** ~150 million km
- **Earth-Mars average distance:** 225 million km
- **Photon capture fraction at 225M km:** ~10⁻¹⁷
- **Bell measurement success rate:** ~50% per swap (in reality)
- **Purification fidelity improvement:** Two pairs of fidelity F → one pair of higher fidelity F' > F
- **Entanglement swapping formula:** If A-R and R-B are entangled, Bell measurement at R creates A-B entanglement

---

## 🔗 Standards & References

- [Briegel, Dür, Cirac, Zoller (1998) — Quantum Repeaters](https://arxiv.org/abs/quant-ph/9803056)
- [Deutsch et al. (1996) — Entanglement Purification](https://arxiv.org/abs/quant-ph/9604039)
- [Micius Satellite — Entanglement Distribution over 1200 km](https://www.science.org/doi/10.1126/science.aan3211)
- [Nature Review — Quantum Repeaters (2019)](https://www.nature.com/articles/s42254-019-0085-4)
- [Lagrange Points — NASA Explanation](https://solarsystem.nasa.gov/resources/754/what-is-a-lagrange-point/)

---

## 💡 How the Examiner Will Probe This

**Q: "How do quantum repeaters extend QKD range, and where does AETHERIX place them?"**
→ Classical repeaters amplify signals — impossible for quantum states due to the no-cloning theorem. Quantum repeaters use entanglement swapping: create entangled pairs per segment, perform Bell measurements at each repeater to project end-to-end entanglement. AETHERIX places them at ES-L4 and ES-L5 — gravitationally stable Lagrange points ~150M km from Earth that also provide conjunction coverage.

**Q: "Why can't you just use a classical optical amplifier for quantum signals?"**
→ The no-cloning theorem. Amplification is fundamentally a copying operation, and quantum mechanics forbids perfect copying of unknown states. Any attempt to amplify a quantum signal introduces noise that destroys the quantum correlations needed for QKD.

**Q: "What is entanglement purification and why is it needed?"**
→ Real-world entangled pairs have imperfect fidelity due to channel noise. Purification takes two noisy pairs and, through joint measurements, produces one higher-fidelity pair. Without purification, errors compound across hops — N hops at fidelity F give end-to-end fidelity F^N.

**Q: "How many photons per second would you need for 1 bps at Mars distance?"**
→ At 225M km with 370 dB FSPL and a 1m receiving telescope, the capture fraction is ~10⁻¹⁷. For 1 detected photon per second, transmit ~10¹⁷ photons/s. At 1550nm (~1.3×10⁻¹⁹ J/photon), that's ~13 mW — feasible for transmit power. But detector dark counts and sifting loss reduce the effective key rate significantly.

**Q: "Has interplanetary QKD ever been demonstrated?"**
→ No. AETHERIX's simulation proves the protocol and architecture are physically sound. The Micius satellite demonstrated satellite-to-ground QKD from LEO (1200 km). Scaling to interplanetary distances is an unsolved engineering challenge. Be honest about this distinction.

---

## ✅ Self-Check Questions

1. Explain why classical repeaters don't work for quantum signals.
2. Describe the entanglement swapping process at a single repeater node.
3. Why does AETHERIX choose Lagrange points for repeater placement? Name two reasons.
4. What is entanglement purification and what happens without it?
5. Has interplanetary QKD been demonstrated? What HAS been demonstrated?

---

## 📂 Deep Dive Resources

- **Source code:** `src/security/repeater_chain.py` — Read the full chain implementation
- **Quantum repeater class:** `src/security/qkd.py` — `QuantumRepeater.perform_entanglement_swapping()`
- **Mock interview:** `interview_prep/practice/mock_interview.md` Question 6
- **Topic summary:** `interview_prep/topic_summaries/quantum_basics.md`
- **Live demo:** [QKD Interactive Demo](https://matx104.github.io/AETHERIX/#qkd)
- **Tests:** `tests/test_quantum_extended.py` — Repeater chain test cases
