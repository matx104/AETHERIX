# Reinforcement Learning for DTN Routing

## Topic Summary

### What Problem Does RL Solve?

Traditional DTN routing uses Contact Graph Routing (CGR), which computes
shortest-delay paths through a scheduled contact plan. CGR assumes the
contact plan is known in advance and deterministic. In reality:

- **Contact windows shift** due to orbital perturbations and clock drift.
- **Link quality varies** with weather (at DSN sites), solar plasma, and
  pointing accuracy.
- **Buffer pressure** from bursty science data can cause congestion.
- **Node failures** (radiation upsets, power loss) break planned contacts.

Reinforcement learning replaces the static CGR lookup with an adaptive
policy that learns from experience: the agent observes the network state,
selects an action (forward / store / drop / split), receives a reward,
and updates its policy to maximise long-term delivery.

---

### State Representation

The AETHERIX RL agent observes `NetworkState` — a 10-field vector:

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `current_node` | str | node ID | Where the bundle currently resides |
| `neighbors` | list[str] | node IDs | Directly reachable next hops |
| `link_qualities` | dict[str, float] | 0.0–1.0 | Normalised link quality per neighbor |
| `buffer_occupancy` | float | 0.0–1.0 | Fraction of local buffer in use |
| `bundle_priority` | int | 0–4 | EMERGENCY(0) → BULK(4) |
| `bundle_size_mb` | float | MB | Payload size |
| `bundle_deadline_hours` | float | hours | Time-to-live before expiry |
| `destination_node` | str | node ID | Final destination |
| `current_tier` | int | 1–5 | Which network tier we're in |
| `neighbor_tiers` | dict[str, int] | 1–5 | Tier of each neighbor |

The agent discretises continuous fields (link quality, buffer, deadline)
into buckets to form a Q-table key. This keeps the state space tractable
(~500 unique states in a 15-node training topology).

---

### Action Space

| Action | When Chosen | Effect |
|--------|-------------|--------|
| **FORWARD** | A neighbor has acceptable link quality | Bundle moves to next hop |
| **STORE** | No neighbor is good enough, buffer has room | Bundle waits for next contact |
| **DROP** | Buffer overflow (>80%) and bundle is low priority | Bundle discarded (custody released) |
| **SPLIT** | Large bundle, multiple marginal links | Bundle fragmented across paths |

The `_find_best_forward` method adds a **tier bonus**: neighbors in a
lower tier (closer to Earth) receive a quality boost, biasing the agent
toward Earth-ward progress even when raw link quality is comparable.

---

### Reward Function

```
R = α(delivery_success) - β(delay_seconds) - γ(hop_count)
    - δ(bundle_dropped) - ε(energy_watt_hours)
```

| Weight | Symbol | Value | Rationale |
|--------|--------|-------|-----------|
| Delivery | α | 1.0 | Primary objective — the bundle must arrive |
| Delay | β | 0.001/s | Penalises latency but weakly (DTN is delay-tolerant by design) |
| Hops | γ | 0.1 | Each hop adds risk and energy; prefer direct paths |
| Drop | δ | 10.0 | Dropping is catastrophic — 10× the delivery reward |
| Energy | ε | 0.01/Wh | Minor concern for solar-powered relays; major for battery rovers |

The reward is **shaped** (not sparse): intermediate forwarding through a
good-quality link earns +0.3 to +1.0, not just the terminal delivery bonus.
This accelerates learning in the Q-table regime where episodes are short.

---

### Learning Algorithm: Tabular Q-Learning

The agent uses **tabular Q-learning** with epsilon-greedy exploration:

1. **State key**: Discretise all continuous fields → hashable tuple.
2. **Action selection**: With probability ε, explore randomly; otherwise
   exploit the best Q-value for the current state.
3. **Q-update**: `Q(s,a) ← Q(s,a) + lr[r + γ·max Q(s',a') - Q(s,a)]`
4. **Experience replay**: Transitions are stored in a circular buffer
   and replayed in mini-batches to decorrelate updates.

**Why not Deep Q-Network (DQN)?** See `DESIGN_RATIONALE.md` §8 — the
15-node training topology has ~500 discretised states, well within
tabular capacity. DQN adds training instability, hyperparameter
sensitivity, and GPU dependency without benefit at this scale. The
upgrade path to DQN is documented for the Phase 6 scale-out to 241 nodes.

---

### Epsilon Schedule

| Parameter | Value | Justification |
|-----------|-------|---------------|
| `epsilon_start` | 1.0 | Full exploration at the start — no prior knowledge |
| `epsilon_min` | 0.01 | Never fully stop exploring — the environment is non-stationary |
| `epsilon_decay` | 0.995 | Reaches ε=0.01 after ~920 episodes; balances speed vs. stability |

The schedule is geometric (multiplicative), not linear. This ensures
many exploration steps early (when the Q-table is sparse) and gradual
exploitation as values converge.

---

### Convergence Detection

Training stops early when the rolling-100-episode reward standard
deviation drops below 0.1. This indicates the policy has stabilised —
further episodes only refine Q-values marginally. In practice, the
15-node training environment converges around episode 800–1200.

---

### Multi-Agent Federated Learning

The `multi_agent.py` module supports federated Q-table aggregation:

1. Each node trains a local agent on its own traffic observations.
2. Periodically, Q-tables are aggregated (averaged) and redistributed.
3. This prevents any single node from overfitting to local traffic
   patterns and speeds up global convergence.

Federated averaging is performed in the control loop of the Mars Orbital
relay tier (tier 4), which has the most diverse traffic view.

---

### Production Upgrade Path

| Current (Demo) | Phase 6 (Production) |
|-----------------|---------------------|
| Tabular Q-learning | Deep Q-Network (DQN) with experience replay |
| 15-node training topology | Full 241-node topology |
| Shaped reward (intermediate) | Sparse reward (delivery only) + curriculum |
| Geometric epsilon decay | Cosine annealing + warm restarts |
| Single-agent training | Multi-agent PPO with parameter sharing |
| ~500 discretised states | ~10⁶ continuous states via function approximation |

See `interview_prep/question_bank/rl_hyperparameters.md` for per-knob
defense of each hyperparameter choice.
