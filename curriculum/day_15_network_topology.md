# Day 15: The 5-Tier Interplanetary Network Topology

## 📅 Thursday, August 06, 2026

## 🎯 Learning Objective

Map AETHERIX's complete 5-tier DTN architecture (241 nodes) from memory, justify the existence of each tier, and defend the medium-choice (optical vs RF) on every inter-tier hop — this directly addresses exam Learning Objective 3 (Network Architecture).

## 📖 The Core Concept

Interplanetary communication cannot be a flat mesh. The distances, orbital dynamics, and link budgets at Earth-Mars scale are so extreme that a single homogeneous network topology would collapse — every link would need to be engineered for the worst case (401 million km at conjunction), wasting capacity at the best case (54.6 million km at opposition). AETHERIX solves this by decomposing the problem into five stratified tiers, each with distinct orbital regimes, link technologies, and node populations.

Think of it as a waterfall. Data generated on the Martian surface (Tier 5) flows upward through Mars orbit (Tier 4), across deep space (Tier 3), down to Earth orbit (Tier 2), and finally to the ground (Tier 1). At each transition, the physical medium is chosen to match the link budget at that range. Inside a planet's gravity well, dense RF is preferred because the distances are short and omnidirectional coverage matters. In deep space, directional optical dominates because telescope gain compensates for the enormous free-space path loss.

**Tier 1 — Earth Ground (5 nodes):** Three NASA Deep Space Network stations (Goldstone, Madrid, Canberra) spaced 120° apart in longitude for continuous coverage, plus two operations centres (Mission Operations Center and Science Operations Center). These are the endpoints — where bundles are injected into and extracted from the interplanetary network. DSN stations carry massive 10 TB buffers because they absorb burst traffic from Mars and never become the bottleneck.

**Tier 2 — Earth Orbital (51 nodes):** Three geostationary relays (Atlantic, Pacific, Indian Ocean positions) forming a triangle for Earth-segment routing, plus a constellation of 48 LEO laser satellites. The LEO mesh provides inter-satellite optical links (ISL) at high data rates, routing data between DSN stations via space rather than relying on terrestrial fibre. This tier is Earth's aggregation layer — it collects deep-space traffic and distributes it to the appropriate ground station.

**Tier 3 — Deep Space Transit (4 nodes):** Two Lagrange relays at Earth-Sun L4 and L5 (60° ahead and behind Earth in its orbit) plus two transfer-orbit relays. These are the critical conjunction-coverage nodes: when the Sun sits between Earth and Mars, the L4/L5 relays maintain line-of-sight to both planets around the solar limb. This tier also hosts quantum repeaters for QKD key exchange — the only tier with `qkd_capable=True` besides Mars orbital.

**Tier 4 — Mars Orbital (4 nodes):** Two areostationary relays (stationary over the Martian equator at 17,032 km altitude), one polar orbiter for high-latitude coverage, and one general-purpose Mars orbiter. These form a full mesh (K4) for redundancy. They serve as the custody anchor — the last reliable deep-space node before data descends to the surface.

**Tier 5 — Mars Surface (177 nodes):** Two bases (Jezero and Oxia Planum), five rovers, ten drones, and 160 sensor nodes. This is the data generation frontier. Surface nodes communicate via UHF RF to the areostationary relays overhead, forming a hierarchical mesh where bases aggregate rover/drone/sensor traffic.

## 🔬 In AETHERIX

The topology is built entirely in `src/orbital/topology.py`. The `NetworkTopology` class manages a dictionary of nodes (`_nodes: Dict[str, DTNNode]`), an adjacency set (`_adjacency`), and a list of `InterTierLink` objects. Calling `build_default_topology()` constructs all 241 nodes across the five `_build_tierN()` methods:

- **Tier 1** (`_build_tier1`): registers `dsn-goldstone`, `dsn-madrid`, `dsn-canberra`, `earth-moc`, `earth-soc` — each with `_DSN_CAPS` (10,240 GB buffer, 200 Mbps, S/X/Ka/optical bands).
- **Tier 2** (`_build_tier2`): registers three GEO relays plus `leo-01` through `leo-48` — each LEO satellite is optical-only (`_LEO_CAPS`), 1,024 GB buffer, 100 Mbps.
- **Tier 3** (`_build_tier3`): registers `es-l4`, `es-l5`, `transfer-01`, `transfer-02` — all with `_LAGRANGE_CAPS` including `qkd_capable=True`.
- **Tier 4** (`_build_tier4`): registers `areo-alpha`, `areo-beta`, `polar-gamma`, `mars-orbiter`.
- **Tier 5** (`_build_tier5`): registers `base-jezero`, `base-oxia`, `rover-01`–`rover-05`, `drone-01`–`drone-10`, `sensor-001`–`sensor-160`.

The `build_inter_tier_links()` method wires every inter-tier hop with rate, latency, and availability. Use `get_tier_summary()` to print node counts per tier, and `get_node_count()` to confirm the 241 total. Pathfinding uses BFS (`find_route()`) over the adjacency set, yielding minimum-hop paths appropriate for a sparse contact plan where every hop is expensive.

## 📐 Key Numbers & Formulas

| Metric | Value |
|--------|-------|
| Total nodes | **241** |
| Tier 1 (Earth Ground) | 5 nodes |
| Tier 2 (Earth Orbital) | 51 nodes (3 GEO + 48 LEO) |
| Tier 3 (Deep Space) | 4 nodes (ES-L4, ES-L5, 2 transfer) |
| Tier 4 (Mars Orbital) | 4 nodes |
| Tier 5 (Mars Surface) | 177 nodes (2 bases + 5 rovers + 10 drones + 160 sensors) |
| QKD-anchored tiers | 3 and 4 (`qkd_capable=True`) |
| Typical end-to-end hops | 5–6 |

**Inter-tier link rates and availability:**

| Hop | Medium | Rate (Mbps) | Latency | Availability |
|-----|--------|------------:|--------:|-------------:|
| 1→2 (DSN↔GEO) | Ka-band RF | 10 | 0.01 s | 0.995 |
| 2→3 (GEO↔Lagrange) | Optical | 100 | 1.0 s | 0.970 |
| 2→3 (LEO↔Lagrange) | Optical | 80 | 1.2 s | 0.920 |
| 3→4 (Lagrange↔Areo) | Optical | 50 | 600 s | 0.900 |
| 4→5 (Areo↔Surface) | UHF RF | 2 | 0.001 s | 0.980 |

## 🔗 Standards & References

- [RFC 4838 — Delay-Tolerant Networking Architecture](https://datatracker.ietf.org/doc/html/rfc4838)
- [CCSDS 734.2-B-1 — DTN Architecture](https://public.ccsds.org/Pubs/734x2b1.pdf)
- [RFC 9171 — Bundle Protocol Version 7](https://datatracker.ietf.org/doc/html/rfc9171)
- [NASA Deep Space Network](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/deep-space-network/)

## 💡 How the Examiner Will Probe This

**Q: "Explain AETHERIX's five-tier network architecture and justify each tier."**
Start with the waterfall metaphor. Walk through each tier: what it does, what nodes it holds, and why it cannot be merged with an adjacent tier. Emphasize that Tier 3's conjunction coverage cannot be replicated by any number of ground stations, and that Tier 2's ISL routing bypasses terrestrial network dependencies.

**Q: "What's the weakest tier?"**
Tier 3 — only 4 nodes, and if both L4 relays fail, conjunction availability drops to zero. That's why each Lagrange point has a primary and backup satellite.

**Q: "Why not merge Tier 1 and Tier 2?"**
The ground and orbital tiers serve fundamentally different functions: ground stations are fixed, high-gain, and weather-sensitive; orbital relays are mobile, always-pointing, and weather-immune. Merging would eliminate the Earth-side aggregation layer.

## ✅ Self-Check Questions

1. How many nodes are in each tier, and what is the total? Verify against `get_node_count()`.
2. Which tier carries the lowest-availability inter-tier link, and what is its availability value?
3. Why does only every 12th LEO satellite get a direct optical link to a Lagrange relay?
4. Which tiers have `qkd_capable=True`, and why those specific tiers?
5. How does BFS routing (`find_route()`) differ from the RL agent's forwarding decisions?

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/topology.py` — `NetworkTopology` class, `build_default_topology()`, `build_inter_tier_links()`
- **Topic summary:** `interview_prep/topic_summaries/network_topology.md`
- **Mock interview:** `interview_prep/practice/mock_interview.md` — Q8 (Network Architecture)
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §8 (Blast-radius analysis), §9.3 (Why not Mars GEO only)
- **Demo:** Run `python src/orbital/topology.py` or call `create_default_topology()` interactively
