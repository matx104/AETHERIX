# Day 26: Doppler Shift Compensation

## 📅 Monday, August 17, 2026

## 🎯 Learning Objective

Calculate both classical and relativistic Doppler shifts for AETHERIX's optical and RF links, explain pre-compensation via orbital prediction, and describe how Doppler rate provides orbit determination data. This addresses exam Learning Objective 4.

## 📖 The Core Concept

Doppler shift is the change in observed frequency caused by relative motion between transmitter and receiver. When a source moves toward you, its frequency appears higher (blueshift); when it recedes, the frequency appears lower (redshift). In interplanetary communications, Doppler shift is not a minor correction — it is enormous, and failing to compensate for it means losing the signal entirely.

**The classical Doppler shift:**

For relative radial velocity v (positive when receding) and carrier frequency f₀, the first-order classical shift is:

```
Δf = −f₀ × (v / c)
```

The maximum relative radial velocity between Earth and Mars is approximately **24 km/s**, occurring near quadrature when the planets' velocity vectors are partially aligned with the line of sight. At 24 km/s:

- **Optical (1550 nm, 193.4 THz):** Δf = 193.4×10¹² × 24,000 / 299,792,458 ≈ **±15.5 GHz**
- **Ka-band (26.5 GHz):** Δf = 26.5×10⁹ × 24,000 / 299,792,458 ≈ **±2.1 GHz**
- **UHF (401 MHz):** Δf = 401×10⁶ × 24,000 / 299,792,458 ≈ **±32 MHz**

These are staggering shifts. A 15.5 GHz shift on an optical carrier means the received frequency deviates by the bandwidth of thousands of RF channels. Without compensation, the receiver's narrow filter would completely miss the signal.

**The relativistic Doppler correction:**

For the precision required in coherent optical detection, the classical approximation is insufficient. The full special-relativistic formula is:

```
f_observed = f₀ × √((1 − β) / (1 + β))
```

where β = v/c. The difference between classical and relativistic predictions is small but measurable: at v = 24 km/s, the relativistic correction is on the order of 10⁻⁸ relative, which at 193.4 THz translates to a measurable difference in the Hz range. This matters for long-integration-phase measurements and coherent detection where sub-Hz precision is needed.

**Doppler rate — the second derivative:**

Equally important is the **rate of change** of Doppler shift (Doppler rate):

```
d(Δf)/dt = f₀ × (a_radial / c)
```

For Earth-Mars links, Doppler rate can reach ~10 kHz/s at Ka-band and ~60 kHz/s at optical frequencies. The receiver's phase-locked loop (PLL) must track these frequency sweeps in real-time. If the Doppler rate exceeds the PLL's tracking bandwidth, the receiver loses lock.

**Compensation strategy:**

AETHERIX uses **predictive pre-compensation** based on orbital mechanics:

1. **Predict the Doppler shift** from orbital propagation. The `doppler.py` module computes both classical and relativistic shifts given the predicted relative velocity.
2. **Pre-shift the transmit frequency** by the predicted Δf. The transmitter intentionally offsets its carrier so that after Doppler shift, the received frequency lands exactly at the nominal center frequency.
3. **Residual tracking** at the receiver. After pre-compensation, the residual Doppler (from prediction errors, perturbations, etc.) is small enough for the PLL to track with its standard bandwidth.

This approach is critical because at 22-minute one-way light time, closed-loop feedback is too slow. By the time the receiver measures the Doppler and sends correction commands, the signal is already 22 minutes old. Pre-compensation based on orbital prediction eliminates the need for real-time feedback.

**Doppler as a measurement tool:**

Doppler shift is not just a nuisance — the rate of change of Doppler (Doppler rate) provides **orbit determination** data. By precisely measuring the received frequency over time, ground stations can reconstruct the spacecraft's trajectory. NASA's DSN has used Doppler tracking for orbit determination since the 1960s. AETHERIX leverages this: predicted Doppler from orbital propagation is compared against measured Doppler, and the residual provides ranging data that improves future predictions.

## 🔬 In AETHERIX

Doppler calculations are implemented in `src/orbital/doppler.py`.

Constants:
```python
OPTICAL_CARRIER_FREQ_HZ = 193.4e12   # 1550 nm
KA_BAND_FREQ_HZ = 26.5e9             # Ka-band
UHF_FREQ_HZ = 401.0e6                # UHF
MAX_EARTH_MARS_RELATIVE_VELOCITY = 24.0  # km/s
```

The `DopplerResult` dataclass captures the full result:
```python
@dataclass(frozen=True)
class DopplerResult:
    frequency_shift_hz: float          # relativistic shift
    shifted_frequency_hz: float        # f₀ + shift
    velocity_km_s: float               # input velocity
    relativistic_correction: float     # relativistic − classical
```

Functions:
- `calculate_classical_doppler(velocity_km_s, frequency_hz)`: Returns `−f × (v/c)`. Positive velocity = receding (redshift / negative shift).
- `calculate_relativistic_doppler(velocity_km_s, frequency_hz)`: Returns `f × √((1−β)/(1+β)) − f`. Uses the full special-relativistic formula.
- `calculate_doppler_with_result(velocity_km_s, frequency_hz)`: Returns a full `DopplerResult` including the difference between relativistic and classical predictions.

The orbital mechanics module (`contact_windows.py`) also has a `calculate_doppler_shift(relative_velocity_km_s, frequency_hz)` function using the classical formula `f × (v/c)`.

## 📐 Key Numbers & Formulas

| Link Type | Carrier Frequency | Max Doppler (v=24 km/s) | Max Doppler Rate |
|-----------|-------------------|------------------------|------------------|
| Optical (1550 nm) | 193.4 THz | ±15.5 GHz | ~60 kHz/s |
| Ka-band | 26.5 GHz | ±2.1 GHz | ~10 kHz/s |
| UHF | 401 MHz | ±32 MHz | ~130 Hz/s |

**Classical Doppler:**
```
Δf = −f₀ × (v / c)     [Hz]
```

**Relativistic Doppler:**
```
f_obs = f₀ × √((1 − β) / (1 + β))     where β = v/c
Δf_rel = f_obs − f₀
```

**Doppler rate:**
```
d(Δf)/dt = f₀ × (a_radial / c)     [Hz/s]
```

## 🔗 Standards & References

- [CCSDS 401.0-B-30 — RF and Modulation Systems (Doppler compensation)](https://public.ccsds.org/Pubs/401x0b30.pdf)
- [CCSDS 141.0-B-1 — Optical Communications (frequency tracking)](https://public.ccsds.org/Pubs/141x0b1.pdf)
- [DSN — 810-005 Handbook, Module 207 (Doppler compensation)](https://deepspace.jpl.nasa.gov/dsndocs/810-005/207/)
- [NASA — Doppler Tracking](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/)

## 💡 How the Examiner Will Probe This

**Q: "What is the Doppler shift at 1550 nm with v = 24 km/s, and how do you compensate?"**
Δf = 193.4 THz × 24,000 / 299,792 km/s ≈ ±15.5 GHz. Compensation: (1) predict the shift from orbital propagation using `doppler.py`, (2) pre-shift the transmit frequency so the received signal lands at nominal center, (3) PLL at the receiver tracks the small residual. This pre-compensation is essential because at 22-min light time, closed-loop feedback is too slow.

**Q: "Why model both classical and relativistic Doppler?"**
The relativistic correction is small (~10⁻⁸ relative) but measurable at optical frequencies — in the Hz range at 193.4 THz. For coherent optical detection requiring sub-Hz precision over long integration phases, the classical approximation introduces errors that degrade signal quality. The relativistic formula uses f_obs = f × √((1−β)/(1+β)).

**Q: "What is Doppler rate, and why does it matter?"**
Doppler rate is d(Δf)/dt = f₀ × (a_radial / c). At Ka-band it reaches ~10 kHz/s. The receiver's PLL must track this frequency sweep. If the rate exceeds the PLL's tracking bandwidth, the receiver loses lock. Doppler rate also provides orbit determination data — comparing predicted vs measured Doppler rate helps refine orbital state estimates.

## ✅ Self-Check Questions

1. Calculate the classical Doppler shift for Ka-band at 26.5 GHz with v = 24 km/s.
2. What is the difference between the classical and relativistic Doppler formulas? When does the correction matter?
3. Why is pre-compensation necessary at interplanetary distances, and why can't closed-loop feedback work?
4. What is the maximum relative radial velocity between Earth and Mars, and when does it occur?
5. How does the `DopplerResult` dataclass's `relativistic_correction` field help assess model accuracy?

## 📂 Deep Dive Resources

- **Source code:** `src/orbital/doppler.py` — `calculate_classical_doppler()`, `calculate_relativistic_doppler()`, `calculate_doppler_with_result()`, `DopplerResult`
- **Orbital module:** `src/orbital/contact_windows.py` — `calculate_doppler_shift()` (classical), `LinkGeometry.doppler_shift_hz`
- **Topic summary:** `interview_prep/topic_summaries/orbital_mechanics.md` — Doppler Shift and Doppler Calculator sections
- **Design rationale:** `docs/DESIGN_RATIONALE.md` — §7 (Doppler shift compensation strategy)
- **Cheat sheet:** `interview_prep/cheat_sheets/formulas.md` — Doppler Shift section
