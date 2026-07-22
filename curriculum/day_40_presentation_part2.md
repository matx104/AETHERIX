# Day 40: Presentation Mastery — Part 2 (Infrastructure, Scenarios, Conclusion)

## 📅 August 31, 2026

## 🎯 Learning Objective
Master the second half of the AETHERIX oral presentation — Infrastructure/Link Budgets (4-5 min), Scenario Analysis (4-5 min), and Conclusion (1 min). Complete full timed run-throughs. Maps to exam weight **Presentation 30%**.

---

## 📖 Section-by-Section Delivery Guide

### Optical Communications & Link Budget (Slide 13) — 2 minutes — LIVE DEMO

**Script:**
> "Let me demonstrate the link budget calculations live."

**Open:** matx104.github.io/AETHERIX → Link Budget tab

**Key talking points:**
- 1550nm laser — standard telecom wavelength, mature components, eye-safe, atmospheric window
- 5W transmit power, 22cm TX aperture, 1m RX telescope
- Closest approach (54.6M km): 100-200 Mbps
- Maximum distance (401M km): 2-5 Mbps
- 30× faster than Mars Reconnaissance Orbiter's current RF capability
- **365 dB FSPL** at average distance — this number MUST roll off your tongue

**If demo fails (memorize this):**
> "At 225 million km average distance, free space path loss is 365 dB. With our transmit and receive gains, we achieve 10-20 Mbps — 10× current RF performance."

### Earth-Mars Data Journey (Slide 14) — 1.5 minutes

**The 7-hop journey:**
1. Mars surface (rover) → Mars relay
2. Mars relay → Mars orbital
3. Mars orbital → ES-L5 relay
4. ES-L5 → ES-L4
5. ES-L4 → GEO relay
6. GEO → DSN ground station
7. DSN → JPL mission control

**Key numbers:**
- 500 MB from Perseverance to JPL
- Total transit: ~13 minutes (vs 12.5 min light-time — near speed of light!)
- DTN overhead: < 5%
- Delivery ratio: 98.7%

### RL-Based Routing (Slides 15-16) — 2 minutes

**Flow:**
1. Traditional CGR requires pre-computed contact schedules — can't adapt
2. RL agent learns from experience: 8 state variables, 4 actions (forward/store/drop/split)
3. Reward function: R = α·delivery − β·delay − γ·hops − δ·drops − ε·energy
4. Epsilon-greedy exploration, epsilon decay 0.995
5. CGR fallback at confidence < 0.3
6. Multi-agent federated learning across distributed nodes

**Key talking point:**
> "The RL agent discovers routes that CGR cannot — paths through the Lagrange relays during conjunction that maintain 50-70% availability when direct Earth-Mars links are blacked out."

### Radiation Hardening (Slides 20-22) — 1.5 minutes

**Quick points:**
- Space radiation causes: SEU, SEL, MBU, TID
- Mars has no global magnetic field — higher radiation exposure
- Hardware mitigation: TMR (Triple Modular Redundancy), SECDED ECC, RAD750/LEON3FT
- Software mitigation: FDIR state machine, memory scrubbing, checkpointing
- NASA cFS integration: pub/sub software bus, autonomous fault tolerance

### Data Prioritization (Slides 23-24) — 1.5 minutes

**4-tier priority system:**
- **P0 Emergency:** Anomaly alerts, < 1 min delivery
- **P1 Mission-critical:** Science events, < 30 min
- **P2 High-priority:** Daily science, < 24 hr
- **P3 Standard:** Housekeeping/logs, < 7 days
- **P4 Bulk:** Archives, < 30 days

**QoS + Compression:**
- CCSDS 121.0-B-3 (lossless) and 122.0-B-2 (wavelet) compression
- Deadline-aware forwarding scheduler
- Emergency preemption: P0 bundles jump the queue

### Demo + Performance (Slides 25-27) — 2 minutes

**Demo the simulation:**
> "Let me run the full simulation."

**Key performance metrics:**
- 98.7% delivery ratio across 5 simulation modules
- End-to-end delay: 12-45 minutes (distance dependent)
- RL routing improves delivery 12% over CGR alone
- 241 nodes simulated, all modules passing

### Conclusion (Slides 28-29) — 1 minute

**Script:**
> "AETHERIX demonstrates that interplanetary communication is not just theoretically possible — it's architecturally solvable today. Bundle Protocol provides the transport layer. Reinforcement learning provides adaptive routing. Quantum key distribution provides information-theoretic security. And hybrid optical-RF links provide the bandwidth. Together, these technologies form a complete communication architecture for Mars mission support. Thank you — I welcome your questions."

**Delivery:**
- Slow down for the conclusion
- Make eye contact with all examiners
- Confident pause. Then: "Thank you. I welcome your questions."

---

## 📐 Full Presentation Timing — Master Sheet

| Section | Slides | Target | Running Total |
|---------|--------|--------|--------------|
| Title + Agenda | 1-2 | 50s | 0:50 |
| Challenge | 3-4 | 3:00 | 3:50 |
| DTN + BP | 5-9 | 4:00 | 7:50 |
| Topology | 10-12 | 3:00 | 10:50 |
| Optical/Link Budget | 13 | 2:00 | 12:50 |
| Earth-Mars Journey | 14 | 1:30 | 14:20 |
| RL Routing | 15-16 | 2:00 | 16:20 |
| Quantum Security | 17-19 | 3:00 | 19:20 |
| Radiation + Priority | 20-24 | 3:00 | 22:20 |
| Demo + Performance | 25-27 | 2:00 | 24:20 |
| Conclusion | 28-29 | 1:00 | 25:20 |

⚠️ **This is 25 minutes — too long!** Target is 15-20 minutes. You need to TRIM.

### Trimming Strategy

**Cut or compress:**
- Radiation + Data Priority: Compress to 2 min (was 3) → save 1 min
- Earth-Mars Journey: Cut to 1 min → save 30s
- Topology: Compress to 2.5 min → save 30s
- **New target: ~18 minutes** ✅

| Section | Trimmed Target |
|---------|---------------|
| Title + Agenda | 45s |
| Challenge | 2:30 |
| DTN + BP | 3:30 |
| Topology | 2:30 |
| Optical | 1:30 |
| Journey | 1:00 |
| RL Routing | 2:00 |
| Quantum | 2:30 |
| Radiation + Priority | 2:00 |
| **Total** | **~18:15** ✅ |

---

## 🔗 Standards & References

- [Presentation Script](https://github.com/matx104/AETHERIX/blob/main/docs/downloads/AETHERIX_Presentation_Script.md)
- [Live Demo Site](https://matx104.github.io/AETHERIX/)
- [CCSDS 121.0-B-3 — Lossless Compression](https://public.ccsds.org/Pubs/121x0b3.pdf)
- [CCSDS 122.0-B-2 — Image Compression](https://public.ccsds.org/Pubs/122x0b2.pdf)

---

## 💡 Examiner Psychology — What They're Thinking

During the presentation, examiners are evaluating:

1. **"Does this student understand what they built?"** — They can tell if you're reciting vs. understanding. Use natural language, not memorized scripts. If you forget a word, paraphrase.

2. **"Can they handle the demo going wrong?"** — Technology fails. If the demo site doesn't load, smoothly transition: "I'll describe the results from the simulation..." Don't panic, don't apologize excessively.

3. **"Is the depth appropriate for Level 6?"** — Level 6 = final-year bachelor's. Show you understand principles AND implementation. Name specific RFCs, cite specific code decisions, show you made deliberate engineering choices.

4. **"Can they manage time?"** — Running over is a red flag. Practice with a timer. If you're at 15 minutes and not at the conclusion, SKIP to the conclusion.

---

## ✅ Practice Checklist for Today

1. [ ] Full timed run-through with trimmed timing (target: 18 minutes)
2. [ ] Practice demo transitions: have the browser tab pre-loaded
3. [ ] Time yourself THREE times — take the average
4. [ ] Practice the "demo fails" backup for each demo moment
5. [ ] Memorize the conclusion word-for-word — it's your last impression
6. [ ] Record a full run-through on video (phone). Watch it back.
7. [ ] Practice in front of a mirror — check your posture and hand gestures
8. [ ] Identify your 3 weakest transition points and drill them

---

## 📂 Deep Dive Resources

- **Full script:** `docs/downloads/AETHERIX_Presentation_Script.md`
- **Slides:** `presentation/AETHERIX_Presentation.md`
- **Demo site:** [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/)
- **Performance data:** `docs/DELIVERABLES_COVERAGE.md`
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — for Q&A defense

---

## 🏆 Tomorrow: Day 41

Full mock interview walkthrough — 15 questions, 30-40 minutes. The other 40% of your grade that happens AFTER the presentation.
