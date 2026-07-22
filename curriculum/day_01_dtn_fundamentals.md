# Day 1: DTN Fundamentals — Why TCP/IP Fails in Space

## 📅 July 23, 2026

## 🎯 Learning Objective
Understand why the TCP/IP protocol stack — the foundation of the terrestrial internet — fundamentally breaks in interplanetary environments, and how Delay-Tolerant Networking (DTN) solves each failure. This maps to **LO1** of the EduQual Level 6 exam: demonstrate deep knowledge of DTN architecture and the Bundle Protocol.

## 📖 The Core Concept

Abdullah, imagine you send a text message on Earth. TCP opens a connection (three-way handshake), sends packets, and receives acknowledgements — all within milliseconds. The entire internet assumes three conditions that hold on Earth but **collapse** across interplanetary distances.

### Failure 1: Round-Trip Time (RTT) is enormous

Earth and Mars range from 54.6 million km (opposition) to 401 million km (conjunction). Light travels at 299,792 km/s, so the **one-way light time (OWLT)** is **3 minutes at opposition to 22.3 minutes at conjunction**. The round-trip time is double that: **6 to 44 minutes**.

TCP's congestion window grows by one packet per RTT. At a 24-minute RTT, ramping up to send even a 10 MB file would take hours just to open the window. TCP's retransmission timeout (RTO) is derived from RTT variance — at interplanetary scales, RTO becomes minutes to hours, and every timeout triggers exponential backoff. The protocol spends more time waiting than transmitting.

Even a TCP three-way handshake — SYN, SYN-ACK, ACK — takes **1.5 × RTT = 37.5 minutes** at average Mars distance (225M km, 12.5 min OWLT). That is before a single data byte leaves.

### Failure 2: Connectivity is intermittent, not continuous

Earth-Mars links are **scheduled contact windows** of 6–12 hours per day for a single DSN station. The link disappears entirely during **solar conjunction** (~2 weeks every 780 days), when the Sun sits between the planets.

TCP treats any gap in communication as congestion. When a contact window closes, TCP's congestion control backs off exponentially — it assumes the network is overloaded. When the window reopens hours later, TCP starts the slow-start phase from scratch. This is not a performance issue; it is a **fundamental model mismatch**.

### Failure 3: Channel asymmetry

Mars downlink (spacecraft → Earth) can run at 200 Mbps, but the uplink (Earth → spacecraft) is often 1/100th of that rate. TCP ACKs are small but latency-critical. An asymmetric return path where ACKs are delayed starves the congestion window, collapsing throughput to a fraction of capacity.

### The DTN Solution: Store-and-Forward

Delay-Tolerant Networking, formalised in **RFC 4838**, replaces TCP's end-to-end session model with a **hop-by-hop store-and-forward** architecture. Instead of maintaining a live connection across the entire path:

1. A node holds data in **persistent storage** until a contact window opens.
2. It transfers the data to the next hop using whatever transport is appropriate for that link (LTP for deep space, TCP for Earth).
3. The receiving node acknowledges **custody** — taking responsibility for onward delivery.
4. The original sender can free its buffer.

This decouples every link. A failure on hop 3 does not require hop 1 to retransmit across the entire 22-minute path. Retransmission is **local to the failed link**.

### The Bundle: DTN's Fundamental Unit

The atomic data unit in DTN is the **bundle** — not a packet. A bundle is a self-contained message carrying source, destination, lifetime, and priority. Bundles are designed to sit in storage for hours, days, or weeks without degradation. They do not require a live session — they wait patiently for the next contact.

This is why AETHERIX (Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange) is built on DTN, not TCP/IP. Every design decision — the five-tier topology, the RL routing agent, the convergence layers, the custody mechanism — exists because TCP/IP cannot serve this environment.

## 🔬 In AETHERIX

The DTN architecture is the substrate of every AETHERIX module. The project README (AGENTS.md) states the network topology is a **5-tier architecture**: Earth Ground (DSN stations), Earth Orbital (GEO relays + LEO laser constellation), Deep Space Transit (Lagrange point relays ES-L4/ES-L5), Mars Orbital (areostationary + polar relays), and Mars Surface (bases, rovers, drones, sensors).

A science bundle travelling from Mars to Earth traverses this entire stack. In `src/routing/bundle.py`, the `Bundle` class implements the BPv7 data unit with fields including `source`, `destination`, `creation_time`, `lifetime_seconds` (default: `86400 * 7` = 7 days), `priority`, and `hops` tracking. The `EndpointID` class parses identifiers like `dtn://mars.surface.rover-01/science`.

The `ForwardingEngine` in `src/routing/forwarding_engine.py` implements the store-and-forward loop: it receives bundles into a priority `BundleQueue`, consults the RL routing agent for each dequeue cycle, and executes the chosen action (forward, store, drop). The engine's `tick()` method purges expired bundles and drains the queue — exactly the DTN control loop.

Key constants in the project docs: Mars distance range **54.6M km to 401M km**, light-time delay **3–22 minutes one-way**, data rates **2–200 Mbps** (distance-dependent).

## 📐 Key Numbers & Formulas
- **One-way light time (OWLT):** t = d / c, where c = 299,792 km/s
- **Mars opposition:** 54.6M km → OWLT = 182 s (3 min)
- **Mars average:** 225M km → OWLT = 750 s (12.5 min)
- **Mars conjunction:** 401M km → OWLT = 1337 s (22.3 min)
- **TCP handshake to Mars (avg):** 1.5 × RTT = 1.5 × 25 min = **37.5 minutes** (just to establish connection)
- **Contact windows:** 6–12 hours/day per DSN station; 18–24 hours with 3 stations
- **Solar conjunction blackout:** ~2 weeks, every **780 days** (synodic period)
- **Data rate range:** 2–200 Mbps (distance-dependent)
- **Earth-Mars synodic period:** 779.94 days
- **DTN architecture standard:** RFC 4838

## 🔗 Standards & References
- [RFC 4838 — Delay-Tolerant Networking Architecture](https://datatracker.ietf.org/doc/html/rfc4838)
- [RFC 9171 — Bundle Protocol Version 7](https://datatracker.ietf.org/doc/html/rfc9171)
- [CCSDS 734.2-B-1 — CCSDS Bundle Protocol Specification](https://public.ccsds.org/Pubs/734x2b1.pdf)
- [NASA/JPL ION-DTN Implementation](https://github.com/nasa/ION-DTN)
- [DTNRG — Delay Tolerant Networking Research Group](https://irtf.org/dtnrg)

## 💡 How the Examiner Will Probe This

**Q: "Why can't you just use TCP with a very large window for Mars communication?"**
→ Even with an infinite window, TCP's congestion control interprets the 6–44 minute RTT as persistent congestion. The RTO would be minutes to hours. TCP also requires continuous connectivity — Earth-Mars links are scheduled 6–12 hour contacts. DTN's store-and-forward with custody transfer explicitly handles disconnections by design.

**Q: "Walk me through what happens to DTN bundles during a solar conjunction."**
→ Direct links blackout ~2 weeks. AETHERIX pre-positions critical data T-14 days, activates Lagrange relays (ES-L4/ES-L5) which maintain line-of-sight around the Sun (50–70% availability vs 0% for direct links), and Mars assets store data locally (64–256 GB buffers). Bundles shorter than the conjunction period expire — acceptable for P3/P4, not for P0.

## ✅ What You Should Be Able to Answer After This Lesson
1. What are the three TCP/IP assumptions that break in space, and why does each fail?
2. How long would a TCP three-way handshake take to Mars at average distance?
3. What is store-and-forward, and how does it differ from end-to-end retransmission?
4. Why is the bundle (not the packet) the fundamental unit in DTN?
5. What is the Earth-Mars synodic period, and why does it matter for solar conjunction planning?

## 📂 Deep Dive Resources
- `src/routing/bundle.py` — the `Bundle` and `EndpointID` classes
- `src/routing/forwarding_engine.py` — the `ForwardingEngine` store-and-forward loop
- `interview_prep/topic_summaries/dtn_fundamentals.md` — full topic summary with practice Q&A
- `docs/DESIGN_RATIONALE.md` — architectural decisions
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
