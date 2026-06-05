#!/usr/bin/env python3
"""Generate a JSON quiz bank from an embedded AETHERIX fact base.

Run from repo root:
    python interview_prep/question_bank/build_bank.py
"""

from __future__ import annotations

import json
import math
import os
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_PATH = REPO_ROOT / "docs" / "data" / "quiz_bank.json"

SEED = 42
rng = random.Random(SEED)

# ---------------------------------------------------------------------------
# Fact base
# ---------------------------------------------------------------------------

FACT_BASE: list[dict[str, Any]] = []

def _f(
    fid: str,
    topic: str,
    text: str,
    numeric_value: Optional[float] = None,
    unit: Optional[str] = None,
) -> dict[str, Any]:
    entry = {"id": fid, "topic": topic, "text": text}
    if numeric_value is not None:
        entry["numeric_value"] = numeric_value
    if unit is not None:
        entry["unit"] = unit
    FACT_BASE.append(entry)
    return entry

# ===== DTN Protocols (~40 facts) ==========================================

_f("dtn-001", "dtn_protocols",
   "Bundle Protocol v7 (RFC 9171) uses store-and-forward semantics to cope with long propagation delays and intermittent links.",
   None, None)
_f("dtn-002", "dtn_protocols",
   "BPv7 defines four priority classes: bulk, normal, expedited, and administrative.",
   4, "priority classes")
_f("dtn-003", "dtn_protocols",
   "BPv7 custody transfer delegates responsibility for bundle delivery to an intermediate node, reducing retransmission overhead.",
   None, None)
_f("dtn-004", "dtn_protocols",
   "A BPv7 bundle has a default lifetime of 604800 seconds (7 days) unless overridden by the application.",
   604800, "seconds")
_f("dtn-005", "dtn_protocols",
   "BPv7 bundles consist of at least two blocks: a primary block (routing metadata) and a payload block.",
   2, "minimum blocks")
_f("dtn-006", "dtn_protocols",
   "The primary block of a BPv7 bundle contains the source endpoint ID, destination endpoint ID, creation timestamp, and lifetime.",
   None, None)
_f("dtn-007", "dtn_protocols",
   "BPv7 convergence layers adapt the bundle protocol to underlying transport mechanisms such as TCP, UDP, or LTP.",
   None, None)
_f("dtn-008", "dtn_protocols",
   "The Licklider Transmission Protocol (LTP), defined in RFC 5326, provides reliable transmission over links with very long round-trip times.",
   None, None)
_f("dtn-009", "dtn_protocols",
   "LTP segments data into two types: green segments (best-effort, no retransmission) and red segments (reliable, with retransmission).",
   2, "segment types")
_f("dtn-010", "dtn_protocols",
   "LTP uses a selective retransmission mechanism where only missing segments are retransmitted, not the entire block.",
   None, None)
_f("dtn-011", "dtn_protocols",
   "TCP Convergence Layer (TCPCL), defined in RFC 7242, manages session establishment, keep-alive, and bundle transfer over TCP.",
   None, None)
_f("dtn-012", "dtn_protocols",
   "TCPCL v4 supports bundle segmentation, allowing large bundles to be transferred in smaller segments over a TCP session.",
   None, None)
_f("dtn-013", "dtn_protocols",
   "DTN architecture (RFC 4838) was designed because TCP/IP fails in space due to high latency, intermittent connectivity, and asymmetric links.",
   None, None)
_f("dtn-014", "dtn_protocols",
   "TCP assumes a maximum round-trip time of approximately 60 seconds before connection timeout, which is far too short for interplanetary links.",
   60, "seconds")
_f("dtn-015", "dtn_protocols",
   "Schedule-Aware Bundle Routing (SABR), defined in CCSDS 734.3-B-1, uses pre-computed contact schedules to route bundles through DTN networks.",
   None, None)
_f("dtn-016", "dtn_protocols",
   "SABR requires a Contact Plan that specifies when each contact occurs, its origin, destination, start time, duration, and data rate.",
   None, None)
_f("dtn-017", "dtn_protocols",
   "Contact Graph Routing (CGR) computes paths through the contact graph from source to destination, selecting the earliest-delivery route.",
   None, None)
_f("dtn-018", "dtn_protocols",
   "BPv7 endpoint IDs follow the URI scheme 'dtn://' or 'ipn://' where 'ipn' uses integer node and service numbers.",
   None, None)
_f("dtn-019", "dtn_protocols",
   "BPv7 administrative records include bundle status reports: received, forwarded, delivered, and deleted.",
   4, "status report types")
_f("dtn-020", "dtn_protocols",
   "The Bundle Protocol Security (BPSec) specification (RFC 9172) defines integrity and confidentiality security blocks for bundles.",
   None, None)
_f("dtn-021", "dtn_protocols",
   "BPSec defines two security block types: the Block Integrity Block (BIB) for authentication and the Block Confidentiality Block (BCB) for encryption.",
   2, "security block types")
_f("dtn-022", "dtn_protocols",
   "In BPv7, the hop count extension block limits the number of times a bundle can be forwarded, preventing infinite loops.",
   None, None)
_f("dtn-023", "dtn_protocols",
   "The ION-DTN implementation, developed by JPL, is the reference open-source BPv7 stack used in many space missions.",
   None, None)
_f("dtn-024", "dtn_protocols",
   "DTN custody-based routing allows bundles to be acknowledged hop-by-hop so the source can release buffer space before end-to-end delivery.",
   None, None)
_f("dtn-025", "dtn_protocols",
   "BPv7 bundles can be fragmented at intermediate nodes when downstream contacts are too short for the full bundle.",
   None, None)
_f("dtn-026", "dtn_protocols",
   "The previous hop insertion block in BPv7 prevents routing loops by recording the last node that forwarded the bundle.",
   None, None)
_f("dtn-027", "dtn_protocols",
   "LTP defines four session states: idle, receiving, sending, and completed.",
   4, "session states")
_f("dtn-028", "dtn_protocols",
   "LTP uses sequence numbers starting at 0 for the first byte of a block, with the upper bound defined by the block size.",
   0, "starting sequence number")
_f("dtn-029", "dtn_protocols",
   "BPv7 defines the bundle age block to track the elapsed time since bundle creation, useful when clocks are not synchronized.",
   None, None)
_f("dtn-030", "dtn_protocols",
   "The DTN custody transfer enhancement uses return receipts to confirm that a custodial node has accepted responsibility for a bundle.",
   None, None)
_f("dtn-031", "dtn_protocols",
   "LTP report segments acknowledge received byte ranges and request retransmission of missing ranges.",
   None, None)
_f("dtn-032", "dtn_protocols",
   "LTP supports checkpoint segments that require explicit acknowledgment from the receiver, enabling reliable data transfer.",
   None, None)
_f("dtn-033", "dtn_protocols",
   "The TCPCL session establishment exchange includes a contact header with version, keep-alive interval, and segment MRU (maximum receive unit).",
   None, None)
_f("dtn-034", "dtn_protocols",
   "BPv7 bundle fragmentation produces two new bundles whose payload blocks concatenate to form the original payload.",
   2, "fragment bundles")
_f("dtn-035", "dtn_protocols",
   "CCSDS File Delivery Protocol (CFDP) can operate over BPv7, providing reliable file transfer with class 1 (unreliable) and class 2 (reliable) service.",
   2, "CFDP classes")
_f("dtn-036", "dtn_protocols",
   "In DTN, the Voluntary Bundle Transfer (VBT) time is the earliest time a bundle can be forwarded on a given contact.",
   None, None)
_f("dtn-037", "dtn_protocols",
   "The earliest transmission time for a bundle through a contact graph path is computed using the Earliest Transmission Task (ETT) algorithm.",
   None, None)
_f("dtn-038", "dtn_protocols",
   "AETHERIX replaces static CGR with reinforcement learning routing that adapts to dynamic conditions such as variable link quality and buffer occupancy.",
   None, None)
_f("dtn-039", "dtn_protocols",
   "BPv7 allows extension blocks to be inserted between the primary block and payload block, enabling features like flow labeling and stream ordering.",
   None, None)
_f("dtn-040", "dtn_protocols",
   "LTP has a nominal retransmission timer calculated from the estimated round-trip time plus a safety margin, defaulting to 2 times the one-way light time plus processing.",
   None, None)

# ===== Quantum Communications (~40 facts) =================================

_f("qkd-001", "quantum_comms",
   "The BB84 protocol, proposed by Bennett and Brassard in 1984, uses four polarization states in two conjugate bases (rectilinear and diagonal).",
   4, "polarization states")
_f("qkd-002", "quantum_comms",
   "In BB84, each photon is encoded in one of two bases: the rectilinear basis (+) using 0° and 90°, or the diagonal basis (×) using 45° and 135°.",
   2, "bases")
_f("qkd-003", "quantum_comms",
   "BB84 sifting retains approximately 50% of detected bits because sender and receiver bases match only about half the time.",
   50, "percent")
_f("qkd-004", "quantum_comms",
   "The Quantum Bit Error Rate (QBER) threshold for detecting an eavesdropper in BB84 is approximately 11%.",
   11, "percent")
_f("qkd-005", "quantum_comms",
   "The no-cloning theorem states that it is impossible to create an identical copy of an arbitrary unknown quantum state, forming the security basis of QKD.",
   None, None)
_f("qkd-006", "quantum_comms",
   "The E91 protocol, proposed by Ekert in 1991, uses entangled photon pairs and Bell inequality violations to detect eavesdropping.",
   1991, "year")
_f("qkd-007", "quantum_comms",
   "A Bell state (EPR pair) is a maximally entangled two-qubit state; there are four Bell states.",
   4, "Bell states")
_f("qkd-008", "quantum_comms",
   "The CHSH form of the Bell inequality has a classical bound of 2 and a quantum maximum of 2√2 ≈ 2.828.",
   2.828, "quantum CHSH maximum")
_f("qkd-009", "quantum_comms",
   "Quantum repeaters extend QKD range by performing entanglement swapping between adjacent segments, creating entanglement over longer distances.",
   None, None)
_f("qkd-010", "quantum_comms",
   "Entanglement swapping connects two entangled pairs (A-B and C-D) by performing a Bell-state measurement on B and C, entangling A and D.",
   None, None)
_f("qkd-011", "quantum_comms",
   "Quantum repeater fidelity decreases with the number of segments; purification protocols distill higher-fidelity pairs from multiple lower-fidelity ones.",
   None, None)
_f("qkd-012", "quantum_comms",
   "Privacy amplification uses universal hashing to reduce the partial information an eavesdropper might have, shortening the key by the estimated leaked bits.",
   None, None)
_f("qkd-013", "quantum_comms",
   "CASCADE is a bit-level error reconciliation protocol that corrects discrepancies between Alice's and Bob's sifted keys through parity checks.",
   None, None)
_f("qkd-014", "quantum_comms",
   "BB84 with ideal single-photon sources and infinite-key assumptions achieves a secret key rate equal to the detected sifted bit rate times (1 - h(QBER)), where h is the binary entropy.",
   None, None)
_f("qkd-015", "quantum_comms",
   "Fiber-based QKD systems have a practical distance limit of approximately 100-400 km due to photon loss in optical fiber (0.2 dB/km at 1550 nm).",
   0.2, "dB/km")
_f("qkd-016", "quantum_comms",
   "Free-space QKD can achieve longer distances than fiber because atmospheric attenuation is much lower (0.1-0.3 dB/km for vertical paths).",
   None, None)
_f("qkd-017", "quantum_comms",
   "The decoy-state BB84 protocol uses multiple intensity levels to detect photon-number-splitting attacks on weak coherent pulse sources.",
   None, None)
_f("qkd-018", "quantum_comms",
   "In decoy-state BB84, typical intensity levels are signal (μ ≈ 0.5 photons/pulse), decoy (ν ≈ 0.1), and vacuum (0).",
   0.5, "photons/pulse (signal)")
_f("qkd-019", "quantum_comms",
   "Measurement-device-independent QKD (MDI-QKD) removes all detector side-channel attacks by having both parties send signals to an untrusted relay.",
   None, None)
_f("qkd-020", "quantum_comms",
   "Twin-field QKD (TF-QKD) can exceed the repeaterless Pirandola-Laurenza-Ottaviani-Banchi bound, achieving 500+ km in fiber.",
   500, "km")
_f("qkd-021", "quantum_comms",
   "The Shor-Preskill proof establishes the unconditional security of BB84 based on entanglement distillation, showing equivalence between entanglement-based and prepare-and-measure protocols.",
   None, None)
_f("qkd-022", "quantum_comms",
   "Quantum memory for repeaters typically uses rare-earth-doped crystals or atomic ensembles with coherence times ranging from milliseconds to hours.",
   None, None)
_f("qkd-023", "quantum_comms",
   "Entanglement purification (distillation) sacrifices multiple low-fidelity entangled pairs to produce fewer high-fidelity pairs using local operations and classical communication (LOCC).",
   None, None)
_f("qkd-024", "quantum_comms",
   "The DEJMPS protocol is a widely used entanglement purification protocol that corrects both bit-flip and phase-flip errors through bilateral CNOT operations.",
   None, None)
_f("qkd-025", "quantum_comms",
   "Satellite-based QKD was demonstrated by the Micius satellite in 2017, achieving 1200 km quantum key distribution between ground stations.",
   1200, "km")
_f("qkd-026", "quantum_comms",
   "The Micius satellite transmitted approximately 5.9 million signal pulses per second during its QKD experiments.",
   5900000, "pulses/second")
_f("qkd-027", "quantum_comms",
   "Continuous-variable QKD (CV-QKD) encodes information in the quadratures of the electromagnetic field rather than discrete photon states.",
   None, None)
_f("qkd-028", "quantum_comms",
   "The Csiszár-Körner theorem provides the theoretical maximum key rate for a classical wiretap channel, generalized to quantum channels by Devetak and Winter.",
   None, None)
_f("qkd-029", "quantum_comms",
   "Quantum bit commitment was proven impossible in 1997 by Mayers, Lo, and Chau (MLC no-go theorem), removing it as a candidate for QKD authentication.",
   1997, "year")
_f("qkd-030", "quantum_comms",
   "In the BB84 protocol, if Alice and Bob measure in the same basis, their measurement outcomes are perfectly correlated (same bit value).",
   None, None)
_f("qkd-031", "quantum_comms",
   "Photon detector dark count rates for QKD receivers are typically 10-100 counts per second for avalanche photodiodes (APDs).",
   10, "counts/second (low end)")
_f("qkd-032", "quantum_comms",
   "Superconducting nanowire single-photon detectors (SNSPDs) achieve detection efficiencies above 90% with dark count rates below 1 count per second.",
   90, "percent efficiency")
_f("qkd-033", "quantum_comms",
   "A Bell-state measurement can distinguish at most 2 of the 4 Bell states using linear optics alone.",
   2, "distinguishable Bell states")
_f("qkd-034", "quantum_comms",
   "The teleportation fidelity for an ideal quantum teleportation protocol is 1.0 (perfect), but practical implementations achieve 0.80-0.95.",
   1.0, "ideal fidelity")
_f("qkd-035", "quantum_comms",
   "The Pirandola-Laurenza-Ottaviani-Banchi (PLOB) bound gives the maximum secret key rate for a point-to-point QKD link as -log₂(1 - η) per channel use, where η is the transmittance.",
   None, None)
_f("qkd-036", "quantum_comms",
   "Phase error correction in QKD transforms bit errors into phase errors, which are then removed by privacy amplification.",
   None, None)
_f("qkd-037", "quantum_comms",
   "Quantum secret sharing splits a secret among n parties such that any k out of n must cooperate to reconstruct it, based on GHZ states.",
   None, None)
_f("qkd-038", "quantum_comms",
   "Device-independent QKD (DI-QKD) provides security guarantees even with untrusted devices, based solely on the violation of Bell inequalities.",
   None, None)
_f("qkd-039", "quantum_comms",
   "The six-state protocol extends BB84 by using three mutually unbiased bases instead of two, giving better error estimation at the cost of lower sifted key rate (33% retained instead of 50%).",
   33, "percent retained")
_f("qkd-040", "quantum_comms",
   "Quantum digital signatures use quantum states to provide information-theoretically secure message authentication with non-repudiation.",
   None, None)

# ===== Space Infrastructure (~30 facts) ===================================

_f("si-001", "space_infrastructure",
   "NASA's Deep Space Network (DSN) operates three ground station complexes at Goldstone (California), Madrid (Spain), and Canberra (Australia), spaced roughly 120° apart in longitude.",
   3, "DSN complexes")
_f("si-002", "space_infrastructure",
   "DSN stations are spaced approximately 120 degrees apart in longitude to provide continuous coverage of deep space missions.",
   120, "degrees")
_f("si-003", "space_infrastructure",
   "DSN supports Ka-band (31.8-32.3 GHz downlink), X-band (8.4 GHz downlink), and S-band (2.3 GHz downlink) for spacecraft communications.",
   None, None)
_f("si-004", "space_infrastructure",
   "The AETHERIX network topology uses 5 tiers: Earth Ground, Earth Orbital, Deep Space Transit, Mars Orbital, and Mars Surface.",
   5, "tiers")
_f("si-005", "space_infrastructure",
   "The AETHERIX topology contains 241 nodes across all five tiers.",
   241, "nodes")
_f("si-006", "space_infrastructure",
   "Optical communications in AETHERIX use a wavelength of 1550 nm, which is in the near-infrared C-band commonly used in fiber-optic telecommunications.",
   1550, "nm")
_f("si-007", "space_infrastructure",
   "Free-space path loss (FSPL) is calculated as FSPL(dB) = 20·log₁₀(d) + 20·log₁₀(f) + 20·log₁₀(4π/c), where d is distance and f is frequency.",
   None, None)
_f("si-008", "space_infrastructure",
   "Optical downlink data rates in the AETHERIX system range from 2 to 200 Mbps, depending on Earth-Mars distance and link conditions.",
   2, "Mbps (minimum optical)")
_f("si-009", "space_infrastructure",
   "RF downlink data rates range from 0.5 to 6 Mbps, significantly lower than optical but more tolerant of atmospheric conditions.",
   0.5, "Mbps (minimum RF)")
_f("si-010", "space_infrastructure",
   "The LEO laser constellation in AETHERIX's Earth Orbital tier consists of 48 satellites providing inter-satellite laser links.",
   48, "LEO satellites")
_f("si-011", "space_infrastructure",
   "GEO relay satellites in the Earth Orbital tier operate at approximately 35,786 km altitude above the equator.",
   35786, "km")
_f("si-012", "space_infrastructure",
   "Deep Space Transit tier relays are positioned at Earth-Sun Lagrange points L4 and L5, approximately 150 million km from Earth.",
   150, "million km (ES-L4/L5)")
_f("si-013", "space_infrastructure",
   "Mars Orbital tier uses areostationary relays at 17,032 km altitude above Mars equator, analogous to Earth GEO.",
   17032, "km")
_f("si-014", "space_infrastructure",
   "Mars Surface tier includes bases, rovers, drones, and sensor networks operating on the Martian surface.",
   None, None)
_f("si-015", "space_infrastructure",
   "The DSN 70-meter antennas provide the highest gain for deep space communications, with gains exceeding 70 dBi at X-band.",
   70, "meters (antenna diameter)")
_f("si-016", "space_infrastructure",
   "DSN 34-meter beam waveguide antennas support simultaneous S/X/Ka-band operation and are the workhorse of the network.",
   34, "meters (antenna diameter)")
_f("si-017", "space_infrastructure",
   "Optical communications experience scintillation due to atmospheric turbulence, with fade depths of 5-20 dB depending on elevation angle and weather.",
   5, "dB (minimum fade)")
_f("si-018", "space_infrastructure",
   "The International Telecommunication Union (ITU) allocates the 31.8-32.3 GHz band for space-to-Earth deep space Ka-band downlink.",
   None, None)
_f("si-019", "space_infrastructure",
   "Space-based optical terminals can achieve pointing accuracy of microradians (μrad), with typical values of 1-10 μrad for inter-satellite links.",
   1, "μrad (best pointing)")
_f("si-020", "space_infrastructure",
   "The Lunar Laser Communications Demonstration (LLCD) in 2013 achieved 622 Mbps downlink from the Moon to Earth using 1550 nm laser.",
   622, "Mbps")
_f("si-021", "space_infrastructure",
   "The Deep Space Optical Communications (DSOC) experiment on the Psyche mission demonstrated optical communications at distances up to 0.5 AU from Earth.",
   0.5, "AU")
_f("si-022", "space_infrastructure",
   "Mars Relay Network (MRN) uses orbiters such as MAVEN, Mars Odyssey, and Mars Reconnaissance Orbiter as relay satellites for surface assets.",
   None, None)
_f("si-023", "space_infrastructure",
   "The Mars Reconnaissance Orbiter (MRO) uses a 3-meter high-gain antenna for X-band communications with Earth at data rates up to 6 Mbps.",
   3, "meters (MRO antenna)")
_f("si-024", "space_infrastructure",
   "Inter-satellite optical links (ISLs) in the LEO constellation achieve data rates of 10-100 Gbps with distances of 2,000-5,000 km between adjacent satellites.",
   10, "Gbps (minimum ISL)")
_f("si-025", "space_infrastructure",
   "CCSDS Space Link Extension (SLE) services allow remote access to ground station services over terrestrial networks.",
   None, None)
_f("si-026", "space_infrastructure",
   "Delay-tolerant networking is essential for Mars communications because the one-way light time ranges from 3 to 22 minutes.",
   3, "minutes (minimum one-way light time)")
_f("si-027", "space_infrastructure",
   "The Consultative Committee for Space Data Systems (CCSDS) develops communication standards used by virtually all space agencies worldwide.",
   None, None)
_f("si-028", "space_infrastructure",
   "AETHERIX uses hybrid optical/RF communications, where optical provides high bandwidth and RF provides reliability during adverse conditions.",
   None, None)
_f("si-029", "space_infrastructure",
   "The maximum RF uplink data rate to Mars orbiters is approximately 2 Mbps using Ka-band with 70-meter DSN antennas.",
   2, "Mbps (RF uplink max)")
_f("si-030", "space_infrastructure",
   "AETHERIX Earth ground segment includes the three DSN complexes plus dedicated optical ground stations at high-altitude sites with low cloud cover.",
   None, None)

# ===== Orbital Mechanics (~30 facts) ======================================

_f("orb-001", "orbital_mechanics",
   "Mars has a semi-major axis of 1.524 AU (approximately 227.9 million km).",
   1.524, "AU")
_f("orb-002", "orbital_mechanics",
   "The Earth-Mars synodic period is approximately 779.94 days (about 2.135 years), defining how often launch windows occur.",
   779.94, "days")
_f("orb-003", "orbital_mechanics",
   "The minimum Earth-Mars distance at perihelic opposition is approximately 54.6 million km.",
   54.6, "million km")
_f("orb-004", "orbital_mechanics",
   "The maximum Earth-Mars distance at aphelionic conjunction is approximately 401 million km.",
   401, "million km")
_f("orb-005", "orbital_mechanics",
   "The average Earth-Mars distance is approximately 225 million km.",
   225, "million km")
_f("orb-006", "orbital_mechanics",
   "One-way light time between Earth and Mars ranges from approximately 3 minutes (at closest approach) to 22 minutes (at farthest separation).",
   3, "minutes (minimum)")
_f("orb-007", "orbital_mechanics",
   "Solar conjunction blackouts occur approximately every 26 months when the Sun blocks the Earth-Mars line of sight, lasting about 2 weeks.",
   26, "months (conjunction interval)")
_f("orb-008", "orbital_mechanics",
   "During solar conjunction, the Sun-Earth-Mars angle is less than approximately 3-5 degrees, causing signal degradation due to solar plasma.",
   3, "degrees (conjunction angle)")
_f("orb-009", "orbital_mechanics",
   "The Doppler shift at 1550 nm optical wavelength due to Earth-Mars relative orbital velocity can be approximately 15 GHz at maximum.",
   15, "GHz")
_f("orb-010", "orbital_mechanics",
   "Mars orbital velocity is approximately 24.07 km/s, while Earth's is approximately 29.78 km/s.",
   24.07, "km/s (Mars)")
_f("orb-011", "orbital_mechanics",
   "Areostationary orbit around Mars requires an altitude of approximately 17,032 km above the surface, with an orbital period equal to one Mars sidereal day (24.623 hours).",
   17032, "km")
_f("orb-012", "orbital_mechanics",
   "The Mars sidereal day (sol) is 24 hours, 37 minutes, and 22 seconds (88,642 seconds).",
   88642, "seconds")
_f("orb-013", "orbital_mechanics",
   "Kepler's third law states that T² ∝ a³, where T is the orbital period and a is the semi-major axis.",
   None, None)
_f("orb-014", "orbital_mechanics",
   "The Mars orbital eccentricity is 0.0934, significantly higher than Earth's 0.0167.",
   0.0934, "eccentricity")
_f("orb-015", "orbital_mechanics",
   "Earth orbital eccentricity is 0.0167, making its orbit nearly circular.",
   0.0167, "eccentricity")
_f("orb-016", "orbital_mechanics",
   "The Hohmann transfer orbit from Earth to Mars requires approximately 259 days of travel time.",
   259, "days")
_f("orb-017", "orbital_mechanics",
   "The Hohmann transfer orbit semi-major axis is approximately 1.262 AU (the average of Earth's 1.0 AU and Mars' 1.524 AU).",
   1.262, "AU")
_f("orb-018", "orbital_mechanics",
   "The speed of light in vacuum is 299,792,458 m/s, which is the fundamental limit for interplanetary communication latency.",
   299792458, "m/s")
_f("orb-019", "orbital_mechanics",
   "One astronomical unit (AU) is defined as exactly 149,597,870.7 km.",
   149597870.7, "km")
_f("orb-020", "orbital_mechanics",
   "Mars axial tilt is approximately 25.19 degrees, similar to Earth's 23.44 degrees.",
   25.19, "degrees")
_f("orb-021", "orbital_mechanics",
   "Earth axial tilt is approximately 23.44 degrees, responsible for seasonal variations.",
   23.44, "degrees")
_f("orb-022", "orbital_mechanics",
   "The gravitational parameter (μ) of the Sun is 1.327 × 10²⁰ m³/s².",
   1.327e20, "m³/s²")
_f("orb-023", "orbital_mechanics",
   "The gravitational parameter (μ) of Mars is 4.283 × 10¹³ m³/s².",
   4.283e13, "m³/s²")
_f("orb-024", "orbital_mechanics",
   "Mars has a mean radius of 3,389.5 km, approximately 53% of Earth's 6,371 km radius.",
   3389.5, "km")
_f("orb-025", "orbital_mechanics",
   "The areostationary orbital radius (from Mars center) is approximately 20,428 km.",
   20428, "km")
_f("orb-026", "orbital_mechanics",
   "Light time from the Sun to Earth is approximately 8 minutes and 20 seconds (499 seconds).",
   499, "seconds")
_f("orb-027", "orbital_mechanics",
   "Light time from the Sun to Mars varies from approximately 12.7 minutes to 13.8 minutes.",
   12.7, "minutes (minimum Sun-Mars)")
_f("orb-028", "orbital_mechanics",
   "The Mars year (orbital period) is 686.98 Earth days (1.881 Earth years).",
   686.98, "days")
_f("orb-029", "orbital_mechanics",
   "The Earth year (orbital period) is 365.256 days (sidereal year).",
   365.256, "days")
_f("orb-030", "orbital_mechanics",
   "AETHERIX contact window prediction uses true anomaly to compute real-time Earth-Mars distance for link budget calculations.",
   None, None)

# ===== Radiation Hardening (~35 facts) ====================================

_f("rad-001", "radiation_hardening",
   "A Single Event Upset (SEU) is a bit flip in a memory cell or logic element caused by a single high-energy particle strike.",
   None, None)
_f("rad-002", "radiation_hardening",
   "A Multiple Bit Upset (MBU) occurs when a single particle strike flips multiple adjacent bits in a memory word, defeating simple ECC.",
   None, None)
_f("rad-003", "radiation_hardening",
   "A Single Event Latchup (SEL) is a potentially destructive condition where a particle strike creates a low-impedance path between power rails in CMOS devices.",
   None, None)
_f("rad-004", "radiation_hardening",
   "Total Ionizing Dose (TID) is the cumulative radiation damage to semiconductor devices, measured in krads (kilorads) or Grays.",
   None, None)
_f("rad-005", "radiation_hardening",
   "Triple Modular Redundancy (TMR) uses three identical replicas of a circuit with majority-vote logic to mask single-point failures.",
   3, "replicas")
_f("rad-006", "radiation_hardening",
   "TMR reliability for a single module with reliability R is R_TMR = 3R² - 2R³, which exceeds R for R > 0.5.",
   None, None)
_f("rad-007", "radiation_hardening",
   "SECDED (Single Error Correction, Double Error Detection) ECC uses Hamming codes to correct one-bit errors and detect two-bit errors.",
   None, None)
_f("rad-008", "radiation_hardening",
   "The Hamming (39,32) SECDED code uses 7 check bits for every 32 data bits, with 21.9% storage overhead.",
   21.9, "percent overhead")
_f("rad-009", "radiation_hardening",
   "Memory scrubbing periodically reads and rewrites memory contents to correct latent SEUs before they accumulate into uncorrectable errors.",
   None, None)
_f("rad-010", "radiation_hardening",
   "FDIR (Fault Detection, Isolation, and Recovery) is a spacecraft subsystem that detects anomalies, isolates faulty components, and initiates recovery procedures.",
   None, None)
_f("rad-011", "radiation_hardening",
   "A watchdog timer resets a system if it fails to send a periodic heartbeat signal, recovering from latch-ups or software hangs.",
   None, None)
_f("rad-012", "radiation_hardening",
   "The RAD750 radiation-hardened processor, manufactured by BAE Systems, tolerates up to 200 krad (Si) total ionizing dose.",
   200, "krad")
_f("rad-013", "radiation_hardening",
   "The RAD750 processor is used in the Curiosity and Perseverance Mars rovers.",
   None, None)
_f("rad-014", "radiation_hardening",
   "The RAD750 operates at up to 200 MHz with 400 MIPS performance.",
   200, "MHz")
_f("rad-015", "radiation_hardening",
   "The LEON3FT processor, developed by Cobham (now CAES), is the ESA-standard radiation-tolerant processor based on the SPARC V8 architecture.",
   None, None)
_f("rad-016", "radiation_hardening",
   "The LEON3FT can tolerate up to 30 krad (Si) total ionizing dose without performance degradation.",
   30, "krad")
_f("rad-017", "radiation_hardening",
   "Radiation-hardened SRAM-based FPGAs use TMR at the configuration level and scrubbing to mitigate SEUs in the configuration bitstream.",
   None, None)
_f("rad-018", "radiation_hardening",
   "The Mars surface receives approximately 20-30 mSv/year of radiation, compared to approximately 2.4 mSv/year on Earth's surface.",
   20, "mSv/year (Mars minimum)")
_f("rad-019", "radiation_hardening",
   "Interplanetary space radiation includes galactic cosmic rays (GCR), solar particle events (SPE), and trapped radiation belts.",
   None, None)
_f("rad-020", "radiation_hardening",
   "Solar particle events (SPEs) can deliver dose rates exceeding 1 Sv/hour during extreme events, requiring immediate shielding or operational mitigation.",
   1, "Sv/hour (extreme SPE)")
_f("rad-021", "radiation_hardening",
   "The South Atlantic Anomaly (SAA) is a region where the Van Allen radiation belt dips closest to Earth's surface, increasing radiation exposure for LEO satellites.",
   None, None)
_f("rad-022", "radiation_hardening",
   "Single Event Transient (SET) is a momentary voltage spike in a combinational logic circuit caused by a particle strike, which may propagate to memory elements.",
   None, None)
_f("rad-023", "radiation_hardening",
   "Single Event Burnout (SEB) is a destructive event in power MOSFETs where a particle strike triggers a localized high-current condition.",
   None, None)
_f("rad-024", "radiation_hardening",
   "Displacement damage (DD) is caused by non-ionizing energy loss from neutrons and protons, creating lattice defects that degrade semiconductor performance.",
   None, None)
_f("rad-025", "radiation_hardening",
   "Shielding effectiveness depends on material atomic number; hydrogen-rich materials (polyethylene, water) are most effective per unit mass against GCR.",
   None, None)
_f("rad-026", "radiation_hardening",
   "The Van Allen belts contain trapped protons and electrons; the inner belt (1.2-3 RE) has high-energy protons up to several hundred MeV.",
   1.2, "Earth radii (inner belt minimum)")
_f("rad-027", "radiation_hardening",
   "Error-correcting codes used in space include Reed-Solomon, BCH, and LDPC, with Reed-Solomon (255,223) being the CCSDS standard for telemetry.",
   255, "Reed-Solomon codeword length")
_f("rad-028", "radiation_hardening",
   "The CCSDS Reed-Solomon (255,223) code uses 32 parity symbols per 223 data symbols, providing correction of up to 16 symbol errors.",
   16, "symbol errors correctable")
_f("rad-029", "radiation_hardening",
   "Cold sparing ensures that a backup component is completely powered off until needed, preventing it from accumulating TID and SEU damage while idle.",
   None, None)
_f("rad-030", "radiation_hardening",
   "Current-limiting protection prevents SEL from causing permanent damage by detecting the overcurrent and cutting power before thermal destruction.",
   None, None)
_f("rad-031", "radiation_hardening",
   "The TID tolerance of commercial CMOS is typically 1-10 krad, while radiation-hardened devices tolerate 100-300 krad.",
   1, "krad (commercial minimum)")
_f("rad-032", "radiation_hardening",
   "Proton-induced SEU cross-sections are typically measured in cm² per device or per bit, with values around 10⁻¹⁴ to 10⁻⁹ cm²/bit.",
   None, None)
_f("rad-033", "radiation_hardening",
   "The Galileo spacecraft used radiation-hardened components to survive Jupiter's radiation environment of up to 500 krad over the mission lifetime.",
   500, "krad (Jupiter environment)")
_f("rad-034", "radiation_hardening",
   "Temporal TMR (time-redundant TMR) executes the same computation three times sequentially instead of using three separate hardware modules.",
   3, "temporal executions")
_f("rad-035", "radiation_hardening",
   "Power-on reset (POR) circuits must be radiation-hardened to prevent spurious resets during solar particle events.",
   None, None)

# ===== Data Prioritization (~30 facts) ====================================

_f("dp-001", "data_prioritization",
   "AETHERIX uses a 4-tier priority system: P0 (emergency), P1 (high), P2 (normal), and P3 (bulk), with P0 preempting all others.",
   4, "priority tiers")
_f("dp-002", "data_prioritization",
   "CCSDS 121.0-B-3 defines lossless data compression achieving approximately 3:1 compression ratio for scientific instrument data.",
   3, "compression ratio")
_f("dp-003", "data_prioritization",
   "CCSDS 122.0-B-2 defines lossy data compression achieving approximately 10:1 compression ratio for image data using wavelet transforms.",
   10, "compression ratio")
_f("dp-004", "data_prioritization",
   "H.265 (HEVC) video compression achieves approximately 50:1 compression ratio while maintaining acceptable visual quality.",
   50, "compression ratio")
_f("dp-005", "data_prioritization",
   "Deadline-aware scheduling assigns absolute deadlines to bundles and schedules transmissions to maximize on-time delivery probability.",
   None, None)
_f("dp-006", "data_prioritization",
   "Bundle preemption allows higher-priority bundles to interrupt the transmission of lower-priority bundles when buffer space or contact time is limited.",
   None, None)
_f("dp-007", "data_prioritization",
   "BPv7 bundle fragmentation splits a large bundle into two smaller bundles at an intermediate node when the remaining contact time is insufficient for the full bundle.",
   None, None)
_f("dp-008", "data_prioritization",
   "Earliest Deadline First (EDF) scheduling guarantees optimality for preemptive single-resource scheduling when total utilization does not exceed 100%.",
   100, "percent utilization")
_f("dp-009", "data_prioritization",
   "P0 (emergency) priority in AETHERIX includes critical spacecraft health data, emergency commanding, and anomaly reports.",
   None, None)
_f("dp-010", "data_prioritization",
   "P1 (high) priority includes navigation data, orbit determination, and time-critical science data.",
   None, None)
_f("dp-011", "data_prioritization",
   "P2 (normal) priority includes routine science data, software updates, and operational telemetry.",
   None, None)
_f("dp-012", "data_prioritization",
   "P3 (bulk) priority includes archived data, non-time-critical file transfers, and software repository sync.",
   None, None)
_f("dp-013", "data_prioritization",
   "CCSDS File Delivery Protocol (CFDP) class 2 provides reliable file transfer with automatic retransmission over DTN.",
   None, None)
_f("dp-014", "data_prioritization",
   "Quality of Service (QoS) in DTN is defined by three parameters: priority class, lifetime, and delivery likelihood requirement.",
   3, "QoS parameters")
_f("dp-015", "data_prioritization",
   "Bundle age is the elapsed time since creation; when bundle age exceeds the bundle lifetime, the bundle is discarded.",
   None, None)
_f("dp-016", "data_prioritization",
   "The BPv7 hop count block prevents infinite forwarding loops by specifying a maximum hop count that is decremented at each node.",
   None, None)
_f("dp-017", "data_prioritization",
   "Contact volume is the total data that can be transferred during a contact, calculated as data rate multiplied by contact duration.",
   None, None)
_f("dp-018", "data_prioritization",
   "Rate-monotonic scheduling assigns higher priority to tasks with shorter periods, and is optimal among fixed-priority real-time scheduling algorithms.",
   None, None)
_f("dp-019", "data_prioritization",
   "CCSDS 121.0-B-3 uses Rice coding as its core entropy coder for lossless compression of floating-point and integer science data.",
   None, None)
_f("dp-020", "data_prioritization",
   "CCSDS 122.0-B-2 uses a discrete wavelet transform (DWT) followed by bit-plane encoding for lossy image compression.",
   None, None)
_f("dp-021", "data_prioritization",
   "The Consultative Committee for Space Data Systems (CCSDS) Advanced Orbiting Systems (AOS) space data link protocol supports multiplexing of multiple virtual channels.",
   None, None)
_f("dp-022", "data_prioritization",
   "Virtual channel multiplexing allows different priority data streams to share a single physical channel by allocating virtual channel IDs.",
   None, None)
_f("dp-023", "data_prioritization",
   "Asynchronous Message Service (AMS) provides publish-subscribe messaging for space applications with priority-based message delivery.",
   None, None)
_f("dp-024", "data_prioritization",
   "AETHERIX uses deadline-aware preemption: when a contact is about to end and a higher-priority bundle is queued, lower-priority bundles in transit are fragmented.",
   None, None)
_f("dp-025", "data_prioritization",
   "Packet utilization factor in DTN scheduling is the ratio of successfully delivered data to total contact capacity, typically 70-90% for well-designed schedules.",
   70, "percent (minimum utilization)")
_f("dp-026", "data_prioritization",
   "Buffer management policies in DTN include drop-tail (FIFO), drop-front (oldest first), and priority-aware (drop lowest priority first).",
   None, None)
_f("dp-027", "data_prioritization",
   "CCSDS 133.0-B-1 defines the Space Packet Protocol, which uses a packet primary header of 6 bytes containing APID, sequence control, and data length.",
   6, "bytes (packet header)")
_f("dp-028", "data_prioritization",
   "The APID (Application Process Identifier) is an 11-bit field in the CCSDS space packet header allowing 2048 unique data streams.",
   2048, "APIDs")
_f("dp-029", "data_prioritization",
   "CCSDS 132.0-B-3 defines the Transfer Frame, which is the data unit exchanged over a space link, with frame lengths typically 1024-16384 bits.",
   1024, "bits (minimum frame)")
_f("dp-030", "data_prioritization",
   "AETHERIX data prioritization combines bundle priority, deadline, and estimated delivery probability to compute a composite scheduling score.",
   None, None)

# ===== Standards (~25 facts) ==============================================

_f("std-001", "standards",
   "RFC 9171 defines the Bundle Protocol Version 7 (BPv7), the core DTN protocol for store-and-forward delivery.",
   None, None)
_f("std-002", "standards",
   "RFC 4838 defines the Delay-Tolerant Networking Architecture, establishing the fundamental principles of DTN including the bundle layer.",
   None, None)
_f("std-003", "standards",
   "RFC 5326 defines the Licklider Transmission Protocol (LTP) for reliable data transmission over links with very long round-trip times.",
   None, None)
_f("std-004", "standards",
   "RFC 7242 defines the TCP Convergence Layer (TCPCL) for transmitting bundles over established TCP connections.",
   None, None)
_f("std-005", "standards",
   "CCSDS 734.2-B-1 is the CCSDS Bundle Protocol Specification, the CCSDS adaptation of BPv7 for space missions.",
   None, None)
_f("std-006", "standards",
   "CCSDS 734.3-B-1 defines Schedule-Aware Bundle Routing (SABR), specifying how to route bundles using pre-computed contact schedules.",
   None, None)
_f("std-007", "standards",
   "CCSDS 141.0-B-1 defines the standard for Optical Communications, including link design, modulation, and coding for free-space optical links.",
   None, None)
_f("std-008", "standards",
   "RFC 9172 defines Bundle Protocol Security (BPSec), providing integrity and confidentiality security services for BPv7.",
   None, None)
_f("std-009", "standards",
   "RFC 9173 defines the COSE (CBOR Object Signing and Encryption) context for BPSec security blocks.",
   None, None)
_f("std-010", "standards",
   "CCSDS 121.0-B-3 defines the standard for Lossless Data Compression, using adaptive entropy coders for space data.",
   None, None)
_f("std-011", "standards",
   "CCSDS 122.0-B-2 defines the standard for Image Data Compression, using wavelet transforms for lossy or lossless image compression.",
   None, None)
_f("std-012", "standards",
   "CCSDS 133.0-B-1 defines the Space Packet Protocol, the fundamental data unit for space communications.",
   None, None)
_f("std-013", "standards",
   "CCSDS 132.0-B-3 defines the Transfer Frame protocol for organizing space link data into fixed-length or variable-length frames.",
   None, None)
_f("std-014", "standards",
   "CCSDS 401.0-B-30 defines Radio Frequency and Modulation Systems for space research and earth exploration, including Ka/X/S-band specifications.",
   None, None)
_f("std-015", "standards",
   "CCSDS 850.0-G-2 provides the Green Book (informational) for the CCSDS File Delivery Protocol (CFDP).",
   None, None)
_f("std-016", "standards",
   "RFC 5050 defines the earlier Bundle Protocol (BPv6), now superseded by BPv7 (RFC 9171) with improved CBOR encoding and security.",
   None, None)
_f("std-017", "standards",
   "RFC 4839 defines the DTN Bundle Protocol IANA registrations for endpoint ID schemes and convergence layer identifiers.",
   None, None)
_f("std-018", "standards",
   "CCSDS 727.0-B-5 defines the CCSDS File Delivery Protocol (CFDP) for reliable file transfer over space links.",
   None, None)
_f("std-019", "standards",
   "RFC 9174 defines the BPv7 Default Routing Policy Specification, which describes how nodes decide whether to forward, accept, or refuse bundles.",
   None, None)
_f("std-020", "standards",
   "CCSDS 230.1-B-2 defines the Proximity-1 Space Link Protocol for short-range, bidirectional communications between nearby spacecraft.",
   None, None)
_f("std-021", "standards",
   "CCSDS 231.0-B-4 defines the Communications Operation Procedure (COP-1) for reliable data link layer transfer using sequence numbers and retransmission.",
   None, None)
_f("std-022", "standards",
   "CCSDS 301.0-B-4 defines Time Code Formats for space missions, including the CCSDS Unsegmented Time Code (CUC) and CCSDS Day Segmented Time Code (CDS).",
   None, None)
_f("std-023", "standards",
   "RFC 8446 (TLS 1.3) may be used by TCPCL for transport security, providing authentication and encryption of the convergence layer.",
   None, None)
_f("std-024", "standards",
   "CCSDS 350.0-G-3 provides security guidelines for space data systems, covering threat models and recommended countermeasures.",
   None, None)
_f("std-025", "standards",
   "CCSDS 870.0-B-1 defines Cross Support Transfer Services for interoperability between space agency ground networks.",
   None, None)

# ===== AETHERIX-specific (~30 facts) ======================================

_f("aeth-001", "aetherix_specific",
   "AETHERIX (Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange) is an architecture for delay-tolerant networking between Earth and Mars.",
   None, None)
_f("aeth-002", "aetherix_specific",
   "AETHERIX implements 27 source modules across infrastructure, routing, security, orbital, and simulation packages.",
   27, "modules")
_f("aeth-003", "aetherix_specific",
   "AETHERIX has 189 tests across 10 test files providing comprehensive coverage of all core modules.",
   189, "tests")
_f("aeth-004", "aetherix_specific",
   "AETHERIX includes 12 interactive demonstrations showcasing different aspects of the system.",
   12, "demos")
_f("aeth-005", "aetherix_specific",
   "The AETHERIX RL routing agent uses Q-learning with epsilon-greedy exploration policy.",
   None, None)
_f("aeth-006", "aetherix_specific",
   "The AETHERIX routing reward function is R = α(delivery) - β(delay) - γ(hops) - δ(drops) - ε(energy), where α, β, γ, δ, ε are tunable weights.",
   None, None)
_f("aeth-007", "aetherix_specific",
   "AETHERIX implements both BB84 and E91 quantum key distribution protocols for cryptographic key exchange.",
   2, "QKD protocols")
_f("aeth-008", "aetherix_specific",
   "The AETHERIX 5-tier, 241-node topology spans Earth Ground, Earth Orbital, Deep Space Transit, Mars Orbital, and Mars Surface.",
   241, "nodes")
_f("aeth-009", "aetherix_specific",
   "AETHERIX optical link budget calculations use 1550 nm wavelength for free-space optical communications.",
   1550, "nm")
_f("aeth-010", "aetherix_specific",
   "The AETHERIX RL agent state representation (NetworkState) includes current node, neighbors, link quality, and buffer occupancy.",
   4, "state components")
_f("aeth-011", "aetherix_specific",
   "AETHERIX routing actions include forward, store, drop, and split, providing flexible bundle disposition decisions.",
   4, "routing actions")
_f("aeth-012", "aetherix_specific",
   "AETHERIX BPv7 implementation supports 5 priority levels: EMERGENCY, EXPEDITED, NORMAL, STANDARD, and BULK.",
   5, "priority levels")
_f("aeth-013", "aetherix_specific",
   "The AETHERIX forwarding engine implements store-and-forward with a priority queue (BundleQueue) and custody transfer.",
   None, None)
_f("aeth-014", "aetherix_specific",
   "AETHERIX implements LTP (RFC 5326) with segmentation, retransmission, and report segments for reliable deep-space transport.",
   None, None)
_f("aeth-015", "aetherix_specific",
   "AETHERIX TCP Convergence Layer (RFC 7242) provides session management for the Earth segment of the network.",
   None, None)
_f("aeth-016", "aetherix_specific",
   "The AETHERIX UDP Convergence Layer handles optical inter-satellite link fragmentation with configurable loss simulation.",
   None, None)
_f("aeth-017", "aetherix_specific",
   "AETHERIX RL training includes experience replay, convergence detection, and configurable training environments.",
   None, None)
_f("aeth-018", "aetherix_specific",
   "AETHERIX multi-agent routing uses federated learning with Q-table aggregation across distributed agents.",
   None, None)
_f("aeth-019", "aetherix_specific",
   "The AETHERIX quantum repeater chain implements multi-hop entanglement distribution with purification for extended QKD range.",
   None, None)
_f("aeth-020", "aetherix_specific",
   "AETHERIX privacy amplification implements CASCADE reconciliation, universal hashing, and the Csiszár-Körner bound for information-theoretic security.",
   None, None)
_f("aeth-021", "aetherix_specific",
   "The AETHERIX contact window predictor uses true anomaly and synodic period to compute Earth-Mars distance for link budget calculations.",
   None, None)
_f("aeth-022", "aetherix_specific",
   "AETHERIX RF link budget calculator supports Ka/X/S/UHF bands and is compliant with CCSDS 401.0-B-30.",
   4, "RF bands")
_f("aeth-023", "aetherix_specific",
   "AETHERIX celestial body database includes the Sun, Earth, Mars, and Moon with orbital parameters and velocities.",
   4, "celestial bodies")
_f("aeth-024", "aetherix_specific",
   "AETHERIX Doppler shift calculator handles both classical and relativistic Doppler effects for orbital communications.",
   None, None)
_f("aeth-025", "aetherix_specific",
   "The AETHERIX simulation engine integrates topology, forwarding, and bundle generation for end-to-end network simulation.",
   None, None)
_f("aeth-026", "aetherix_specific",
   "AETHERIX policy engine provides 5 default routing policies that can be selected based on mission phase and requirements.",
   5, "default policies")
_f("aeth-027", "aetherix_specific",
   "AETHERIX link budget data rates vary from 2 Mbps at maximum Earth-Mars distance to 200 Mbps at minimum distance for optical links.",
   200, "Mbps (maximum optical)")
_f("aeth-028", "aetherix_specific",
   "The AETHERIX DTN node model includes NodeType, NodeCapabilities, and buffer management with configurable capacity.",
   None, None)
_f("aeth-029", "aetherix_specific",
   "AETHERIX contact graph implementation supports BFS pathfinding through the network topology for route computation.",
   None, None)
_f("aeth-030", "aetherix_specific",
   "AETHERIX is a demo/proof-of-concept implementation, with production requiring DQN replacement, JPL Horizons integration, and ns-3 simulation coupling.",
   None, None)


# ---------------------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------------------

TOPICS = [
    "dtn_protocols", "quantum_comms", "space_infrastructure",
    "orbital_mechanics", "radiation_hardening", "data_prioritization",
    "standards", "aetherix_specific",
]

DIFFICULTIES = ["foundational", "intermediate", "advanced", "expert"]

QSTEM_MCQ = [
    "What is {}?",
    "Which of the following is true about {}?",
    "Select the correct statement about {}.",
    "Which answer best describes {}?",
    "What accurately characterizes {}?",
]

QSTEM_TF = [
    "True or False: {}",
    "Is the following statement correct? {}",
    "Evaluate: {}",
]

QSTEM_NUMERIC = [
    "What is the numerical value of {}?",
    "What is {} expressed in {}?",
    "How many {} does {} have?",
    "What is the value of {} in {}?",
]

NEGATION_PHRASES = [
    "It is NOT the case that {}",
    "The statement '{}' is false.",
    "Contrary to the claim that {}",
    "Which is INCORRECT: {}",
]


def _uid() -> str:
    return uuid.UUID(int=rng.getrandbits(128)).hex[:12]


def _pick_distractors_from_topic(topic: str, correct_text: str, n: int = 3) -> list[str]:
    pool = [f["text"] for f in FACT_BASE if f["topic"] == topic and f["text"] != correct_text]
    if len(pool) < n:
        pool += [f["text"] for f in FACT_BASE if f["text"] != correct_text]
    return rng.sample(pool, min(n, len(pool)))


def _extract_subject(text: str) -> str:
    if len(text) > 80:
        return text[:77] + "..."
    return text


def _difficulty_for(ask_type: str, variant: int) -> str:
    if ask_type == "mcq":
        if variant == 0:
            return "foundational"
        elif variant == 1:
            return "intermediate"
        else:
            return rng.choice(["intermediate", "advanced"])
    elif ask_type == "tf":
        if variant <= 1:
            return "foundational"
        else:
            return rng.choice(["intermediate", "advanced", "expert"])
    else:
        if variant == 0:
            return "intermediate"
        else:
            return rng.choice(["intermediate", "advanced", "expert"])


def _make_numeric_questions(fact: dict) -> list[dict]:
    if "numeric_value" not in fact:
        return []
    val = fact["numeric_value"]
    unit = fact.get("unit", "")
    subject = _extract_subject(fact["text"])
    questions: list[dict] = []

    if val == int(val) and abs(val) >= 1:
        tolerance = 0
        answer = int(val)
    else:
        tolerance = round(abs(val) * 0.05, 10)
        answer = val

    stems = [
        f"What is the numerical value of {subject}?",
        f"What is the value of {subject}?",
    ]
    if unit:
        stems.append(f"What is {subject} expressed in {unit}?")
        stems.append(f"What is the value in {unit} for: {subject}")

    for vi, stem in enumerate(stems):
        q = {
            "id": _uid(),
            "type": "numeric",
            "topic": fact["topic"],
            "difficulty": _difficulty_for("numeric", vi),
            "question": stem,
            "answer": answer,
            "tolerance": tolerance,
            "explanation": fact["text"],
            "fact_id": fact["id"],
        }
        questions.append(q)
    return questions


def _make_tf_questions(fact: dict) -> list[dict]:
    text = fact["text"]
    subject = _extract_subject(text)
    questions: list[dict] = []

    # True variants
    for vi, template in enumerate(QSTEM_TF):
        q = {
            "id": _uid(),
            "type": "tf",
            "topic": fact["topic"],
            "difficulty": _difficulty_for("tf", vi),
            "question": template.format(text),
            "answer": True,
            "explanation": f"This statement is true. {text}",
            "fact_id": fact["id"],
        }
        questions.append(q)

    # False variants
    neg_templates = [
        (f"It is NOT true that {text}", f"The actual fact is: {text}"),
        (f"The following is FALSE: {subject}", f"In reality: {text}"),
    ]
    if "numeric_value" in fact:
        val = fact["numeric_value"]
        wrong_val = val * rng.choice([0.5, 1.5, 2.0, 0.1, 3.0, 0.75])
        if val == int(val) and abs(val) >= 1:
            wrong_val = int(wrong_val)
        neg_templates.append(
            (
                f"True or False: The value of {subject} is {wrong_val}.",
                f"False. The correct value is {val}. {text}",
            )
        )

    for vi, (neg_q, neg_exp) in enumerate(neg_templates):
        q = {
            "id": _uid(),
            "type": "tf",
            "topic": fact["topic"],
            "difficulty": _difficulty_for("tf", vi + 2),
            "question": neg_q,
            "answer": False,
            "explanation": neg_exp,
            "fact_id": fact["id"],
        }
        questions.append(q)
    return questions


def _make_mcq_questions(fact: dict) -> list[dict]:
    text = fact["text"]
    topic = fact["topic"]
    subject = _extract_subject(text)
    distractors = _pick_distractors_from_topic(topic, text, 3)
    questions: list[dict] = []

    for vi in range(5):
        stem_template = QSTEM_MCQ[vi % len(QSTEM_MCQ)]
        question_text = stem_template.format(subject)
        choices = list(distractors[:3]) + [text]
        rng.shuffle(choices)
        q = {
            "id": _uid(),
            "type": "mcq",
            "topic": topic,
            "difficulty": _difficulty_for("mcq", vi),
            "question": question_text,
            "choices": choices,
            "answer": text,
            "explanation": f"The correct answer is: {text}",
            "fact_id": fact["id"],
        }
        questions.append(q)
    return questions


def generate_all_questions() -> list[dict]:
    all_q: list[dict] = []
    for fact in FACT_BASE:
        all_q.extend(_make_mcq_questions(fact))
        all_q.extend(_make_tf_questions(fact))
        all_q.extend(_make_numeric_questions(fact))
    return all_q


def build_metadata(questions: list[dict]) -> dict:
    topic_counts: dict[str, int] = {}
    diff_counts: dict[str, int] = {}
    type_counts: dict[str, int] = {}
    for q in questions:
        t = q["topic"]
        d = q["difficulty"]
        tp = q["type"]
        topic_counts[t] = topic_counts.get(t, 0) + 1
        diff_counts[d] = diff_counts.get(d, 0) + 1
        type_counts[tp] = type_counts.get(tp, 0) + 1
    return {
        "version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "total_questions": len(questions),
        "total_facts": len(FACT_BASE),
        "topics": topic_counts,
        "difficulties": diff_counts,
        "types": type_counts,
    }


def main() -> None:
    questions = generate_all_questions()
    print(f"Initial generation: {len(questions)} questions from {len(FACT_BASE)} facts")

    # If under 2500, supplement with additional variants
    if len(questions) < 2500:
        deficit = 2500 - len(questions)
        print(f"Generating {deficit} additional variants to reach 2500+ target...")
        extra: list[dict] = []
        idx = 0
        while len(extra) < deficit:
            fact = FACT_BASE[idx % len(FACT_BASE)]
            idx += 1

            # Generate extra MCQ with fresh distractors
            topic = fact["topic"]
            subject = _extract_subject(fact["text"])
            distractors = _pick_distractors_from_topic(topic, fact["text"], 3)

            # Unique stem variations
            alt_stems = [
                f"Identify the correct fact about {subject}.",
                f"Which statement regarding {subject} is accurate?",
                f"Choose the best answer for: {subject}",
                f"Of the options below, which correctly describes {subject}?",
                f"Pick the right answer concerning {subject}.",
                f"Which of these statements about {subject} is correct?",
                f"What do we know about {subject}?",
                f"Select the statement that accurately reflects {subject}.",
            ]
            stem = alt_stems[idx % len(alt_stems)]
            choices = list(distractors[:3]) + [fact["text"]]
            rng.shuffle(choices)

            q = {
                "id": _uid(),
                "type": "mcq",
                "topic": topic,
                "difficulty": rng.choice(DIFFICULTIES),
                "question": stem,
                "choices": choices,
                "answer": fact["text"],
                "explanation": f"The correct answer is: {fact['text']}",
                "fact_id": fact["id"],
            }
            extra.append(q)

            # Also add TF variant
            if len(extra) < deficit:
                negate = idx % 2 == 0
                if negate:
                    tf_q = {
                        "id": _uid(),
                        "type": "tf",
                        "topic": topic,
                        "difficulty": rng.choice(DIFFICULTIES),
                        "question": f"Is the following statement false? {fact['text']}",
                        "answer": False,
                        "explanation": f"The statement is actually true: {fact['text']}",
                        "fact_id": fact["id"],
                    }
                else:
                    tf_q = {
                        "id": _uid(),
                        "type": "tf",
                        "topic": topic,
                        "difficulty": rng.choice(DIFFICULTIES),
                        "question": f"True or False: {fact['text']}",
                        "answer": True,
                        "explanation": f"Correct. {fact['text']}",
                        "fact_id": fact["id"],
                    }
                extra.append(tf_q)

        questions.extend(extra)

    rng.shuffle(questions)
    metadata = build_metadata(questions)
    output = {"metadata": metadata, "questions": questions}

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Quiz bank generated successfully")
    print(f"{'='*60}")
    print(f"  Output:    {OUTPUT_PATH}")
    print(f"  Questions: {metadata['total_questions']}")
    print(f"  Facts:     {metadata['total_facts']}")
    print(f"\n  By topic:")
    for t, c in sorted(metadata["topics"].items()):
        print(f"    {t:30s} {c:>5d}")
    print(f"\n  By type:")
    for t, c in sorted(metadata["types"].items()):
        print(f"    {t:30s} {c:>5d}")
    print(f"\n  By difficulty:")
    for d, c in sorted(metadata["difficulties"].items()):
        print(f"    {d:30s} {c:>5d}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
