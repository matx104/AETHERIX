# Day 6: The Q-Learning Routing Agent — Actions, States & Epsilon-Greedy

## 📅 July 28, 2026

## 🎯 Learning Objective
Understand the internal mechanics of AETHERIX's RL routing agent: the state representation (`NetworkState`), the four-action space, the epsilon-greedy exploration policy, and how the agent makes routing decisions in real time. This maps to **LO1** and is a likely deep-dive topic: the examiner will want you to explain the agent *from first principles*.

## 📖 The Core Concept

### What Is Q-Learning?

Q-learning is a model-free reinforcement learning algorithm. The agent does not need a model of the environment — it learns entirely from experience. The core idea is a **Q-table**: a lookup table where each entry `Q(s, a)` estimates the *expected long-term reward* of taking action `a` in state `s`. Over many episodes of interaction, these estimates converge toward the optimal policy.

The update rule is the heart of Q-learning:

```
Q(s, a) ← Q(s, a) + α × [r + γ × max_a' Q(s', a') − Q(s, a)]
```

Where:
- `s` = current state, `a` = action taken
- `r` = reward received
- `s'` = next state after the action
- `α` = learning rate (how quickly new information overrides old)
- `γ` = discount factor (how much future rewards matter relative to immediate ones)
- `max_a' Q(s', a')` = the best estimated value achievable from the next state

The term `[r + γ × max_a' Q(s', a') − Q(s, a)]` is the **temporal difference (TD) error** — the gap between what the agent expected and what it actually experienced. The learning rate α controls how aggressively the agent corrects this gap.

### The State Space: NetworkState

The agent's world model is the `NetworkState` — a structured snapshot of the routing decision context. It captures everything the agent needs to decide what to do with a bundle right now:

| Field | Type | Purpose |
|-------|------|---------|
| `current_node` | str | Where the bundle currently sits |
| `neighbors` | list[str] | Directly reachable next hops |
| `link_qualities` | dict[str, float] | Normalised quality (0.0–1.0) per neighbour |
| `buffer_occupancy` | float | Fraction of local buffer in use (0.0–1.0) |
| `bundle_priority` | int | 0–4 (EMERGENCY → BULK) |
| `bundle_size_mb` | float | Payload size in megabytes |
| `bundle_deadline_hours` | float | Time-to-live before expiry |
| `destination_node` | str | Final destination |
| `current_tier` | int | Network tier 1–5 |
| `neighbor_tiers` | dict[str, int] | Tier of each neighbour |

The agent **discretises** continuous fields to form a compact Q-table key. Buffer occupancy splits into `high` (>0.7) / `low`. Link quality splits into `good` (>0.5) / `poor` / `none`. Priority splits into `urgent` (P0/P1) / `normal`. This discretisation keeps the state space tractable (~500 unique states in the 15-node training topology) and makes the Q-table *interpretable* — essential for defending decisions in a viva.

### The Action Space: Four Choices

| Action | When Chosen | Effect |
|--------|-------------|--------|
| **FORWARD** | A neighbour has acceptable link quality (≥ 0.3) | Bundle moves to next hop |
| **STORE** | No neighbour is good enough, or buffer has room to wait | Bundle waits for next contact |
| **DROP** | Buffer overflow (>80%) and bundle is low priority (P3/P4) | Bundle discarded, custody released |
| **SPLIT** | Large bundle, multiple marginal paths available | Bundle fragmented for multipath routing |

The `SPLIT` action is for multipath routing — when a large bundle (e.g., 500 MB image mosaic) cannot be delivered over a single contact window, the agent fragments it across multiple next hops. This increases aggregate throughput and resilience. Per RFC 9171, the `IS_FRAGMENT` flag (0x01) is set, and reassembly occurs at the destination.

### Epsilon-Greedy Exploration

The agent faces the **exploration-exploitation dilemma**: should it try the action it believes is best (exploit), or try a random action to discover potentially better strategies (explore)?

AETHERIX uses **epsilon-greedy**: with probability ε, explore randomly; with probability 1−ε, exploit the best-known Q-value. The exploration rate ε starts at **1.0** (full exploration — no prior knowledge) and decays geometrically by a factor of **0.995** per episode, reaching **0.01** after approximately 920 episodes. The agent never fully stops exploring (ε floors at 0.01) because the environment is **non-stationary** — link conditions change with orbital phase, solar activity, and equipment status.

### The Tier-Aware Routing Bonus

A critical implementation detail: the `_find_best_forward` method adds a **tier bonus** to neighbours in a lower tier (closer to Earth). This biases the agent toward **Earth-ward directional progress** even when raw link quality is comparable between neighbours. Without this bonus, the agent might bounce a bundle sideways within a tier rather than making progress toward the destination — a problem in multi-relay topologies.

## 🔬 In AETHERIX

The agent is implemented in `src/routing/rl_agent.py` as `RLRoutingAgent`.

**`RoutingAction`** enum: `FORWARD = "forward"`, `STORE = "store"`, `DROP = "drop"`, `SPLIT = "split"`.

**`NetworkState`** dataclass with all 10 fields (the tier fields `current_tier` and `neighbor_tiers` default to 0/empty for backward compatibility with callers that don't supply tier context).

**`RoutingDecision`** dataclass: `action`, `next_hop` (Optional), `confidence` (float), `reasoning` (str).

**Key methods:**
- `get_state_key(state)` — discretises: `buffer_level` (high/low at 0.7), `link_level` (good/poor/none at 0.5), `priority_level` (urgent if ≤1, else normal). Returns `f"{node}|{buffer}|{link}|{priority}"`.
- `select_action(state)` — main entry point. Handles edge cases (no neighbours → STORE; destination is neighbour and quality ≥ 0.3 → FORWARD with 0.95 confidence). Then epsilon-greedy: `_explore()` if `random.random() < epsilon`, else `_exploit()`.
- `_explore(state)` — random choice among FORWARD/STORE (and DROP if buffer > 0.8). Confidence 0.3.
- `_exploit(state)` — if priority ≤ URGENT (P0/P1), calls `_find_fastest_forward()` (highest link quality). Otherwise checks buffer pressure, then `_find_best_forward()` (scored by quality × 0.7 + tier bonus).
- `_find_best_forward(state)` — scores each neighbour: `quality × 0.7` base score. If `neighbor_tiers` is populated and neighbour is in a lower tier, adds `0.5 + 0.1 × tier_difference`. This ensures tier-ward motion.
- `calculate_reward(...)` — computes `R = α·delivery − β·delay − γ·hops − δ·drops − ε·energy`.
- `update(state, action, reward, next_state)` — tabular Q-learning update with `learning_rate=0.001`, `discount_factor=0.99`.

## 📐 Key Numbers & Formulas
- **Actions:** FORWARD, STORE, DROP, SPLIT (4 actions)
- **MIN_LINK_QUALITY:** **0.3** (below this, agent refuses to forward)
- **HIGH_BUFFER_THRESHOLD:** **0.8** (above this, DROP becomes a candidate action)
- **URGENT_PRIORITY:** **1** (P0 and P1 are "urgent")
- **Epsilon start:** 1.0 (full exploration)
- **Epsilon minimum:** 0.01 (never fully stop exploring)
- **Learning rate (α):** 0.001
- **Discount factor (γ):** 0.99
- **State key discretisation thresholds:** buffer 0.7, link 0.5
- **Tier bonus:** `0.5 + 0.1 × (current_tier − neighbor_tier)` for downward-tier neighbours
- **Q-learning update:** `Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') − Q(s,a)]`

## 🔗 Standards & References
- [Sutton & Barto — Reinforcement Learning: An Introduction (Ch. 6: Q-Learning)](http://incompleteideas.net/book/RLbook2020.pdf)
- [Watkins (1989) — Q-Learning original paper](https://link.springer.com/article/10.1007/BF00992698)
- [RFC 9171 — Bundle Protocol v7 (fragmentation for SPLIT action)](https://datatracker.ietf.org/doc/html/rfc9171)
- `interview_prep/question_bank/rl_hyperparameters.md` — per-knob justification of every threshold

## 💡 How the Examiner Will Probe This

**Q: "Your RL agent has four actions: forward, store, drop, split. When would 'split' be the right choice?"**
→ Split is for multipath routing. When a large bundle (e.g., 500 MB image mosaic) cannot be delivered over a single contact window, the agent fragments it across multiple next hops or contact windows. This increases aggregate throughput and resilience — if one path degrades, other fragments still arrive. Per RFC 9171, IS_FRAGMENT (0x01) is set, reassembly at destination. Trade-off: fragment overhead increases header bytes, so split is only worthwhile for large bundles or when no single path has sufficient contact time.

**Q: "Walk me through what happens inside select_action() when a P0 emergency bundle arrives at a relay with three neighbours."**
→ First edge case checks: if destination is a direct neighbour with quality ≥ 0.3, forward directly at 0.95 confidence. Otherwise, epsilon-greedy: with probability ε explore randomly, else exploit. Since priority ≤ 1 (URGENT), `_find_fastest_forward()` is called — it sorts neighbours by link quality and forwards to the highest-quality one above 0.3 threshold. Confidence 0.8. If no links above threshold, stores at 0.6 confidence.

## ✅ What You Should Be Able to Answer After This Lesson
1. What are the 10 fields of NetworkState, and which are discretised for the Q-table key?
2. What is the Q-learning update rule, and what does the TD error term represent?
3. How does epsilon-greedy work, and why does ε floor at 0.01 instead of reaching zero?
4. What is the tier bonus in `_find_best_forward`, and why is it necessary?
5. When would the agent choose STORE over FORWARD?

## 📂 Deep Dive Resources
- `src/routing/rl_agent.py` — `RLRoutingAgent`, `NetworkState`, `RoutingAction`, `RoutingDecision`
- `src/routing/training.py` — `Trainer`, `TrainingEnvironment` (15-node topology)
- `interview_prep/topic_summaries/reinforcement_learning.md` — state/action/reward summary
- `interview_prep/question_bank/rl_hyperparameters.md` — MIN_LINK_QUALITY justification
- `docs/DESIGN_RATIONALE.md` §4.2 — derivation of the 0.3 threshold
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
