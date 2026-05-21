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

## Experience Replay & Training

[38] L.-J. Lin, "Self-Improving Reactive Agents Based on Determination of the Optimal Behavior: Case Studies of Reinforcement Learning," Ph.D. dissertation, University of Pittsburgh, 1992.

> Introduces experience replay — storing past transitions and replaying them during training to break temporal correlations and improve sample efficiency. AETHERIX's training pipeline implements experience replay buffers at each routing agent, enabling offline training on historical contact schedules and simulated traffic patterns without requiring live network interaction.

[39] S. Zhang, R. S. Sutton, and M. White, "A Deeper Look at Experience Replay," arXiv preprint arXiv:1712.01275, 2017.

> Analyzes why experience replay improves deep RL stability, demonstrating that prioritized replay based on TD-error magnitude accelerates convergence. AETHERIX's federated training module uses prioritized experience replay to focus learning on routing decisions with the highest prediction error — typically involving conjunction blackouts and link failures where the current Q-table is least accurate.

## Federated Reinforcement Learning

[40] X. Wang, R. Gao, and L. Jiao, "Federated Reinforcement Learning: Algorithm, Application and Opportunity," arXiv preprint arXiv:2105.10619, 2021.

> Surveys federated reinforcement learning (FRL), where distributed agents train local models and periodically aggregate updates without sharing raw data. AETHERIX's multi-agent federation uses FRL to maintain routing intelligence across the 5-tier topology: each node trains on local traffic observations, then shares Q-table updates (not packet data) via federated averaging, preserving data sovereignty at each mission operations center.

[41] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. Aguera y Arcas, "Communication-Efficient Learning of Deep Networks from Decentralized Data," in *Proc. 20th Int. Conf. Artificial Intelligence and Statistics (AISTATS)*, 2017, pp. 1273-1282.

> Introduces Federated Averaging (FedAvg), the foundational algorithm for federated learning. AETHERIX adapts FedAvg for Q-table aggregation: each node performs k episodes of local Q-learning, then transmits its Q-table delta to a central aggregator (e.g., at a Lagrange relay) which computes a weighted average. The communication cost is bounded by the state-action space size, making it feasible over deep-space links with limited contact windows.

## Multi-Agent Q-Learning & Convergence

[42] J. Hu and M. P. Wellman, "Multiagent Reinforcement Learning: Theoretical Framework and an Algorithm," in *Proc. 15th Int. Conf. Machine Learning (ICML)*, 1998, pp. 242-250.

> Introduces Nash Q-learning, extending Q-learning to multi-agent settings where each agent maintains Q-functions over joint actions. Proves convergence to a Nash equilibrium under specific exploration conditions. AETHERIX's multi-agent routing uses a simplified cooperative variant where agents share action observations, converging faster than fully independent Q-learning at the cost of modest communication overhead.

[43] C. J. C. H. Watkins and P. Dayan, "Q-Learning," *Machine Learning*, vol. 8, no. 3, pp. 279-292, May 1992. doi: 10.1007/BF00992698

> The original convergence proof for Q-learning, establishing that tabular Q-learning with appropriate learning rate decay converges to the optimal Q-function with probability 1. AETHERIX's routing agent relies on this guarantee in the single-agent (centralized training) setting; the multi-agent extension requires additional convergence assumptions documented in Hu & Wellman (1998). The training pipeline implements learning rate scheduling (α_t = 1/visit_count(s,a)) to satisfy Watkins & Dayan's convergence conditions.
