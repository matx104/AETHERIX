# AETHERIX Acronym Reference

Complete A-Z list of acronyms used in the AETHERIX project and interplanetary networking domain.

---

## A

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **AETHERIX** | Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange | The name of this project — an interplanetary DTN platform for Mars communication |
| **AES** | Advanced Encryption Standard | Symmetric encryption algorithm (AES-256 used in AETHERIX for data confidentiality after QKD key exchange) |
| **AO** | Adaptive Optics | Deformable mirror system that corrects atmospheric turbulence in real-time for optical ground stations |
| **APD** | Avalanche Photodiode | Semiconductor photon detector used in optical receivers (~10% quantum efficiency at 1550 nm) |
| **AU** | Astronomical Unit | 149,597,870.7 km — mean Earth-Sun distance |
| **AODV** | Ad-hoc On-Demand Distance Vector | A terrestrial ad-hoc routing protocol; not used in AETHERIX (RL replaces it) |

## B

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **BB84** | Bennett-Brassard 1984 | The first and most widely implemented QKD protocol; prepare-and-measure scheme using polarised photons |
| **BER** | Bit Error Rate | Fraction of bits received in error; deep-space optical achieves 10⁻⁶ to 10⁻⁹ after FEC |
| **BP** | Bundle Protocol | CCSDS/IETF protocol for delay-tolerant networking; BPv7 is the current version (RFC 9171) |
| **BPv7** | Bundle Protocol Version 7 | Current DTN bundle protocol standard using CBOR encoding; AETHERIX's core protocol |
| **BPSec** | Bundle Protocol Security | RFC 9172 — security extension for BPv7 providing integrity and confidentiality at the block level |
| **BSM** | Bell-State Measurement | Quantum operation in entanglement swapping; projects two qubits onto a Bell state |
| **BGP** | Border Gateway Protocol | Internet routing protocol; not used in AETHERIX but analogous to the DTN routing function |

## C

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **CBOR** | Concise Binary Object Representation | Binary data format (RFC 8949) used for BPv7 primary block encoding |
| **CCSDS** | Consultative Committee for Space Data Systems | International body that develops space communication standards (734.2, 735.1, 141.0, 142.0) |
| **CGR** | Contact Graph Routing | State-of-practice DTN routing algorithm using pre-planned contact schedules; AETHERIX fallback |
| **CHSH** | Clauser-Horne-Shimony-Holt | Bell inequality test used in E91 to verify entanglement; S > 2 confirms quantum correlations |
| **CME** | Coronal Mass Ejection | Solar event producing high-energy particles; affects radiation environment and link quality |
| **CRC** | Cyclic Redundancy Check | Error-detecting code (CRC32) used to verify bundle integrity during storage and transmission |
| **CRYSTALS** | Cryptographic Suite for Algebraic Lattices | NIST PQC family including Kyber (KEM) and Dilithium (signatures) |

## D

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **dBm** | Decibels relative to 1 milliwatt | Power measurement unit; 0 dBm = 1 mW, 37 dBm = 5 W |
| **DILITHIUM** | see ML-DSA | Lattice-based digital signature algorithm standardised as FIPS 204 |
| **DQN** | Deep Q-Network | RL algorithm using neural networks to approximate Q-values; planned AETHERIX upgrade from Q-tables |
| **DSN** | Deep Space Network | NASA's three-station (Goldstone, Madrid, Canberra) interplanetary communication system |
| **DSOC** | Deep Space Optical Communications | NASA's 2023 laser communication demonstration on the Psyche spacecraft |
| **DTN** | Delay-Tolerant Networking | Network architecture for high-delay, intermittent-connectivity environments (RFC 4838) |
| **DTLS** | Datagram Transport Layer Security | Security protocol over UDP; not used in AETHERIX (BPSec replaces it at the bundle layer) |

## E

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **E91** | Ekert 1991 | Entanglement-based QKD protocol using Bell inequality verification |
| **EDAC** | Error Detection And Correction | Hardware-level memory protection (SECDED) against radiation-induced bit flips |
| **EID** | Endpoint Identifier | BPv7 address format: `dtn://node/service` (e.g., `dtn://mars.surface.rover-01/science`) |
| **EIRP** | Effective Isotropic Radiated Power | Pt + Gt (dBm + dB); measures effective transmit power including antenna gain |
| **EPR** | Einstein-Podolsky-Rosen | Entangled particle pair used in E91 and quantum repeater protocols |
| **ES-L4** | Earth-Sun Lagrange Point 4 | 60° ahead of Earth in orbit; AETHERIX relay and quantum repeater location |
| **ES-L5** | Earth-Sun Lagrange Point 5 | 60° behind Earth in orbit; AETHERIX relay and quantum repeater location |
| **ESA** | European Space Agency | European space organisation; ESTRACK is ESA's equivalent of DSN |
| **ETSI** | European Telecommunications Standards Institute | Standards body publishing QKD specifications (TS 103 645, TS 103 724) |

## F

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **FEC** | Forward Error Correction | Error correction applied at the transmitter (LDPC codes); avoids retransmission delay |
| **FIPS** | Federal Information Processing Standards | NIST standards; FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA) |
| **FSPL** | Free Space Path Loss | Signal attenuation over distance in vacuum: 20·log₁₀(4πd/λ); 353–370 dB for Earth-Mars optical |
| **FWHM** | Full Width at Half Maximum | Measure of laser beam width or detector timing resolution |

## G

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **GEO** | Geostationary Earth Orbit | 35,786 km altitude; appears stationary over equator; AETHERIX uses 3 GEO relays |
| **GCR** | Galactic Cosmic Rays | Background radiation contributing to long-term electronics degradation |
| **GM** | Gravitational Parameter | μ = GM; μ_Sun = 1.327×10²⁰ m³/s²; used in orbital period calculations |

## H

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **HALO** | High Altitude Long Operation | Not used in AETHERIX; listed for completeness |

## I

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **IETF** | Internet Engineering Task Force | Standards body publishing RFC 9171 (BPv7), RFC 5326 (LTP), RFC 4838 (DTN Architecture) |
| **ION** | Interplanetary Overlay Network | JPL's open-source BPv7 implementation; reference DTN software stack |
| **ISL** | Inter-Satellite Link | Direct communication between satellites; 1–10 Gbps optical ISL in AETHERIX LEO constellation |
| **ISS** | International Space Station | Orbital laboratory at 400 km; not part of AETHERIX architecture |

## J

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **JPL** | Jet Propulsion Laboratory | NASA centre managing DSN, DSOC, and Mars missions; operates ION-DTN software |

## K

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **KEM** | Key Encapsulation Mechanism | Asymmetric cryptographic primitive for key exchange; ML-KEM (Kyber) is the NIST standard |
| **KYBER** | see ML-KEM | Lattice-based KEM standardised as FIPS 203; used in AETHERIX for PQC key exchange fallback |
| **CK** | Csiszár-Körner | Theorem establishing the secrecy capacity of a wiretap channel; bounds privacy amplification compression ratio |

## L

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **LDPC** | Low-Density Parity Check | Powerful FEC code used in optical communications; ~0.8 dB from Shannon limit |
| **LEO** | Low Earth Orbit | 200–2,000 km altitude; AETHERIX uses 48 LEO satellites for ISL mesh |
| **LNIS** | Logical Node Identification Scheme | CCSDS 142.0-B-2 standard for unique space link identifiers; v5 used in AETHERIX |
| **LTP** | Licklider Transmission Protocol | Deep-space convergence layer (RFC 5326) with red/green segments and link-local retransmission |
| **LUKE** | LEO-to-User Ka-band Enhanced | Hypothetical link type; not a formal AETHERIX component |

## M

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **ML-DSA** | Module-Lattice Digital Signature Algorithm | NIST PQC signature standard (FIPS 204); based on Dilithium; used for bundle authentication in AETHERIX |
| **ML-KEM** | Module-Lattice Key Encapsulation Mechanism | NIST PQC KEM standard (FIPS 203); based on Kyber; AETHERIX fallback key exchange |
| **MOC** | Mission Operations Center | Ground facility controlling spacecraft; receives data from DSN stations via TCPCL |
| **MRO** | Mars Reconnaissance Orbiter | NASA spacecraft currently serving as a Mars communication relay (6 Mbps RF) |

## N

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **NIST** | National Institute of Standards and Technology | US standards body; published FIPS 203/204/205 for post-quantum cryptography |
| **ns-3** | Network Simulator 3 | Discrete-event network simulator; planned for AETHERIX integration |
| **NTP** | Network Time Protocol | Clock synchronisation protocol; insufficient for interplanetary timing (assumes low delay) |

## O

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **OMNeT++** | Objective Modular Network Testbed in C++ | Network simulation framework; alternative to ns-3 for AETHERIX |
| **OWLT** | One-Way Light Time | Signal propagation time between two nodes; 3.0–22.3 min for Earth-Mars |

## P

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **PAT** | Pointing, Acquisition, and Tracking | Procedure for establishing and maintaining optical link alignment |
| **PQC** | Post-Quantum Cryptography | Algorithms believed secure against quantum computers (ML-KEM, ML-DSA, SLH-DSA) |
| **PPO** | Proximal Policy Optimisation | Advanced RL algorithm; potential upgrade path beyond DQN for AETHERIX |
| **PSK** | Pre-Shared Key | Symmetric key distributed before communication; used as initial key for QKD authentication |

## Q

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **QBER** | Quantum Bit Error Rate | Error rate in sifted QKD key; must be <11% (Shor-Preskill threshold) for security |
| **QKD** | Quantum Key Distribution | Physics-based key exchange protocol (BB84, E91); information-theoretically secure |
| **QoS** | Quality of Service | Traffic prioritisation; AETHERIX uses 5 priority levels (P0–P4) |
| **Q-table** | Quality Table | Tabular storage of state-action values in Q-learning; AETHERIX demo RL implementation |

## R

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **RAD750** | Radiation-hardened 750 | BAE Systems radiation-hardened processor; 10× more SEU-resistant than commercial parts |
| **RF** | Radio Frequency | Electromagnetic communication (Ka-band at 32 GHz); AETHERIX backup link |
| **RFC** | Request for Comments | IETF standards documents; RFC 9171 (BPv7), RFC 5326 (LTP), RFC 4838 (DTN) |
| **RL** | Reinforcement Learning | Machine learning paradigm where an agent learns optimal actions through reward signals |
| **RTG** | Radioisotope Thermoelectric Generator | Nuclear power source for deep-space missions; potential power source for Lagrange relays |
| **RTLT** | Round-Trip Light Time | 2× OWLT; 6.0–44.6 min for Earth-Mars |
| **RTO** | Retransmission Timeout | Time after which unacknowledged data is retransmitted |

## S

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **SECDED** | Single Error Correction, Double Error Detection | EDAC code protecting each memory word against radiation-induced bit flips |
| **SEL** | Single-Event Latchup | Radiation-induced short circuit; requires power cycle to clear |
| **SEU** | Single-Event Upset | Radiation-induced bit flip in memory or logic; mitigated by EDAC and TMR |
| **SGP4** | Simplified General Perturbations 4 | Orbital propagation algorithm using TLE inputs; used for LEO satellite tracking |
| **SDP4** | Simplified Deep-space Perturbations 4 | SGP4 variant for deep-space (high-eccentricity) orbits |
| **SLH-DSA** | Stateless Hash-Based Digital Signature Algorithm | NIST PQC standard (FIPS 205); based on SPHINCS+; AETHERIX backup signature scheme |
| **SNR** | Signal-to-Noise Ratio | Ratio of signal power to noise power; determines achievable data rate via Shannon capacity |
| **SNSPD** | Superconducting Nanowire Single-Photon Detector | High-efficiency (~80%) photon detector for optical ground stations |
| **SPHINCS+** | see SLH-DSA | Hash-based signature scheme; no lattice assumption for defence-in-depth |
| **SSP** | Sub-Satellite Point | Ground point directly below a satellite |

## T

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **TCP** | Transmission Control Protocol | Reliable Internet transport; unsuitable for interplanetary use due to delay assumptions |
| **TCPCL** | TCP Convergence Layer | BPv7 convergence layer adapter for TCP transport (RFC 7242); used in AETHERIX Earth segment |
| **TLE** | Two-Line Element | Orbital element format for SGP4 propagation; publicly available from Space Track |
| **TMR** | Triple Modular Redundancy | Hardware fault tolerance: three identical circuits with majority voting |
| **TRL** | Technology Readiness Level | NASA scale (1–9) measuring technology maturity; optical space links at TRL 7–8, RF at TRL 9 |

## U

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **UDP** | User Datagram Protocol | Connectionless transport; used in AETHERIX's UDP-CL for optical ISL |
| **UDP-CL** | UDP Convergence Layer | BPv7 convergence layer for low-overhead, high-throughput links |

## V

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **VANET** | Vehicular Ad-hoc Network | Not used in AETHERIX; DTN concepts apply to vehicle networks |

## W

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **WDM** | Wavelength Division Multiplexing | Multiple wavelengths on one fibre; potential upgrade for ISL capacity |

## X–Z

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **Z-basis** | Rectilinear (Computational) Basis | QKD measurement basis: |0⟩ and |1⟩ states |
| **X-basis** | Diagonal (Hadamard) Basis | QKD measurement basis: |+⟩ and |−⟩ states |

---

## New Acronyms (Extended Capabilities)

| Acronym | Expansion | Definition |
|---------|-----------|------------|
| **LTP** | Licklider Transmission Protocol | Deep-space convergence layer (RFC 5326) with red/green segments and link-local retransmission; implemented in AETHERIX's LTP convergence layer module |
| **TCPCL** | TCP Convergence Layer | BPv7 convergence layer for TCP transport (RFC 7242); used for Earth-segment DSN links |
| **UDP-CL** | UDP Convergence Layer | BPv7 convergence layer for low-overhead, high-throughput links; used for optical inter-satellite links |
| **BFS** | Breadth-First Search | Graph traversal algorithm used in AETHERIX's forwarding engine as shortest-path fallback when RL Q-values are unavailable |
| **CASCADE** | CASCADE Protocol | Interactive bit-level error correction protocol for QKD key reconciliation; implemented in AETHERIX's security module |
| **CK** | Csiszár-Körner | Foundational theorem bounding the secrecy capacity of wiretap channels; used for privacy amplification parameter selection |
| **DQN** | Deep Q-Network | RL architecture using neural network function approximation; planned upgrade from tabular Q-learning in AETHERIX |
| **MADQN** | Multi-Agent Deep Q-Network | Multi-agent extension of DQN for distributed routing; AETHERIX's target architecture for federated RL training |
