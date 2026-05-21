# NASA/JPL Technical Documents Reference

NASA and JPL technical documents, handbooks, and mission documents referenced by AETHERIX.

---

## DSN Telecommunications Link Design Handbook

- **Document**: DSN No. 810-005, Revision E
- **Title**: DSN Telecommunications Link Design Handbook
- **Year**: 2023 (ongoing revisions)
- **Source**: NASA / Jet Propulsion Laboratory, California Institute of Technology
- **Link**: https://deepspace.jpl.nasa.gov/dsndocs/810-005/

The authoritative reference for link budget design across all DSN ground stations (Goldstone, Madrid, Canberra), covering antenna gain patterns, receiver noise temperatures, transmit power specifications, and atmospheric loss models for S-band through Ka-band and optical frequencies. AETHERIX's `src/infrastructure/link_budget.py` draws methodology from this handbook for free-space path loss, received power, and link margin calculations, adapted for the 1550 nm optical wavelength used in the Earth-Mars link.

**Key Modules for AETHERIX:**
- Module 101: DSN service categories and link design process
- Module 104: 34-m BWG antenna telecommunications interfaces
- Module 105: Atmospheric and environmental attenuation models
- Module 201: Link budget equations and noise calculations

**AETHERIX Relevance**: Provides the ground-truth link budget methodology that the optical link calculator is modeled after. The Mars distance range (54.6M–401M km) and data rate targets (2–200 Mbps) in AETHERIX are calibrated against DSN capabilities documented here.

---

## Mars Reconnaissance Orbiter Telecommunications

- **Document**: JPL Article 6 (Deep Space Communications series)
- **Title**: Mars Reconnaissance Orbiter Telecommunications
- **Authors**: J. Taylor, D. K. Lee, S. Shambayati
- **Year**: 2006
- **Source**: Jet Propulsion Laboratory, Pasadena, CA
- **Link**: https://descanso.jpl.nasa.gov/DPSummary/MRO%20Telecom%20Article%206.pdf

Describes the telecommunications subsystem design and in-flight performance of the Mars Reconnaissance Orbiter (MRO), including X-band direct-to-Earth links, UHF relay links to surface assets, and the Electra software-defined radio. AETHERIX references MRO's relay architecture as a validated baseline for the Mars orbital tier in the 5-tier topology, where areostationary and polar orbit relays provide last-hop connectivity to Mars surface assets (bases, rovers, drones, sensors).

**Key Sections for AETHERIX:**
- Chapter 3: X-band link budget and data rate performance at Mars distances
- Chapter 5: UHF relay link design for surface asset communication
- Chapter 7: Electra proximal link operations and adaptive data rates

**AETHERIX Relevance**: Informs the Mars orbital tier design, particularly the relay model for surface communications and the data rate adaptation strategies used when link conditions degrade during dust storms or occultation events.

---

## LunaNet Interoperability Specification

- **Document**: NASA-SPEC-20230002, Version 5
- **Title**: LunaNet Interoperability Specification
- **Year**: 2023
- **Source**: NASA Space Communications and Navigation (SCaN) Program
- **Link**: https://www.nasa.gov/directorates/somd/space-communications-navigation-program/lunanet-interoperability-specification/

Defines the interoperability standards for LunaNet, NASA's proposed lunar communication and navigation network, including DTN-based data transport, delay-tolerant routing, and cross-support interfaces between multiple service providers. AETHERIX references LunaNet as a contemporary implementation of the same DTN architecture principles (CCSDS 734.2-B-1, BPv7) applied to a cislunar environment, providing validated design patterns for multi-node relay networks that AETHERIX extends to the Earth-Mars domain.

**Key Sections for AETHERIX:**
- Section 3: LunaNet architecture and DTN integration approach
- Section 5: Network layer services including delay-tolerant routing
- Section 7: Security services and key management for space DTN
- Appendix A: Service interface definitions and protocol bindings

**AETHERIX Relevance**: Serves as a near-term operational reference for DTN deployment. AETHERIX's hybrid optical/RF relay design and multi-tier node addressing follow patterns established in LunaNet, scaled to interplanetary distances and longer contact window intervals.

---

## Mars Communication Relay Mission Concept Study

- **Document**: JPL CL#18-2467
- **Title**: Mars Communication Relay Mission Concept Study
- **Year**: 2018
- **Source**: Jet Propulsion Laboratory, California Institute of Technology
- **Link**: Not publicly available (JPL internal document; summary in Edwards & DePaula 2007)

A mission concept study for a dedicated Mars communications relay infrastructure, evaluating orbit selection (areostationary vs. elliptical), link budgets for surface-to-orbit and orbit-to-Earth hops, and relay network sizing for projected Mars exploration data volumes. AETHERIX uses the relay sizing methodology and orbital geometry analysis from this study to define the Mars orbital tier, including the number of relay satellites, their orbital parameters, and the data throughput targets for the integrated Earth-Mars network.

**Key Topics for AETHERIX:**
- Areostationary vs. elliptical relay orbit trade-offs for Mars coverage
- Surface-to-orbit UHF/optical link budget for relay hops
- Projected data volume requirements for Mars surface assets through 2040
- Relay satellite constellation sizing and redundancy analysis

**AETHERIX Relevance**: Directly informs the Mars orbital tier design in the 5-tier topology, particularly the choice of areostationary relays for continuous surface coverage and polar orbit relays for high-latitude base support.

---

## NASA Systems Engineering Handbook

- **Document**: NASA SP-2016-6105 Rev2
- **Title**: NASA Systems Engineering Handbook
- **Year**: 2016
- **Source**: NASA Headquarters, Washington, DC
- **Link**: https://www.nasa.gov/reference/systems-engineering-handbook/

The comprehensive guide to NASA systems engineering processes, covering requirements definition, architecture design, verification and validation, risk management, and technical reviews. AETHERIX follows the systems engineering framework from this handbook for structuring the project architecture across its five modules (infrastructure, orbital, routing, security, simulation), defining interface control documents between modules, and establishing verification criteria for link budget accuracy and routing performance.

**Key Sections for AETHERIX:**
- Chapter 4: System design processes — stakeholder expectations and technical requirements
- Chapter 5: Product realization — implementation, integration, and verification
- Chapter 6: Technical management — risk management and decision analysis
- Appendix C: Requirements statement attributes and verification methods

**AETHERIX Relevance**: Provides the overarching systems engineering discipline for the project. The module decomposition (infrastructure, orbital, routing, security, simulation), interface definitions between modules, and the verification approach for link budget and routing modules follow NASA SE practices documented here.
