# Day 32: Data Classification — The 4-Tier Priority System

## 📅 August 23, 2026

## 🎯 Learning Objective

Master AETHERIX's four-tier mission data classification system and understand how each tier maps onto a BPv7 `BundlePriority`, enabling the scheduler, policy engine, and RL agent to make consistent priority-aware decisions, directly supporting **exam objective 2(f): mission-critical data prioritization**.

---

## 📖 The Core Concept

### The Problem: Starved Downlinks

A Mars-to-Earth optical contact may last minutes and offer tens of Mbps, while a single day's panorama is gigabytes. When bandwidth is intermittent and dwarfed by demand, the question is not *how fast* to send data but *what to send, in what order, over a finite window*. The answer begins with classification: every byte generated on Mars must be assigned a priority tier that determines its access to the downlink.

### The Four Tiers

AETHERIX defines four `DataCategory` values, highest urgency first. Each maps directly onto a BPv7 `BundlePriority` so the classification flows through the existing bundle/forwarding machinery unchanged:

| Tier | `DataCategory` | Examples | Maps to `BundlePriority` | Rank | Preemptive? |
|-----:|----------------|----------|--------------------------|-----:|:-----------:|
| 1 | **EMERGENCY_SAFETY** | Health telemetry, collision avoidance, fault alerts | EMERGENCY (0) | 0 | **yes** |
| 2 | **MISSION_CRITICAL** | Command acknowledgements, time-sensitive science events | HIGH_SCIENCE (1) | 1 | no |
| 3 | **HIGH_PRIORITY** | Routine telemetry, scheduled science observations | STANDARD (2) | 2 | no |
| 4 | **LOW_PRIORITY** | Housekeeping logs, bulk file transfers, software images | BULK (4) | 3 | no |

### Why Four Tiers, Not Three?

RFC 9171 defines five `BundlePriority` levels (EMERGENCY=0 through BULK=4). AETHERIX uses four of them for mission data:

- **P0 EMERGENCY** covers everything from immediate safety alerts (must arrive in minutes) to fault reports. The cost of a missed safety alert is catastrophic, so this tier is *preemptive* — it can interrupt an in-progress transfer.
- **P1 MISSION_CRITICAL** covers command acknowledgements and time-sensitive science events (e.g., a seismic event that must be catalogued within 30 minutes). Same reliability guarantees as P0 (LTP red segments + custody), but cannot preempt.
- **P2 HIGH_PRIORITY** covers routine telemetry and scheduled observations. This is the "bulk of routine traffic" — the daily panorama, periodic sensor readings.
- **P3 LOW_PRIORITY** covers housekeeping logs, bulk file transfers, and software images. This data can wait a contact (or several).

The distinction between P0/P1 and P2/P3 is critical: the former use LTP **red** segments (reliable, acknowledged, retransmitted) with custody transfer; the latter use LTP **green** segments (best-effort). The RL agent's drop penalty is also tier-dependent: δ=10.0 for P0 drops versus δ=0.1 for P4, ensuring the agent never sacrifices high-priority data for low-priority throughput.

### Priority Space Note

BPv7's five levels are EMERGENCY(0), HIGH_SCIENCE(1), STANDARD(2), HOUSEKEEPING(3), BULK(4). AETHERIX's four mission tiers use four of these; **HOUSEKEEPING (3) is reserved** for the underlying bundle layer. This avoids collision between application-level classification and protocol-level housekeeping traffic.

### The Preemption Property

Only `EMERGENCY_SAFETY` has the `preemptive` property set to `True`. This means:
- An emergency bundle can interrupt an in-progress lower-priority transfer
- It is routed immediately via the most reliable available path
- After the emergency clears, the interrupted transfer resumes

This is not a theoretical concern — during a solar conjunction with only Lagrange relay paths at reduced bandwidth, emergency health telemetry must reach Earth regardless of what else is in the queue.

### How Priority Flows Through the System

The `rank` property of each `DataCategory` is the integer value of the underlying `BundlePriority`. Rank 0 is most urgent. This rank drives three independent decision systems:

1. **QoSScheduler**: sorts items by `(category.rank ASC, deadline_s ASC)` — strict priority, then earliest deadline.
2. **PolicyEngine**: the `emergency_fast_path` policy (priority 100) forwards bundles with priority ≤ 1 to the best link; `congestion_control` (priority 90) drops bundles with priority ≥ 3 when buffer > 90%.
3. **RL Agent**: the reward function's drop penalty (δ) is weighted by priority — dropping a P0 bundle costs 10.0 reward points, dropping a P4 bundle costs 0.1.

All three systems agree on the ordering: EMERGENCY first, BULK last. This consistency is not accidental — it is enforced by the shared `BundlePriority` mapping.

---

## 🔬 In AETHERIX

The classification is implemented in `src/routing/prioritization.py` as the `DataCategory` enum (line 38). Each member is a tuple of `(label, examples, bundle_priority)`. The `__init__` method stores these, and two properties drive downstream logic:

- `rank` → `int(self.bundle_priority.value)` — used for sorting
- `preemptive` → `True` only for `EMERGENCY_SAFETY`

The `make_bundle()` function (line 304) converts a `TrafficItem` into a BPv7 `Bundle` with the mapped priority and lifetime:

```python
Bundle(
    source=EndpointID.from_string(f"dtn://{source}/data"),
    destination=EndpointID.from_string(f"dtn://{dest}/data"),
    priority=item.category.bundle_priority,
    payload_size_bytes=item.effective_bytes(),
    lifetime_seconds=int(max(60, item.deadline_s)),
)
```

The demo scenario `simulate_downlink()` (line 317) creates a realistic mixed-priority workload over a 900-second / 30 Mbps contact:

| Item | Category | Raw Size | Deadline |
|------|----------|---------:|---------:|
| rover-health-telemetry | EMERGENCY_SAFETY | 2 MB | 60 s |
| command-acknowledgements | MISSION_CRITICAL | 5 MB | 120 s |
| seismic-event-capture | MISSION_CRITICAL | 40 MB | 300 s |
| daily-panorama-imagery | HIGH_PRIORITY | 8 GB | 900 s |
| housekeeping-logs | LOW_PRIORITY | 400 MB | 1200 s |
| software-update-archive | LOW_PRIORITY | 6 GB | 1800 s |

The scheduler delivers emergency and mission-critical items in full, fragments the panorama across contacts, and defers the bulk software update — exactly the behaviour a bandwidth-starved mission needs.

---

## 📐 Key Numbers & Formulas

| Number | Value | Context |
|--------|-------|---------|
| Data tiers | **4** | EMERGENCY, MISSION_CRITICAL, HIGH_PRIORITY, LOW_PRIORITY |
| BPv7 priority levels | **5** | EMERGENCY(0) through BULK(4) |
| Emergency rank | **0** | Always attempted first |
| Bulk rank | **4** | Always attempted last |
| Drop penalty P0 | **δ = 10.0** | RL reward function |
| Drop penalty P4 | **δ = 0.1** | RL reward function |
| Preemptive tiers | **1** | Only EMERGENCY_SAFETY |
| Buffer share P0/P1/P2/P3/P4 | 5% / 15% / 40% / 25% / 15% | Starvation prevention |

---

## 🔗 Standards & References

- [RFC 9171 §4.2.4](https://www.rfc-editor.org/rfc/rfc9171#section-4.2.4) — Bundle priority classes
- [CCSDS 734.2-B-1](https://public.ccsds.org/Pubs/734x2b1.pdf) — DTN Architecture (QoS, custody)
- **Repo:** `src/routing/prioritization.py` — `DataCategory` enum (line 38)
- **Repo:** `src/routing/bundle.py` — `BundlePriority` enum
- **Repo:** `interview_prep/topic_summaries/data_prioritization.md`

---

## 💡 How the Examiner Will Probe This

**Q: "How does AETHERIX handle data prioritisation during a solar conjunction when bandwidth is severely limited?"**

> During conjunction, direct Earth-Mars links are unavailable for ~2 weeks. The Lagrange relay path provides 50–70% availability but at reduced bandwidth. P0 emergency bundles are routed immediately via the Lagrange path using LTP red segments with custody transfer. P1 high-science data queues behind P0 with the same reliability. P2 standard data is stored locally on Mars assets until direct links resume. P3/P4 bundles are deferred entirely. The RL agent's priority-weighted drop penalty ensures high-priority data is never sacrificed.

**Q: "Why do you map four tiers onto five BPv7 priority levels?"**

> BPv7 defines five levels (EMERGENCY=0 through BULK=4). AETHERIX's four mission tiers use four of them; HOUSEKEEPING (3) is reserved for the underlying bundle layer's own administrative traffic. This prevents application-level classification from colliding with protocol-level housekeeping bundles. The mapping is direct — each DataCategory carries a reference to its BundlePriority, so the classification flows through the forwarding engine unchanged.

**Q: "What if the buffer fills up — which bundles get dropped?"**

> Eviction is strictly priority-ordered. The policy engine's `congestion_control` rule (priority 90) activates when buffer > 90%: it drops bundles with priority ≥ 3 (HOUSEKEEPING and BULK), oldest first. If that is not enough, P2 STANDARD bundles are expired reluctantly. P0 (EMERGENCY) and P1 (HIGH_SCIENCE) are **never evicted** — they are protected by the policy engine. Additionally, the RL agent proactively forwards lower-priority bundles before the buffer fills, because its reward function penalises drops (δ=10.0 for P0).

---

## ✅ Self-Check Questions

1. List the four `DataCategory` tiers in order of urgency and their corresponding `BundlePriority` values.
2. Which tier has the `preemptive` property, and what does preemption mean operationally?
3. Why is HOUSEKEEPING (3) not used as a mission data tier?
4. How do the QoSScheduler, PolicyEngine, and RL agent all agree on priority ordering?
5. During a buffer overflow, what is the eviction order, and which tiers are protected?

---

## 📂 Deep Dive Resources

- **Source code:** `src/routing/prioritization.py` — `DataCategory`, `make_bundle()`, `simulate_downlink()`
- **Source code:** `src/routing/bundle.py` — `BundlePriority` enum
- **Topic summary:** `interview_prep/topic_summaries/data_prioritization.md`
- **Mock interview:** Q13 in `interview_prep/practice/mock_interview.md`
- **Design rationale:** `docs/DESIGN_RATIONALE.md` §6 (buffer sizing and eviction)
