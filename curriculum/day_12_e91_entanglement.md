# Day 12: E91 Protocol & Quantum Entanglement

## 📅 August 3, 2026

## 🎯 Learning Objective
Understand the E91 (Ekert 1991) entanglement-based QKD protocol, the physics of quantum entanglement, Bell's inequality, and why E91 is the protocol of choice for long-range quantum repeater architectures. Maps to exam objective **b. Quantum Communication and Cryptography**.

---

## 📖 The Core Concept

While BB84 uses single photons encoded in random bases, E91 takes a fundamentally different approach: it uses **entangled photon pairs**. The security guarantee is also different — BB84 relies on the no-cloning theorem; E91 relies on the violation of **Bell's inequality**, a test that distinguishes quantum mechanics from classical physics.

### What is Entanglement?

When two particles are entangled, their properties are correlated in a way that transcends classical probability. The canonical example is the Bell state:

```
|Φ+⟩ = (|00⟩ + |11⟩) / √2
```

This means: if Alice and Bob each hold one half of an entangled pair, and they both measure in the same basis, they always get the **same** result — even though the result itself is random. The correlation is perfect.

Einstein, Podolsky, and Rosen (EPR) argued this was impossible — it implied "spooky action at a distance." They proposed that hidden variables must predetermine the outcomes. In 1964, John Bell proved that no local hidden variable theory can reproduce all quantum predictions, and he formulated an inequality that classical systems satisfy but quantum systems violate.

### The E91 Protocol — Step by Step

**Step 1: Entangled pair generation**
A source (which could be anywhere — even between Alice and Bob) creates entangled photon pairs. In AETHERIX, this source is co-located with the Lagrange-point relay satellites.

**Step 2: Distribution**
One photon goes to Alice, one to Bob. They could be on opposite sides of the solar system.

**Step 3: Random basis measurement**
Each randomly chooses a measurement basis and records the result.

**Step 4: Key sifting**
Matching bases → sifted key (same as BB84). The correlations give identical key bits.

**Step 5: Bell test (the key difference)**
Non-matching bases are NOT discarded. Instead, they're used to test Bell's inequality. If the Bell parameter S > 2, the results violate the classical limit — confirming quantum correlations and ruling out eavesdropping.

**Step 6: Security from Bell violation**
If S = 2√2 ≈ 2.828 (the Tsirelson bound), the correlations are maximally quantum. Any eavesdropper would reduce S toward the classical limit of 2.0, making detection possible.

### Why E91 for Space?

**Device-independent security:** E91's security doesn't depend on trusting the source or detectors. Even if Eve controls the entanglement source, the Bell test catches her. This matters for space applications where hardware is physically remote.

**Entanglement swapping:** E91 naturally extends to quantum repeater architectures. By entangling Alice↔Repeater and Repeater↔Bob, then performing a Bell measurement at the repeater, Alice and Bob become entangled without ever sharing a direct link. This is the mechanism for interplanetary QKD (covered in depth on Day 13).

### BB84 vs E91 — When to Use Each

| Property | BB84 | E91 |
|----------|------|-----|
| Security basis | No-cloning theorem | Bell inequality violation |
| Photon source | Single photons | Entangled pairs |
| Device-independent? | No | Yes |
| Range (no repeater) | ~2000 km free-space | ~2000 km free-space |
| Best for | Near-Earth links | Deep space + repeaters |
| Implementation complexity | Lower | Higher |

AETHERIX uses **both**: BB84 for near-Earth segments (LEO-to-ground), E91 for the Earth-Mars deep-space link via quantum repeaters.

---

## 🔬 In AETHERIX

The `E91Protocol` class in `src/security/qkd.py` implements entanglement-based QKD:

```python
BELL_VIOLATION_THRESHOLD = 2.0   # Classical limit
BELL_QUANTUM_MAX = 2.828          # Tsirelson bound (2√2)
```

**Key implementation details:**
- `_generate_entangled_pair()`: Creates `|Φ+⟩` — perfectly correlated Bell pair. Returns `(bit, bit)` — when both measure in the same basis, results are identical.
- `_measure_with_angle()`: Supports Bell test measurement angles (Alice: 0°, 45°, 90°; Bob: 22.5°, 67.5°, 112.5°).
- `execute()`: Generates `num_pairs` entangled pairs, each party measures randomly, sifts matching-basis results, computes QBER.

The AETHERIX architecture notes: "Phase 3: Earth-Mars QKD via Lagrange point repeaters — entanglement swapping extends range."

---

## 📐 Key Numbers & Formulas

- **Bell inequality classical limit:** S ≤ 2.0
- **Tsirelson bound (quantum maximum):** S = 2√2 ≈ 2.828
- **Bell state:** `|Φ+⟩ = (|00⟩ + |11⟩) / √2`
- **E91 measurement angles (Alice):** 0°, 45°, 90°
- **E91 measurement angles (Bob):** 22.5°, 67.5°, 112.5°
- **QBER threshold:** < 11% (same as BB84)
- **Entangled pair correlation:** Perfect (100%) when measured in same basis

---

## 🔗 Standards & References

- [Ekert 1991 — E91 Protocol](https://link.aps.org/doi/10.1103/PhysRevLett.67.661)
- [Bell 1964 — Bell's Theorem](https://link.aps.org/doi/10.1103/PhysicsPhysiqueFizika.1.195)
- [Einstein, Podolsky, Rosen (1935) — EPR Paradox](https://journals.aps.org/pr/abstract/10.1103/PhysRev.47.777)
- [Aspect et al. (1982) — Experimental Bell Test](https://link.aps.org/doi/10.1103/PhysRevLett.49.1804)
- [Hensen et al. (2015) — Loophole-free Bell Test](https://www.nature.com/articles/nature15759)

---

## 💡 How the Examiner Will Probe This

**Q: "How does E91 differ from BB84?"**
→ BB84 uses single photons with security from the no-cloning theorem. E91 uses entangled pairs with security from Bell inequality violation. E91 is device-independent — even if Eve controls the source, the Bell test catches her. AETHERIX uses BB84 for near-Earth and E91 for deep-space repeater links.

**Q: "What is Bell's inequality and why does its violation matter?"**
→ Bell's inequality sets a limit (S ≤ 2.0) that any classical local hidden-variable theory must satisfy. Quantum mechanics violates this — entangled systems can reach S = 2√2 ≈ 2.828. If an eavesdropper tampers with entangled photons, the Bell parameter drops toward the classical limit, revealing the intrusion.

**Q: "Why are entangled pairs useful for interplanetary QKD?"**
→ Entanglement swapping via quantum repeaters extends the range. By placing repeaters at ES-L4 and ES-L5, the Earth-Mars link is split into two segments. Each segment generates entangled pairs; swapping at the repeater creates end-to-end entanglement between Earth and Mars without a direct quantum link.

**Q: "What is the Tsirelson bound?"**
→ 2√2 ≈ 2.828. It's the maximum possible Bell parameter in quantum mechanics — the strongest quantum correlation achievable. It represents perfectly entangled Bell pairs.

---

## ✅ Self-Check Questions

1. Write out the Bell state |Φ+⟩ and explain what it means for Alice and Bob's measurements.
2. What is the classical limit of Bell's inequality, and what value would quantum mechanics predict?
3. Explain why E91 provides "device-independent" security.
4. How does entanglement swapping work, and why is it needed for Earth-Mars QKD?
5. When would you choose E91 over BB84?

---

## 📂 Deep Dive Resources

- **Source code:** `src/security/qkd.py` — Read `E91Protocol` class
- **Repeater chain:** `src/security/repeater_chain.py` — Entanglement swapping implementation
- **Topic summary:** `interview_prep/topic_summaries/quantum_basics.md`
- **Mock interview:** `interview_prep/practice/mock_interview.md` Question 6
- **Live demo:** [QKD Interactive Demo](https://matx104.github.io/AETHERIX/#qkd) — switch between BB84 and E91
- **Tests:** `tests/test_qkd.py`, `tests/test_quantum_extended.py`
