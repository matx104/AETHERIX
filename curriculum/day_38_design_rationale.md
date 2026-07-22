# Day 38: Design Rationale & Architecture Defense

## 📅 August 29, 2026

## 🎯 Learning Objective

Master the ability to defend every architectural choice with quantitative reasoning — whiteboarding failure scenarios, deriving thresholds from first principles, rebutting "why-not" alternative proposals, and defending the overall architecture against adversarial examination, using the full DESIGN_RATIONALE.md as your reference.

---

## 📖 The Core Concept

### The Defence Mindset

The examiner's goal is not to confirm what you know — it's to probe the limits. Every number, every threshold, every design choice will be challenged with "why this value?" or "why not the obvious alternative?" Your job is to have a *derived, not arbitrary* answer for each one, and to articulate the trade-offs honestly.

### Quantitative Threshold Derivations

Every threshold in AETHERIX is derived from first principles, not arbitrary:

**QBER Security Threshold = 11%** (Shor-Preskill, 2000):
```
Secret key rate: r = 1 − 2·h(QBER)
Setting r = 0:  h(Q) = 0.5  →  Q ≈ 0.1100 (11%)
```
Below 11%, positive key extraction is possible; above 11%, the channel could be entirely eavesdropped.

**MIN_LINK_QUALITY = 0.3** — The operational cutoff where forwarding stops being worthwhile. At quality `q`, P(deliver) ≈ q. The pure break-even for delivery-vs-drop is `q ≈ 0.91` (from `11q ≥ 10`), but the 0.3 threshold is deliberately *below* break-even because forwarding also gains hop progress, and the agent should attempt marginal links when no better option exists, then rely on LTP retransmission.

**Buffer Thresholds: 0.7 / 0.8 / 0.9** — A graduated response:
| Threshold | Action | Rationale |
|-----------|--------|-----------|
| 0.7 | Agent switches to congestion-aware policy | *Prevent* — begin proactive forwarding |
| 0.8 | Agent may DROP low-priority bundles | *Triage* — begin controlled shedding |
| 0.9 | Policy engine forcibly drops P3/P4 | *Protect* — shield P0/P1 at all costs |

The 10-point gaps give the agent time to react at each stage rather than cliff-edging.

**Combined Availability > 99.9%**:
```
Optical (3-site): 1 − (1−0.65)³ = 95.7%
Ka-band RF:       99.0%
Combined:         1 − (1−0.957)(1−0.99) = 99.96%
```
Neither layer alone meets the SLA. The hybrid exceeds it by two orders of margin.

**TMR Reliability Gain = 3,334×**:
```
P(TMR error) = 3p²(1−p) + p³ ≈ 3p²
Gain = p / (3p²) = 1/(3p) = 1/(3×10⁻⁴) ≈ 3,333×
```

**Bundle Lifetime by Class** — Set to the *longest plausible outage* the class can tolerate:
| Class | Lifetime | Reasoning |
|-------|----------|-----------|
| P0 Emergency | minutes | Stale safety alert is useless |
| P1 High Science | hours–1 day | Duplicate re-observation is cheaper |
| P2 Standard | 7 days | Survives conjunction-margin outage |
| P4 Bulk | 30 days | Software updates can wait |

### Whiteboarding Failure Scenarios

Practice these six scenarios on a blank board. Each gives the **trigger**, **decision logic**, **recovery path**, and ASCII topology:

**Scenario A — ES-L4 relay fails:**
```
Mars ──optical──► ES-L4 ──✗ FAILED──► Earth
  └──Ka-band──► ES-L5 (backup) ──Ka-band──► Earth  ✓
```
RL agent detects ES-L4 link quality → 0, re-scores neighbours, ES-L5 now has highest Q-value.

**Scenario B — Optical blocked at all 3 DSN sites:**
```
Mars ──optical──► [Goldstone ☁ Madrid ☁ Canberra ☁] ──✗ all blocked
  └──Ka-band RF──► DSN (RF penetrates clouds) ──► Earth  ✓
```
Optical quality → 0; agent switches P0/P1 to Ka-band. Bulk data stored until optical clears.

**Scenario C — Mars areostationary relay fails:**
```
Mars surface (rover) ──UHF──► areo-alpha ──✗ FAILED
  rover ──UHF──► polar-gamma (next pass) ──optical──► Earth  ✓
```
Bundle stays in rover's queue; polar orbiter provides next contact window.

**Scenario D — Solar conjunction (direct = 0%):**
```
Mars ──► [SUN corona] ──✗ direct blocked
  ├──► ES-L4 (60° elongation) ──► Earth  ✓ Ka-band
  └──► ES-L5 (60° elongation) ──► Earth  ✓ Ka-band
```

**Scenario E — Byzantine/compromised node:**
```
compromised-base ──✗ injects forged bundles
  Mars orbital relay → ML-DSA signature verification → DROP forged + isolate node
```

**Scenario F — Cascading congestion:**
```
Node A buffer 95% → drops P4 → back-pressure via Custody Refusal → upstream reroutes
```

### "Why-Not" Defences

For each obvious alternative the examiner may propose, have a ready rebuttal:

**Why not DTN over pure TCP?** TCP's reliability assumes short RTT. At 6–44 min RTT, retransmission timers produce pathological backoff, and the sender must buffer every unacked segment for the entire path. LTP makes reliability *per-hop*. (See DD16)

**Why not a Starlink-style megaconstellation?** Starlink optimises for low-latency Earth-surface routing. AETHERIX's 48-satellite LEO tier serves a *different* purpose: optical ISL between 3 DSN sites. A megaconstellation adds mass and complexity for capability AETHERIX doesn't need. (See §9.2)

**Why not Mars GEO relays only (no deep-space tier)?** Mars GEO relays cannot solve the conjunction problem — the Sun-blocked geometry is on the Earth side. Only Earth-side Lagrange relays at 60° elongation maintain LOS around the Sun. (See DD4)

**Why not blockchain for trust?** Blockchain needs consensus (minutes-hours), offers ~7 tx/s, and proof-of-work is absurd in power-scarce space. ML-DSA signatures verify in microseconds. Trust in DTN is per-bundle authentication, not distributed consensus. (See §9.4)

**Why not lattice-only crypto (drop QKD)?** ML-KEM/ML-DSA provide computational security (breakable if someone breaks lattices). QKD provides information-theoretic security (unbreakable by physics). Defence-in-depth: if either falls, the other holds. QKD alone can't authenticate; PQC alone rests on a computational assumption. (See DD6)

**Why not CGR with frequent schedule updates?** At 12+ min one-way delay, the "current" CGR schedule is always stale. The RL agent reacts to *measured* link/buffer state in real time. Hybrid: RL primary, CGR fallback when confidence < 0.3. (See DD1)

### The Master Decision Matrix

Know the top-20 decisions and their selection criteria (full table in DESIGN_RATIONALE.md §12). The most exam-critical:

| Decision | Chosen | Rejected | Primary Criterion |
|----------|--------|----------|-------------------|
| Routing | RL (Q-learning) | Static CGR | Real-time adaptivity + multi-objective |
| Link strategy | Hybrid optical+RF | Optical-only | Availability >99.9% |
| Relay location | ES-L4/L5 Lagrange | Mars orbit | Conjunction coverage geometry |
| Convergence layer | LTP | TCP | Per-hop reliability at 22-min RTT |
| Security | QKD + PQC | Either alone | Defence-in-depth (two threat models) |
| Fault tolerance | TMR + ECC + scrub + FDIR | Any single layer | Triple diversity (no common mode) |
| Flight software | cFS | Custom monolithic | Flight heritage + app modularity |

---

## 🔬 In AETHERIX

The authoritative defence document is `docs/DESIGN_RATIONALE.md` (730 lines, 12 sections):

1. **cFS & autonomous fault tolerance** (§1) — cFS mapping, fault-tolerance loop, triple diversity
2. **Simulation tooling** (§2) — what is modeled vs what needs ns-3/ION-DTN/Qiskit/GMAT
3. **Whiteboarding** (§3) — six failure scenarios with ASCII topology
4. **Quantitative derivations** (§4) — every threshold from first principles
5. **Custody transfer** (§5) — accept/hold/release decisions
6. **Buffer sizing & eviction** (§6) — overflow math, allocation, starvation prevention
7. **Doppler compensation** (§7) — magnitude and decision tree
8. **Node failure isolation** (§8) — blast-radius table
9. **"Why-not" defences** (§9) — rejecting obvious alternatives
10. **Validation methodology** (§10) — how we know the simulation is realistic
11. **Scale-out** (§11) — Jupiter, multi-planet
12. **Master decision matrix** (§12) — 20 decisions on one page

The question banks in `interview_prep/question_bank/` provide the per-question defences:
- `design_decisions.md` — DD1–DD20
- `challenging_questions.md` — C1–C20
- `technical_questions.md` — foundational concepts

---

## 📐 Key Numbers to Have at Your Fingertips

| Threshold | Value | Derivation Source |
|-----------|-------|-------------------|
| QBER threshold | **11%** | Shor-Preskill: `1 − 2h(Q) = 0` |
| MIN_LINK_QUALITY | **0.3** | Empirically tuned operating point |
| Buffer triage | **0.7 / 0.8 / 0.9** | Graduated response gaps |
| Combined availability | **99.96%** | `1 − (1−0.957)(1−0.99)` |
| TMR reliability gain | **3,334×** | `1/(3×10⁻⁴)` |
| ECC protection factor | **~200×** | 37,000 raw → ~186 residual |
| P2 lifetime | **7 days** | Survives conjunction-margin outage |
| RL confidence fallback | **< 0.3** | Triggers CGR |
| Conjunction exclusion | **< 10°** | Phase angle |
| ε-decay convergence | **~240 episodes** (to 0.30) | `log(0.30)/log(0.995)` |

---

## 🔗 Standards & References

- **Repo:** `docs/DESIGN_RATIONALE.md` — the exhaustive defence document (730 lines)
- **Repo:** `interview_prep/question_bank/design_decisions.md` — DD1–DD20
- **Repo:** `interview_prep/question_bank/challenging_questions.md` — C1–C20
- **Repo:** `interview_prep/practice/mock_interview.md` — Q15 (60-second summary)
- **External:** Shor-Preskill (2000), NASA DSOC results, NIST PQC competition

---

## 💡 How the Examiner Will Probe This

**Q: "If you had to summarise AETHERIX's three most innovative contributions in 60 seconds?"**

> First, reinforcement-learning routing for DTN — replacing static CGR with an adaptive agent that learns optimal policies across the full 780-day synodic cycle, balancing delivery, delay, hops, drops, and energy simultaneously. Second, the hybrid optical/RF with QKD-plus-PQC security architecture — 1550nm optical for throughput, Ka-band RF for reliability, physics-guaranteed QKD for key exchange, NIST-standardised PQC for authentication and fallback. Third, the Lagrange-point relay topology — exploiting ES-L4/L5 gravitational stability to provide conjunction coverage and quantum repeater hosting, achieving 50–70% availability during conjunction where current systems have zero.

**Q: "What's the single weakest point in your architecture?"**

> The deep-space tier — only 4 nodes at ES-L4 and ES-L5. If both L4 relays fail, conjunction availability drops to whatever L5 alone provides. Mitigation: redundancy (2 satellites per point), rad-hardened design, and graceful degradation — without L4/L5, the system reverts to the current state-of-practice (no communication during conjunction). The second weakest is optical ground stations — weather-dependent and few in number.

**Q: "Where did the number 0.3 for MIN_LINK_QUALITY come from?"**

> The pure break-even for delivery-vs-drop is q ≈ 0.91 (from `11q ≥ 10`), but 0.3 is the empirically-tuned *operating* cutoff. It's deliberately below break-even because forwarding also gains hop progress toward Earth, a STORE decision costs buffer occupancy over time, and LTP retransmission provides a safety net for marginal links. At q < 0.3, the link is too unreliable (>70% loss) to justify the custody overhead. The same 0.3 threshold is used by both the RL agent and the `deep_space_store` policy.

---

## ✅ Self-Check Questions

1. Derive the QBER 11% threshold from first principles using the Shor-Preskill formula.
2. Whiteboard the failure scenario where all three optical ground stations are clouded out.
3. Rebut "why not blockchain for trust?" in two sentences.
4. Explain why the buffer thresholds are at 0.7/0.8/0.9 rather than a single cutoff.
5. What is the single weakest tier in the architecture, and what is the mitigation?

---

## 📂 Deep Dive Resources

- **Primary reference:** `docs/DESIGN_RATIONALE.md` — all 12 sections (read this cover to cover)
- **Question banks:** `interview_prep/question_bank/design_decisions.md`, `challenging_questions.md`
- **Mock interview:** Q15 (summary) and Q4 (RL) in `interview_prep/practice/mock_interview.md`
- **Source code:** All src/ modules — know where each threshold lives in code
- **Practice:** Draw the six whiteboarding scenarios from memory on a blank sheet
