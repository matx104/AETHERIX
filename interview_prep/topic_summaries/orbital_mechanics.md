# Orbital Mechanics — Topic Summary

## Keplerian Orbital Elements

Six parameters define any orbit (implemented in `src/orbital/contact_windows.py` as `OrbitalElements`):

| Element | Symbol | Earth | Mars |
|---------|--------|-------|------|
| Semi-major axis | a | 1.000 AU | 1.524 AU |
| Eccentricity | e | 0.0167 | 0.0934 |
| Inclination | i | 0.00005° | 1.850° |
| Right ascension of ascending node | Ω | −11.26° | 49.58° |
| Argument of periapsis | ω | 102.95° | 286.50° |
| Mean anomaly at epoch | M | 100.46° | 19.41° |

The orbital radius at any point: `r = a(1 − e²) / (1 + e·cos(θ))`, where θ is the true anomaly.

Mars's eccentricity (0.0934) is significantly higher than Earth's (0.0167), which means the Earth-Mars distance varies more than a simple circular-orbit model would predict.

## Synodic Period and Distance Cycle

The Earth-Mars synodic period is **779.94 days** (≈780 days), derived from:

```
1/P_synodic = |1/P_earth − 1/P_mars| = |1/365.25 − 1/686.98|
```

Over one synodic period, the Earth-Mars distance cycles through:

| Phase | Distance | One-Way Light Time | Communication Quality |
|-------|----------|--------------------|-----------------------|
| Opposition (closest) | 54.6M km | 3.0 min | Best — max data rate |
| Quadrature | ~225M km | 12.5 min | Average |
| Conjunction (farthest, Sun between) | 401M km | 22.3 min | Worst — solar interference |

AETHERIX simulations should cover at least one full synodic period (780 days) to capture the complete distance variation. The RL routing agent trains across this cycle to learn distance-adaptive policies.

## Contact Windows

A contact window is the interval during which two nodes have line-of-sight with acceptable geometry. For AETHERIX:

- **Earth-Mars direct**: 6–12 hours/day depending on orbital geometry and ground station visibility.
- **DSN coverage**: Three stations at 120° longitude spacing (Goldstone, Madrid, Canberra) ensure at least one station has Mars above the horizon at any time.
- **Mars surface-to-orbital**: Areostationary relays provide continuous coverage to equatorial bases; polar orbiters cover high latitudes with ~90-minute passes.
- **LEO constellation**: 48 satellites in the Earth orbital tier provide inter-satellite links (ISL) at 1–10 Gbps, routing data between DSN stations via optical crosslinks.

Contact prediction in AETHERIX uses SGP4/SDP4 for real-time propagation (TLE-based) and JPL Horizons for mission planning (high-precision ephemeris). The `predict_contact_windows()` function in `src/orbital/contact_windows.py` returns windows as `(start_time, end_time, max_data_volume)` tuples.

## Doppler Shift

Relative motion between Earth and Mars causes a frequency shift:

```
Δf/f₀ = v_radial / c
```

- Maximum Earth-Mars radial velocity: ~24 km/s.
- At 1550 nm (193.4 THz): Δf ≈ 15 GHz shift.
- For coherent optical detection (used in AETHERIX's deep-space links), this requires real-time frequency tracking with a phase-locked loop or digital compensation.
- RF links (Ka-band, ~32 GHz) experience ~2.5 GHz Doppler — easier to compensate but lower data rates.

Doppler is not just a nuisance — the rate of change of Doppler (Doppler rate) provides orbit determination data. AETHERIX uses predicted Doppler from orbital propagation to pre-compensate transmission frequency, reducing acquisition time at the receiver.

## Light-Time Calculation

One-way light time (OWLT): `t = d / c`, where c = 299,792.458 km/s.

| Distance | OWLT |
|----------|------|
| 54.6M km (min) | 3.0 min |
| 225M km (avg) | 12.5 min |
| 401M km (max) | 22.3 min |
| 1 AU | 8.3 min |

Round-trip light time (RTLT) is double these values: 6 to 44 minutes.

This has a fundamental implication for any real-time protocol: a command sent from Earth takes 3–22 minutes to arrive, and confirmation takes another 3–22 minutes to return. AETHERIX's RL agent must make routing decisions with state information that is always 3–22 minutes stale, which is why the agent's reward function penalises delay (β = 0.001 per second) to favour timely delivery over shortest-path routing.

## Areostationary Orbit

Mars's equivalent of geostationary orbit:

- Altitude: **17,032 km** above Mars surface.
- Orbital period: **24.623 hours** (one Mars sidereal day).
- Appears stationary over a point on the Martian equator.
- AETHERIX deploys **2 areostationary relays** at 0° and 180° longitude, providing continuous coverage to equatorial and mid-latitude surface assets.

The areostationary altitude is derived from Mars's gravitational parameter (μ_Mars = 4.283×10¹³ m³/s²) and sidereal rotation period (88,642 seconds) using Kepler's third law: `a = (μ·T²/(4π²))^(1/3)`.

## Solar Conjunction Handling

Approximately every 780 days, Earth and Mars are on opposite sides of the Sun (conjunction). The Sun's radio noise and coronal plasma disrupt direct RF and optical links for ~2 weeks.

AETHERIX conjunction strategy:
1. **T-14 days**: Pre-position critical uploads (software updates, command sequences).
2. **T-7 days**: Activate Lagrange-point relay path (ES-L4/ES-L5 at 60° offset).
3. **T-0 to T+14 days**: Autonomous operations. Mars assets execute pre-loaded command sequences. All data stored locally.
4. **T+14 days**: Resume direct links. Transmit stored backlog.
5. **Throughout**: Lagrange relays maintain 50–70% availability via the indirect path.

The Lagrange relays work because ES-L4 and ES-L5 are 60° ahead/behind Earth in its orbit — even when the direct Earth-Mars line passes behind the Sun, the L4/L5 relays have line-of-sight to both planets around the solar limb.

---

## Practice Questions

### Q1. "Calculate the free-space path loss for a 1550 nm optical link at Mars opposition (54.6M km)."

```
FSPL = 20·log₁₀(4π·d/λ)
     = 20·log₁₀(4π × 54.6×10⁹ / 1.55×10⁻⁶)
     = 20·log₁₀(4.43×10¹⁷)
     = 20 × 17.646
     = 352.9 dB
```

At average distance (225M km), FSPL ≈ 365.2 dB. At aphelion (401M km), FSPL ≈ 370.2 dB. This 17 dB variation over the synodic period is why AETHERIX's data rate ranges from 200 Mbps (opposition) to 2 Mbps (aphelion) — a factor of 50.

### Q2. "Why does AETHERIX use areostationary orbit instead of low Mars orbit for relay satellites?"

Areostationary relays provide continuous, fixed-geometry coverage to surface bases — no tracking required, no handover between passes. A low Mars orbit relay at 400 km altitude has a 2-hour period but only ~10 minutes of line-of-sight per pass to any given surface point. For DTN store-and-forward, either works, but areostationary simplifies the contact schedule (always-on vs. scheduled passes). The trade-off: areostationary is farther (17,032 km vs 400 km), so the link budget is ~33 dB worse, and it doesn't cover polar regions. That's why AETHERIX also includes polar orbiters for high-latitude coverage.

### Q3. "How does the synodic period affect your RL agent's training?"

The RL agent trains over one or more complete 780-day synodic cycles to experience the full range of conditions: opposition (short delay, high bandwidth), quadrature (medium), conjunction (long delay, low bandwidth, solar interference). If training only covered the opposition phase, the agent would learn policies that fail during conjunction — always forwarding immediately rather than storing for later. AETHERIX's contact window predictions (`predict_contact_windows()`) feed the simulation environment with time-varying topology, forcing the agent to learn when to store vs. forward. The Q-table entries are indexed by `(node, neighbor_link_quality, buffer_occupancy, bundle_priority, distance_phase)` where distance_phase discretises the synodic cycle.

### Q4. "What is the Doppler shift at Ka-band (32 GHz), and how do you compensate?"

At 32 GHz with v_radial = 24 km/s: Δf = f₀ × v/c = 32×10⁹ × 24,000/299,792,458 = 2.56 GHz. This is 6% of the carrier frequency — enormous. Compensation requires: (1) predicted Doppler from orbital propagation (SGP4/JPL Horizons) to pre-shift the transmit frequency, (2) a phase-locked loop at the receiver for residual tracking, (3) for optical links at 193.4 THz, the shift is ~15 GHz, compensated by tunable lasers with ~10 GHz tuning range. AETHERIX uses pre-compensation based on orbital prediction, reducing the residual Doppler to within the receiver's tracking bandwidth.

### Q5. "How do you predict contact windows, and what determines their duration?"

Contact windows are predicted by propagating the orbits of both endpoints and computing line-of-sight geometry. For Earth ground stations: the station must have Mars above a minimum elevation angle (typically 10° for RF, 20–30° for optical to reduce atmospheric path length). The window opens when Mars rises above this angle and closes when it sets — typically 6–12 hours depending on Mars's declination relative to the station's latitude. AETHERIX uses SGP4 (for LEO assets with TLE inputs) and JPL Horizons API (for planetary positions) via `src/orbital/contact_windows.py`. The output includes: `(start_time, end_time, max_data_volume)` where max_data_volume = data_rate × window_duration × link_efficiency. The RL agent uses these predictions to schedule bundle forwarding, prioritising bundles with approaching deadlines.

## Celestial Body Database

AETHERIX maintains a celestial body database with orbital parameters and derived velocities for all bodies relevant to the Earth-Mars link:

| Body | Semi-major Axis (AU) | Orbital Period (days) | Mean Orbital Velocity (km/s) | Eccentricity | Inclination to Ecliptic |
|------|---------------------|-----------------------|-------------------------------|--------------|------------------------|
| Earth | 1.000 | 365.25 | 29.78 | 0.0167 | 0.00° |
| Mars | 1.524 | 686.98 | 24.07 | 0.0934 | 1.85° |
| Moon | 0.00257 (from Earth) | 27.32 | 1.02 | 0.0549 | 5.14° |
| Phobos | 0.0000628 (from Mars) | 0.319 | 2.14 | 0.0151 | 1.08° |
| Deimos | 0.000157 (from Mars) | 1.263 | 1.35 | 0.0002 | 1.79° |

Orbital velocities are derived from `v = √(μ/r)` for circular approximation, where μ is the body's gravitational parameter and r is the orbital radius. For eccentric orbits, the velocity varies between periapsis `v_p = √(μ(1+e)/(a(1-e)))` and apoapsis `v_a = √(μ(1-e)/(a(1+e)))`.

The maximum relative radial velocity between Earth and Mars is approximately 24 km/s, occurring near quadrature when the velocity vectors are partially aligned with the line connecting the two planets. This value is critical for Doppler shift calculations and determines the required frequency tracking bandwidth.

## Doppler Shift Calculator

AETHERIX's Doppler shift calculator (implemented in `src/orbital/contact_windows.py`) computes both classical and relativistic frequency shifts for any transmitter-receiver pair.

### Classical Doppler Shift

```
Δf_classical = f₀ × (v_radial / c)
```

Where `v_radial` is the radial component of the relative velocity (positive when separating). This is the first-order approximation valid when `v << c`.

### Relativistic Doppler Shift

For the precision required in coherent optical detection, the full special-relativistic formula is used:

```
f_observed = f₀ × √((1 − β) / (1 + β))
```

Where `β = v_radial / c`. The relativistic correction is small but measurable: at v = 24 km/s, the difference between classical and relativistic predictions is ~0.5 Hz at 193.4 THz — within the tracking bandwidth of modern coherent receivers but significant for long-integration-phase measurements.

### Doppler Rate

The rate of change of Doppler (Doppler rate) is equally important:

```
d(Δf)/dt = f₀ × (a_radial / c)
```

Where `a_radial` is the radial acceleration. For Earth-Mars, Doppler rate can reach ~100 Hz/s at Ka-band, requiring the receiver's phase-locked loop to track frequency sweeps. AETHERIX pre-compensates both Doppler shift and Doppler rate at the transmitter based on predicted orbital state, reducing residual tracking burden.

### Doppler by Link Type

| Link Type | Carrier Frequency | Max Doppler Shift | Max Doppler Rate | Compensation Method |
|-----------|-------------------|-------------------|------------------|---------------------|
| Optical (1550 nm) | 193.4 THz | ±15.5 GHz | ~60 kHz/s | Tunable laser + digital PLL |
| Ka-band RF | 32.0 GHz | ±2.56 GHz | ~10 kHz/s | Frequency synthesiser + PLL |
| UHF RF | 0.40 GHz | ±32 MHz | ~130 Hz/s | Fixed-frequency with autotrack |

## Full 241-Node Topology with Inter-Tier Links

The AETHERIX network comprises 241 nodes (updated from 232 after adding 9 relay spares) across 5 tiers with defined inter-tier and intra-tier links:

### Node Distribution

| Tier | Name | Nodes | Composition |
|------|------|-------|-------------|
| T1 | Earth Ground | 6 | 3 DSN RF stations + 3 optical ground stations |
| T2 | Earth Orbital | 51 | 3 GEO relays + 48 LEO laser mesh (6 planes × 8 sats) |
| T3 | Deep Space Transit | 4 | 2× ES-L4 relay (primary + spare) + 2× ES-L5 relay |
| T4 | Mars Orbital | 4 | 2 areostationary relays + 2 polar orbiters |
| T5 | Mars Surface | 176 | 5 base hubs + 20 rovers + 40 science stations + 50 drones + 61 sensor nodes |
| **Total** | | **241** | |

### Inter-Tier Links

| Link | Tiers | Technology | Data Rate | Typical Delay |
|------|-------|-----------|-----------|---------------|
| Ground ↔ GEO | T1 ↔ T2 | Optical uplink + Ka-band RF | 1–10 Gbps / 6 Mbps | 240 ms RTT |
| Ground ↔ LEO | T1 ↔ T2 | Optical downlink + Ka-band RF | 1–10 Gbps / 6 Mbps | 4 ms RTT |
| GEO ↔ L4/L5 | T2 ↔ T3 | Optical deep-space | 50–200 Mbps | 8–15 min OWLT |
| LEO ↔ L4/L5 | T2 ↔ T3 | Optical deep-space | 50–200 Mbps | 8–15 min OWLT |
| L4/L5 ↔ Mars Orbital | T3 ↔ T4 | Optical deep-space | 2–100 Mbps | 3–12 min OWLT |
| Mars Orbital ↔ Surface | T4 ↔ T5 | Optical + UHF RF | 100 Mbps / 1 Mbps | <0.1 s OWLT |

### Intra-Tier Links

| Tier | Link Type | Technology | Data Rate |
|------|-----------|-----------|-----------|
| T2 | LEO ISL (intra-plane) | Optical laser crosslink | 10 Gbps |
| T2 | LEO ISL (inter-plane) | Optical laser crosslink | 1–5 Gbps |
| T2 | GEO ↔ GEO | Optical / terrestrial fibre | 10 Gbps |
| T3 | L4 ↔ L5 | Optical crosslink | 50 Mbps |
| T4 | Areo ↔ Areo | Optical ISL | 1 Gbps |
| T4 | Areo ↔ Polar | Optical + UHF | 100 Mbps |
| T5 | Base ↔ Base | UHF mesh | 1 Mbps |
| T5 | Base ↔ Rover/Drone | UHF / optical short-range | 1–10 Mbps |

The topology is modelled as a directed graph where each edge is annotated with `(data_rate, delay, availability, contact_schedule)`. The RL agent's state representation includes the node's current tier, which determines the set of feasible next-hops and link characteristics.
