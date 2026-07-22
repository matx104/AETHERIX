# Day 31: NASA Core Flight System (cFS) Integration

## 📅 August 22, 2026

## 🎯 Learning Objective

Understand NASA's Core Flight System (cFS) — the flight-software framework that hosts AETHERIX's components as independent applications on a publish/subscribe Software Bus — and explain how this architecture enables autonomous fault tolerance, hot-swappable apps, and graceful degradation, directly satisfying **exam objective 2(e)**.

---

## 📖 The Core Concept

### What cFS Is (and Isn't)

The NASA Core Flight System (cFS) is **not an operating system**. It is a layered *application framework* that runs on top of VxWorks, RTEMS, or a POSIX real-time OS. Developed at NASA Goddard Space Flight Center and open-sourced under a BSD licence, cFS has flight heritage on LRO (Lunar Reconnaissance Orbiter), SLS (Space Launch System), DART (Double Asteroid Redirection Test), and numerous CubeSats.

The key architectural insight: cFS treats flight software as a collection of **independent applications** that communicate via a **Software Bus** — a publish/subscribe message-passing system. No app calls another app directly. Instead, each app publishes messages to named topics and subscribes to topics it cares about. This decoupling is what makes the system fault-tolerant: if one app crashes, the others continue operating.

### Why cFS Over a Custom Bare-Metal Flight Software?

| Criterion | cFS | Custom bare-metal FSW | Why cFS wins |
|-----------|-----|----------------------|--------------|
| Flight heritage | LRO, SLS, DART | None | Proven on actual missions |
| Modularity | App-based (load/unload at runtime) | Monolithic | Routing app hot-swappable without reflash |
| Message bus | Pub/sub, fully decoupled | Point-to-point calls | Apps don't crash together |
| Open source | BSD, NASA GSFC maintained | N/A | Auditable, no vendor lock-in |
| Time/Space partitioning | Time-Access File (TAF) | Manual scheduling | Deterministic CPU allocation |

### The Software Bus Pattern

Think of the Software Bus as an in-space message broker (conceptually similar to MQTT or a real-time Kafka). Each cFS app registers interest in message types:

```
Routing App subscribes to:  LINK_STATE, BUFFER_STATUS
Routing App publishes:      FORWARD_CMD

Forwarding App subscribes to: FORWARD_CMD, BUNDLE_RX
Forwarding App publishes:     BUNDLE_TX, CUSTODY_EVT
```

If the RL routing agent fails (confidence drops below 0.3), the policy engine app simply publishes a `POLICY_OVERRIDE` message. The forwarding app receives it and switches to deterministic CGR-style routing — **no single app is a single point of failure**. The routing app can even be killed and restarted (or reloaded from a golden image) while the rest of the spacecraft continues operating normally.

### Autonomous Fault-Tolerance Loop

The interaction between cFS, FDIR, and the RL agent creates a layered autonomy:

```
SEU flips a bit → ECC corrects (transparent)
     ↓ if uncorrectable
Watchdog timeout → FDIR detects anomaly
     ↓
FDIR: ISOLATE the failing cFS app (not the whole spacecraft)
     ↓
RESET that app → reload from golden image
     ↓
If recovery budget exhausted → SAFE_MODE (cease autonomous action, await Earth)
```

The critical design choice: cFS isolates at the *app* level, not the *spacecraft* level. A monolithic flight software would require a full spacecraft reboot for any anomaly; cFS kills and restarts only the failing application. The Q-table is reloaded from non-volatile storage; bundles in custody are retransmitted by LTP; the network routes around the temporarily-degraded node.

### The Triple Diversity Principle

AETHERIX does not rely on a single fault-tolerance mechanism. Three independent layers must all fail for a corrupt result to propagate:

| Layer | Catches | Mechanism |
|-------|---------|-----------|
| **Hardware** | TID, SEL | Rad-hard parts (RAD750), current limiting |
| **Memory** | SEU, MBU | SECDED ECC + bit interleaving + 60s scrubbing |
| **Compute** | Logic SEU, hang | TMR + watchdog + FDIR state machine |

At p = 1e-4, TMR reduces system error to ≈ 3×10⁻⁸ — a 3,334× improvement. ECC adds another ~200× on memory. Combined, the residual uncorrectable rate over a 210-day cruise is ~186 events from ~37,000 raw upsets. These layers are *independent*: a common-mode fault in one layer does not defeat the others.

---

## 🔬 In AETHERIX

AETHERIX is a *simulation* of the networking layer, but the deployment target is cFS. The DESIGN_RATIONALE.md §1.2 maps every AETHERIX component to a cFS application:

| AETHERIX Component | cFS App | Subscribes | Publishes |
|--------------------|---------|------------|-----------|
| RL routing agent (`rl_agent.py`) | `AETHERIX_ROUTING_APP` | `LINK_STATE`, `BUFFER_STATUS` | `FORWARD_CMD` |
| Forwarding engine (`forwarding_engine.py`) | `AETHERIX_FWD_APP` | `FORWARD_CMD`, `BUNDLE_RX` | `BUNDLE_TX`, `CUSTODY_EVT` |
| LTP convergence layer (`ltp.py`) | `AETHERIX_LTP_APP` | `BUNDLE_TX` | `LTP_REPORT` |
| Policy engine (`policy_engine.py`) | `AETHERIX_POLICY_APP` | `FWD_CONTEXT` | `POLICY_OVERRIDE` |
| FDIR watchdog (`radiation.py`) | `AETHERIX_FDIR_APP` | `WATCHDOG_KICK` | `SAFE_MODE_CMD` |

The **`PolicyEngine`** in `src/simulation/policy_engine.py` is the deterministic fallback. Its `evaluate()` method iterates policies from highest to lowest priority and returns the first matching rule's action. The default fallback decision (when nothing matches) is `("store", "")` — safe for DTN, because storing never loses data. The five default policies are:
1. `emergency_fast_path` (priority 100) — priority ≤ 1 → forward to best link
2. `congestion_control` (priority 90) — buffer > 0.9 AND priority ≥ 3 → drop
3. `deep_space_store` (priority 80) — link quality < 0.3 → store
4. `bulk_defer` (priority 70) — priority 4 AND buffer > 0.5 → store
5. `tier_aware_routing` (priority 60) — forward toward lower-tier neighbour

---

## 📐 Key Numbers & Formulas

| Number | Value | Context |
|--------|-------|---------|
| cFS flight heritage | LRO, SLS, DART | Proven missions |
| AETHERIX cFS apps | **5** | Routing, Forward, LTP, Policy, FDIR |
| TMR reliability gain | **3,334×** | At p = 1e-4 |
| ECC protection factor | **~200×** | Raw upsets → residual |
| Residual uncorrectable | **~186 events** | Over 210-day cruise from ~37,000 raw |
| Policy fallback | `store` | Safe default when no rule matches |
| RL confidence threshold | **< 0.3** | Triggers CGR/policy fallback |
| SAFE_MODE | beacon-only, await ground | After max_recovery_attempts exhausted |

---

## 🔗 Standards & References

- [NASA cFS GitHub](https://github.com/nasa/cfs) — Open-source flight software framework
- [cFS Mission Publications](https://github.com/nasa/cFS/blob/main/docs/cFSMissionPublications.md) — Heritage papers
- **Repo:** `docs/DESIGN_RATIONALE.md` §1 (Core Flight System & autonomous fault tolerance)
- **Repo:** `src/simulation/policy_engine.py` — PolicyEngine with 5 default policies
- **Repo:** `src/computing/radiation.py` — FDIRController (the watchdog cFS app model)

---

## 💡 How the Examiner Will Probe This

**Q: "How does the RL routing agent interact with the policy engine in a cFS deployment?"**

> They are independent cFS apps communicating via the Software Bus. The routing agent subscribes to `LINK_STATE` and `BUFFER_STATUS` and publishes `FORWARD_CMD`. The policy engine subscribes to `FWD_CONTEXT` and publishes `POLICY_OVERRIDE`. Under normal operation, the RL agent's decisions flow through. If the agent's confidence drops below 0.3, the policy app overrides with deterministic CGR-style routing. No single app is a single point of failure — the routing agent can crash and be restarted without affecting the forwarding engine.

**Q: "What happens if the FDIR watchdog fires during a critical bundle transfer?"**

> The FDIR app detects the anomaly (watchdog timeout or subsystem unhealthy), isolates the failing cFS app, resets it, and reloads from the golden image. The bundle itself is protected by custody transfer — the preceding custodian retains a copy and retransmits once the next-hop is restored. The transfer is delayed, not lost. If the recovery budget is exhausted, the node enters SAFE_MODE, and the network routes around it.

**Q: "Why use cFS instead of writing custom flight software?"**

> Three reasons. First, flight heritage — cFS has flown on LRO, SLS, and DART, so the framework itself is proven. Second, modularity — the app-based architecture means I can hot-swap the routing agent without reflashing the entire spacecraft, and isolate faults at the app level rather than rebooting everything. Third, the Software Bus decouples components — if the RL agent fails, the policy engine takes over via a message, not a code-level dependency. Building equivalent fault isolation in a monolithic FSW would require reinventing what cFS already provides.

---

## ✅ Self-Check Questions

1. Is cFS an operating system? Explain what it actually is.
2. Map the five AETHERIX components to their cFS applications and their publish/subscribe messages.
3. What is the "triple diversity" principle, and why must the three layers be independent?
4. What is the default fallback decision in the policy engine, and why is it "safe for DTN"?
5. Why does cFS isolate faults at the app level rather than the spacecraft level?

---

## 📂 Deep Dive Resources

- **Design rationale:** `docs/DESIGN_RATIONALE.md` §1 (cFS mapping, fault-tolerance loop, triple diversity)
- **Source code:** `src/simulation/policy_engine.py` — `PolicyEngine`, `load_default_policies()`
- **Source code:** `src/computing/radiation.py` — `FDIRController`
- **Standards compliance:** `interview_prep/topic_summaries/standards_compliance.md`
- **External:** [NASA cFS documentation](https://github.com/nasa/cFs)
