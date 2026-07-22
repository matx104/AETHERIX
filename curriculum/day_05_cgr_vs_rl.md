# Day 5: Contact Graph Routing vs RL Routing

## 📅 July 27, 2026

## 🎯 Learning Objective
Understand Contact Graph Routing (CGR) — the current state-of-practice for DTN routing — its limitations, and how AETHERIX's reinforcement-learning approach overcomes them. Know exactly when and why the system falls back to CGR. This maps to **LO1** and is the central architectural argument of the entire project.

## 📖 The Core Concept

### What Is Contact Graph Routing?

Contact Graph Routing (CGR) is the routing approach used by virtually every operational DTN today (NASA's ION-DTN, ESA's missions). It works by building a graph where each **vertex is a scheduled contact window** — a tuple of `(from_node, to_node, start_time, end_time, data_rate)`. An edge connects vertex A to vertex B if A's destination equals B's source and A ends before B starts (the bundle can traverse A then B without an impossible wait).

CGR then runs a pathfinding algorithm (typically Dijkstra or BFS) over this contact graph to find the path with the **earliest delivery time** or least delay. The result is deterministic and provably optimal — *if the contact schedule is accurate*.

### CGR's Four Critical Limitations

AETHERIX exists because CGR has four fundamental weaknesses in the real interplanetary environment:

1. **Cannot adapt to unplanned link failures.** Solar flares, equipment faults, dust storms, and radiation upsets cause contacts that were *scheduled* to fail. CGR has no mechanism to detect this and reroute in real time — it follows the schedule until a human uploads a new one.

2. **No multi-objective optimisation.** CGR minimises delay. But a real Mars mission needs to balance delay against energy budget, buffer pressure, and drop risk simultaneously. A path that is fastest might drain a battery-powered rover's energy reserves or overload a relay's buffer.

3. **Schedule staleness.** The contact schedule must be uploaded from Earth. At 12+ minutes one-way delay, the "current" schedule is always stale by at least 24 minutes (round trip). A solar flare that began 5 minutes ago will not be reflected in any schedule the Mars relay has.

4. **Does not learn from experience.** CGR treats every routing decision independently. It does not remember that link X consistently degrades during a particular orbital phase, or that buffer overflow tends to cascade from node Y.

### The RL Approach: Adaptive, Multi-Objective, Learning

AETHERIX replaces the static CGR lookup with a reinforcement-learning agent that:

- **Observes the current network state** — link qualities, buffer occupancy, bundle priority, deadline — in real time from local measurements.
- **Selects an action** from `{FORWARD, STORE, DROP, SPLIT}` based on learned Q-values.
- **Receives a reward** that balances five objectives: `R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)`.
- **Updates its policy** through Q-learning, improving over time.
- **Adapts to unplanned events** — a link failure that CGR would blindly follow, the RL agent detects (quality drops below threshold) and reroutes immediately.

### The Hybrid: RL Primary, CGR Fallback

This is the key architectural decision: AETHERIX does not throw away CGR. It uses a **hybrid** approach:

- **RL agent is primary** for all routing decisions.
- **CGR is the fallback** when the RL agent's confidence drops below **0.3** (the `MIN_LINK_QUALITY` threshold).

Why keep CGR as a fallback? Because the RL agent might encounter a state space it was not trained on — a network configuration outside the simulation's training distribution. In that case, blindly trusting the agent could produce catastrophic decisions. CGR provides a **deterministic, safe floor** — it may not be optimal, but it will never make a nonsensical routing choice.

The DESIGN_RATIONALE.md states this clearly: "The hybrid (RL primary, CGR fallback when agent confidence < 0.3) gets the best of both."

### The Trade-off

RL requires training time and compute. The AETHERIX demo uses tabular Q-learning (Q-tables); the production upgrade path is Deep Q-Network (DQN) with experience replay. The trade-off is:
- **Benefit:** real-time adaptivity, multi-objective optimisation, learning from experience
- **Cost:** training overhead, the need for a fallback when the agent is uncertain

## 🔬 In AETHERIX

The CGR component is implemented in `src/routing/contact_graph.py`:

**`Contact`** dataclass models a scheduled contact: `contact_id`, `source_node`, `dest_node`, `start_time`, `end_time`, `data_rate_mbps`, `delay_seconds`, `state` (PENDING/ACTIVE/COMPLETED/FAILED/CANCELLED), `volume_megabits`. The `calculate_volume()` method computes `data_rate_mbps × duration_seconds / 8.0`.

**`ContactGraph`** stores contacts in adjacency lists (`_outgoing`, `_incoming` dicts). Key methods:
- `add_contact(contact)` — registers a contact in both adjacency lists.
- `get_active_contacts(current_time)` — returns contacts where `start_time <= now <= end_time`.
- `find_path(source, destination)` — **BFS traversal** over the contact graph, exploring in order of hop count. Returns the list of `Contact` objects forming the path. BFS is preferred over Dijkstra because edge weights (delay) are **time-dependent** — a contact opening sooner may have a later end-to-end delivery than one opening later with shorter subsequent hops.
- `get_reachable_nodes(source)` — BFS to find all nodes reachable from source.

The RL routing is in `src/routing/rl_agent.py`. The `RLRoutingAgent` uses `MIN_LINK_QUALITY = 0.3` as the threshold below which it refuses to forward (returning STORE instead). This same 0.3 value serves as the confidence floor for the CGR fallback.

The `ForwardingEngine` (`forwarding_engine.py`) wires both together: it consults the RL agent via `select_action()` on every dequeue cycle. If the agent returns a decision with low confidence or no acceptable links, the engine can fall back to the contact graph's `find_path()`.

The DESIGN_RATIONALE.md §9.7 documents this decision: "CGR re-plans on schedule refresh. At 12+ min one-way delay, the 'current' schedule is always stale. The RL agent reacts to measured link/buffer state in real time."

## 📐 Key Numbers & Formulas
- **CGR fallback threshold:** RL agent confidence < **0.3** (`MIN_LINK_QUALITY`)
- **Schedule staleness:** ≥ 24 minutes (round-trip upload delay)
- **CGR objective:** minimise delay (single objective)
- **RL objective:** maximise `R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)` (five objectives)
- **Contact volume formula:** `data_rate_mbps × duration_seconds / 8.0`
- **Pathfinding:** BFS (not Dijkstra) due to time-dependent edge weights
- **Current state-of-practice:** CGR (used by NASA ION-DTN, ESA missions)
- **AETHERIX upgrade path:** tabular Q-learning → DQN with experience replay

## 🔗 Standards & References
- [CCSDS 734.3-B-1 — Schedule-Aware Bundle Routing (SABR)](https://public.ccsds.org/Pubs/734x3b1.pdf)
- [RFC 9171 — Bundle Protocol v7 (routing requirements)](https://datatracker.ietf.org/doc/html/rfc9171)
- [Burleigh, "The Interplanetary Internet: Architecture and Key Concepts" (CGR origins)](https://datatracker.ietf.org/doc/html/rfc4838)
- [NASA ION-DTN (CGR implementation)](https://github.com/nasa/ION-DTN)
- `docs/DESIGN_RATIONALE.md` §9.7 — "Why not CGR with frequent schedule updates?"

## 💡 How the Examiner Will Probe This

**Q: "How does your RL routing agent work, and what advantage does it have over Contact Graph Routing?"**
→ The agent uses Q-learning with four actions (forward, store, drop, split). State includes node, link qualities, buffer, priority, deadline, destination. Reward balances five objectives. Compared to CGR, the RL agent adapts in real time to unplanned events, optimises multiple objectives instead of just delay, and learns from experience over the 780-day synodic period. CGR requires pre-uploaded schedules that are stale by 12+ minutes. The fallback is CGR when agent confidence < 0.3.

**Q: "Why keep CGR as a fallback? If RL is better, why not use it exclusively?"**
→ Because the RL agent might encounter states outside its training distribution — a network configuration it never saw during simulation. Blindly trusting the agent in unfamiliar territory could produce catastrophic routing decisions. CGR provides a deterministic safe floor. The hybrid gives the best of both: RL's adaptivity when it's confident, CGR's reliability when it's not.

## ✅ What You Should Be Able to Answer After This Lesson
1. What are the four limitations of CGR that motivate AETHERIX's RL approach?
2. At what confidence threshold does the system fall back to CGR, and why that value?
3. Why does AETHERIX use BFS instead of Dijkstra for contact graph pathfinding?
4. What is the contact volume formula, and why does it matter for path validation?
5. What is the production upgrade path from the current RL implementation?

## 📂 Deep Dive Resources
- `src/routing/contact_graph.py` — `ContactGraph`, `Contact`, `find_path()`
- `src/routing/rl_agent.py` — `RLRoutingAgent`, `MIN_LINK_QUALITY = 0.3`
- `src/routing/forwarding_engine.py` — how the engine wires RL + CGR
- `docs/DESIGN_RATIONALE.md` — §9.7 (CGR vs RL rationale)
- `interview_prep/topic_summaries/reinforcement_learning.md` — RL vs CGR comparison
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
