# Day 30: Software Mitigation — FDIR, Memory Scrubbing, Checkpointing, BIST

## 📅 August 21, 2026

## 🎯 Learning Objective

Understand the *software-layer* fault tolerance that builds on top of the hardware substrate: the FDIR (Fault Detection, Isolation and Recovery) state machine, memory scrubbing, checkpoint/restart, N-version programming, and Built-In Self-Test (BIST) — and explain how autonomous recovery works when Earth is 15 light-minutes away.

---

## 📖 The Core Concept

### The Autonomy Imperative

At Mars, the one-way light time is 3–22 minutes, meaning a round-trip is 6–44 minutes. If a processor latches up (SEL), the destructive window is *seconds*. Earth cannot be in the loop. The spacecraft must detect, isolate, and recover from faults entirely autonomously — this is the role of the FDIR state machine and its supporting software techniques.

### FDIR State Machine

FDIR (Fault Detection, Isolation and Recovery) is the autonomous response chain that activates when the hardware substrate alone is insufficient — for example, when an SET corrupts the program counter or an SEL latches a peripheral. It operates as a five-state machine:

```
NOMINAL → ANOMALY_DETECTED → ISOLATED → RECOVERING → (NOMINAL | SAFE_MODE)
```

| State | Meaning | Trigger to enter |
|-------|---------|------------------|
| **NOMINAL** | All subsystems healthy, watchdog freshly kicked | Successful recovery or startup |
| **ANOMALY_DETECTED** | Subsystem reports unhealthy OR watchdog expired | Fault detected |
| **ISOLATED** | Faulty unit logically disconnected to prevent cascade | Automatic, after anomaly |
| **RECOVERING** | Reset + reload from golden (read-only) image; re-kick watchdog | Automatic, after isolation |
| **SAFE_MODE** | Recovery budget exhausted; minimal-power, beacon-only, await ground | After max_recovery_attempts failed resets |

Two detection mechanisms feed the state machine:
1. **Subsystem health reports** — software components report their own status (healthy/unhealthy).
2. **Watchdog timer expiry** — the catch-all. Any failure that hangs the processor eventually starves the watchdog, triggering recovery without the fault being explicitly detected.

Recovery is *bounded*: after `max_recovery_attempts` (default 3) failed resets, the controller drops to SAFE_MODE rather than reboot-loop indefinitely. This is deliberate — at 22-minute one-way light time, an agent thrashing in an unknown fault state is worse than a silent, safe spacecraft. SAFE_MODE ceases autonomous action and waits for ground intervention via the beacon-only low-power path.

### Memory Scrubbing

SECDED only helps if a *second* upset does not land in the same word before the first is corrected. A scrubber periodically reads, corrects, and rewrites every memory word, bounding the accumulation window. With upsets Poisson-distributed at mean λ per word per scrub interval:

```
λ = rate_per_bit_s × word_bits × scrub_interval_s
P(uncorrectable) = 1 − P(0) − P(1) = 1 − e^−λ − λe^−λ
```

Faster scrubbing shrinks λ and drives the double-hit residual toward zero. With a **60-second scrub interval** (AETHERIX default), the accumulation term becomes vanishingly small — the dominant residual shifts to MBUs that survive bit-interleaving, which is a *different* mechanism (single high-LET ion, not two independent strikes).

### Checkpointing and Golden Images

When the FDIR controller triggers recovery, it reloads the software from a **golden image** — a read-only, radiation-verified copy stored in non-volatile memory. This guarantees the restored code has not been corrupted. Similarly, the RL agent's Q-table is checkpointed to non-volatile storage periodically so it can be reloaded after a reset without losing learned routing policies.

The checkpoint strategy:
- Q-table state: saved after every N training episodes to non-volatile storage
- Configuration parameters: stored as golden copies, reloaded on every reset
- In-flight bundles: protected by custody transfer — the preceding custodian retransmits

### N-Version Programming

For the most critical computations (e.g., collision avoidance decisions), N-version programming provides diversity at the *algorithm* level: independent teams write different implementations of the same specification, and a voter selects the majority result. This protects against software bugs (common in TMR where all replicas run identical code) but at the cost of N× development effort. AETHERIX uses this conceptually for the routing decision: the RL agent's recommendation is cross-checked against the policy engine's deterministic CGR-style routing, and the policy engine's `POLICY_OVERRIDE` takes precedence when the agent's confidence is below threshold.

### Built-In Self-Test (BIST)

BIST runs at startup and periodically during operation: the processor executes a known-answer test, checksums its own code space, and verifies memory integrity. If BIST fails, the node transitions to DEGRADED or OFFLINE status, and the network routes around it. In the AETHERIX model, this is reflected in the `NodeStatus` enum: `ACTIVE` (nominal), `DEGRADED` (partial failure), `OFFLINE` (failed/isolated).

---

## 🔬 In AETHERIX

`src/computing/radiation.py` implements the software mitigation stack:

**`FDIRController`** (line 298): A dataclass with `watchdog_timeout_s=5.0`, `max_recovery_attempts=3`, and the `FDIRState` enum. The `detect(now_s, healthy)` method runs one FDIR cycle:
- Checks if `(now_s - last_kick_s) > watchdog_timeout_s` → watchdog expired
- If unhealthy or watchdog expired → `ANOMALY_DETECTED` → calls `_isolate_and_recover()`
- `_isolate_and_recover()` increments `recovery_attempts`; if it exceeds `max_recovery_attempts`, transitions to `SAFE_MODE`
- A successful reset re-kicks the watchdog

**`MemoryScrubber`** (line 255): Models periodic scrubbing with `word_bits=32`, `scrub_interval_s=60.0`. The `expected_upsets_per_word(rate)` method computes the Poisson λ, and `uncorrectable_probability(rate)` returns `1 - e^−λ - λe^−λ`. The `residual_word_error_rate_per_day()` method multiplies by intervals per day.

The demo walk-through (`watchdog_timeout_s=5, max_recovery_attempts=2`) shows:
```
t= 0s healthy=True  → NOMINAL
t= 3s healthy=True  → NOMINAL
t=14s healthy=False → RECOVERING (attempt 1: reset + golden reload)
t=20s healthy=False → RECOVERING (attempt 2)
t=30s healthy=False → SAFE_MODE  (budget exhausted → beacon-only)
```

In the deployed cFS architecture, the FDIR controller maps to the `AETHERIX_FDIR_APP` cFS application, subscribing to `WATCHDOG_KICK` messages and publishing `SAFE_MODE_CMD` on the Software Bus.

---

## 📐 Key Numbers & Formulas

| Number | Value | Context |
|--------|-------|---------|
| Watchdog timeout | **5 seconds** | `FDIRController.watchdog_timeout_s` |
| Max recovery attempts | **3** (default), 2 (demo) | Before SAFE_MODE |
| Scrub interval | **60 seconds** | `MemoryScrubber.scrub_interval_s` |
| FDIR states | **5** | NOMINAL → ANOMALY → ISOLATED → RECOVERING → SAFE_MODE |
| Poisson uncorrectable | `1 − e^−λ − λe^−λ` | P(≥2 upsets per word per scrub interval) |
| Golden image | **read-only, non-volatile** | Source for FDIR reload |
| Mars one-way light time | **3–22 minutes** | Why autonomous recovery is mandatory |

---

## 🔗 Standards & References

- [ECSS-E-ST-10-12C](https://ecss.nl/) — Radiation calculation (referenced by the model)
- [NASA Fault Management Handbook](https://www.nasa.gov/smallsat-institute) — FDIR best practices
- **Repo:** `src/computing/radiation.py` — `FDIRController` (line 298), `MemoryScrubber` (line 255)
- **Repo:** `docs/DESIGN_RATIONALE.md` §1.3 (autonomous fault-tolerance loop)
- **Repo:** `interview_prep/topic_summaries/radiation_hardening.md` — FDIR section

---

## 💡 How the Examiner Will Probe This

**Q: "What actually happens when an SEL fires, given that you are 15 light-minutes from Earth?"**

> SEL is a parasitic short that draws overcurrent and is potentially destructive within seconds, so you cannot wait for ground. The hardware detects the overcurrent and power-cycles the affected unit (current-limited switches, latchup-current monitor). The FDIR controller then sees the unit as unhealthy, transitions NOMINAL → ANOMALY_DETECTED → ISOLATED → RECOVERING, reloads from the golden image, and re-kicks the watchdog. If the latch recurs and exhausts the recovery budget, it drops to SAFE_MODE (beacon-only). At no point does any of this require Earth — the 30+ minute round-trip is far longer than the destructive window.

**Q: "Why does SAFE_MODE exist? Why not keep trying to recover indefinitely?"**

> At 22-minute one-way light time, an agent thrashing in an unknown fault state — consuming power, potentially corrupting data, cycling hardware — is worse than a silent, safe spacecraft. SAFE_MODE is the deliberate fail-safe: cease autonomous action, go to minimal power, transmit a beacon, and wait for ground to diagnose. It guarantees the spacecraft stays contactable so Earth can intervene with full information.

**Q: "Memory scrubbing every 60 seconds — why is the accumulation term negligible?"**

> With a 60-second scrub interval, the Poisson λ (expected upsets per word per interval) is extremely small — on the order of 1e-5 even in the interplanetary environment. P(≥2 upsets) = 1 − e^−λ − λe^−λ ≈ λ²/2 ≈ 1e-10. This means two independent strikes landing in the same word before the next scrub is vanishingly rare. The dominant residual shifts to MBUs — a single high-LET ion flipping multiple bits in one strike — which is a fundamentally different mechanism that interleaving and scrubbing only partially address.

---

## ✅ Self-Check Questions

1. List the five FDIR states in order and the trigger for each transition.
2. Why is the watchdog timer described as the "catch-all" detection mechanism?
3. What is a golden image, and why must it be read-only?
4. Calculate the Poisson λ for a 32-bit word with a 60-second scrub interval at the interplanetary SEU rate.
5. Why is SAFE_MODE the correct design choice rather than unlimited recovery attempts?

---

## 📂 Deep Dive Resources

- **Source code:** `src/computing/radiation.py` — `FDIRController`, `MemoryScrubber`, `FDIRState`
- **Design rationale:** `docs/DESIGN_RATIONALE.md` §1.3 (autonomous fault-tolerance loop with cFS)
- **Topic summary:** `interview_prep/topic_summaries/radiation_hardening.md` — FDIR and scrubbing sections
- **Mock interview:** Q12 follow-up probes in `interview_prep/practice/mock_interview.md`
- **Demo:** Run `python src/computing/radiation.py` for the FDIR walk-through
