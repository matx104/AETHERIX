# IETF RFCs Reference

Internet Engineering Task Force (IETF) Request for Comments documents referenced by AETHERIX.

---

## RFC 9171 — Bundle Protocol Version 7

- **RFC**: 9171
- **Title**: Bundle Protocol Version 7
- **Published**: January 2022
- **Authors**: S. Burleigh (IPNGROUP), K. Fall (NASA/Ames), E. J. Birrane III (JHU/APL)
- **Link**: https://www.rfc-editor.org/rfc/rfc9171
- **Status**: Standards Track (Proposed Standard)

The core Bundle Protocol specification for DTN, defining the BPv7 bundle format, endpoint ID scheme, processing rules, and administrative record types. This is the primary protocol standard implemented in AETHERIX's `src/routing/bundle.py`, governing how data is encapsulated into self-delimiting bundles with source/destination endpoint IDs, lifetime constraints, hop-by-hop custody tracking, and priority classification (bulk, normal, expedited, etc.).

**Key Sections for AETHERIX:**
- Section 4.2.1: Primary block fields (destination, source, report-to, custodian)
- Section 4.3: Bundle processing control flags (custody transfer, status reports)
- Section 5.2–5.6: Forwarding, delivery, and custody acceptance procedures
- Section 4.2.2: CRC types and integrity verification

---

## RFC 5326 — Licklider Transmission Protocol Specification

- **RFC**: 5326
- **Title**: Licklider Transmission Protocol — Specification
- **Published**: September 2008
- **Authors**: M. Ramadas (Ohio Univ.), S. Burleigh (IPNGROUP), S. Farrell (Trinity College Dublin)
- **Link**: https://www.rfc-editor.org/rfc/rfc5326
- **Status**: Standards Track (Proposed Standard)

Specifies LTP as a reliable convergence-layer protocol for links with very long round-trip times (minutes to hours) and intermittent connectivity. AETHERIX uses LTP beneath the Bundle Protocol to provide guaranteed delivery over the Earth-Mars link, leveraging its checkpoint/retransmission mechanism, session-oriented segmentation, and ability to suspend and resume sessions during contact window interruptions.

**Key Sections for AETHERIX:**
- Section 4: LTP data structures (sessions, segments, reception claims)
- Section 6: Retransmission and reliability procedures for long-delay links
- Section 8: Convergence-layer adapter interface to the Bundle Protocol
- Section 10: Security considerations including authentication and replay protection

---

## RFC 4838 — Delay-Tolerant Networking Architecture

- **RFC**: 4838
- **Title**: Delay-Tolerant Networking Architecture
- **Published**: April 2007
- **Authors**: V. Cerf (Google), S. Burleigh (JPL), A. Hooke (JPL), L. Torgerson (JPL), R. Durst (SIG), K. Scott (JPL), K. Fall (Intel Research), H. Weiss (SPARTA)
- **Link**: https://www.rfc-editor.org/rfc/rfc4838
- **Status**: Informational

The foundational DTN architecture document, establishing the concept of a bundle layer that operates above heterogeneous transport protocols and below applications, enabling communication across partitioned and intermittently connected networks. AETHERIX's entire architecture is grounded in this document, adopting the store-and-forward model, custody-based reliability, endpoint ID naming scheme, and the principle of late binding of addresses at each hop.

**Key Sections for AETHERIX:**
- Section 3: Architecture overview — bundle layer positioning and store-and-forward
- Section 4: Endpoint IDs and naming in DTN
- Section 7: Custody transfer and reliable delivery semantics
- Section 8: Security architecture considerations for DTN

---

## RFC 9172 — Bundle Protocol Security (BPSec)

- **RFC**: 9172
- **Title**: Bundle Protocol Security (BPSec)
- **Published**: June 2022
- **Authors**: E. J. Birrane III (JHU/APL), K. McKeever (JHU/APL)
- **Link**: https://www.rfc-editor.org/rfc/rfc9172
- **Status**: Standards Track (Proposed Standard)

Specifies security blocks for the Bundle Protocol, providing integrity (Block Integrity Block — BIB) and confidentiality (Block Confidentiality Block — BCB) services at the bundle-block level. While AETHERIX currently focuses on QKD-based key exchange in `src/security/qkd.py`, BPSec is the complementary standard for applying authenticated encryption to individual blocks within a bundle, protecting against tampering and eavesdropping at relay nodes in the 5-tier topology.

**Key Sections for AETHERIX:**
- Section 3: Security block types and operational semantics
- Section 4: Security processing at accept, forward, and deliver stages
- Section 5: Key management and security context parameters

---

## RFC 7242 — Delay-Tolerant Networking TCP Convergence Layer Protocol

- **RFC**: 7242
- **Title**: Delay-Tolerant Networking TCP Convergence Layer Protocol
- **Published**: August 2014
- **Authors**: M. Demmer (UC Berkeley), J. Ott (TU Berlin), S. Perreault (Viagenie)
- **Link**: https://www.rfc-editor.org/rfc/rfc7242
- **Status**: Standards Track (Proposed Standard)

Defines the TCP convergence layer (TCPCL) for Bundle Protocol, providing reliable segment-based transport over TCP connections with session establishment, length-prefixed data segments, and session teardown procedures. AETHERIX uses TCPCL for Earth-segment links (DSN stations to Mission Operations Centers) where terrestrial-scale round-trip times allow TCP's congestion control to operate effectively. TCPCL complements LTP: LTP handles the deep-space hop (Earth orbital to Mars orbital), while TCPCL handles the terrestrial distribution hop.

**Key Sections for AETHERIX:**
- Section 4: TCPCL session establishment and parameter negotiation
- Section 5: Data segment transmission with length-prefix framing
- Section 6: Session termination and idle handling
- Section 7: Security considerations including TLS integration

---

## RFC 9174 — Delay-Tolerant Networking LTP Convergence-Layer Adapter

- **RFC**: 9174
- **Title**: Delay-Tolerant Networking Licklider Transmission Protocol (LTP) Convergence-Layer Adapter
- **Published**: January 2023
- **Authors**: S. Burleigh (IPNGROUP)
- **Link**: https://www.rfc-editor.org/rfc/rfc9174
- **Status**: Standards Track (Proposed Standard)

Specifies the convergence-layer adapter that maps BPv7 bundle transfer operations onto LTP sessions, defining how bundles are segmented into LTP blocks (red-part for reliable delivery, green-part for best-effort) and how custody transfer acknowledgments map to LTP reception claims. AETHERIX's LTP convergence layer implements this adapter, using red-part segments for high-priority bundles (P0-P2) requiring guaranteed delivery and green-part segments for bulk data (P3-P4) where retransmission overhead is not justified.

**Key Sections for AETHERIX:**
- Section 3: Bundle-to-LTP-block mapping and segmentation rules
- Section 4: Red-part vs green-part handling for different priority classes
- Section 5: Custody transfer interaction with LTP session management
- Section 6: Flow control and buffer management for long-delay links
