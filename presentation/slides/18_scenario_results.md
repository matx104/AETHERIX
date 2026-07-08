# Slide 18: Scenario Results & Reproducibility

## Real Simulation Data (seed=42, Python 3.13)

---

### Earth-Mars Baseline (30-day, average distance 225 M km)

| Metric | Value |
|--------|-------|
| Duration | 720 hours |
| Time step | 60 s |
| Bundles generated | 7,205 |
| Bundles delivered | 112 |
| Delivery ratio | 1.6% |
| Total events | 977,781 |
| Topology | 241 nodes (5 tiers) |

> Low delivery ratio is expected for an **untrained** Q-learning agent on
> the full 241-node topology. Module 3 of `run_simulation.py` shows
> convergence on the 15-node training topology.

---

### Per-Priority Delivery Breakdown

| Priority | Delivered | Dropped | Notes |
|----------|-----------|---------|-------|
| EMERGENCY | 3 | 331 | Small volume, highest drop rate (untrained routing) |
| HIGH_SCIENCE | 5 | 740 | |
| HOUSEKEEPING | 19 | 1,379 | Best raw delivery (most generated) |
| STANDARD | 69 | 3,573 | Bulk of traffic |
| BULK | 16 | 1,070 | |

---

### Solar Conjunction Scenario (14-day, 401 M km, optical blackout)

| Phase | Optical | RF (Ka-band) | RF (X-band) | Action |
|-------|---------|--------------|-------------|--------|
| Normal ops | 50 Mbps | Backup | — | Optical primary |
| Pre-conjunction (−48h) | Degrading | 10 Mbps | — | RL agent switches to RF |
| Conjunction peak | Blocked | Degraded (−8 dB) | 2 Mbps | Store-and-forward via L4/L5 |
| Recovery ramp (+48h) | Restoring | Restoring | — | Gradual optical resumption |

> The RL agent detects link quality < 0.3 and switches to **STORE** action,
> holding bundles in Lagrange-relay buffers until the conjunction clears.

---

### RL Training Convergence (500 episodes, seed=42)

| Metric | First 100 | Last 100 | Improvement |
|--------|-----------|----------|-------------|
| Avg reward | 3.63 | 11.86 | +8.23 |
| Final epsilon | 1.0 | 0.082 | |
| Q-table states | 0 | 120 | |
| Q-table entries | 0 | 288 | |

---

### Reproducibility Checklist

| Parameter | Value |
|-----------|-------|
| Seed | 42 |
| Python | 3.13 |
| Dependencies | stdlib only (zero pip for core) |
| Command | `python run_simulation.py` |
| Scenario YAML | `config/earth-mars-baseline.yaml` |
| Verify | `python src/simulation/run_scenario.py --config config/earth-mars-baseline.yaml` |
