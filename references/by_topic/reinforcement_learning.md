# Reinforcement Learning for Network Routing References

AETHERIX replaces static Contact Graph Routing with an RL-based routing agent that adapts to dynamic link conditions (variable latency, buffer congestion, asymmetric data rates). The references below cover the RL foundations (DQN, policy gradients), prior work applying RL to network routing and DTN scheduling, and multi-agent RL for distributed routing across the 5-tier network topology.

## Most Important

| Ref | Citation | Why Critical |
|-----|----------|--------------|
| [30] | Mnih et al., 2015 | DQN paper — the architecture AETHERIX will upgrade to from Q-tables |
| [31] | Sutton & Barto, 2018 | Standard RL textbook — theoretical foundation |
| [32] | Stampa et al., 2017 | RL for SDN routing — closest prior work to AETHERIX's approach |
| [34] | Sun et al., 2018 | RL for deep-space network scheduling — directly applicable |
| [36] | Busoniu et al., 2008 | Multi-agent RL survey — needed for distributed AETHERIX nodes |

---

## Foundational RL

[30] V. Mnih et al., "Human-Level Control Through Deep Reinforcement Learning," *Nature*, vol. 518, no. 7540, pp. 529-533, Feb. 2015. doi: 10.1038/nature14236

> The Deep Q-Network (DQN) paper that demonstrated RL could learn directly from high-dimensional state representations using neural network function approximation. AETHERIX's current `RLRoutingAgent` uses a Q-table; the production upgrade path identified in the architecture docs is to replace this with a DQN using Mnih's experience replay and target network stabilization techniques.

[31] R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 2nd ed. Cambridge, MA: MIT Press, 2018.

> The standard textbook on reinforcement learning, covering temporal-difference learning, policy gradient methods, and function approximation. AETHERIX's reward function formulation — R = α(delivery) - β(delay) - γ(hops) - δ(drops) - ε(energy) — follows the Markov Decision Process framework described in Chapters 3 and 6.

## RL for Networking

[32] G. Stampa, M. Arias, D. Sánchez-Charles, V. Muntés-Mulero, and A. Cabellos, "A Deep-Reinforcement Learning Approach for Software-Defined Networking Routing Optimization," arXiv preprint arXiv:1709.07080, 2017.

> Applies DQN to routing optimization in software-defined networks. While focused on terrestrial SDN, the state representation (network topology, link utilization, delay) and action space (next-hop selection) are structurally identical to AETHERIX's `NetworkState` and `RoutingAction` abstractions. The key transferable insight is that RL can learn non-obvious routing policies that outperform shortest-path heuristics.

[33] A. Valadarsky, M. Schapira, D. Shahaf, and A. Tamar, "Learning to Route," in *Proc. 16th ACM Workshop on Hot Topics in Networks*, 2017, pp. 185-191.

> Proposes learning routing policies directly from traffic patterns using RL. Demonstrates that learned policies can adapt to network dynamics that static routing tables cannot handle — the core motivation for AETHERIX's RL approach over static Contact Graph Routing.

[34] P. Sun, J. Li, M. Z. A. Bhuiyan, L. Wang, and B. Li, "Modeling and Simulation of Deep-Space Network Scheduling Using Reinforcement Learning," in *Proc. IEEE Int. Conf. Communications*, 2018, pp. 1-6.

> Directly applies RL to deep-space network scheduling, optimizing antenna allocation and data transmission scheduling at DSN stations. This is the closest published work to AETHERIX's application domain and validates the feasibility of RL for deep-space communication optimization. AETHERIX extends this by also optimizing the routing path, not just scheduling.

[35] N. Bezirgiannidis, F. Tsapeli, S. Diamantopoulos, and V. Tsaoussidis, "Towards Flexibility and Programmability of the Delay Tolerant Network of the DSN," in *Proc. IEEE Aerospace Conf.*, 2016, pp. 1-9.

> Argues for programmable, flexible DTN routing in the Deep Space Network rather than static contact plans. This paper motivates AETHERIX's entire RL routing component: if contact plans are too rigid for real DSN operations, a learning-based approach that adapts to observed conditions is the natural solution.

## Multi-Agent RL

[36] L. Busoniu, R. Babuska, and B. De Schutter, "A Comprehensive Survey of Multiagent Reinforcement Learning," *IEEE Trans. Syst., Man, Cybern. C, Appl. Rev.*, vol. 38, no. 2, pp. 156-172, Mar. 2008.

> Comprehensive survey of multi-agent RL (MARL). AETHERIX's 5-tier topology (Earth ground, Earth orbital, deep space transit, Mars orbital, Mars surface) implies routing agents at each node that must cooperate without a central controller. Busoniu's taxonomy of MARL approaches (cooperative, competitive, communication-based) informs the choice of cooperative MARL for AETHERIX's distributed routing.

[37] P. Hernandez-Leal, M. Kaisers, T. Baarslag, and E. M. de Cote, "A Survey of Learning in Multiagent Environments: Dealing with Non-Stationarity," arXiv preprint arXiv:1707.09183, 2017.

> Addresses the fundamental challenge in MARL: each agent's learning makes the environment non-stationary for all other agents. In AETHERIX's context, as routing policies update at individual nodes, the optimal policy for other nodes changes. Hernandez-Leal's analysis of non-stationarity mitigation strategies (experience replay stabilization, opponent modeling) will be critical for AETHERIX's production MARL implementation.
