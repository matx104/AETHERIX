# Network Topology

## Topic Summary

### The 5-Tier Architecture

AETHERIX decomposes the Earth-to-Mars communication problem into five
stratified tiers, each with distinct orbital dynamics, link budgets, and
node populations. Bundles traverse the tiers over inter-tier links whose
physical medium is chosen to match the link budget at that range: dense RF
inside each planet's gravity well, directional optical in deep space where
antenna gain compensates for enormous path loss.

The topology is built programmatically in `src/orbital/topology.py`
(`build_default_topology()`), then wired with inter-tier links in
`build_inter_tier_links()`. The full network has **241 nodes**.

| Tier | Name | Nodes | Composition | Primary role |
|------|------|------:|-------------|--------------|
| 1 | Earth Ground | 5 | 3 DSN stations (34 m dishes) + 2 ops centres (MOC, SOC) | Ground segment, DSN up/downlink |
| 2 | Earth Orbital | 51 | 3 GEO relays + 48 LEO laser satellites (1200 km) | Earth-side aggregation, optical ISL |
| 3 | Deep Space Transit | 4 | 2 Lagrange relays (ES-L4, ES-L5) + 2 transfer relays | Deep-space store-and-forward |
| 4 | Mars Orbital | 4 | 2 areostationary + 1 polar + 1 orbiter | Mars-side relay, custody anchor |
| 5 | Mars Surface | 177 | 2 bases + 5 rovers + 10 drones + 160 sensors | Surface science and operations |
| **Total** | | **241** | | |

> **Node-count note**: The headline 241 is exact (`get_node_count()` on the
> default topology). The per-tier split sums to 241 because Tier 1 includes
> the two ground ops centres (MOC/SOC) alongside the three DSN stations,
> and Tier 5 holds 177 surface assets.

---

### Tier-by-Tier Capabilities

Every node carries a `NodeCapabilities` record (buffer, supported bands,
max data rate, processing power). The capacities are shared per node type.

| Node type | Buffer (GB) | Max rate (Mbps) | Bands | Optical | QKD |
|-----------|------------:|----------------:|-------|:-------:|:---:|
| DSN station | 10 240 | 200 | S, X, Ka, optical | yes | no |
| Ops centre (MOC/SOC) | 10 240 | 200 | X, Ka | no | no |
| GEO relay | 5 120 | 150 | Ka, optical | yes | no |
| LEO laser satellite | 1 024 | 100 | optical | yes | no |
| Lagrange relay | 5 120 | 150 | Ka, optical | yes | **yes** |
| Areostationary / polar relay | 2 048 | 100 | UHF, Ka, optical | yes | **yes** |
| Mars base | 2 048 | 10 | UHF, X | no | no |
| Rover | 100 | 2 | UHF | no | no |
| Drone | 50 | 5 | UHF | no | no |
| Sensor node | 10 | 0.5 | UHF | no | no |

QKD terminates at the Lagrange (tier 3) and Mars-orbital (tier 4) tiers —
the only nodes with `qkd_capable=True`, anchoring BB84/E91 key exchange at
the deep-space and Mars-orbital boundaries.

---

### Inter-Tier Links

Inter-tier links (`InterTierLink` dataclass) carry the bulk of cross-planet
traffic. Each declares a link type, data rate, latency, and availability.

| Hop | Medium | Rate (Mbps) | Latency | Availability |
|-----|--------|------------:|--------:|-------------:|
| 1 -> 2 (DSN <-> GEO) | Ka-band RF | 10 | 0.01 s | 0.995 |
| 2 -> 3 (GEO <-> Lagrange) | Optical (1550 nm) | 100 | 1.0 s | 0.970 |
| 2 -> 3 (LEO <-> Lagrange) | Optical (1550 nm) | 80 | 1.2 s | 0.920 |
| 3 -> 4 (Lagrange <-> Areo) | Optical (1550 nm) | 50 | 600 s | 0.900 |
| 4 -> 5 (Areo <-> Surface) | UHF RF | 2 | 0.001 s | 0.980 |

**Medium choice rationale**: optical dominates tiers 2-3-4 because the high
gain of a telescope (+113 dBi at 22 cm, 1550 nm) closes the link despite
the -370 dB free-space loss at average distance. RF (Ka at 1-2, UHF at
4-5) is preferred where beam divergence, pointing, or atmosphere make
optical impractical. The 600 s one-way latency on the 3 -> 4 hop reflects
the deep-space light-time; the Mars-orbital-to-surface hop (0.001 s) is
effectively instantaneous by comparison.

---

### Intra-Tier Connectivity

Within each tier, nodes are meshed for redundancy:

| Tier | Intra-tier wiring |
|------|-------------------|
| 1 | DSN/ops centres backed by terrestrial network |
| 2 | 3 GEO relays form a triangle; 48 LEO sats form a ring (i -> i+1 mod 48) |
| 3 | 4 Lagrange/transfer relays form a full mesh (K4) |
| 4 | 4 Mars orbitals form a full mesh (K4) |
| 5 | 2 bases linked; rovers/drones homed to a base round-robin; sensors parented to drones |

Only every 12th LEO satellite (`leo_ids[::12]`) gets a direct optical link
to a Lagrange relay, giving 4 cross-links and bounding the 2 -> 3 fan-out.

---

### BFS Routing Across the Topology

Pathfinding uses breadth-first search over the adjacency set
(`find_route()`, `topology.py:314`). BFS yields the **minimum-hop** path,
appropriate because every inter-tier hop is expensive (energy, latency,
custody overhead) and the contact plan is sparse.

```
find_route(source, dest):
    visited <- {source}
    queue   <- [(source, [source])]
    while queue not empty:
        (node, path) <- queue.popleft()
        for neighbor in adjacency[node]:
            if neighbor in visited: continue
            visited.add(neighbor)
            if neighbor == dest: return path + [neighbor]
            queue.append((neighbor, path + [neighbor]))
    return []
```

BFS runs on a static, always-on contact graph (`get_contact_graph()`);
per-contact rate and delay are attached to each edge for the forwarding
engine and RL agent to consume. The RL routing agent
(`src/routing/rl_agent.py`) operates *on top of* this adjacency, choosing
store-vs-forward per bundle rather than recomputing paths.

---

### Diameter and Headline Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Total nodes | 241 | `get_node_count()` |
| Typical end-to-end hops | 5-6 | Earth asset to Mars sensor |
| QKD-anchored tiers | 3 and 4 | `qkd_capable=True` |
| Highest-availability link | 1 -> 2 (0.995) | Ka-band, short range |
| Lowest-availability link | 3 -> 4 (0.900) | Deep-space optical |

---

### Key Formulas Summary

| Formula | Equation | Used In |
|---------|----------|---------|
| Node count | `len(self._nodes)` | `topology.py:305` |
| Tier summary | `count per node.tier` | `topology.py:308` |
| Inter-tier rate | `lookup InterTierLink by (lo, hi)` | `_link_rate()` |
| Inter-tier delay | `lookup InterTierLink by (lo, hi)` | `_link_delay()` |
| BFS path | `BFS over adjacency` | `find_route()` |
| Combined availability | `1 - prod(1 - A_i)` | see `link_budget.md` |
