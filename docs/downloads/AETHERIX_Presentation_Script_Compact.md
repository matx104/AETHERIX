# AETHERIX Presentation Script (Compact — 25 Slides)

> **Student:** Muhammad Abdullah Tariq  
> **Programme:** Diploma in AI Operations  
> **Topic:** EduQual Level 6 — Topic 59  
> **Duration:** ~10 minutes  
> **Slides:** 25  

---

## Slide 1: Introduction

**[0:00 — 30 seconds]**

Good morning. I'm Muhammad Abdullah Tariq, presenting AETHERIX — an architecture for interplanetary communication supporting Mars missions. AETHERIX stands for Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange. Today I'll walk you through how we solve the fundamental challenges of communicating across millions of kilometers of space.

---

## Slide 2: Agenda

**[0:30 — 20 seconds]**

Here's our roadmap for the next 18 minutes. We'll cover the challenge, the architecture, DTN protocols, network topology, link budgets, AI routing, quantum security, orbital mechanics, radiation hardening, data prioritization, and close with a live demo and performance comparison.

---

## Slide 3: What is AETHERIX

**[0:50 — 1 minute 30 seconds]**

AETHERIX addresses these challenges through four integrated innovations. First, Bundle Protocol version 7 provides delay-tolerant networking via store-and-forward. Second, reinforcement learning agents replace static routing with autonomous adaptive decisions. Third, quantum key distribution provides information-theoretically secure encryption. And fourth, hybrid optical-radio frequency links deliver 10 to 100 times higher data rates with RF backup for reliability.

---

## Slide 4: The Distance

**[2:20 — 1 minute 30 seconds]**

The distance to Mars varies from 55 million kilometers at closest approach to over 400 million kilometers when Earth and Mars are on opposite sides of the Sun. At the speed of light, that's a one-way delay of 3 to 22 minutes. TCP/IP expects millisecond round-trip times — it simply cannot work with 6 to 44 minute round-trips. Current Mars missions achieve only 0.5 to 6 megabits per second. And every 780 days, during solar conjunction, direct communication is impossible for about two weeks.

---

## Slide 5: The Answer

**[3:50 — 1 minute 30 seconds]**

The Bundle Protocol works like a postal service rather than a phone call. Instead of requiring a live connection between sender and receiver, each bundle is stored at every intermediate node until the next link becomes available. Custody transfer is critical: each node that accepts a bundle takes legal responsibility for its delivery. The previous custodian can then free its buffer.

---

## Slide 6: System Architecture

**[5:20 — 1 minute]**

The architecture has five core modules feeding into a simulation engine. Infrastructure handles optical and RF link budget calculations. Routing implements the RL agent, BPv7 bundles, and the store-and-forward engine. Security covers QKD protocols and repeater chains. Orbital computes contact windows and Doppler shifts. And Simulation integrates everything for end-to-end scenario analysis.

---

## Slide 7: Architecture Diagram

**[6:20 — 1 minute]**

This diagram shows how the source modules feed into the simulation engine and web demos. Each module is independently testable — we have 189 automated tests validating correctness.

---

## Slide 8: BPv7 Deep Dive

**[7:20 — 2 minutes]**

BPv7 is the postal service protocol. Walk through the stack: Application at top, BPv7 as the store-and-forward layer, three convergence layers for different link types, physical at bottom. Custody transfer is the key innovation — each node takes legal responsibility. Priority P0 emergency to P4 bulk. We use three convergence layers: LTP for deep space, TCPCL for Earth-segment connections, and UDP-CL for inter-satellite optical links.

---

## Slide 9: Network Topology

**[9:20 — 2 minutes]**

The network spans five tiers with 241 nodes. Earth's ground segment with DSN stations in Goldstone, Madrid, and Canberra — spaced 120 degrees apart for 24/7 coverage. Tier 2 has GEO relays and a 48-satellite LEO laser constellation. Tier 3 has Lagrange point relays at ES-L4 and ES-L5 — critical because they maintain communication around the Sun during conjunction. Tier 4 is Mars orbital with areostationary relays at 17,032 km. Tier 5 is the Mars surface network.

---

## Slide 10: 5-Tier Network Diagram

**[11:20 — 1 minute]**

Earth-to-deep-space links at 100 Mbps via 1550 nm laser. Deep-space-to-Mars is distance-dependent at 2 to 200 Mbps. Mars orbital to surface uses UHF S-band at 2 Mbps. LEO inter-satellite mesh runs at 10 Gbps with laser links.

---

## Slide 11: Optical Communications

**[12:20 — 2 minutes]**

Let me demonstrate the link budget calculations live. At closest approach — 54.6 million kilometers — our 5-watt laser with a 22-centimeter transmit aperture and 1-meter ground receive telescope achieves 100 to 200 megabits per second. That's over 30 times faster than the current Mars Reconnaissance Orbiter. Even at maximum distance of 401 million kilometers, we maintain 2 to 5 megabits per second.

---

## Slide 12: Data Rate vs Distance Chart

**[14:20 — 20 seconds]**

Data rate degrades from 200 Mbps at closest approach to 2 Mbps at maximum distance — but even minimum is competitive with current RF.

---

## Slide 13: Earth-Mars Journey

**[14:40 — 1 minute]**

Here's the 7-hop journey. 500 MB from Perseverance to JPL. Total transit about 13 minutes versus 12.5 minutes light-time — near speed of light! DTN overhead under 5 percent. 98.7 percent delivery ratio.

---

## Slide 14: RL Routing

**[15:40 — 2 minutes]**

Traditional Contact Graph Routing requires pre-computed contact schedules that cannot adapt to unexpected conditions. Our reinforcement learning agent learns from experience. It observes state variables including link quality, buffer occupancy, bundle priority, and deadline. It selects from four actions: forward, store, drop, or split. The reward function balances delivery success against delay, hop count, and energy consumption.

---

## Slide 15: RL Routing Heatmap Chart

**[17:40 — 20 seconds]**

The Q-value heatmap shows how the RL agent converges on optimal routing decisions. Warm colors represent high-value routes the agent has learned work best. Cool colors are poor choices the agent avoids.

---

## Slide 16: Quantum Security

**[18:00 — 2 minutes]**

Quantum key distribution provides security based on the laws of physics, not computational difficulty. In the BB84 protocol, Alice sends quantum bits in random bases. Bob measures in random bases. They publicly compare a sample to estimate the Quantum Bit Error Rate. If the QBER is below 11 percent, the key is secure. We deploy QKD in three phases: Earth-to-LEO, GEO, and ultimately quantum repeaters at Lagrange points for Earth-Mars security.

---

## Slide 17: QKD Security Chart

**[20:00 — 20 seconds]**

QBER analysis showing the security threshold. Below 11% QBER, no eavesdropper can have intercepted the key without detection.

---

## Slide 18: Orbital Mechanics

**[20:20 — 1 minute 30 seconds]**

The 780-day synodic period means we cycle from best-case opposition through worst-case conjunction. During the roughly two-week conjunction window, direct communication is impossible. AETHERIX's Lagrange point relays at ES-L4 and ES-L5 maintain a path around the Sun, providing 50 to 70 percent availability even during conjunction. Doppler shift of 15 gigahertz at 1550 nm requires real-time compensation.

---

## Slide 19: Data Flow Diagram Visual

**[21:50 — 20 seconds]**

The visual data flow through the complete protocol stack.

---

## Slide 20: Performance

**[22:10 — 1 minute]**

The bottom line: AETHERIX delivers 10 to 100 times higher data rates with greater than 95 percent availability at one-tenth the cost per megabyte. Our architecture scales to 241 nodes compared to the 5 to 10 assets currently connected. The routing is autonomous. The security is quantum-ready.

---

## Slide 21: Performance Comparison Chart

**[23:10 — 20 seconds]**

Head-to-head comparison showing AETHERIX outperforming current systems across every metric.

---

## Slide 22: Implementation

**[23:30 — 1 minute]**

This is real, working code. 27 Python modules, 189 tests, 12 interactive demos. All the physics is real — no mocked data. The showcase site has live calculators you can use right now. Standards compliance is complete — seven CCSDS Blue Books and four IETF RFCs.

---

## Slide 23: Roadmap

**[24:30 — 1 minute]**

Phases 1 through 4 are done — this is what you see today. Phase 5 adds ns-3 simulation for realistic network modeling. Phase 6 upgrades to a Deep Q-Network and integrates with NASA's ION-DTN implementation. Phase 7 moves to hardware prototypes with software-defined radios and optical ground station demonstrations.

---

## Slide 24: Conclusion

**[25:30 — 1 minute]**

In summary, AETHERIX delivers four key outcomes: 10 to 100 times faster communications through optical links, over 95 percent availability through multi-path redundancy, AI-driven autonomous routing replacing static schedules, and quantum-secured future-proof encryption.

---

## Slide 25: Thank You

**[26:30 — 30 seconds]**

Thank you. I welcome your questions. All simulations are available live at matx104.github.io/AETHERIX.

---
