# Day 24: Orbital Mechanics & Earth-Mars Distance

## 📅 Saturday, August 15, 2026

## 🎯 Learning Objective

Apply Keplerian orbital mechanics to explain the Earth-Mars distance cycle (54.6M km to 401M km), derive the synodic period (779.94 days), and articulate how this variation drives every aspect of AETHERIX's design from data rates to RL training. This addresses exam Learning Objective 4.

## 📖 The Core Concept

Earth and Mars orbit the Sun at different distances and different speeds. Earth, at 1.000 AU, completes an orbit every 365.25 days. Mars, at 1.524 AU, takes 686.98 days. Because Mars is farther out and moves slower (Kepler's third law: T² ∝ a³), the two planets continuously change their relative geometry. This changing geometry is the single most important physical fact in interplanetary communication design.

**The two-body problem and Keplerian elements:**

Every orbit can be described by six Keplerian elements. AETHERIX implements these in the `OrbitalElements` dataclass:

1. **Semi-major axis (a):** Half the longest diameter of the orbital ellipse. Earth: 1.000 AU. Mars: 1.524 AU.
2. **Eccentricity (e):** How elliptical the orbit is. Earth: 0.0167 (nearly circular). Mars: 0.0934 (noticeably elliptical — Mars's distance from the Sun varies by ~42 million km over its orbit).
3. **Inclination (i):** Tilt of the orbital plane. Earth: 0.00005°. Mars: 1.850° (slightly tilted relative to Earth's orbital plane).
4. **Right ascension of ascending node (Ω):** Orientation of the orbit in space.
5. **Argument of periapsis (ω):** Orientation of the ellipse within the orbital plane.
6. **Mean anomaly (M):** Position along the orbit at a reference epoch.

These six numbers fully determine a planet's position at any time (ignoring perturbations). AETHERIX uses J2000 epoch values from standard astronomical references.

**The orbital radius equation:**

At any true anomaly ν (the angle from periapsis), the orbital radius is:

```
r = a(1 − e²) / (1 + e·cos(ν))
```

For Mars at periapsis (ν=0): r = 1.524 × (1 − 0.0934²) / (1 + 0.0934) = 1.381 AU.
For Mars at apoapsis (ν=180°): r = 1.524 × (1 − 0.0934²) / (1 − 0.0934) = 1.666 AU.

Mars's eccentricity means its distance from the Sun varies by ~0.285 AU (~42.6 million km) — significantly more than Earth's ~0.034 AU variation. This is why the closest possible Earth-Mars approach (54.6M km) is not simply the difference of semi-major axes.

**The synodic period:**

The synodic period is the time between successive oppositions (closest approaches). It is derived from the difference in angular velocities:

```
1/P_synodic = |1/P_earth − 1/P_mars| = |1/365.25 − 1/686.98| = 0.001282/day

P_synodic = 779.94 days ≈ 780 days
```

Every 780 days, the Earth-Mars geometry cycles through its full range:
- **Opposition (~day 0):** Earth between Sun and Mars. Distance: 54.6M km. Light time: 3.0 min. Best communication.
- **Quadrature (~day 195):** 90° separation. Distance: ~150–225M km. Light time: 8–12.5 min. Average.
- **Conjunction (~day 390):** Sun between Earth and Mars. Distance: up to 401M km. Light time: 22.3 min. Worst communication — solar interference.
- **Quadrature again (~day 585):** Distance decreasing.
- **Next opposition (~day 780):** Cycle repeats.

**Why this matters for AETHERIX:**

The RL routing agent trains across the full 780-day synodic cycle to experience every condition. If training only covered opposition, the agent would learn policies that fail during conjunction — always forwarding immediately rather than storing. The agent's state includes a "distance phase" that discretises the synodic cycle, allowing it to learn distance-adaptive policies.

**Mars's higher eccentricity (0.0934 vs Earth's 0.0167)** means the actual distance at any given phase angle varies cycle-to-cycle. Some oppositions are closer than others. This adds a layer of unpredictability that the RL agent must handle through its stochastic exploration.

## 🔬 In AETHERIX

Orbital mechanics is implemented in `src/orbital/contact_windows.py` with supporting data in `src/orbital/bodies.py`.

Key constants:
```python
AU_KM = 149_597_870.7
SPEED_OF_LIGHT_KM_S = 299_792.458
EARTH_ORBITAL_PERIOD_DAYS = 365.25
MARS_ORBITAL_PERIOD_DAYS = 686.98
SYNODIC_PERIOD_DAYS = 779.94
```

The `OrbitalElements` dataclass stores J2000 Keplerian elements for both planets. The `ORBITAL_ELEMENTS` dictionary provides Earth and Mars values.

Key functions:
- `calculate_orbital_radius(elements, true_anomaly_deg)`: r = a(1−e²)/(1+e·cos(ν)).
- `calculate_position_heliocentric(elements, true_anomaly_deg)`: Full 3-axis rotation from orbital plane to ecliptic coordinates, returning (x, y, z) in AU.
- `calculate_earth_mars_distance(earth_anomaly, mars_anomaly)`: Computes heliocentric positions for both planets and returns the Euclidean distance in km.
- `calculate_light_time(distance_km)`: d / SPEED_OF_LIGHT_KM_S.
- `get_distance_timeline(num_points=780)`: Generates (day, distance_km, light_time_min) tuples across the full synodic period.

The `bodies.py` module provides `CelestialBodyData` with physical parameters (mass, radius, orbital period) and a `get_orbital_velocity()` function using v = √(μ/a).

## 📐 Key Numbers & Formulas

| Parameter | Earth | Mars |
|-----------|-------|------|
| Semi-major axis | 1.000 AU | 1.524 AU |
| Eccentricity | 0.0167 | 0.0934 |
| Inclination | 0.00005° | 1.850° |
| Orbital period | 365.25 days | 686.98 days |
| Mean orbital velocity | 29.78 km/s | 24.07 km/s |

**Earth-Mars distance and light time:**

| Phase | Distance | One-Way Light Time |
|-------|----------|-------------------|
| Opposition (closest) | 54.6M km (0.365 AU) | 3.0 min |
| Average | 225M km (1.5 AU) | 12.5 min |
| Conjunction (farthest) | 401M km (2.68 AU) | 22.3 min |
| **Synodic period** | **779.94 days** | — |

**Key formulas:**
```
Orbital radius:  r = a(1 − e²) / (1 + e·cos(ν))

Orbital period:  T = 2π√(a³/μ)

Synodic period:  1/P_syn = |1/P_inner − 1/P_outer|

Orbital velocity:  v = √(μ/a)   [circular approximation]
```

## 🔗 Standards & References

- [Vallado — "Fundamentals of Astrodynamics and Applications" (2013)](https://store.knovel.com/knovel2/Toc.jsp?BookID=3576)
- [JPL Horizons System — Solar System Dynamics](https://ssd.jpl.nasa.gov/horizons/)
- [Standish, E.M. — JPL Planetary and Lunar Ephemerides](https://ssd.jpl.nasa.gov/planets/ephemerides/)
- [NASA — Mars Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html)

## 💡 How the Examiner Will Probe This

**Q: "What is the Earth-Mars synodic period and why does it matter?"**
779.94 days (~780). It's the time between successive oppositions. AETHERIX simulations must cover at least one full cycle to capture the complete distance variation. The RL agent trains across this period to learn distance-adaptive policies — if it only saw opposition conditions, it would fail during conjunction.

**Q: "Why is the closest approach 54.6M km, not simply 0.524 AU?"**
Because both orbits are elliptical. Mars's eccentricity (0.0934) means its distance from the Sun varies by ~42M km. The closest approach occurs when Earth is near aphelion and Mars is near perihelion simultaneously — a rare alignment. The simple subtraction (1.524−1.000) × AU = 78.4M km would be the average distance if both orbits were circular.

**Q: "How does the 22-minute one-way light time at conjunction affect your protocol design?"**
A command sent from Earth takes 22 minutes to arrive. Confirmation takes another 22 minutes to return. The RL agent must make routing decisions with state information that is always 3–22 minutes stale. This is why DTN store-and-forward is essential — the agent cannot wait for real-time feedback, and LTP custody transfer localizes retransmission to the failed hop.

## ✅ Self-Check Questions

1. Derive the synodic period from Earth and Mars orbital periods. Show the formula.
2. What are Mars's six Keplerian elements at J2000? Which ones differ most from Earth?
3. Compute Mars's orbital radius at periapsis and apoapsis using the orbital radius equation.
4. What is the maximum Earth-Mars distance, and what causes it to be that large?
5. Why does the RL agent's training span the full 780-day synodic period?

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/contact_windows.py` — `OrbitalElements`, `ORBITAL_ELEMENTS`, `calculate_orbital_radius()`, `calculate_position_heliocentric()`, `calculate_earth_mars_distance()`
- **Supporting data:** `src/orbital/bodies.py` — `CelestialBodyData`, `BODIES`, `get_orbital_velocity()`
- **Topic summary:** `interview_prep/topic_summaries/orbital_mechanics.md` — Synodic Period, Keplerian Elements
- **Cheat sheet:** `interview_prep/cheat_sheets/constants.md` — Earth/Mars Parameters
- **Cheat sheet:** `interview_prep/cheat_sheets/formulas.md` — Orbital Mechanics section
