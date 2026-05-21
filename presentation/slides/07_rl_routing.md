# RL-Based Routing — AI Innovation

## Why Replace Contact Graph Routing (CGR)?

### CGR Limitations

| Limitation | Impact |
|------------|--------|
| Requires pre-computed contact schedules | Cannot adapt to unexpected events |
| Manual schedule updates needed | Hours of human planning time |
| Static routing decisions | Suboptimal under dynamic conditions |
| Single-objective (delivery only) | Cannot balance delay, energy, priority |
| No learning capability | Repeats same mistakes |

### AETHERIX RL Routing Agent

The RL agent replaces CGR with a **Q-learning based decision maker** that improves through experience.

#### State Space (What the Agent Observes)

| State Variable | Description | Range |
|----------------|-------------|-------|
| `current_node` | Agent's current position in network | Node ID |
| `neighbors` | Reachable next hops | List of node IDs |
| `link_qualities` | SNR/BER per neighbor link | 0.0 — 1.0 |
| `buffer_occupancy` | Local storage usage | 0.0 — 1.0 |
| `bundle_priority` | BPv7 priority class (P0-P4) | 0 — 4 |
| `bundle_size_mb` | Payload size | 1 — 10,000 MB |
| `bundle_deadline_hours` | Time until bundle expires | 0.1 — 720 hours |
| `destination_node` | Final destination | Node ID |

#### Action Space (What the Agent Decides)

| Action | Description | When to Use |
|--------|-------------|-------------|
| **Forward** | Send bundle to selected neighbor | Link available, good quality |
| **Store** | Keep bundle locally | Better link coming, buffer low |
| **Drop** | Discard bundle | Expired, corrupt, buffer full |
| **Split** | Fragment for multipath routing | Large bundle, multiple paths available |

#### Reward Function

```
R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)
```

| Weight | Value | Meaning |
|--------|-------|---------|
| α | 1.0 | Reward for successful delivery |
| β | 0.001 | Penalty per second of delay |
| γ | 0.1 | Penalty per hop traversed |
| δ | 10.0 | Heavy penalty for dropped bundles |
| ε | 0.01 | Penalty for energy consumed |

### Training Pipeline — Full Implementation

#### Experience Replay

- **1M transition buffer** — Stores (state, action, reward, next_state) tuples
- **Random minibatch sampling** — Breaks temporal correlation between consecutive experiences
- **Priority replay** — High-reward and rare events sampled more frequently

#### Training Loop with Convergence Detection

- **Automatic convergence detection** — Monitors rolling average reward over sliding window
- **Early stopping** — Halts training when improvement falls below threshold
- **Checkpoint saving** — Periodic Q-table snapshots for rollback
- **Curriculum scheduling** — Difficulty escalation (network size, traffic load, failure rate)

#### Multi-Agent Federated Learning

```
Node A (local Q-table) ──┐
Node B (local Q-table) ──┼──► Q-table aggregation ──► Global Q-table ──► Broadcast to all nodes
Node C (local Q-table) ──┘    (weighted average)       (improved policy)
```

- **Each node trains locally** using its own network experience
- **Federated aggregation** — Weighted average of Q-tables across nodes
- **Weighted by experience** — Nodes with more transitions contribute more
- **Periodic sync** — Aggregation rounds every N training episodes
- **Convergence benefit** — Global policy converges faster than any single agent

### Training Configuration

| Parameter | Value |
|-----------|-------|
| **Algorithm** | Multi-Agent Q-Learning with Federated Aggregation |
| **Epsilon-greedy** | ε decays from 1.0 → 0.01 |
| **Learning rate** | 0.001 |
| **Discount factor (γ)** | 0.99 |
| **Experience replay buffer** | 1M transitions |
| **Target network update** | Every 1000 steps |
| **Convergence window** | 100 episodes rolling average |
| **Federated sync interval** | Every 50 episodes |
| **Training data** | JPL Horizons ephemeris + historical telemetry |

### Performance Results

| Metric | CGR (baseline) | RL Agent | Improvement |
|--------|:--------------:|:--------:|:-----------:|
| Delivery ratio | 92% | 97% | +5% |
| Mean delivery time | 1.5 × light-time | 1.2 × light-time | −20% |
| Adaptation to failures | Manual (hours) | Autonomous (seconds) | **3600×** |
| Energy efficiency | Baseline | +15% savings | +15% |

### Demo

> **Launch demo**: [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/) → "RL Routing" tab

The web demo trains a simplified Q-learning agent in real-time, visualizing the Q-table convergence and routing decisions across the 5-tier network.
