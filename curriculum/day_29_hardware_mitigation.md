# Day 29: Hardware Mitigation — TMR, SECDED ECC, Rad-Hardened Processors

## 📅 August 20, 2026

## 🎯 Learning Objective

Understand the hardware-level radiation mitigation techniques that form the *trustworthy substrate* for AETHERIX's on-board computing: Triple Modular Redundancy (TMR), SECDED ECC memory (Hamming codes), radiation-hardened processors (RAD750/LEON3FT), and watchdog timers — and be able to defend *why hardware mitigation cannot be replaced by software alone*.

---

## 📖 The Core Concept

### The Trustworthy Substrate Principle

Software runs on the same silicon that gets hit by radiation. A bit-flip in the program counter, a stack pointer, or the ECC logic itself defeats any purely-software defence. Therefore, hardware mitigation must establish a *trustworthy substrate* — a computing base whose errors are masked or corrected at the transistor level — on top of which software defences (checkpointing, retries, protocol-level CRCs) can build with confidence.

### Triple Modular Redundancy (TMR)

TMR is the gold standard for protecting *combinational logic and control paths*. Three identical replicas compute the same result in parallel; a majority voter outputs the answer. The system produces a wrong result only when **two or more replicas err simultaneously**.

For an independent per-replica fault probability `p`, the probability the TMR system outputs a wrong result is:

```
P(TMR error) = 3p²(1−p) + p³   ≈  3p²   for small p
```

At `p = 1e-4` (the representative per-operation logic fault probability in AETHERIX):
```
P(TMR error) = 3(1e-4)²(1−1e-4) + (1e-4)³ ≈ 3.0e-8
Reliability gain = p / P(TMR error) = 1e-4 / 3.0e-8 ≈ 3,334×
```

TMR is the right tool for *logic* (the routing decision engine, state machines) where the fault is a wrong transient result. It is the *wrong* tool for bulk memory: triplicating 512 Mbit would triple area and power for a worse result than SECDED gets at ~22% overhead. TMR also cannot help against common-mode faults (a global clock glitch, an SET in the voter itself) and assumes the three replicas fail independently — an assumption violated by a solar particle event that hammers all three simultaneously.

### SECDED ECC Memory (Hamming + Overall Parity)

Single Error Correct, Double Error Detect (SECDED) is the workhorse for *stored data*. It augments a Hamming code with one overall parity bit:

| Bit errors in word | Outcome |
|--------------------|---------|
| 0 | OK |
| 1 | **CORRECTED** (the common SEU case) |
| 2 | DETECTED_UNCORRECTABLE (flags the error, prevents silent corruption) |
| ≥3 | SILENT_CORRUPTION (beyond the code's minimum distance) |

The check-bit count is the smallest `r` satisfying `2^r ≥ data_bits + r + 1`, plus one overall parity bit for double-error detection. For a **32-bit word**: 7 Hamming bits + 1 parity = **8 check bits**, giving an overhead of `8/32 = 21.9%`.

For a 64-bit word: 8 Hamming bits + 1 parity = 9 check bits, overhead 14.1%.

### Radiation-Hardened Processors

| Processor | Heritage | TID Tolerance | SEL | Notes |
|-----------|----------|---------------|-----|-------|
| **BAE RAD750** | Curiosity, Perseverance C&DH | **~200 krad(Si)** | Immune | PowerPC architecture, ~200 MHz |
| **ESA LEON3FT / GR712RC** | ESA missions | ~100–300 krad | Latchup-immune | SPARC V8, fault-tolerant design |
| Commercial SRAM FPGA | — | 5–30 krad | Susceptible | Not qualified for deep space |

The RAD750 is the flight-proven choice for Mars missions. Its ~200 krad tolerance against a 687-day Mars surface mission (accumulated dose ≈ 0.1 krad at 0.05 krad/yr) yields a **~2,100× margin**. This looks absurdly over-designed for the surface — but the same part must survive the Van Allen transit (5 krad/yr), a potential solar particle event (20 krad/yr peak), and a decade of operation. TID tolerance is not a tunable parameter; you buy the part that is qualified.

### Watchdog Timers

The watchdog is the catch-all for any failure that cannot be explicitly detected. A hardware timer must be "kicked" (reset) by healthy software within a timeout window (default 5 seconds in AETHERIX). If the software hangs — due to an SEU in the scheduler, an infinite loop, a deadlocked I/O — the timer expires and triggers autonomous recovery. The beauty of the watchdog is its universality: *any* failure that starves the CPU eventually triggers it, without needing to enumerate every possible fault.

---

## 🔬 In AETHERIX

`src/computing/radiation.py` implements all hardware mitigations as testable models:

**`TMRVoter`** (line 148): A dataclass with a `vote(a, b, c)` method that returns `(result, was_fault_masked)`. The majority logic: if `a == b == c`, no fault; if any two agree, the majority is returned and `corrected` increments; if all three differ, `uncorrectable` increments. The static method `system_error_probability(p)` computes the closed-form `3p²(1−p) + p³`, and `reliability_gain(p)` computes the ratio `p / system_error_probability(p)`.

**`ECCMemory`** (line 202): Models a SECDED word with `data_bits=32`. The `parity_bits` property computes the Hamming check bits dynamically. The `read_word(n_bit_errors)` method simulates reading a word that experienced N upsets, returning `("OK"|"CORRECTED"|"DETECTED_UNCORRECTABLE"|"SILENT_CORRUPTION", data_valid)`.

**`FDIRController`** (line 298): Contains the watchdog with `watchdog_timeout_s=5.0` and `max_recovery_attempts=3`. The `kick_watchdog(now_s)` method records the last kick; `detect(now_s, healthy)` checks if the watchdog has expired or the subsystem reports unhealthy.

The **`simulate_transit()`** function (line 400) runs the full end-to-end transit simulation and reports: ~37,000 raw upsets reduced to ~186 uncorrectable residual errors — a **~200× protection factor** — with TMR adding a further **~3,334× reliability gain** on combinational logic.

---

## 📐 Key Numbers & Formulas

| Number | Value | Context |
|--------|-------|---------|
| TMR system error probability @ p=1e-4 | **3.0e-8** | `3p²(1−p) + p³` |
| TMR reliability gain @ p=1e-4 | **~3,334×** | `p / P(TMR error)` |
| SECDED overhead (32-bit word) | **21.9%** | 8 check bits / 32 data bits |
| SECDED overhead (64-bit word) | **14.1%** | 9 check bits / 64 data bits |
| RAD750 TID tolerance | **200 krad(Si)** | Curiosity, Perseverance heritage |
| RAD750 surface margin | **~2,100×** | 200 krad / 0.1 krad over 687 days |
| Watchdog timeout | **5 seconds** | Default in FDIRController |
| Max recovery attempts | **3** | Before dropping to SAFE_MODE |
| Overall protection factor | **~200×** | Raw upsets → residual uncorrectable |

---

## 🔗 Standards & References

- [ECSS-E-ST-10-12C](https://ecss.nl/) — Radiation calculation standard
- [BAE RAD750 Datasheet](https://www.baesystems.com/en/product/rad750-rad-hard-powerpc) — Flight processor specification
- [ESA LEON3FT / GR712RC](https://www.gaisler.com/) — Fault-tolerant SPARC processor
- **Repo:** `src/computing/radiation.py` — `TMRVoter` (line 148), `ECCMemory` (line 202)
- **Repo:** `interview_prep/topic_summaries/radiation_hardening.md` — mitigation tables

---

## 💡 How the Examiner Will Probe This

**Q: "TMR gives a 3,334× gain. Is that realistic, and why not just use TMR everywhere?"**

> The 3,334× figure is the honest closed-form at p=1e-4. TMR is right for combinational logic and control paths where the fault is transient and the voter masks it at zero latency. It is wrong for bulk memory: triplicating 512 Mbit triples area and power for a worse result than SECDED at 22% overhead. Also, TMR assumes independent failure — an SPE that hammers all replicas violates this. So: TMR on critical logic, ECC on memory, and neither alone is sufficient.

**Q: "What's the difference between SECDED and TMR?"**

> SECDED corrects single-bit errors in *memory* at the hardware level — it is passive and always on, with 22% storage overhead. TMR is active redundancy for *computation* — the same calculation runs three times in parallel, a voter selects the majority. SECDED handles stored data errors; TMR handles logic errors from transient faults.

**Q: "Your RAD750 has ~2,100× TID margin on the Mars surface. Isn't that absurdly over-designed?"**

> The surface dose is low because the thin atmosphere attenuates GCR. But the margin covers the *worst case across all mission phases*: Van Allen transit (5 krad/yr), a major SPE (20 krad/yr peak), and a decade of operation. TID tolerance is not tunable — you buy the qualified part. The RAD750 is the flight-proven choice that survives every phase.

---

## ✅ Self-Check Questions

1. Derive the TMR system error probability formula. Why is it ≈ 3p² for small p?
2. How many check bits does SECDED require for a 64-bit data word? What is the overhead percentage?
3. Why is TMR the wrong choice for protecting 512 Mbit of bulk memory?
4. What happens if all three TMR replicas are struck simultaneously by a solar particle event?
5. Calculate the RAD750's TID margin for a 210-day transit through the Van Allen belts at 5 krad/yr.

---

## 📂 Deep Dive Resources

- **Source code:** `src/computing/radiation.py` — `TMRVoter`, `ECCMemory`, `FDIRController`
- **Topic summary:** `interview_prep/topic_summaries/radiation_hardening.md`
- **Mock interview:** Q12 and Q12 follow-up in `interview_prep/practice/mock_interview.md`
- **Demo:** Run `python src/computing/radiation.py` for the live TMR/ECC/FDIR demo
- **Design rationale:** `docs/DESIGN_RATIONALE.md` §1.4 (triple diversity principle)
