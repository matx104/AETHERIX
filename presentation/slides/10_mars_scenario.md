# Mars Mission Scenario — End-to-End Demo

## [LIVE DEMO] Mission Communication Scenario

> **Launch demo**: [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/) → "Mars Mission" tab

### Scenario: Perseverance Rover Science Data Upload

**Context**: Perseverance rover at Jezero Crater has collected 500 MB of high-priority science imagery and spectral data. The data must reach the Mission Operations Center (MOC) at JPL within 24 hours.

### Bundle Creation

| Field | Value |
|-------|-------|
| Source | `mars.surface.perseverance` |
| Destination | `earth.control.moc` |
| Priority | P2 (Standard Science) |
| Payload size | 500 MB |
| Lifetime | 24 hours |
| Custody | Requested (reliable delivery) |
| Security | QKD-encrypted session key |

### Data Flow Timeline

| Step | Time | Event | Node |
|:----:|:----:|-------|------|
| 1 | T+0s | Rover generates 500 MB science bundle | Mars Surface |
| 2 | T+2s | Bundle created with P2 priority, custody requested | Mars Surface |
| 3 | T+5s | RL agent selects route: via MRS-Alpha (link quality 0.85) | Mars Orbital |
| 4 | T+10s | UHF uplink to areostationary relay MRS-Alpha | Mars Orbital |
| 5 | T+12s | Inter-satellite optical link to polar orbiter | Mars Orbital |
| 6 | T+15s | Deep space optical downlink initiated (1550 nm) | Deep Space |
| 7 | T+750s | Bundle reaches Earth LEO constellation | Earth Orbital |
| 8 | T+752s | DSN Madrid receives and forwards via fiber | Earth Ground |
| 9 | T+754s | MOC delivery confirmed, custody transfer complete | Earth Ground |

### Network Path Visualization

```
Perseverance ──UHF──► MRS-Alpha ──Optical ISL──► MRS-Polar
                                                      │
                                            1550 nm laser
                                            225 M km
                                            12.5 min light-time
                                                      │
                                                      ▼
DSN Madrid ◄──Fiber── LEO Constellation ◄──── Deep Space Link
     │
     ▼
  JPL MOC ✓ Delivered
```

### Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Total transfer time** | ~13 minutes | vs 12.5 min fundamental light-time |
| **DTN overhead** | < 5% | Store-and-forward processing + custody ACKs |
| **Delivery ratio** | 98.7% | Across simulated 780-day synodic period |
| **Sustained throughput** | 15 Mbps | At average (225 M km) distance |
| **Hops traversed** | 7 | Surface → Orbital → Deep Space → LEO → DSN → MOC |
| **Routing decision time** | < 50 ms | RL agent inference |

### Why DTN Makes This Possible

1. **No end-to-end connection** — Each hop operates independently
2. **Custody transfer** — Each node takes responsibility, source buffer freed
3. **Priority scheduling** — P2 science data gets 6-8 hours/day of contact time
4. **RL routing** — Agent chose MRS-Alpha over MRS-Beta (0.85 vs 0.72 link quality)
5. **Store-and-forward** — If any link drops, bundle waits at last custodian

### Failure Scenario (What If?)

If the deep space optical link drops at T+400s (solar flare):
- Bundle stored at MRS-Polar (current custodian)
- RL agent detects link degradation, switches to ES-L4 relay path
- Bundle rerouted via Lagrange point relay
- Delivery delayed by ~30 minutes (not lost)
- **This is the fundamental advantage of store-and-forward DTN**
