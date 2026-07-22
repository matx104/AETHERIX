# Day 19: Mars Orbital & Surface Assets

## 📅 Monday, August 10, 2026

## 🎯 Learning Objective

Describe AETHERIX's Tier 4 (Mars Orbital) and Tier 5 (Mars Surface) architecture, including areostationary relay orbit at 17,032 km, polar orbiter coverage, and the 177-node surface hierarchy of bases, rovers, drones, and sensors — mapping to exam Learning Objective 3.

## 📖 The Core Concept

Mars is where AETHERIX's network reaches its maximum depth — 181 nodes across orbital and surface tiers, representing the data generation frontier of the interplanetary network. Understanding these tiers requires grasping Mars-specific orbital mechanics and the hierarchical surface mesh design.

**Tier 4 — Mars Orbital (4 nodes):**

Mars, like Earth, has a geostationary-equivalent orbit — called **areostationary orbit**. At an altitude of exactly **17,032 km** above the Martian surface, a satellite's orbital period matches Mars's sidereal rotation period of 24.623 hours (88,642 seconds). From the surface, such a satellite appears fixed in the sky — no antenna tracking required. AETHERIX deploys **two areostationary relays** (`areo-alpha` and `areo-beta`) positioned at different longitudes (0° and 180°), providing continuous coverage to equatorial and mid-latitude surface bases.

The areostationary altitude is derived from Kepler's third law:

```
a = (μ_Mars × T² / 4π²)^(1/3)
```

where μ_Mars = 4.283×10¹³ m³/s² and T = 88,642 seconds. The result: an orbital radius of 20,428 km from Mars's centre, or 17,032 km above the 3,389.5 km Martian surface.

Areostationary orbit has limitations: it cannot cover polar regions (the satellites are over the equator), and at 17,032 km altitude, the link budget to surface assets is ~33 dB worse than a low Mars orbit at 400 km. AETHERIX addresses this with a **polar orbiter** (`polar-gamma`) that covers high latitudes with ~90-minute passes, and a **general-purpose Mars orbiter** (`mars-orbiter`). Together, these four Mars orbital nodes form a full mesh (K4) — every node connected to every other for maximum redundancy. They are the last reliable deep-space node before data descends to the surface, serving as the critical **custody anchor**.

**Tier 5 — Mars Surface (177 nodes):**

The surface tier is a hierarchical mesh:

- **2 Bases** (`base-jezero`, `base-oxia`): Named after real Mars landing sites (Jezero Crater, where Perseverance landed; Oxia Planum, ESA's ExoMars target). Bases are the surface aggregation points — 2,048 GB buffers, 10 Mbps UHF/X-band, 20,000 MIPS processing. They serve as local DTN hubs for nearby assets.

- **5 Rovers** (`rover-01`–`rover-05`): Mobile science platforms with 100 GB buffers, 2 Mbps UHF. Each rover is homed to a base in round-robin fashion. Rovers generate the highest-value science data but have the most constrained buffers and data rates.

- **10 Drones** (`drone-01`–`drone-10`): Aerial platforms (inspired by NASA's Ingenuity helicopter) with 50 GB buffers, 5 Mbps UHF. Drones bridge between bases and the sensor mesh — each drone parents a set of sensors.

- **160 Sensor nodes** (`sensor-001`–`sensor-160`): The leaf nodes — seismometers, weather stations, radiation monitors. Each has a tiny 10 GB buffer, 0.5 Mbps UHF, and 500 MIPS processing. Sensors connect to drones (not directly to bases or orbiters), forming a three-level hierarchy: sensors → drones → bases → orbiters.

**Why this hierarchy?** A flat mesh of 177 nodes would be unmanageable — every node would need to track 176 neighbors. The hierarchical design means a sensor only talks to its parent drone, which talks to its parent base, which talks to the areostationary relay overhead. This limits the state each node must maintain and concentrates buffer capacity where it's needed most.

## 🔬 In AETHERIX

In `src/orbital/topology.py`:

**Tier 4** (`_build_tier4()`): registers `areo-alpha`, `areo-beta`, `polar-gamma`, `mars-orbiter` — all with `_AREO_CAPS` (2,048 GB buffer, 100 Mbps, UHF/Ka/optical, `qkd_capable=True`). The K4 mesh is wired in `build_inter_tier_links()`:
```python
for i in range(len(mars_orbital)):
    for j in range(i + 1, len(mars_orbital)):
        self._link(mars_orbital[i], mars_orbital[j])
```

**Tier 5** (`_build_tier5()`): registers 2 bases (`_BASE_CAPS`), 5 rovers (`_ROVER_CAPS`), 10 drones (`_DRONE_CAPS`), and 160 sensors (`_SENSOR_CAPS`). The hierarchical wiring:
```python
self._link(base_ids[0], base_ids[1])           # bases linked
for i, rover in enumerate(rover_ids):
    self._link(base_ids[i % len(base_ids)], rover)  # rovers → bases (round-robin)
for i, drone in enumerate(drone_ids):
    self._link(base_ids[i % len(base_ids)], drone)  # drones → bases (round-robin)
for i, sensor in enumerate(sensor_ids):
    self._link(drone_ids[i % len(drone_ids)], sensor)  # sensors → drones (round-robin)
```

The 4→5 inter-tier link: every Mars orbiter connects to every base at UHF RF, 2 Mbps, 0.001s latency, 0.98 availability.

## 📐 Key Numbers & Formulas

| Asset | Count | Buffer (GB) | Max Rate (Mbps) | Bands |
|-------|------:|------------:|----------------:|-------|
| Areostationary relay | 2 | 2,048 | 100 | UHF, Ka, optical |
| Polar orbiter | 1 | 2,048 | 100 | UHF, Ka, optical |
| Mars orbiter | 1 | 2,048 | 100 | UHF, Ka, optical |
| Base | 2 | 2,048 | 10 | UHF, X |
| Rover | 5 | 100 | 2 | UHF |
| Drone | 10 | 50 | 5 | UHF |
| Sensor | 160 | 10 | 0.5 | UHF |
| **Tier 5 total** | **177** | | | |
| **Tier 4 + 5 total** | **181** | | | |

**Areostationary altitude:** h = (μ·T²/4π²)^(1/3) − R_Mars = 20,428 − 3,389.5 = **17,032 km**

## 🔗 Standards & References

- [CCSDS 401.0-B-30 — Radio Frequency and Modulation Systems](https://public.ccsds.org/Pubs/401x0b30.pdf) (UHF relay)
- [NASA Mars Relay Network](https://www.nasa.gov/mission_pages/mars/missions/)
- [JPL — Mars Telecommunications Orbiter ( heritage)](https://www.jpl.nasa.gov/)
- [Vallado — "Fundamentals of Astrodynamics" (2013), Ch. 3](https://www.amazon.com/Fundamentals-Astrodynamics-Applications-Technology-Mechanics/dp/1881883183)

## 💡 How the Examiner Will Probe This

**Q: "Why does AETHERIX use areostationary orbit instead of low Mars orbit for relay satellites?"**
Areostationary relays provide continuous, fixed-geometry coverage to surface bases — no tracking required, no handover between passes. A low Mars orbit relay at 400 km has a 2-hour period but only ~10 minutes of line-of-sight per pass. For DTN store-and-forward, either works, but areostationary simplifies the contact schedule. The trade-off: areostationary is farther (17,032 km vs 400 km), so the link budget is ~33 dB worse, and it doesn't cover poles. That's why AETHERIX also includes polar orbiters.

**Q: "How does the surface mesh hierarchy work?"**
Three levels: sensors report to drones (UHF, 0.5 Mbps), drones report to bases (UHF, 5 Mbps), bases uplink to areostationary relays (UHF, 10 Mbps). This limits neighbor state and concentrates buffer capacity. A sensor only tracks its parent drone, not the entire 177-node surface.

**Q: "What happens if an areostationary relay fails?"**
The rover's UHF link to the relay times out → the bundle stays in the rover's queue (store-and-forward by design). The polar orbiter `polar-gamma` passes overhead on its next orbit. The rover forwards to `polar-gamma`, which carries the bundle Earth-ward. DTN's whole premise is tolerating exactly this.

## ✅ Self-Check Questions

1. Derive the areostationary altitude from Kepler's third law. What is the result?
2. Why does a polar orbiter complement areostationary relays? What coverage gap does it fill?
3. How are rovers assigned to bases in the topology wiring? What algorithm is used?
4. Which surface asset has the smallest buffer, and what is its capacity?
5. Why do Mars orbital relays have `qkd_capable=True` alongside Lagrange relays?

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/topology.py` — `_build_tier4()`, `_build_tier5()`, `_AREO_CAPS`, `_BASE_CAPS`, `_ROVER_CAPS`, `_DRONE_CAPS`, `_SENSOR_CAPS`
- **Topic summary:** `interview_prep/topic_summaries/orbital_mechanics.md` — Areostationary Orbit section
- **Mock interview:** `interview_prep/practice/mock_interview.md` — Q8 follow-up
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §3.3 (areo-alpha failure scenario)
- **Cheat sheet:** `interview_prep/cheat_sheets/constants.md` — Mars Parameters
