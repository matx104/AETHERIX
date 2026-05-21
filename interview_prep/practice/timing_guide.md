# Timing Guide — Interview Answer Pacing

## Why Timing Matters

With 30–40 minutes for ~15–20 questions, you have approximately **2 minutes per question** on average. Some questions need 30 seconds; others deserve 3 minutes. The key is matching answer length to question depth and not running out of time before covering all topics.

---

## Answer Length Categories

### 30-Second Answers (Definitions, Numbers, Quick Facts)

Use for: definition questions, single-number queries, yes/no with brief justification.

**Structure**: Direct answer → one supporting detail → stop.

**Examples**:
- "What does BPv7 stand for?" → "Bundle Protocol Version 7, defined in RFC 9171, published September 2022. It's the IETF standard for delay-tolerant networking."
- "What's the Mars synodic period?" → "779.94 days, approximately 780 days. This is the time between successive Earth-Mars oppositions."
- "What wavelength does AETHERIX use?" → "1550 nanometres, in the C-band. Chosen for telecom heritage, atmospheric transparency, and eye safety."
- "What's the QBER threshold?" → "11%, per the Shor-Preskill proof. Below this, BB84 is provably secure against any attack permitted by quantum mechanics."

**Pacing tip**: 30 seconds ≈ 60–75 words at normal speaking pace. If you've said more than 3 sentences, stop.

---

### 1-Minute Answers (Concept Explanations)

Use for: "explain X", "what is Y", "how does Z work" questions.

**Structure**: Define it (10 sec) → how it works (30 sec) → AETHERIX application (15 sec) → stop (5 sec buffer).

**Template**: "[Term] is [definition]. It works by [mechanism, 2–3 steps]. In AETHERIX, we use this for [specific application, with a number]."

**Example**: "Explain custody transfer."
> "Custody transfer is a DTN reliability mechanism where responsibility for a bundle moves hop-by-hop from sender to receiver. When node B accepts custody from node A, node A can discard its copy. This matters because it localises retransmission — if B fails to deliver to C, only the B-to-C link retransmits, not the entire path. In AETHERIX, we set the custody-requested flag on all P0 through P2 bundles, which travel through our five-tier network from Mars surface to Earth ground."

**Pacing tip**: 1 minute ≈ 120–150 words. Aim for 5–7 sentences.

---

### 2-Minute Answers (Comparisons, Design Decisions, Trade-offs)

Use for: "why did you choose X over Y", "compare A and B", "what are the trade-offs" questions.

**Structure**: Direct answer (15 sec) → explanation of choice (45 sec) → trade-offs (30 sec) → AETHERIX context (20 sec) → bridge to related topic (10 sec).

**Example**: "Why RL instead of CGR?"
> "AETHERIX uses reinforcement learning instead of Contact Graph Routing for three reasons. [15 sec]
>
> First, adaptability. CGR computes paths from a pre-planned contact schedule that's uploaded from Earth — at 12.5 minutes one-way light time, that schedule is always stale. The RL agent makes decisions based on current local observations: link quality, buffer occupancy, bundle priority. It adapts when a solar flare degrades a link or a buffer fills up. [45 sec]
>
> Second, multi-objective optimisation. CGR minimises delay. Our reward function balances five objectives: delivery, delay, hop count, drop rate, and energy. The weights — alpha=1.0, beta=0.001, gamma=0.1, delta=10.0, epsilon=0.01 — encode operational priorities that a single-metric algorithm can't capture. [30 sec]
>
> In AETHERIX's demo, the Q-learning agent trains across the full 780-day synodic period, learning distance-phase-aware policies. The trade-off is that RL needs training time and provides no optimality guarantee — so we fall back to CGR when agent confidence drops below 0.3. [20 sec]
>
> The planned upgrade to Deep Q-Network would address the Q-table's scalability limitations. [10 sec]"

**Pacing tip**: 2 minutes ≈ 240–300 words. Use numbers and specific AETHERIX values to demonstrate preparation.

---

## Bridge Phrases (Buy Thinking Time)

When you need 3–5 seconds to think, use one of these phrases naturally:

| Situation | Bridge Phrase |
|-----------|--------------|
| Need to recall a number | "The key figure here is..." |
| Structuring a complex answer | "There are three aspects to this question..." |
| Connecting to AETHERIX | "In the context of AETHERIX specifically..." |
| Acknowledging a good question | "That touches on an important design consideration..." |
| Moving from theory to application | "The practical implication of this is..." |
| Comparing two options | "The trade-off between these approaches is..." |
| When you're not sure | "I'd approach this by considering..." or "To the best of my understanding..." |
| Redirecting to your strength | "This relates to an area I explored in depth, which is..." |
| Buying time on a hard question | "Let me think about this from first principles..." |
| Closing an answer | "So to summarise: [one sentence]" |

---

## Practice Drills

### Drill 1: Rapid-Fire Definitions (5 minutes)

Set a timer. Answer each in ≤30 seconds:

1. Define DTN.
2. What is BPv7?
3. Name AETHERIX's 5 priority levels.
4. What is QBER?
5. State the Mars synodic period.
6. What is FSPL at average Earth-Mars distance?
7. Name the 3 DSN stations.
8. What is ML-KEM?
9. Define areostationary orbit.
10. What wavelength does AETHERIX use?
11. How many nodes in AETHERIX?
12. What is LTP?
13. Name the 5 network tiers.
14. What is the Shor-Preskill threshold?
15. What is the RL reward function?

**Check**: Did you finish all 15 in 5 minutes? If not, shorten your definitions.

### Drill 2: 1-Minute Concept Explanations (5 minutes)

Set a timer for 1 minute each. Explain:

1. Store-and-forward
2. Custody transfer
3. BB84 protocol
4. Solar conjunction handling
5. Contact windows

**Check**: Did each answer end between 50–70 seconds? Did you include an AETHERIX-specific detail?

### Drill 3: 2-Minute Design Justifications (10 minutes)

Set a timer for 2 minutes each. Answer:

1. Why RL over CGR?
2. Why 1550 nm?
3. Why 5 tiers?
4. Why hybrid optical/RF?
5. Why QKD plus PQC?

**Check**: Did you acknowledge trade-offs in each answer? Did you include specific numbers?

### Drill 4: Full Mock (35 minutes)

Use the mock interview script (`mock_interview.md`). Have someone ask questions at random order. Time each answer. Target: all 15 questions answered in 30 minutes with no answer exceeding 2.5 minutes.

---

## Red Flags (What NOT To Do)

| Red Flag | Why It's Bad | Fix |
|----------|--------------|-----|
| Answering a 30-sec question in 3 minutes | Eats time for other topics | Practice Drill 1 — cut to one sentence |
| Saying "I'm not sure" without attempting an answer | Appears unprepared | Use bridge: "I'd approach this by considering..." |
| Giving a generic answer without AETHERIX specifics | Looks like memorised textbook | Always include at least one project-specific number |
| Ignoring trade-offs | Appears to have surface understanding | End every design answer with "the trade-off is..." |
| Name-dropping standards without explaining them | Suggests memorisation without understanding | If you cite RFC 9171, know what it specifies |
| Rambling without structure | Hard for examiner to follow | Use "three reasons" or "two aspects" structure |
| Not stopping when finished | Adds filler, dilutes strong answer | Silence is better than filler. Stop. Wait for next question. |

---

## Time Budget for 35-Minute Interview

| Phase | Duration | Content |
|-------|----------|---------|
| Opening (Q1–Q3) | 6 min | DTN fundamentals — you know these cold |
| Middle 1 (Q4–Q7) | 8 min | RL routing, QKD, quantum repeaters — complex topics, use 2 min each |
| Middle 2 (Q8–Q11) | 8 min | Architecture, DSN, orbital mechanics — mix of 1.5 and 2 min answers |
| Deep dive (Q12–Q14) | 6 min | Radiation, prioritisation, standards — show depth |
| Closing (Q15) | 3 min | Summary — your strongest 2-minute pitch |
| Buffer | 4 min | Follow-up probes, transitions |
| **Total** | **35 min** | |
