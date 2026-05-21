# Learning Objective 4: Orbital Mechanics & Propagation Models

## Free Online Courses & Certificates

### University Courses (Free)
- **[Orbital Mechanics — University of Colorado (Coursera)](https://www.coursera.org/courses?query=orbital+mechanics)** — Free audit
- **[Astronomy — Duke University (Coursera)](https://www.coursera.org/learn/astronomy-introduction)** — Free audit
- **[Introduction to Space Science — MIT OCW](https://ocw.mit.edu/courses/16-01-unified-engineering-i-ii-iii-iv-fall-2005-spring-2006/)** — Free materials
- **[Orbital Mechanics for Engineering Students — CU Boulder](https://www.coursera.org/learn/spacecraft-dynamics-kinetics)** — Free audit
- **[Kerbal Space Program — Educational](https://www.kerbalspaceprogram.com/)** — Best hands-on orbital mechanics learning tool

### Official Documentation (Free)
- **[JPL Horizons System](https://ssd.jpl.nasa.gov/horizons/)** — THE tool for precise ephemeris
- **[JPL Horizons User Manual](https://ssd.jpl.nasa.gov/doc/horizons/)** — How to use the API
- **[NASA SPICE Toolkit](https://naif.jpl.nasa.gov/naif/toolkit.html)** — Spacecraft position/geometry
- **[Celestrak TLE Data](https://celestrak.org/)** — Two-Line Element sets for SGP4 propagation
- **[GMAT — General Mission Analysis Tool](https://software.nasa.gov/software/GSFC-54099)** — NASA's orbital mechanics software (free)

### YouTube Videos (Free)

#### Must-Watch (Orbital Mechanics)
| Video | Channel | Duration | Why Watch |
|-------|---------|----------|-----------|
| [Orbital Mechanics — Full Course](https://www.youtube.com/watch?v=J1lRLElluEQ) | CrashCourse | ~50 min | Complete overview |
| [Kepler's Laws Explained](https://www.youtube.com/watch?v=G1AyGHqMolM) | CrashCourse | ~10 min | Foundation |
| [Lagrange Points — Full Explanation](https://www.youtube.com/watch?v=mxpVbU5FH0s) | PBS Space Time | ~15 min | Critical for AETHERIX |
| [Hohmann Transfer Orbits](https://www.youtube.com/watch?v=GsXppO8pI-8) | ScienceClic | ~10 min | Earth-Mars trajectory |
| [Synodic Period Explained](https://www.youtube.com/results?search_query=synodic+period+explained) | Various | ~10 min | 780-day cycle |
| [Doppler Effect in Space](https://www.youtube.com/results?search_query=doppler+effect+space+communications) | Various | ~10 min | Frequency shift |

#### Interactive Tools
| Tool | Type | Link | Purpose |
|------|------|------|---------|
| [Kerbal Space Program](https://www.kerbalspaceprogram.com/) | Game (paid, ~$30) | kerbalspaceprogram.com | Best orbital mechanics learning tool ever made |
| [Universe Sandbox](https://universesandbox.com/) | Simulation (paid) | universesandbox.com | Gravitational simulation |
| [Orbiter](http://orbit.medphys.ucl.ac.uk/) | Free Simulator | orbit.medphys.ucl.ac.uk | Free space flight simulator |
| [JPL Horizons Web Interface](https://ssd.jpl.nasa.gov/horizons/app.html) | Free Web Tool | ssd.jpl.nasa.gov | Real ephemeris data |
| [NASA Eyes on the Solar System](https://eyes.nasa.gov/) | Free Visualization | eyes.nasa.gov | 3D solar system viewer |
| [Heavens-Above](https://www.heavens-above.com/) | Free | heavens-above.com | Satellite tracking |

### Academic Papers / Books (Free / Open Access)

| Resource | Author | Year | Link | Priority |
|----------|--------|------|------|:--------:|
| *Fundamentals of Astrodynamics* (excerpts) | Bate, Mueller, White | 2020 | Dover (affordable) | REFERENCE |
| Orbital Mechanics lectures | MIT OCW | — | [MIT OCW](https://ocw.mit.edu/) | HIGH |
| "Status of JPL Horizons" | Giorgini | 2015 | [IAU](https://doi.org/10.1017/S1743921315005443) | MEDIUM |

### Key Formulas to Master

```
1. Free-Space Path Loss:
   FSPL (dB) = 20 × log₁₀(4πd/λ)

2. Orbital Radius (Ellipse):
   r = a(1 − e²) / (1 + e × cos(θ))

3. Orbital Period:
   T = 2π × √(a³/μ)
   μ_Sun = 1.327 × 10²⁰ m³/s²

4. Synodic Period:
   1/P_syn = |1/P_inner − 1/P_outer|
   Earth-Mars: P_syn = 779.94 days

5. Light Time:
   t = d/c
   c = 299,792,458 m/s

6. Doppler Shift:
   Δf/f = v/c

7. Earth-Mars Distance:
   d = √(r_E² + r_M² − 2·r_E·r_M·cos(Δθ))
```

### Key Concepts to Master

1. **Earth-Mars distance cycle** — Perihelion (54.6M km) to aphelion (401M km), synodic 780 days
2. **Light-time calculation** — t = d/c, know all 3 scenarios by heart
3. **Contact windows** — When and why communication is possible
4. **Solar conjunction** — Angular separation near 0°, Sun blocks line-of-sight
5. **Doppler compensation** — Δf ≈ 15 GHz at 1550 nm, v_max ≈ 24 km/s
6. **SGP4/SDP4 propagation** — TLE-based orbit prediction
7. **Areostationary orbit** — 17,032 km altitude, 24.623 hr period

### Practice Calculations

1. What is the one-way light time to Mars at 225M km? → 750s = 12.5 min
2. What is FSPL at 1550 nm over 225M km? → −365.0 dB
3. What is the Doppler shift at v=24 km/s for 1550 nm? → Δf ≈ 15 GHz
4. What is the areostationary orbital period? → 24.623 hours (1 Mars sol)
5. How long is the synodic period? → 779.94 days
