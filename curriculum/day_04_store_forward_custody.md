# Day 4: Store-and-Forward & Custody Transfer

## 📅 July 26, 2026

## 🎯 Learning Objective
Understand the runtime mechanics of DTN: how the store-and-forward engine receives, queues, routes, and delivers bundles, and how custody transfer localises retransmission to the failed hop. This maps to **LO1** and is critical for explaining "how your system actually works" during the interview.

## 📖 The Core Concept

### Store-and-Forward: The Operational Loop

Store-and-forward is the heartbeat of DTN. Unlike TCP's live session model where data flows continuously from source to destination, DTN nodes operate in a **receive-hold-decide-send** cycle. Each node is an autonomous agent that:

1. **Receives** a bundle from a neighbour (or generates one locally).
2. **Checks** if this node is the final destination — if so, deliver and stop.
3. **Checks** if the bundle has expired (lifetime exceeded) — if so, discard with a status report.
4. **Stores** the bundle in a priority queue in persistent storage.
5. **Consults** the routing policy (RL agent or CGR fallback) to decide: forward, store, drop, or split.
6. **Dispatches** the bundle to the appropriate convergence layer when a contact window opens.
7. **Handles custody** — if the bundle has `CUSTODY_REQUESTED` set, the node retains a copy until a downstream node confirms custody.

This loop runs as a non-blocking event loop at every DTN node. Bundle arrivals, contact-window openings, custody timeouts, and routing decisions are all events processed in priority order.

### Custody Transfer: Hop-by-Hop Reliability

Custody transfer is the DTN equivalent of TCP's ACK, but **hop-by-hop instead of end-to-end**. Here is the critical distinction:

- **TCP:** Receiver sends ACKs all the way back to the original sender. A retransmission traverses the entire path.
- **DTN custody:** Each intermediate node acknowledges receipt to the *previous hop only* and takes responsibility for onward delivery. Once node B accepts custody from node A, **node A can free its buffer**. If B later fails to deliver to C, it is B's job (not A's) to retransmit.

Why does this matter? In interplanetary DTN, each link is 3–22 minutes one-way. End-to-end ACKs at 22-minute one-way delay are impractical for flow control. Custody transfer **localises retransmission to the failed link** — if the B→C hop fails, only B retransmits to C; A is not involved. This is operationally critical because:
- Spacecraft have limited buffer space (typically 64–256 GB SSD)
- End-to-end ACKs would take 6–44 minutes per round trip
- Custody is per-hop, so retransmission latency is bounded by a single hop, not the full path

### The Custody Lifecycle

1. **Custody Request:** The source sets `CUSTODY_REQUESTED` (flag 0x08) in the bundle's processing control flags.
2. **Custody Acceptance:** The receiving node returns a Custody Acceptance administrative record. The bundle is added to the node's custody set.
3. **Custody Refusal:** If the receiver's buffer is full or the bundle fails validation, it returns a Custody Refusal with a reason code (buffer full, lifetime expired, unsupported block type). The sender selects an alternate next-hop or stores the bundle.
4. **Custody Release:** Once the current custodian receives Custody Acceptance from the next downstream node, it may safely delete the bundle from persistent storage.
5. **Retransmission Timer:** If no Custody Acceptance arrives within `min(remaining_lifetime / 2, contact_window_end)` seconds, the custodian retransmits on the next available contact.

In AETHERIX, `CUSTODY_REQUESTED` is set on all Priority 0–2 bundles. Priority 3–4 bundles use best-effort (no custody).

### Buffer Management

Each node maintains buffers organised by priority. The scheduler drains queues in strict priority order. When buffer occupancy exceeds **90% capacity**, a tail-drop policy applies starting from the lowest priority (P4) upward. **P0 and P1 queues are protected — they are never dropped due to congestion.** If the buffer reaches 100%, P2 bundles are selectively expired (oldest lifetime first) before touching P0/P1.

This mirrors operational reality: a Mars relay with a full buffer is one dust storm away from catastrophic data loss. The priority-aware dropping ensures emergency data always gets through.

## 🔬 In AETHERIX

The store-and-forward engine is implemented in `src/routing/forwarding_engine.py`.

**`BundleQueue`** is a priority-sorted queue using Python's `bisect.insort`. The `_sort_key()` orders bundles by `(priority.value, creation_time + lifetime_seconds)` — lowest priority value first (EMERGENCY=0), then earliest absolute deadline. This ensures the most urgent, soonest-expiring bundle is always at the head. Key methods: `enqueue()` (sorted insert), `dequeue()` (pop head), `peek()` (look at head), `remove_expired()` (purge bundles where `is_expired`).

**`ForwardingEngine`** is the core runtime, bound to a single local node. It owns a `BundleQueue`, a routing agent reference, and a custody set (`_custody_bundles` dict). Key methods:
- `receive_bundle(bundle, from_node)` — adds a `RECEIVED` hop; if this node is the destination, marks `delivered`; otherwise enqueues.
- `process_queue(neighbors)` — drains the queue: for each bundle, builds a `NetworkState`, queries the RL agent, executes the decision.
- `_execute_forward(bundle, next_hop, neighbor)` — checks if neighbour can accept (buffer space, reachability); if not, re-queues with "stored" event. Calls `neighbor.store_bundle()` and `local_node.forward_bundle()`.
- `_execute_store(bundle)` — stores locally for deferred transmission; if local buffer full, drops.
- `_execute_drop(bundle)` — records `DROPPED` hop, releases buffer.
- `accept_custody(bundle)` — adds to `_custody_bundles`, records `CUSTODY_ACCEPTED` event.
- `release_custody(bundle, next_hop)` — removes from custody set, records `CUSTODY_RELEASED`.
- `tick(current_time, neighbors)` — one time-step: purge expired, then drain queue.

**`ForwardingEvent`** is an immutable record with 8 event types: `received`, `forwarded`, `stored`, `dropped`, `delivered`, `expired`, `custody_accepted`, `custody_released`. Every action produces an event for telemetry and auditing. The `get_forwarding_history(bundle_id)` method returns the complete event chain for any bundle.

The `get_queue_stats()` method returns occupancy by tier: `emergency_count`, `standard_count`, `bulk_count` — useful for monitoring buffer pressure.

## 📐 Key Numbers & Formulas
- **CUSTODY_REQUESTED flag:** `0x08` (set on P0–P2 bundles)
- **Buffer overflow threshold:** 90% → tail-drop from P4 upward
- **Protected queues:** P0 and P1 — never dropped due to congestion
- **Custody retransmission timer:** `min(remaining_lifetime / 2, contact_window_end)` seconds
- **Queue sort order:** `(priority.value ascending, absolute_deadline ascending)`
- **8 ForwardingEvent types:** received, forwarded, stored, dropped, delivered, expired, custody_accepted, custody_released
- **Default bundle lifetime:** 7 days (604,800 s) for science data

## 🔗 Standards & References
- [RFC 9171 §4.3 — Bundle Custody (BPv7)](https://datatracker.ietf.org/doc/html/rfc9171#section-4.3)
- [RFC 9171 §4.5 — Custody Transfer](https://datatracker.ietf.org/doc/html/rfc9171)
- [CCSDS 734.2-B-1 — DTN Architecture](https://public.ccsds.org/Pubs/734x2b1.pdf)
- [RFC 4838 — DTN Architecture (store-and-forward)](https://datatracker.ietf.org/doc/html/rfc4838)

## 💡 How the Examiner Will Probe This

**Q: "Explain custody transfer as if I'm a network engineer familiar with TCP."**
→ Custody transfer is like TCP's ACK but hop-by-hop instead of end-to-end. In TCP, the receiver ACKs the original sender. In DTN custody, each intermediate node acknowledges the *previous hop* and takes responsibility for forwarding. Once B accepts custody from A, A frees its buffer. If B fails to deliver to C, B retransmits — not A. This localises retransmission to the failed link, critical when each link is 3–22 minutes one-way.

**Q: "What happens when a node's buffer fills up?"**
→ The engine applies tail-drop starting from P4 (lowest priority) upward. P0 and P1 queues are protected — never dropped due to congestion. If buffer reaches 100%, P2 bundles are selectively expired (oldest lifetime first). The RL agent's reward function penalises drops (δ=10.0), so the agent learns to *proactively forward* before hitting 90%.

## ✅ What You Should Be Able to Answer After This Lesson
1. What are the steps in the store-and-forward loop at each DTN node?
2. How does custody transfer differ from TCP's end-to-end ACK, and why does this matter for interplanetary links?
3. What is the custody retransmission timer formula in AETHERIX?
4. What happens to queue priority when the buffer exceeds 90%? Which queues are protected?
5. What are the 8 ForwardingEvent types, and which one fires when custody is accepted?

## 📂 Deep Dive Resources
- `src/routing/forwarding_engine.py` — `ForwardingEngine`, `BundleQueue`, `ForwardingEvent`
- `src/routing/bundle.py` — `accept_custody()`, `release_custody()`, `is_expired`
- `interview_prep/topic_summaries/dtn_fundamentals.md` — custody lifecycle and buffer management detail
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
