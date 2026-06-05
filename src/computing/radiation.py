"""
AETHERIX Radiation-Hardened Computing Module
=============================================

Simulates the space radiation environment and the fault-tolerance mechanisms
that let on-board computers survive it during an Earth-Mars mission.

Covered effects (CCSDS / ECSS terminology):
    SEU  - Single Event Upset      : a bit flip in memory/register
    MBU  - Multiple Bit Upset      : >1 bit flipped by one particle
    SEL  - Single Event Latchup    : parasitic short, needs power cycle
    SET  - Single Event Transient  : transient glitch in combinational logic
    TID  - Total Ionizing Dose     : cumulative dose degradation (krad)
    DD   - Displacement Damage      : lattice damage from non-ionizing dose

Mitigations modelled:
    TMR          - Triple Modular Redundancy (majority voter)
    ECC / SECDED - Single Error Correct, Double Error Detect (Hamming)
    Scrubbing    - periodic rewrite of corrected memory before 2nd upset
    FDIR         - Fault Detection, Isolation and Recovery state machine
                   with a watchdog timer

MODELLING HONESTY
-----------------
This is a *transparent analytic model*, not a device qualification. SEU rates
are computed as `flux * per-bit saturation cross-section`, using representative
order-of-magnitude figures from the radiation-effects literature (ECSS-E-ST-10-12C,
JESD89, RAD750/LEON3FT datasheets). Real rates depend on the LET spectrum, device
geometry and shielding; here we use a single effective cross-section and an
integral flux. Stochastic demos use a fixed seed (default 42) for reproducibility.

Reference standards / heritage:
- ECSS-E-ST-10-12C  : Calculation of radiation-induced effects
- JESD57 / JESD89   : SEU/SEE test and reporting methods
- NASA RAD750 (BAE) : ~200 krad(Si) TID, SEL-immune flight processor (Curiosity,
                      Perseverance C&DH heritage)
- ESA LEON3FT / GR712RC : fault-tolerant SPARC V8 flight processor

Reference: AETHERIX Topic 59, learning objective (e).
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

# Seconds per day, used to convert per-second rates to per-day figures.
SECONDS_PER_DAY = 86_400


class RadiationEffect(Enum):
    """Single Event and cumulative radiation effects on electronics."""
    SEU = "Single Event Upset"          # recoverable bit flip
    MBU = "Multiple Bit Upset"          # multiple adjacent bits flipped
    SEL = "Single Event Latchup"        # potentially destructive, power cycle
    SET = "Single Event Transient"      # combinational glitch
    TID = "Total Ionizing Dose"         # cumulative degradation
    DD = "Displacement Damage"          # lattice damage (solar cells, sensors)

    @property
    def is_destructive(self) -> bool:
        """SEL and severe TID/DD can permanently damage hardware."""
        return self in (RadiationEffect.SEL, RadiationEffect.TID, RadiationEffect.DD)

    @property
    def is_recoverable(self) -> bool:
        """Soft errors recoverable by ECC/TMR/reboot."""
        return self in (RadiationEffect.SEU, RadiationEffect.MBU, RadiationEffect.SET)


@dataclass
class RadiationEnvironment:
    """
    A space radiation environment characterised for SEU estimation.

    Attributes:
        name: human-readable label
        particle_flux: integral ionising-particle flux [particles / cm^2 / s]
        tid_rate_krad_yr: total ionising dose accumulation [krad(Si) / year]
                          behind nominal spacecraft shielding (~100 mil Al)
        description: where this environment is encountered
    """
    name: str
    particle_flux: float           # particles / cm^2 / s
    tid_rate_krad_yr: float        # krad(Si) / year
    description: str = ""

    def tid_after(self, days: float) -> float:
        """Accumulated TID in krad(Si) after a given number of days."""
        return self.tid_rate_krad_yr * (days / 365.25)

    def margin_against(self, device_tid_tolerance_krad: float, days: float) -> float:
        """
        Design margin = device tolerance / accumulated dose.
        > 1 means the device survives the exposure with margin.
        """
        dose = self.tid_after(days)
        if dose <= 0:
            return float("inf")
        return device_tid_tolerance_krad / dose


# Representative environments (order-of-magnitude; see MODELLING HONESTY note).
# Flux figures are effective integral fluxes used to drive the analytic SEU model.
ENVIRONMENTS: Dict[str, RadiationEnvironment] = {
    "leo": RadiationEnvironment(
        "Low Earth Orbit (incl. SAA)", particle_flux=2.0, tid_rate_krad_yr=0.1,
        description="Trapped protons in the South Atlantic Anomaly dominate SEU."),
    "van_allen": RadiationEnvironment(
        "Van Allen Belt transit", particle_flux=50.0, tid_rate_krad_yr=5.0,
        description="Intense trapped-particle belts crossed when leaving Earth."),
    "interplanetary": RadiationEnvironment(
        "Interplanetary cruise (GCR)", particle_flux=4.0, tid_rate_krad_yr=0.3,
        description="Galactic cosmic rays at solar minimum; few but very high-LET ions."),
    "solar_particle_event": RadiationEnvironment(
        "Solar Particle Event (peak)", particle_flux=1.0e4, tid_rate_krad_yr=20.0,
        description="Solar flare/CME proton storm; orders of magnitude flux spike."),
    "mars_surface": RadiationEnvironment(
        "Mars surface", particle_flux=0.7, tid_rate_krad_yr=0.05,
        description="Thin atmosphere + no global field; ~half the GCR of free space."),
}


# --- Single Event Upset rate model -----------------------------------------

def seu_rate_per_bit_day(
    flux: float,
    cross_section_cm2_per_bit: float = 1.0e-12,
) -> float:
    """
    Analytic SEU rate per bit per day.

        rate = flux [cm^-2 s^-1] * sigma [cm^2/bit] * 86400 [s/day]

    Default sigma = 1e-12 cm^2/bit is a representative *commercial* SRAM
    saturation cross-section. A radiation-hardened part is typically
    1e-14 cm^2/bit or better (~100x fewer upsets).

    Returns upsets per bit per day.
    """
    return flux * cross_section_cm2_per_bit * SECONDS_PER_DAY


# --- Triple Modular Redundancy ----------------------------------------------

@dataclass
class TMRVoter:
    """
    Triple Modular Redundancy majority voter.

    Three replicas compute the same result; the voter outputs the majority.
    The system only produces a wrong answer when >= 2 replicas are wrong,
    so for an independent per-replica fault probability p:

        P(system error) = 3 * p^2 * (1 - p) + p^3   (approx 3 p^2 for small p)
    """
    corrected: int = 0
    uncorrectable: int = 0

    def vote(self, a: int, b: int, c: int) -> Tuple[int, bool]:
        """
        Majority vote over three replica outputs.

        Returns (result, was_fault_masked). `was_fault_masked` is True when
        the three inputs were not unanimous but a 2-of-3 majority existed.
        """
        if a == b == c:
            return a, False
        # find majority of the three
        if a == b or a == c:
            self.corrected += 1
            return a, True
        if b == c:
            self.corrected += 1
            return b, True
        # all three differ -> no majority, uncorrectable
        self.uncorrectable += 1
        return a, False

    @staticmethod
    def system_error_probability(replica_fault_prob: float) -> float:
        """Closed-form probability the TMR system outputs a wrong result."""
        p = replica_fault_prob
        return 3 * p * p * (1 - p) + p ** 3

    @staticmethod
    def reliability_gain(replica_fault_prob: float) -> float:
        """How many times more reliable TMR is vs a single (simplex) module."""
        p = replica_fault_prob
        if p <= 0:
            return float("inf")
        tmr = TMRVoter.system_error_probability(p)
        if tmr <= 0:
            return float("inf")
        return p / tmr


# --- SECDED error-correcting memory -----------------------------------------

@dataclass
class ECCMemory:
    """
    SECDED (Single Error Correct, Double Error Detect) memory model using a
    Hamming code with one extra overall parity bit.

    Behaviour:
        0 bit errors -> OK
        1 bit error  -> corrected (the workhorse case for SEU)
        2 bit errors -> detected but NOT corrected (raises uncorrectable)
       >2 bit errors -> may alias / mis-correct (counted as uncorrectable)

    `data_bits` is the word width protected (e.g. 32 or 64 bits).
    """
    data_bits: int = 32
    corrected: int = 0
    detected_uncorrectable: int = 0
    silent: int = 0

    @property
    def parity_bits(self) -> int:
        """Hamming SECDED check bits: smallest r with 2^r >= data+r+1, plus 1."""
        r = 1
        while (2 ** r) < (self.data_bits + r + 1):
            r += 1
        return r + 1  # +1 overall parity bit for double-error *detection*

    @property
    def overhead_percent(self) -> float:
        """Storage overhead of the check bits relative to data bits."""
        return 100.0 * self.parity_bits / self.data_bits

    def read_word(self, n_bit_errors: int) -> Tuple[str, bool]:
        """
        Simulate reading a word that experienced `n_bit_errors` upsets.

        Returns (status, data_valid).
        """
        if n_bit_errors <= 0:
            return "OK", True
        if n_bit_errors == 1:
            self.corrected += 1
            return "CORRECTED", True
        if n_bit_errors == 2:
            self.detected_uncorrectable += 1
            return "DETECTED_UNCORRECTABLE", False
        # 3+ errors: beyond code distance, may silently corrupt
        self.silent += 1
        return "SILENT_CORRUPTION", False


# --- Memory scrubbing --------------------------------------------------------

@dataclass
class MemoryScrubber:
    """
    Periodic memory scrubber. Between scrubs, SEUs accumulate in each word.
    SECDED survives only if at most one upset lands in a word before the next
    scrub rewrites the corrected value. The residual (uncorrectable) rate is

        P(>=2 upsets in a word per scrub interval)  ~  Poisson(lambda)

    where lambda = upset_rate_per_bit_s * word_bits * scrub_interval_s.
    """
    word_bits: int = 32
    scrub_interval_s: float = 60.0   # scrub every 60 s

    def expected_upsets_per_word(self, upset_rate_per_bit_day: float) -> float:
        """Mean upsets accumulated in one word between scrubs (lambda)."""
        per_bit_per_s = upset_rate_per_bit_day / SECONDS_PER_DAY
        return per_bit_per_s * self.word_bits * self.scrub_interval_s

    def uncorrectable_probability(self, upset_rate_per_bit_day: float) -> float:
        """P(>=2 upsets per word per scrub interval) under a Poisson model."""
        lam = self.expected_upsets_per_word(upset_rate_per_bit_day)
        p0 = math.exp(-lam)
        p1 = lam * math.exp(-lam)
        return max(0.0, 1.0 - p0 - p1)

    def residual_word_error_rate_per_day(self, upset_rate_per_bit_day: float) -> float:
        """Uncorrectable word errors per word per day after SECDED+scrubbing."""
        intervals_per_day = SECONDS_PER_DAY / self.scrub_interval_s
        return self.uncorrectable_probability(upset_rate_per_bit_day) * intervals_per_day


# --- FDIR state machine ------------------------------------------------------

class FDIRState(Enum):
    """Fault Detection, Isolation and Recovery states."""
    NOMINAL = "NOMINAL"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    ISOLATED = "ISOLATED"
    RECOVERING = "RECOVERING"
    SAFE_MODE = "SAFE_MODE"


@dataclass
class FDIRController:
    """
    Minimal Fault Detection, Isolation and Recovery controller with a watchdog.

    The watchdog must be 'kicked' within `watchdog_timeout_s`; otherwise the
    controller assumes a hung processor and triggers autonomous recovery.
    After `max_recovery_attempts` failed recoveries it falls back to SAFE_MODE
    (minimal-power, beacon-only) and waits for ground intervention.
    """
    watchdog_timeout_s: float = 5.0
    max_recovery_attempts: int = 3
    state: FDIRState = FDIRState.NOMINAL
    recovery_attempts: int = 0
    last_kick_s: float = 0.0
    event_log: List[str] = field(default_factory=list)

    def _log(self, msg: str) -> None:
        self.event_log.append(msg)

    def kick_watchdog(self, now_s: float) -> None:
        """Healthy software pets the watchdog to prove it is alive."""
        self.last_kick_s = now_s

    def detect(self, now_s: float, healthy: bool) -> FDIRState:
        """
        Run one FDIR cycle. Returns the resulting state.

        A fault is flagged if the subsystem reports unhealthy OR the watchdog
        has expired since the last kick.
        """
        watchdog_expired = (now_s - self.last_kick_s) > self.watchdog_timeout_s

        if self.state == FDIRState.SAFE_MODE:
            return self.state

        if not healthy or watchdog_expired:
            reason = "subsystem-unhealthy" if not healthy else "watchdog-timeout"
            self.state = FDIRState.ANOMALY_DETECTED
            self._log(f"t={now_s:.1f}s ANOMALY ({reason})")
            return self._isolate_and_recover(now_s)

        if self.state != FDIRState.NOMINAL:
            self.state = FDIRState.NOMINAL
            self._log(f"t={now_s:.1f}s recovered -> NOMINAL")
        return self.state

    def _isolate_and_recover(self, now_s: float) -> FDIRState:
        self.state = FDIRState.ISOLATED
        self._log(f"t={now_s:.1f}s isolate faulty unit")
        self.recovery_attempts += 1
        if self.recovery_attempts > self.max_recovery_attempts:
            self.state = FDIRState.SAFE_MODE
            self._log(f"t={now_s:.1f}s recovery budget exhausted -> SAFE_MODE")
            return self.state
        self.state = FDIRState.RECOVERING
        self._log(f"t={now_s:.1f}s recovery attempt {self.recovery_attempts} "
                  f"(reset + reload from golden image)")
        # a successful reset re-kicks the watchdog
        self.kick_watchdog(now_s)
        return self.state


# --- End-to-end mission simulation ------------------------------------------

# Representative per-operation logic upset probability used to quote a stable
# TMR reliability gain (literature-style figure, decoupled from the memory SEU
# rate which protects a different failure mode).
TMR_REPRESENTATIVE_FAULT_PROB = 1.0e-4


@dataclass
class TransitResult:
    """Result of an Earth-Mars transit radiation simulation."""
    environment: str
    transit_days: float
    memory_mbit: float
    accumulated_tid_krad: float
    raw_upsets_unprotected: float
    residual_errors_protected: float
    protection_factor: float
    tmr_reliability_gain: float
    ecc_overhead_percent: float
    mbu_fraction: float
    interleave_factor: float

    def summary(self) -> str:
        return (
            f"Transit: {self.transit_days:.0f} days through {self.environment}\n"
            f"  Memory protected           : {self.memory_mbit:.0f} Mbit\n"
            f"  Accumulated TID            : {self.accumulated_tid_krad:.1f} krad(Si)\n"
            f"  Raw upsets (unprotected)   : {self.raw_upsets_unprotected:,.0f}\n"
            f"  MBU fraction / interleaving: {self.mbu_fraction:.0%} / "
            f"{self.interleave_factor:.0%} defeated\n"
            f"  Residual uncorrectable     : {self.residual_errors_protected:,.1f} "
            f"over mission ({self.residual_errors_protected / self.transit_days:.2f}/day)\n"
            f"  Protection factor          : {self.protection_factor:,.0f}x fewer errors\n"
            f"  TMR reliability gain       : {self.tmr_reliability_gain:,.0f}x "
            f"(@ p={TMR_REPRESENTATIVE_FAULT_PROB:.0e}/op)\n"
            f"  ECC storage overhead       : {self.ecc_overhead_percent:.1f}%"
        )


def simulate_transit(
    environment: str = "interplanetary",
    transit_days: float = 210.0,
    memory_mbit: float = 512.0,
    cross_section_cm2_per_bit: float = 1.0e-12,
    word_bits: int = 32,
    scrub_interval_s: float = 60.0,
    mbu_fraction: float = 0.05,
    interleave_factor: float = 0.90,
    seed: int = 42,
) -> TransitResult:
    """
    Estimate radiation impact on an on-board computer during Earth-Mars transit
    and the improvement from SECDED+scrubbing and TMR.

    The residual (uncorrectable) error budget has two physically distinct terms:
      1. Accumulation: two *independent* single-bit upsets landing in the same
         word before the next scrub (Poisson double-hit) - very rare with fast
         scrubbing.
      2. MBU: a *single* high-LET ion flipping >=2 adjacent bits in one word.
         SECDED detects but cannot correct these. Physical bit-interleaving
         spreads a logical word across cells so most MBUs become single-bit-per-
         word and are corrected; `interleave_factor` is the fraction defeated.
    In practice term (2) dominates, which is why this is the realistic residual.

    Args:
        environment: key into ENVIRONMENTS (default 'interplanetary').
        transit_days: cruise duration (~210 d is a fast Hohmann-class transit).
        memory_mbit: protected memory size in megabits.
        cross_section_cm2_per_bit: per-bit SEU saturation cross-section.
        word_bits: ECC word width.
        scrub_interval_s: scrubbing period.
        mbu_fraction: fraction of strikes that produce a multiple-bit upset.
        interleave_factor: fraction of MBUs defeated by physical interleaving.
        seed: RNG seed (reproducibility; only used for illustrative sampling).

    Returns:
        TransitResult with raw vs protected error figures.
    """
    random.seed(seed)
    env = ENVIRONMENTS[environment]
    total_bits = memory_mbit * 1_000_000
    total_words = total_bits / word_bits

    rate_per_bit_day = seu_rate_per_bit_day(env.particle_flux, cross_section_cm2_per_bit)

    # Raw upsets if completely unprotected.
    raw_upsets = rate_per_bit_day * total_bits * transit_days

    # Term 1 - independent double-hit accumulation between scrubs.
    scrubber = MemoryScrubber(word_bits=word_bits, scrub_interval_s=scrub_interval_s)
    residual_per_word_day = scrubber.residual_word_error_rate_per_day(rate_per_bit_day)
    accumulation_errors = residual_per_word_day * total_words * transit_days

    # Term 2 - MBUs that survive bit-interleaving (dominant residual).
    mbu_errors = raw_upsets * mbu_fraction * (1.0 - interleave_factor)

    residual_errors = accumulation_errors + mbu_errors
    protection = (raw_upsets / residual_errors) if residual_errors > 0 else float("inf")

    ecc = ECCMemory(data_bits=word_bits)

    return TransitResult(
        environment=env.name,
        transit_days=transit_days,
        memory_mbit=memory_mbit,
        accumulated_tid_krad=env.tid_after(transit_days),
        raw_upsets_unprotected=raw_upsets,
        residual_errors_protected=residual_errors,
        protection_factor=protection,
        tmr_reliability_gain=TMRVoter.reliability_gain(TMR_REPRESENTATIVE_FAULT_PROB),
        ecc_overhead_percent=ecc.overhead_percent,
        mbu_fraction=mbu_fraction,
        interleave_factor=interleave_factor,
    )


# --- Demo --------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 64)
    print("AETHERIX Radiation-Hardened Computing — Earth-Mars Transit")
    print("=" * 64)

    result = simulate_transit(environment="interplanetary", transit_days=210)
    print(result.summary())

    print("\nRAD750 TID margin over a 687-day Mars surface mission:")
    mars = ENVIRONMENTS["mars_surface"]
    margin = mars.margin_against(device_tid_tolerance_krad=200.0, days=687)
    print(f"  Dose = {mars.tid_after(687):.1f} krad(Si), "
          f"RAD750 tolerance = 200 krad -> margin = {margin:,.0f}x")

    print("\nTMR system error probability vs single module:")
    for p in (1e-2, 1e-4, 1e-6):
        sys_p = TMRVoter.system_error_probability(p)
        print(f"  replica p={p:.0e} -> TMR p={sys_p:.2e} "
              f"({TMRVoter.reliability_gain(p):,.0f}x better)")

    print("\nFDIR watchdog recovery walk-through:")
    fdir = FDIRController(watchdog_timeout_s=5.0, max_recovery_attempts=2)
    timeline = [(0, True), (3, True), (10, True), (14, False), (20, False), (30, False)]
    for t, healthy in timeline:
        if healthy:
            fdir.kick_watchdog(t)
        state = fdir.detect(t, healthy)
        print(f"  t={t:>2}s healthy={str(healthy):<5} -> {state.value}")
    print("  log:")
    for line in fdir.event_log:
        print(f"    {line}")
