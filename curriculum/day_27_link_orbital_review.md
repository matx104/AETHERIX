# Day 27: Link Budget & Orbital Mechanics Integration Review

## 📅 Tuesday, August 18, 2026

## 🎯 Learning Objective

Integrate link budget analysis with orbital mechanics to explain AETHERIX's end-to-end performance: how Earth-Mars distance drives data rates from 200 Mbps to 2 Mbps, how this variation shapes RL training, and how to present this analysis in the oral exam. This consolidates exam Learning Objective 4.

## 📖 The Core Concept

Over the past week, Abdullah, you've learned link budgets (Days 21–23) and orbital mechanics (Days 24–26) as separate topics. Today, you must synthesize them into a single coherent narrative. The examiner will not ask isolated FSPL questions — they will ask you to **connect the physics to the system performance**.

**The master equation chain:**

Everything connects through one variable: **distance**. The Earth-Mars distance, varying from 54.6 million km (opposition) to 401 million km (conjunction) over the 779.94-day synodic period, drives a cascading chain of effects:

```
Distance (d) → FSPL (20·log₁₀(4πd/λ)) → Received Power → Link Margin → Achievable Data Rate
```

At opposition (54.6M km):
- FSPL at 1550 nm: ~353 dB
- Received power: high → margin is generous
- Data rate: up to 200 Mbps
- Light time: 3.0 minutes one-way

At conjunction (401M km):
- FSPL at 1550 nm: ~370 dB
- Received power: low → margin shrinks
- Data rate: drops to ~2 Mbps
- Light time: 22.3 minutes one-way

The 17.3 dB FSPL swing (20·log₁₀(401/54.6)) translates to a **100× data rate range** because data rate scales with SNR, which scales with received power, which scales with 1/d².

**How AETHERIX encodes this:**

The `estimate_data_rate()` function in `contact_windows.py` directly implements the inverse-square relationship:

```python
def estimate_data_rate(distance_km):
    min_distance_km = 54.6e6
    max_rate_mbps = 200.0
    rate = max_rate_mbps * (min_distance_km / distance_km) ** 2
    return max(2.0, min(200.0, rate))  # clamp to [2, 200] Mbps
```

This means:
- At opposition (54.6M km): rate = 200 × (54.6/54.6)² = **200 Mbps**
- At average (225M km): rate = 200 × (54.6/225)² = 200 × 0.0588 = **11.8 Mbps**
- At conjunction (401M km): rate = 200 × (54.6/401)² = 200 × 0.0185 = **3.7 Mbps**

The function clamps to a minimum of 2 Mbps (below this, even basic communication becomes impractical) and maximum of 200 Mbps (hardware limit).

**Performance across the synodic cycle:**

| Phase | Distance | FSPL (1550 nm) | Data Rate | Light Time | RL Agent Behavior |
|-------|----------|----------------|-----------|------------|-------------------|
| Opposition (±90 days) | 54.6–80M km | 353–358 dB | 200→100 Mbps | 3–4.5 min | Aggressive forwarding, high throughput |
| Quadrature (±180 days) | 150–225M km | 360–365 dB | 50→12 Mbps | 8–12.5 min | Balanced store/forward |
| Near-conjunction (±30 days) | 300–401M km | 368–370 dB | 5→2 Mbps | 17–22.3 min | Conservative, store-heavy, use Lagrange relays |
| Conjunction (14 days) | ~401M km | ~370 dB | 0 (direct) | 22.3 min | Autonomous ops, all data stored, relay-only |

**Why this matters for the RL agent:**

The RL agent's reward function includes a delay penalty (β = 0.001 per second). During conjunction, the 22-minute light time means every forward decision incurs a 1,320-penalty-point cost. The agent learns to minimize forwards during conjunction and maximize them during opposition. This distance-adaptive policy is exactly what static CGR cannot achieve — CGR uses a fixed contact schedule that doesn't adapt to real-time link quality.

**The hybrid optical/RF integration:**

During phases where optical margin goes negative (near conjunction), the system automatically falls back to RF Ka-band. RF has lower FSPL (due to lower frequency) but also lower antenna gain — the net result is 2–6 Mbps, which is still sufficient for critical P0/P1 bundles. The combined availability (99.96%) ensures the network never goes completely dark, even during conjunction (via Lagrange relay paths).

**Presenting this in the oral exam:**

When the examiner asks about performance, don't just recite numbers. Tell the story:
1. Start with distance (54.6M–401M km, synodic cycle of 780 days).
2. Show how FSPL follows (353–370 dB at 1550 nm).
3. Translate to data rate (200→2 Mbps via inverse-square).
4. Explain how the RL agent adapts (distance-phase in state, adaptive store/forward).
5. Note the conjunction fallback (Lagrange relays, 50–70% availability).

## 🔬 In AETHERIX

The integration is visible across multiple source files:

- **`src/orbital/contact_windows.py`:** `estimate_data_rate(distance_km)` encodes the inverse-square law; `get_distance_timeline(num_points=780)` generates the full-cycle timeline; `predict_contact_windows()` combines distance with contact duration estimates.
- **`src/infrastructure/link_budget.py`:** `calculate_mars_earth_link(scenario)` computes optical budgets at minimum/average/maximum distances, showing how margin varies with distance.
- **`src/infrastructure/rf_link_budget.py`:** `calculate_mars_earth_link(scenario)` does the same for RF, showing why RF maintains connectivity when optical fails.
- **`src/orbital/doppler.py`:** Doppler shifts are velocity-dependent, and velocity varies with orbital position — another distance-driven effect.
- **`src/orbital/topology.py`:** Inter-tier link rates (e.g., 3→4 at 50 Mbps, 600s latency) are set to reflect the deep-space light-time and path loss at Lagrange-to-Mars distances.

The topology's `get_contact_graph()` method attaches per-contact data rate and delay to each edge, so the routing engine and RL agent always operate with distance-aware metrics.

## 📐 Key Numbers & Formulas

**The integration chain — memorize this:**

```
Distance → FSPL → Received Power → Margin → Data Rate → RL Policy

d = 54.6M km → FSPL = 353 dB → P_rx ≈ −222 dBm → margin generous → 200 Mbps → aggressive forwarding
d = 225M km  → FSPL = 365 dB → P_rx ≈ −234 dBm → margin tight   → 12 Mbps  → balanced
d = 401M km  → FSPL = 370 dB → P_rx ≈ −239 dBm → margin negative → 2 Mbps   → store + Lagrange relay
```

**Data rate formula (inverse-square):**
```
R(d) = 200 × (54.6M / d)²  Mbps, clamped to [2, 200]
```

**Synodic cycle summary:**

| Parameter | Opposition | Average | Conjunction |
|-----------|-----------|---------|-------------|
| Distance | 54.6M km | 225M km | 401M km |
| Light time | 3.0 min | 12.5 min | 22.3 min |
| FSPL (1550 nm) | 353 dB | 365 dB | 370 dB |
| Data rate | 200 Mbps | 12 Mbps | 2 Mbps |
| RF fallback needed? | No | Marginal | Yes (Ka-band) |
| Lagrange relay needed? | No | No | Yes (50–70% avail.) |

## 🔗 Standards & References

- [CCSDS 141.0-B-1 — Optical Communications Physical Layer](https://public.ccsds.org/Pubs/141x0b1.pdf)
- [CCSDS 401.0-B-30 — RF and Modulation Systems](https://public.ccsds.org/Pubs/401x0b30.pdf)
- [RFC 4838 — DTN Architecture](https://datatracker.ietf.org/doc/html/rfc4838)
- [RFC 9171 — Bundle Protocol Version 7](https://datatracker.ietf.org/doc/html/rfc9171)
- [NASA DSOC — Deep Space Optical Communications results (2023)](https://www.jpl.nasa.gov/missions/dsoc/)

## 💡 How the Examiner Will Probe This

**Q: "Walk me through how AETHERIX's data rate varies over the synodic cycle."**
Start with distance (54.6M–401M km over 780 days). FSPL follows as 20·log₁₀(4πd/λ): 353→370 dB at 1550 nm. Received power drops accordingly. Data rate scales as 1/d²: 200 Mbps at opposition → 2 Mbps at conjunction. The RL agent adapts by storing more during high-distance phases and forwarding aggressively during opposition. Near conjunction, RF Ka-band fallback and Lagrange relay paths maintain connectivity.

**Q: "Your link margin is negative at conjunction. Does the system stop working?"**
No. Three mechanisms maintain connectivity: (1) data rate is reduced from 200 to 2 Mbps, which improves Eb/N0 by 20 dB (Shannon capacity trade-off); (2) RF Ka-band backup provides 2–6 Mbps with better weather resilience; (3) Lagrange relay paths (ES-L4/L5) bypass the Sun-blocked direct path with 50–70% availability. DTN store-and-forward ensures no data is lost — only delayed.

**Q: "How does the 22-minute light time at conjunction affect your RL agent?"**
The agent's state information is always 3–22 minutes stale. It cannot rely on real-time feedback. Instead, it uses contact window predictions and distance-phase awareness to make proactive decisions. The reward function's delay penalty (β=0.001/s) is small enough that a 22-minute forward (penalty 1.32) is still better than indefinite storage if a contact window is available. The agent learns the optimal trade-off between waiting for better conditions and forwarding now.

## ✅ Self-Check Questions

1. Walk through the complete chain: distance → FSPL → received power → data rate for average distance.
2. Why does data rate scale as 1/d² rather than 1/d? What physics drives this?
3. How does the `estimate_data_rate()` function's clamping to [2, 200] Mbps reflect real hardware constraints?
4. Explain why the RL agent's delay penalty (β=0.001/s) is set to that specific value relative to conjunction light times.
5. If you had 60 seconds to explain AETHERIX's distance-driven performance variation, what would you say?

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/contact_windows.py` (distance → rate), `src/infrastructure/link_budget.py` (distance → margin), `src/orbital/doppler.py` (velocity → Doppler)
- **Topic summaries:** `interview_prep/topic_summaries/link_budget.md` + `orbital_mechanics.md` (read together for integration)
- **Mock interview:** `interview_prep/practice/mock_interview.md` — Q10 (FSPL at 225M km), Q11 (contact windows)
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §4 (quantitative derivations), §11 (scale-out to Jupiter)
- **Demo:** Run `python src/infrastructure/link_budget.py` for all three scenarios (minimum/average/maximum) side by side
