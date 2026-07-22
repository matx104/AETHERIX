# Day 41: Mock Interview Mastery — 15 Questions, 30-40 Minutes

## 📅 September 1, 2026

## 🎯 Learning Objective
Master the technical interview portion of the exam. Walk through all 15 mock interview questions with model answers, learn the STAR-T response structure, and practice time management and admitting uncertainty gracefully. Maps to exam weight **Technical Depth 40% + Problem-Solving 20%**.

---

## 📖 The Interview Game Plan

After your 15-20 minute presentation, the examiner opens the floor to **30-40 minutes of technical questioning**. This is where 60% of your grade lives (Technical Depth 40% + Problem-Solving 20%).

### The STAR-T Response Structure

For every interview answer, use this framework:

- **S** — **Set up**: Direct answer first (1-2 sentences). Don't build to the point — lead with it.
- **T** — **Technical detail**: Expand with specifics. Name the RFC, the class name, the parameter value.
- **A** — **AETHERIX context**: Tie it to YOUR project. "In AETHERIX, this is implemented as..."
- **R** — **Rationale**: Why you made this choice. "We chose X over Y because..."
- **T** — **Trade-off**: What's the limitation or alternative? "The downside is..."

**Example — Q: "Why DTN over TCP?"**
> **(S)** TCP is unsuitable for space because it assumes low latency, continuous connectivity, and end-to-end acknowledgements. **(T)** At Mars's average RTT of 25 minutes, a TCP three-way handshake alone takes 37.5 minutes. **(A)** In AETHERIX, we use Bundle Protocol v7 (RFC 9171) with store-and-forward — each node holds bundles until the next contact window. **(R)** We chose this because contact windows are only 6-12 hours/day. **(T)** The trade-off is increased storage requirements at relay nodes, which we mitigate with data prioritization.

---

## 📖 All 15 Questions — Quick Reference

### LO1: DTN Fundamentals

**Q1: Why is TCP/IP unsuitable for interplanetary communication?** (2 min)
- Three TCP assumptions break: low latency, continuous connectivity, end-to-end ACKs
- TCP handshake to Mars: 1.5 × 25 min RTT = 37.5 min just to connect
- DTN solves with store-and-forward + custody transfer + convergence layers

**Q2: Explain BPv7 bundle structure and priority classes.** (2 min)
- Primary block (CBOR): source/dest EID, timestamp, lifetime, hop count, flags
- Payload block: application data
- Extension blocks: security, metadata
- 5 priority levels: P0 Emergency → P4 Bulk
- Flags: CUSTODY_REQUESTED (0x08), IS_FRAGMENT (0x01)

**Q3: How do convergence layers adapt to different link types?** (2 min)
- LTP (RFC 5326): deep space — red/green segments, checkpoint-based retransmission
- TCPCL (RFC 7242): Earth segment — reliable, TCP-based
- UDP-CL: inter-satellite laser links — high speed, loss modeling
- Bundle layer sits ABOVE transport — swap convergence layers per hop

### LO2: RL-Based Routing

**Q4: Explain your RL agent's state, action, and reward design.** (2.5 min)
- State: 8 variables (link quality, buffer occupancy, bundle priority, time-to-deadline, neighbor count, contact schedule, energy level, congestion)
- Actions: forward, store, drop, split
- Reward: R = α·delivery(1.0) − β·delay − γ·hops − δ·drops(10.0) − ε·energy
- Epsilon-greedy, decay 0.995, CGR fallback at confidence < 0.3

**Q5: How does multi-agent federated learning work?** (2 min)
- Each node runs its own Q-learning agent
- Periodically aggregate Q-tables (weighted average)
- Preserves privacy — no raw data shared, only learned policy parameters
- Faster convergence than single-agent on large networks

### LO3: Quantum Communication

**Q6: Walk through BB84.** (2.5 min)
- 8 steps: random bits → random bases → send qubits → Bob measures → compare bases → sift → QBER → security decision
- QBER < 11% (Shor-Preskill) → secure
- Eavesdropper introduces ~25% QBER → detected

**Q7: Why both QKD AND post-quantum crypto?** (2 min)
- Defense-in-depth
- QKD: information-theoretic security, but needs hardware, low key rate (1-10 bps Mars)
- ML-KEM (FIPS 203): fallback key exchange over any channel
- ML-DSA (FIPS 204): authentication — QKD can't authenticate
- 3,309-byte signatures: 0.3% overhead on 1MB bundle, 33× on 100-byte command

### LO4: Space Infrastructure

**Q8: Explain your 5-tier topology.** (2.5 min)
- Tier 1: Earth Ground (DSN: Goldstone, Madrid, Canberra — 120° apart)
- Tier 2: Earth Orbital (3 GEO + 48 LEO laser constellation, Walker Delta)
- Tier 3: Deep Space (ES-L4, ES-L5 Lagrange relays + quantum repeaters)
- Tier 4: Mars Orbital (areostationary at 17,032 km)
- Tier 5: Mars Surface (167 nodes: bases, rovers, drones, sensors)
- Total: 241 nodes

**Q9: Derive the link budget for Earth-Mars optical.** (3 min)
- FSPL = 20·log₁₀(4πd/λ)
- At 225M km, 1550nm: FSPL ≈ 365 dB
- TX: 5W, 22cm aperture → EIRP calculation
- RX: 1m telescope → received power ≈ -234 dBm
- Result: 10-200 Mbps depending on distance

**Q10: How do Lagrange relays maintain connectivity during conjunction?** (2 min)
- Solar conjunction: Sun blocks direct Earth-Mars line-of-sight for ~2 weeks
- ES-L4 and ES-L5 are 60° ahead/behind Earth — they can "see around" the Sun
- RF fallback via Lagrange relays: 50-70% conjunction availability
- Optical blackout during peak conjunction — Ka-band RF maintains minimum data flow

### LO5: Radiation & Data Priority

**Q11: What radiation effects threaten spacecraft electronics?** (2 min)
- SEU: Single Event Upset (bit flip)
- SEL: Single Event Latch-up (destructive current)
- MBU: Multiple Bit Upset
- TID: Total Ionizing Dose (cumulative degradation)
- Mars: no global magnetic field → higher radiation than Earth orbit

**Q12: How does your 4-tier priority system work?** (2 min)
- P0 Emergency: anomaly alerts, < 1 min
- P1 Mission-critical: science events, < 30 min
- P2 High-priority: daily science, < 24 hr
- P3 Standard: housekeeping, < 7 days
- P4 Bulk: archives, < 30 days
- Emergency preemption: P0 jumps queue regardless of buffer state
- CCSDS 121/122 compression reduces payload size before queuing

### LO6: Standards & Design Rationale

**Q13: Which standards does AETHERIX comply with?** (2 min)
- RFCs: 9171 (BPv7), 5326 (LTP), 7242 (TCPCL), 4838 (DTN Architecture)
- CCSDS: 734.2-B-1 (DTN), 735.1-B-1 (Security), 141.0-B-1 (Optical), 401.0-B-30 (RF), 121/122 (Compression)
- NIST: FIPS 203 (ML-KEM), 204 (ML-DSA), 205 (SLH-DSA)

**Q14: What was your most challenging design decision?** (2 min)
- RL routing vs pure CGR
- Decision: hybrid approach — RL primary, CGR fallback at confidence < 0.3
- Rationale: RL discovers novel routes CGR can't, but CGR provides guaranteed baseline
- Trade-off: RL requires training time and doesn't guarantee optimality

**Q15: If you could add one feature, what would it be?** (2 min)
- Software-defined radio (SDR) for dynamic spectrum allocation
- Or: machine learning for solar flare prediction to pre-emptively route around conjunctions
- Or: blockchain for tamper-evident command logging
- Pick ONE and defend it. Don't list three half-baked ideas.

---

## 📐 Interview Time Budget

| Phase | Questions | Time |
|-------|----------|------|
| DTN (LO1) | Q1-Q3 | 6 min |
| RL (LO2) | Q4-Q5 | 4.5 min |
| Quantum (LO3) | Q6-Q7 | 4.5 min |
| Infrastructure (LO4) | Q8-Q10 | 7.5 min |
| Radiation/Priority (LO5) | Q11-Q12 | 4 min |
| Standards/Rationale (LO6) | Q13-Q15 | 6 min |
| **Total** | **15 Qs** | **~32.5 min** |

---

## 💡 Critical Interview Skills

### 1. Admit Uncertainty Gracefully

If you don't know something:
> "That's a great question. I focused primarily on [X] in this project. For [Y], I'd need to research further, but my initial thinking would be [reasonable speculation]."

**Never:** "I don't know." (Dead end)
**Never:** Make up an answer. (They'll catch it)
**Always:** Pivot to what you DO know.

### 2. The "Yes, and..." Technique

When the examiner adds complexity:
> **Examiner:** "What if two Lagrange relays fail simultaneously?"
> **You:** "That's an important edge case. With both ES-L4 and ES-L5 down, the primary conjunction path is severed. The system would fall back to..." [describe Mars-relay → direct-to-DSN when line-of-sight permits, accepting reduced availability during conjunction]

Acknowledge the scenario is valid, then reason through it.

### 3. Quantify Everything

Vague answers lose points. Specific numbers win:
- ❌ "High data rate" → ✅ "100 Mbps at closest approach"
- ❌ "Long delay" → ✅ "3-22 minutes one-way"
- ❌ "Many nodes" → ✅ "241 nodes across 5 tiers"
- ❌ "Good security" → ✅ "QBER < 11%, Shor-Preskill threshold"

### 4. Don't Over-Answer

2 minutes per question. If you finish in 90 seconds and covered the key points, STOP. Don't pad. Examiners appreciate conciseness — it shows mastery.

### 5. The Follow-Up Trap

Examiners often probe deeper after a good answer. This is a GOOD sign — they're engaged. But be careful:
- If they push into areas beyond your project scope, say so: "That's beyond what AETHERIX simulates, but the theoretical framework would be..."
- If they push on a weakness, acknowledge it honestly: "You're right, that's a limitation. The mitigation I implemented was..."

---

## 🔗 References

- [Mock Interview Script](https://github.com/matx104/AETHERIX/blob/main/interview_prep/practice/mock_interview.md)
- [Question Bank](https://github.com/matx104/AETHERIX/tree/main/interview_prep/question_bank) — 106 practice questions
- [Topic Summaries](https://github.com/matx104/AETHERIX/tree/main/interview_prep/topic_summaries) — 11 topic deep-dives
- [Cheat Sheets](https://github.com/matx104/AETHERIX/tree/main/interview_prep/cheat_sheets) — formulas + constants

---

## ✅ Practice Checklist for Today

1. [ ] Read the full mock interview script (`interview_prep/practice/mock_interview.md`)
2. [ ] Practice answering Q1, Q4, Q6, Q8, Q9 OUT LOUD with a timer
3. [ ] For each answer: check STAR-T structure — did you lead with the direct answer?
4. [ ] Practice the "I don't know" pivot 3 times until it feels natural
5. [ ] Memorize the numbers: 365 dB, 11%, 241, 3,309, 0.995, 0.3
6. [ ] Have someone ask you random questions from the question bank
7. [ ] Time yourself on Q9 (link budget derivation) — must be ≤ 3 min
8. [ ] Practice defending Q14 (design decision) — pick your strongest decision

---

## 📂 Deep Dive Resources

- **Mock interview:** `interview_prep/practice/mock_interview.md`
- **Question bank:** `interview_prep/question_bank/` — 106 entries
- **Topic summaries:** `interview_prep/topic_summaries/` — 11 summaries
- **Cheat sheets:** `interview_prep/cheat_sheets/formulas.md` and `constants.md`
- **Design rationale:** `docs/DESIGN_RATIONALE.md`

---

## 🏆 Tomorrow: Day 42 — Exam Day Strategy

The final lesson. Everything comes together. Rest, preparation, mindset, and the ultimate cheat sheet.
