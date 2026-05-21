# Mock Interview Script — AETHERIX Oral Exam

**Candidate**: Muhammad Abdullah Tariq
**Project**: AETHERIX — Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange
**Exam**: EduQual Level 6 Oral Examination
**Format**: 15–20 min presentation + 30–40 min technical interview
**This script**: 30-minute interview portion (15 questions, ~2 min each)

---

## Interview Instructions

- Each question includes a suggested time, model answer, and follow-up probe.
- The examiner may skip or reorder questions.
- Questions cover all 6 Learning Objectives.
- Answers should be concise: start with the direct answer, then expand.

---

## Question 1 — DTN Fundamentals (LO1)
**Time**: 2 minutes

**Examiner**: "Why is TCP/IP fundamentally unsuitable for interplanetary communication, and how does DTN solve this?"

**Model Answer**: TCP makes three assumptions that break in space. First, it assumes low latency — TCP's congestion window grows by one packet per RTT, so at Mars's 6-to-44 minute RTT, ramp-up takes hours. Second, TCP assumes continuous connectivity, but Earth-Mars links are scheduled contacts of 6–12 hours per day. When the link drops, TCP backs off exponentially. Third, TCP uses end-to-end acknowledgements, which means a retransmission must traverse the entire path again. DTN solves all three with store-and-forward: each node holds bundles in persistent storage until the next contact opens. Custody transfer localises retransmission to the failed hop. The bundle layer sits above transport protocols, so different convergence layers can serve different link characteristics — LTP for deep space, TCP for Earth, UDP for ISL.

**Follow-up probe**: "Can you quantify how long a TCP connection setup would take to Mars?"

> TCP three-way handshake = 1.5 × RTT = 1.5 × 25 min (average) = 37.5 minutes just to establish the connection. That's before any data is sent.

---

## Question 2 — Bundle Protocol (LO1)
**Time**: 2 minutes

**Examiner**: "Explain the structure of a BPv7 bundle and how priority classes work in AETHERIX."

**Model Answer**: A BPv7 bundle has three parts: the primary block (CBOR-encoded, containing source and destination EIDs, creation timestamp, lifetime, hop count, and processing control flags), the payload block (application data), and optional extension blocks for security and metadata. In AETHERIX, the `Bundle` class implements this per RFC 9171 with flags like `CUSTODY_REQUESTED` (0x08) and `IS_FRAGMENT` (0x01). We define five priority levels: P0 Emergency (anomaly alerts, <1 min delivery), P1 High Science (solar events, <30 min), P2 Standard (daily science, <24 hr), P3 Housekeeping (logs, <7 days), and P4 Bulk (archives, <30 days). The RL agent uses priority to select routing actions and convergence layer modes — P0/P1 use LTP red segments with custody; P3/P4 use LTP green without custody.

**Follow-up probe**: "What flag would you set on an emergency bundle?"

> `CUSTODY_REQUESTED` (0x08) plus `DEST_IS_SINGLETON` (0x10) plus `ACK_REQUESTED` (0x20). These ensure guaranteed single-destination delivery with custody tracking.

---

## Question 3 — Convergence Layers (LO1)
**Time**: 1.5 minutes

**Examiner**: "Compare LTP and TCPCL as convergence layers. When would you use each?"

**Model Answer**: LTP is for high-delay, intermittent deep-space links. It provides red (reliable, ACKed) and green (best-effort) segments with link-local retransmission. Its timers default to minutes or hours. TCPCL wraps TCP for reliable Earth-segment connections where delay is milliseconds and the link is always available. In AETHERIX, Mars-to-Lagrange-to-Earth hops use LTP, while DSN-station-to-Mission-Operations-Center uses TCPCL. The same bundle transits both — that's the power of the convergence layer architecture. We also use UDP-CL for the LEO inter-satellite links at 1–10 Gbps where the overhead of reliability is unnecessary.

**Follow-up probe**: "What's the advantage of LTP's red/green split over just using two separate channels?"

> A single LTP session can mix red and green blocks, avoiding the overhead of two session setups. This matters because session establishment itself costs one RTT on a deep-space link.

---

## Question 4 — RL Routing (LO1)
**Time**: 2 minutes

**Examiner**: "How does your RL routing agent work, and what advantage does it have over Contact Graph Routing?"

**Model Answer**: The agent uses Q-learning with four actions: FORWARD to a neighbour, STORE locally, DROP, or SPLIT for multipath routing. The state includes current node, neighbour link qualities, buffer occupancy, bundle priority, bundle deadline, and destination. The reward function balances five objectives: `R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)` with α=1.0, β=0.001, γ=0.1, δ=10.0, ε=0.01. Compared to CGR, the RL agent adapts in real-time to unplanned events like link failures, optimises multiple objectives simultaneously instead of just minimising delay, and learns from experience over the 780-day synodic period. CGR requires pre-uploaded contact schedules that are stale by 12+ minutes; the RL agent makes decisions based on current local observations. The fallback is CGR when agent confidence is below 0.3.

**Follow-up probe**: "Why is the drop penalty (10.0) so much larger than the delivery reward (1.0)?"

> Because dropping a bundle is total failure — the data is lost. Delivery is the baseline expectation (reward 1.0). The asymmetric penalty ensures the agent strongly prefers any delivery path over dropping, even if the delivery path has higher delay or more hops.

---

## Question 5 — QKD Fundamentals (LO2)
**Time**: 2 minutes

**Examiner**: "Walk me through the BB84 protocol. What makes it secure?"

**Model Answer**: Alice generates random bits and randomly encodes each in either the rectilinear basis (|0⟩/|1⟩) or diagonal basis (|+⟩/|−⟩). She sends single photons to Bob, who measures each in a random basis. About 50% of the time their bases match, and those bits form the raw key. They publicly compare bases (not bit values) to identify matching pairs, then sample a subset to measure QBER. If QBER < 11% — the Shor-Preskill threshold — the key is secure. Any eavesdropper measuring in the wrong basis disturbs the photon state due to the no-cloning theorem, introducing detectable errors. After error correction and privacy amplification, the final key is information-theoretically secure — meaning no amount of computing power, including quantum computers, can break it.

**Follow-up probe**: "What if QBER comes back at 8% — is that secure?"

> Yes. 8% is below the 11% Shor-Preskill threshold. The remaining key has some information leakage to the eavesdropper, but privacy amplification compresses the key by an amount related to the binary entropy h(0.08) ≈ 0.4, producing a shorter but perfectly secret final key.

---

## Question 6 — Quantum Repeaters (LO2)
**Time**: 2 minutes

**Examiner**: "How do quantum repeaters extend QKD range, and where does AETHERIX place them?"

**Model Answer**: Direct QKD is limited by photon loss to roughly 100–500 km in fibre or 2,000 km free-space. Quantum repeaters extend this through entanglement swapping: a repeater at R1 receives one half of an entangled pair from Alice and one from R2, performs a Bell-state measurement on its two qubits, and announces the result. This collapses Alice and R2 into an entangled state even though they never interacted. By chaining repeaters, end-to-end entanglement spans the full distance. In AETHERIX, quantum repeaters are co-located with the Lagrange-point relay satellites at ES-L4 and ES-L5 — approximately 150M km from Earth. This splits the Earth-Mars link into two more tractable segments. The trade-off: interplanetary QKD has never been demonstrated. Our simulation in `src/security/qkd.py` proves the protocol layer is sound, but the hardware challenges are significant.

**Follow-up probe**: "How many photons per second would you need for a 1 bps key rate at Mars distance?"

> At 225M km with 370 dB FSPL and a 1 m receiving telescope, the fraction of photons captured is roughly 10⁻¹⁷. To get 1 detected photon per second, you'd need to transmit ~10¹⁷ photons per second. At 1550 nm, each photon has ~1.3×10⁻¹⁹ J, so the transmit power for photons alone would be ~13 mW — feasible. But detector dark counts, background noise, and the 50% sifting loss reduce the effective key rate significantly.

---

## Question 7 — Post-Quantum Cryptography (LO2)
**Time**: 1.5 minutes

**Examiner**: "Why does AETHERIX use both QKD and post-quantum cryptography?"

**Model Answer**: Defence-in-depth. QKD provides information-theoretic security for key exchange — guaranteed by physics. But QKD requires dedicated hardware, line-of-sight, and has low key rates (1–10 bps Earth-Mars). If the quantum channel is unavailable due to weather or equipment issues, we need a fallback. That's ML-KEM (FIPS 203, based on Kyber) — a lattice-based key encapsulation mechanism that runs on classical hardware over any channel. For authentication, we always use ML-DSA (FIPS 204, based on Dilithium) because QKD alone cannot authenticate the communicating parties — only distribute keys. The layered approach means: if the quantum channel fails, ML-KEM handles key exchange; if lattice cryptography is compromised, QKD keys remain secure.

**Follow-up probe**: "What's the overhead of ML-DSA signatures on bundles?"

> ML-DSA-65 signatures are 3,309 bytes. For a typical 1 MB science bundle, this is 0.3% overhead — negligible. For small command bundles (100 bytes), the signature is 33× the payload, which is significant. That's where we might use the hash-based SLH-DSA alternative for small messages.

---

## Question 8 — Network Architecture (LO3)
**Time**: 2 minutes

**Examiner**: "Explain AETHERIX's five-tier network architecture and justify each tier."

**Model Answer**: Tier 1 is Earth ground — 6 nodes comprising 3 DSN RF stations (Goldstone, Madrid, Canberra) and 3 optical ground stations, providing 24/7 coverage and weather diversity. Tier 2 is Earth orbital — 51 nodes: 3 GEO relays for reliable Earth-segment routing and 48 LEO satellites in 6 orbital planes with optical inter-satellite links at 1–10 Gbps, enabling high-throughput routing between DSN stations via space. Tier 3 is deep space — 4 nodes at ES-L4 and ES-L5 Lagrange points, providing conjunction coverage and quantum relay services. Tier 4 is Mars orbital — 4 nodes: 2 areostationary relays at 17,032 km for continuous equatorial coverage and 2 polar orbiters for high-latitude coverage. Tier 5 is Mars surface — 167 nodes: bases, rovers, drones, and sensors. Each tier serves a purpose that cannot be merged: Tier 3's conjunction coverage cannot be achieved by any number of ground stations, and Tier 2's ISL routing bypasses terrestrial network dependencies.

**Follow-up probe**: "What's the weakest tier?"

> Tier 3 — only 4 nodes, and if both L4 relays fail, conjunction availability drops to zero. That's why each Lagrange point has a primary and backup satellite.

---

## Question 9 — DSN Integration (LO3)
**Time**: 1.5 minutes

**Examiner**: "How does AETHERIX integrate with the existing DSN?"

**Model Answer**: AETHERIX uses CCSDS-compliant BPv7 bundles, so any DSN station running ION-DTN (the reference BPv7 implementation from JPL) can route AETHERIX bundles without modification. The integration point is the convergence layer: DSN stations communicate with spacecraft via LTP for deep-space links and with the Mission Operations Center via TCPCL for Earth links. AETHERIX adds optical ground stations co-located near existing DSN complexes, following CCSDS 141.0-B-1 for the optical physical layer. The DSN's 70-meter and 34-meter antennas continue serving RF Ka-band links as backup. Endpoint IDs follow LNIS v5 (CCSDS 142.0-B-2), ensuring unique addressing across AETHERIX and any future interplanetary network like LunaNet.

**Follow-up probe**: "Does AETHERIX compete with the DSN or complement it?"

> Complement. AETHERIX adds optical capability and intelligent routing on top of DSN's existing RF infrastructure. The DSN remains the primary RF ground segment; AETHERIX adds optical ground stations and space-based relay infrastructure.

---

## Question 10 — Orbital Mechanics (LO4)
**Time**: 2 minutes

**Examiner**: "Calculate the one-way light time and free-space path loss for an optical link at Mars's average distance of 225 million km."

**Model Answer**: Light time: t = d/c = 225×10⁶ km / 299,792.458 km/s = 750.6 seconds ≈ 12.5 minutes. Free-space path loss at 1550 nm: FSPL = 20·log₁₀(4πd/λ) = 20·log₁₀(4π × 225×10⁹ / 1.55×10⁻⁶) = 20·log₁₀(1.82×10¹⁸) = 20 × 18.26 = 365.2 dB. This is the fundamental challenge — 365 dB of signal attenuation. With 5 W transmit power (37 dBm), a 22 cm TX aperture gain of ~104 dBi, and a 1 m RX aperture gain of ~117 dBi, the EIRP is 141 dBm, and after subtracting FSPL plus atmospheric and pointing losses (~10 dB), the received power is approximately −234 dBm. That's in the photon-counting regime — individual photons arrive every few nanoseconds.

**Follow-up probe**: "How does this change at opposition versus conjunction?"

> At opposition (54.6M km), FSPL drops to ~353 dB — 12 dB less loss, which translates to ~16× more received power and proportionally higher data rates (up to 200 Mbps). At conjunction (401M km), FSPL rises to ~370 dB, reducing the data rate to ~2 Mbps.

---

## Question 11 — Contact Windows (LO4)
**Time**: 1.5 minutes

**Examiner**: "How does AETHERIX predict contact windows, and how does the RL agent use them?"

**Model Answer**: Contact windows are predicted using orbital propagation: SGP4 for LEO satellites with TLE inputs, and JPL Horizons for planetary positions. The `predict_contact_windows()` function in `src/orbital/contact_windows.py` computes line-of-sight intervals between node pairs, filtered by minimum elevation angle (10° for RF, 20–30° for optical). Each window is a tuple of (start_time, end_time, max_data_volume). The RL agent uses these predictions in its state representation — knowing that a high-quality contact window opens in 2 hours, the agent may choose STORE now rather than forwarding through a poor-quality link. The agent's time-varying policy is one of its advantages over static CGR: it learns to be opportunistic about contact windows.

**Follow-up probe**: "What's the typical Earth-Mars contact window duration?"

> 6–12 hours per day for a single DSN station, depending on Mars's declination and the station's latitude. With three DSN stations, total coverage can be 18–24 hours/day.

---

## Question 12 — Radiation Hardening (LO5)
**Time**: 1.5 minutes

**Examiner**: "How does the space radiation environment affect AETHERIX's computing systems, and what mitigations are in place?"

**Model Answer**: The interplanetary radiation environment causes single-event upsets (bit flips in memory), single-event latchups (short circuits requiring power cycles), and total ionising dose degradation over time. The Mars orbital environment is particularly harsh — no magnetic field shielding. AETHERIX mitigates this at three levels. Hardware: radiation-hardened processors (LEON3 or RAD750) with 10× SEU resistance, plus EDAC (SECDED) on every memory word correcting single-bit flips. Logical: triple modular redundancy for critical routing decisions — three independent computations with majority voting. Protocol-level: LTP retransmission handles radiation-induced transmission errors, and store-and-forward buffers use CRC32 scrubbing to detect and correct data corruption during multi-day storage.

**Follow-up probe**: "What's the difference between SECDED and TMR?"

> SECDED corrects single-bit errors in memory at the hardware level — it's passive and always on. TMR is active redundancy for computation — the same calculation runs three times in parallel, and a voter selects the majority result. SECDED handles memory errors; TMR handles logic errors from radiation-induced transient faults.

---

## Question 13 — Data Prioritisation (LO6)
**Time**: 1.5 minutes

**Examiner**: "How does AETHERIX handle data prioritisation during a solar conjunction when bandwidth is severely limited?"

**Model Answer**: During conjunction, direct Earth-Mars links are unavailable for ~2 weeks. The Lagrange relay path provides 50–70% availability but at reduced bandwidth. The RL agent's priority-aware routing becomes critical: P0 emergency bundles (spacecraft health alerts) are routed immediately via the Lagrange path using LTP red segments with custody transfer. P1 high-science data is queued behind P0 with the same reliability guarantees. P2 standard data is stored locally on Mars assets until direct links resume — the 780-day synodic period means the conjunction is predictable, so the agent learns to pre-position data before it starts. P3/P4 bundles are deferred entirely. The reward function's drop penalty (δ=10.0 for P0, δ=0.1 for P4) ensures the agent never sacrifices high-priority data for low-priority throughput. The total Mars surface buffer capacity (167 nodes × 64–256 GB each) can store the full conjunction backlog.

**Follow-up probe**: "What if the buffer fills up?"

> The agent must DROP the lowest-priority bundles first (P4, then P3). The drop penalty is weighted by priority, so the agent always prefers dropping P4 over P3, P3 over P2, etc. If P0 bundles are at risk of dropping, the system sends an alert requesting operational intervention — this is the threshold where autonomous operation requires human decision-making.

---

## Question 14 — Standards (Cross-cutting)
**Time**: 1.5 minutes

**Examiner**: "Which standards does AETHERIX comply with, and why is standards compliance important for a research project?"

**Model Answer**: AETHERIX follows four CCSDS Blue Books: 734.2-B-1 (DTN Architecture), 735.1-B-1 (Bundle Protocol), 141.0-B-1 (Optical Communications), and 142.0-B-2 (Space Link Identifiers). Three IETF RFCs: 9171 (BPv7), 5326 (LTP), and 4838 (DTN Architecture). And three NIST PQC standards: FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA). Standards compliance matters even in research because: (1) it ensures the demo reflects real-world constraints, (2) it makes the results comparable to other DTN research using the same protocols, (3) it demonstrates professional awareness of the engineering domain, and (4) it provides a clear path from demo to deployment — the bundle format, convergence layers, and security mechanisms are already standardised, so a production system would use the same architecture.

**Follow-up probe**: "Name one thing in your implementation that doesn't fully comply with the standard."

> The LTP convergence layer is simulated, not fully implemented. RFC 5326 specifies detailed session management, checkpoint/report segment exchanges, and timer behaviour. AETHERIX models the logical behaviour (red/green, retransmission) but doesn't implement the full state machine. For a demo, this is acceptable; for deployment, ION-DTN provides a compliant LTP implementation.

---

## Question 15 — Design Justification (Summary)
**Time**: 2 minutes

**Examiner**: "If you had to summarise AETHERIX's three most innovative contributions in 60 seconds, what would they be?"

**Model Answer**: First, reinforcement-learning routing for DTN — replacing static contact graph routing with an adaptive agent that learns optimal policies across the full 780-day Earth-Mars synodic cycle. The agent balances delivery, delay, hops, drops, and energy simultaneously, adapts to unplanned failures, and degrades gracefully to CGR when uncertain. Second, the hybrid optical/RF with QKD-plus-PQC security architecture — combining 1550 nm optical links for throughput (up to 200 Mbps), Ka-band RF for reliability (>95% availability), physics-guaranteed QKD for key exchange, and NIST-standardised post-quantum cryptography for authentication and fallback. Third, the Lagrange-point relay topology — exploiting the gravitational stability of ES-L4 and ES-L5 to provide conjunction coverage and quantum repeater hosting, achieving 50–70% availability during solar conjunction where current systems have zero. Together, these move interplanetary networking from scheduled, static, low-throughput communication to adaptive, secure, high-throughput data exchange.

**Follow-up probe**: "What's the biggest risk to the project's success?"

> The RL agent's performance in scenarios not covered by training data. If the real Mars environment presents conditions outside the simulation's state space, the agent may make poor decisions. The CGR fallback mitigates this, but the fallback doesn't have the RL agent's multi-objective optimisation. This is why DQN with continuous state representation is the priority upgrade — it generalises better than the current Q-table.
