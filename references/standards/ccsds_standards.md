# CCSDS Standards Reference

Consultative Committee for Space Data Systems (CCSDS) Blue Books referenced by AETHERIX.

---

## CCSDS 734.2-B-1 — Delay-Tolerant Networking Architecture

- **Document**: CCSDS 734.2-B-1 (Blue Book)
- **Title**: Delay-Tolerant Networking (DTN) Architecture
- **Published**: November 2015
- **PDF**: https://public.ccsds.org/Pubs/734x2b1.pdf

Defines the overall DTN architecture for space communications, including the concept of a "bundle layer" that sits above transport protocols and below applications. AETHERIX bases its entire network architecture on this document, adopting the store-and-forward paradigm, custody transfer, and the tiered topology model described for multi-hop interplanetary links.

**Key Sections for AETHERIX:**
- Section 3: DTN architectural elements (bundles, nodes, endpoints)
- Section 4: Bundle layer services and custody transfer semantics
- Section 5: Convergence layer adapters and their role in heterogeneous links

---

## CCSDS 735.1-B-1 — Bundle Protocol Specification

- **Document**: CCSDS 735.1-B-1 (Blue Book)
- **Title**: Bundle Protocol Specification
- **Published**: September 2020
- **PDF**: https://public.ccsds.org/Pubs/735x1b1.pdf

Specifies the Bundle Protocol (BP) encoding, processing rules, and block structures for DTN. AETHERIX implements BPv7 bundles in `src/routing/bundle.py`, using this standard as the authoritative reference for the primary block format, endpoint ID scheme, lifetime fields, and custody tracking mechanisms.

**Key Sections for AETHERIX:**
- Section 4.2: Primary bundle block format and fields
- Section 4.3: Bundle processing control flags
- Section 5: Bundle routing and forwarding rules
- Section 6: Custody transfer and administrative records

---

## CCSDS 735.2-B-1 — Bundle Protocol Security (BPSec)

- **Document**: CCSDS 735.2-B-1 (Blue Book)
- **Title**: Bundle Protocol Security (BPSec)
- **Published**: October 2022
- **PDF**: https://public.ccsds.org/Pubs/735x2b1.pdf

Defines security services for the Bundle Protocol, including integrity and confidentiality security blocks that can be applied to individual blocks within a bundle. AETHERIX references BPSec for the security layer design, complementing the QKD-based key exchange in `src/security/qkd.py` with block-level authentication and encryption for bundles traversing untrusted relay nodes.

**Key Sections for AETHERIX:**
- Section 3: Security block types (BIB, BCB) and their placement
- Section 4: Security processing at bundle acceptance and forwarding
- Section 5: Key management considerations for space DTN

---

## CCSDS 734.1-B-1 — Licklider Transmission Protocol

- **Document**: CCSDS 734.1-B-1 (Blue Book)
- **Title**: Licklider Transmission Protocol (LTP) for CCSDS
- **Published**: May 2015
- **PDF**: https://public.ccsds.org/Pubs/734x1b1.pdf

Specifies LTP as a convergence-layer protocol designed for deep-space links with long round-trip times and intermittent connectivity. AETHERIX uses LTP as the underlying reliable transport beneath the Bundle Protocol, providing segmentation, retransmission, and session management for the long-delay Earth-Mars link where TCP is infeasible.

**Key Sections for AETHERIX:**
- Section 3: LTP session model and data segment structures
- Section 5: Retransmission and reliability mechanisms for long-delay links
- Section 7: Convergence with the Bundle Protocol (BP-LTP adapter)

---

## CCSDS 142.0-B-2 — Space Link Identification (LNIS v5)

- **Document**: CCSDS 142.0-B-2 (Blue Book)
- **Title**: Space Data Link Protocols — Conventions and Procedures for Space Link Identification
- **Published**: November 2021
- **PDF**: https://public.ccsds.org/Pubs/142x0b2.pdf

Standardizes space link identifiers and the Logical Node Identification Scheme (LNIS) v5, used to uniquely identify spacecraft, ground stations, and relay nodes across the CCSDS framework. AETHERIX adopts the LNIS addressing conventions to assign unique identifiers to each node in the 5-tier topology (Earth ground, Earth orbital, deep-space transit, Mars orbital, Mars surface).

**Key Sections for AETHERIX:**
- Section 3: Space link identifier structure and assignment
- Section 4: LNIS v5 node identification format
- Section 5: Cross-support identification for multi-agency interoperability

---

## CCSDS 141.0-B-1 — Optical Communications Physical Layer

- **Document**: CCSDS 141.0-B-1 (Blue Book)
- **Title**: Optical Communications Physical Layer
- **Published**: August 2019
- **PDF**: https://public.ccsds.org/Pubs/141x0b1.pdf

Defines the physical layer specifications for free-space optical communications in space, including modulation formats, coding schemes, and link parameters. AETHERIX uses this standard as the basis for the optical link budget calculations in `src/infrastructure/link_budget.py`, particularly for the 1550 nm wavelength parameters, receiver sensitivity models, and atmospheric attenuation factors.

**Key Sections for AETHERIX:**
- Section 3: Optical link parameters and wavelength selection
- Section 4: Modulation and coding for deep-space optical links
- Section 5: Link budget methodology and margin requirements

---

## CCSDS 131.0-B-4 — TM Synchronization and Channel Coding

- **Document**: CCSDS 131.0-B-4 (Blue Book)
- **Title**: TM Synchronization and Channel Coding
- **Published**: September 2023
- **PDF**: https://public.ccsds.org/Pubs/131x0b4.pdf

Specifies synchronization, channel coding, and frame structures for telemetry (TM) space data links. AETHERIX references this standard for the RF fallback link design, where telemetry frames must be encoded and synchronized for reliable transmission during optical link outages or high-attenuation scenarios such as solar conjunction.

**Key Sections for AETHERIX:**
- Section 3: Transfer frame structure and synchronization
- Section 4: Channel coding schemes (Reed-Solomon, convolutional, LDPC)
- Section 5: RF link performance under degraded conditions

---

## CCSDS 910.11-B-1 — Cross Support Service Management

- **Document**: CCSDS 910.11-B-1 (Blue Book)
- **Title**: Cross Support Service Management — Service Specification
- **Published**: August 2018
- **PDF**: https://public.ccsds.org/Pubs/910x11b1.pdf

Defines service management interfaces for cross-support between space agencies, allowing one agency's ground station to communicate with another agency's spacecraft. AETHERIX references this standard for the multi-agency DSN interoperability model, where the three DSN complexes (Goldstone, Madrid, Canberra) may provide cross-support relay services during Mars-Earth communication windows.

**Key Sections for AETHERIX:**
- Section 3: Service management framework and interface definitions
- Section 4: Cross-support agreements and service-level parameters
- Section 5: Scheduling and allocation of ground station resources
