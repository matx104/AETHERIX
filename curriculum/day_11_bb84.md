# Day 11: BB84 Protocol Deep Dive

## 📅 August 2, 2026

## 🎯 Learning Objective
Master the BB84 (Bennett-Brassard 1984) QKD protocol step-by-step, including the quantum mechanics behind basis choices, sifting, QBER estimation, and eavesdropper detection. Maps to exam objective **b. Quantum Communication and Cryptography** (highest probability interview topic for quantum).

---

## 📖 The Core Concept

BB84 is the first and most widely implemented QKD protocol. Named after Charles Bennett and Gilles Brassard, who proposed it in 1984. It's the protocol you're most likely to be asked to explain step-by-step in the oral exam. **Know this cold.**

### The Protocol — 8 Steps

**Step 1: Alice generates random bits**
Alice creates a string of random classical bits: `01101001...`

**Step 2: Alice chooses random bases**
For each bit, Alice randomly chooses one of two bases:
- **Rectilinear (Z basis):** encodes 0 as `|0⟩` and 1 as `|1⟩`
- **Diagonal (X basis):** encodes 0 as `|+⟩` and 1 as `|−⟩`

The key insight: the *same* bit value looks different depending on the basis chosen. Bit "0" is `|0⟩` in rectilinear but `|+⟩` in diagonal.

**Step 3: Alice sends qubits to Bob**
Alice transmits the polarized photons over the quantum channel (free-space optical link in AETHERIX).

**Step 4: Bob measures with random bases**
Bob, not knowing Alice's basis choices, randomly selects a basis for each measurement. On average, Bob's basis matches Alice's ~50% of the time.

**Step 5: Basis reconciliation (public channel)**
Alice and Bob publicly announce which basis they used for each qubit — **but NOT the bit values.** This is critical: the basis choice is public; the measurement results are private.

**Step 6: Key sifting**
They discard all bits where bases didn't match (~50% of the total). The remaining bits form the **sifted key**.

**Step 7: QBER estimation**
They publicly compare a random subset of the sifted key to estimate the Quantum Bit Error Rate (QBER). This reveals errors from channel noise or eavesdropping.

**Step 8: Security decision**
- If QBER < 11% (Shor-Preskill threshold) → Key is secure. Proceed to error correction + privacy amplification.
- If QBER ≥ 11% → Eavesdropper detected. Abort and discard all key material.

### Eavesdropper Detection — Why BB84 is Secure

If Eve intercepts the quantum channel (intercept-resend attack):
1. Eve must measure each qubit (she can't copy it — no-cloning theorem)
2. Eve doesn't know Alice's basis, so she guesses randomly
3. ~50% of the time, Eve guesses wrong, and her measurement collapses the qubit into the wrong basis
4. When Eve forwards her measured qubit to Bob, ~25% of the sifted key bits will be wrong
5. This introduces a ~25% QBER — well above the 11% threshold → **detected**

This is the fundamental security guarantee: the act of eavesdropping *necessarily* introduces detectable errors.

### Post-Processing

After confirming QBER < 11%, two more steps produce the final key:
- **Information reconciliation (CASCADE):** Correct residual errors between Alice and Bob's keys
- **Privacy amplification:** Compress the key to eliminate any information Eve might have gained, producing a shorter but perfectly secret final key

---

## 🔬 In AETHERIX

The `BB84Protocol` class in `src/security/qkd.py` implements all 8 steps:

```python
SECURITY_THRESHOLD = 0.11  # 11% QBER threshold
```

**Key implementation details:**
- `_measure_qubit()`: If measurement basis matches preparation basis → deterministic result (plus channel error). If basis differs → random result (50/50).
- `execute()`: Runs all 8 steps, returns a `QKDResult` with sifted key, QBER, and security assessment.
- Eavesdropping is simulated via the `channel_error` parameter: 0.0 = clean channel, 0.25 = intercept-resend attack.

**Simulation Module 5 output:**
- 2048 qubits exchanged
- Clean channel: QBER = 0.0%, 1019 sifted key bits, SECURE
- Eavesdropped: QBER = 24.7%, NOT SECURE — key discarded

Post-processing lives in `src/security/privacy_amplification.py`:
- `information_reconciliation()` — CASCADE-style error correction
- `universal_hash()` — Privacy amplification via universal hashing

---

## 📐 Key Numbers & Formulas

- **Security threshold:** QBER < 11% (Shor-Preskill)
- **Sifting loss:** ~50% (bits discarded when bases don't match)
- **Intercept-resend detection:** Introduces ~25% QBER (detectable)
- **Efficiency formula:** `sifted_key_length / raw_qubits ≈ 0.50`
- **Key rate Earth-Mars:** ~1-10 bps
- **Binary entropy for privacy amplification:** h(QBER) determines compression ratio. At QBER = 8%: h(0.08) ≈ 0.4

---

## 🔗 Standards & References

- [BB84 — Bennett & Brassard (1984)](https://www.scirp.org/reference/referencespapers?referenceid=3040259)
- [Shor-Preskill Proof (2000)](https://arxiv.org/abs/quant-ph/0003004) — Proves BB84 security with QBER < 11%
- [CASCADE Error Correction — Brassard & Salvail (1994)](https://link.springer.com/article/10.1007/BF01213034)
- [Privacy Amplification — Bennett et al. (1995)](https://ieeexplore.ieee.org/document/467469)
- [Micius Satellite BB84 Demonstration (2017)](https://www.science.org/doi/10.1126/science.aan3211)

---

## 💡 How the Examiner Will Probe This

**Q: "Walk me through the BB84 protocol."**
→ Give the 8 steps above. Emphasize: (1) Alice encodes random bits in random bases, (2) Bob measures in random bases, (3) they publicly compare bases (not values), (4) sift to matching-basis bits, (5) estimate QBER, (6) if < 11%, proceed to error correction + privacy amplification.

**Q: "What if QBER comes back at 8% — is that secure?"**
→ Yes. 8% is below the 11% Shor-Preskill threshold. The key has some information leakage, but privacy amplification compresses it by the binary entropy h(0.08) ≈ 0.4, producing a shorter but perfectly secret final key.

**Q: "What's the advantage of BB84 over just using RSA?"**
→ RSA's security depends on factoring being computationally hard — but Shor's algorithm breaks it on a quantum computer. BB84's security is guaranteed by the no-cloning theorem — a law of physics, not computational difficulty. No computer, quantum or classical, can break it.

**Q: "How does Eve's intercept-resend attack get detected?"**
→ Eve must measure each qubit without knowing Alice's basis. Half the time she picks the wrong basis, collapsing the qubit incorrectly. When she forwards to Bob, ~25% of sifted bits are wrong — producing a detectable QBER spike above the 11% threshold.

---

## ✅ Self-Check Questions

1. List all 8 steps of BB84 in order. Which step involves the public channel?
2. Why do Alice and Bob publicly compare bases but NOT bit values?
3. An eavesdropper uses intercept-resend. What QBER do you expect, and why?
4. QBER is measured at 8%. Is the key secure? What happens next?
5. What is the sifting loss and why does it occur?

---

## 📂 Deep Dive Resources

- **Source code:** `src/security/qkd.py` — Read `BB84Protocol.execute()` carefully
- **Post-processing:** `src/security/privacy_amplification.py` — CASCADE + universal hashing
- **Mock interview:** `interview_prep/practice/mock_interview.md` Question 5
- **Topic summary:** `interview_prep/topic_summaries/quantum_basics.md`
- **Live demo:** [QKD Interactive Demo](https://matx104.github.io/AETHERIX/#qkd)
- **Tests:** `tests/test_qkd.py` — Read the test cases to understand expected behavior
