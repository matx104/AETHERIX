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

### Training Approach

- **Algorithm**: Multi-Agent Deep Q-Network (MADQN)
- **Epsilon-greedy** exploration: ε decays from 1.0 → 0.01
- **Learning rate**: 0.001
- **Discount factor (γ)**: 0.99
- **Experience replay**: 1M transition buffer
- **Target network update**: Every 1000 steps
- **Training data**: JPL Horizons ephemeris + historical telemetry
- **Federated learning**: Each node trains locally, shares model weights

### Expected Performance

| Metric | CGR (baseline) | RL Agent | Improvement |
|--------|:--------------:|:--------:|:-----------:|
| Delivery ratio | 92% | 97% | +5% |
| Mean delivery time | 1.5 × light-time | 1.2 × light-time | −20% |
| Adaptation to failures | Manual (hours) | Autonomous (seconds) | **3600×** |
| Energy efficiency | Baseline | +15% savings | +15% |

### Demo

> **Launch demo**: [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/) → "RL Routing" tab

The web demo trains a simplified Q-learning agent in real-time, visualizing the Q-table convergence and routing decisions across the 5-tier network.
