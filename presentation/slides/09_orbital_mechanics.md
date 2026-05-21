# Orbital Mechanics — Contact Windows

## Communication Window Prediction

### Mars Orbital Parameters

| Parameter | Value | Note |
|-----------|-------|------|
| Semi-major axis | 1.524 AU (227.9 M km) | Average orbital radius |
| Eccentricity | 0.0934 | Significantly elliptical |
| Orbital period | 686.98 days | 1.88 Earth years |
| Synodic period | 779.94 days | Opposition → opposition |
| Min distance (perihelion opposition) | 54.6 M km (0.365 AU) | Best communication |
| Max distance (aphelion conjunction) | 401 M km (2.68 AU) | Worst communication |
| Areostationary orbit | 17,032 km altitude | Mars GEO equivalent |

### Earth-Mars Distance Over Synodic Period

```
Distance (AU)
3.0 ┤                                              ╭─── Conjunction (blackout)
    │                                         ╭────╯
2.5 ┤                                    ╭────╯
    │                               ╭────╯
2.0 ┤                          ╭────╯
    │                     ╭────╯
1.5 ┤                ╭────╯
    │           ╭────╯
1.0 ┤      ╭────╯
    │ ╭────╯
0.5 ┤─╯ Opposition (best)
    ├──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──→ Month
    0  2  4  6  8  10 12 14 16 18 20 22 24 26
```

### Contact Window Types

| Window Type | Availability | Duration/Day | Data Rate | Months Around |
|-------------|:----------:|:------------:|:---------:|:-------------:|
| **Optimal** (opposition) | 99% | 8-12 hours | 100-200 Mbps | ±3 months |
| **Good** | 95% | 6-8 hours | 20-100 Mbps | ±6 months |
| **Fair** (quadrature) | 85% | 2-4 hours | 5-20 Mbps | ±9 months |
| **Poor** (near conjunction) | 50% | 0-2 hours | 1-5 Mbps | ±12 months |
| **Blackout** (conjunction) | 0% direct | 0 hours | Lagrange relay only | ±2 weeks |

### Solar Conjunction Strategy

During conjunction (~2 weeks), the Sun blocks the direct Earth-Mars line-of-sight:

1. **T-14 days**: Pre-position critical uploads to Mars assets
2. **T-7 days**: Activate Lagrange relay path (ES-L4/ES-L5)
3. **T-0 to T+14**: Autonomous operations — no Earth commands
4. **Mars assets**: Store data locally in buffers
5. **T+14 days**: Resume direct links, transmit backlog

**AETHERIX achieves 50-70% availability during conjunction via Lagrange relays.**

### Doppler Shift Compensation

| Parameter | Value |
|-----------|-------|
| Max relative velocity | ~24 km/s (Earth-Mars) |
| Frequency shift at 1550 nm | Δf ≈ 15 GHz |
| Percentage shift | Δf/f ≈ 0.008% |
| Compensation method | Real-time frequency tracking + pre-compensation |
| Impact if uncompensated | Signal falls outside receiver bandwidth |

### Tools & Integration

- **JPL Horizons API** — High-precision ephemeris for orbital predictions
- **SGP4/SDP4** — Real-time orbital propagation (TLE-based)
- **Contact window calculator** — Predicts communication opportunities
- **AETHERIX RL agent** — Schedules transmissions within predicted windows

### Key Formula

```
Earth-Mars distance:
r = √(r_Earth² + r_Mars² − 2 × r_Earth × r_Mars × cos(Δθ))

Where:
  r_Earth = 1.0 AU
  r_Mars  = 1.524 AU
  Δθ      = angular separation (true anomaly difference)
```

### Demo

> **Launch demo**: [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/) → "Orbital Mechanics" tab
