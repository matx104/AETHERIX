"""
AETHERIX Radiation-Hardened Computing Package

Models the space radiation environment and the fault-tolerance techniques
used to survive it: Single Event Effects (SEU/SEL/MBU), Total Ionizing Dose
(TID), Triple Modular Redundancy (TMR), SECDED error-correcting memory,
memory scrubbing, and Fault Detection, Isolation and Recovery (FDIR).

Reference standards / heritage:
- ECSS-E-ST-10-12C   - Methods for the calculation of radiation effects
- JESD57 / JESD89     - SEU test and reporting methods
- NASA RAD750, ESA LEON3FT/GR712RC radiation-hardened processors
"""

from .radiation import (
    RadiationEffect,
    RadiationEnvironment,
    TMRVoter,
    ECCMemory,
    MemoryScrubber,
    FDIRController,
    FDIRState,
    seu_rate_per_bit_day,
    simulate_transit,
    ENVIRONMENTS,
)

__all__ = [
    "RadiationEffect",
    "RadiationEnvironment",
    "TMRVoter",
    "ECCMemory",
    "MemoryScrubber",
    "FDIRController",
    "FDIRState",
    "seu_rate_per_bit_day",
    "simulate_transit",
    "ENVIRONMENTS",
]
