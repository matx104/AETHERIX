# DTN & Bundle Protocol — The Foundation

## Delay-Tolerant Networking (DTN)

### Why DTN?

Traditional internet protocols (TCP/IP) require continuous end-to-end connectivity. Space networks have:
- Intermittent links (scheduled contacts, orbital geometry)
- Long propagation delays (3-22 min one-way)
- Asymmetric data rates (downlink >> uplink)
- High error rates (radiation, atmospheric effects)

DTN solves this by **decoupling communication from connectivity**.

### Bundle Protocol v7 (RFC 9171) — Protocol Stack

```
┌─────────────────────────────────────────────────┐
│              Application Layer                   │
│         (Science data, commands, imagery)         │
├─────────────────────────────────────────────────┤
│         Bundle Protocol v7 (BPv7)                │
│   • Store-and-forward                            │
│   • Custody transfer                             │
│   • Priority scheduling (P0-P4)                  │
│   • Bundle fragmentation                         │
│   • Security blocks (BPSec)                      │
├─────────────────────────────────────────────────┤
│         Convergence Layer Adapters               │
│   • LTP  — Deep space (long-delay, reliable)     │
│   • TCPCL — Earth segment (reliable, ordered)    │
│   • UDP-CL — Optical ISL (low overhead)          │
├─────────────────────────────────────────────────┤
│         Physical Layer                           │
│   • Optical (1550 nm laser) — Primary            │
│   • RF (Ka/X-band) — Backup                      │
└─────────────────────────────────────────────────┘
```

### How Store-and-Forward Works

1. **Source** creates a bundle (payload + metadata: destination, priority, lifetime)
2. **Forward** to next hop when link becomes available
3. **Store** locally in persistent storage during outages
4. **Custody transfer** — receiving node accepts responsibility
5. **Repeat** hop-by-hop until destination reached
6. No end-to-end connection required at any point

### Custody Transfer

| Concept | Description |
|---------|-------------|
| **Custodian** | Node currently responsible for bundle delivery |
| **Acceptance** | Next-hop acknowledges custody acceptance |
| **Release** | Previous custodian can discard the bundle |
| **Retransmission** | Current custodian retransmits if no acceptance |
| **Benefit** | Source buffer freed; reliability is hop-by-hop |

### Priority Classes (BPv7)

| Priority | Name | Max Acceptable Delay | Example |
|----------|------|---------------------|---------|
| 0 | Emergency | < 1 min | Anomaly alerts, emergency commands |
| 1 | Expedited | < 30 min | Time-critical science (solar events) |
| 2 | Standard | < 24 hours | Daily science data, imagery |
| 3 | Normal | < 7 days | Housekeeping telemetry, logs |
| 4 | Bulk | < 30 days | Archive data, software updates |

### Standards Compliance

- **CCSDS 734.2-B-1** — DTN Architecture
- **CCSDS 735.1-B-1** — Bundle Protocol Specification
- **CCSDS 735.2-B-1** — Bundle Protocol Security (BPSec)
- **RFC 9171** — Bundle Protocol Version 7
- **RFC 5326** — Licklider Transmission Protocol (LTP)
