# Day 14: Post-Quantum Cryptography (ML-KEM, ML-DSA)

## 📅 August 5, 2026

## 🎯 Learning Objective
Understand post-quantum cryptography (PQC), the NIST FIPS 203/204/205 standards, and why AETHERIX uses a defense-in-depth approach combining QKD with lattice-based PQC for key exchange and authentication. Maps to exam objective **b. Quantum Communication and Cryptography**.

---

## 📖 The Core Concept

### The Quantum Threat

Shor's algorithm, running on a sufficiently powerful quantum computer, breaks RSA, Diffie-Hellman, and elliptic curve cryptography (ECC) in polynomial time. While large-scale quantum computers don't exist yet, the threat is real enough that NIST ran a multi-year competition to standardize quantum-resistant algorithms.

**Harvest-now-decrypt-later:** Adversaries can record encrypted traffic today and decrypt it years from now when quantum computers mature. This means the migration to PQC is urgent *now*, not when quantum computers arrive.

### NIST Post-Quantum Standards

After a 7-year competition starting in 2016, NIST finalized three standards in 2024:

**FIPS 203 — ML-KEM (Module-Lattice-Based Key Encapsulation)**
- Based on CRYSTALS-Kyber
- Purpose: Key encapsulation (replacing RSA/ECDH key exchange)
- Security: Equivalent to AES-256
- Key sizes: ~800 bytes (public key), ~1,600 bytes (ciphertext)
- Fast on classical hardware — no quantum computer needed

**FIPS 204 — ML-DSA (Module-Lattice-Based Digital Signature)**
- Based on CRYSTALS-Dilithium
- Purpose: Digital signatures (replacing RSA/ECDSA)
- ML-DSA-65 signature size: **3,309 bytes**
- Fast verification on classical hardware

**FIPS 205 — SLH-DSA (Stateless Hash-Based Digital Signature)**
- Based on SPHINCS+
- Purpose: Digital signatures using only hash functions (no lattice assumption)
- Signature size: Much larger (~49,000 bytes)
- Conservative security — if lattices fall, hash-based signatures still hold

### Why AETHERIX Uses Both QKD AND PQC

This is **defense-in-depth** — the most important concept to articulate in the exam:

**Layer 1: QKD (Information-Theoretic Security)**
- Security guaranteed by the laws of physics
- No computer can break it — not even a quantum computer
- **Limitation:** Requires dedicated quantum hardware, line-of-sight, and has very low key rates (1-10 bps Earth-Mars)
- If the quantum channel is unavailable (weather, equipment failure, solar conjunction), QKD is down

**Layer 2: ML-KEM (Computational Security — Quantum-Resistant)**
- Runs on classical hardware over any channel
- Provides key exchange when QKD is unavailable
- Security depends on the hardness of the lattice problem — believed quantum-resistant
- **Limitation:** Computational, not information-theoretic. If someone breaks the lattice problem, ML-KEM falls

**Layer 3: ML-DSA (Authentication)**
- QKD can distribute keys but **cannot authenticate** the communicating parties
- ML-DSA solves this — digital signatures prove identity
- Every bundle is signed with ML-DSA for non-repudiation and integrity

**The layered guarantee:**
- If the quantum channel fails → ML-KEM handles key exchange
- If lattice cryptography is compromised → QKD keys remain secure
- Authentication always uses ML-DSA regardless of key exchange method

### Practical Considerations — Signature Overhead

ML-DSA-65 signatures are **3,309 bytes**. For different bundle sizes:
- **1 MB science bundle:** 3,309 bytes = 0.3% overhead → negligible
- **100-byte command bundle:** 3,309 bytes = 33× the payload → significant!

For small command bundles, the overhead is problematic. That's where **SLH-DSA** or hash-based signatures might be preferred — or signature aggregation schemes where one signature covers multiple commands.

---

## 🔬 In AETHERIX

Post-quantum cryptography is referenced throughout AETHERIX's architecture:

**In `src/security/qkd.py`:**
- The `calculate_key_rate()` function acknowledges deep-space key rate limitations
- The simulation demonstrates that QKD produces keys at 1-10 bps for Mars distance — too slow for bulk encryption, suitable for key exchange on high-value links

**In the documentation:**
- `AETHERIX.md` (exam topic) lists ML-KEM (FIPS 203) and ML-DSA (FIPS 204) as post-quantum algorithms
- Standards compliance table cites NIST FIPS 203, 204, 205
- The design rationale discusses the layered security approach

**In the mock interview (Question 7):**
> "Why does AETHERIX use both QKD and post-quantum cryptography?"
> Answer: Defense-in-depth. QKD provides information-theoretic security for key exchange. But QKD requires dedicated hardware and has low key rates. ML-KEM (FIPS 203) is the fallback for key exchange. ML-DSA (FIPS 204) handles authentication because QKD alone cannot authenticate parties.

---

## 📐 Key Numbers & Formulas

- **ML-DSA-65 signature size:** 3,309 bytes
- **ML-KEM public key:** ~800 bytes
- **ML-KEM ciphertext:** ~1,600 bytes
- **SLH-DSA signature size:** ~49,000 bytes (conservative alternative)
- **Signature overhead on 1MB bundle:** 0.3%
- **Signature overhead on 100-byte command:** 3,309% (33× payload)
- **Shor's algorithm:** Breaks RSA, DH, ECC in polynomial time
- **Grover's algorithm:** Halves effective key length (AES-256 → effectively AES-128)

---

## 🔗 Standards & References

- [NIST FIPS 203 — ML-KEM (Kyber)](https://csrc.nist.gov/pubs/fips/203/final)
- [NIST FIPS 204 — ML-DSA (Dilithium)](https://csrc.nist.gov/pubs/fips/204/final)
- [NIST FIPS 205 — SLH-DSA (SPHINCS+)](https://csrc.nist.gov/pubs/fips/205/final)
- [NIST Post-Quantum Cryptography Project](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [CRYSTALS-Kyber Specification](https://pq-crystals.org/kyber/)
- [CRYSTALS-Dilithium Specification](https://pq-crystals.org/dilithium/)
- [Shor's Algorithm (1994)](https://ieeexplore.ieee.org/document/365700)

---

## 💡 How the Examiner Will Probe This

**Q: "Why does AETHERIX use both QKD and post-quantum cryptography?"**
→ Defense-in-depth. QKD provides information-theoretic security guaranteed by physics — but it requires dedicated hardware, line-of-sight, and has low key rates (1-10 bps at Mars). ML-KEM (FIPS 203) is the fallback for key exchange over any classical channel. ML-DSA (FIPS 204) handles authentication — QKD can't authenticate parties, only distribute keys. If one layer fails, the other holds.

**Q: "What's the overhead of ML-DSA signatures on bundles?"**
→ ML-DSA-65 signatures are 3,309 bytes. For a 1 MB science bundle, that's 0.3% — negligible. For a 100-byte command bundle, the signature is 33× the payload — significant. For small messages, SLH-DSA or hash-based alternatives might be better.

**Q: "What problem does Shor's algorithm create?"**
→ Shor's algorithm factors integers and solves discrete logarithms in polynomial time on a quantum computer. This breaks RSA (factoring), Diffie-Hellman (discrete log), and ECC (elliptic curve discrete log) — the three pillars of modern public-key cryptography. A large enough quantum computer could decrypt all currently captured traffic.

**Q: "What is 'harvest-now-decrypt-later'?"**
→ Adversaries record encrypted traffic today, storing it for future decryption when quantum computers mature. This means PQC migration is urgent now — data that must remain confidential for decades needs quantum-resistant encryption today.

**Q: "Why is ML-KEM considered quantum-resistant?"**
→ ML-KEM's security relies on the hardness of the Module Learning With Errors (MLWE) lattice problem. Unlike factoring or discrete logarithms, no efficient quantum algorithm is known for solving lattice problems. It's *believed* quantum-resistant — not proven, but based on the best current understanding.

---

## ✅ Self-Check Questions

1. Name the three NIST post-quantum standards and what each is used for.
2. Explain the defense-in-depth approach. Why not use just QKD or just PQC?
3. What is the signature overhead of ML-DSA-65 on a 1 MB bundle? On a 100-byte command?
4. Why can't QKD handle authentication? What does AETHERIX use instead?
5. Explain the "harvest-now-decrypt-later" threat and why it makes PQC migration urgent today.

---

## 📂 Deep Dive Resources

- **Mock interview:** `interview_prep/practice/mock_interview.md` Question 7
- **Exam topic document:** `AETHERIX.md` — Section h lists PQC standards
- **Standards compliance:** `interview_prep/topic_summaries/standards_compliance.md`
- **Standards reference page:** [Deep Space Standards](https://matx104.github.io/AETHERIX/#deep-space-standards)
- **NIST PQC page:** [csrc.nist.gov/projects/post-quantum-cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- **Live demo:** [Space Security](https://matx104.github.io/AETHERIX/#space-security) — QKD + PQC overview
