# Day 39: Presentation Mastery — Part 1 (Network & Quantum)

## 📅 August 30, 2026

## 🎯 Learning Objective
Master the first half of the AETHERIX oral presentation — Network Architecture (4-5 min) and Quantum Communication (3-4 min). Practice timing, transitions, and delivery. Maps to exam weight **Presentation 30%**.

---

## 📖 The Presentation Game Plan

Your exam is **15-20 minutes presentation + 30-40 minutes technical interview**. The presentation is 30% of your grade. That's the difference between a merit and a distinction.

### Total Presentation Structure (~18 minutes)

| Section | Slides | Time | This Lesson? |
|---------|--------|------|-------------|
| Title + Agenda | 1-2 | 50s | ✓ |
| The Challenge | 3-4 | 3 min | ✓ |
| DTN + Bundle Protocol | 5-9 | 4 min | ✓ |
| Network Topology | 10-12 | 3 min | ✓ |
| Optical/Link Budget | 13 | 2 min | ✗ (Day 40) |
| Earth-Mars Journey | 14 | 1.5 min | ✗ |
| RL Routing | 15-16 | 2 min | ✗ |
| Quantum Security | 17-19 | 3 min | ✓ |
| Radiation + Data Priority | 20-24 | 3 min | ✗ (Day 40) |
| Demo + Performance | 25-27 | 2 min | ✗ (Day 40) |
| Conclusion | 28-29 | 1 min | ✗ (Day 40) |

**Today: Practice Sections 1-4 + 8.** These are your strongest areas after 38 days of study.

---

## 📖 Section-by-Section Delivery Guide

### Opening (Slides 1-2) — 50 seconds

**Script:**
> "Good morning. I'm Muhammad Abdullah Tariq, presenting AETHERIX — an architecture for interplanetary communication supporting Mars missions."

**Delivery tips:**
- Stand centered, hands visible, brief pause after the acronym
- Make eye contact with EACH examiner — scan the room
- DON'T rush the opening. First impressions set the tone
- Memorize the acronym expansion cold: **A**utonomous **E**xtraterrestrial **H**igh-throughput **E**nhancing **R**outing and **I**nter-**p**lanetary e**X**change

### The Challenge (Slides 3-4) — 3 minutes

**Key talking points:**
- Distance: 54.6M - 401M km (variable)
- Delay: 3-22 minutes one-way light time
- Current capability: 0.5-6 Mbps (RF only)
- Solar conjunction: 2-week blackout
- Why TCP/IP fails: low-latency assumption, continuous connectivity, end-to-end ACKs

**The killer line:**
> "A TCP three-way handshake to Mars takes 37.5 minutes — just to establish the connection. Before any data is sent."

**Transition to solution:**
> "We need a fundamentally different approach."

### DTN + Bundle Protocol (Slides 5-9) — 4 minutes

**Flow:**
1. Bundle Protocol v7 (RFC 9171) — store-and-forward
2. Three convergence layers: LTP (deep space), TCPCL (Earth), UDP-CL (ISL)
3. Store-and-forward walkthrough: bundle arrives → stored → waits for contact → forwards
4. Custody transfer localizes retransmission to the failed hop

**Standards to name-drop (know these cold):**
- BPv7: RFC 9171 (2022)
- LTP: RFC 5326 (2008)
- DTN Architecture: CCSDS 734.2-B-1

### Network Topology (Slides 10-12) — 3 minutes

**The five tiers:**
1. **Tier 1 — Earth Ground:** DSN (Goldstone, Madrid, Canberra) — 120° apart for 24/7 coverage
2. **Tier 2 — Earth Orbital:** 3 GEO relays + 48-satellite LEO laser constellation (Walker Delta, 6 planes)
3. **Tier 3 — Deep Space:** ES-L4 and ES-L5 Lagrange relays + quantum repeaters
4. **Tier 4 — Mars Orbital:** Areostationary relays at 17,032 km altitude
5. **Tier 5 — Mars Surface:** Bases, rovers, drones, sensors — 167 nodes

**Total: 241 nodes across 5 tiers.**

**Key data rates:**
- Earth → Deep Space: 100 Mbps (1550nm laser)
- Deep Space → Mars: 2-200 Mbps (distance dependent)
- Mars orbital → surface: 2 Mbps (UHF/S-band)
- LEO ISL mesh: 10 Gbps (laser)

### Quantum Security (Slides 17-19) — 3 minutes

**Flow:**
1. The quantum threat: Shor's algorithm breaks RSA/ECC
2. BB84 protocol: two bases, sifting, QBER < 11%
3. E91 + entanglement for deep-space
4. Defense-in-depth: QKD + ML-KEM (FIPS 203) + ML-DSA (FIPS 204)

**Demo moment:**
> "Let me show the QKD simulation." [Open matx104.github.io/AETHERIX → QKD tab]

**If demo fails (backup):**
> "In our simulation, 2048 qubits are exchanged. A clean channel produces QBER = 0%. With an eavesdropper present, QBER jumps to 25% — well above the 11% Shor-Preskill threshold. The key is discarded."

---

## 🔬 Presentation Files to Rehearse From

- **Full script:** `docs/downloads/AETHERIX_Presentation_Script.md` — every slide with exact words
- **Slide deck:** `presentation/AETHERIX_Presentation.md` — 29 slides
- **Demo site:** [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/)

---

## 📐 Timing Targets for Today's Sections

| Section | Target Time | Max |
|---------|------------|-----|
| Opening | 50s | 1 min |
| Challenge | 3 min | 3.5 min |
| DTN/BP | 4 min | 4.5 min |
| Topology | 3 min | 3.5 min |
| Quantum | 3 min | 3.5 min |
| **Total** | **~14 min** | **16 min** |

---

## 🔗 Standards & References

- [Presentation Script](https://github.com/matx104/AETHERIX/blob/main/docs/downloads/AETHERIX_Presentation_Script.md)
- [Slide Deck](https://github.com/matx104/AETHERIX/blob/main/presentation/AETHERIX_Presentation.md)
- [Live Demo Site](https://matx104.github.io/AETHERIX/)
- [RFC 9171 — Bundle Protocol](https://www.rfc-editor.org/rfc/rfc9171)
- [CCSDS 734.2-B-1 — DTN Architecture](https://public.ccsds.org/Pubs/734x2b1.pdf)

---

## 💡 How the Examiner Will Evaluate This

**They're watching for:**
- **Clarity:** Can you explain complex topics simply? Don't drown them in jargon.
- **Pacing:** Are you rushing or dragging? Aim for ~150 words/minute.
- **Transitions:** Do sections flow naturally? "Now that we've solved the networking challenge, let's address security..."
- **Eye contact:** Don't read from slides. Glance at notes, talk to the examiners.
- **Confidence:** If you stumble, pause, breathe, continue. Don't apologize.

**Common mistakes to avoid:**
- Reading slides verbatim (examiners can read)
- Diving too deep on one topic and running out of time
- Forgetting to mention the live demo early (hook their interest)
- Speaking too fast when nervous

---

## ✅ Practice Checklist for Today

1. [ ] Read the full presentation script once, out loud, timed
2. [ ] Practice the opening 3 slides until you don't need notes
3. [ ] Time yourself on the DTN section — must be ≤ 4 minutes
4. [ ] Time yourself on the Topology section — must be ≤ 3 minutes
5. [ ] Practice the QKD demo transition smoothly
6. [ ] Record yourself (phone audio) and listen for pacing/filler words
7. [ ] Memorize: RFC 9171, RFC 5326, CCSDS 734.2-B-1, QBER 11%

---

## 📂 Deep Dive Resources

- **Full script:** `docs/downloads/AETHERIX_Presentation_Script.md`
- **Slides:** `presentation/AETHERIX_Presentation.md`
- **Demo site:** [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/)
- **Exam readiness design:** `docs/superpowers/specs/2026-06-05-aetherix-exam-readiness-design.md`
- **Mock interview (for context):** `interview_prep/practice/mock_interview.md`
