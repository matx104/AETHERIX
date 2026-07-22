# Day 23: Free Space Path Loss Mathematics

## 📅 Friday, August 14, 2026

## 🎯 Learning Objective

Derive the Free Space Path Loss (FSPL) formula from first principles, compute it at 1550 nm across the full range of Earth-Mars distances (54.6M km to 401M km), and explain the ~17 dB opposition-to-conjunction variation that drives AETHERIX's data rate range from 200 Mbps to 2 Mbps. This addresses exam Learning Objective 4.

## 📖 The Core Concept

Free Space Path Loss (FSPL) is the single most important quantity in deep-space communications. It represents how much signal power is lost as electromagnetic radiation spreads over the enormous distances between planets. Understanding FSPL is understanding why interplanetary communication is hard.

**The physics derivation:**

Imagine a transmitter at the centre of a sphere. The radiated power spreads uniformly over the sphere's surface. At distance d, the sphere's surface area is 4πd². A receiving antenna with effective area A_eff captures a fraction A_eff / (4πd²) of the total power. This geometric dilution is the physical origin of FSPL.

For an isotropic radiator (one that radiates equally in all directions), the power density at distance d is:

```
S = P_tx / (4πd²)          [W/m²]
```

The "path loss" is the ratio of transmitted power to received power when both antennas are isotropic. For a signal at wavelength λ, the effective area of an isotropic antenna is λ²/4π. So:

```
FSPL = P_tx / P_rx = (4πd²) / (λ²/4π) = (4πd/λ)²
```

In decibels:

```
FSPL_dB = 20·log₁₀(4πd/λ)
```

Since c = λ·f, this can also be written as:

```
FSPL_dB = 20·log₁₀(4π·d·f / c) = 20·log₁₀(d) + 20·log₁₀(f) − 147.55
```

The last form separates the distance term from the frequency term — useful for quick mental estimates.

**Computing FSPL at 1550 nm across the synodic cycle:**

| Scenario | Distance | FSPL (1550 nm) |
|----------|----------|----------------|
| Opposition (closest) | 54.6M km | ~353 dB |
| Quadrature | ~150M km | ~362 dB |
| Average | 225M km | ~365 dB |
| Conjunction (farthest) | 401M km | ~370 dB |

Let's verify the average case:
```
FSPL = 20·log₁₀(4π × 225×10⁹ m / 1.55×10⁻⁶ m)
     = 20·log₁₀(4π × 1.45×10¹⁷)
     = 20·log₁₀(1.82×10¹⁸)
     = 20 × 18.26
     = 365.2 dB
```

**The 6 dB per doubling rule:**

FSPL increases by 6.02 dB for every doubling of distance (one octave). This comes directly from the 20·log₁₀(d) term — log₁₀(2) ≈ 0.301, so 20 × 0.301 = 6.02 dB.

The Earth-Mars distance ratio from opposition to conjunction is 401/54.6 ≈ 7.3. In dB: 20·log₁₀(7.3) ≈ 17.3 dB. This 17 dB swing is the fundamental driver of AETHERIX's variable data rate — from 200 Mbps at opposition to 2 Mbps at conjunction, a factor of 100 (20 dB in power terms).

**Why FSPL is worse at optical than RF:**

At 1550 nm (193.4 THz), the FSPL at 225M km is ~365 dB. At Ka-band (26.5 GHz), the FSPL at the same distance is ~294 dB — about 71 dB less loss. This seems to favour RF. But optical telescopes achieve far higher gain than RF dishes of comparable size (because gain scales as (D/λ)², and λ is 100,000× smaller for optical). The net result: optical's higher antenna gains more than compensate for the higher FSPL, enabling Gbps-class links that RF cannot match.

**What FSPL does NOT include:**

FSPL is purely geometric spreading. It does not account for atmospheric absorption, rain fade, pointing errors, or implementation losses. These are added separately in the full link budget. In deep space, the propagation path is almost entirely vacuum, so FSPL dominates and other losses are small by comparison.

## 🔬 In AETHERIX

Both link budget calculators implement FSPL:

**Optical** (`src/infrastructure/link_budget.py`):
```python
def calculate_free_space_loss_db(self, distance_km):
    distance_m = distance_km * 1000
    fspl = (4 * math.pi * distance_m / self.wavelength_m) ** 2
    return -10 * math.log10(fspl)
```
This returns `−10·log₁₀((4πd/λ)²) = −20·log₁₀(4πd/λ)` — the FSPL as a negative dB value representing loss.

**RF** (`src/infrastructure/rf_link_budget.py`):
```python
def calculate_free_space_loss_db(self, distance_km):
    distance_m = distance_km * 1000
    fspl_ratio = 4 * math.pi * distance_m * self.frequency_hz / SPEED_OF_LIGHT_M_S
    return -20 * math.log10(fspl_ratio)
```
This uses frequency instead of wavelength: `−20·log₁₀(4πdf/c)`. Mathematically identical since c = λf.

Both calculators are initialized with the respective carrier (1550 nm wavelength for optical, 26.5 GHz frequency for Ka-band). The `calculate_mars_earth_link(scenario)` methods apply FSPL at "minimum" (55M km), "average" (225M km), or "maximum" (401M km) distance.

The orbital mechanics module (`src/orbital/contact_windows.py`) provides the `estimate_data_rate(distance_km)` function that uses the inverse-square relationship: `rate = 200 × (54.6M/d)²`, clamped to [2, 200] Mbps. This directly encodes the FSPL-driven data rate variation.

## 📐 Key Numbers & Formulas

**Master FSPL formula:**
```
FSPL = 20·log₁₀(4πd/λ)  =  20·log₁₀(4πdf/c)  =  20·log₁₀(d) + 20·log₁₀(f) − 147.55
```

| Earth-Mars Distance | Light Time | FSPL at 1550 nm | FSPL at Ka-band (26.5 GHz) |
|---------------------|------------|-----------------|---------------------------|
| 54.6M km (opposition) | 3.0 min | ~353 dB | ~282 dB |
| 225M km (average) | 12.5 min | ~365 dB | ~294 dB |
| 401M km (conjunction) | 22.3 min | ~370 dB | ~299 dB |

**Key relationships:**
- FSPL increases **6 dB per distance doubling**
- Opposition-to-conjunction swing: `20·log₁₀(401/54.6) ≈ 17.3 dB`
- Data rate varies as 1/d²: 200 Mbps → 2 Mbps = 100× ratio = 20 dB

## 🔗 Standards & References

- [CCSDS 141.0-B-1 — Optical Communications Physical Layer](https://public.ccsds.org/Pubs/141x0b1.pdf)
- [CCSDS 401.0-B-30 — RF and Modulation Systems](https://public.ccsds.org/Pubs/401x0b30.pdf)
- [Kraus, J.D. — "Radio Astronomy" (1966), Ch. 3 — FSPL derivation](https://books.google.com/books?id=RFtRAAAAMAAJ)

## 💡 How the Examiner Will Probe This

**Q: "Calculate the free-space path loss for a 1550 nm optical link at 225 million km."**
FSPL = 20·log₁₀(4π × 225×10⁹ / 1.55×10⁻⁶) = 20·log₁₀(1.82×10¹⁸) = 20 × 18.26 = **365.2 dB**. This is the fundamental challenge — 365 dB of signal attenuation.

**Q: "How does FSPL change between opposition and conjunction?"**
Distance ratio: 401/54.6 ≈ 7.3. FSPL swing: 20·log₁₀(7.3) ≈ 17.3 dB. This 17 dB variation is why the data rate swings from 200 Mbps (opposition) to 2 Mbps (conjunction) — a factor of 100.

**Q: "Why is optical FSPL 71 dB worse than Ka-band at the same distance?"**
FSPL scales as 20·log₁₀(f). The frequency ratio: 193.4 THz / 26.5 GHz ≈ 7,300. In dB: 20·log₁₀(7,300) ≈ 77 dB. Optical FSPL is ~77 dB worse, but optical antenna gain compensates by more than that — a 22 cm telescope at 1550 nm gives +113 dBi vs +52 dBi for a 3 m dish at Ka-band.

## ✅ Self-Check Questions

1. Derive FSPL from the sphere-spreading argument. Why does it scale as (4πd/λ)²?
2. What is the "6 dB per doubling" rule, and where does it come from?
3. Compute FSPL at 1550 nm and 54.6 million km. Verify against the opposition value.
4. Why does `estimate_data_rate()` in `contact_windows.py` use an inverse-square relationship?
5. Express FSPL as 20·log₁₀(d) + 20·log₁₀(f) − 147.55. Where does the −147.55 come from?

## 📂 Deep Dive Resources

- **Source code:** `src/infrastructure/link_budget.py` — `calculate_free_space_loss_db()` (optical); `src/infrastructure/rf_link_budget.py` — same method (RF)
- **Orbital module:** `src/orbital/contact_windows.py` — `estimate_data_rate()` (inverse-square data rate)
- **Topic summary:** `interview_prep/topic_summaries/link_budget.md` — FSPL section
- **Mock interview:** `interview_prep/practice/mock_interview.md` — Q10 (FSPL calculation)
- **Cheat sheet:** `interview_prep/cheat_sheets/formulas.md` — FSPL equations
