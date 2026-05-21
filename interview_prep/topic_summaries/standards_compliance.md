# Standards Compliance — Topic Summary

## Why Standards Matter

AETHERIX does not operate in isolation. It must interoperate with existing infrastructure (NASA DSN, ESA ESTRACK, future LunaNet/MarsNet). Standards ensure:

1. **Interoperability** — any compliant implementation can exchange bundles with any other.
2. **Heritage** — builds on decades of space communication engineering.
3. **Verification** — compliance can be tested against a published specification.
4. **Certification** — EduQual Level 6 assesses awareness of professional standards.

## CCSDS Blue Books

The Consultative Committee for Space Data Systems (CCSDS) publishes recommended standards as "Blue Books" (approved recommendations).

### CCSDS 734.2-B-1: Delay-Tolerant Networking Architecture

Defines the DTN architecture for space: the bundle layer sits above transport protocols and below applications. Specifies the concept of regions, convergence layers, and custody transfer. AETHERIX's five-tier network topology and hop-by-hop custody model are direct applications of this architecture. Key concepts from this standard: administrative records, bundle status reports, custody signals.

### CCSDS 735.1-B-1: Bundle Protocol

Specifies the Bundle Protocol for space use, including CBOR encoding of the primary block, endpoint ID formats, bundle processing control flags, and convergence-layer service requirements. AETHERIX's `Bundle` class (`src/routing/bundle.py`) implements this: primary block with source/destination EIDs, creation timestamp, lifetime, and processing flags (0x01–0x40). The endpoint ID format `dtn://node/service` follows this standard.

### CCSDS 141.0-B-1: Optical Communications Physical Layer

Defines the physical layer for optical communications in space: wavelength selection, modulation formats, pointing/acquisition/tracking (PAT) procedures, and link budget methodology. AETHERIX's link budget calculations (`src/infrastructure/link_budget.py`) follow this standard's methodology: EIRP, FSPL, atmospheric loss, pointing loss, receiver sensitivity, and margin calculation.

### CCSDS 142.0-B-2: Space Link Identifiers (LNIS v5)

Defines the Logical Node Identification Scheme for space links. AETHERIX endpoint IDs follow LNIS v5 compliant naming: `earth.dsn.goldstone`, `mars.areo.alpha`, `transit.esl4.relay`. The standard ensures unique identification across international partners — critical when NASA, ESA, and potentially CNSA assets share a DTN.

## IETF RFCs

### RFC 9171: Bundle Protocol Version 7 (September 2022)

The IETF's DTN Working Group published BPv7 as RFC 9171. Key differences from BPv6 (the previous version):
- CBOR encoding replaces SDNV (Self-Delimiting Numeric Values).
- Simplified primary block structure.
- Block integrity and confidentiality separated into BPSec (RFC 9172).
- Extension blocks replace the previous extension mechanism.

AETHERIX implements BPv7 (not BPv6) because it is the current standard and has a cleaner security model via BPSec.

### RFC 5326: Licklider Transmission Protocol (September 2008)

LTP is the convergence layer for deep-space links. Key features:
- **Red/green segments**: red segments are acknowledged and retransmitted; green are best-effort.
- **Sessions**: each data transfer is a session with a unique session ID.
- **Report segments**: the receiver sends RS to indicate which data arrived; the sender retransmits gaps.
- **Checkpointing**: periodic checkpoints trigger reports even without errors.

AETHERIX uses LTP for all deep-space hops (Mars ↔ Lagrange ↔ Earth) and TCPCL for Earth-segment connections (DSN ↔ MOC).

### RFC 4838: DTN Architecture (April 2007)

The foundational DTN architecture document. Defines: the bundle layer as an overlay, the concept of regions with different convergence layers, custody transfer, and the security considerations unique to delay-tolerant networks. AETHERIX's network design is consistent with this architecture — the bundle layer sits above LTP/TCPCL/UDP-CL and below the application layer.

## NIST Post-Quantum Cryptography Standards

### FIPS 203: ML-KEM (Module-Lattice-Based Key Encapsulation Mechanism)

Standardised August 2024. Based on CRYSTALS-Kyber. Provides key encapsulation that is believed to be secure against quantum computer attacks. AETHERIX uses ML-KEM as a fallback key exchange when QKD is unavailable (cloud cover, equipment maintenance, link outage). ML-KEM-768 provides ~180-bit classical security equivalent.

### FIPS 204: ML-DSA (Module-Lattice-Based Digital Signature Algorithm)

Standardised August 2024. Based on CRYSTALS-Dilithium. Provides digital signatures resistant to quantum computing. AETHERIX uses ML-DSA for bundle authentication — every bundle carries a post-quantum signature verifying its source and integrity. This prevents bundle injection attacks even from adversaries with quantum computers.

### FIPS 205: SLH-DSA (Stateless Hash-Based Digital Signature Algorithm)

Based on SPHINCS+. A hash-based signature scheme with no lattice assumption — provides defence-in-depth if lattice-based cryptography is compromised. AETHERIX uses SLH-DSA as an alternative signature scheme for the highest-security bundles (P0 emergency data).

## ETSI QKD Standards

The European Telecommunications Standards Institute (ETSI) publishes QKD-related standards through its Industry Specification Group on Quantum Key Distribution:

- **ETSI TS 103 645**: QKD component characterization.
- **ETSI TS 103 724**: QKD system security requirements.

While AETHERIX is not formally certified to ETSI QKD standards (it is a research project), the QKD simulation in `src/security/qkd.py` follows the protocol definitions and security thresholds (QBER < 11%) consistent with these standards.

## Interoperability with DSN and LunaNet

AETHERIX is designed for compatibility with:

1. **NASA DSN**: Uses CCSDS-compliant bundle format, so any DSN station capable of ION-DTN (the reference BPv7 implementation) can route AETHERIX bundles. The optical ground stations follow CCSDS 141.0-B-1 PAT procedures.

2. **LunaNet** (planned): NASA's proposed lunar communication network uses the same DTN architecture (CCSDS 734.2). AETHERIX's endpoint ID scheme (`dtn://...`) is compatible. LunaNet would be an additional routing region in the DTN architecture.

3. **MarsNet** (future): Any future Mars communication infrastructure using BPv7 would interoperate with AETHERIX's Mars orbital and surface tiers. The five-tier topology can absorb additional nodes without architectural changes.

---

## Practice Questions

### Q1. "Why does AETHERIX use BPv7 instead of BPv6?"

BPv7 (RFC 9171, 2022) replaces BPv6 with several improvements: CBOR encoding is more efficient and has better tooling support than SDNV; the security model is separated into BPSec (RFC 9172) for block integrity and confidentiality, which is cleaner than BPv6's integrated security; extension blocks are more flexible. BPv6 is effectively deprecated for new implementations. The IETF DTN Working Group and CCSDS both recommend BPv7. Using BPv7 also ensures compatibility with ION-DTN 4.x (the reference implementation), which has dropped BPv6 support.

### Q2. "How does your endpoint ID scheme ensure uniqueness across international partners?"

AETHERIX follows CCSDS 142.0-B-2 (LNIS v5), which defines a hierarchical namespace: the node identifier includes a mission/operator prefix and a unique asset identifier. For example: `dtn://earth.esa.malargue/ops` vs `dtn://earth.nasa.goldstone/ops`. The scheme authority (managed by CCSDS SLS area) assigns top-level identifiers, preventing collisions. Within AETHERIX's own namespace, node IDs like `mars.surface.rover-01` are project-scoped. When interoperating with LunaNet or MarsNet, the CCSDS-assigned mission prefix ensures each project's namespace is distinct.

### Q3. "What's the difference between LTP and TCPCL, and when would you use each?"

LTP is for high-delay, scheduled-contact links (deep space). It assumes the link may be unavailable for long periods and uses link-local retransmission. TCPCL is for well-connected terrestrial links where TCP provides reliable transport. In AETHERIX: Mars → Lagrange → Earth uses LTP (minutes of delay, scheduled contacts); DSN station → Mission Operations Center uses TCPCL (millisecond delay, always-on); inter-satellite links in the LEO constellation use UDP-CL (low delay, high bandwidth, acceptable loss). The beauty of BPv7 is that the bundle layer is transport-agnostic — the same bundle traverses LTP, TCPCL, and UDP-CL hops without modification.

### Q4. "Why should an examiner trust that your post-quantum cryptography choices are sound?"

Three reasons. First, the algorithms are NIST standards (FIPS 203/204, published August 2024), selected through a 7-year public competition involving hundreds of cryptanalysts worldwide. Second, the security reductions are published in peer-reviewed papers — ML-KEM's security reduces to the Module-LWE problem, which has been studied since 2005. Third, AETHERIX uses a layered approach: QKD provides physics-guaranteed security for key exchange, ML-KEM provides a computational-security fallback, and ML-DSA provides authentication. Even if one layer is compromised, the others remain. This defence-in-depth approach is standard practice in security engineering.

### Q5. "If you had to demonstrate compliance to a CCSDS panel, what would you show?"

I would present four artefacts: (1) The BPv7 implementation in `src/routing/bundle.py` showing CBOR-encoded primary blocks, correct processing flags (0x01–0x40 per RFC 9171 §4.2.1), and LNIS v5 compliant endpoint IDs per CCSDS 142.0-B-2. (2) The LTP convergence layer usage showing red/green segment handling per RFC 5326. (3) The link budget methodology in `src/infrastructure/link_budget.py` following CCSDS 141.0-B-1's FSPL, EIRP, and margin calculation approach. (4) The five-tier DTN architecture consistent with CCSDS 734.2-B-1's region and convergence layer model. Each of these has traceability from the source code to the specific section of the standard.
