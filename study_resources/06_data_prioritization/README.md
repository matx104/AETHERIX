# Learning Objective 6: Mission-Critical Data Prioritization

## Free Online Courses & Certificates

### University Courses (Free)
- **[Reinforcement Learning — David Silver (UCL)](https://www.davidsilver.uk/teaching/)** — THE free RL course, 10 lectures
- **[Reinforcement Learning — Sutton & Barto Book (Free)](http://incompleteideas.net/book/the-book.html)** — Complete free online textbook
- **[Deep Reinforcement Learning — Berkeley CS 285](https://rail.eecs.berkeley.edu/deeprlcourse/)** — Sergey Levine's course, all lectures free
- **[Introduction to RL — Coursera/Alberta](https://www.coursera.org/specializations/reinforcement-learning)** — Free audit

### Official Documentation (Free)
- **[RFC 9171 §4.2 — Bundle Priority](https://www.rfc-editor.org/rfc/rfc9171#section-4.2)** — BPv7 priority classes
- **[CCSDS 735.1-B-1 — Bundle Protocol](https://public.ccsds.org/Pubs/735x1b1.pdf)** — Priority and scheduling

### YouTube Videos (Free)

#### Must-Watch (RL & Routing)
| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [RL Course — David Silver Lecture 1](https://www.youtube.com/watch?v=2pWv7GO9uf0) | UCL | ~90 min | Start of the best free RL series |
| [Q-Learning Explained](https://www.youtube.com/watch?v=qhRNvCVVJaA) | ML with Phil | ~15 min | AETHERIX uses Q-learning |
| [Deep Q-Network (DQN)](https://www.youtube.com/watch?v=wc-FxNENg9U) | ML with Phil | ~15 min | AETHERIX's future upgrade |
| [Epsilon-Greedy Exploration](https://www.youtube.com/results?search_query=epsilon+greedy+reinforcement+learning) | Various | ~10 min | How the agent explores |
| [Multi-Agent RL](https://www.youtube.com/results?search_query=multi+agent+reinforcement+learning) | Various | ~15 min | Federated learning concept |
| [RL for Network Routing](https://www.youtube.com/results?search_query=reinforcement+learning+network+routing) | Various | ~15 min | Direct application |

#### QoS & Priority
| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [Quality of Service (QoS) Explained](https://www.youtube.com/results?search_query=QoS+quality+of+service+networking) | NetworkChuck | ~10 min | Priority queuing concepts |
| [Packet Scheduling Algorithms](https://www.youtube.com/results?search_query=packet+scheduling+algorithms) | Various | ~10 min | FIFO, PQ, WFQ |

### Academic Papers (Free / Open Access)

| Paper | Authors | Year | Link | Priority |
|-------|---------|------|------|:--------:|
| "Human-Level Control Through Deep RL" | Mnih et al. | 2015 | [Nature](https://doi.org/10.1038/nature14236) | HIGH |
| *Reinforcement Learning: An Introduction* (free) | Sutton & Barto | 2018 | [Book](http://incompleteideas.net/book/the-book.html) | MUST READ |
| "Deep-RL for Software-Defined Networking" | Stampa et al. | 2017 | [arXiv](https://arxiv.org/abs/1709.07080) | MEDIUM |
| "A Comprehensive Survey of Multiagent RL" | Busoniu et al. | 2008 | [IEEE](https://doi.org/10.1109/TSMCC.2007.913919) | MEDIUM |

### Blogs & Articles (Free)

- **[OpenAI Spinning Up](https://spinningup.openai.com/)** — Best free RL resource, with code
- **[Stable Baselines3 Docs](https://stable-baselines3.readthedocs.io/)** — RL library, tutorials
- **[RL — An Introduction (Sutton & Barto)](http://incompleteideas.net/book/the-book.html)** — FREE full textbook

### Key Concepts to Master

1. **BPv7 Priority Classes** — P0 (Emergency) through P4 (Bulk), know them all with examples
2. **Q-Learning** — Q(s,a) table, Bellman equation, epsilon-greedy exploration
3. **Reward Function** — R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy). Know the weights.
4. **State Space** — What the agent observes (8 variables in AETHERIX)
5. **Action Space** — Forward, store, drop, split
6. **Federated Learning** — Distributed training across space nodes
7. **Contact Graph Routing** — Know what it is and why RL is better

### Practice Questions

1. List the 5 BPv7 priority classes with examples (30 seconds)
2. Explain Q-learning in 60 seconds (state, action, reward, Q-table)
3. Why does AETHERIX use RL instead of CGR? (1 minute)
4. What is the reward function? Why is δ (drop penalty) so high? (30 seconds)
5. Explain epsilon-greedy exploration (30 seconds)
