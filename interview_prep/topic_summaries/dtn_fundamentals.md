# DTN Fundamentals — Topic Summary

## Why TCP/IP Fails in Space

TCP/IP assumes three conditions absent in interplanetary links:

1. **Low round-trip time** — TCP congestion windows grow by one packet per RTT. At Mars (6–44 min RTT), a 10 MB transfer would take hours just to ramp up the window. TCP's fast retransmit relies on receiving three duplicate ACKs within one RTT, impossible when the RTT itself is 12 minutes.
2. **Continuous bi-directional connectivity** — Space links are scheduled contact windows (6–12 hours/day for Earth-Mars). TCP treats any gap as congestion and backs off exponentially.
3. **Symmetric channel capacity** — Mars uplink is often 1/100th of downlink. TCP ACKs are tiny but latency-critical; the asymmetric return path collapses the congestion window.

The IETF recognised this in RFC 4838 (DTN Architecture), which defines a network model tolerant of partitions, high delay, and intermittent connectivity.

## Store-and-Forward

BPv7 nodes hold bundles in persistent storage until the next contact opens. Each hop independently stores the bundle, acknowledges custody, and schedules the next forward. This decouples every link — a failure on hop 3 does not require hop 1 to retransmit.

AETHERIX applies this end-to-end: a science bundle from Mars rover `dtn://mars.surface.rover-01/science` is stored at the areostationary relay, then at the Lagrange relay (ES-L4), then at the GEO relay, then at the DSN ground station. Each node may hold the bundle for hours or days.

## Custody Transfer

Custody transfer shifts reliable-delivery responsibility from the original source to the current custodian. Once a downstream node accepts custody (returns a custody-acceptance signal), the upstream node may discard its copy. This matters because:

- Spacecraft have limited buffer space (typically 64–256 GB SSD).
- End-to-end ACKs at 22-minute one-way delay are impractical for flow control.
- Custody is per-hop, so retransmission is local to the failed link, not end-to-end.

In AETHERIX, the `CUSTODY_REQUESTED` flag (0x08, RFC 9171 §4.2.1) is set on all Priority 0–2 bundles. Priority 3–4 bundles use best-effort (no custody).

## Convergence Layers

BPv7 is protocol-agnostic at the transport layer. Convergence layer adapters (CLAs) map BPv7 to underlying transport:

| CLA | Use Case | Key Property |
|-----|----------|--------------|
| **LTP** (RFC 5326) | Deep-space hops (Mars ↔ Lagrange ↔ Earth) | Red/green segments, link-local retransmission, no end-to-end assumption |
| **TCPCL** (RFC 9174) | Earth segment (DSN ↔ MOC, intra-DSN) | Reliable TCP transport, bundle segmentation |
| **UDP-CL** | Optical inter-satellite links (LEO mesh, Mars ISL) | Low overhead, 1–10 Gbps ISL rates |

LTP is the critical one. It splits data into red (reliable, ACKed) and green (best-effort) blocks. For AETHERIX, science data uses green (volume-optimal) while commands/custody signals use red.

## BPv7 Bundle Structure

Per RFC 9171 and CCSDS 735.1-B-1:

- **Primary block** (CBOR-encoded): source EID, destination EID, creation timestamp, lifetime, hop count, fragmentation info, processing control flags.
- **Payload block**: application data (telemetry, images, commands).
- **Extension blocks** (optional): hop-by-hop security (BPSec), previous-node, bundle age.

AETHERIX endpoint IDs follow LNIS v5 (CCSDS 142.0-B-2): `dtn://mars.surface.rover-01/science`, `dtn://earth.dsn.goldstone/ops`, `dtn://transit.esl4.relay/forward`.

## Priority Classes

AETHERIX maps five priority levels (defined in `src/routing/bundle.py`):

| Priority | Class | Max Latency | Behaviour |
|----------|-------|-------------|-----------|
| P0 | Emergency | <1 min | Pre-empt all others, custody mandatory, red LTP |
| P1 | High Science | <30 min | Pre-empt P2–P4, custody, red LTP |
| P2 | Standard | <24 hr | Normal scheduling, custody, green LTP |
| P3 | Housekeeping | <7 days | Opportunistic, no custody |
| P4 | Bulk | <30 days | Fill idle capacity, no custody |

The RL agent uses `bundle_priority` (0–4) as a state variable. Dropping a P0 bundle incurs penalty δ = 10.0 in the reward function; dropping P4 costs δ = 0.1.

## Contact Graph Routing vs RL Routing

**CGR** (the current state-of-practice for DTN):
- Builds a contact graph from pre-planned contact schedules.
- Uses Dijkstra over the contact graph to find least-delay paths.
- Deterministic and provably optimal — if the schedule is accurate.

**CGR limitations that AETHERIX addresses with RL**:
- Cannot adapt to unplanned link failures (solar flares, equipment faults).
- No multi-objective optimisation (delay vs energy vs buffer).
- Schedule must be uploaded from Earth — 12-minute stale at best.
- Does not learn from experience.

**AETHERIX RL approach** (Q-learning → DQN):
- State: `(current_node, neighbors, link_qualities, buffer_occupancy, bundle_priority, bundle_deadline)`.
- Actions: `{FORWARD, STORE, DROP, SPLIT}`.
- Reward: `R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)` with α=1.0, β=0.001, γ=0.1, δ=10.0, ε=0.01.
- Learns from simulation over full 780-day synodic period.
- Falls back to CGR if RL confidence < 0.3.

Trade-off: RL requires training time and compute. The demo uses Q-tables; production would use DQN with experience replay.

---

## Practice Questions

### Q1. "Why can't you just use TCP with a very large window for Mars communication?"

Even with an infinite window, TCP's congestion control interprets the 6–44 minute RTT as persistent congestion. The retransmission timer (RTO) is derived from RTT variance; at interplanetary scales, RTO would be minutes to hours, and every timeout causes exponential backoff. Additionally, TCP requires continuous bi-directional connectivity — but Earth-Mars links are scheduled contacts of 6–12 hours. When the contact ends, TCP treats the gap as a failure. DTN's store-and-forward with custody transfer explicitly handles these disconnections by design.

### Q2. "Explain custody transfer as if I'm a network engineer familiar with TCP."

Custody transfer is like TCP's ACK, but hop-by-hop instead of end-to-end. In TCP, the receiver sends ACKs back to the original sender. In DTN custody transfer, each intermediate node acknowledges receipt to the previous hop and takes responsibility for forwarding. Once node B accepts custody from node A, node A can free its buffer. If B later fails to deliver to C, it is B's job (not A's) to retransmit. This localises retransmission to the failed link — critical when each link is 3–22 minutes one-way.

### Q3. "When would you use LTP green vs red segments in AETHERIX?"

Red segments (reliable) for anything requiring guaranteed delivery: command uplinks, custody signals, P0/P1 bundles (emergency and high-science data). The LTP receiver sends a report segment (RS) and the sender retransmits any missing data. Green segments (best-effort) for bulk science data where occasional loss is acceptable — a corrupted image frame can be discarded without retransmitting the entire file. In AETHERIX, the RL agent's routing decision uses the bundle's priority class to select red or green at each hop, not just at the source.

### Q4. "Your RL agent has four actions: forward, store, drop, split. When would 'split' be the right choice?"

Split is for multipath routing. When a large bundle (e.g., a 500 MB image mosaic from a Mars rover) cannot be delivered over a single contact window, the agent can fragment it across multiple next hops or multiple contact windows. This increases aggregate throughput and resilience — if one path degrades, the other fragments still arrive. Per RFC 9171, the `IS_FRAGMENT` flag (0x01) is set, and reassembly occurs at the destination. Trade-off: fragment overhead increases header bytes and requires reassembly logic, so split is only worthwhile for bundles above a size threshold or when no single path has sufficient remaining contact time.

### Q5. "What happens to DTN bundles during a solar conjunction?"

During solar conjunction (~2 weeks, every 780 days), the Sun is between Earth and Mars, causing radio interference and near-total direct-link blackout. AETHERIX handles this with a three-phase strategy: (1) Pre-position critical data T-14 days before conjunction, (2) activate Lagrange-point relays (ES-L4/ES-L5) which are 60° ahead/behind in orbit and maintain a line-of-sight around the Sun, achieving 50–70% availability versus 0% for direct links, (3) Mars-side assets operate autonomously for the conjunction period, storing data locally in their buffers (typically 64–256 GB). After conjunction, the backlog transmits during the first available contact window. Bundles with lifetime shorter than the conjunction period will expire — this is acceptable for housekeeping data (P3) but not for emergency alerts (P0), which are routed via the Lagrange path.
