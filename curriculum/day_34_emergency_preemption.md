# Day 34: Emergency Protocols & Priority Preemption

## 📅 August 25, 2026

## 🎯 Learning Objective

Master AETHERIX's emergency communication protocol — how a safety-critical bundle preempts in-progress traffic, transmits via a low-rate direct-to-Earth backup link, and triggers safe-mode communications — and understand the buffer overflow eviction policy that protects high-priority data at all costs.

---

## 📖 The Core Concept

### When Safety Can't Wait

On Earth, a "priority interrupt" means reordering a queue. In deep space, it means something more dramatic: an emergency bundle arrives mid-transfer and must *physically interrupt* an in-progress data stream, transmit via a backup link, and then let the original transfer resume. This is the EmergencyProtocol — the mechanism that ensures a collision-avoidance alert or a spacecraft health telemetry burst reaches Earth even when the primary downlink is fully occupied.

### The Preemption Decision

Only `EMERGENCY_SAFETY` traffic has the `preemptive` property set to `True`. When an emergency bundle arrives while another transfer is in progress, the protocol follows this decision tree:

```
Emergency bundle arrives mid-transfer.
  ├─ Is the in-progress item rank ≤ emergency rank?
  │     → NO PREEMPTION (current item is equally or more urgent)
  ├─ Else:
  │     1. PREEMPT: suspend the current transfer
  │     2. SEND EMERGENCY: via direct-to-Earth backup at 10 kbps
  │     3. RESUME: original item continues after the emergency clears
```

The rank comparison is crucial: if the in-progress item is already EMERGENCY (rank 0), a new emergency does not preempt it — they are equally urgent, so the first one finishes. Only a *lower-priority* in-progress item is preempted.

### The 10 kbps Direct-to-Earth Backup

The emergency is sent via a dedicated **direct-to-Earth backup link** at `direct_to_earth_rate_bps = 1.0e4` (10 kbps). This is deliberately a *thin but reliable* path — far below the 30 Mbps optical downlink, but it closes even when the primary link is down (weather, pointing failure, conjunction). The design insight: an emergency alert is small (bytes, not megabytes), so the low rate still meets its seconds-level deadline.

Example: a 50,000-byte collision-avoidance alert at 10 kbps:
```
tx_time = (50,000 × 8) / 10,000 = 40 seconds
```
Forty seconds is well within the emergency deadline. Compare this to waiting for the 8 GB panorama to finish on the optical link (minutes), then queueing behind mission-critical data — the delay could be fatal.

### Safe-Mode Communications

When the FDIR controller exhausts its recovery budget and drops to SAFE_MODE, the spacecraft's communication profile changes fundamentally:

| Mode | Communications | Power | Data rate |
|------|---------------|-------|-----------|
| NOMINAL | Full DTN stack, RL routing, optical+RF | Full | 2–200 Mbps |
| DEGRADED | Policy engine routing, RF only | Reduced | 0.5–6 Mbps |
| SAFE_MODE | Beacon-only, minimal power, await ground | Minimal | ~10 kbps beacon |

SAFE_MODE is the fail-safe: the spacecraft ceases autonomous action, transmits a beacon on the S-band (2.3 GHz) TT&C channel, and waits for Earth to diagnose and command recovery. The beacon carries essential health information (power state, last known fault, current time) at minimal power. This is the same approach used by every deep-space mission — Voyager, Mars rovers, Cassini all have a safe-mode beacon.

### Buffer Overflow Eviction Policy

When sustained ingress exceeds egress (approaching conjunction, multiple assets transmitting simultaneously), buffers fill. AETHERIX's eviction policy is graduated and strictly priority-ordered:

| Buffer State | Threshold | Action |
|--------------|----------|--------|
| **Normal** | < 50% | Accept all bundles |
| **Loaded** | 50–90% | Defer BULK (rank 4) bundles; `bulk_defer` policy |
| **Critical** | > 90% | Drop housekeeping/bulk; `congestion_control` policy |

The `congestion_control` policy (priority 90 in the policy engine, `match_all=True`) fires when:
```
buffer_occupancy > 0.9  AND  bundle.priority >= 3
→ DROP
```

The eviction order is always:
1. **P4 BULK** (oldest first) — never mission-critical, re-transmittable
2. **P3 HOUSEKEEPING** (oldest first) — continuously regenerated telemetry
3. **P2 STANDARD** (only if buffer > 95%) — reluctantly, unique science data
4. **P0/P1 → NEVER EVICTED** — protected absolutely

The `BundleQueue` sorts by `(priority, deadline)`, so the first bundles dropped are always the lowest priority with the furthest deadline. EMERGENCY (rank 0) and HIGH_SCIENCE (rank 1) are never evicted while a lower-priority bundle occupies space.

### Buffer Allocation (Starvation Prevention)

To prevent a burst of P0 emergency bundles from starving P2–P4 of storage, each priority class has a guaranteed buffer share:

| Class | Buffer Share | Reasoning |
|-------|-------------|-----------|
| P0 Emergency | 5% | Small but guaranteed; emergencies are rare bursts |
| P1 High Science | 15% | Moderate guaranteed share |
| P2 Standard | 40% | The bulk of routine traffic |
| P3 Housekeeping | 25% | High volume, low urgency |
| P4 Bulk | 15% | Large transfers, opportunistic |

Plus any *unallocated* space is fair game for any class. This prevents a P0 flood from consuming the entire buffer while still giving emergency data guaranteed headroom.

### Custody Refusal as Back-Pressure

When a node reaches 95% buffer, it sends a **Custody Refusal** to upstream nodes. The upstream node stops forwarding to the congested destination and seeks alternate paths. This is analogous to IEEE 802.3x pause frames but at the DTN layer — it prevents cascading congestion by creating back-pressure rather than forward-pressure.

---

## 🔬 In AETHERIX

The emergency protocol is implemented in `src/routing/prioritization.py`:

**`EmergencyProtocol`** (line 267): A dataclass with `direct_to_earth_rate_bps = 1.0e4` and a `log` list. The `preempt(in_progress, emergency)` method:
1. Checks if `in_progress.rank <= emergency.rank` → if so, no preemption (current item equally urgent)
2. Logs the preemption event
3. Computes `tx_s = (emergency.effective_bytes() × 8) / direct_to_earth_rate_bps`
4. Logs the emergency transmission and resume events
5. Returns `{"preempted": bool, "emergency_sent": True, "emergency_tx_s": tx_s}`

The demo (line 357) shows a collision-avoidance alert preempting a daily panorama:
```python
emergency = TrafficItem("collision-avoidance-alert", EMERGENCY_SAFETY, 50_000, 5, "telemetry")
in_progress = TrafficItem("daily-panorama-imagery", HIGH_PRIORITY, 80_000_000, 900, "image_lossy")
proto.preempt(in_progress, emergency)
# → PREEMPT daily-panorama-imagery for collision-avoidance-alert
# → emergency sent via 10 kbps backup in 0.04s
# → resume daily-panorama-imagery after emergency clears
```

The **policy engine** in `src/simulation/policy_engine.py` implements the eviction logic:
- `congestion_control` (priority 90, match_all=True): `buffer > 0.9 AND priority >= 3 → drop`
- `bulk_defer` (priority 70, match_all=True): `priority == 4 AND buffer > 0.5 → store`

---

## 📐 Key Numbers & Formulas

| Number | Value | Context |
|--------|-------|---------|
| Direct-to-Earth backup rate | **10 kbps** | `direct_to_earth_rate_bps = 1.0e4` |
| Emergency tx time (50 KB) | **40 seconds** | At 10 kbps |
| Collision alert tx time (50 KB) | **0.04 seconds** | Wait — actually 50,000×8/10,000 = 40 s |
| Preemptive tier | **EMERGENCY_SAFETY only** | `preemptive = True` |
| Congestion threshold | **> 90%** | `congestion_control` policy |
| Bulk defer threshold | **> 50% buffer, P4** | `bulk_defer` policy |
| Eviction order | P4 → P3 → P2 | P0/P1 never evicted |
| Buffer shares | 5/15/40/25/15% | P0/P1/P2/P3/P4 starvation prevention |
| Custody refusal | **> 95% buffer** | Upstream back-pressure |

---

## 🔗 Standards & References

- [RFC 9171 §4.4](https://www.rfc-editor.org/rfc/rfc9171#section-4.4) — Custody transfer
- [CCSDS 734.2-B-1](https://public.ccsds.org/Pubs/734x2b1.pdf) — DTN Architecture (QoS)
- **Repo:** `src/routing/prioritization.py` — `EmergencyProtocol` (line 267)
- **Repo:** `src/simulation/policy_engine.py` — `congestion_control`, `bulk_defer` policies
- **Repo:** `interview_prep/topic_summaries/data_prioritization.md`
- **Repo:** `docs/DESIGN_RATIONALE.md` §6 (buffer sizing, eviction, allocation)

---

## 💡 How the Examiner Will Probe This

**Q: "Walk me through what happens when a collision-avoidance alert arrives while a panorama is being transmitted."**

> The EmergencyProtocol checks: is the in-progress item (panorama, rank 2) more urgent than the emergency (rank 0)? No. So it preempts: suspends the panorama transfer, sends the 50 KB collision alert via the 10 kbps direct-to-Earth backup link (taking ~40 seconds), then resumes the panorama from where it left off. The alert uses a separate, reliable backup link — it does not need to wait for the optical downlink to clear.

**Q: "Why 10 kbps for the emergency backup? Isn't that incredibly slow?"**

> It is deliberately thin but reliable. The backup link closes even when the primary optical link is down (weather, pointing failure, conjunction). An emergency alert is small — bytes, not megabytes — so even at 10 kbps, a 50 KB alert transmits in 40 seconds, well within its deadline. The design philosophy is: guarantee delivery of small critical data over any channel, rather than risk losing it on a high-rate but unreliable link.

**Q: "What happens if buffers overflow during a conjunction approach?"**

> The graduated eviction policy activates. At 50% buffer, P4 bulk bundles are deferred (`bulk_defer` policy). At 90%, the `congestion_control` policy forcibly drops P3 housekeeping and P4 bulk bundles, oldest first. P2 standard bundles are dropped only above 95%. P0 and P1 are never evicted — protected absolutely. Additionally, at 95%, the node sends Custody Refusal upstream, creating back-pressure that prevents cascading congestion. The RL agent's reward function (δ=10.0 for P0 drops) also trains it to proactively forward lower-priority data *before* the buffer fills.

---

## ✅ Self-Check Questions

1. What condition must be true for the EmergencyProtocol to preempt an in-progress transfer?
2. Calculate the transmission time for a 100 KB emergency alert on the 10 kbps backup link.
3. What is the eviction order during buffer overflow, and which tiers are protected?
4. Why does the buffer use guaranteed per-class shares (5/15/40/25/15%)?
5. What is Custody Refusal, and how does it prevent cascading congestion?

---

## 📂 Deep Dive Resources

- **Source code:** `src/routing/prioritization.py` — `EmergencyProtocol`, `simulate_downlink()` demo
- **Source code:** `src/simulation/policy_engine.py` — `congestion_control`, `bulk_defer`
- **Topic summary:** `interview_prep/topic_summaries/data_prioritization.md` — emergency protocol section
- **Design rationale:** `docs/DESIGN_RATIONALE.md` §6 (buffer eviction, allocation, overflow math)
- **Mock interview:** Q13 and Q13 follow-up in `interview_prep/practice/mock_interview.md`
