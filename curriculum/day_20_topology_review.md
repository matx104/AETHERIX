# Day 20: Topology Review & Design Defense

## 📅 Tuesday, August 11, 2026

## 🎯 Learning Objective

Synthesize the full 5-tier, 241-node topology into a coherent defense: identify the weakest tier, explain redundancy strategies, describe mesh networking and handover protocols, and articulate why each architectural choice was made — consolidating exam Learning Objective 3.

## 📖 The Core Concept

Over the past five lessons, you've learned each tier individually. Today, Abdullah, you must defend the topology as a **complete system**. An examiner will not ask you to recite node counts — they will probe your understanding of **why** this topology exists, **what fails**, and **how the system recovers**. This lesson is your dress rehearsal for the topology defense.

**The weakest-tier analysis:**

Tier 3 (Deep Space Transit) is the acknowledged vulnerability. With only 4 nodes, it has the lowest redundancy of any tier. If both ES-L4 relays fail simultaneously, conjunction availability for the L4 path drops to zero — all conjunction traffic must reroute through ES-L5. If ES-L5 also fails, there is no conjunction coverage at all. This is why AETHERIX deploys a **primary and spare** at each Lagrange point, and why the K4 intra-tier mesh ensures any surviving node can reach any other.

The 3→4 inter-tier link (Lagrange↔Mars Orbital) is the **lowest-availability link** in the topology at 0.900. This reflects the enormous path loss, deep-space pointing challenges, and solar interference even at 60° offset during conjunction. A 0.90 availability means approximately 1 in 10 transmission attempts needs LTP retransmission — acceptable because DTN's store-and-forward architecture treats retransmission as routine, not exceptional.

**Redundancy strategies by tier:**

Each tier employs a different redundancy strategy matched to its failure modes:

- **Tier 1 (Ground):** Geographic diversity — three DSN complexes at 120° spacing ensure no single weather event or outage takes down all ground stations.
- **Tier 2 (Orbital):** Structural redundancy — the GEO triangle and LEO ring provide multiple paths. If one GEO relay fails, the triangle still routes through the other two.
- **Tier 3 (Deep Space):** Spatial redundancy — primary + spare at each Lagrange point, plus a K4 mesh so any node can relay through any other.
- **Tier 4 (Mars Orbital):** Full mesh (K4) — four orbitals, all interconnected. If one fails, three remain.
- **Tier 5 (Surface):** Hierarchical with fallback — if an areostationary relay fails, polar orbiters pick up traffic on their next pass. Store-and-forward ensures no data is lost during the gap.

**Mesh networking and handover:**

Within each tier, mesh connectivity provides alternative paths. The BFS routing in `find_route()` naturally discovers these alternatives — if one neighbor is unreachable, the BFS explores other branches. The RL agent operates on top of this adjacency, making per-bundle store-vs-forward decisions based on current link quality rather than statically routing through a predetermined path.

Handover between contact windows is handled by the DTN architecture itself — there is no TCP-style connection to tear down and rebuild. When a Mars orbiter passes over a rover, the rover forwards bundles during the window and simply holds them when the orbiter sets. The next orbiter pass opens a new window. This **contact-scheduled handover** is fundamentally different from cellular-style handover: there is no real-time session migration, just opportunistic forwarding during predicted contact windows.

**The no-shared-fate principle:**

The tiered design ensures failures are localized. A Tier 5 sensor failure cannot affect Tiers 1–3 because there is no synchronous dependency — only store-and-forward contact windows. This is the opposite of a live TCP mesh where one node's failure stalls dependent connections. The blast radius of any single failure is bounded by the tier hierarchy.

## 🔬 In AETHERIX

The complete topology is instantiated by `create_default_topology()` in `src/orbital/topology.py`, which calls `build_default_topology()` (all five tiers) then `build_inter_tier_links()` (all inter-tier and intra-tier wiring). After construction:

- `get_node_count()` returns **241**
- `get_tier_summary()` returns `{1: 5, 2: 51, 3: 4, 4: 4, 5: 177}`
- `get_contact_graph()` builds a bidirectional contact graph for every adjacency edge, attaching rate and delay to each contact.

The `find_route(source, dest)` method uses BFS over `_adjacency` to find minimum-hop paths. This is appropriate because every inter-tier hop is expensive (energy, latency, custody overhead) and the contact plan is sparse. The RL routing agent (`src/routing/rl_agent.py`) operates **on top of** this adjacency, choosing store-vs-forward per bundle rather than recomputing paths.

The `_link_rate()` and `_link_delay()` methods look up inter-tier link characteristics by tier pair. For same-tier links, the rate is the minimum of the two endpoints' `max_data_rate_mbps`, and delay is 0.001s.

## 📐 Key Numbers & Formulas

| Defense Point | Value |
|---------------|-------|
| Total nodes | 241 |
| Weakest tier | Tier 3 (4 nodes) |
| Lowest-availability link | 3→4 at 0.900 |
| Highest-availability link | 1→2 at 0.995 |
| QKD-anchored tiers | 3 and 4 |
| Typical end-to-end hops | 5–6 |
| Mars surface buffer capacity | 177 nodes × 10–2,048 GB |
| Areostationary relay buffer | 2,048 GB each (~1.4× conjunction backlog margin) |

**Combined availability formula:**
```
A_combined = 1 − (1 − A_optical)(1 − A_RF) = 1 − (1−0.957)(1−0.99) = 99.96%
```

## 🔗 Standards & References

- [RFC 4838 — DTN Architecture](https://datatracker.ietf.org/doc/html/rfc4838)
- [CCSDS 734.3-B-1 — Schedule-Aware Bundle Routing (SABR)](https://public.ccsds.org/Pubs/734x3b1.pdf)
- [RFC 9171 — Bundle Protocol Version 7 §4.5 (Custody)](https://datatracker.ietf.org/doc/html/rfc9171#section-4.5)

## 💡 How the Examiner Will Probe This

**Q: "What's the weakest tier, and what's your mitigation?"**
Tier 3 — 4 nodes, lowest-availability link (0.90). Mitigation: primary + spare at each Lagrange point, K4 intra-tier mesh, and the RL agent automatically reroutes to ES-L5 if ES-L4 fails. The blast radius of a Lagrange failure is bounded — only conjunction traffic is affected; normal opposition/quadrature traffic uses direct links.

**Q: "Draw your backup path if ES-L4 fails."**
Mars → (optical) → ES-L5 → (Ka-band) → Earth. Latency unchanged (same hop count). ES-L5 may carry slightly less margin but is fully operational. P0 bundles reroute immediately; P4 deferred (store).

**Q: "Why not a flat mesh of all 241 nodes?"**
A flat mesh would require each node to maintain 240 neighbor states. At interplanetary scale, most of those "neighbors" are unreachable most of the time. The tiered hierarchy limits neighbor state to a manageable set, concentrates buffer capacity where needed, and matches link technology to link budget at each range.

**Q: "How does the system handle cascading congestion?"**
Policy engine drops P4 first, then P3, never P0/P1. RL agent learns to proactively forward lower-priority bundles before hitting 90% buffer. Custody refusal provides back-pressure — a congested node signals upstream to seek alternate paths rather than pushing more data into a full queue.

## ✅ Self-Check Questions

1. What is the weakest tier, and what is the lowest-availability inter-tier link? Justify both.
2. Explain the K4 intra-tier mesh in Tier 3. How does it provide conjunction resilience?
3. What is the blast radius of a Mars surface sensor failure? Why is it contained?
4. How does the combined availability formula yield 99.96%? Walk through the numbers.
5. Why does the BFS minimum-hop routing strategy make sense for a sparse DTN contact plan?

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/topology.py` — `create_default_topology()`, `find_route()`, `get_tier_summary()`, `get_contact_graph()`
- **Topic summary:** `interview_prep/topic_summaries/network_topology.md` — complete reference
- **Mock interview:** `interview_prep/practice/mock_interview.md` — Q8 (Architecture), Q13 (Data Prioritisation)
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §3 (failure-mode decision trees), §8 (blast-radius analysis), §9 (why-not defenses)
- **Cheat sheet:** `interview_prep/cheat_sheets/constants.md` — Network Parameters
