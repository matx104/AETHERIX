# Day 37: Performance Analysis — Metrics, Methodology, Validation

## 📅 August 28, 2026

## 🎯 Learning Objective

Master the performance metrics AETHERIX uses to evaluate its DTN architecture (delivery ratio, end-to-end delay, throughput, hop count), understand the simulation methodology that produces them, and be able to defend the validation approach — including honestly acknowledging what is *not yet validated*.

---

## 📖 The Core Concept

### Why Performance Metrics Matter

An architecture without measured performance is just a design. The examiner will ask: "How do you know your system actually works?" The answer lies in simulation metrics that quantify end-to-end behaviour across the full 780-day synodic period, validated against known real-world baselines.

### The Core Metrics

**Delivery Ratio** — The fraction of generated bundles that reach their destination before expiring. The most fundamental metric: `delivery_ratio = delivered / total`. In the baseline simulation, AETHERIX targets **>95%** delivery ratio, with P0/P1 bundles at near-100%.

**End-to-End Delay** — The time from bundle creation to delivery, measured as `deliver_time - creation_time`. This includes light-time propagation (irreducible: 3–22 minutes one-way), queuing delay (waiting for the next contact), and processing overhead. The presentation claims DTN overhead under 5% — meaning total transit ≈ 13 minutes for a 12.5-minute light-time path.

**Throughput** — Total bytes delivered per unit time. For the optical link: 2–200 Mbps (distance-dependent). For Ka-band RF: 0.5–6 Mbps. The simulator measures `throughput_mb = total_delivered_bytes / (1024 × 1024)`.

**Average Hops** — The mean number of intermediate nodes a bundle traverses. AETHERIX's 7-hop Earth-Mars path (surface → orbiter → Lagrange → Earth LEO → DSN → MOC) is typical. More hops mean more custody overhead and more failure risk.

### Per-Priority and Per-Node Statistics

AETHERIX doesn't just compute aggregate metrics — it breaks them down:

**Per-Priority Stats**: Each `BundlePriority` level tracks delivered count, dropped count, and average delay separately. This reveals whether P0 emergency bundles truly get preferential treatment (they should: near-100% delivery, lowest delay) or whether the scheduler is fair across classes.

**Per-Node Stats**: Each node tracks queue size, bundles forwarded, bundles stored, and buffer utilization. This identifies bottlenecks — if one Lagrange relay consistently has 90%+ buffer utilization, it's a capacity constraint.

### Simulation Methodology

The `Simulator` class in `src/simulation/simulator.py` is a **time-stepped discrete simulation**:

```
1. Build topology (create_default_topology)
2. Create forwarding engines for all nodes
3. Step from t=0 to t=duration in time_step_seconds increments
4. At each step:
   a. Probabilistically generate a new bundle (source: Tiers 4-5, dest: Tiers 1-2)
   b. Inject into source node's forwarding engine
   c. Call engine.tick() for every node
   d. Propagate forwarded bundles to next-hop engines
   e. Accumulate delivery/drop/expire statistics
5. Build SimulationResult with all metrics
```

The default configuration:
- **Duration**: 720 hours (30 days)
- **Time step**: 60 seconds
- **Seed**: 42 (for reproducibility)
- **Earth-Mars distance**: 225M km (average)
- **Optical data rate**: 50 Mbps
- **RF data rate**: 2 Mbps
- **Bundle generation rate**: 10 per hour

Bundle generation is weighted by priority: `[0.05, 0.10, 0.50, 0.20, 0.15]` for P0–P4, meaning 50% of traffic is P2 Standard (the bulk of routine science), with small fractions of emergency and bulk.

### Validation Layers

| Layer | Method | What It Catches |
|-------|--------|-----------------|
| **Unit tests** | 480+ automated tests assert each function's output | Logic errors, regressions |
| **Physics sanity** | Link-budget formulas compared to published DSOC/DSN values | Formula errors |
| **Protocol conformance** | BPv7/LTP behaviour checked against RFC examples | Protocol-logic errors |
| **Determinism** | Same seed → identical output (`--seed`) | Non-determinism bugs |
| **Boundary tests** | Empty queues, full buffers, expired bundles, no neighbors | Edge-case crashes |

### What Is NOT Yet Validated (Honesty)

| Claim | Current Basis | Needs (Phase 6) |
|-------|---------------|-----------------|
| Exact delivery ratios | Simulation model | ns-3 packet-level comparison |
| QKD key rates at 400 M km | Probabilistic model | Qiskit photon-level sim |
| Contact-window precision | Keplerian two-body | GMAT/Orekit numerical propagation |
| RL policy quality | Simulated topology | ION-DTN real-stack deployment |

**How to state this in the oral:** *"I built the architecture and validated the algorithms on a transparent, dependency-free model. The reward function, the policy engine, and the conjunction-recovery logic are all proven. The absolute numbers are model-level estimates, not flight-measured. Phase 6 ports the validated policies into ION-DTN's convergence layers and re-runs them under ns-3 for packet-level realism."*

### Identifying Bottlenecks

The per-node statistics reveal where the system is constrained:

- **Lagrange relays during conjunction**: buffer utilization spikes as they become the only path
- **Areostationary relays**: queue depth grows if multiple surface assets transmit simultaneously
- **DSN ground stations**: rarely the bottleneck (10 TB buffer), but scheduling conflicts can delay

The policy engine's `congestion_control` (buffer > 90%) and the RL agent's proactive forwarding (penalised for drops) work together to prevent these bottlenecks from causing cascade failures.

---

## 🔬 In AETHERIX

The `SimulationResult` dataclass (`src/simulation/simulator.py`, line 54) captures all metrics:

```python
@dataclass
class SimulationResult:
    config: SimulationConfig
    total_bundles: int = 0
    delivered_bundles: int = 0
    dropped_bundles: int = 0
    stored_bundles: int = 0
    expired_bundles: int = 0
    forwarded_bundles: int = 0
    average_delay_seconds: float = 0.0
    average_hops: float = 0.0
    delivery_ratio: float = 0.0
    throughput_mb: float = 0.0
    per_priority_stats: Dict[str, Dict] = ...
    per_node_stats: Dict[str, Dict] = ...
```

The `_build_result()` method (line 362) computes delivery ratio, average delay (from bundle birth to delivery timestamps), average hops (from `bundle.hops`), and throughput (sum of delivered payload bytes). Per-priority stats track delivered/dropped/avg_delay for each `BundlePriority`. Per-node stats track queue_size, bundles_forwarded, bundles_stored, and buffer_utilization.

The `generate_bundle()` method (line 136) creates bundles probabilistically with the priority weight distribution `[0.05, 0.10, 0.50, 0.20, 0.15]`, source from Tiers 4–5, destination from Tiers 1–2.

---

## 📐 Key Numbers & Formulas

| Metric | Target/Value | Context |
|--------|-------------|---------|
| Delivery ratio | **>95%** (overall), ~100% for P0 | Baseline scenario |
| End-to-end delay overhead | **<5%** above light-time | DTN processing cost |
| Throughput (optical) | **2–200 Mbps** | Distance-dependent |
| Throughput (RF) | **0.5–6 Mbps** | Ka-band fallback |
| Average hops | **~7** | Surface → MOC path |
| Simulation duration | **720 hours** (30 days) | Default config |
| Time step | **60 seconds** | Discrete steps |
| Priority weights | 5/10/50/20/15% | P0/P1/P2/P3/P4 |
| Automated tests | **480+** | Validation layer |
| Reproducibility seed | **42** | Same seed → same output |

---

## 🔗 Standards & References

- [NASA DSOC Results (2023)](https://www.nasa.gov/mission/dsoc/) — Real-world optical link validation baseline
- [ION-DTN](https://github.com/nasa/ION-DTN) — Reference BPv7 implementation for comparison
- **Repo:** `src/simulation/simulator.py` — `Simulator`, `SimulationResult`, `SimulationConfig`
- **Repo:** `docs/DESIGN_RATIONALE.md` §2 (simulation tooling), §10 (validation methodology)
- **Repo:** `interview_prep/question_bank/challenging_questions.md` — C8 (validation), C18 (policy testing)

---

## 💡 How the Examiner Will Probe This

**Q: "How do you validate that your simulation results are realistic and not artifacts of the simulation model?"**

> Five layers: unit tests (480+ asserting each function), physics sanity (link-budget formulas compared to DSOC published results), protocol conformance (BPv7/LTP checked against RFC examples), determinism (same seed → same output), and boundary tests (empty queues, full buffers, expired bundles). I honestly acknowledge that absolute numbers are model-level estimates, not flight-measured. The validation path is documented: ns-3 for packet realism, GMAT for orbital precision, ION-DTN for wire compatibility.

**Q: "What's your delivery ratio, and how does it break down by priority?"**

> The baseline scenario targets >95% overall delivery ratio, with P0 Emergency and P1 High Science at near-100% (they use LTP red segments with custody and preemptive priority). P2 Standard is typically 90–95%. P3/P4 may see lower ratios during congestion, but their bundles have long lifetimes (7–30 days) so they survive until the next contact. The per-priority stats in SimulationResult track this breakdown.

**Q: "How do you validate that routing policy changes actually improve performance?"**

> A/B testing within the simulation. Baseline run with current policy over the full synodic period, recording all metrics. Treatment run with modified policy using the same seed. Comparison of delivery rate, latency, hop count, drop rate, and energy per priority level. Statistical significance via 10+ runs with different seeds. Regression tests verify edge cases. Every configuration is also compared against CGR — if the modified policy performs worse than CGR on any priority, it's flagged.

---

## ✅ Self-Check Questions

1. What is the delivery ratio target, and how does it vary by priority class?
2. How does the simulator generate bundles? What are the priority weights and source/destination tiers?
3. List the five validation layers and what each catches.
4. Name three claims that are NOT yet validated and what tool each needs (Phase 6).
5. How would you identify a bottleneck node from the per-node statistics?

---

## 📂 Deep Dive Resources

- **Source code:** `src/simulation/simulator.py` — full simulation engine
- **Source code:** `src/simulation/policy_engine.py` — policy evaluation
- **Design rationale:** `docs/DESIGN_RATIONALE.md` §2 (simulation tooling), §10 (validation)
- **Challenging questions:** C8, C18 in `interview_prep/question_bank/challenging_questions.md`
- **Presentation script:** Slide 14, 20, 23 in `docs/downloads/AETHERIX_Presentation_Script.md`
