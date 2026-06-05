# CCSDS Standards Reference

Consultative Committee for Space Data Systems (CCSDS) Blue Books referenced by AETHERIX.

---

## CCSDS 734.0-G-1 — DTN Architecture (Rationale, Scenarios & Requirements)

- **Document**: CCSDS 734.0-G-1 (Green Book — informational)
- **Title**: Rationale, Scenarios, and Requirements for DTN in Space
- **Published**: August 2010
- **PDF**: https://public.ccsds.org/Pubs/734x0g1e1.pdf

Establishes the architectural rationale for Delay/Disruption-Tolerant Networking in
space, including the "bundle layer" that sits above transport and below applications,
the store-and-forward paradigm, and the Solar System Internetwork (SSI) concept.
AETHERIX bases its overall network architecture on this document together with the
IETF DTN architecture (RFC 4838), adopting custody transfer and the tiered topology
model for multi-hop interplanetary links.

> **Note:** the *normative* IETF DTN architecture is **RFC 4838**. This CCSDS Green
> Book is the space-specific rationale/requirements companion.

**Key Sections for AETHERIX:**
- Section 2: DTN scenarios for deep-space and near-Earth relays
- Section 3: Architectural elements (bundles, nodes, endpoints, custody)
- Section 4: Requirements for the Solar System Internetwork

---

## CCSDS 734.2-B-1 — CCSDS Bundle Protocol Specification

- **Document**: CCSDS 734.2-B-1 (Blue Book — Recommended Standard)
- **Title**: CCSDS Bundle Protocol Specification
- **Published**: September 2015
- **PDF**: https://public.ccsds.org/Pubs/734x2b1.pdf

The CCSDS profile of the DTN Bundle Protocol: encoding, processing rules, and block
structures for store-and-forward delivery. AETHERIX implements BPv7 bundles in
`src/routing/bundle.py`, using the IETF **RFC 9171** (Bundle Protocol Version 7) as
the primary normative reference and this CCSDS Blue Book as the space-systems profile
for the primary block format, endpoint-ID scheme, lifetime fields, and custody
tracking.

> **Note:** AETHERIX targets **BPv7 (RFC 9171)**. CCSDS 734.2-B-1 corresponds to the
> earlier RFC 5050-era bundle format; the two are aligned in architecture and are
> cited together for completeness.

**Key Sections for AETHERIX:**
- Section 4: Primary bundle block format and fields
- Section 4: Bundle processing control flags
- Section 5: Bundle forwarding and custody transfer
- Section 6: Administrative records

---

## RFC 9172 — Bundle Protocol Security (BPSec)

- **Document**: IETF RFC 9172 (Proposed Standard)
- **Title**: Bundle Protocol Security (BPSec)
- **Published**: January 2022
- **URL**: https://www.rfc-editor.org/rfc/rfc9172

Defines security services for the Bundle Protocol: the Block Integrity Block (BIB) and
Block Confidentiality Block (BCB) that apply integrity and confidentiality to
individual blocks within a bundle. AETHERIX references BPSec for the bundle-layer
security design, complementing the QKD-based key exchange in `src/security/qkd.py`
with block-level authentication and encryption for bundles traversing untrusted relay
nodes. Default security contexts are defined in **RFC 9173**.

> **Note:** BPSec is an **IETF** standard (there is no CCSDS 735.2-B-1 BPSec Blue
> Book). CCSDS 735.x is the *Application & Support Layer* (e.g. 735.1-B-1 is the
> **Asynchronous Message Service, AMS** — not the Bundle Protocol).

**Key Sections for AETHERIX:**
- Section 3: Security blocks (BIB, BCB) and their placement
- Section 4: Security processing at bundle acceptance and forwarding
- Section 9: Key management considerations for space DTN

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

## CCSDS 142.0-B-1 — Optical Communications Coding & Synchronization

- **Document**: CCSDS 142.0-B-1 (Blue Book — Recommended Standard)
- **Title**: Optical Communications Coding and Synchronization
- **Published**: August 2019
- **PDF**: https://public.ccsds.org/Pubs/142x0b1.pdf

Specifies channel coding and synchronization for free-space optical links: LDPC-encoded
Synchronization-Marked Codewords (SMCWs), PN spreading, and Pulse-Position Modulation
(PPM) for photon-starved deep-space regimes. Together with the optical physical layer
(141.0-B-1), AETHERIX cites this standard for the coding/sync assumptions behind the
optical link budget in `src/infrastructure/link_budget.py`.

> **Correction note:** earlier AETHERIX drafts mislabeled "CCSDS 142.0-B-2 (Space Link
> Identifiers / LNIS v5)". That document does not exist as described — 142.0 is the
> optical coding/sync standard. Node addressing in AETHERIX is handled by the BPv7
> endpoint-ID scheme (`dtn://node/service`), and CCSDS space-link/spacecraft identifiers
> are administered via the **SANA** registry (CCSDS 135.0-B family), not 142.0.

**Key Sections for AETHERIX:**
- Section 3: LDPC coding for the photon-starved optical channel
- Section 4: Synchronization-marked codewords and PN spreading
- Section 5: PPM symbol mapping and guard slots

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

---

## CCSDS 734.3-B-1 — Schedule-Aware Bundle Routing (SABR)

- **Document**: CCSDS 734.3-B-1 (Blue Book — Recommended Standard)
- **Title**: Schedule-Aware Bundle Routing (SABR)
- **Published**: July 2019
- **PDF**: https://public.ccsds.org/Pubs/734x3b1.pdf

Specifies SABR — the CCSDS routing algorithm for DTN that computes forwarding routes
from a *contact plan* (the predicted schedule of communication opportunities derived
from orbital mechanics). SABR is the standardized form of Contact Graph Routing (CGR).
**This is the baseline AETHERIX's reinforcement-learning router augments and is
benchmarked against** — SABR/CGR is deterministic and schedule-driven, while the RL
agent in `src/routing/rl_agent.py` adapts to link-quality and buffer state that a
static contact plan cannot capture.

**Key Sections for AETHERIX:**
- Section 2: Contact plan and the contact graph model
- Section 3: Route computation over scheduled contacts (CGR)
- Section 4: Route selection, and limitations AETHERIX's RL agent addresses
