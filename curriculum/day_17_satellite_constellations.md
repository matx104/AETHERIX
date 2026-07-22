# Day 17: Satellite Constellations & Inter-Satellite Links

## 📅 Saturday, August 08, 2026

## 🎯 Learning Objective

Describe AETHERIX's Tier 2 orbital architecture — three GEO relays plus a 48-satellite LEO laser constellation — and defend the inter-satellite link (ISL) strategy, connecting to exam Learning Objective 3 (Network Infrastructure).

## 📖 The Core Concept

Tier 2 of the AETHERIX topology is Earth's orbital aggregation layer. It comprises two very different satellite populations that serve complementary purposes: geostationary (GEO) relays for persistent, fixed-geometry coverage, and a LEO laser constellation for high-throughput inter-satellite routing.

**GEO Relays (3 nodes):** Three geostationary relays positioned over the Atlantic, Pacific, and Indian Oceans provide reliable Earth-segment routing. At 35,786 km altitude, GEO satellites orbit with a 24-hour period matching Earth's rotation — they appear stationary from the ground. This fixed geometry means no tracking is required for ground stations: point once, and the link is always there. GEO relays serve as the stable bridge between DSN ground stations (Tier 1) and the deep-space Lagrange relays (Tier 3). In `topology.py`, the three GEO relays form a triangle — each linked to the other two — providing redundant paths and eliminating single points of failure in the Earth orbital segment.

**LEO Laser Constellation (48 nodes):** A constellation of 48 low-Earth-orbit satellites arranged in 6 orbital planes of 8 satellites each (a Walker Delta constellation pattern). This configuration provides global coverage with overlapping footprints. Unlike GEO, LEO satellites are in constant motion — orbiting at roughly 7.5 km/s with orbital periods of about 90–100 minutes at their operational altitude (~1,200 km). The LEO constellation serves a fundamentally different purpose from Starlink or similar megaconstellations: it is not about providing broadband to Earth's surface. Instead, it provides **optical inter-satellite links (ISL)** that route data between DSN stations via space, bypassing terrestrial network dependencies.

**Why optical ISL?** Inter-satellite links in vacuum have no atmospheric attenuation — the ideal environment for laser communications. At 1–10 Gbps, LEO ISLs provide orders of magnitude more throughput than any Earth-to-space link. The AETHERIX topology wires the 48 LEO satellites as a ring (`leo[i] → leo[(i+1) mod 48]`), enabling data to traverse the constellation. Crucially, only every 12th LEO satellite (`leo_ids[::12]`) gets a direct optical link to a Lagrange relay — this bounds the 2→3 fan-out to 4 cross-links, preventing the deep-space tier from being overwhelmed by LEO traffic.

**Walker Delta pattern:** In a Walker Delta constellation, satellites in successive orbital planes are offset by a phase angle, creating a consistent geometric relationship between planes. The "Delta" pattern means the planes are arranged so that as one satellite sets below the horizon, another from an adjacent plane is rising — providing continuous coverage. For AETHERIX's purpose (ISL routing, not surface coverage), the 6-plane × 8-satellite arrangement ensures that multiple cross-plane optical links are always available.

**The ISL advantage:** By routing data through space rather than through terrestrial fibre, AETHERIX reduces latency for cross-continent DSN handoffs (a Goldstone-to-Canberra ISL path through the LEO mesh is shorter than a trans-Pacific fibre route when both stations need to coordinate). The LEO tier also provides a survivable routing layer — if terrestrial networks are congested or damaged, the orbital backbone continues functioning.

## 🔬 In AETHERIX

In `src/orbital/topology.py`, Tier 2 is built in `_build_tier2()`:

```python
# GEO relays
for node_id in ("geo-atlantic", "geo-pacific", "geo-indian"):
    self.register_node(DTNNode(node_type=NodeType.GEO_RELAY, tier=2, capabilities=_GEO_CAPS))

# LEO constellation
for i in range(1, 49):
    self.register_node(DTNNode(node_id=f"leo-{i:02d}", node_type=NodeType.LEO_SATELLITE,
                                tier=2, capabilities=_LEO_CAPS))
```

The `_GEO_CAPS` profile: 5,120 GB buffer, 150 Mbps max rate, Ka-band + optical, both optical and RF capable. The `_LEO_CAPS` profile is more constrained: 1,024 GB buffer, 100 Mbps max rate, **optical-only** (`rf_capable=False`) — these satellites communicate exclusively by laser, which is why they need ISL partners.

Intra-tier wiring in `build_inter_tier_links()`:
- **GEO triangle:** `self._link(geo_ids[0], geo_ids[1])`, `self._link(geo_ids[1], geo_ids[2])`, `self._link(geo_ids[2], geo_ids[0])`
- **LEO ring:** `for i in range(len(leo_ids)): self._link(leo_ids[i], leo_ids[(i+1) % len(leo_ids)])`
- **LEO→Lagrange cross-links:** only `leo_ids[::12]` (4 satellites) connect to Lagrange relays at 80 Mbps optical, 1.2s latency, 0.92 availability.

## 📐 Key Numbers & Formulas

| Parameter | GEO Relay | LEO Satellite |
|-----------|-----------|---------------|
| Count | 3 | 48 |
| Altitude | 35,786 km | ~1,200 km |
| Orbital period | 24 hours | ~90 min |
| Constellation pattern | Triangle (3-node mesh) | Walker Delta (6 planes × 8 sats) |
| Buffer | 5,120 GB | 1,024 GB |
| Max data rate | 150 Mbps | 100 Mbps |
| Bands | Ka + optical | Optical only |
| ISL data rate | 1–10 Gbps (ring mesh) | 1–10 Gbps (ring mesh) |
| LEO→Lagrange rate | 80 Mbps (every 12th sat) | — |

**GEO orbital period formula:** T = 2π√(a³/μ), where a is the orbital radius (Earth radius + altitude) and μ is Earth's gravitational parameter.

## 🔗 Standards & References

- [CCSDS 141.0-B-1 — Optical Communications Physical Layer](https://public.ccsds.org/Pubs/141x0b1.pdf)
- [Walker, J.G. — "Continuous Whole-Earth Coverage by Circular-Orbit Satellite Patterns" (1971)](https://ui.adsabs.harvard.edu/abs/1971rsms.36..821w)
- [Iridium constellation — heritage ISL architecture](https://www.iridium.com/)
- [NASA TDRSS — Tracking and Data Relay Satellite System](https://www.nasa.gov/mission_pages/tdrss/)

## 💡 How the Examiner Will Probe This

**Q: "Why not use a Starlink-style megaconstellation?"**
AETHERIX's LEO tier serves a different purpose: optical ISL between DSN sites, not global broadband. A megaconstellation adds mass and complexity for capability AETHERIX doesn't need. The selection criterion is DSN interconnection, not surface coverage. 48 satellites in 6 planes provide sufficient crosslinks.

**Q: "Why is the LEO→Lagrange link limited to every 12th satellite?"**
To bound fan-out. If all 48 LEO satellites connected to Lagrange relays, the deep-space tier would be overwhelmed. Selecting every 12th satellite (4 cross-links) provides redundancy while keeping the deep-space hop manageable.

**Q: "Why are LEO satellites optical-only?"**
In vacuum, optical links achieve Gbps rates with compact terminals. Adding RF capability would require additional mass, power, and antenna hardware for marginal benefit — the LEO constellation's job is ISL routing, which optical does best.

## ✅ Self-Check Questions

1. What is the difference in purpose between AETHERIX's GEO relays and its LEO constellation?
2. Why does the LEO ring use `(i+1) % 48` wrapping in the adjacency wiring?
3. How many LEO satellites have direct links to Lagrange relays, and why that number?
4. What data rates are achievable on LEO inter-satellite links, and what medium is used?
5. What is a Walker Delta constellation pattern, and why does it matter for coverage?

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/topology.py` — `_build_tier2()`, `_GEO_CAPS`, `_LEO_CAPS`, `build_inter_tier_links()` (LEO ring + cross-links)
- **Topic summary:** `interview_prep/topic_summaries/network_topology.md` — Intra-Tier Connectivity
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §9.2 (Why not a Starlink-style megaconstellation)
- **Cheat sheet:** `interview_prep/cheat_sheets/constants.md` — Network Parameters
