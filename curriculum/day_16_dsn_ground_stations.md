# Day 16: DSN Integration & Ground Stations

## 📅 Friday, August 07, 2026

## 🎯 Learning Objective

Explain how AETHERIX integrates with NASA's Deep Space Network, describe the three DSN complexes and their 120° spacing strategy, and articulate why ION-DTN makes the integration transparent — mapping to exam Learning Objective 3 (Network Infrastructure).

## 📖 The Core Concept

NASA's Deep Space Network (DSN) is the backbone of interplanetary communication. Without it, no spacecraft beyond Earth orbit could communicate. The DSN consists of three complexes strategically placed 120° apart in longitude: **Goldstone** (California, USA, ~243°E), **Madrid** (Robledo, Spain, ~355°E), and **Canberra** (Australia, ~149°E). This spacing ensures that at least one complex always has any deep-space target above the horizon — Earth's rotation continuously brings a new station into view as another sets.

Each complex houses multiple antennas: a single 70-meter dish (the largest, for the faintest signals) and several 34-meter dishes that can be arrayed together for additional gain. The 70-meter antennas — DSS-14 at Goldstone, DSS-63 at Madrid, DSS-43 at Canberra — are the workhorses for distant missions at maximum Mars range (401 million km), where the received signal is in the attowatt regime.

AETHERIX integrates with the DSN at the convergence-layer level. The critical insight is that AETHERIX uses CCSDS-compliant BPv7 bundles — the same bundle format the DSN already routes via ION-DTN (Interplanetary Overlay Network), JPL's reference BPv7 implementation. This means **any DSN station running ION-DTN can route AETHERIX bundles without modification**. The integration point is clean: deep-space links use LTP (Licklider Transmission Protocol) convergence layer; Earth-side links from DSN stations to the Mission Operations Center use TCPCL (TCP Convergence Layer).

Beyond the traditional RF infrastructure, AETHERIX adds **optical ground stations** co-located near existing DSN complexes. These require: high-altitude sites with low atmospheric turbulence, 1-meter-plus receiving telescopes, adaptive optics to correct wavefront distortion, and superconducting nanowire single-photon detectors (SNSPDs) for photon-counting reception. The optical physical layer follows CCSDS 141.0-B-1, the international standard for optical communications coding and synchronization.

The 70-meter and 34-meter RF dishes continue serving Ka-band links as backup to optical. This dual ground infrastructure — RF at the DSN, optical at co-located facilities — gives AETHERIX the weather diversity it needs. When clouds block optical reception at one site, the RF link still works, and vice versa.

Endpoint identification across the network follows CCSDS 142.0-B-2 (LNISS v5), ensuring unique addressing that interoperates with any future interplanetary network such as LunaNet. This standards-first approach means AETHERIX does not compete with the DSN — it **complements** it, adding optical capability and intelligent routing on top of existing RF infrastructure.

## 🔬 In AETHERIX

In `src/orbital/topology.py`, the three DSN stations are registered in `_build_tier1()`:

```python
for node_id in ("dsn-goldstone", "dsn-madrid", "dsn-canberra"):
    self.register_node(DTNNode(
        node_id=node_id,
        node_type=NodeType.GROUND_STATION,
        tier=1,
        capabilities=_DSN_CAPS,
    ))
```

The `_DSN_CAPS` configuration is the most capable node profile in the network: a 10,240 GB (10 TB) buffer, 200 Mbps maximum data rate, support for all four bands (S, X, Ka, optical), both `optical_capable=True` and `rf_capable=True`, and 50,000 MIPS of processing power. The enormous buffer is deliberate — DSN stations are the endpoints that absorb burst traffic and never become the bottleneck.

Two additional Tier 1 nodes — `earth-moc` (Mission Operations Center) and `earth-soc` (Science Operations Center) — handle operations management. These have slightly reduced capabilities (`optical_capable=False`, supporting X-band and Ka-band only) but share the same 10 TB buffer and 200 Mbps data rate.

The inter-tier link from Tier 1 to Tier 2 (`build_inter_tier_links()`) connects every DSN station to every GEO relay with Ka-band RF at 10 Mbps, 0.01 seconds latency, and 0.995 availability — the highest-availability link in the entire topology, reflecting the short, reliable nature of the Earth-side hop.

## 📐 Key Numbers & Formulas

| DSN Parameter | Value |
|---------------|-------|
| Number of complexes | 3 (Goldstone, Madrid, Canberra) |
| Longitude spacing | ~120° apart |
| Largest dishes | 70 m (DSS-14, DSS-63, DSS-43) |
| Standard dishes | 34 m (arrayable for higher gain) |
| AETHERIX DSN buffer | 10,240 GB (10 TB) per node |
| AETHERIX DSN max rate | 200 Mbps |
| AETHERIX DSN bands | S, X, Ka, optical |
| Tier 1→2 link availability | 0.995 (highest in topology) |
| Optical ground station aperture | ≥1 m telescope + adaptive optics |

## 🔗 Standards & References

- [CCSDS 141.0-B-1 — Optical Communications Physical Layer](https://public.ccsds.org/Pubs/141x0b1.pdf)
- [CCSDS 142.0-B-2 — Space Link Identifiers (LNISS v5)](https://public.ccsds.org/Pubs/142x0b2.pdf)
- [RFC 9171 — Bundle Protocol Version 7](https://datatracker.ietf.org/doc/html/rfc9171) (ION-DTN reference implementation)
- [RFC 5326 — Licklider Transmission Protocol](https://datatracker.ietf.org/doc/html/rfc5326)
- [ION-DTN — JPL Open Source](https://github.com/nasa-jpl/ION-DTN)
- [NASA DSN — Deep Space Network](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/deep-space-network/)

## 💡 How the Examiner Will Probe This

**Q: "How does AETHERIX integrate with the existing DSN?"**
Answer: AETHERIX uses CCSDS-compliant BPv7 bundles, so any DSN station running ION-DTN routes AETHERIX bundles natively. The integration point is the convergence layer — LTP for deep-space links, TCPCL for Earth-side. AETHERIX adds optical ground stations co-located near DSN complexes following CCSDS 141.0-B-1. Endpoint IDs follow LNISS v5 for cross-network interoperability.

**Q: "Does AETHERIX compete with the DSN or complement it?"**
Complement. The DSN remains the primary RF ground segment. AETHERIX adds optical capability, space-based relay infrastructure, and intelligent RL routing on top. No existing DSN functionality is replaced.

**Q: "What happens if one DSN complex goes offline?"**
The other two maintain coverage. At 120° spacing, any two complexes can cover the sky with brief gaps. This is the geographic diversity principle — the same idea that drives the three-site optical diversity strategy.

## ✅ Self-Check Questions

1. Why are the three DSN complexes spaced 120° apart in longitude?
2. What is the largest DSN antenna diameter, and why is it needed at maximum Mars distance?
3. What CCSDS standard governs the optical communications physical layer, and what governs endpoint identification?
4. How does ION-DTN enable transparent integration without modifying existing DSN operations?
5. Why does the `_DSN_CAPS` profile include the largest buffer (10 TB) in the entire topology?

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/topology.py` — `_build_tier1()`, `_DSN_CAPS`
- **Topic summary:** `interview_prep/topic_summaries/space_challenges.md` — DSN Architecture section
- **Mock interview:** `interview_prep/practice/mock_interview.md` — Q9 (DSN Integration)
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §9.1 (Why not DTN over pure TCP)
- **External:** NASA DSN Now — [https://eyes.nasa.gov/dsn/](https://eyes.nasa.gov/dsn/) (live antenna status)
