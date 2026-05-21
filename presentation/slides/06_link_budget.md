# Optical Link Budget — Performance Analysis

## [LIVE DEMO] Link Budget Calculator

> **Launch demo**: [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/) → "Link Budget" tab

### Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Transmitter power** | 5 W (37 dBm) | Typical space-qualified laser |
| **TX aperture** | 22 cm (0.22 m) | Mars orbiter class |
| **RX aperture** | 1.0 m | Ground telescope (DSN-scale) |
| **Wavelength** | 1550 nm (C-band) | Telecom heritage, eye-safe |
| **Aperture efficiency** | 0.55 | Conservative estimate |
| **Target data rate** | 10 Mbps (nominal) | Science data return |

### Key Equations

**Free-Space Path Loss (FSPL):**
```
FSPL (dB) = 20 × log₁₀(4π × d / λ)
```

**Antenna Gain:**
```
G (dB) = 10 × log₁₀(η × (π × D / λ)²)
```

**Received Power:**
```
Pr = Pt + Gt + Gr − FSPL − Latm − Lpoint
```

**Link Margin:**
```
Margin = Pr − Sensitivity − SNR_required
```

### Results by Distance Scenario

| Scenario | Distance | FSPL | Data Rate | Light Time | Margin |
|----------|----------|------|-----------|------------|--------|
| **Perihelion** (min) | 54.6 M km | −352.9 dB | **100-200 Mbps** | 3.0 min | +15 dB |
| **Average** | 225 M km | −365.0 dB | **10-20 Mbps** | 12.5 min | +8 dB |
| **Aphelion** (max) | 401 M km | −370.0 dB | **2-5 Mbps** | 22.3 min | +3 dB |

### Comparison: AETHERIX Optical vs Current RF

| Metric | Current (MRO Ka-band) | AETHERIX (1550 nm) | Improvement |
|--------|----------------------|-------------------|:-----------:|
| Peak data rate | 6 Mbps | 200 Mbps | **33×** |
| Average data rate | 2 Mbps | 20 Mbps | **10×** |
| Worst-case rate | 0.5 Mbps | 2 Mbps | **4×** |
| Daily data volume | 5-10 GB | 50-100 GB | **10-20×** |

### Why 1550 nm?

1. **Telecom heritage** — Mature component supply chain (amplifiers, detectors, fibers)
2. **Atmospheric window** — Low absorption at sea level (clear sky)
3. **Eye safety** — Class 1M at typical transmit powers
4. **Detector options** — APD (avalanche photodiode) or SNSPD (superconducting nanowire)
5. **Fiber compatibility** — Standard telecom fiber for ground segment

### Standards

- **CCSDS 141.0-B-1** — Optical Communications Physical Layer
- **CCSDS 131.0-B-4** — TM Synchronization and Channel Coding
- Based on NASA DSOC (Deep Space Optical Communications) mission parameters
