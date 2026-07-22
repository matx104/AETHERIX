# Day 22: RF Link Budgets (Ka/X/S/UHF)

## 📅 Thursday, August 13, 2026

## 🎯 Learning Objective

Compute a complete RF link budget for Ka-band, including system noise temperature, carrier-to-noise ratio, and Eb/N0 — and explain why RF is AETHERIX's backup to optical despite lower data rates. This addresses exam Learning Objective 4.

## 📖 The Core Concept

While optical provides the throughput, RF provides the reliability. RF signals at Ka-band (26.5 GHz), X-band (8.4 GHz), S-band (2.3 GHz), and UHF (401 MHz) penetrate clouds, tolerate pointing errors orders of magnitude larger than optical, and have decades of flight heritage. AETHERIX's strategy is **optical primary, RF backup** — RF is always available when optical fails.

**The RF link budget chain differs from optical in three critical ways:**

1. **Antenna gain is lower.** RF parabolic dishes have much lower gain-to-size ratio than optical telescopes. A 3-meter spacecraft dish at Ka-band produces ~+52 dBi; a 34-meter DSN dish produces ~+80 dBi. Compare this to the +113 dBi of a 22 cm optical telescope. The FSPL is lower for RF (because frequency is lower), but the net effect is that RF cannot match optical's received power.

2. **Noise matters.** Unlike optical (photon-counting), RF links are noise-limited. The key metric is the system noise temperature: `Tsys = Tant + T₀·(NF_linear − 1)`, where Tant is the antenna noise temperature (deep-space sky is cold, ~50 K), T₀ is the reference temperature (290 K), and NF is the receiver noise figure. With NF = 2 dB (1.585 linear), Tsys = 50 + 290 × (1.585 − 1) ≈ 220 K. Thermal noise power is N = k·T·B, where k is Boltzmann's constant (1.38×10⁻²³ J/K) and B is bandwidth.

3. **Eb/N0 replaces SNR.** RF link quality is measured as Eb/N0 (energy per bit to noise density ratio): `Eb/N0 = C/N − 10·log₁₀(B/Rb)`, where C/N is carrier-to-noise ratio and Rb is bit rate. The required Eb/N0 depends on modulation and coding. AETHERIX uses a conservative 10 dB default (assuming legacy uncoded or light coding). Production systems with LDPC or turbo codes would recover ~8 dB.

**Ka-band link budget at average distance (225M km):**

- TX power: 20 W (+43 dBm), solid-state power amplifier
- TX antenna: 3 m dish → ~+52 dBi
- EIRP: ~+94 dBm
- FSPL at 26.5 GHz, 225M km: ~−290 dB
- RX antenna: 34 m DSN dish → ~+80 dBi
- System temperature: ~220 K
- Noise power in 12 MHz bandwidth: ~−128 dBm
- Received power: ~−133 dBm
- C/N: ~−5 dB → with Eb/N0 adjustment: margin is modest at average distance

**Why RF is the backup, not the primary:**

RF Ka-band achieves 2–6 Mbps versus optical's 10–200 Mbps. The beam divergence at Ka-band (~0.1°) is ~100× wider than optical (~10 μrad), meaning most of the transmitted energy misses the receiver. Pointing requirements are relaxed (<0.5° vs <10 μrad for optical), making RF operationally simpler. And RF penetrates clouds and rain — when all three optical ground stations are clouded out, the RF link at any DSN complex still works.

**The combined availability argument:**

If optical site availability = 95.7% (three diverse sites) and Ka-band RF availability = 99.0%, then:
```
A_combined = 1 − (1−0.957)(1−0.99) = 1 − 0.043×0.01 = 99.96%
```
This exceeds the 99.9% target. Neither layer alone meets it — optical alone (95.7%) fails the SLA; RF alone (99%) barely meets it. The hybrid exceeds it by two orders of margin.

## 🔬 In AETHERIX

The RF link budget is implemented in `src/infrastructure/rf_link_budget.py`.

The `RFLinkBudgetCalculator` class is initialized with a carrier frequency. Four frequency constants are defined:
- `KA_BAND_FREQ_HZ = 26.5e9` (26.5 GHz)
- `X_BAND_FREQ_HZ = 8.4e9` (8.4 GHz)
- `S_BAND_FREQ_HZ = 2.3e9` (2.3 GHz)
- `UHF_FREQ_HZ = 401e6` (401 MHz)

Key methods:
- `calculate_free_space_loss_db(distance_km)`: `−20·log₁₀(4π·d·f/c)` — note this uses frequency rather than wavelength, but is mathematically identical.
- `calculate_antenna_gain_dbi(diameter_m, efficiency)`: `10·log₁₀(η·(π·D·f/c)²)`.
- `calculate_system_temperature(antenna_temp_k, noise_figure_db)`: `Tant + T₀·(NF_linear − 1)` with T₀ = 290 K.
- `calculate_noise_power_dbm(system_temp_k, bandwidth_hz)`: `10·log₁₀(kTB) + 30`.
- `calculate_rf_link_budget(...)`: Complete budget from EIRP to Eb/N0 and link margin.

The `calculate_mars_earth_link(scenario)` method uses representative deep-space parameters:
- **Ka-band:** 20W TX, 3m spacecraft dish, 34m DSN RX, 10 Mbps data rate, required Eb/N0 = 10 dB.
- **UHF (surface relay):** 10W TX, 0.3m antenna, 5m RX, 256 kbps, required Eb/N0 = 9 dB.

The `RFLinkBudget` dataclass captures all 23 fields including EIRP, received power, noise power, C/N, Eb/N0, and link margin. The `__str__` method produces a formatted ASCII-art report with OPEN/CLOSED status.

## 📐 Key Numbers & Formulas

| Band | Frequency | Use Case | Max Data Rate |
|------|-----------|----------|---------------|
| Ka | 26.5 GHz | High-rate deep-space downlink | 2–6 Mbps |
| X | 8.4 GHz | Deep-space standard / conjunction fallback | 0.5–2 Mbps |
| S | 2.3 GHz | TT&C, emergency | <1 Mbps |
| UHF | 401 MHz | Mars surface relay | 64 kbps – 1 Mbps |

**Key formulas:**

```
FSPL = −20·log₁₀(4π·d·f/c)           [dB]

G_antenna = 10·log₁₀(η·(π·D·f/c)²)  [dBi]

Tsys = Tant + T₀·(10^(NF/10) − 1)   [K], T₀ = 290 K, Tant ≈ 50 K

N_noise = 10·log₁₀(k·Tsys·B) + 30   [dBm]

Eb/N0 = C/N − 10·log₁₀(B/Rb)       [dB]

Margin = Eb/N0_achieved − Eb/N0_required  [dB]
```

**Ka-band at 225M km:** Tsys ≈ 220 K, bandwidth ≈ 12 MHz, noise power ≈ −128 dBm.

## 🔗 Standards & References

- [CCSDS 401.0-B-30 — Radio Frequency and Modulation Systems](https://public.ccsds.org/Pubs/401x0b30.pdf)
- [CCSDS 131.0-B-4 — Flexible Advanced Coding and Modulation](https://public.ccsds.org/Pubs/131x0b4.pdf)
- [ITU-R P.676 — Attenuation by Atmospheric Gases](https://www.itu.int/rec/R-REC-P.676)
- [ITU-R P.618 — Propagation Data for Rain Attenuation](https://www.itu.int/rec/R-REC-P.618)
- [NASA DSN — 810-005 Telecommunications Link Design Handbook](https://deepspace.jpl.nasa.gov/dsndocs/810-005/)

## 💡 How the Examiner Will Probe This

**Q: "Why is RF the backup, not the primary?"**
RF Ka-band achieves 2–6 Mbps vs optical's 10–200 Mbps. The beam divergence is ~100× wider, so most energy misses the receiver. But RF penetrates clouds and tolerates pointing errors 500× larger. It's the guaranteed-delivery layer when optical fails. Combined availability of optical + RF exceeds 99.9%, while neither alone does.

**Q: "Calculate the system noise temperature."**
Tsys = Tant + T₀·(NF_linear − 1) = 50 + 290×(10^(2/10) − 1) = 50 + 290×0.585 ≈ 220 K. The deep-space sky is cold (50 K), but the receiver's noise figure adds thermal noise. Lower Tsys = better sensitivity — this is why DSN uses cryogenic LNAs.

**Q: "What happens during solar conjunction?"**
Ka-band degrades significantly due to solar corona plasma. X-band (8.4 GHz, lower frequency) is more resistant to coronal effects and becomes the conjunction fallback. But even X-band is degraded — the Lagrange relay path (ES-L4/L5) maintains 50–70% availability during conjunction, far better than any direct link.

## ✅ Self-Check Questions

1. Derive the system noise temperature for Tant = 50 K and NF = 2 dB. What is Tsys?
2. What is the noise power at Tsys = 220 K in a 12 MHz bandwidth?
3. Why does UHF use different TX/RX parameters than Ka-band in `calculate_mars_earth_link()`?
4. What is the Eb/N0 relationship to C/N, and how does bandwidth factor in?
5. How does the combined availability formula work? Walk through 95.7% optical + 99% RF.

## 📂 Deep Dive Resources

- **Source code:** `src/infrastructure/rf_link_budget.py` — `RFLinkBudgetCalculator`, `RFLinkBudget`, factory functions `create_ka_band_calculator()` and `create_uhf_calculator()`
- **Demo script:** `python src/infrastructure/rf_link_budget.py` (prints Ka-band and UHF budgets)
- **Topic summary:** `interview_prep/topic_summaries/link_budget.md` — RF Link Budget section
- **Cheat sheet:** `interview_prep/cheat_sheets/formulas.md` — Link Budget Equations
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §4.4 (Combined availability derivation)
