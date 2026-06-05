# Network Topology — Five-Tier Architecture

## AETHERIX Network: 241 Nodes Across 5 Tiers

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 1: Earth Ground Segment (6 nodes)            │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      │
│  │ DSN Goldstone│◄────►│  DSN Madrid  │◄────►│ DSN Canberra │      │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘      │
│  ┌──────┴───────┐      ┌──────┴───────┐                          │
│  │  MOC / NOC   │      │     SOC      │                          │
│  └──────────────┘      └──────────────┘                          │
└─────────┼─────────────────────┼─────────────────────┼──────────────┘
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 2: Earth Orbital Assets (51 nodes)           │
│     ┌────────┐           ┌────────┐           ┌────────┐           │
│     │GEO Sat1│◄─────────►│GEO Sat2│◄─────────►│GEO Sat3│           │
│     └───┬────┘           └───┬────┘           └───┬────┘           │
│         └───────────────────┬┴──────────────────┬─┘                 │
│             LEO Laser Constellation (48 satellites)                  │
└─────────────────────────────┼────────────────────────────────────────┘
                              │ ⚡ Optical/RF Links
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 TIER 3: Deep Space Transit Relays (4 nodes)          │
│  ┌────────────┐         ┌────────────┐                             │
│  │ ES-L4 Relay│◄───────►│ ES-L5 Relay│                             │
│  └─────┬──────┘         └─────┬──────┘                             │
│  ┌─────┴──────┐         ┌─────┴──────┐                             │
│  │Transit Sat1│◄───────►│Transit Sat2│                             │
│  └─────┬──────┘         └─────┬──────┘                             │
└─────────┼─────────────────────┼────────────────────────────────────┘
          │                     │
          ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 4: Mars Orbital Assets (4 nodes)             │
│  ┌───────────┐   ISL   ┌───────────┐   ISL   ┌───────────┐        │
│  │MRS-Alpha  │◄───────►│MRS-Beta   │         │           │        │
│  │(Areostat) │         │(Areostat) │         │(Polar ×2) │        │
│  └─────┬─────┘         └─────┬─────┘         └─────┬─────┘        │
└────────┼─────────────────────┼─────────────────────┼──────────────┘
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 5: Mars Surface Network (176 nodes)          │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐             │
│  │ Base-α │    │ Base-β │    │Rovers  │    │ Drones │             │
│  └───┬────┘    └───┬────┘    └───┬────┘    └───┬────┘             │
│      └─────────────┴─────────────┴─────────────┘                    │
│           Distributed Sensor Network (UHF/Optical)                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Tier Summary

| Tier | Location | Nodes | Key Assets | Link Types |
|------|----------|:------:|------------|------------|
| 1 | Earth Ground | 6 | DSN stations + control centers | Fiber, RF |
| 2 | Earth Orbital | 51 | 3 GEO relays + 48 LEO laser sats | Optical ISL, RF |
| 3 | Deep Space | 4 | ES-L4, ES-L5 + transfer orbit relays | Optical, quantum |
| 4 | Mars Orbital | 4 | 2 areostationary + 2 polar orbiters | Optical ISL, RF |
| 5 | Mars Surface | 176 | Bases, rovers, drones, sensors | UHF, short-range optical |
| **Total** | | **241** | | |

### Routing & Graph Modules

- **Contact Graph Module** — Models scheduled contact windows between all node pairs with start time, duration, and data rate
- **BFS Routing** — Breadth-first search across the contact graph for minimum-hop path discovery
- **Shortest-path algorithms** — Weighted routing by latency, hop count, or link quality
- **Multi-path discovery** — Identifies redundant paths for fault tolerance

### Design Principles

- **Multiple redundant paths** — No single point of failure between Earth and Mars
- **Lagrange point relays** — Maintain communication during solar conjunction
- **Quantum repeater locations** — ES-L4/ES-L5 enable entanglement distribution
- **Areostationary orbit** — 17,032 km altitude, 24.6-hour period (Mars GEO equivalent)
- **Scalable** — Architecture supports 100+ assets as Mars infrastructure grows

### Link Performance

| Link Segment | Data Rate | Latency | Availability |
|:-------------|:---------:|:-------:|:------------:|
| Earth Ground ↔ Earth Orbit | 1-100 Gbps | ~120 ms | 99.9% |
| Earth ↔ Mars (optical) | 2-200 Mbps | 3-22 min | 85-95% |
| Mars Orbit ↔ Mars Surface | 2-100 Mbps | 2-40 ms | 70-90% |
| Inter-Satellite Links | 1-10 Gbps | 1-10 ms | 98% |
