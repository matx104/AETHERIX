# AETHERIX Technical Interview Questions

## 50+ Expected Questions with Prepared Answers

---

## Category A: DTN & Bundle Protocol

### A1. Why is TCP/IP unsuitable for interplanetary communication?
**Answer**: TCP/IP assumes:
1. **Low latency** (RTT < 1 second) - Mars has 6-44 minute RTT
2. **Continuous connectivity** - Space links have scheduled contacts
3. **End-to-end paths** - DTN uses hop-by-hop forwarding
4. **Symmetric bandwidth** - Space links are highly asymmetric

TCP's congestion control and acknowledgment mechanisms fail completely at interplanetary delays.

### A2. Explain the store-and-forward mechanism in Bundle Protocol.
**Answer**: In BPv7:
1. Source creates a **bundle** with payload + metadata
2. Bundle forwarded to next hop when link available
3. Receiving node **stores** bundle in persistent storage
4. Takes **custody** (responsibility for delivery)
5. Forwards when next link available
6. Process repeats until destination reached

No end-to-end connection needed - tolerates hours/days of delay.

### A3. What is custody transfer and why is it important?
**Answer**: Custody transfer shifts responsibility for bundle delivery from sender to receiver:
- Sender can discard bundle after custody accepted
- Reduces buffer requirements at source
- Provides reliability without end-to-end ACKs
- Critical for resource-constrained spacecraft
- Defined in CCSDS 734.2-B-1

### A4. What convergence layers does BPv7 support?
**Answer**: Three main convergence layers:
1. **LTP** (Licklider Transmission Protocol) - Deep space, retransmission at link layer
2. **TCPCL** (TCP Convergence Layer) - Reliable Earth segment connections
3. **UDP-CL** - Low overhead, optical inter-satellite links

Each optimized for different link characteristics.

### A5. How does LTP differ from TCP?
**Answer**:
| Aspect | TCP | LTP |
|--------|-----|-----|
| ACK scope | End-to-end | Link-by-link |
| RTT assumption | Milliseconds | Minutes to hours |
| Retransmission | Source only | Each hop |
| Red/Green data | No | Yes (reliable vs best-effort) |
| Designed for | Internet | Deep space |

---

## Category B: Quantum Communication

### B1. Explain the BB84 quantum key distribution protocol.
**Answer**: BB84 (Bennett-Brassard 1984):
1. Alice sends qubits in random bases (rectilinear/diagonal)
2. Bob measures in random bases
3. Public basis comparison (classical channel)
4. Keep bits where bases matched (~50%)
5. Sample to check QBER (Quantum Bit Error Rate)
6. If QBER < 11%, key is secure
7. Privacy amplification produces final key

Security from quantum mechanics - measurement disturbs state.

### B2. Why is QKD "information-theoretically secure"?
**Answer**: Security is based on physics, not computational hardness:
- **No-cloning theorem**: Cannot copy unknown quantum state
- **Measurement disturbance**: Any eavesdropping changes state
- **Heisenberg uncertainty**: Cannot measure both bases perfectly
- Even quantum computers cannot break this
- Contrasts with RSA/ECC which rely on computational difficulty

### B3. What are quantum repeaters and why are they needed?
**Answer**: Quantum repeaters extend QKD range:
- Photon loss limits direct QKD to ~100-500 km
- Cannot amplify quantum states (no-cloning)
- Repeaters use **entanglement swapping**:
  1. Generate entanglement A-R1 and R1-R2
  2. Bell measurement at R1
  3. Result: A-R2 entanglement (longer distance)
- AETHERIX places repeaters at Lagrange points

### B4. How does entanglement enable secure communication?
**Answer**: E91 protocol (Ekert 1991):
1. Source generates entangled photon pairs
2. One photon to Alice, one to Bob
3. Both measure in random bases
4. Correlations violate Bell inequality (proves entanglement)
5. Correlated measurements become shared key
6. Any eavesdropping breaks correlations (detected)

### B5. What is post-quantum cryptography?
**Answer**: Algorithms resistant to quantum computer attacks:
- **CRYSTALS-Kyber** - Key encapsulation (NIST standard)
- **CRYSTALS-Dilithium** - Digital signatures
- Based on lattice problems (not factoring)
- Complementary to QKD (different threat model)
- AETHERIX uses both: QKD for key exchange, PQC for signatures

---

## Category C: Space Infrastructure

### C1. Why use Lagrange points for relay satellites?
**Answer**: Lagrange points (L1-L5) offer:
- **Gravitational stability** - Low station-keeping fuel
- **L4/L5 specifically**: 60° ahead/behind in orbit
- **Solar conjunction coverage** - Can relay around Sun
- **Quantum repeater locations** - Extend QKD range
- L4/L5 are stable equilibrium points (Trojan points)

### C2. Explain the DSN's global coverage strategy.
**Answer**: Three complexes 120° apart:
- **Goldstone** (California, USA)
- **Madrid** (Spain)
- **Canberra** (Australia)

Ensures 24/7 coverage - at least one station always has line-of-sight to any spacecraft. AETHERIX integrates with DSN for optical ground stations.

### C3. What is an areostationary orbit?
**Answer**: Mars equivalent of geostationary:
- Altitude: 17,032 km above Mars surface
- Period: 24.623 hours (one Mars day)
- Appears stationary over Mars equator
- Ideal for relay satellites to surface bases
- AETHERIX uses 2 areostationary relays (0° and 180° longitude)

### C4. How do you handle solar conjunction blackouts?
**Answer**: Solar conjunction strategy:
1. **Pre-position data** (T-14 days) - Critical uploads
2. **Lagrange relay activation** (T-7 days) - L4/L5 path
3. **Autonomous operations** (T-0 to T+14 days) - No Earth commands
4. **Store locally** - Mars assets buffer data
5. **Resume direct links** (T+14 days) - Transmit backlog

AETHERIX achieves 50-70% availability during conjunction via relays.

### C5. Why hybrid optical/RF links?
**Answer**: Complementary strengths:

| Aspect | Optical | RF (Ka-band) |
|--------|---------|--------------|
| Data rate | 100-200 Mbps | 2-10 Mbps |
| Weather sensitivity | High | Low |
| Power efficiency | High | Medium |
| Pointing accuracy | μrad | mrad |
| TRL | 7-8 | 9 |

Optical primary, RF backup = >99% availability.

---

## Category D: Orbital Mechanics

### D1. Calculate one-way light time to Mars.
**Answer**: Light time = distance / speed of light

| Distance | Calculation | Result |
|----------|-------------|--------|
| Minimum (54.6M km) | 54.6×10⁶ / 299,792 | **3.0 minutes** |
| Average (225M km) | 225×10⁶ / 299,792 | **12.5 minutes** |
| Maximum (401M km) | 401×10⁶ / 299,792 | **22.3 minutes** |

Round-trip: double these values.

### D2. What is a contact window?
**Answer**: Period when communication link is possible:
- Defined by line-of-sight between nodes
- Affected by: orbital geometry, Earth rotation, elevation angle
- Typical Earth-Mars: 6-12 hours/day
- Predicted using orbital propagation (SGP4/SDP4)
- AETHERIX RL agent schedules transmissions within windows

### D3. How does Doppler shift affect communications?
**Answer**: Relative motion causes frequency shift:
- Formula: Δf/f = v/c
- Max Earth-Mars relative velocity: ~24 km/s
- At 1550nm: Δf ≈ 15 GHz shift
- Compensation: Real-time frequency tracking
- Critical for coherent optical detection

### D4. Explain the Mars synodic period significance.
**Answer**: Synodic period = 779.94 days (≈780 days):
- Time between successive oppositions
- Complete cycle of Earth-Mars relative positions
- Simulation should cover full period
- Opposition: best communication conditions
- Conjunction: worst (solar blackout)

### D5. How does orbital propagation work?
**Answer**: Position prediction methods:
1. **SGP4/SDP4** - General perturbations, TLE-based
2. **JPL Horizons** - High-precision ephemeris
3. **Numerical integration** - Force models (gravity, solar pressure)

AETHERIX uses JPL Horizons for planning, SGP4 for real-time.

---

## Category E: Design Decisions

### E1. Why RL instead of traditional CGR?
**Answer**: CGR limitations addressed by RL:
1. **Adaptability** - RL learns from real conditions
2. **No manual schedules** - Autonomous decisions
3. **Multi-objective** - Balance delivery, delay, energy
4. **Unexpected events** - Handle anomalies gracefully
5. **Continuous improvement** - Learn over time

Trade-off: Higher compute, training needed. Fallback to CGR if RL fails.

### E2. Why 1550nm wavelength for optical links?
**Answer**: 1550nm (C-band) chosen for:
1. **Telecom heritage** - Mature component availability
2. **Low atmospheric absorption** - Window in Earth atmosphere
3. **Eye safety** - Class 1M at typical powers
4. **Fiber compatibility** - Standard telecom fiber
5. **Detector technology** - APD and SNSPD options

### E3. How did you determine link budget parameters?
**Answer**: Based on:
1. **DSOC mission parameters** - NASA's proven design
2. **CCSDS 141.0-B-1** - Optical communications standard
3. **LLCD results** - Lunar laser demo data
4. **Conservative margins** - 10 dB link margin target
5. **Atmospheric models** - Clear sky assumption with diversity

### E4. What are the main technical challenges?
**Answer**: Top 5 challenges:
1. **Pointing accuracy** - μrad precision over millions of km
2. **Atmospheric turbulence** - Adaptive optics needed
3. **Solar conjunction** - 2-week blackout periods
4. **Radiation environment** - SEU mitigation
5. **Power constraints** - Limited spacecraft power budget

### E5. How does your design compare to existing systems?
**Answer**:
| Metric | Current | AETHERIX |
|--------|---------|----------|
| Data rate | 0.5-6 Mbps | 2-200 Mbps |
| Routing | Static | AI-adaptive |
| Security | Symmetric | Quantum |
| Availability | 60-75% | >95% |
| Scalability | 5-10 assets | 100+ nodes |

**10-100x improvement** in key metrics.

---

## Category F: Advanced Protocol Deep-Dive

### F1. Explain the LTP red/green segment model.
**Answer**: LTP (RFC 5326) splits each data transfer session into two segment types:
- **Red segments**: Reliable delivery — the sender transmits data segments followed by a checkpoint. The receiver responds with a Report Segment (RS) listing received data bounds. Any gaps trigger selective retransmission. Red segments guarantee delivery at the cost of bandwidth overhead (ACK traffic and potential retransmissions).
- **Green segments**: Best-effort delivery — sent once with no acknowledgement or retransmission. Green data arrives if the channel is clean; corrupted or lost green segments are simply discarded.

In AETHERIX, segment type is selected per-bundle based on priority:
- P0/P1 bundles → all red (guaranteed delivery for emergency and high-science data).
- P2 bundles → metadata block red (custody tracking), payload green (retransmitting large payloads is bandwidth-expensive).
- P3/P4 bundles → all green (best-effort is acceptable for housekeeping and bulk).

The red/green model is unique to LTP — TCP provides all-reliable, UDP provides all-best-effort. LTP's mixed model is ideal for deep space where bandwidth is precious and not all data deserves retransmission overhead.

### F2. How does experience replay prevent catastrophic forgetting in DQN?
**Answer**: Catastrophic forgetting occurs when a neural network overwrites previously learned weights with new training data, "forgetting" earlier experiences. In DQN for DTN routing, this would mean the agent forgets how to route during opposition conditions after training on conjunction scenarios.

Experience replay prevents this by:
1. **Storing transitions**: Every experience `(state, action, reward, next_state)` is stored in a replay buffer (typically 10⁶ transitions).
2. **Random sampling**: Instead of training on consecutive experiences (which are temporally correlated), the network trains on random mini-batches sampled uniformly from the buffer.
3. **Breaking correlation**: Random sampling ensures the network sees a diverse mix of old and new experiences in every training step, preventing it from overfitting to recent conditions.
4. **Replay ratio**: Each stored transition may be used in multiple training steps, maximising the learning extracted from rare but important events (e.g., a solar flare that only occurs once in 780 days).

In AETHERIX's context: without experience replay, the agent trained over the 780-day synodic period would forget opposition-phase routing by the time it reaches conjunction. The replay buffer maintains a uniform distribution of experiences across all distance phases, ensuring the policy remains effective throughout the entire cycle.

### F3. What is the Csiszár-Körner bound?
**Answer**: The Csiszár-Körner bound (1978) defines the maximum rate at which secret key material can be extracted from correlated random variables observed by two parties (Alice and Bob) in the presence of an eavesdropper (Eve):

```
S ≤ H(X) − H(X|Y)
```

For BB84 over a binary symmetric channel with error probability p (QBER):
```
S ≤ 1 − h(p)
```

Where h(p) = −p log₂(p) − (1−p) log₂(1−p) is binary entropy.

This bound tells us:
- At QBER = 0%: S = 1.0 (all raw key bits become secret key).
- At QBER = 5%: S = 0.714 (71.4% efficiency).
- At QBER = 11%: S = 0.499 (the Shor-Preskill threshold — positive but reduced).
- At QBER ≥ 50%: S ≤ 0 (no secret key possible).

In AETHERIX, this bound is used in the privacy amplification stage to calculate the maximum extractable key length: `m = n × S − leak_EC − security_parameter`. The simulation compares actual key rates against this theoretical maximum to verify that post-processing is not unnecessarily discarding key material.

### F4. How does BFS routing scale with 241 nodes?
**Answer**: BFS pathfinding on AETHERIX's contact graph scales as O(V + E) per query, where V is the number of contact vertices and E is the number of valid contact-to-contact edges. For the 241-node topology:

- **Contact vertices**: Each inter-tier link has ~1 contact per day per node pair. Over a 780-day simulation with ~200 active node pairs: V ≈ 156,000 contact vertices.
- **Edges**: Each contact can connect to subsequent contacts at the destination node. Average fan-out ≈ 5–10 edges per vertex: E ≈ 780,000–1,560,000 edges.
- **Per-query time**: BFS traversal of this graph takes ~1–5 ms on modern hardware (well within the real-time routing requirement).
- **Query frequency**: The RL agent queries BFS only as a fallback (when confidence < 0.3), so query rate is low (~1 per second during normal operation).

Scalability concerns arise if the network grows beyond 1000 nodes or if the simulation horizon extends beyond 780 days. The contact graph can be pruned by removing expired contacts (past contacts) and contacts too short for any feasible bundle, keeping the active graph size manageable. Additionally, the tiered topology constrains the search — bundles typically traverse 4–5 hops, so BFS only needs to explore contacts within a bounded time window (±max_lifetime).

### F5. What is the relationship between link margin and data rate?
**Answer**: Link margin and data rate are directly coupled through the Shannon capacity and the receiver's required Eb/N₀ (energy per bit to noise spectral density ratio):

```
Margin = P_received − P_sensitivity(required for target BER at current data rate)
```

The relationship works as follows:
1. **Higher data rate → lower margin**: At a fixed transmit power and distance, increasing the data rate spreads the available energy across more bits. Each bit has less energy, so the signal-to-noise ratio (SNR) drops, and the link margin shrinks. Doubling the data rate reduces the margin by 3 dB.
2. **Lower data rate → higher margin**: Reducing the data rate concentrates energy into fewer bits, improving SNR. AETHERIX exploits this at aphelion: reducing from 200 Mbps to 2 Mbps recovers ~20 dB of link margin, keeping the link operational.
3. **Adaptive coding and modulation (ACM)**: AETHERIX dynamically adjusts the FEC code rate and modulation order based on current margin. At opposition (high margin): high-order modulation (64-QAM) with weak FEC (code rate 0.9) = 200 Mbps. At aphelion (low margin): low-order modulation (BPSK/QPSK) with strong FEC (code rate 0.5) = 2 Mbps. This is the same principle used in DVB-S2 for satellite TV.

The formula: `DataRate = Bandwidth × log₂(1 + SNR)`, where SNR = `Margin + ReceiverSensitivity`. When margin drops, reducing the data rate is the primary lever to maintain positive margin — the alternative (increasing transmit power) is constrained by spacecraft power budgets.

---

## Quick Tips for Interview

1. **Start with the standard**: "According to CCSDS 734.2..."
2. **Use numbers**: Specific values show preparation
3. **Acknowledge trade-offs**: Shows mature understanding
4. **Connect to project**: Relate answers to AETHERIX design
5. **Draw if needed**: Visual explanations are powerful
