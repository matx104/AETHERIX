# Day 9: DTN Integration — How All Modules Work Together

## 📅 July 31, 2026

## 🎯 Learning Objective
Understand how all AETHERIX DTN modules — bundles, convergence layers, store-and-forward, RL routing, CGR fallback, custody transfer, and multi-agent coordination — integrate into a single running system. Walk through `run_simulation.py` Module 1 (Baseline DTN) as the integration showcase. This maps to **LO1** and is the "big picture" question the examiner will use to test your systems-thinking.

## 📖 The Core Concept

### The Integration Stack

An AETHERIX node is a layered system. Data flows through these layers in order:

```
Application Layer
    ↓ (generate bundle)
Bundle Protocol Layer (BPv7)       ← bundle.py
    ↓ (route decision)
Routing Layer                       ← rl_agent.py, contact_graph.py
    ↓ (forwarding decision)
Store-and-Forward Engine            ← forwarding_engine.py
    ↓ (custody, queuing, dispatch)
Convergence Layer Adapter           ← ltp.py, tcpcl.py, udp_cl.py
    ↓ (segment, transmit)
Underlying Link                     ← optical / RF channel
```

When a bundle arrives at a node, it flows **up** the stack: convergence layer reassembles segments → forwarding engine receives bundle → routing agent decides next action → (if delivered) application layer consumes payload.

### The Module 1 Walkthrough: Baseline DTN

`run_simulation.py` Module 1 is the integration test — it exercises the entire DTN stack end-to-end without RL or quantum security. Here is the flow:

**Step 1 — Topology Creation.** The simulation builds the 5-tier interplanetary topology:
- Tier 1: Earth DSN ground stations (Goldstone, Canberra, Madrid)
- Tier 2: GEO relay satellites
- Tier 3: Lagrange point relays (Earth-Sun L1/L2, Earth-Moon L2)
- Tier 4: Mars orbiters (MRO, MAVEN, TGO, ExoMars)
- Tier 5: Mars surface assets (rovers, landers)

Each node is a `Node` instance with: node_id, node_type, tier, position (3D coordinates), buffer_capacity, transmission_power, and a convergence layer stack.

**Step 2 — Contact Schedule.** A contact schedule is generated based on orbital mechanics. Each contact is a `Contact` object with start_time, end_time, data_rate, and one-way delay. Contacts are fed into the `ContactGraph`.

**Step 3 — Bundle Generation.** Science data bundles are generated at Mars surface nodes. Each bundle has: source (Mars rover), destination (Earth DSN), priority (P2 standard), payload (simulated instrument data), lifetime (7 days), and `CUSTODY_REQUESTED` flag set.

**Step 4 — Routing and Forwarding.** At each simulation tick:
1. Each node's `ForwardingEngine.tick()` is called.
2. Expired bundles are purged.
3. The queue is drained: for each bundle, a `NetworkState` is constructed and the routing agent is queried.
4. The agent returns a `RoutingDecision` (FORWARD/STORE/DROP/SPLIT).
5. The engine executes the decision: forwards via convergence layer, stores locally, drops, or fragments.
6. Forwarding events (`ForwardingEvent`) are logged for every action.

**Step 5 — Convergence Layer Transmission.** When a bundle is forwarded, the convergence layer adapter handles the actual transmission:
- For scheduled contacts with reliable links: **TCPCL** (RFC 7242) for session-based transmission.
- For deep-space links with long delays: **LTP** (RFC 5326) with red parts for reliable delivery, green parts for best-effort.
- For broadcast or low-overhead links: **UDP-CL** for best-effort.

**Step 6 — Custody Transfer.** When a bundle with `CUSTODY_REQUESTED` is forwarded, the receiving node sends a Custody Acceptance administrative record. The sending node releases custody and frees buffer. If no acceptance arrives within the retransmission window, the custodian retransmits.

**Step 7 — Delivery Confirmation.** When a bundle reaches its final destination, the `ForwardingEngine` marks it as delivered and generates a Delivery Confirmation. The simulation records delivery time, hop count, and path taken.

**Step 8 — Metrics Collection.** Module 1 collects: delivery ratio, average delay, hop count distribution, buffer occupancy over time, custody transfer count, and drop count. These metrics are the baseline against which RL routing (Module 3) and QKD security (Module 5) are compared.

### The Integration Review Checklist

When defending the integration, be ready to trace a single bundle through the entire stack:

1. **Creation:** Mars rover generates a 50 MB image bundle, priority P2, lifetime 7 days, `CUSTODY_REQUESTED`.
2. **Queuing:** Bundle enters the rover's `BundleQueue`, sorted by `(priority, deadline)`.
3. **Routing:** Engine calls `agent.select_action()`. Agent sees: buffer 30%, link to orbiter quality 0.7, destination Earth. Decision: FORWARD to MRO orbiter, confidence 0.8.
4. **Transmission:** Engine calls LTP adapter. Red segment (reliable). Bundle transmitted over the RF link during the contact window.
5. **Custody:** MRO accepts custody. Rover's buffer freed. `ForwardingEvent(CUSTODY_ACCEPTED)` logged.
6. **Next Hop:** MRO's engine routes bundle to Lagrange relay. LTP over optical link.
7. **Final Hop:** Lagrange relay forwards to Earth DSN. TCPCL over ground network.
8. **Delivery:** DSN marks delivered. Total path: Mars → MRO → Lagrange → Earth. 4 hops, ~24 minutes total delay.

## 🔬 In AETHERIX

The integration driver is `run_simulation.py` (562 lines) at the repository root. It runs **6 modules**:

| Module | Name | Purpose |
|--------|------|---------|
| 1 | Baseline DTN | End-to-end bundle delivery over 5-tier topology |
| 2 | Optical vs RF Link Budget | Compare data rates, delay, availability |
| 3 | RL Routing Convergence | Train RL agent, show improvement over baseline |
| 4 | Failure & Recovery | Inject node/link failures, show adaptive rerouting |
| 5 | QKD Security | Simulate BB84 key exchange, QBER monitoring |
| 6 | Radiation Hardening | Simulate SEU events, TMR correction |

**Module 1** (`simulate_baseline_dtn()`) creates the topology, contact schedule, and bundle workload, then runs the simulation loop:

```python
def simulate_baseline_dtn():
    # 1. Create topology
    topology = build_interplanetary_topology()
    # 2. Create contact schedule
    schedule = generate_contact_schedule(topology)
    # 3. Generate bundles at Mars nodes
    bundles = generate_bundle_workload(topology)
    # 4. Run simulation
    for tick in range(simulation_duration):
        for node in topology.nodes:
            node.forwarding_engine.tick(tick, topology.get_neighbors(node))
    # 5. Collect metrics
    return collect_metrics(topology)
```

Each node's `ForwardingEngine` is wired to: a `BundleQueue`, a `Node` (for buffer/battery state), an `RLRoutingAgent` (for decisions), and a `ContactGraph` (for fallback routing). The convergence layers (`LTPAdapter`, `TCPCLAdapter`, `UDPCLAdapter`) are attached based on link type.

The `collect_metrics()` function aggregates `ForwardingEvent` logs across all nodes to compute: delivery ratio, average end-to-end delay, hop count distribution, peak buffer occupancy, and custody transfer success rate.

## 📐 Key Numbers & Formulas
- **Topology tiers:** 5 (Earth DSN → GEO → Lagrange → Mars orbit → Mars surface)
- **Nodes in training topology:** 15
- **Baseline delivery ratio (Module 1):** typically 85–95% (no failures)
- **Average delay:** 20–40 minutes (Mars to Earth, multi-hop)
- **Bundle lifetime (science data):** 7 days (604,800 s)
- **Simulation modules:** 6
- **Integration trace:** Creation → Queue → Route → Transmit → Custody → Forward → Deliver
- **Convergence layers used:** LTP (deep-space), TCPCL (ground/relay), UDP-CL (broadcast)

## 🔗 Standards & References
- [RFC 9171 — Bundle Protocol v7](https://datatracker.ietf.org/doc/html/rfc9171)
- [CCSDS 734.0-G-1 — Mars Relay Network](https://public.ccsds.org/Pubs/734x0g1.pdf)
- [RFC 4838 — DTN Architecture (integration principles)](https://datatracker.ietf.org/doc/html/rfc4838)
- [NASA DTN Tutorials](https://www.nasa.gov/delay-tolerant-networking)

## 💡 How the Examiner Will Probe This

**Q: "Walk me through what happens when a Mars rover generates a science data bundle — trace it to Earth."**
→ The rover creates a BPv7 bundle with source=Mars rover, destination=Earth DSN, priority P2, CUSTODY_REQUESTED. It enters the priority queue sorted by (priority, deadline). The forwarding engine constructs a NetworkState and queries the RL agent, which decides FORWARD to the MRO orbiter (link quality 0.7, confidence 0.8). The LTP adapter transmits a red segment over RF. MRO accepts custody, freeing the rover's buffer. MRO's engine routes to the Lagrange relay via optical link. The relay forwards to Earth DSN via TCPCL. DSN marks delivered. Path: Mars→MRO→Lagrange→Earth, 4 hops, ~24 min delay.

**Q: "How do your convergence layers integrate with the forwarding engine?"**
→ Each node has a convergence layer adapter matched to its link type. When the engine executes a FORWARD decision, it calls `adapter.send_bundle(bundle, next_hop)`. The adapter handles segmentation (LTP red/green, TCPCL sessions, UDP-CL datagrams), transmission, and reassembly confirmation. The adapter notifies the engine on successful delivery (for custody release) or failure (for retransmission). The engine is convergence-layer-agnostic — it works with any adapter implementing the send/receive interface.

## ✅ What You Should Be Able to Answer After This Lesson
1. What are the 7 steps in the Module 1 baseline DTN simulation?
2. What are the 5 tiers in the interplanetary topology?
3. Trace a bundle from creation to delivery — name each layer it passes through.
4. What metrics does Module 1 collect, and why are they the baseline?
5. How does the ForwardingEngine integrate with the RL agent, ContactGraph, and convergence layers?

## 📂 Deep Dive Resources
- `run_simulation.py` — all 6 modules, especially `simulate_baseline_dtn()`
- `src/routing/forwarding_engine.py` — the integration hub
- `src/routing/node.py` — node model with convergence layer stack
- `src/routing/contact_graph.py` — CGR fallback
- `docs/DESIGN_RATIONALE.md` — integration architecture
- Live demo: [https://matx104.github.io/AETHERIX/](https://matx104.github.io/AETHERIX/)
