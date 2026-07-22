# Day 35: Standards Compliance — CCSDS Blue Books, IETF RFCs, NIST FIPS

## 📅 August 26, 2026

## 🎯 Learning Objective

Master the full standards landscape AETHERIX complies with — CCSDS Blue Books, IETF RFCs, and NIST post-quantum cryptography standards — and articulate *why standards compliance matters even in a research project*, directly supporting the examiner's assessment of professional engineering awareness.

---

## 📖 The Core Concept

### Why Standards Matter (Even in Research)

AETHERIX does not operate in isolation. It must interoperate with existing infrastructure (NASA DSN, ESA ESTRACK, future LunaNet/MarsNet). Standards ensure:

1. **Interoperability** — any compliant implementation can exchange bundles with any other.
2. **Heritage** — builds on decades of space communication engineering.
3. **Verification** — compliance can be tested against a published specification.
4. **Certification** — EduQual Level 6 assesses awareness of professional standards.

A research project that ignores standards proves nothing about deployability. A research project that *follows* standards demonstrates a clear path from demo to deployment — the bundle format, convergence layers, and security mechanisms are already standardised.

### CCSDS Blue Books

The Consultative Committee for Space Data Systems (CCSDS) publishes recommended standards as "Blue Books" (approved recommendations).

**CCSDS 734.2-B-1: DTN Architecture** — Defines the DTN architecture for space: the bundle layer sits above transport protocols and below applications. Specifies regions, convergence layers, and custody transfer. AETHERIX's five-tier topology and hop-by-hop custody model are direct applications.

**CCSDS 735.1-B-1: Bundle Protocol** — Specifies the Bundle Protocol for space use: CBOR encoding of the primary block, endpoint ID formats, bundle processing control flags (0x01–0x40), convergence-layer service requirements. AETHERIX's `Bundle` class implements this with source/destination EIDs, creation timestamp, lifetime, and processing flags.

**CCSDS 141.0-B-1: Optical Communications Physical Layer** — Defines wavelength selection, modulation formats, pointing/acquisition/tracking (PAT) procedures, and link budget methodology. AETHERIX's `link_budget.py` follows this standard's FSPL, EIRP, atmospheric loss, pointing loss, and margin calculation.

**CCSDS 142.0-B-2: Space Link Identifiers (LNIS v5)** — Defines the Logical Node Identification Scheme. AETHERIX endpoint IDs follow this: `earth.dsn.goldstone`, `mars.areo.alpha`, `transit.esl4.relay`.

### IETF RFCs

**RFC 9171: Bundle Protocol Version 7 (September 2022)** — The IETF's DTN Working Group published BPv7. Key improvements over BPv6:
- CBOR encoding replaces SDNV (Self-Delimiting Numeric Values)
- Simplified primary block structure
- Security separated into BPSec (RFC 9172)
- Extension blocks replace the previous extension mechanism

**RFC 5326: Licklider Transmission Protocol (September 2008)** — LTP is the convergence layer for deep-space links:
- **Red/green segments**: red segments are acknowledged and retransmitted; green are best-effort
- **Sessions**: each data transfer is a session with a unique session ID
- **Report segments**: the receiver indicates which data arrived; the sender retransmits gaps
- **Checkpointing**: periodic checkpoints trigger reports even without errors

**RFC 4838: DTN Architecture (April 2007)** — The foundational DTN architecture document: the bundle layer as an overlay, regions with different convergence layers, custody transfer, and security considerations.

**RFC 7242 / RFC 9174: TCP Convergence Layer** — TCPCL v4 is used for all terrestrial Earth-segment links where TCP provides reliable transport at millisecond delay.

### NIST Post-Quantum Cryptography Standards

**FIPS 203: ML-KEM (August 2024)** — Module-Lattice-Based Key Encapsulation Mechanism, based on CRYSTALS-Kyber. AETHERIX uses ML-KEM as a fallback key exchange when QKD is unavailable. ML-KEM-768 provides ~180-bit classical security equivalent.

**FIPS 204: ML-DSA (August 2024)** — Module-Lattice-Based Digital Signature Algorithm, based on CRYSTALS-Dilithium. AETHERIX uses ML-DSA for bundle authentication — every bundle carries a post-quantum signature. ML-DSA-65 signatures are 3,309 bytes.

**FIPS 205: SLH-DSA (August 2024)** — Stateless Hash-Based Digital Signature Algorithm, based on SPHINCS+. Provides defence-in-depth if lattice-based cryptography is compromised. Used for the highest-security bundles (P0 emergency data).

### Acknowledged Compliance Gaps

AETHERIX does **not** claim full compliance in these areas:
- **BPSec (RFC 9172)**: Not yet implemented. Bundle integrity and confidentiality blocks are planned for production.
- **LTP security (LTPLS)**: Not implemented. Deferred to production upgrade.
- **CCSDS File Delivery Protocol (CFDP)**: Not implemented. AETHERIX uses raw BPv7 bundles.
- **SLE (Space Link Extension)**: Not implemented. Direct DSN integration would require SLE service instances.

---

## 🔬 In AETHERIX

Standards compliance is woven through every module:

**`src/routing/bundle.py`**: Implements RFC 9171 / CCSDS 735.1-B-1. The `Bundle` class encodes source/destination EIDs, creation timestamp, lifetime, hop count, and processing control flags as a CBOR primary block. Flags 0x01 (IS_FRAGMENT) through 0x40 are fully implemented. `CUSTODY_REQUESTED` (0x08) enables custody transfer per RFC 9171 §4.4.

**`src/infrastructure/link_budget.py`**: Implements CCSDS 141.0-B-1. The `LinkBudgetCalculator` computes `FSPL = 20·log₁₀(4πd/λ)`, `EIRP = P_tx + G_tx`, atmospheric attenuation, pointing loss, and `Margin = P_received − P_sensitivity`.

**`src/routing/prioritization.py`**: Implements CCSDS 121.0-B-3 (lossless compression) and CCSDS 122.0-B-2 (image compression) as `CompressionProfile` ratios applied analytically.

**`src/security/qkd.py`**: Implements ETSI TS 103 645/724 compliant QKD protocol definitions with QBER < 11% threshold. FIPS 203/204/205 referenced for PQC fallback.

**Module-to-standard traceability** (full table in `standards_compliance.md`):
- `bundle.py` → CCSDS 735.1-B-1, RFC 9171
- `link_budget.py` → CCSDS 141.0-B-1, CCSDS 142.0-B-2
- `rl_agent.py` → CCSDS 734.2-B-1
- `qkd.py` → ETSI TS 103 645/724, FIPS 203/204/205

---

## 📐 Key Numbers & Formulas

| Standard | Number | AETHERIX Application |
|----------|--------|---------------------|
| CCSDS DTN Architecture | 734.2-B-1 | Five-tier topology, custody model |
| CCSDS Bundle Protocol | 735.1-B-1 | CBOR primary block, processing flags |
| CCSDS Optical Communications | 141.0-B-1 | FSPL, EIRP, link margin methodology |
| CCSDS Space Link Identifiers | 142.0-B-2 | Endpoint ID naming scheme |
| CCSDS Lossless Compression | 121.0-B-3 | Rice/adaptive telemetry compression |
| CCSDS Image Compression | 122.0-B-2 | Wavelet image compression |
| IETF BPv7 | RFC 9171 (2022) | Bundle class, flags, fragmentation |
| IETF LTP | RFC 5326 (2008) | Deep-space convergence layer |
| IETF DTN Architecture | RFC 4838 (2007) | Overlay, regions, custody |
| IETF TCPCL | RFC 9174 (2021) | Earth-segment convergence |
| NIST ML-KEM | FIPS 203 (2024) | Post-quantum key exchange fallback |
| NIST ML-DSA | FIPS 204 (2024) | Bundle authentication signatures |
| NIST SLH-DSA | FIPS 205 (2024) | Hash-based signature for P0 bundles |

---

## 🔗 Standards & References

- [CCSDS Recommendations](https://public.ccsds.org/Publications/BlueBooks.aspx) — All Blue Books
- [IETF DTN Working Group](https://datatracker.ietf.org/wg/dtn/documents/) — RFCs 9171, 5326, 4838, 9174
- [NIST PQC Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography) — FIPS 203/204/205
- [ETSI QKD Standards](https://www.etsi.org/committee/qkd) — TS 103 645/724
- **Repo:** `interview_prep/topic_summaries/standards_compliance.md` — full traceability table
- **Repo:** `docs/DESIGN_RATIONALE.md` — simulation tooling compliance section

---

## 💡 How the Examiner Will Probe This

**Q: "Which standards does AETHERIX comply with, and why is standards compliance important for a research project?"**

> Four CCSDS Blue Books: 734.2-B-1 (DTN Architecture), 735.1-B-1 (Bundle Protocol), 141.0-B-1 (Optical), 142.0-B-2 (Space Link Identifiers). Three IETF RFCs: 9171 (BPv7), 5326 (LTP), 4838 (DTN Architecture). Three NIST PQC standards: FIPS 203 (ML-KEM), 204 (ML-DSA), 205 (SLH-DSA). Standards matter because: (1) the demo reflects real-world constraints, (2) results are comparable to other DTN research, (3) it demonstrates professional awareness, (4) there's a clear path from demo to deployment.

**Q: "Why BPv7 instead of BPv6?"**

> BPv7 (RFC 9171, 2022) replaces BPv6 with CBOR encoding (more efficient, better tooling than SDNV), a cleaner security model via BPSec (RFC 9172), and more flexible extension blocks. BPv6 is effectively deprecated. The IETF DTN Working Group and CCSDS both recommend BPv7. Using it ensures compatibility with ION-DTN 4.x, the reference implementation.

**Q: "Name one thing in your implementation that doesn't fully comply with the standard."**

> The LTP convergence layer is simulated, not fully implemented. RFC 5326 specifies detailed session management, checkpoint/report segment exchanges, and timer behaviour. AETHERIX models the logical behaviour (red/green, retransmission) but doesn't implement the full state machine. For a demo, this is acceptable; for deployment, ION-DTN provides a compliant LTP implementation.

---

## ✅ Self-Check Questions

1. List the four CCSDS Blue Books AETHERIX complies with and what each covers.
2. What are the three NIST PQC standards (FIPS numbers) and their AETHERIX applications?
3. Why does AETHERIX use BPv7 rather than BPv6? Name two technical reasons.
4. Name two acknowledged compliance gaps and explain why they are deferred.
5. If you had to demonstrate CCSDS compliance to a panel, what four artefacts would you show?

---

## 📂 Deep Dive Resources

- **Topic summary:** `interview_prep/topic_summaries/standards_compliance.md` — comprehensive traceability
- **Mock interview:** Q14 in `interview_prep/practice/mock_interview.md`
- **Design decisions:** DD9 (LTP), DD10 (priority levels), DD11 (CBOR) in `interview_prep/question_bank/design_decisions.md`
- **Source code:** `src/routing/bundle.py`, `src/infrastructure/link_budget.py`, `src/security/qkd.py`
- **External:** CCSDS, IETF DTN WG, NIST PQC pages (links above)
