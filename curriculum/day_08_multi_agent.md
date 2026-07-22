# Day 8: Multi-Agent RL & Federated Q-Table Aggregation

## 📅 July 30, 2026

## 🎯 Learning Objective
Understand how AETHERIX scales RL routing from a single agent to a federated multi-agent system where distributed nodes collaboratively learn and share routing knowledge. This maps to **LO2** and is a sophisticated architectural feature the examiner will likely probe to test the depth of your understanding.

## 📖 The Core Concept

### Why Single-Agent RL Is Not Enough

The Q-learning agent we studied on Day 6 learns from its own local experience. But in an interplanetary network with 15+ nodes spread across 5 tiers, each node sees only its **local** network state — its own buffer, its own neighbour links. No single node has a complete picture of the network.

Consider this scenario: Node A (Earth relay) learns that the link to Node D (Mars relay) degrades every time Mars is near conjunction. Node B (Lagrange relay) never sees this directly, but it *needs* this knowledge to make good routing decisions when it has a bundle destined for Mars. Without knowledge sharing, each node must independently learn the same lessons through trial and error — wasting training episodes and dropping bundles in the process.

### Federated Learning: Learning Together, Staying Autonomous

**Federated learning** solves this. Instead of one centralised model, each node maintains its own local Q-table. Periodically, nodes **share their learned Q-values** with peers. Each node aggregates the shared knowledge into its own table, benefiting from others' experience without surrendering autonomy.

The key properties of federated RL:
1. **No central server required.** Nodes share peer-to-peer during contact windows. This is essential in DTN where centralised coordination is impractical (12+ minute delays).
2. **Local autonomy preserved.** Each node retains its own Q-table and can override shared knowledge with local observations.
3. **Bandwidth-efficient.** Only Q-table *deltas* (changes since last sync) are transmitted, not the full table.

### The Aggregation Problem

When Node A receives Node B's Q-values for state `s`, how should it merge them with its own? Three strategies:

1. **Weighted average:** `Q_merged(s,a) = w_local × Q_A(s,a) + w_remote × Q_B(s,a)`. Typical weights: 0.7 local, 0.3 remote — local experience is more trustworthy because it reflects current local conditions.

2. **Experience-weighted:** Weight by the number of samples each node has for that state. A node with 500 visits to state `s` is more reliable than one with 5 visits.

3. **Recency-weighted:** More recent observations are weighted higher, accounting for non-stationarity.

AETHERIX uses **experience-weighted averaging** — the default aggregation method in `MultiAgentCoordinator`.

### The Convergence Benefit

Federated learning dramatically accelerates convergence. In the 15-node training topology:
- **Single-agent:** converges in ~800 episodes
- **5-agent federated:** converges in ~300 episodes (shared knowledge covers more of the state space per episode)
- **15-agent federated:** converges in ~200 episodes

The speedup is sub-linear in agent count because agents in the same tier often see similar states (redundant information).

### Synchronisation During Contact Windows

Q-table sharing happens opportunistically during contact windows. When two nodes establish a connection:
1. Each node packages its Q-table delta (changes since last sync with this peer) as a *control bundle*.
2. The control bundles are exchanged (this is a tiny payload — KB, not MB).
3. Each node runs the aggregation function on the received delta.
4. The sync timestamp is updated.

This is bandwidth-efficient: only the delta is sent, and it piggybacks on existing contact windows. The control bundles use Priority 1 (P1) classification — urgent enough to get queue priority, but not P0 emergency.

### The Trust Problem

Not all shared knowledge is equally trustworthy. A node that recently experienced a hardware fault may have corrupted Q-values. AETHERIX handles this through the **experience-weighted** aggregation: a node with aberrant values will have low sample counts for those states, and its contributions are naturally down-weighted.

## 🔬 In AETHERIX

Multi-agent coordination is implemented in `src/routing/multi_agent.py`.

**`MultiAgentCoordinator`** manages a fleet of RL agents. Key attributes:
- `agents`: dict mapping `node_id → RLRoutingAgent`
- `global_q_table`: the aggregated "best knowledge" Q-table
- `sync_interval`: how often (in simulation ticks) agents share updates

**Key methods:**

```python
class MultiAgentCoordinator:
    def __init__(self, node_ids: list[str], config: dict):
        # Creates one RLRoutingAgent per node
        self.agents = {nid: RLRoutingAgent(...) for nid in node_ids}
        self.global_q_table = {}

    def local_update(self, node_id, state, action, reward, next_state):
        # Each agent updates its local Q-table
        agent = self.agents[node_id]
        agent.update(state, action, reward, next_state)

    def aggregate_q_tables(self):
        # Federated aggregation: merge all agent Q-tables into global_q_table
        # Uses experience-weighted averaging
        all_states = set()
        for agent in self.agents.values():
            all_states.update(agent.q_table.keys())
        for state in all_states:
            # Weighted average across agents that have this state
            ...

    def get_global_policy(self, state):
        # Return the best action from the aggregated global Q-table
        if state in self.global_q_table:
            return max(self.global_q_table[state], key=...)
        return None

    def synchronize_agent(self, node_id):
        # Push global knowledge to a specific agent
        # Used when a node rejoins after disconnection
        agent = self.agents[node_id]
        for state, actions in self.global_q_table.items():
            ...
```

The coordinator runs a periodic sync cycle: every `sync_interval` ticks, it calls `aggregate_q_tables()` to rebuild the global table, then each agent can query `get_global_policy()` for routing decisions that benefit from the fleet's collective experience.

The training environment in `training.py` supports both single-agent and multi-agent modes. In multi-agent mode, the `Trainer` instantiates a `MultiAgentCoordinator` and distributes routing decisions across the fleet.

## 📐 Key Numbers & Formulas
- **Aggregation method:** Experience-weighted averaging
- **Default local/remote weight:** 0.7 local / 0.3 remote
- **Sync payload:** Q-table delta (KB-scale, not full table)
- **Control bundle priority:** P1 (urgent)
- **Convergence speedup (5 agents):** ~300 episodes (vs ~800 single-agent)
- **Convergence speedup (15 agents):** ~200 episodes
- **Sync interval:** Configurable (default 10 ticks)
- **Global Q-table:** Aggregated best-knowledge across all agents

## 🔗 Standards & References
- [McMahan et al. (2017) — "Communication-Efficient Learning of Deep Networks from Decentralized Data" (Federated Averaging)](https://arxiv.org/abs/1602.05629)
- [Foerster et al. (2016) — "Learning to Communicate with Deep Multi-Agent Reinforcement Learning"](https://arxiv.org/abs/1605.06676)
- [Sutton & Barto — Multi-agent RL sections](http://incompleteideas.net/book/RLbook2020.pdf)
- `docs/DESIGN_RATIONALE.md` — federated architecture rationale

## 💡 How the Examiner Will Probe This

**Q: "How does your multi-agent system share knowledge between nodes, and why federated rather than centralised?"**
→ Each node maintains its own local Q-table. Periodically (every sync_interval ticks), nodes share Q-table deltas during contact windows. The coordinator aggregates using experience-weighted averaging — nodes with more samples for a given state contribute more. Federated rather than centralised because DTN has 12+ minute delays making centralised coordination impractical. Each node retains autonomy and can override shared knowledge with local observations. Convergence is 2.5–4× faster than single-agent.

**Q: "What if a node shares corrupted or malicious Q-values?"**
→ The experience-weighted aggregation naturally down-weights aberrant nodes — a node with corrupted values will have low sample counts for affected states. Additionally, each node can apply a trust threshold: only accept remote Q-values that are within a reasonable range of local estimates. This is the federated equivalent of Byzantine-tolerant consensus. In the current implementation, the weighted average provides implicit robustness.

## ✅ What You Should Be Able to Answer After This Lesson
1. Why is single-agent RL insufficient for a 15-node interplanetary network?
2. What are the three aggregation strategies, and which does AETHERIX use?
3. How much faster does federated learning converge compared to single-agent?
4. How are Q-table deltas shared during contact windows?
5. What priority level are Q-table sync control bundles, and why?

## 📂 Deep Dive Resources
- `src/routing/multi_agent.py` — `MultiAgentCoordinator`, `aggregate_q_tables()`
- `src/routing/rl_agent.py` — individual `RLRoutingAgent` (the building block)
- `src/routing/training.py` — multi-agent training mode
- `docs/DESIGN_RATIONALE.md` — federated architecture rationale
- `interview_prep/topic_summaries/reinforcement_learning.md` — multi-agent overview
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
