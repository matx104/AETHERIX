# Day 21: Optical Link Budgets (1550 nm)

## 📅 Wednesday, August 12, 2026

## 🎯 Learning Objective

Walk through a complete optical link budget calculation at 1550 nm — from transmit power through EIRP, free-space loss, aperture gains, to received power and link margin — and explain why optical is AETHERIX's primary deep-space link. This addresses exam Learning Objective 4 (Link Budgets).

## 📖 The Core Concept

A link budget is the most fundamental engineering analysis in any communication system. It is an accounting of every gain and every loss from the transmitter to the receiver. The bottom line is the **link margin**: how many decibels of headroom exist between the received signal quality and the minimum needed for error-free decoding.

For deep-space optical links, the link budget tells you whether your photons actually arrive. At Earth-Mars distances, the received power is not measured in milliwatts or microwatts — it's measured in individual photons per second. The link budget tells you if enough arrive.

**The optical link budget chain:**

Starting from the transmitter, the signal chain is:

1. **Transmit power (dBm):** A 5-watt laser converts to +37 dBm. This is the raw optical power launched into the transmit telescope.

2. **Transmit antenna (telescope) gain (dB):** A telescope concentrates light into a narrow beam rather than radiating isotropically. For a 22 cm aperture at 1550 nm with 55% efficiency: G = 10·log₁₀(0.55 × (π × 0.22 / 1.55×10⁻⁶)²) ≈ +113 dBi. This enormous gain is why optical works at interplanetary distances — the beam divergence is only ~7 microradians.

3. **EIRP (Effective Isotropic Radiated Power):** EIRP = transmit power + transmit gain + transmit pointing loss + transmit optics efficiency. This is what the transmitter "effectively" radiates if it were an isotropic source.

4. **Free-space path loss (FSPL):** The dominant loss. At average Earth-Mars distance (225 million km) and 1550 nm: FSPL ≈ −365 dB. This staggering number represents the inverse-square dilution of photons over interplanetary distances.

5. **Atmospheric loss:** About −1 to −3 dB for a clear sky at moderate elevation. Clouds block optical entirely (hence the need for RF backup).

6. **Receive antenna (telescope) gain:** A 1-meter ground telescope at 1550 nm provides ~+117 dBi gain, collecting the tiny fraction of photons that arrive.

7. **Receiver losses:** Optics efficiency (−2 dB), pointing loss (−0.5 dB), implementation loss (−2 dB).

8. **Received power:** EIRP + FSPL + atmospheric loss + RX gain + RX losses. At 225 million km, this works out to approximately **−234 dBm** — deep in the photon-counting regime.

9. **Receiver sensitivity:** The minimum detectable power for a given data rate. The simplified model: sensitivity = −50 + 10·log₁₀(data_rate_mbps) dBm.

10. **Link margin:** Received power − sensitivity − required SNR. A positive margin means the link closes.

The key insight: optical works despite the enormous path loss because telescope gains (+113 dBi TX, +117 dBi RX) partially compensate for the −365 dB FSPL. No RF antenna can achieve comparable gain-to-size ratio — this is the fundamental physics advantage of optical.

## 🔬 In AETHERIX

The optical link budget is implemented in `src/infrastructure/link_budget.py`.

The `LinkBudgetCalculator` class is initialized with `wavelength_m = 1550e-9` (1550 nm) by default. The core calculation method is `calculate_optical_link_budget()` with these default parameters:

- `tx_power_watts = 5.0` (5W laser → +37 dBm)
- `tx_aperture_m = 0.22` (22 cm Mars orbiter aperture, DSOC-class)
- `rx_aperture_m = 1.0` (1m Earth ground station telescope)
- `data_rate_mbps = 10.0` (target 10 Mbps)
- Pointing losses: TX −1.0 dB, RX −0.5 dB
- Optics efficiency: TX −2.0 dB, RX −2.0 dB
- Atmospheric loss: −3.0 dB
- Implementation loss: −2.0 dB
- Required SNR: 10.0 dB
- Aperture efficiency: 0.55 (both TX and RX)

Key methods:
- `calculate_free_space_loss_db(distance_km)`: Returns `−10·log₁₀((4π·d/λ)²)` — the FSPL as a negative dB value.
- `calculate_antenna_gain_db(aperture_diameter_m, efficiency)`: Returns `10·log₁₀(η·(π·D/λ)²)`.
- `calculate_mars_earth_link(scenario)`: Convenience method for "minimum" (55M km), "average" (225M km), and "maximum" (401M km) scenarios.
- `calculate_one_way_light_time(distance_km)`: Returns d/c in seconds.

The `OpticalLinkBudget` dataclass captures all input parameters and calculated values (EIRP, received power, link margin).

## 📐 Key Numbers & Formulas

| Parameter | Value |
|-----------|-------|
| Wavelength | 1550 nm (193.4 THz) |
| TX power | 5 W (+37 dBm) |
| TX aperture | 22 cm → ~+113 dBi gain |
| RX aperture | 1.0 m → ~+117 dBi gain |
| FSPL at 225M km | ~−365 dB |
| Received power at 225M km | ~−234 dBm |
| Required SNR | 10.0 dB |
| Default data rate target | 10 Mbps |

**Key formulas:**

```
FSPL = −10·log₁₀((4π·d/λ)²)          [dB]

Gain = 10·log₁₀(η·(π·D/λ)²)          [dBi], η = 0.55

EIRP = P_tx_dBm + G_tx + L_pointing_tx + L_optics_tx

P_received = EIRP + FSPL + L_atm + G_rx + L_optics_rx + L_pointing_rx + L_impl

Sensitivity = −50 + 10·log₁₀(R_data)  [dBm]

Margin = P_received − Sensitivity − Required_SNR
```

## 🔗 Standards & References

- [CCSDS 141.0-B-1 — Optical Communications Physical Layer](https://public.ccsds.org/Pubs/141x0b1.pdf)
- [NASA DSOC — Deep Space Optical Communications (2023 demonstration)](https://www.jpl.nasa.gov/missions/dsoc/)
- [Hemmati, H. — "Deep Space Optical Communications" (NASA JPL, 2006)](https://ntrs.nasa.gov/citations/20060020438)

## 💡 How the Examiner Will Probe This

**Q: "Calculate the received power for an optical link at Mars's average distance of 225 million km."**
Light time: 225×10⁶ km / 299,792 km/s ≈ 750.6 seconds ≈ 12.5 min. FSPL at 1550 nm: ≈ −365 dB. With 5W TX (+37 dBm), 22 cm TX gain (~113 dBi), 1m RX gain (~117 dBi), EIRP ≈ +141 dBm. After subtracting FSPL plus atmospheric and pointing losses (~10 dB total), received power ≈ −234 dBm. That's photon-counting regime — individual photons arrive every few nanoseconds.

**Q: "How does this change at opposition vs conjunction?"**
At opposition (54.6M km), FSPL drops ~12 dB → ~16× more received power → data rates up to 200 Mbps. At conjunction (401M km), FSPL rises ~5 dB → data rate drops to ~2 Mbps. The 17 dB FSPL swing across the synodic cycle is the fundamental driver of variable data rates.

**Q: "Your margin is negative at average distance. Is the link broken?"**
The demo calculator uses simplified physics (no FEC coding gain, conservative detector model). Production systems with rate-1/2 LDPC codes recover ~8 dB, and aperture scaling to 8–12 m ground telescopes adds ~3 dB more. The link budget closes with these improvements. See DESIGN_RATIONALE.md §5 for the full derivation.

## ✅ Self-Check Questions

1. What is the FSPL at 1550 nm and 225 million km? Show the formula.
2. What are the TX and RX aperture gains for a 22 cm and 1 m telescope at 1550 nm?
3. What is the received power at average distance, and what does "photon-counting regime" mean?
4. How does the `calculate_mars_earth_link()` method map scenario names to distances?
5. Why does optical outperform RF at interplanetary distances despite higher FSPL?

## 📂 Deep Dive Resources

- **Source code:** `src/infrastructure/link_budget.py` — `LinkBudgetCalculator`, `OpticalLinkBudget`, `calculate_optical_link_budget()`
- **Demo script:** `scripts/link_budget_demo.sh` or `python src/infrastructure/link_budget.py`
- **Topic summary:** `interview_prep/topic_summaries/link_budget.md` — Optical Link Budget section
- **Mock interview:** `interview_prep/practice/mock_interview.md` — Q10 (Orbital Mechanics / FSPL calculation)
- **Cheat sheet:** `interview_prep/cheat_sheets/formulas.md` — Link Budget Equations
