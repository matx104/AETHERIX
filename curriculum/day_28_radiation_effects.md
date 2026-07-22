# Day 28: Radiation Effects on Space Electronics

## 📅 August 19, 2026

## 🎯 Learning Objective

Master the six radiation effects that threaten interplanetary electronics (SEU, SEL, MBU, SET, TID, Displacement Damage) and understand why the Mars radiation environment — with no global magnetic field — demands dedicated mitigation, directly supporting **exam objective 2(e): hardware resilience and radiation-hardened computing**.

---

## 📖 The Core Concept

Space is not a vacuum for electronics — it is a constant bombardment of ionising particles. Every transistor orbiting between Earth and Mars is struck by radiation that would instantly corrupt or destroy consumer hardware. To design a survivable interplanetary network, you must first understand *what* radiation does to silicon, and *why* each effect demands a different defence.

### The Particle Environment

Three distinct populations of particles fill interplanetary space:

1. **Trapped belts** — Earth's magnetic field captures solar wind protons and electrons, concentrating them in the Van Allen belts and the South Atlantic Anomaly (SAA). Any spacecraft leaving Earth transits this intense region.

2. **Solar Particle Events (SPE)** — Solar flares and coronal mass ejections (CMEs) blast out proton storms with fluxes up to 10,000× the background rate. These are *bursty*, lasting hours to days, and pose the greatest acute threat.

3. **Galactic Cosmic Rays (GCR)** — Supernovae across the galaxy produce fully-stripped ions up to iron (Fe-56) with extremely high Linear Energy Transfer (LET). The flux is low (a few particles per cm² per second) but continuous, and these high-LET ions are the dominant cause of single-event upsets.

### Mars Has No Shield

Earth's magnetic field deflects most charged particles, and its thick atmosphere absorbs the remainder. Mars has **neither** — no global magnetic field and only a thin CO₂ atmosphere (~0.6% of Earth's surface pressure). This means the Mars surface receives roughly half the GCR flux of free space, but is far more exposed than Earth. Electronics and any future crew face chronic dose accumulation.

### The Six Effects

Radiation effects divide into two families: **single-event effects (SEE)** — stochastic, instantaneous strikes by individual particles — and **cumulative effects** — gradual degradation from dose accumulation over the mission lifetime.

**Single-Event Upset (SEU):** A charged particle passes through a memory cell or register, depositing enough charge to flip a bit. The cell itself is undamaged — rewriting the correct value restores normal operation. SEUs are the most common radiation effect and the primary target of ECC and TMR.

**Multiple-Bit Upset (MBU):** A single high-LET ion deposits charge across *multiple adjacent cells* in one strike. This overwhelms simple parity checks because two or more bits in the same word are corrupted simultaneously. MBUs are increasingly common as device geometries shrink.

**Single-Event Latchup (SEL):** Ionising charge triggers a parasitic PNPN thyristor structure inherent in CMOS, creating a low-impedance short circuit. This draws overcurrent and is *potentially destructive* within seconds if not power-cycled. SEL-immune processes (epitaxial layers, guard rings) are a primary reason rad-hard parts exist.

**Single-Event Transient (SET):** A particle strike produces a transient voltage glitch in combinational logic. If the glitch propagates to a flip-flop and is clocked in, it becomes a permanent error; if not, it dissipates harmlessly. SETs are the reason TMR protects combinational paths.

**Total Ionizing Dose (TID):** Ionising energy trapped in gate oxide layers shifts transistor threshold voltages, increases leakage current, and degrades timing margins — *cumulatively and irreversibly*. Measured in krad(Si). No amount of software can restore a transistor whose Vₜ has drifted past spec.

**Displacement Damage (DD):** Non-ionising energy loss knocks atoms out of the semiconductor lattice. This degrades solar cell efficiency, increases sensor dark current, and dims laser diodes — effects measured via the Non-Ionising Energy Loss (NIEL) function.

The critical distinction for the examiner: SEE are *stochastic* (random strikes, mitigable by redundancy) while TID and DD are *cumulative* (dose-driven, mitigable only by part selection and shielding).

---

## 🔬 In AETHERIX

The entire radiation environment model lives in `src/computing/radiation.py`. The `RadiationEffect` enum defines all six effects with two key properties:

- `is_destructive` → returns `True` for SEL, TID, and DD (permanent damage)
- `is_recoverable` → returns `True` for SEU, MBU, and SET (soft errors fixable by ECC/reboot)

The `RadiationEnvironment` dataclass characterises each environment with a `particle_flux` (particles/cm²/s) and a `tid_rate_krad_yr` (krad(Si)/year behind ~100 mil Al shielding). Five environments are pre-defined in the `ENVIRONMENTS` dictionary:

```python
"interplanetary":    flux=4.0,    tid=0.3   krad/yr   (GCR, solar minimum)
"solar_particle_event": flux=1.0e4, tid=20.0  krad/yr  (peak SPE storm)
"mars_surface":      flux=0.7,    tid=0.05  krad/yr   (post-attenuation)
```

The SEU rate per bit per day follows a simple analytic model: `rate = flux × σ × 86400`, where σ is the per-bit saturation cross-section (default 1e-12 cm²/bit for commercial SRAM, ~1e-14 for rad-hard). The `tid_after(days)` method computes accumulated dose, and `margin_against(tolerance, days)` returns the design margin — the RAD750's 200 krad tolerance against a 687-day Mars surface mission yields a ~2,100× margin.

---

## 📐 Key Numbers & Formulas

| Number | Value | Context |
|--------|-------|---------|
| Interplanetary GCR flux | **4.0** particles/cm²/s | Solar minimum, deep cruise |
| Peak SPE flux | **10,000** particles/cm²/s | 2,500× the GCR background |
| Mars surface flux | **0.7** particles/cm²/s | ~50% attenuation of free-space GCR |
| Commercial σ (SEU cross-section) | **1e-12** cm²/bit | Representative SRAM |
| Rad-hard σ | **~1e-14** cm²/bit | ~100× fewer upsets |
| SEU rate formula | `flux × σ × 86400` | Upsets per bit per day |
| Interplanetary SEU rate | **~3.46e-7** upsets/bit/day | At σ = 1e-12 |
| TID dose formula | `tid_rate × (days / 365.25)` | krad(Si) |
| SEL destructive window | **seconds** | Must power-cycle before thermal damage |

---

## 🔗 Standards & References

- [ECSS-E-ST-10-12C](https://ecss.nl/standard/ecss-e-st-10-12c-rev-1-space-engineering-methods-for-calculation-of-radiation-received-by-electronic-components/) — Calculation of radiation-induced effects
- [JESD57 / JESD89](https://www.jedec.org/) — SEU/SEE test and reporting methods
- [NASA Radiation Hardening Overview](https://radhome.gsfc.nasa.gov/) — Radiation effects and mitigation
- **Repo:** `src/computing/radiation.py` (lines 52–122)
- **Repo:** `interview_prep/topic_summaries/radiation_hardening.md`

---

## 💡 How the Examiner Will Probe This

**Q: "Your simulation shows ~37,000 raw upsets during a 210-day transit. Where does that number come from?"**

> Walk through the formula: `rate = 4.0 × 1e-12 × 86400 = 3.46e-7` upsets/bit/day. Over 512 Mbit (5.12e8 bits) × 210 days: `3.46e-7 × 5.12e8 × 210 ≈ 37,000`. State that the model is analytic (flux × cross-section), not device-qualified — representative order-of-magnitude figures from the ECSS/JESD89 literature.

**Q: "Why is the Mars radiation environment described as 'harsh' when the surface flux is lower than interplanetary?"**

> The flux is lower (~0.7 vs 4.0) because the thin atmosphere attenuates ~50% of GCR. But Mars has no global magnetic field, so there is no magnetospheric deflection of charged particles — unlike Earth, which rejects most particles before they reach the atmosphere. The cumulative dose and SEU risk on the Mars surface are still significant over a multi-year mission, and any SPE is largely unattenuated.

**Q: "What's the fundamental difference between SEE and TID from an engineering standpoint?"**

> SEE are stochastic and recoverable — you mitigate them with redundancy (TMR, ECC) that masks or corrects the transient error. TID is cumulative and irreversible — the transistor physically degrades, and no amount of redundancy restores it. You mitigate TID at the *silicon level* (rad-hard processes, shielding) at part selection time, not at runtime.

---

## ✅ Self-Check Questions

1. Which three radiation effects are classified as *destructive* in the AETHERIX model, and why?
2. What is the difference between an SEU and an MBU, and why does an MBU overwhelm simple parity?
3. Calculate the accumulated TID for a 210-day interplanetary transit at 0.3 krad/yr.
4. Why does Mars have no equivalent of Earth's South Atlantic Anomaly?
5. If you halve the device cross-section from 1e-12 to 5e-13, what happens to the SEU rate?

---

## 📂 Deep Dive Resources

- **Source code:** `src/computing/radiation.py` — `RadiationEffect`, `RadiationEnvironment`, `ENVIRONMENTS`
- **Topic summary:** `interview_prep/topic_summaries/radiation_hardening.md` — full quantitative tables
- **Demo site:** [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX) → Radiation module
- **Mock interview Q12:** `interview_prep/practice/mock_interview.md`
- **External:** ECSS-E-ST-10-12C Rev.1 (radiation calculation standard)
