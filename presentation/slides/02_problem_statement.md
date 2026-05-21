# The Challenge — Why Space Communication is Hard

## The Problem: Earth-to-Mars Communication

### Extreme Challenges

| Challenge | Impact |
|-----------|--------|
| **Distance** | 54.6 M — 401 M km (7× range) |
| **One-way delay** | 3 — 22 minutes (light-time) |
| **Round-trip time** | 6 — 44 minutes |
| **Bandwidth** | Current: 0.5 — 6 Mbps (RF only) |
| **Blackouts** | 2-week solar conjunction |
| **Environment** | Radiation, extreme temperatures, power limits |

### Why TCP/IP Fails

| TCP/IP Assumption | Space Reality |
|-------------------|---------------|
| Low latency (< 1 s RTT) | 6 — 44 min RTT |
| Continuous connectivity | Scheduled contacts, frequent disruptions |
| End-to-end connection | No persistent path exists |
| Symmetric bandwidth | Highly asymmetric uplink/downlink |
| Reliable acknowledgments | ACKs take minutes to arrive |

### The Fundamental Gap

Current Mars missions rely on:
- **Static contact schedules** — manual planning, weeks in advance
- **Single-path routing** — no adaptability to failures
- **RF-only links** — bandwidth-limited to a few Mbps
- **Classical cryptography** — vulnerable to future quantum attacks

> **"We need a fundamentally different networking paradigm for interplanetary communication."**

---

### Key Numbers to Remember

- **54.6 M km** — minimum Earth-Mars distance (perihelion opposition)
- **401 M km** — maximum Earth-Mars distance (aphelion conjunction)
- **780 days** — Mars synodic period (opposition to opposition)
- **0.5 — 6 Mbps** — current Mars data rates (MRO via Ka-band RF)
