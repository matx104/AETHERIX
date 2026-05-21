# Orbital Mechanics & Space Systems References

AETHERIX must predict when Earth and Mars nodes can communicate (contact windows) based on orbital positions, and model the varying distance (54.6M–401M km) that drives link budget calculations and light-time delays (3–22 minutes). The references below cover the astrodynamics theory, Mars communication relay experience, and ephemeris data sources that underpin AETHERIX's `contact_windows.py` module.

## Most Important

| Ref | Citation | Why Critical |
|-----|----------|--------------|
| [38] | Vallado, 2013 | Standard astrodynamics textbook — basis for orbital calculations |
| [43] | Giorgini, 2015 | JPL Horizons — the ephemeris source AETHERIX should integrate |
| [41] | Edwards et al., 2006 | Mars relay strategies — directly models AETHERIX's Mars tier |

---

## Astrodynamics Textbooks

[38] D. A. Vallado, *Fundamentals of Astrodynamics and Applications*, 4th ed. Hawthorne, CA: Microcosm Press, 2013.

> The standard reference for orbital mechanics calculations. Vallado's treatment of Keplerian orbits, perturbation theory, and coordinate frame transformations (EME2000, ICRF) provides the mathematical foundation for AETHERIX's `calculate_earth_mars_distance()` function, which computes interplanetary distance from true anomaly using the vis-viva equation and orbital element conversions.

[39] H. D. Curtis, *Orbital Mechanics for Engineering Students*, 4th ed. Oxford, UK: Butterworth-Heinemann, 2020.

> A pedagogically clear orbital mechanics textbook with extensive worked examples. Curtis's derivation of the Kepler equation (M = E - e·sin E) and its numerical solution is the algorithm AETHERIX uses for converting mean anomaly to true anomaly in the synodic period distance timeline calculation.

[40] R. R. Bate, D. D. Mueller, and J. E. White, *Fundamentals of Astrodynamics*, 2nd ed. Mineola, NY: Dover Publications, 2020.

> Classic astrodynamics text with a focus on the two-body problem and Lambert's problem. Bate's formulation of the orbit equation (r = p / (1 + e·cos θ)) is the starting point for AETHERIX's distance calculations. The synodic period analysis (Earth–Mars ≈ 780 days) used in `get_distance_timeline()` follows the approach described here.

## Mars Communications

[41] C. D. Edwards, J. T. Adams, D. J. Bell, R. Cesarone, R. DePaula, et al., "Relay Communications Strategies for Mars Exploration Through 2020," *Acta Astronautica*, vol. 59, no. 1-5, pp. 310-318, Jul.-Sep. 2006.

> Describes the Mars relay network architecture using orbiters (MRO, Odyssey, MAVEN, ExoMars TGO) as data relays for surface assets. AETHERIX's Mars orbital tier (areostationary + polar orbit relays) and Mars surface tier (bases, rovers, drones, sensors) are modeled on this operational architecture. Edwards's analysis of relay contact opportunities informs AETHERIX's contact window prediction.

[42] R. E. Gladden, "Mars Reconnaissance Orbiter Relay Telecommunications Support of Mars Surface Exploration," *Acta Astronautica*, vol. 65, no. 9-10, pp. 1430-1436, Nov.-Dec. 2009.

> Details MRO's Electra relay radio operations supporting Mars surface missions. Provides real-world data on relay session durations, data volumes, and contact frequencies. AETHERIX's Mars relay link parameters are calibrated to MRO-era performance.

## Ephemeris & Precision Orbit Data

[43] J. D. Giorgini, "Status of the JPL Horizons Ephemeris System," in *IAU General Assembly*, 2015, Meeting #29, id. 2256293.

> Describes JPL's Horizons system, which provides high-precision ephemeris data for solar system bodies via telnet, email, and web API interfaces. AETHERIX's architecture docs identify Horizons integration as a production upgrade: replacing the current simplified two-body orbital model with Horizons-fetched ephemeris that includes planetary perturbations, non-gravitational forces, and relativistic corrections. This would improve contact window prediction accuracy from hours to minutes.

[55] C. D. Edwards and R. DePaula, "Key Telecommunications Technologies for Increasing Data Return for Future Mars Exploration," *Acta Astronautica*, vol. 61, no. 1-6, pp. 131-138, Jun.-Aug. 2007.

> Analyzes technology options for increasing Mars data return, including optical communications, higher-frequency RF (Ka-band), and relay optimization. Edwards's data rate projections for Mars missions directly inform AETHERIX's 2–200 Mbps range and the distance-dependent rate model in `LinkBudgetCalculator`.

[56] NASA, "Mars Communication Relay Mission Concept Study," JPL CL#18-2467, Jet Propulsion Laboratory, 2018.

> A JPL concept study for a dedicated Mars communication relay satellite. Proposes an areostationary relay with simultaneous UHF (surface links) and Ka-band/Optical (Earth links) — matching AETHERIX's Mars orbital tier design. The link budget analysis in this document validates AETHERIX's assumed link parameters for the Mars leg.
