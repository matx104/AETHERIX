# Optical Communications References

AETHERIX uses a hybrid optical/RF communication architecture where the primary data path is a 1550 nm laser link achieving 2–200 Mbps depending on Earth–Mars distance. The references below cover NASA's flight demonstrations (LLCD, DSOC), the textbook theory behind AETHERIX's link budget calculator, and the channel models needed for deep-space optical link design.

## Most Important

| Ref | Citation | Why Critical |
|-----|----------|--------------|
| [23] | Boroson et al., 2014 | LLCD results — proves high-rate laser comms work from lunar distance |
| [25] | Biswas et al., 2018 | DSOC design — the architecture AETHERIX mirrors for Mars ranges |
| [27] | Hemmati, 2006 | Standard textbook — AETHERIX's `LinkBudgetCalculator` follows this |
| [49] | CCSDS 141.0-B-1 | Official optical comms physical layer standard |

---

## NASA/JPL Demonstrations

[23] D. M. Boroson, B. S. Robinson, D. V. Murphy, D. A. Burianek, F. Khatri, et al., "Overview and Results of the Lunar Laser Communication Demonstration," *Proc. SPIE*, vol. 8971, p. 89710S, Mar. 2014. doi: 10.1117/12.2045508

> Reports the Lunar Laser Communication Demonstration (LLCD) that achieved 622 Mbps downlink from the Moon at 1550 nm. LLCD is the direct precursor to the technology AETHERIX models: same wavelength, similar photon-counting receivers, and comparable pointing-and-tracking requirements. AETHERIX's link budget parameters (transmit power, aperture diameter, detector sensitivity) are calibrated to LLCD-era hardware.

[24] B. S. Robinson et al., "The NASA Lunar Laser Communication Demonstration – Successful High-Rate Laser Communications To and From the Moon," in *Proc. SpaceOps 2014 Conf.*, 2014, p. 1685.

> A mission-level summary of LLCD operations, including uplink (20 Mbps) and downlink (622 Mbps) performance, weather impacts, and ground station operations. The operational lessons (scheduling around clouds, ground station diversity) inform AETHERIX's multi-DSN-station topology.

[25] A. Biswas, B. Moision, W. T. Roberts, W. H. Farr, A. Gray, et al., "Deep Space Optical Communications (DSOC)," *Proc. SPIE*, vol. 10524, p. 105240J, Feb. 2018. doi: 10.1117/12.2296426

> Describes the DSOC payload on the Psyche mission, targeting Mars-equivalent distances (~2 AU). DSOC's architecture — ground laser transmitter, space-based photon-counting detector, and pointing-and-acquisition system — is the closest operational analog to AETHERIX's deep-space optical links. AETHERIX's data rate model (2–200 Mbps distance-dependent) follows DSOC performance projections.

[26] M. D. Shaw et al., "Deep Space Optical Communications (DSOC) Far Detector and Ground Laser Transmitter Development," *Proc. SPIE*, vol. 11180, p. 1118029, Sep. 2019.

> Details DSOC's ground segment: the uplink beacon laser, downlink photon-counting detector arrays, and the Table Mountain Facility ground station. AETHERIX's DSN ground station model (Goldstone, Madrid, Canberra) draws on these specifications for calculating uplink EIRP and downlink sensitivity.

## Link Budget Analysis

[27] H. Hemmati, Ed., *Deep Space Optical Communications*, Deep Space Communications and Navigation Series. Hoboken, NJ: Wiley-Interscience, 2006.

> The authoritative textbook on deep-space optical link design. Covers free-space loss, pointing loss, atmospheric attenuation, scintillation, and receiver sensitivity in a unified framework. AETHERIX's `OpticalLinkBudget` dataclass and `LinkBudgetCalculator` class in `src/infrastructure/link_budget.py` are structured to follow Hemmati's link budget equation chain: EIRP → free-space loss → pointing loss → atmospheric loss → received power → link margin.

[28] B. Moision and J. Hamkins, "Deep Space Optical Communications," in *Near-Earth Laser Communications*, H. Hemmati, Ed. Boca Raton, FL: CRC Press, 2009, ch. 12.

> Extends the Hemmati textbook to deep-space-specific channel models, including background radiation from planets and the Sun, and photon-counting receiver performance at Mars distances. AETHERIX's distance-dependent data rate model uses Moision's channel capacity analysis.

[29] W. K. Marshall, "Free-Space Optical Communication Link Budget," in *Optical Wireless Communications*, S. Arnon et al., Eds. Cambridge, UK: Cambridge Univ. Press, 2012, ch. 5.

> A focused treatment of the optical link budget equation with worked examples. Marshall's formulation of the link margin equation (received power minus required sensitivity, in dB) is the exact approach used in AETHERIX's `LinkBudgetCalculator.calculate_link_margin()` method.

## Related CCSDS Standard

[49] CCSDS, "Optical Communications Physical Layer," CCSDS 141.0-B-1, Blue Book, Aug. 2019. [Online]. Available: https://public.ccsds.org/Pubs/141x0b1.pdf

> The CCSDS standard for the optical communications physical layer, specifying modulation formats, coding schemes, and acquisition sequences. AETHERIX's optical link module should conform to this standard in production for interoperability with CCSDS-compliant ground stations and relay satellites.
