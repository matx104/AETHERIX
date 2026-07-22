# Day 36: Failure & Recovery — Solar Conjunction Scenario

## 📅 August 27, 2026

## 🎯 Learning Objective

Master the solar conjunction failure scenario — the single most important scenario in AETHERIX — including the orbital geometry, the optical blackout, the Ka-band/X-band fallback chain via ES-L4/L5 Lagrange relays, and the recovery ramp, enabling you to whiteboard the full failure-and-recovery decision tree under examiner pressure.

---

## 📖 The Core Concept

### The Conjunction Problem

Approximately every **26 months** (the Earth-Mars synodic period), the two planets pass near solar conjunction — the Sun appears between Earth and Mars. The Sun's corona raises the noise floor until no reliable direct link exists. This is not a transient outage; it is a predictable, ~2-week period of zero direct-path availability.

### Orbital Geometry

The conjunction exclusion is defined by a phase angle threshold: when the Sun-Earth-Mars angle drops below **10 degrees**, the direct path is considered unusable. The `predict_contact_windows()` function in `src/orbital/contact_windows.py` implements this as a hard exclusion:

```
if phase_angle < 10 degrees: skip window
```

At this geometry, the solar corona causes:
- **Solar plasma scintillation** — free electrons in the corona cause rapid phase and amplitude fluctuations on RF signals
- **Optical extinction** — the Sun's intense brightness makes photon-counting detection impossible
- **Increased path loss** — signals grazing the Sun's limb experience additional attenuation

### The Fallback Chain

AETHERIX's failure handling is layered — each layer degrades gracefully to the next:

```
Tier 0 (Normal):  Optical 1550 nm, 50-200 Mbps
    ↓ (optical fails: clouds, pointing, conjunction)
Tier 1:            Ka-band RF, 2-10 Mbps (penetrates clouds)
    ↓ (Ka degraded: solar plasma scintillation during conjunction)
Tier 2:            X-band RF via Lagrange relays, lower rate
    ↓ (all direct paths blocked: conjunction blackout)
Tier 3:            Store-and-forward via ES-L4 / ES-L5 Lagrange relays
```

### Why the Lagrange Relays Work

The Lagrange relays at ES-L4 and ES-L5 sit **~60 degrees ahead/behind Earth** in its orbit around the Sun. This means they have line-of-sight to both Earth and Mars *around the solar limb* even during conjunction, when the direct Earth-Mars path is occulted. They provide **50–70% availability** during conjunction — not 100%, because the geometry is marginal and the relay path is longer (higher path loss), but vastly better than the 0% of the direct path.

| Band | Frequency | Use in Failure Chain |
|------|----------:|----------------------|
| Optical | 1550 nm | Primary (highest rate, weather-sensitive) |
| Ka | 26.5 GHz | Primary RF fallback (optical failed) |
| X | 8.4 GHz | Conjunction fallback (Ka degraded by plasma) |
| S | 2.3 GHz | TT&C / emergency beacon |

### The Recovery Ramp

Links do not snap back to full rate once the angle passes 10 degrees — the corona is still hot. AETHERIX ramps capacity back gradually:

| Phase | Sun Angle | Optical | Ka-band | Behaviour |
|-------|----------:|:-------:|:-------:|-----------|
| **Blackout** | < 10° | down | down | Store-only via Lagrange relays |
| **Early recovery** | 10–15° | down | degraded | X-band trickle; drain emergency backlog |
| **Partial** | 15–25° | marginal | up | Ka restores; agent forwards rank ≤ 1 |
| **Nominal** | > 25° | up | up | Full optical + Ka; resume bulk transfers |

The drained backlog order is fixed by the QoS scheduler: EMERGENCY first, then MISSION_CRITICAL, HIGH_PRIORITY, BULK last. Buffer occupancy returns below 0.9% and `congestion_control` stands down.

### Data Triage During Conjunction

During the ~2-week conjunction, the RL agent's priority-aware routing becomes critical:
- **P0 Emergency** bundles routed immediately via Lagrange relay using LTP red segments with custody
- **P1 High Science** queued behind P0 with same reliability guarantees
- **P2 Standard** stored locally on Mars assets until direct links resume
- **P3/P4** deferred entirely

The 780-day synodic period means the conjunction is *predictable* — the agent learns to pre-position data before it starts. The total Mars surface buffer capacity (167 nodes × 64–256 GB each) can store the full conjunction backlog.

### Availability Math

The combined optical + RF availability is computed as:

```
A_combined = 1 − (1 − A_optical)(1 − A_rf)
           = 1 − (1 − 0.957)(1 − 0.99)
           = 1 − 0.043 × 0.01
           = 0.9996  →  99.96%
```

| Layer | Availability | Residual Outage |
|-------|-------------:|----------------:|
| Optical (3-site diversity) | 95.7% | 4.3% |
| Ka-band RF | 99.0% | 1.0% |
| **Combined** | **99.96%** | **0.04%** |

The 99.96% combined figure exceeds the 99.9% target. During conjunction, however, both optical and Ka degrade, and availability drops to the Lagrange relay's **50–70%**.

---

## 🔬 In AETHERIX

The conjunction scenario is modeled in multiple places:

**`src/orbital/contact_windows.py`** (line 253): The `predict_contact_windows()` function computes the Sun-Earth-Mars phase angle and excludes windows below 10 degrees. The conjunction recurrence is governed by the **780-day synodic period** (technically 779.94 days).

**`src/simulation/policy_engine.py`**: The `deep_space_store` policy (priority 80) triggers when `link_quality < 0.3` — the same threshold the RL agent uses (`MIN_LINK_QUALITY = 0.3` in `rl_agent.py:83`). During conjunction, link quality drops below 0.3 and bundles are stored.

**`src/routing/rl_agent.py`** (line 83): The `MIN_LINK_QUALITY = 0.3` threshold is the break-even point where the agent stops forwarding and starts storing. This corresponds roughly to the -3 dB margin boundary.

**Demo:** `run_simulation.py -m 4` runs the full conjunction scenario walkthrough, showing the transition from normal operations through conjunction to recovery.

The failure-and-recovery whiteboarding scenarios are documented in `docs/DESIGN_RATIONALE.md` §3 (Scenarios A–F), each with ASCII topology and decision logic.

---

## 📐 Key Numbers & Formulas

| Number | Value | Context |
|--------|-------|---------|
| Synodic period | **~26 months** (779.94 days) | Earth-Mars conjunction recurrence |
| Conjunction exclusion half-angle | **10 degrees** | Phase angle threshold |
| Typical blackout duration | **~2 weeks** | Direct path unavailable |
| Lagrange relay availability | **50–70%** | During conjunction (vs 0% direct) |
| ES-L4/L5 offset | **60 degrees** from Sun-Earth line | Why they maintain LOS |
| Min link quality threshold | **0.3** | Forward vs store decision |
| Optical availability (3 sites) | **95.7%** | `(1 - 0.35³)` cloud model |
| Combined optical+RF | **99.96%** | Normal operations |
| Conjunction availability | **50–70%** | Lagrange relay only |
| Mars surface buffer/node | **64–256 GB** | Stores full conjunction backlog |

---

## 🔗 Standards & References

- [NASA DSN Solar Conjunction](https://www.nasa.gov/dsn) — Conjunction operations
- [CCSDS 502.0-B-3](https://public.ccsds.org/Pubs/502x0b3e1.pdf) — Orbital data (SGP4/SDP4)
- **Repo:** `src/orbital/contact_windows.py` — phase angle exclusion
- **Repo:** `interview_prep/topic_summaries/failure_recovery.md` — full failure mode catalogue
- **Repo:** `docs/DESIGN_RATIONALE.md` §3 — whiteboarding scenarios A–F
- **Demo:** `run_simulation.py -m 4` — conjunction scenario

---

## 💡 How the Examiner Will Probe This

**Q: "Draw your backup network path if the Earth-Mars direct link fails during solar conjunction."**

> *[Draw on whiteboard: Mars → ES-L4 (60° elongation) → Earth via Ka-band]* The direct path is occulted when the Sun-Earth-Mars phase angle < 10°. The Lagrange relays at ES-L4 and ES-L5 sit ~60° off the Sun-Earth line, so they maintain line-of-sight to both planets. P0 emergency bundles route via ES-L5 using Ka-band RF (the agent reroutes because ES-L4 may be at lower quality). P2–P4 bundles are stored locally. Availability is 50–70%, not 100%, but vastly better than the 0% of the direct path.

**Q: "What if the Lagrange relay itself fails?"**

> Each Lagrange point has a primary and backup satellite (2× L4, 2× L5 = 4 nodes in Tier 3). If one L4 relay fails, traffic reroutes to ES-L5. The weakest tier is Tier 3 — only 4 nodes. If both L4 relays fail, conjunction availability drops but L5 still provides a path. The system degrades gracefully: without L4/L5, it reverts to the current state-of-practice (no communication during conjunction).

**Q: "How does the system recover after conjunction ends?"**

> Links don't snap back — the corona is still hot. The recovery ramp has four phases: blackout (<10°, store-only), early recovery (10–15°, X-band trickle), partial (15–25°, Ka restores, agent forwards P0/P1), and nominal (>25°, full optical+Ka). The drained backlog order is fixed by the QoS scheduler: EMERGENCY first, then MISSION_CRITICAL, HIGH_PRIORITY, BULK last. Buffer occupancy drops below 90% and congestion_control stands down.

---

## ✅ Self-Check Questions

1. What is the phase angle threshold for conjunction exclusion, and how long does a typical blackout last?
2. Why can the ES-L4/L5 Lagrange relays maintain connectivity during conjunction when direct links cannot?
3. Draw the four-phase recovery ramp (blackout → nominal) with the Sun angle ranges.
4. Calculate the combined optical+RF availability and show why it exceeds 99.9%.
5. What data triage policy does the RL agent follow during conjunction?

---

## 📂 Deep Dive Resources

- **Topic summary:** `interview_prep/topic_summaries/failure_recovery.md` — five canonical failure modes
- **Design rationale:** `docs/DESIGN_RATIONALE.md` §3 (whiteboarding scenarios), §8 (blast-radius analysis)
- **Challenging questions:** C16 (zero contact windows) in `interview_prep/question_bank/challenging_questions.md`
- **Mock interview:** Q13 in `interview_prep/practice/mock_interview.md`
- **Demo:** `run_simulation.py -m 4` for the conjunction walkthrough
