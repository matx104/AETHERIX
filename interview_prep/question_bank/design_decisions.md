# Design Decisions — 15 Questions with Detailed Answers

---

### DD1. Why use Reinforcement Learning instead of Contact Graph Routing?

**Question**: CGR is the established standard for DTN routing. Why replace it with RL?

**Answer**: CGR computes optimal routes over a pre-planned contact graph, but it has three limitations that matter for AETHERIX. First, it cannot adapt in real-time to unplanned events — a solar flare degrading a link or a node buffer filling up requires waiting for an updated schedule from Earth (12+ minutes stale). Second, CGR optimises for a single metric (typically minimum delay), while AETHERIX needs to balance delivery probability, latency, hop count, drop rate, and energy consumption simultaneously — the RL reward function `R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)` captures all five. Third, CGR cannot learn from experience; the RL agent improves its policy over the 780-day synodic period simulation, developing distance-phase-aware routing that no pre-planned schedule could encode.

**Trade-offs**: RL requires training time (hours of simulation before deployment) and has no optimality guarantee. If the RL agent's confidence drops below 0.3, AETHERIX falls back to CGR. The current demo uses Q-tables (limited state space); production would use DQN with experience replay.

---

### DD2. Why 1550 nm wavelength for the optical links?

**Question**: Why not 800 nm or 1064 nm, which are also used in space communications?

**Answer**: 1550 nm sits in the C-band, chosen for four reasons. First, telecom heritage — decades of terrestrial fibre-optic development have produced mature, cheap, and reliable components (laser diodes, modulators, detectors). Second, atmospheric transmission — 1550 nm is in an atmospheric absorption window with low scattering. Third, eye safety — 1550 nm is strongly absorbed by the cornea, preventing retinal damage at powers that would be hazardous at 800 nm. Fourth, detector options — both avalanche photodiodes (APDs, cheaper, ~10% quantum efficiency) and superconducting nanowire single-photon detectors (SNSPDs, expensive, ~80% QE) are available at this wavelength.

**Trade-offs**: 1550 nm has higher atmospheric scattering than 1064 nm in some conditions. The diffraction-limited beam divergence is wider than at shorter wavelengths (λ/D). However, the component maturity and eye safety outweigh these factors for AETHERIX's mission profile.

---

### DD3. Why a 5-tier network topology?

**Question**: Could you achieve the same with fewer tiers?

**Answer**: Each tier serves a distinct purpose that cannot be merged without losing capability. Tier 1 (Earth ground, 6 nodes) provides DSN integration and geographic diversity. Tier 2 (Earth orbital, 51 nodes: 3 GEO relays + 48 LEO laser mesh) handles atmospheric bypass and inter-station routing — without this, data from Canberra would need to traverse terrestrial networks to reach Goldstone, adding latency and failure modes. Tier 3 (deep space, 4 nodes at L4/L5) provides conjunction coverage and quantum relay — nothing else can maintain Earth-Mars connectivity when the Sun is between them. Tier 4 (Mars orbital, 4 nodes: 2 areostationary + 2 polar orbiters) provides Mars surface coverage. Tier 5 (Mars surface, 167 nodes) is the data source and sink. Removing any tier breaks a unique capability.

**Trade-offs**: More tiers mean more nodes (232 total), more complex contact scheduling, and more potential failure points. The RL agent's state space grows with network complexity. However, the tiered architecture localises failures — a Tier 5 rover failure does not affect Tier 1–3 operations.

---

### DD4. Why place relay satellites at Lagrange points ES-L4 and ES-L5?

**Question**: Why not use Mars orbit or a different relay strategy?

**Answer**: Three properties make ES-L4/ES-L5 unique. First, gravitational stability — objects at L4/L5 are in stable equilibrium (Trojan points), requiring near-zero station-keeping fuel over the mission lifetime. L1/L2 are unstable and need continuous correction. Second, conjunction coverage — at 60° ahead/behind Earth in its orbit, the L4/L5 relays have line-of-sight to Mars around the solar limb even during conjunction, providing 50–70% availability versus 0% for direct links. Third, intermediate distance — at ~1 AU from Earth, they split the deep-space link into two shorter hops with better link budgets. No Mars-orbit relay can solve the conjunction problem because the Sun-blocked geometry is on the Earth side.

**Trade-offs**: L4/L5 are ~150M km from Earth, so the relay satellite needs its own power, thermal, and communication systems — essentially a full deep-space mission. The 4-node deep-space tier (2× L4, 2× L5 with redundancy) adds significant launch and operations cost.

---

### DD5. Why hybrid optical/RF instead of optical-only?

**Question**: Optical has 10–100× the data rate. Why carry the mass and complexity of RF transceivers?

**Answer**: Optical links are weather-dependent — clouds completely block 1550 nm, and atmospheric turbulence causes 3–10 dB scintillation losses. A global cloud cover analysis shows any single optical ground site has ~60–70% clear-sky availability. With three spatially diverse sites, optical-only availability reaches ~90%, but still leaves 10% downtime unacceptable for emergency communications. RF (Ka-band) penetrates clouds and provides 99%+ availability at lower data rates (125 kbps–6 Mbps). The hybrid design uses optical for throughput and RF for reliability, achieving >95% combined availability. During normal operations, both links run simultaneously; the RL agent routes P0/P1 bundles via RF for guaranteed delivery and bulk data via optical for speed.

**Trade-offs**: Carrying both transceivers adds mass (~10–20 kg for Ka-band), power (20–100 W for RF), and complexity (two pointing systems). The hybrid approach is standard for all recent deep-space missions (e.g., NASA's DSOC co-flew with the RF system on Psyche).

---

### DD6. Why use both QKD and post-quantum cryptography?

**Question**: Isn't one layer of quantum-safe security sufficient?

**Answer**: They address different threat models. QKD provides information-theoretic security — the key exchange is guaranteed secure by the laws of physics, not by computational assumptions. However, QKD requires dedicated hardware (single-photon sources, detectors), line-of-sight, and has very low key rates at interplanetary distances (1–10 bps). PQC (ML-KEM, ML-DSA) provides computational security on classical hardware, works over any channel, and handles authentication (which QKD alone cannot). The combination is defence-in-depth: if the quantum channel is unavailable (weather, equipment failure), ML-KEM handles key exchange. If lattice-based cryptography is compromised, QKD keys are unaffected. ML-DSA provides authentication for every bundle regardless of which key exchange method was used.

**Trade-offs**: Dual-layer security adds protocol complexity and computational overhead. ML-DSA signatures are 2.5–4.6 KB, adding overhead to every bundle. The RL agent must account for this when making SPLIT decisions.

---

### DD7. Why start with Q-learning before moving to Deep Q-Network (DQN)?

**Question**: DQN is more powerful. Why begin with the simpler approach?

**Answer**: Q-learning with a Q-table is the correct starting point for three reasons. First, interpretability — every Q-value is inspectable: "from node X, the best action when buffer is 80% full and link quality is 0.6 is STORE." This is essential for a research project where the student must explain and justify the agent's behaviour. A neural network is a black box. Second, rapid iteration — training a Q-table takes seconds to minutes on a laptop, versus hours for DQN. This allows fast experimentation with reward function parameters (α, β, γ, δ, ε). Third, the state space for the demo is manageable — AETHERIX's 232 nodes with discretised state variables fit in a Q-table.

**Trade-offs**: Q-tables don't scale — a production deployment with continuous state variables would need DQN or PPO. The transition plan is documented: replace the Q-table with a neural network, add experience replay, and use target networks for stability. The demo's Q-learning validates the reward function design and proves the concept before investing in DQN.

---

### DD8. Why 232 nodes in the network simulation?

**Question**: How was this number determined?

**Answer**: The 232 nodes are derived bottom-up from the mission requirements. Tier 5 (Mars surface, 167 nodes) is sized for a mature Mars exploration scenario: 5 major bases (each with a hub), 20 rovers, 40 fixed science stations, 50 drones, and 52 sensor nodes. Tier 4 (Mars orbital, 4 nodes) has 2 areostationary relays and 2 polar orbiters — the minimum for global Mars coverage. Tier 3 (deep space, 4 nodes) has 2 primary + 2 backup Lagrange relays. Tier 2 (Earth orbital, 51 nodes) has 3 GEO relays plus a 48-satellite LEO laser constellation (6 orbital planes × 8 satellites, similar to proposed laser-comm constellations). Tier 1 (Earth ground, 6 nodes) has 3 RF (DSN) and 3 optical ground stations.

**Trade-offs**: 232 nodes creates a large state space for the RL agent. The current Q-table discretises state variables to keep the table tractable. A smaller network (e.g., 50 nodes) would train faster but wouldn't represent a realistic Mars exploration scenario.

---

### DD9. Why use LTP as the primary convergence layer for deep-space hops?

**Question**: Why not just use UDP with application-layer reliability?

**Answer**: LTP provides three capabilities that UDP-CL lacks. First, structured retransmission — LTP's report segments (RS) precisely identify which data blocks arrived and which need retransmission, minimising redundant data over expensive deep-space links. Second, red/green differentiation — within a single session, some blocks can be reliable (red, for commands) and others best-effort (green, for science), without establishing separate connections. Third, LTP is designed for the timing characteristics of deep space — its timers default to minutes/hours, not milliseconds. Building equivalent reliability over UDP would essentially mean reimplementing LTP poorly. RFC 5326 already solved this problem.

**Trade-offs**: LTP is more complex to implement than UDP-CL. ION-DTN provides a reference implementation, but for AETHERIX's custom simulation, the LTP behaviour is modelled rather than fully implemented.

---

### DD10. Why 5 priority levels for bundles?

**Question**: RFC 9171 defines only 3 priority classes (bulk, normal, expedited). Why add more?

**Answer**: AETHERIX expands to 5 levels to better differentiate latency requirements in the Mars exploration scenario. RFC 9171's three classes are coarse — "expedited" covers everything from immediate safety alerts (must arrive in minutes) to high-value science observations (should arrive within 30 minutes). Splitting into P0 (Emergency, <1 min) and P1 (High Science, <30 min) allows the RL agent to make finer routing decisions: P0 bundles pre-empt everything and use the most reliable path (RF + LTP red + custody), while P1 bundles use the fastest available path (optical + LTP green + custody). Similarly, splitting P3 (Housekeeping, <7 days) from P4 (Bulk, <30 days) prevents low-priority status logs from competing with genuine bulk transfers like software updates.

**Trade-offs**: More priority levels increase scheduling complexity. The RL agent must learn differentiated policies for each level. In practice, P0 and P1 are the critical distinctions — P3/P4 could share a queue without significant performance loss.

---

### DD11. Why use CBOR encoding in BPv7 instead of Protocol Buffers or JSON?

**Question**: There are many serialisation formats. Why CBOR?

**Answer**: CBOR (Concise Binary Object Representation, RFC 8949) was chosen by the IETF DTN Working Group for BPv7 for three reasons. First, compact binary encoding — a CBOR-encoded bundle primary block is smaller than JSON or XML, saving bandwidth on expensive deep-space links. Second, deterministic encoding — CBOR has a well-defined canonical form, essential for cryptographic hashing (bundle integrity checks). Third, self-describing — CBOR includes type information, allowing forward-compatible extension blocks. Protocol Buffers were considered but require a pre-shared schema, which is problematic when endpoints may not have had contact for days. CBOR is specified by RFC 9171; AETHERIX follows the standard rather than making a custom choice.

**Trade-offs**: CBOR is less human-readable than JSON. Debugging requires hex dumps or CBOR decoders. The trade-off favours efficiency over readability for a deployed system.

---

### DD12. Why a 48-satellite LEO constellation in the Earth orbital tier?

**Question**: Why not use existing communications satellites or a smaller constellation?

**Answer**: The 48-satellite constellation (6 planes × 8 satellites) serves a specific purpose: optical inter-satellite links (ISL) between DSN ground stations. DSN stations in Goldstone, Madrid, and Canberra are on different continents. Terrestrial fibre routes between them add latency (100–300 ms) and are not under AETHERIX's control. The LEO laser mesh routes data between DSN stations via space in <20 ms per hop, with 1–10 Gbps ISL capacity. 48 satellites in 6 planes ensures at least one satellite is visible from any DSN station at all times with inter-plane crosslinks. This is similar in concept to Starlink's laser mesh but with fewer satellites because the connectivity requirement (3 ground stations) is much less demanding than global coverage.

**Trade-offs**: 48 satellites is a significant constellation to deploy. A simpler alternative is 3 GEO relays (one per DSN station), which provides the same inter-station routing with fewer assets but at the cost of higher latency (GEO hop is 240 ms) and single-point-of-failure per station. AETHERIX uses both: 3 GEO relays for reliability plus 48 LEO satellites for high-throughput ISL routing.

---

### DD13. Why is the RL reward function weighted with those specific values?

**Question**: α=1.0, β=0.001, γ=0.1, δ=10.0, ε=0.01 — how were these determined?

**Answer**: The weights encode AETHERIX's operational priorities. α=1.0 (delivery reward) is the primary objective — a bundle must be delivered. δ=10.0 (drop penalty) is an order of magnitude larger than the delivery reward because dropping a bundle represents total failure (the data is lost), whereas successful delivery is the baseline expectation. β=0.001 per second means a 12-hour delay costs 0.001 × 43,200 = 43.2 penalty points — significant enough to prefer faster routes but not so large that the agent takes risky shortcuts. γ=0.1 per hop discourages unnecessary intermediate stops (each hop adds custody overhead and failure risk). ε=0.01 per Wh keeps energy consumption in check without dominating the decision — a 5 W laser transmitting for 1 hour costs 0.01 × 5 = 0.05 penalty. These values were tuned empirically during simulation.

**Trade-offs**: The weights are scenario-dependent. During a dust storm, ε might need to increase (power is scarce). During conjunction, β might decrease (delays are unavoidable). A production system would use dynamic weight adjustment based on current conditions — this is a planned enhancement.

---

### DD14. Why deploy quantum repeaters only at Lagrange points rather than in Mars orbit?

**Question**: Mars orbit is closer to Mars surface assets. Wouldn't that be more useful?

**Answer**: Quantum repeaters extend entanglement range. The bottleneck for Earth-Mars QKD is not the Mars-surface-to-Mars-orbit hop (17,032 km, easily covered by direct BB84) — it's the 54–401 million km deep-space hop. Placing repeaters at ES-L4/ES-L5 splits this into two segments of ~150M km each, which is still extremely challenging but more tractable than 400M km direct. Mars-orbit quantum repeaters would only help with the short-range Mars-local hops, which don't need repeaters. Additionally, the Lagrange relay satellites already exist for classical communication — co-locating quantum payloads avoids launching dedicated spacecraft.

**Trade-offs**: The Lagrange repeaters don't help with the Mars-side quantum links. If future Mars surface assets needed QKD between distant bases (e.g., 500+ km apart), Mars-orbit repeaters would be needed. This is not in the current design scope.

---

### DD15. Why simulate over the full 780-day synodic period rather than a shorter window?

**Question**: Training the RL agent for 780 simulated days is computationally expensive. Why not train on a representative 30-day window?

**Answer**: The Earth-Mars distance varies by a factor of 7.3× (54.6M to 401M km) over the synodic period, and the communication conditions change dramatically: data rates from 200 Mbps to 2 Mbps, light-time from 3 to 22 minutes, and the conjunction blackout around the midpoint. A 30-day window captures only a narrow slice of these conditions. An agent trained only at opposition (short delay, high bandwidth) would learn to always forward immediately — a catastrophic policy during conjunction when no direct link exists. Similarly, an agent trained only during conjunction would over-store, wasting contact windows at opposition. The full 780-day training ensures the policy is robust across all conditions.

**Trade-offs**: Longer training consumes more compute. The Q-table approach mitigates this because tabular Q-learning converges faster than DQN. For the DQN upgrade, techniques like prioritised experience replay and curriculum learning (starting with easy opposition scenarios before introducing conjunction) would reduce training time.
