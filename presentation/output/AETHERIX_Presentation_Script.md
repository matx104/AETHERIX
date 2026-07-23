# AETHERIX Presentation Script
## Speaker Notes — Full Script with Timing

**Total Time: ~18 minutes**
**Presenter: Muhammad Abdullah Tariq**
**Date: January 2026**

---

## Slide 1: Title — 30 seconds

**Say:**

"Good morning. I'm Muhammad Abdullah Tariq, presenting AETHERIX — an architecture for interplanetary communication supporting Mars missions. AETHERIX stands for Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange. Today I'll walk you through how we solve the fundamental challenges of communicating across millions of kilometers of space."

**Body Language:** Stand centered, hands visible. Brief pause after the acronym. Make eye contact with each examiner.

---

## Slide 2: Agenda — 20 seconds

**Say:**

"Here's our roadmap for the next 18 minutes. We'll start with the challenge — why space breaks the internet. Then walk through the architecture: DTN protocols, the 5-tier network topology, optical link budgets, AI-driven routing, quantum security, orbital mechanics, and two specialized modules — radiation hardening and data prioritization. We'll close with a live demo and performance comparison."

---

## Slide 3: What is AETHERIX? — 1.5 minutes

**Say:**

"AETHERIX addresses these challenges through four integrated innovations. First, Bundle Protocol version 7 provides delay-tolerant networking via store-and-forward. Second, reinforcement learning agents replace static routing with autonomous adaptive decisions. Third, quantum key distribution provides information-theoretically secure encryption. And fourth, hybrid optical-radio frequency links deliver 10 to 100 times higher data rates with RF backup for reliability. I have a live interactive demo running at matx104.github.io/AETHERIX where all of these simulations run in the browser — I'll demonstrate specific modules as we go."

**Gesture toward each technology as you mention it.**

---

## Slide 4: The Distance — 1.5 minutes

**Say:**

"Before discussing solutions, let's understand why space communication is fundamentally different from terrestrial networking. The distance to Mars varies from 55 million kilometers at closest approach to over 400 million kilometers when Earth and Mars are on opposite sides of the Sun. At the speed of light, that's a one-way delay of 3 to 22 minutes. TCP/IP expects millisecond round-trip times — it simply cannot work with 6 to 44 minute round-trips. Current Mars missions like the Mars Reconnaissance Orbiter achieve only 0.5 to 6 megabits per second using Ka-band radio frequency links. And every 780 days, during solar conjunction, direct communication is impossible for about two weeks."

**Emphasis:** Stress "7x range" — pause on this. "TCP assumes continuous connectivity — space has scheduled contacts."

---

## Slide 5: The Answer (DTN) — 1.5 minutes

**Say:**

"The Bundle Protocol works like a postal service rather than a phone call. Instead of requiring a live connection between sender and receiver, each bundle — which is a unit of data with metadata like priority, destination, and lifetime — is stored at every intermediate node until the next link becomes available. Custody transfer is critical: each node that accepts a bundle takes legal responsibility for its delivery. The previous custodian can then free its buffer. This means reliability is built hop-by-hop, not end-to-end."

**Draw the protocol stack if whiteboard available:** Application -> BPv7 -> Convergence Layer -> Physical

---

## Slide 6: System Architecture — 1 minute

**Say:**

"The architecture has five core modules feeding into a simulation engine. Infrastructure handles optical and RF link budget calculations. Routing implements the RL agent, BPv7 bundles, and the store-and-forward engine. Security covers QKD protocols and repeater chains. Orbital computes contact windows and Doppler shifts. And Simulation integrates everything for end-to-end scenario analysis. All modules are standards-compliant with CCSDS and IETF."

---

## Slide 7: Architecture Diagram — 30 seconds

**Say:**

"This diagram shows how the source modules feed into the simulation engine and web demos. Each module is independently testable — we have 189 automated tests validating correctness."

---

## Slide 8: BPv7 Deep Dive — 2 minutes

**Say:**

"BPv7 is the postal service protocol. Walk through the stack: Application at top, BPv7 as the store-and-forward layer, three convergence layers for different link types, physical at bottom. Custody transfer is the key innovation — each node takes legal responsibility. Priority P0 (emergency) to P4 (bulk). We use three convergence layers optimized for different link conditions: LTP for deep space where delays are longest, TCPCL for reliable Earth-segment connections, and UDP-CL for fast inter-satellite optical links."

**Know these cold for Q&A:**
- BPv7 specified in RFC 9171 (2022)
- LTP specified in RFC 5326 (2008)
- DTN Architecture: CCSDS 734.2-B-1

---

## Slide 9: DTN Store-and-Forward — 1.5 minutes

**Say:**

"Walk through the store-and-forward process. Bundle arrives, gets stored, node waits for next contact opportunity, then forwards. If link drops, bundle stays stored and retries. No data loss. This is fundamentally different from TCP's end-to-end retransmission. LTP handles the deep-space hop with reliable segments and retransmission. TCPCL manages Earth-segment distribution. UDP-CL models optical inter-satellite links with fragmentation and loss simulation."

---

## Slide 10: Network Topology — 2 minutes

**Say:**

"The network spans five tiers with 241 nodes. Starting at Tier 1, Earth's ground segment with DSN stations in Goldstone, Madrid, and Canberra — spaced 120 degrees apart for 24/7 coverage. Tier 2 has three GEO relays and a 48-satellite LEO laser constellation for inter-satellite links. Tier 3 is the deep space transit layer — this is where our Lagrange point relays at ES-L4 and ES-L5 live, along with quantum repeaters for entanglement distribution. These are critical because they maintain a communication path around the Sun during solar conjunction. Tier 4 is the Mars orbital constellation with areostationary relays at 17,032 kilometers altitude. Finally, Tier 5 is the Mars surface network with bases, rovers, drones, and sensors."

**Point to each tier in the diagram as you describe it.**

---

## Slide 11: 5-Tier Network Detail — 1 minute

**Say:**

"Here are the exact numbers. Earth-to-deep-space links at 100 Mbps via 1550 nm laser. Deep-space-to-Mars is distance-dependent at 2 to 200 Mbps. Mars orbital to surface uses UHF S-band at 2 Mbps. And the LEO inter-satellite mesh runs at 10 Gbps with laser links."

---

## Slide 12: Network Diagram Visual — 30 seconds

**Say:**

"This visualization shows the full 5-tier topology with three redundant paths. No single link failure can sever Earth-Mars communication."

---

## Slide 13: Optical Communications — 2 minutes — **LIVE DEMO**

**Say:**

"Let me demonstrate the link budget calculations live."

[Open matx104.github.io/AETHERIX -> Link Budget tab]

"At closest approach — 54.6 million kilometers — our 5-watt laser with a 22-centimeter transmit aperture and 1-meter ground receive telescope achieves 100 to 200 megabits per second. That's over 30 times faster than the current Mars Reconnaissance Orbiter. Even at maximum distance of 401 million kilometers, we maintain 2 to 5 megabits per second. We choose 1550 nanometers because it's the standard telecom wavelength — mature components, eye-safe at these powers, and there's an atmospheric window at this wavelength for ground reception."

**If demo fails:** "At 225 million km, FSPL is -365 dB. With our transmit and receive gains, we achieve 10-20 Mbps — 10x current RF performance."

---

## Slide 14: Earth-Mars Journey — 1.5 minutes

**Say:**

"Here's the 7-hop journey. 500 MB from Perseverance to JPL. Total transit about 13 minutes versus 12.5 minutes light-time — near speed of light! DTN overhead under 5 percent. 98.7 percent delivery ratio."

---

## Slide 15: RL-Based Routing — 2 minutes

**Say:**

"Traditional Contact Graph Routing requires pre-computed contact schedules that cannot adapt to unexpected conditions. Our reinforcement learning agent learns from experience. It observes eight state variables including current link quality, buffer occupancy, bundle priority, and deadline. It then selects from four actions: forward to a neighbor, store locally for a better link, drop an expired bundle, or split a large bundle across multiple paths. The reward function balances delivery success against delay, hop count, and energy consumption."

**Know the reward weights:** alpha=1.0, beta=0.001, gamma=0.1, delta=10.0, epsilon=0.01

---

## Slide 16: Quantum Security — 2 minutes

**Say:**

"Quantum key distribution provides security based on the laws of physics, not computational difficulty. In the BB84 protocol, Alice sends quantum bits in random bases. Bob measures in random bases. About half the time their bases match, and those bits become the raw key. They publicly compare a sample to estimate the Quantum Bit Error Rate. If the QBER is below 11 percent, the key is secure — any eavesdropper would have disturbed the quantum states enough to be detected. We deploy QKD in three phases: proven Earth-to-LEO links first, advancing to GEO, and ultimately using quantum repeaters at Lagrange points for Earth-Mars security."

**Know the 11% QBER threshold — you WILL be asked.**

---

## Slide 17: Orbital Mechanics — 1.5 minutes

**Say:**

"Mars communications are governed by orbital mechanics. The 780-day synodic period means we cycle from best-case opposition through worst-case conjunction. During the roughly two-week conjunction window, direct communication is impossible. AETHERIX's Lagrange point relays at ES-L4 and ES-L5 maintain a path around the Sun, providing 50 to 70 percent availability even during conjunction. Doppler shift of 15 gigahertz at our 1550 nanometer wavelength requires real-time compensation."

**Know:** Min: 54.6M km (3 min), Max: 401M km (22 min), Synodic: 779.94 days

---

## Slide 18: Radiation-Hardened Computing — 1.5 minutes

**Say:**

"Space radiation is relentless. Single-event upsets flip bits constantly — about 37,000 during a Mars transit. Our defense-in-depth: triple modular redundancy masks logic faults with a 3,334x reliability gain. SECDED ECC corrects single-bit errors. Scrubbing prevents double-bit accumulation. And FDIR with a watchdog catches everything else. The RAD750 processor can tolerate 200 kilorads — far above what a Mars mission needs."

---

## Slide 19: Data Prioritization — 1.5 minutes

**Say:**

"Like an emergency room. P0 emergency gets sent immediately — it can even preempt an in-progress transfer. P1 mission-critical next. P2 routine science. P4 bulk data fills remaining bandwidth. Compression multiplies effective capacity: 3x for telemetry, 10x for images, 50x for video. Our scheduler keeps the link at 100 percent utilization by fragmenting large bundles."

---

## Slide 20: End-to-End Mission — 2 minutes — **LIVE DEMO**

**Say:**

"Let's walk through a complete mission scenario — transferring 500 megabytes of science data from the Perseverance rover to the Mission Operations Center at JPL. The bundle traverses 7 hops — surface to orbiter, orbiter to deep space link, deep space to Earth LEO constellation, then through DSN Madrid to JPL. Total time: about 13 minutes. The fundamental light-time is 12.5 minutes, so the DTN processing overhead is less than 5 percent. Now here's the critical point — if the deep space optical link drops at any point, the bundle is NOT lost. It's stored at the last custodian node and the RL agent reroutes through an alternate path."

---

## Slide 21: Data Flow Diagram — 1 minute

**Say:**

"This shows the end-to-end bundle journey through all protocol layers. From application data, through BPv7 wrapping, RL routing decision, QKD encryption, LTP segmentation, physical transmission across multiple link types, and finally reassembly and delivery."

---

## Slide 22: Data Flow Visual — 30 seconds

**Say:**

"The visual data flow through the complete protocol stack."

---

## Slide 23: Performance Comparison — 1 minute

**Say:**

"The bottom line: AETHERIX delivers 10 to 100 times higher data rates with greater than 95 percent availability at one-tenth the cost per megabyte. Our architecture scales to 241 nodes, compared to the 5 to 10 assets currently connected. The routing is autonomous and adaptive rather than static. And the security is quantum-ready — future-proof against the quantum computing threat."

**Speak confidently on numbers — they're your strongest evidence. Don't rush through them.**

---

## Slide 24: Implementation — 1.5 minutes

**Say:**

"This is real, working code. 27 Python modules, 480 tests, 12 interactive demos. All the physics is real — no mocked data. The showcase site has live calculators you can use right now. Standards compliance is complete — CCSDS, IETF, and NIST. We reference seven CCSDS Blue Books and four IETF RFCs."

---

## Slide 25: Roadmap — 1.5 minutes

**Say:**

"Phases 1 through 4 are done — this is what you see today. Phase 5 adds ns-3 simulation for realistic network modeling. Phase 6 upgrades to a Deep Q-Network and integrates with NASA's ION-DTN implementation. Phase 7 moves to hardware prototypes with software-defined radios and optical ground station demonstrations."

---

## Slide 26: Conclusion — 1 minute

**Say:**

"In summary, AETHERIX delivers four key outcomes: 10 to 100 times faster communications through optical links, over 95 percent availability through multi-path redundancy, AI-driven autonomous routing replacing static schedules, and quantum-secured future-proof encryption."

---

## Slide 27: Thank You — 30 seconds

**Say:**

"Thank you. I welcome your questions. All simulations are available live at matx104.github.io/AETHERIX."

**End with confidence. Pause. Make eye contact. Wait for the first question.**

---

## Quick Numbers Reference

| Number | Context |
|--------|---------|
| 299,792 km/s | Speed of light |
| 54.6 M km | Mars minimum distance (3 min) |
| 401 M km | Mars maximum distance (22 min) |
| 780 days | Synodic period |
| 1550 nm | Optical wavelength |
| 11% | QBER security threshold |
| 17,032 km | Areostationary orbit altitude |
| 241 | Total network nodes |
| 5 W | Typical laser power |
| 0.5-6 Mbps | Current Mars data rates |
| 2-200 Mbps | AETHERIX data rates |
| 189 | Automated tests |
| 27 | Python modules |

## Standards to Cite

- "As specified in CCSDS 734.2-B-1..."
- "Per RFC 9171, the Bundle Protocol..."
- "Following CCSDS 141.0-B-1 optical communications..."
- "According to the Shor-Preskill proof..."

## Handling Difficult Questions

**If you don't know the answer:** "That's an excellent question. I'd need to verify the specific details, but based on the architecture..."

**If challenged on a number:** "The specific value depends on the mission configuration. For our baseline scenario using DSOC-derived parameters..."

**If asked about implementation gaps:** "This is currently at proof-of-concept stage. Production deployment would require [DQN / ION-DTN integration / hardware-in-the-loop testing]."

## Demo Fallback

If the live demo fails, verbally walk through: "At average distance of 225 million kilometers, the free-space path loss is minus 365 decibels. With our 22-centimeter transmit aperture and 1-meter receive telescope, we achieve 10 to 20 megabits per second — that's 10 times current RF performance. The RL agent trains using Q-learning with epsilon-greedy exploration, and the BB84 QKD simulation shows that with zero channel error and no eavesdropper, we achieve a QBER below 1 percent, well within the 11 percent security threshold."
