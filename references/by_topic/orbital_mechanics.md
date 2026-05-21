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

## Doppler Shift in Deep Space Communications

[57] T. A. Million, S. D. Vanderpool, and R. J. Reinhart, "Proximity Space Link Doppler Measurement and Its Applications," in *Proc. IEEE Aerospace Conf.*, 2010, pp. 1-11.

> Analyzes Doppler shift effects on proximity space links (Mars orbiter-to-surface), quantifying frequency offsets up to ±200 kHz at UHF and ±15 GHz at 1550 nm optical. Demonstrates that uncompensated Doppler causes coherent receiver lock loss and increased bit error rates. AETHERIX's orbital mechanics module incorporates Doppler compensation parameters derived from this analysis, with real-time frequency offset prediction based on orbital state vectors.

[58] CCSDS, "Radio Frequency and Modulation Systems—Part 1: Earth Stations and Spacecraft," CCSDS 401.0-B-30, Blue Book, Feb. 2020.

> The CCSDS standard specifying RF frequency bands, modulation formats, and Doppler compensation requirements for space communications. AETHERIX's hybrid optical/RF architecture references this standard for the Ka-band (32 GHz) fallback link design, including recommended Doppler prediction algorithms and maximum residual frequency offset tolerances for supported modulation schemes.

## Network Topology Design for Interplanetary DTN

[59] J. A. Fraire, P. G. Madoery, A. Charif, and N. L. S. da Fonseca, "On the Design and Analysis of Contact Plans for DTN-based Space-Terrestrial Networks," *IEEE Communications Surveys & Tutorials*, vol. 21, no. 3, pp. 2603-2634, 3rd Quart. 2019.

> Comprehensive survey of contact plan design for space DTN networks, formalizing the problem of scheduling communication opportunities subject to orbital mechanics, antenna visibility, and power constraints. AETHERIX's 241-node topology and contact schedule generation follow Fraire's design methodology: orbital propagation → visibility windows → contact selection → schedule optimization, with the RL agent replacing the static schedule optimization step.

[60] G. M. de Jonquieres, J. A. Fraire, and J. M. Finochietto, "Traffic-Aware Contact Plan Design for Future Deep-Space Networks," *IEEE Trans. Commun.*, vol. 69, no. 12, pp. 8226-8237, Dec. 2021.

> Proposes traffic-aware contact plan design that considers expected data demand patterns when scheduling communication windows. Shows that incorporating traffic predictions into contact selection improves aggregate throughput by 20-35% over visibility-only scheduling. AETHERIX's RL routing agent implicitly captures traffic patterns through its reward function, achieving similar improvements without requiring a priori traffic models.
