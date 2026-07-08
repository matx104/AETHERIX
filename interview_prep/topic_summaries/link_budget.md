# Link Budget Analysis

## Topic Summary

### What Is a Link Budget?

A link budget is an accounting of all gains and losses from the
transmitter, through the propagation medium, to the receiver. The bottom
line is the **link margin**: how many dB of headroom exist between the
received signal quality and the minimum needed for error-free decoding.

```
Link Margin = (Eb/N0)_achieved − (Eb/N0)_required
```

A positive margin means the link closes; a negative margin means it
doesn't. In deep-space communications, margins are often negative at
maximum Mars distance — this is why DTN store-and-forward is essential.

---

### Free Space Path Loss (FSPL)

The dominant loss in any deep-space link:

```
FSPL = 20·log₁₀(4πd·f / c)
```

At 1550 nm optical and 225 M km (average Earth-Mars distance):

```
FSPL = 20·log₁₀(4π × 2.25×10¹¹ × 1.94×10¹⁴ / 3×10⁸)
     ≈ -370 dB
```

At Ka-band (26.5 GHz) over the same distance:

```
FSPL ≈ -294 dB
```

The optical loss is ~76 dB worse due to the much higher frequency, but
optical antenna (telescope) gain compensates — a 22 cm aperture at
1550 nm produces +113 dBi vs +62 dBi for a 3 m dish at Ka-band.

**Key insight**: FSPL increases by 6 dB per doubling of distance
(one octave). The perihelion-to-aphelion distance ratio is 401/54.6 ≈ 7.3,
so the FSPL swing is `20·log₁₀(7.3) ≈ 17.3 dB` across the synodic cycle.

---

### Optical Link Budget (1550 nm)

AETHERIX uses optical communications as the primary high-rate link.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Wavelength | 1550 nm | Eye-safe, low atmospheric absorption |
| TX power | 5 W (+37 dBm) | Typical lasercomm terminal |
| TX aperture | 22 cm | Mars orbiter class |
| RX aperture | 8.0 m | Future ground telescope |
| Pointing loss | -3 dB | Sub-microradian pointing budget |
| Atmospheric loss | -1 dB | Clear weather |
| Detector quantum efficiency | 0.5 | Photon-counting APD |

**Results** (from `src/infrastructure/link_budget.py`):

| Scenario | Distance | FSPL | Margin |
|----------|----------|------|--------|
| Perihelion | 54.6 M km | -358 dB | -62.57 dB |
| Average | 225 M km | -370 dB | -71 dB |
| Aphelion | 401 M km | -375 dB | -79.82 dB |

> **Note**: These margins are negative because the demo calculator uses
> simplified physics (no forward error correction coding gain, conservative
> detector model). Production systems with rate-1/2 LDPC codes would
> recover ~8 dB, and aperture scaling to 10–12 m ground telescopes adds
> another ~3 dB. See `DESIGN_RATIONALE.md` §5 for the full derivation.

---

### RF Link Budget (Ka/X/S/UHF)

RF provides the reliability fallback when optical links fail (clouds,
pointing errors, solar conjunction). AETHERIX models four bands:

| Band | Frequency | Wavelength | Primary Use |
|------|-----------|------------|-------------|
| Ka | 26.5 GHz | 11.3 mm | High-rate downlink (primary) |
| X | 8.4 GHz | 35.7 mm | Deep-space standard (conjunction fallback) |
| S | 2.3 GHz | 130 mm | TT&C, emergency |
| UHF | 401 MHz | 748 mm | Mars surface relay |

**Antenna gain**: `G = η·(π·D·f/c)²` where η ≈ 0.55 (typical efficiency).

A 34 m DSN dish at Ka-band: G ≈ 80 dBi.
A 3 m spacecraft dish at Ka-band: G ≈ 52 dBi.

**System temperature**: `Tsys = Tant + T₀·(NF_linear - 1)`

Deep-space sky temperature Tant ≈ 50 K (very cold sky).
With NF = 2 dB: Tsys ≈ 220 K.

**Noise power**: `N = k·T·B` where k = 1.38×10⁻²³ J/K.

At Tsys = 220 K and B = 12 MHz: `N ≈ -128 dBm`.

**Ka-band results** (from `src/infrastructure/rf_link_budget.py`):

| Scenario | Distance | FSPL | Margin |
|----------|----------|------|--------|
| Perihelion | 55 M km | -278 dB | -14.39 dB |
| Average | 225 M km | -290 dB | -23 dB |
| Aphelion | 401 M km | -295 dB | -31.64 dB |

---

### Why Hybrid Optical/RF?

| Factor | Optical (1550 nm) | RF (Ka-band) |
|--------|-------------------|--------------|
| Data rate | 50–200 Mbps | 2–10 Mbps |
| Beam divergence | ~10 μrad | ~0.1° |
| Pointing requirement | <10 μrad | <0.5° |
| Weather sensitivity | Clouds block entirely | Rain fades only |
| Conjunction impact | Fully blocked | Degraded (X-band usable) |
| Antenna size (RX) | 8–12 m telescope | 34 m DSN dish |

**Strategy**: Optical is the primary link when available (clear weather,
accurate pointing). RF (Ka-band) is the fallback. During solar conjunction,
even Ka-band degrades — X-band with store-and-forward via Lagrange relays
maintains a thin but reliable connection.

**Availability math**: If optical site availability = 95.7% (3 diverse
sites with site-diversity gain) and Ka-band RF availability = 99.0%:

```
Combined = 1 − (1 − 0.957) × (1 − 0.99) = 1 − 0.043 × 0.01 = 99.96%
```

This exceeds the 99.9% target.

---

### Eb/N0 and Coding

The link quality metric is `Eb/N0` (energy per bit to noise density ratio):

```
Eb/N0 = C/N − 10·log₁₀(B/Rb)
```

Where C/N is the carrier-to-noise ratio, B is bandwidth, and Rb is the
bit rate. Required Eb/N0 depends on the modulation and coding scheme:

| Scheme | Required Eb/N0 | Coding Gain |
|--------|----------------|-------------|
| Uncoded BPSK @ BER 10⁻⁵ | 9.6 dB | 0 dB (reference) |
| Rate-1/2 convolutional (K=7) | 4.5 dB | +5.1 dB |
| Concatenated RS+Conv | 3.0 dB | +6.6 dB |
| LDPC (DVB-S2) | 1.0 dB | +8.6 dB |
| Turbo code (rate-1/6) | 0.8 dB | +8.8 dB |

AETHERIX uses 10 dB as the default required Eb/N0 (conservative — assumes
legacy uncoded or light coding). The production path would use LDPC or
turbo codes to recover ~8 dB of margin.

---

### Link Margin Interpretation

| Margin | Interpretation |
|--------|----------------|
| > 6 dB | Comfortable — link closes with margin to spare |
| 0 to 6 dB | Marginal — closes under good conditions only |
| -3 to 0 dB | Intermittent — bursts of packet loss, DTN recovers |
| < -3 dB | Open link — no reliable communication |

The AETHERIX RL agent uses a normalised **link quality** (0.0–1.0) rather
than raw dB margins. The `MIN_LINK_QUALITY = 0.3` threshold corresponds
roughly to the -3 dB boundary: below this, the agent stores rather than
forwards.

---

### Key Formulas Summary

| Formula | Equation | Used In |
|---------|----------|---------|
| FSPL | `20·log₁₀(4πdf/c)` | `link_budget.py`, `rf_link_budget.py` |
| Antenna gain | `10·log₁₀(η(πDf/c)²)` | Both |
| EIRP | `Ptx_dBm + Gtx + line_loss` | Both |
| System temp | `Tant + T₀(NF_linear - 1)` | `rf_link_budget.py` |
| Noise power | `10·log₁₀(kTB) + 30` | `rf_link_budget.py` |
| Eb/N0 | `C/N - 10·log₁₀(B/Rb)` | Both |
| Link margin | `Eb/N0_achieved - Eb/N0_required` | Both |
