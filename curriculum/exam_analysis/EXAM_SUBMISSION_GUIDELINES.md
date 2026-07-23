# AETHERIX EXAM — SUBMISSION GUIDELINES & ZERO-FAIL CHECKLIST

> **PRIVATE — this file is git-ignored and must NEVER be committed or pushed.**
> The repository `github.com/matx104/AETHERIX` is PUBLIC (an examiner requirement)
> and the examiner inspects it. Exam strategy does not belong in the submission.

| Fact | Value |
|------|-------|
| Program | Al-Nafi AI-Ops Diploma — EduQual Level 6 Diploma in AI Operations |
| Topic | 59 — Interplanetary Communication Network (DTN + Quantum + Space Infrastructure) |
| Exam date | **September 3, 2026** (Zoom, camera ON required) |
| Examiner | Muhammad Faisal (founder) or Muhammad Fel (faculty) |
| Attempt | **Second** — first attempt (different topic, same examiner) was rejected |
| Live demo | https://matx104.github.io/AETHERIX/ |
| Repo | https://github.com/matx104/AETHERIX (must stay public, clean-clone runnable) |

---

## 1. Why the first attempt failed (all six causes must stay fixed)

1. **Zero embedded citations** — 40+ citations existed for Q&A but none were in the
   submission. Examiner's rule: **"If it doesn't come to me, it doesn't exist."**
2. **Attribution fraud** — industry statistics (IBM/Forrester-class baselines)
   presented as personal achievements ("we achieved X").
3. **No architecture diagrams in the submission** — described verbally only.
4. **No code submitted** — the repo existed but was not part of the package.
5. **Presentation didn't match the topic brief line-by-line** — learning-objective gaps.
6. **Unverifiable numbers** — every statistic was an orphan without a source tag.

The examiner called the work "conceptually very strong." The failure was
**packaging, not substance**. The fix is more evidence, properly attributed — never
"dumbing it down."

---

## 2. The citation framework — three-layer attribution

Every claim on every slide is tagged as exactly one of:

- **Layer A — Industry/Scientific baseline `[1]–[20]`**: someone else's data.
  "Current Mars downlink rates are 0.5–6 Mbps [1]."
- **Layer B — Project design decision `[A1]–[A8]`**: cite the code.
  "AETHERIX replaces static CGR with a Q-learning agent (src/routing/rl_agent.py) [A1]."
- **Layer C — Simulation result `[A1]–[A8]`, explicitly labelled**: cite the run.
  "Radiation protection factor 200× — run_simulation.py Module 6 [A6]."

**Critical rule:** never present Layer A data as a Layer C result. Design *targets*
(>95% availability, 2–200 Mbps capability) are labelled as targets, never as
measured results. If a number cannot be cited, it is removed or labelled an
estimate with stated assumptions (this is why the $0.10/$0.01 cost/MB row was
**removed** from all decks and the handout).

### Reference numbering (as embedded in the decks)

- `[1]` NASA JPL Mars Relay Network · `[2]` CCSDS 734.2-B-1 · `[3]` JPL Horizons
  ephemeris · `[4]` NASA DSOC (Psyche) · `[5]` CCSDS 141.0-B-1 · `[6]` CCSDS
  131.0-B-3 · `[7]` CCSDS 121.0-B-3 · `[8]` CCSDS 122.0-B-2 · `[9]` RFC 9171 ·
  `[10]` RFC 5326 · `[11]` RFC 7242 · `[12]` RFC 4838 · `[13]` Bennett-Brassard
  1984 · `[14]` Ekert 1991 · `[15]` Shor-Preskill 2000 · `[16]` NIST FIPS 203 ·
  `[17]` NIST FIPS 204 · `[18]` BAE RAD750 · `[19]` ESA LEON3FT · `[20]` RFC 4838 §3.1
- `[A1]` rl_agent.py · `[A2]` topology.py · `[A3]` run_simulation.py Module 3 ·
  `[A4]` link_budget.py · `[A5]` qkd.py · `[A6]` radiation.py · `[A7]`
  prioritization.py · `[A8]` run_simulation.py Module 4 (solar conjunction)

---

## 3. The submission package — six artifacts, all IN the examiner's hands

| # | Artifact | Location |
|---|----------|----------|
| 1 | Presentation deck (PPTX + PDF, compact 31 + full 50) | `presentation/output/` |
| 2 | Architecture diagrams (embedded in decks + standalone PNGs) | `docs/diagrams/` |
| 3 | Code — key scripts at minimum: `rl_agent.py`, `qkd.py`, `run_simulation.py` | repo |
| 4 | References slides (2 per deck: Industry [1]–[20] + Project [A1]–[A8]) | in decks |
| 5 | One-page examiner handout with Key References section | `presentation/handouts/` |
| 6 | Live demo URL, tested, open in a tab | matx104.github.io/AETHERIX |

Nothing is left as "available upon request." Zip/email the package to the examiner
**before** the exam if pre-submission is allowed — ask.

---

## 4. Learning objectives a–h → slide coverage (compact deck, 31 slides)

| LO | Requirement | Compact slides |
|----|-------------|----------------|
| a | DTN Protocols (BPv7, store-and-forward, custody) | 5, 8 |
| b | Quantum Communication (QKD, repeaters, PQC) | 16, 17 |
| c | Space Infrastructure (constellations, DSN, Lagrange) | 6, 7, 9, 10 |
| d | Orbital Mechanics (propagation, Doppler, link budget) | 11, 12, 18 |
| e | Radiation Hardening (SEU, TMR, ECC, FDIR) | 19 |
| f | Data Prioritization (QoS, compression, emergency) | 20 |
| g | Industry Application (real missions, agencies) | 22, 23, 24 |
| h | Tools & Standards (Python, CCSDS, RFC) | 26 |

Also required and present: Trade-off Analysis (24: 1550 nm optical vs RF, custom RL
vs ION-DTN, Q-table vs DQN) and Failure & Recovery (25: optical blackout →
Ka-band RF fallback via ES-L4/L5 Lagrange relays). References at 29–30.

---

## 5. The lingo audit — precise vocabulary only

| ❌ Don't say | ✅ Say instead |
|-------------|----------------|
| "data gets sent" | "bundle custodial transfer via BPv7 convergence layer" |
| "the path changes" | "dynamic topology reconfiguration based on contact windows" |
| "it's secure" | "information-theoretic security via QKD (BB84 decoy-state)" |
| "AI finds the best route" | "Q-learning agent optimizes routing policy via reward-driven exploration" |
| "it stores data" | "store-and-forward persists bundles during link unavailability" |
| "radiation messes up computers" | "single event upsets induce bit flips in memory registers" |
| "it fixes itself" | "FDIR transitions to safe mode" |
| "signal gets weaker" | "free-space path loss attenuates the carrier ∝ distance²" |
| "we use encryption" | "post-quantum assurance via ML-KEM (FIPS 203)" |
| "it's faster" | "10–100× throughput improvement over baseline RF [1] vs [A4]" |

**Keyword hit-list** (the examiner ticks boxes): Bundle Protocol Agent, custodial
transfer, convergence layer, LTP, CGR, endpoint ID · QBER threshold, BB84, decoy
states, E91, entanglement swapping, privacy amplification, CASCADE, ML-KEM,
ML-DSA · DSN Goldstone/Madrid/Canberra, areostationary, Lagrange, Walker Delta,
EIRP · synodic period, true anomaly, solar conjunction, Doppler compensation,
link margin · SEU, SEL, TID, TMR, SECDED, memory scrubbing, FDIR, watchdog ·
QoS scheduling, CCSDS compression, deadline-aware preemption, P0–P4.

---

## 6. Examiner patterns — the 11 decoded moves

1. **The Funnel** — broad → narrow → specificity trap. Answer with specifics first.
2. **The Slide Anchor** — questions come FROM your slides; slides are the question bank.
3. **The Trap Question** — the "obvious" answer is wrong; pause on compliance questions.
4. **The ELI5** — plain English first, then the technical term.
5. **The Business Context Reframe** — add business impact to every technical answer.
6. **The Capstone Synthesis** — final questions combine domains. Structure:
   Architecture → Security → Compliance → AI.
7. **The Lingo Penalty** — informal vocabulary loses marks even when content is right.
8. **The Riddle-Reveal** — an analogy leads to a tool/concept name; listen for the noun.
9. **The "List Five"** — prepare 5-item lists: DTN implementations, QKD protocols,
   RL algorithms, orbital perturbations, radiation effects.
10. **Time-Bound Answers** — "give me 20 seconds": crisp bullet delivery.
11. **Slam Dunk Flagging** — hesitating on a flagged-easy question is a negative signal.

### Must-know instant answers
- DTN? → store-and-forward networking for high-delay/disruption environments.
- Protocol? → Bundle Protocol v7, RFC 9171. Convergence layer for deep space? → LTP (RFC 5326).
- Tiers/nodes? → five tiers, 241 nodes. QBER? → quantum bit error rate, secure below 11%.
- Reward function? → R = α·delivery − β·delay − γ·hops − δ·drops − ε·energy; α=1.0, δ=10.0.
- Exploration? → epsilon-greedy, decay 0.995. PQC? → ML-KEM (FIPS 203), ML-DSA (FIPS 204).
- Why DTN not TCP? → ~44 min RTT breaks the handshake; DTN needs no end-to-end connection.
- Solar conjunction? → optical fails → Module 4: Ka-band RF via ES-L4/L5 Lagrange relays.
- Capstone answer structure: (1) architecture, (2) security layer, (3) routing
  intelligence, (4) radiation resilience, (5) standards compliance.

---

## 7. Countdown checklists

### T-48 h (September 1)
- [ ] Citations audit: every statistic on every slide has [N]/[AN]
- [ ] References slides present in both decks; attribution is three-layer clean
- [ ] All 8 LOs mapped; Radiation + Prioritization + Trade-off + Failure slides present
- [ ] Code, diagrams, handout, decks all IN the package; PPTX + PDF open on a clean machine
- [ ] Clean clone: `python run_simulation.py` works with zero pip installs
- [ ] `python -m pytest tests/ -q` → all pass

### T-24 h (September 2)
- [ ] Full timed run-through (15–20 min), recorded and reviewed
- [ ] Mock interview vs the 106-question bank; lingo + keyword density check
- [ ] Package sent to examiner (if pre-submission allowed); demo URL + Zoom tested

### T-0 (September 3)
- [ ] Camera ON · presenter mode ready · demo tab open · repo open for "show me the code"
- [ ] References slide one keypress away during Q&A
- [ ] Bismillah — start naturally · speak slowly · structure answers ("First… second…")
- [ ] One sentence of business impact per answer
- [ ] Admit ignorance cleanly: "I don't know that value, but the underlying concept is…"

---

## 8. The walk-away decision (if offered)

Last time the examiner offered a clean withdrawal three times; proceeding was a
mistake. This time: be prepared enough that it isn't offered. If it is:
- Fumbled 3+ questions badly → **take the exit**, keep the record clean.
- Performing well but a format issue is cited → ask for the specific requirement,
  address it live if possible.
- Offered as courtesy while performing well → decline politely: "I'm confident in
  my work, I'd like to continue."

---

## 9. Verification status — July 23, 2026 (submission day)

Verified by fresh runs on this machine:

- **480/480 tests pass** (`pytest tests/ -q`, 11.5 s).
- **`run_simulation.py` exits 0 on system Python** (zero pip installs): Module 6
  shows 37,159 raw upsets → 185.8 residual, 200× protection, 3,334× TMR gain,
  2,127× RAD750 TID margin; Module 5 BB84 clean 0.0% / eavesdropped 24.7% QBER.
- **Compact PDF 31 pages / compact PPTX 31 slides; full PDF 50 pages / full PPTX
  50 slides.** Every content slide carries [N]/[AN] citation footers (only title
  and Thank-You pages have none). Two References slides per deck.
- **Cost/MB claim removed** everywhere; handout has Key References [1]–[20] + [A1]–[A8].
- **No hardcoded absolute paths** in tracked source; `requirements.txt` pinned;
  architecture diagrams in `docs/diagrams/`; README Getting Started present;
  showcase site has References nav + 64-entry IEEE list, and quotes 480 tests.
- **Fixed today during verification:** full-PDF footer denominator (was "/ 51" on a
  50-page deck), stale "189 tests" in two speaker-note blocks + the presentation
  script, stale "202-test suite" comment in requirements.txt, and the deck date
  ("January 2026" → "September 2026" in all four generators). All four decks
  regenerated and re-verified after the fixes.

### ⚠ Open risk — public repo contains exam-strategy material
`curriculum/exam_analysis/` (decoded examiner patterns, transcripts) and
`interview_prep/` (question bank, mock answers, cheat sheets) are **tracked in the
public repo the examiner will inspect**. Decide deliberately whether to relocate
them to a private repo before submission. This file itself is git-ignored.

---

*"Do not be sorry. Be better." — Kratos*
