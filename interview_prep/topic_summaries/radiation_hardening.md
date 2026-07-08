# Radiation Hardening — Topic Summary

## Deep-Space Radiation Environment

Interplanetary electronics face three distinct particle populations. Each has a different energy spectrum, time profile, and damage mechanism, so they must be mitigated separately.

| Environment | Source | Dominant particles | Time profile | Primary threat |
|-------------|--------|--------------------|--------------|----------------|
| Trapped belts | Earth's magnetic field captures solar wind | Protons (MeV), electrons | Continuous, peaked at SAA / Van Allen | SEU during launch & Earth-departure burns |
| Solar particle events (SPE) | Solar flares, coronal mass ejections | Protons (10s–100s MeV), heavy ions | Bursty, hours to days, ~10³× background | SEL, burst MBUs, acute TID |
| Galactic cosmic rays (GCR) | Supernovae across the galaxy | Fully stripped ions, up to Fe (high LET) | Low, continuous flux; anti-correlated with solar cycle | Single high-LET SEU/MBU |
| Mars orbit / surface | No global magnetic field, thin CO₂ atmosphere | GCR (attenuated ~50%), SPE | Continuous | Chronic dose to electronics and crew |

Modelled in `src/computing/radiation.py` as `ENVIRONMENTS`, with representative integral particle fluxes (particles/cm²/s) and TID accumulation rates (krad(Si)/year behind ~100 mil Al):

```
leo                   flux=2.0      tid=0.1    krad/yr   (SAA trapped protons)
van_allen             flux=50.0     tid=5.0    krad/yr   (departure transit)
interplanetary        flux=4.0      tid=0.3    krad/yr   (GCR, solar minimum)
solar_particle_event  flux=1.0e4    tid=20.0   krad/yr   (peak SPE storm)
mars_surface          flux=0.7      tid=0.05   krad/yr   (post-attenuation)
```

## Single-Event Effects (SEE)

A single ionising particle deposits charge in a device, producing a transient that manifests differently depending on where it strikes. These are **stochastic** events (distinct from the cumulative TID below).

| Effect | Abbrev | Mechanism | Impact | Recoverable? |
|--------|--------|-----------|--------|--------------|
| Single-event upset | SEU | Charge flips a memory cell or register bit | Silent data corruption | Yes — rewrite, ECC, reboot |
| Multiple-bit upset | MBU | One high-LET ion flips ≥2 adjacent bits | Overwhelms simple parity | Often (with interleaving + SECDED) |
| Single-event latchup | SEL | Parasitic PNPN thyristor fires, drawing overcurrent | Destructive short if not power-cycled | Requires power cycle; can be destructive |
| Single-event transient | SET | Glitch propagates through combinational logic | Wrong combinational result (clocked in or not) | Yes if not latched |

### SEU Rate Model

The analytic SEU rate per bit per day is the product of flux, per-bit saturation cross-section, and the seconds-per-day constant:

```
rate = flux [cm^-2 s^-1] * sigma [cm^2 / bit] * 86400 [s / day]
```

With a representative commercial SRAM cross-section `sigma = 1e-12 cm^2/bit`, the interplanetary environment gives `4.0 * 1e-12 * 86400 ≈ 3.46e-7` upsets/bit/day. A radiation-hardened part (e.g. LEON3FT) reduces sigma to ~1e-14, a ~100× improvement. Implemented in `seu_rate_per_bit_day()`.

## Total Ionizing Dose (TID) and Displacement Damage

Unlike SEE, these are **cumulative** and **irreversible** — the device degrades over the mission lifetime.

| Mechanism | Cause | Effect | Metric |
|-----------|-------|--------|--------|
| TID | Ionising energy trapped in oxide layers | Threshold-voltage shift, leakage rise, timing drift | krad(Si) |
| Displacement damage (DD) | Non-ionising energy loss knocks atoms out of lattice | Solar-cell efficiency drop, sensor dark current, LED/LD degradation | MeV-equivalent displacement (NIEL) |

Dose accumulates linearly with time at the environment's `tid_rate_krad_yr`:

```
dose(t) = tid_rate_krad_yr * (t / 365.25)
margin   = device_tolerance_krad / dose(t)
```

A margin > 1 means the device survives the exposure with headroom. Reference flight parts and their TID tolerance:

| Processor | Heritage | TID tolerance | SEL |
|-----------|----------|---------------|-----|
| BAE RAD750 | Curiosity, Perseverance C&DH | **~200 krad(Si)** | Immune |
| ESA LEON3FT / GR712RC | fault-tolerant SPARC V8 | ~100–300 krad | Latchup-immune |
| Commercial SRAM-based FPGA | — | 5–30 krad | Susceptible |

The RAD750's ~200 krad tolerance against a 687-day Mars-surface mission (dose ≈ 0.1 krad) yields a margin of ~2,100× — the limiting environment is the Van Allen transit and any SPE, not the surface.

## Mitigation Techniques

### Triple Modular Redundancy (TMR)

Three identical replicas compute the same result; a majority voter outputs the answer. The system is wrong only when ≥2 replicas err simultaneously. For an independent per-replica fault probability `p`:

```
P(TMR error) = 3 p^2 (1 - p) + p^3        ≈ 3 p^2   for small p
reliability_gain = p / P(TMR error)
```

At the representative per-operation fault probability `p = 1e-4` used in the module:

```
P(TMR error) = 3.0e-8      reliability_gain = 3,334x
```

TMR is implemented in `TMRVoter` (`vote()` returns the majority and a `was_fault_masked` flag). It is the right tool for **combinational logic and control paths** (the routing decision engine), where the fault is a wrong transient result, not stored data.

### SECDED ECC Memory (Hamming + overall parity)

Single Error Correct, Double Error Detect: a Hamming code augmented with one overall parity bit. Behaviour per word read:

| Bit errors in word | Outcome |
|--------------------|---------|
| 0 | OK |
| 1 | CORRECTED (the common SEU case) |
| 2 | DETECTED_UNCORRECTABLE |
| ≥3 | SILENT_CORRUPTION (beyond code distance) |

Check-bit count is the smallest `r` with `2^r >= data_bits + r + 1`, plus one overall parity bit for double-error detection. For a 32-bit word that is 7 Hamming bits + 1 parity = 8, an `overhead_percent` of **21.9%**. Implemented in `ECCMemory.read_word()`.

### Memory Scrubbing

SECDED only helps if a second upset does not land in the same word before the first is corrected. A scrubber periodically reads, corrects, and rewrites every word, bounding the accumulation window. With upsets Poisson-distributed at mean `lambda` per word per scrub interval:

```
lambda        = rate_per_bit_s * word_bits * scrub_interval_s
P(uncorrect) = 1 - P(0) - P(1) = 1 - e^-lambda - lambda e^-lambda
```

Faster scrubbing shrinks `lambda` and drives the double-hit residual toward zero. Implemented in `MemoryScrubber`. Default scrub interval: 60 s.

### The Dominant Residual: MBU

The double-hit accumulation term is vanishingly small with 60 s scrubbing. The dominant residual is **multi-bit upsets that survive physical bit-interleaving** — a single high-LET ion flipping ≥2 bits in one logical word. Interleaving spreads a logical word across physically distant cells so most MBUs become single-bit-per-word and are corrected; an `interleave_factor` (default 0.90) is the fraction defeated. The residual is:

```
mbu_errors = raw_upsets * mbu_fraction * (1 - interleave_factor)
```

## Quantitative Transit Results (radiation.py)

Running `simulate_transit(environment="interplanetary", transit_days=210, memory_mbit=512)` reproduces the following, reproducible with seed 42:

| Metric | Value |
|--------|-------|
| Transit duration | 210 days (Hohmann-class) |
| Memory protected | 512 Mbit |
| Accumulated TID | 0.2 krad(Si) |
| Raw upsets (unprotected) | **~37,000** (37,159) |
| MBU fraction | 5% |
| Interleaving defeats | 90% of MBUs |
| Residual uncorrectable | **~186** (185.8) over mission (~0.88/day) |
| Protection factor | **~200×** fewer errors |
| TMR reliability gain (@ p=1e-4) | **~3,334×** |
| ECC storage overhead | 21.9% |

Headline result: roughly **37,000 raw upsets during a 210-day transit are reduced to ~186 uncorrectable residual errors — a ~200× overall protection factor**, with TMR adding a further ~3,334× reliability gain on combinational logic.

## Hardware vs Software Mitigation Trade-offs

| Layer | Technique | Catches | Cost | Latency |
|-------|-----------|---------|------|---------|
| Hardware (silicon) | Rad-hard process, SEL-immune layout, DICE latches | TID, SEL, most SEU | High NRE, long lead, ~100× unit cost | Zero (transparent) |
| Hardware (logic) | TMR voters, EDAC controllers | SEU/SET in logic & memory | 3× area + power for TMR, ~22% memory overhead | Zero (combinational) |
| Firmware | Scrubbing, watchdog, golden-image reload | Accumulated errors, hung state | Periodic CPU cycles | Seconds |
| Software | Checksums, redundant compute-and-compare, retry | End-to-end data integrity | CPU time, complexity | Variable |

Why not solve it all in software? Software runs on the same silicon that gets hit. A bit-flip in the program counter, a stack pointer, or the ECC logic itself defeats any purely-software scheme. Hardware mitigation (rad-hard parts, TMR, EDAC) provides a **trustworthy substrate** that software defences can then build on. The AETHERIX layering is: rad-hard processor + TMR on critical routing logic + SECDED on all memory + scrubbing + FDIR/watchdog + DTN-level CRC/retransmission — each layer assumes the one beneath is basically sound and adds independent coverage.

## FDIR State Machine and Watchdog Timer

FDIR (Fault Detection, Isolation and Recovery) is the autonomous response when the trustworthy substrate is not enough — e.g. an SET corrupts the PC, or an SEL latches a peripheral. Implemented in `FDIRController` with five states:

```
NOMINAL -> ANOMALY_DETECTED -> ISOLATED -> RECOVERING -> (NOMINAL | SAFE_MODE)
```

| State | Meaning |
|-------|---------|
| NOMINAL | All subsystems healthy, watchdog freshly kicked |
| ANOMALY_DETECTED | Subsystem reports unhealthy OR watchdog expired |
| ISOLATED | Faulty unit logically disconnected to prevent cascade |
| RECOVERING | Reset + reload from golden (read-only) image; re-kick watchdog |
| SAFE_MODE | Recovery budget exhausted; minimal-power beacon-only, await ground |

A fault is flagged when a subsystem reports unhealthy **or** the watchdog has not been kicked within `watchdog_timeout_s` (default 5 s). The watchdog is the catch-all: any failure that hangs the processor — SEU in the scheduler, infinite loop, deadlocked I/O — eventually starves the watchdog and triggers autonomous recovery without needing the fault to be explicitly detected.

Recovery is bounded: after `max_recovery_attempts` (default 3) failed resets, the controller drops to SAFE_MODE rather than reboot-loop indefinitely. This guarantees the spacecraft stays contactable (beacon-only, low power) so ground can intervene.

Demo walk-through from the module (`watchdog_timeout_s=5, max_recovery_attempts=2`):

```
t= 0s healthy=True  -> NOMINAL
t= 3s healthy=True  -> NOMINAL
t=10s healthy=True  -> NOMINAL
t=14s healthy=False -> RECOVERING   (attempt 1: reset + golden reload)
t=20s healthy=False -> RECOVERING   (attempt 2)
t=30s healthy=False -> SAFE_MODE    (budget exhausted -> beacon-only)
```

## Impact on the DTN Stack

Radiation-induced errors raise the effective bit error rate on every link and corrupt bundles held in store-and-forward buffers for hours to days. AETHERIX defends at three independent levels:

1. **Hardware**: rad-hard processor, TMR routing logic, SECDED memory with 60 s scrubbing — the ~200× protection factor above.
2. **FDIR**: watchdog + golden-image recovery keeps nodes alive without ground in the loop, despite the light-time delay (3–22 min one-way).
3. **Protocol**: LTP segment-level retransmission catches transmission errors locally; bundle CRC32 plus custody transfer catches anything that survives storage. Errors are corrected where they occur rather than forcing end-to-end retransmission across a multi-day path.

---

## Practice Questions

### Q1. "Your simulation shows ~37,000 raw upsets but only ~186 uncorrectable. Where does the ~200× come from, and what dominates the residual?"

Two mitigation layers reduce the raw count. SECDED corrects every single-bit-per-word upset, and 60 s scrubbing bounds accumulation so two independent upsets rarely land in one word before the next scrub — that term is negligible. The dominant residual is multi-bit upsets: ~5% of strikes flip ≥2 adjacent bits, of which physical bit-interleaving defeats 90%. The surviving 10% (37,000 × 0.05 × 0.10 ≈ 185) are detected but uncorrectable by SECDED, giving the ~200× protection factor. So the realistic residual is MBU-limited, not accumulation-limited, which is why bit-interleaving geometry matters more than scrub rate once you scrub often enough.

### Q2. "TMR gives a 3,334× gain at p=1e-4. Is that realistic, and why not just use TMR everywhere?"

The 3,334× figure is the closed-form `p / (3p²(1-p) + p³)` at p=1e-4, and it is honest for that p — but p is a per-operation combinational fault probability, not a memory SEU rate, and it assumes the three replicas fail independently. TMR is the right tool for **combinational logic and control paths** (the routing decision, state machines), where a wrong result is transient and the voter masks it at zero latency. It is the wrong tool for bulk memory: triplicating 512 Mbit would triple area and power for a worse result than SECDED+scrubbing gets at 22% overhead. TMR also cannot help against common-mode faults (a global clock glitch, an SET in the voter itself) and assumes independent failure — violated by an SPE that hammers all replicas at once. So: TMR on critical logic, ECC on memory, and neither alone is sufficient.

### Q3. "What actually happens when an SEL fires, given that you are 15 light-minutes from Earth?"

SEL is a parasitic short that draws overcurrent and is potentially destructive within seconds, so you cannot wait for ground. The hardware detects the overcurrent and power-cycles the affected unit autonomously (current-limited switches, latchup-current monitor). The FDIR controller then sees the unit as unhealthy, transitions NOMINAL → ANOMALY_DETECTED → ISOLATED → RECOVERING, reloads from the golden image, and re-kicks the watchdog. If the latch recurs and exhausts `max_recovery_attempts`, it drops to SAFE_MODE (beacon-only, minimal power) and waits. At no point does any of this require Earth — the round-trip light time of 30+ minutes is far longer than the destructive window, so the architecture is built around fully autonomous detection and recovery.

### Q4. "Why is TID handled by part selection rather than coding?"

TID is cumulative and irreversible: ionising charge trapped in the gate oxide shifts threshold voltages, raises leakage, and eventually pushes timing out of spec. No amount of ECC, TMR, or software can restore a transistor whose Vt has drifted — the device is permanently degraded. So TID is mitigated at the silicon level: radiation-hardened processes (thick oxides, guard rings), shielded packaging, and qualified parts with a known tolerance curve (the RAD750's ~200 krad). The software's only role is margin tracking: monitor the dose and, as the part approaches its tolerance, derate the clock or shed functions. You design TID margin in at part selection and shielding; you design SEE mitigation in at the logic and protocol level.

### Q5. "Your RAD750 has ~2,100× TID margin on the Mars surface. Isn't that absurdly over-designed?"

The surface dose is low because the thin atmosphere plus the chosen orbit attenuate GCR. But the margin has to cover the worst case, not the average: a major solar particle event during cruise can deliver on the order of the yearly interplanetary dose in a few days, and the Van Allen transit accumulates dose far faster than the surface. The same ~200 krad part that looks over-specified on the surface is what gets you safely through launch, belt transit, an SPE, and a decade of operation. Also, TID tolerance is not a tunable parameter — you buy the part that is qualified, and the RAD750 is the flight-proven choice. The "excess" surface margin is the price of a single part that survives every phase of the mission.
