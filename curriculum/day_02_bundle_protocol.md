# Day 2: Bundle Protocol v7 — Structure, Encoding, Flags & Priority

## 📅 July 24, 2026

## 🎯 Learning Objective
Master the internal structure of a BPv7 bundle — primary block, payload block, extension blocks — along with CBOR encoding, processing control flags, and the five-level priority system. This maps to **LO1** and is one of the most frequently probed topics in the oral interview.

## 📖 The Core Concept

### The Three-Part Bundle

A Bundle Protocol Version 7 bundle (RFC 9171) is **not** an IP packet. It is a structured message designed to survive extended storage and intermittent transmission. Every bundle consists of three logical parts:

1. **Primary Block** — the routing metadata. This is CBOR-encoded and contains the source EID (Endpoint ID), destination EID, creation timestamp, lifetime, hop-count limit, fragmentation info, and processing control flags. Think of it as the envelope: it tells every node where the bundle came from, where it's going, how long it's valid, and how it should be handled.

2. **Payload Block** — the application data: telemetry, images, commands, science measurements. This is the letter inside the envelope. In AETHERIX, payloads range from 2 MB emergency telemetry to 8 GB panoramic imagery.

3. **Extension Blocks** (optional) — additional metadata for security (BPSec), previous-node tracking, bundle age, and custody tracking. Extension blocks are extensible: new standards can add block types without changing the primary block format.

### CBOR Encoding

BPv7 encodes the primary block using **CBOR (Concise Binary Object Representation, RFC 8949)** — a compact binary data format. Unlike JSON (text-based, verbose), CBOR produces minimal wire size, which matters enormously when every byte costs 12.5 minutes of light-time to transmit. CBOR is self-describing: a decoder can parse the structure without a separate schema.

### Processing Control Flags

The primary block carries **processing control flags** — bit-fields that tell nodes how to handle the bundle. These are defined in RFC 9171 §3.1 and implemented in AETHERIX's `BundleFlags` enum. The critical flags for your exam:

| Flag | Hex Value | Meaning |
|------|-----------|---------|
| `IS_FRAGMENT` | `0x01` | This bundle is a fragment of a larger ADU |
| `PAYLOAD_IS_ADMIN` | `0x02` | Payload is an administrative record |
| `NO_FRAGMENT` | `0x04` | Bundle must not be fragmented |
| **`CUSTODY_REQUESTED`** | **`0x08`** | Source requests custodial retransmission |
| `DEST_IS_SINGLETON` | `0x10` | Destination is a single endpoint (not multicast) |
| `ACK_REQUESTED` | `0x20` | Administrative acknowledgement requested |
| `STATUS_REQUESTED` | `0x40` | Status report requested |

The **`CUSTODY_REQUESTED` flag (0x08)** is the single most important flag for your exam. When set, it tells every intermediate node: "do not delete your copy until a downstream node has confirmed custody." This is the mechanism that enables reliable delivery over intermittent links.

### The Five Priority Levels

AETHERIX defines five priority classes (P0–P4), each with distinct latency targets and handling rules. These are not arbitrary — they encode operational reality:

| Priority | Class | Target Latency | Custody | LTP Mode |
|----------|-------|---------------|---------|----------|
| **P0** | Emergency (spacecraft health, safety) | < 1 min | Mandatory | Red |
| **P1** | High Science (time-sensitive observations) | < 30 min | Yes | Red |
| **P2** | Standard (regular telemetry, daily data) | < 24 hr | Yes | Green |
| **P3** | Housekeeping (logs, status) | < 7 days | No | Green |
| **P4** | Bulk (archives, software updates) | < 30 days | No | Green |

The RL routing agent uses `bundle_priority` (0–4) as a **state variable**. Dropping a P0 bundle incurs the full drop penalty (δ = 10.0) in the reward function; dropping a P4 bundle costs far less. The priority also determines whether custody transfer is used and whether LTP segments are red (reliable) or green (best-effort).

### Endpoint IDs (EIDs)

Every bundle carries source and destination EIDs. AETHERIX follows the LNIS v5 format (CCSDS 142.0-B-2): `scheme://node_id/service_id`. Examples:
- `dtn://mars.surface.rover-01/science` — a Mars rover's science service
- `dtn://earth.dsn.goldstone/ops` — Goldstone DSN operations
- `dtn://transit.esl4.relay/forward` — the ES-L4 Lagrange relay's forwarding service

The `dtn://` scheme is the default; `ipn://` is an alternative for numeric IPN addressing.

## 🔬 In AETHERIX

The bundle structure is fully implemented in `src/routing/bundle.py`. The `BundlePriority` IntEnum defines all five levels:
```python
class BundlePriority(IntEnum):
    EMERGENCY = 0       # Spacecraft health, safety alerts
    HIGH_SCIENCE = 1    # Time-sensitive observations
    STANDARD = 2        # Regular telemetry and data
    HOUSEKEEPING = 3    # Status updates, logs
    BULK = 4            # Archived datasets, software updates
```

The `BundleFlags` IntEnum mirrors RFC 9171 exactly: `CUSTODY_REQUESTED = 0x08`, `IS_FRAGMENT = 0x01`, `DEST_IS_SINGLETON = 0x10`, etc.

The `Bundle` dataclass stores all primary-block fields: `bundle_id` (auto-generated 8-char hex), `source`/`destination` (EndpointID objects), `creation_time`, `lifetime_seconds` (default `86400 * 7` = 7 days), `priority`, `flags`, `payload`, `hops` list, and `custody_holders` list. The `__post_init__` method auto-calculates `payload_size_bytes`.

The `accept_custody()` method appends to `custody_holders` and records a `CUSTODY_ACCEPTED` hop. The `release_custody()` method removes the node from `custody_holders`. The `is_expired` property checks `time.time() > (creation_time + lifetime_seconds)`.

The `create_science_bundle()` factory function generates standard bundles with 7-day lifetime, useful for demonstrations.

## 📐 Key Numbers & Formulas
- **CUSTODY_REQUESTED flag:** `0x08` (bit 3)
- **IS_FRAGMENT flag:** `0x01` (bit 0)
- **DEST_IS_SINGLETON flag:** `0x10` (bit 4)
- **Default bundle lifetime:** `86400 × 7 = 604,800 seconds` (7 days)
- **Priority levels:** P0–P4 (EMERGENCY=0 through BULK=4)
- **Bundle ID format:** 8-character uppercase hex (e.g., `A3F2B1C9`)
- **CBOR standard:** RFC 8949
- **Bundle Protocol standard:** RFC 9171

## 🔗 Standards & References
- [RFC 9171 — Bundle Protocol Version 7](https://datatracker.ietf.org/doc/html/rfc9171)
- [RFC 8949 — Concise Binary Object Representation (CBOR)](https://datatracker.ietf.org/doc/html/rfc8949)
- [CCSDS 735.1-B-1 — Bundle Protocol](https://public.ccsds.org/Pubs/735x1b1.pdf)
- [CCSDS 142.0-B-2 — Space Link Identifiers](https://public.ccsds.org/Pubs/142x0b2.pdf)

## 💡 How the Examiner Will Probe This

**Q: "Explain the structure of a BPv7 bundle and how priority classes work."**
→ Three parts: primary block (CBOR-encoded routing metadata — source/dest EID, timestamp, lifetime, flags), payload block (application data), optional extension blocks (security, tracking). Five priority levels P0–P4 with distinct latency targets. The RL agent uses priority as a state variable to select routing actions and convergence layer modes — P0/P1 use LTP red segments with custody; P3/P4 use LTP green without custody.

**Q: "What flag would you set on an emergency bundle?"**
→ `CUSTODY_REQUESTED` (0x08) + `DEST_IS_SINGLETON` (0x10) + `ACK_REQUESTED` (0x20). These ensure guaranteed single-destination delivery with custody tracking and acknowledgement.

**Q: "Why CBOR instead of JSON or Protobuf?"**
→ CBOR is compact binary (minimal wire size — critical when every byte costs 12+ minutes light-time), self-describing (no external schema needed), and standardised in RFC 8949. JSON is text-based and verbose; Protobuf requires a separate schema file.

## ✅ What You Should Be Able to Answer After This Lesson
1. What are the three parts of a BPv7 bundle, and what does each contain?
2. What is the hex value of the CUSTODY_REQUESTED flag, and what happens when it is set?
3. Name all five priority levels (P0–P4) with their target latencies and custody rules.
4. What is the default bundle lifetime in AETHERIX, and how is expiry checked?
5. Why does BPv7 use CBOR encoding instead of JSON?

## 📂 Deep Dive Resources
- `src/routing/bundle.py` — `Bundle`, `BundlePriority`, `BundleFlags`, `EndpointID` classes
- `interview_prep/topic_summaries/dtn_fundamentals.md` — priority table and custody detail
- `interview_prep/practice/mock_interview.md` — Question 2 (Bundle Protocol)
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
