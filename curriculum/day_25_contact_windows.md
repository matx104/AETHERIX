# Day 25: Contact Window Prediction

## 📅 Sunday, August 16, 2026

## 🎯 Learning Objective

Explain how AETHERIX predicts communication contact windows using orbital propagation, understand the role of line-of-sight geometry and minimum elevation angles, and describe how the RL agent uses these predictions for opportunistic store-vs-forward decisions. This addresses exam Learning Objective 4.

## 📖 The Core Concept

A contact window is the interval during which two DTN nodes have line-of-sight with acceptable geometry for communication. In terrestrial networks, connections are continuous — you don't predict when your phone can reach a cell tower. In interplanetary DTN, contact windows are **scheduled, finite, and predictable** — and predicting them correctly is essential for efficient data routing.

**What determines a contact window:**

Three factors determine whether two nodes can communicate:

1. **Line-of-sight (LOS):** No planet, moon, or the Sun blocks the straight-line path between transmitter and receiver. For Earth-Mars links, the Sun is the major blocker during conjunction. For surface-to-orbit links, the planet's curvature blocks LOS when the satellite is below the horizon.

2. **Elevation angle:** Even when a target is above the horizon, atmospheric path length matters. Low elevation angles mean the signal passes through more atmosphere, increasing attenuation and turbulence. AETHERIX uses:
   - **10° minimum elevation for RF links** — RF tolerates more atmospheric path.
   - **20–30° minimum for optical links** — optical is far more sensitive to atmospheric turbulence and cloud cover.

3. **Orbital geometry:** A satellite's orbital trajectory determines when it rises above and sets below the minimum elevation angle. For a DSN station at a given latitude, Mars appears above the horizon for 6–12 hours per day depending on Mars's declination relative to the station's latitude.

**Earth-Mars direct contact windows:**

With three DSN stations at 120° longitude spacing, at least one station always has Mars above the horizon. A single station typically gets 6–12 hours of usable contact per day. With three stations arrayed, total daily coverage can reach 18–24 hours. During solar conjunction, direct windows drop to zero — the Sun physically blocks LOS for approximately two weeks.

**Mars surface-to-orbital contact windows:**

Areostationary relays (at 17,032 km, fixed over the equator) provide **continuous** coverage to equatorial surface assets — no window prediction needed, the relay is always overhead. This is the key advantage of areostationary orbit for relay: the contact schedule is trivially "always on."

Polar orbiters, by contrast, have ~90-minute orbital periods with only ~10 minutes of line-of-sight per pass to any given surface point. These windows are highly predictable but require scheduling — the RL agent must know when the next polar pass occurs to decide whether to store or forward.

**LEO constellation contact windows:**

The 48-satellite LEO constellation provides inter-satellite links that are always available (satellites in the same plane maintain continuous LOS) and cross-plane links that are intermittent (available when two satellites from different planes are within pointing range).

**How predictions are computed:**

AETHERIX uses two propagation methods:
- **SGP4/SDP4** for LEO satellites with Two-Line Element (TLE) inputs — the standard simplified general perturbation model.
- **JPL Horizons** for planetary positions — high-precision ephemeris from NASA's Solar System Dynamics group.

The simplified model in AETHERIX (`predict_contact_windows()`) computes a phase angle between Earth and Mars orbital positions. When the phase angle drops below 10°, a conjunction blackout is declared — no direct contact. Otherwise, contact duration scales as the sine of the phase angle, with a base of 8 hours.

**How the RL agent uses predictions:**

Contact window predictions are injected into the RL agent's state representation. If the agent knows a high-quality contact window opens in 2 hours, it may choose STORE now rather than forwarding through a poor-quality link. This time-varying policy is one of the agent's key advantages over static Contact Graph Routing (CGR) — it learns to be opportunistic about contact windows.

## 🔬 In AETHERIX

Contact window prediction is implemented in `src/orbital/contact_windows.py`.

The `ContactWindow` dataclass captures each predicted window:
```python
@dataclass
class ContactWindow:
    start_time_jd: float        # Julian date
    end_time_jd: float          # Julian date
    duration_hours: float
    max_elevation_deg: float
    average_distance_km: float
    max_data_rate_mbps: float
    window_type: str            # "direct", "relay", "emergency"
```

The `LinkGeometry` dataclass captures instantaneous link state:
```python
@dataclass
class LinkGeometry:
    distance_km: float
    light_time_seconds: float
    elevation_angle_deg: float
    azimuth_deg: float
    doppler_shift_hz: float
```

The `predict_contact_windows(start_day, duration_days, ground_station)` function:
1. Iterates day-by-day through the prediction period.
2. Computes simplified orbital anomalies for Earth and Mars.
3. Calculates distance via `calculate_earth_mars_distance()`.
4. Computes light time via `calculate_light_time()`.
5. Derives a phase angle; if < 10°, declares conjunction blackout (`continue` — skip this day).
6. Otherwise, duration = 8.0 × sin(phase_angle) hours; if < 2 hours, skip (minimum useful contact).
7. Estimates data rate via `estimate_data_rate(distance_km)`.
8. Creates a `ContactWindow` object with all parameters.

The `get_distance_timeline(num_points=780)` function generates the full synodic period timeline for mission planning.

## 📐 Key Numbers & Formulas

| Parameter | Value |
|-----------|-------|
| Single DSN station contact | 6–12 hours/day |
| Three DSN stations combined | 18–24 hours/day |
| Minimum elevation (RF) | 10° |
| Minimum elevation (optical) | 20–30° |
| Conjunction blackout threshold | Phase angle < 10° |
| Base contact duration | 8 hours × sin(phase_angle) |
| Minimum useful contact | 2 hours |
| Polar orbiter pass duration | ~10 minutes (from ~90-min orbit) |
| Areostationary coverage | Continuous (equatorial) |

**Data volume per window:**
```
Max_data_volume = data_rate × window_duration × link_efficiency
```

## 🔗 Standards & References

- [CCSDS 734.3-B-1 — Schedule-Aware Bundle Routing (SABR)](https://public.ccsds.org/Pubs/734x3b1.pdf)
- [RFC 5326 — Licklider Transmission Protocol (contact scheduling)](https://datatracker.ietf.org/doc/html/rfc5326)
- [JPL Horizons — Web Interface](https://ssd.jpl.nasa.gov/horizons/app.html)
- [Celestrak — TLE / SGP4 source](https://celestrak.org/)
- [Vallado et al. — "Revisiting Spacetrack Report #3" (SGP4)](https://celestrak.org/NORAD/documentation/spacetrk.pdf)

## 💡 How the Examiner Will Probe This

**Q: "How does AETHERIX predict contact windows, and how does the RL agent use them?"**
Contact windows are predicted by propagating orbits (SGP4 for LEO, JPL Horizons for planets) and computing line-of-sight geometry filtered by minimum elevation angle (10° RF, 20–30° optical). The `predict_contact_windows()` function returns windows as (start, end, max_data_volume) tuples. The RL agent uses these in its state representation — knowing a window opens in 2 hours, it may STORE rather than forward through a poor link. This time-aware policy is its advantage over static CGR.

**Q: "What's the typical Earth-Mars contact window duration?"**
6–12 hours per day for a single DSN station, depending on Mars's declination and the station's latitude. With three DSN stations, total coverage can be 18–24 hours/day. During conjunction, direct contact drops to zero for ~2 weeks.

**Q: "Why 10° elevation for RF but 20–30° for optical?"**
Optical links are far more sensitive to atmospheric turbulence and cloud cover. At low elevation angles, the signal passes through more atmosphere (longer slant range), increasing scintillation and absorption. RF at Ka-band tolerates more atmospheric path because it has wider beam divergence and is less affected by turbulence.

## ✅ Self-Check Questions

1. What three factors determine whether a contact window is open between two nodes?
2. Why do areostationary relays provide "always-on" contact while polar orbiters require scheduling?
3. What phase angle triggers a conjunction blackout in the simplified model? Why?
4. How does the base contact duration (8 hours) scale with phase angle? What mathematical function is used?
5. Give an example of how the RL agent's time-varying policy outperforms static CGR using contact window awareness.

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/contact_windows.py` — `ContactWindow`, `LinkGeometry`, `predict_contact_windows()`, `get_distance_timeline()`
- **Topic summary:** `interview_prep/topic_summaries/orbital_mechanics.md` — Contact Windows section
- **Mock interview:** `interview_prep/practice/mock_interview.md` — Q11 (Contact Windows)
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §3.3 (polar orbiter fallback scenario)
- **Cheat sheet:** `interview_prep/cheat_sheets/formulas.md` — Light Time & Distance section
