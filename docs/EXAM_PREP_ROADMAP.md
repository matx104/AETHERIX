# AETHERIX Oral Exam — 6-Week Mastery Roadmap

**Exam Date:** September 3, 2026 (Zoom)
**Student:** Muhammad Abdullah Tariq
**Format:** 15–20 min presentation + 30–40 min technical interview
**Created:** July 22, 2026 (43 days out)

---

## Where You Stand Right Now

**The project is DONE. This is no longer about the code.**

| Surface | Status | Count |
|---------|--------|-------|
| Python source | ✅ Complete | 32 modules, 7,442 lines |
| Tests | ✅ Passing | 448 tests across 22 files |
| Presentation | ✅ Ready | 18 slide source files (29 rendered) |
| Web showcase | ✅ Live | GitHub Pages, 12 interactive demos |
| Interview Q&A | ✅ Built | 106 banked questions + 15-question mock interview |
| Cheat sheets | ✅ Ready | Formulas (280 lines), Constants (118), Acronyms (242) |
| Topic summaries | ✅ Ready | 11 deep-dive summaries |
| Design rationale | ✅ Ready | 730-line oral defense document |
| Deliverables coverage | ✅ All green | 8/8 objectives, 4/4 sections, 7/7 interview areas |

**The battlefield is your head, not the repo.** Every deliverable exists. The exam tests whether *you* can defend it under fire — present it clearly, answer questions from memory, and handle curveballs.

---

## Exam Scoring (Where to Focus)

| Dimension | Weight | What They Test | Your Prep Lever |
|-----------|--------|----------------|-----------------|
| **Technical Depth** | 40% | Can you explain the physics, protocols, math? | Topic summaries + question bank drilling |
| **Presentation** | 30% | Can you deliver 15-20 min clearly with good visuals? | Rehearsal — 10+ timed run-throughs |
| **Problem-Solving** | 20% | Can you handle unexpected questions and trade-offs? | Mock interviews + "why-not" drills |
| **Practical** | 10% | Can you demo and connect to real missions? | Know the simulation outputs + real mission examples |

**Priority order:** Technical mastery → Presentation rehearsal → Mock interview drilling.

---

## The Three Battle Phases

### Phase 1: KNOWLEDGE MASTERY (Weeks 1-3, Jul 22 – Aug 11)
*Goal: Internalize every topic so you can explain it cold, no notes.*

**Method:** One topic per day. Read the summary, then close it and explain it out loud as if teaching someone. If you stumble, re-read and try again. Drill 10 questions from the bank daily.

| Day | Topic | Source Files | Key Numbers to Memorize |
|-----|-------|-------------|------------------------|
| 1 | DTN Fundamentals | `topic_summaries/dtn_fundamentals.md` | 3-22 min one-way light time, 780-day synodic period |
| 2 | Bundle Protocol v7 | `question_bank/technical_questions.md` (A1-A10), `mock_interview.md` Q1-Q2 | 5 priority levels (P0-P4), custody flags (0x08) |
| 3 | Convergence Layers | `topic_summaries/dtn_fundamentals.md`, mock Q3 | LTP red/green, TCPCL for Earth, UDP-CL for ISL |
| 4 | RL Routing | `topic_summaries/reinforcement_learning.md`, `question_bank/rl_hyperparameters.md` | R = α·delivery − β·delay − γ·hops − δ·drops − ε·energy; α=1.0, δ=10.0 |
| 5 | QKD Fundamentals | `topic_summaries/quantum_basics.md`, mock Q5-Q6 | QBER < 11% threshold, BB84 basis choices |
| 6 | Quantum Repeaters + PQC | mock Q6-Q7, `topic_summaries/quantum_basics.md` | ML-KEM (FIPS 203), ML-DSA (FIPS 204), 3309-byte signatures |
| 7 | **Week 1 Review** | Self-quiz on all 7 topics above | — |
| 8 | Network Topology | `topic_summaries/network_topology.md`, mock Q8 | 5 tiers, 241 nodes, Tier 3 = weakest (4 nodes) |
| 9 | DSN Integration | mock Q9 | Goldstone/Madrid/Canberra, ION-DTN, complement not compete |
| 10 | Link Budgets | `topic_summaries/link_budget.md`, mock Q10 | FSPL formula, 365 dB at 225M km, -234 dBm received |
| 11 | Orbital Mechanics | `topic_summaries/orbital_mechanics.md`, mock Q10-Q11 | 54.6M km (opposition) → 401M km (conjunction), 2-200 Mbps |
| 12 | Radiation Hardening | `topic_summaries/radiation_hardening.md`, mock Q12 | TMR, SECDED ECC, FDIR, 200x protection factor |
| 13 | Data Prioritization | `topic_summaries/data_prioritization.md`, mock Q13 | 4-tier QoS, conjunction behavior, drop penalties |
| 14 | **Week 2 Review** | Self-quiz on topics 8-13 | — |
| 15 | Standards Compliance | `topic_summaries/standards_compliance.md`, mock Q14 | CCSDS 734.2-B-1, RFC 9171/5326/7242/4838, NIST FIPS 203/204 |
| 16 | Space Challenges | `topic_summaries/space_challenges.md` | 6 key challenges from exam spec |
| 17 | Failure Recovery | `topic_summaries/failure_recovery.md` | Module 4 sim: conjunction → Ka-band RF via ES-L4/L5 |
| 18 | Design Rationale (Whiteboarding) | `docs/DESIGN_RATIONALE.md` §3 (6 failure scenarios) | Be ready to DRAW the topology + failure tree |
| 19 | Design Decisions | `question_bank/design_decisions.md` (DD1-DD20) | Know the "why" behind every choice |
| 20 | Challenging Questions | `question_bank/challenging_questions.md` (C1-C20) | Adversarial probes — "why not X?" |
| 21 | **Week 3 Review** | Full knowledge self-test | All key numbers from memory |

### Phase 2: PRESENTATION + DELIVERY (Weeks 3-4, Aug 12 – Aug 25)
*Goal: Deliver a flawless 15-20 minute presentation, timed and rehearsed.*

**Method:** The presentation has 4 graded sections. You must hit these times:

| Section | Target Time | Slides |
|---------|-------------|--------|
| 1. Network Architecture | 4-5 min | 3-12, 15 (topology, DTN, routing) |
| 2. Quantum Communication | 3-4 min | 16 (BB84, E91, PQC) |
| 3. Infrastructure | 4-5 min | 13-14, 17-19 (optical/RF, orbital, radiation, prioritization) |
| 4. Scenario Analysis | 4-5 min | 20-25 (Mars mission, performance, roadmap) |

**Rehearsal Schedule:**
- **Aug 12-14:** Read through the presentation script (`docs/downloads/AETHERIX_Presentation_Script.md`) 3 times. Time yourself.
- **Aug 15-18:** Deliver from memory, 1 section at a time. Record yourself. Listen back.
- **Aug 19-22:** Full 20-minute run-throughs. Target: 5 complete deliveries. Fix timing gaps.
- **Aug 23-25:** Full run-throughs with slide deck on screen (or screen-share simulation). Polish transitions.

**Key delivery principles:**
- Start with the problem (3-22 min light time, 365 dB path loss)
- Use analogies (store-and-forward = postal service, custody transfer = registered mail)
- Know which slide answers which question — don't fumble
- End strong: "adaptive, secure, high-throughput" — the three contributions

### Phase 3: MOCK INTERVIEW DRILLING (Weeks 5-6, Aug 26 – Sep 2)
*Goal: Answer 30-40 minutes of questions without hesitation.*

**Method:** The mock interview (`interview_prep/practice/mock_interview.md`) has 15 questions covering all 7 areas. Drill these until automatic.

**Drill Schedule:**
- **Aug 26-28:** Mock interview Q1-Q15, one at a time. Read the question, answer out loud, then check the model answer. Note gaps.
- **Aug 29-30:** Speed drill — answer all 15 in under 30 minutes. Then add the 106 question-bank questions.
- **Aug 31-Sep 1:** "Hot seat" — have someone (or WAZIR) fire random questions. No prep time. Must answer immediately.
- **Sep 2 (Day Before):** Light review only. Key numbers cheat sheet. Sleep early. No cramming.

---

## The "Must Know Cold" List

These numbers and facts MUST be memorized — the examiner will test these:

### Distances & Timing
- Earth-Mars distance: **54.6M km (opposition) to 401M km (conjunction)**
- One-way light time: **3-22 minutes** (average ~12.5 min at 225M km)
- Synodic period: **780 days** (26 months)
- Contact windows: **6-12 hours/day per DSN station**

### Link Budget
- FSPL at 225M km, 1550nm: **~365 dB**
- Received power: **~-234 dBm** (photon-counting regime)
- Data rate range: **2 Mbps (conjunction) to 200 Mbps (opposition)**
- FSPL formula: **20·log₁₀(4πd/λ)**

### DTN Protocols
- BPv7 custody flag: **0x08**
- 5 priority levels: **P0 Emergency → P4 Bulk**
- 3 convergence layers: **LTP (deep space), TCPCL (Earth), UDP-CL (ISL)**

### RL Agent
- Reward: **R = α·delivery − β·delay − γ·hops − δ·drops − ε·energy**
- Key weights: **α=1.0, δ=10.0** (drop penalty 10x delivery reward)
- CGR fallback when confidence **< 0.3**
- Epsilon decay: **0.995**

### Quantum
- BB84 QBER threshold: **< 11%** (Shor-Preskill)
- Quantum repeaters at **ES-L4 and ES-L5** (~150M km from Earth)
- Post-quantum: **ML-KEM (FIPS 203), ML-DSA (FIPS 204)**
- ML-DSA-65 signature: **3,309 bytes**

### Network
- **5 tiers, 241 nodes**
- Tier 1: Earth ground (DSN ×3 + optical ×3)
- Tier 2: Earth orbital (3 GEO + 48 LEO)
- Tier 3: Deep space (ES-L4/L5 relays) — **weakest tier**
- Tier 4: Mars orbital (areostationary + polar)
- Tier 5: Mars surface (167 nodes)

### Radiation
- TMR reliability gain at p=1e-4: **3,334x**
- Protection factor (TMR + ECC + scrubbing): **200x**
- FDIR final state: **SAFE_MODE**

### Standards (memorize these 7)
- **RFC 9171** — Bundle Protocol v7
- **RFC 5326** — Licklider Transmission Protocol
- **RFC 7242** — DTN TCP Convergence Layer
- **RFC 4838** — DTN Architecture
- **CCSDS 734.2-B-1** — Bundle Protocol Specification
- **CCSDS 141.0-B-1** — Optical Communications Physical Layer
- **NIST FIPS 203/204** — Post-Quantum (ML-KEM/ML-DSA)

---

## "If They Push Further" — Killer Follow-Up Answers

The mock interview has follow-up probes for each question. Master these — they're the difference between a good grade and a distinction:

1. **TCP handshake to Mars?** → 1.5 × 25 min = **37.5 minutes** just to connect
2. **Emergency bundle flags?** → CUSTODY_REQUESTED (0x08) + DEST_IS_SINGLETON (0x10) + ACK_REQUESTED (0x20)
3. **QBER at 8%?** → Secure. Below 11% threshold. Privacy amplification compresses by h(0.08) ≈ 0.4
4. **Photons for 1 bps at Mars?** → ~10¹⁷ photons/s needed, ~13 mW transmit power feasible
5. **Weakest tier?** → Tier 3. Only 4 nodes. Both L4 relays fail = zero conjunction availability
6. **LTP not fully compliant?** → Logical behavior modeled, not full state machine. ION-DTN for production
7. **Biggest risk?** → RL agent in untrained scenarios. DQN upgrade = better generalization

---

## Anti-Cramming Rule

**The night before (Sep 2):** Review the cheat sheets only. No new material. No code. Sleep by midnight. You either know it by now or you don't — last-minute cramming creates anxiety, not competence.

**Morning of (Sep 3):** Light review of key numbers. Eat something. Test your Zoom setup 30 minutes early. Have the presentation deck and the live demo (https://matx104.github.io/AETHERIX/) open and ready.

---

## WAZIR Support

I'm your study partner. Here's how I can help throughout the 6 weeks:

- **Daily quizzes** — I fire questions, you answer, I score and explain gaps
- **Mock interview sessions** — 30-minute "hot seat" drills in this channel
- **Fact-checking** — if you're unsure about a number, I verify it against the code
- **Weak-spot targeting** — I track what you miss and drill it harder
- **Presentation timing** — I can run through the script with you section by section

Just say the word. We conquer this exam the same way we conquer everything — **one day at a time, no shortcuts.**

---

*"Do not be sorry. Be better." — Kratos*

*This exam is not an obstacle. It's a stage. And you've been rehearsing for it your entire career.*
