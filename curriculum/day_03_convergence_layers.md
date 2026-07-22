# Day 3: Convergence Layers — LTP, TCPCL, and UDP-CL

## 📅 July 25, 2026

## 🎯 Learning Objective
Understand the convergence layer architecture that lets BPv7 bundles ride over heterogeneous transport protocols, and know exactly when AETHERIX uses LTP (deep space), TCPCL (Earth segment), and UDP-CL (optical inter-satellite links). This maps to **LO1** and is frequently probed in the "compare and justify" style of oral exam question.

## 📖 The Core Concept

### The Convergence Layer Concept

The Bundle Protocol is deliberately **transport-agnostic**. It does not define how bundles physically move between nodes — that is the job of a **Convergence Layer Adapter (CLA)**. A CLA sits below the bundle layer and maps BPv7 semantics onto a specific transport protocol. This separation is the architectural genius of DTN: the *same bundle* can traverse a 1550 nm optical link to a Lagrange relay, then a Ka-band RF link to a DSN station, then a TCP fibre link to a Mission Operations Center — each hop using the transport best suited to its link characteristics.

AETHERIX implements three convergence layers:

### 1. LTP — Licklider Transmission Protocol (RFC 5326)

Named after J.C.R. Licklider, LTP is designed for the most hostile transport environment: **high-delay, intermittent deep-space links**. Its key innovation is the **red/green segment model**:

- **Red segments** require reliable delivery. The sender transmits all red data, then a checkpoint. The receiver replies with a **Report Segment (RS)** listing which byte offsets arrived. Missing offsets trigger retransmission. This cycle repeats until all red data is acknowledged. Retransmission is **link-local** — only the failed hop retransmits, not the source.
- **Green segments** are best-effort. Sent once with no acknowledgement. Useful for bulk data where occasional loss is acceptable.

A single LTP **session** can carry both red and green blocks, avoiding the overhead of two separate session setups. This matters because session establishment costs one RTT on a deep-space link — 12 to 44 minutes.

LTP timers are set to at least the **one-way light time plus processing margin**: 3 minutes at opposition, 22 minutes at conjunction. The protocol does not assume continuous bi-directional connectivity — it was designed for exactly the Mars-to-Earth environment.

### 2. TCPCL — TCP Convergence Layer (RFC 7242 / RFC 9174)

TCPCL wraps TCP for **Earth-segment hops** where delay is milliseconds and the link is reliably available. It is used for:
- DSN station → Mission Operations Center (1–10 Gbps terrestrial links, <10 ms RTT)
- Intra-DSN transfers (Goldstone ↔ Madrid ↔ Canberra)
- MOC → data archive pipeline

TCPCL features: **session establishment** (SESSION_INIT/SESSION_ACK handshake), **bundle segmentation** (large bundles split into TCPCL data segments), **length-prefixed framing** (multiplexing over one TCP connection), and **keep-alive** messages (detect failure within seconds — appropriate for terrestrial RTT).

### 3. UDP-CL — UDP Convergence Layer

UDP-CL is for **optical inter-satellite links (ISL)** — the LEO laser mesh (48 satellites, 1–10 Gbps ISL) where the overhead of reliability mechanisms is unnecessary:
- No retransmission — ISL links have very low BER (<10⁻⁹) and short propagation delays (<5 ms intra-plane).
- Bundle-level CRC32 detects corruption; corrupted bundles are dropped and retransmitted end-to-end via custody transfer.
- Rate control is implicit: ISL bandwidth is known and stable.
- Jumbo frames (MTU up to 9000 bytes) reduce per-bundle framing overhead.

### When to Use Each — The Decision Matrix

| Link Type | CLA | Reliability | Typical Delay | AETHERIX Use |
|-----------|-----|-------------|---------------|--------------|
| Deep space (Mars↔Lagrange↔Earth) | LTP | Red/green selectable | 3–22 min OWLT | All interplanetary hops |
| Earth terrestrial (DSN↔MOC) | TCPCL | Full TCP reliability | <10 ms RTT | Ground segment routing |
| Optical ISL (LEO mesh) | UDP-CL | Best-effort + custody | <5 ms | High-throughput satellite crosslinks |

The bundle's **priority class** determines the LTP segment type: P0/P1 bundles → all red segments (guaranteed delivery). P2 bundles → metadata block red (for custody), payload green (retransmit not worth bandwidth). P3/P4 bundles → all green segments.

## 🔬 In AETHERIX

**LTP** is implemented in `src/routing/ltp.py` as `LTPSessionEngine`. Key details:
- `DEFAULT_MTU = 1400` bytes (accommodates CCSDS AOS frames)
- `segment_bundle()` splits a bundle payload into MTU-sized segments. The **first segment is marked as a checkpoint** (`is_checkpoint=True`) to bootstrap the acknowledgment cycle. The **last red segment carries `is_eors=True`** (end-of-red-session).
- `reconstruct_bundle()` sorts segments by offset before reassembly — handling out-of-order delivery common in deep-space links.
- `check_timeouts()` defaults to **1800 seconds (30 minutes)**, modelling a conservative Earth-Mars round-trip at maximum separation.
- `LTPOpcode` enum: DATA=0, REPORT=1, REPORT_ACK=2, CHECKPOINT=3, CHECKPOINT_ACK=4.
- `LTPReport` carries reception claims listing received byte ranges; `has_gaps()` triggers retransmission.
- `_compute_gaps()` walks sorted claims to find uncovered byte ranges.

**TCPCL** is in `src/routing/tcpcl.py` as `TCPConvergenceLayer`. It implements `register_endpoint()`, `connect()` (simulated handshake), `send_bundle()` (SESSION_INIT → SESSION_ACK → DATA_SEGMENT flow), and `receive_bundle()`. Message types: `DATA_SEGMENT`, `ACK`, `REFUSE_BUNDLE`, `SESSION_INIT`, `SESSION_ACK`. `TCPCLSession` tracks `bytes_transferred` and `is_complete`.

**UDP-CL** is in `src/routing/udp_cl.py` as `UDPConvergenceLayer`. Key details:
- `mtu_bytes = 1472` (standard UDP MTU minus headers)
- `loss_rate` parameter simulates link conditions; `send_datagram()` returns `False` if randomly lost
- `fragment_bundle()` splits payload into datagrams with `sequence_number`, `fragment_offset`, `total_length` metadata
- `reconstruct_bundle()` checks completeness against expected offsets before reassembly
- `UDPCLStats` tracks `datagrams_sent`, `datagrams_lost`, `bytes_sent/received`

## 📐 Key Numbers & Formulas
- **LTP MTU:** 1,400 bytes (DEFAULT_MTU)
- **LTP timeout:** 1,800 seconds (30 min) — models Earth-Mars max RTT
- **LTP opcodes:** DATA=0, REPORT=1, REPORT_ACK=2, CHECKPOINT=3
- **UDP-CL MTU:** 1,472 bytes
- **UDP-CL ISL rate:** 1–10 Gbps
- **TCPCL RTT (Earth segment):** < 10 ms
- **LEO ISL BER:** < 10⁻⁹
- **Priority → LTP mapping:** P0/P1 → all red; P2 → metadata red + payload green; P3/P4 → all green
- **RFC 5326:** LTP standard
- **RFC 7242:** TCPCL v3 (obsoleted by RFC 9174 for TCPCL v4)

## 🔗 Standards & References
- [RFC 5326 — Licklider Transmission Protocol](https://datatracker.ietf.org/doc/html/rfc5326)
- [RFC 7242 — TCP Convergence-Layer Protocol](https://datatracker.ietf.org/doc/html/rfc7242)
- [RFC 9174 — TCPCLv4](https://datatracker.ietf.org/doc/html/rfc9174)
- [CCSDS 734.0-B-1 — LTP for CCSDS](https://public.ccsds.org/Pubs/734x0b1.pdf)
- [RFC 9171 — Bundle Protocol v7 (CLA architecture)](https://datatracker.ietf.org/doc/html/rfc9171)

## 💡 How the Examiner Will Probe This

**Q: "Compare LTP and TCPCL as convergence layers. When would you use each?"**
→ LTP is for high-delay intermittent deep-space links — it provides red (reliable, ACKed) and green (best-effort) segments with link-local retransmission. Timers default to minutes/hours. TCPCL wraps TCP for reliable Earth-segment connections where delay is milliseconds. In AETHERIX, Mars↔Lagrange↔Earth hops use LTP; DSN↔MOC uses TCPCL. The same bundle transits both — that's the power of the convergence layer architecture.

**Q: "What's the advantage of LTP's red/green split over just using two separate channels?"**
→ A single LTP session can mix red and green blocks, avoiding the overhead of two session setups. Session establishment costs one RTT on a deep-space link — 12 to 44 minutes. Mixing within one session eliminates that doubled overhead.

## ✅ What You Should Be Able to Answer After This Lesson
1. What is a convergence layer adapter, and why is BPv7 transport-agnostic?
2. What is the difference between LTP red and green segments, and when would you use each?
3. What is the LTP default MTU and default timeout in AETHERIX, and why those values?
4. Why does UDP-CL not implement retransmission for optical inter-satellite links?
5. How does a single bundle transition from LTP to TCPCL as it moves from Mars to Earth?

## 📂 Deep Dive Resources
- `src/routing/ltp.py` — `LTPSessionEngine`, `LTPSegment`, `LTPReport`, `LTPSession`
- `src/routing/tcpcl.py` — `TCPConvergenceLayer`, `TCPCLSession`, `TCPCLMessage`
- `src/routing/udp_cl.py` — `UDPConvergenceLayer`, `UDPCLDatagram`
- `interview_prep/topic_summaries/dtn_fundamentals.md` — convergence layer comparison table
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
