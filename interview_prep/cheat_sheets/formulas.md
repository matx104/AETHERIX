# AETHERIX Formula Cheat Sheet

## Link Budget Equations

### Free Space Path Loss (FSPL)
```
FSPL (dB) = 20 × log₁₀(4π × d / λ)
         = 20 × log₁₀(d) + 20 × log₁₀(f) - 147.55

Where:
  d = distance (meters)
  λ = wavelength (meters)
  f = frequency (Hz)
```

### Antenna Gain
```
G (dB) = 10 × log₁₀(η × (π × D / λ)²)

Where:
  η = aperture efficiency (typically 0.55)
  D = aperture diameter (meters)
  λ = wavelength (meters)
```

### Link Budget
```
Pr = Pt + Gt + Gr - FSPL - Latm - Lpoint - Lother

Where:
  Pr = received power (dBm)
  Pt = transmitted power (dBm)
  Gt = transmitter gain (dB)
  Gr = receiver gain (dB)
  Latm = atmospheric loss (dB)
  Lpoint = pointing loss (dB)
```

### Link Margin
```
Margin = Pr - Sensitivity - Required_SNR
```

---

## Light Time & Distance

### One-Way Light Time
```
t = d / c

Where:
  d = distance (meters)
  c = 299,792,458 m/s
```

### Quick Reference
| Distance | Light Time |
|----------|------------|
| 1 AU (149.6M km) | 499 seconds (8.3 min) |
| Mars min (54.6M km) | 182 seconds (3 min) |
| Mars avg (225M km) | 750 seconds (12.5 min) |
| Mars max (401M km) | 1337 seconds (22.3 min) |

---

## Orbital Mechanics

### Orbital Radius (Ellipse)
```
r = a(1 - e²) / (1 + e × cos(θ))

Where:
  a = semi-major axis
  e = eccentricity
  θ = true anomaly
```

### Orbital Period
```
T = 2π × √(a³ / μ)

Where:
  μ = GM (gravitational parameter)
  μ_Sun = 1.327×10²⁰ m³/s²
```

### Synodic Period
```
1/P_synodic = |1/P_inner - 1/P_outer|

Earth-Mars: P_synodic = 779.94 days
```

### Doppler Shift
```
Δf/f = v/c

For optical (1550nm) at v=24 km/s:
Δf ≈ 15 GHz
```

---

## Shannon Capacity

### Channel Capacity
```
C = B × log₂(1 + SNR)

Where:
  C = capacity (bps)
  B = bandwidth (Hz)
  SNR = signal-to-noise ratio (linear)
```

---

## Quantum Key Distribution

### Key Rate (BB84)
```
R = f × η × r_sift × (1 - h(QBER) - f_EC × h(QBER))

Where:
  f = photon rate
  η = detector efficiency
  r_sift = ~0.5 (basis matching)
  h() = binary entropy function
  QBER = quantum bit error rate
  f_EC = error correction efficiency
```

### Security Threshold
```
QBER < 11% → Secure
QBER ≥ 11% → Abort (eavesdropper likely)
```

---

## RL Reward Function (AETHERIX)

```
R = α(delivered) - β(delay) - γ(hops) - δ(drops) - ε(energy)

Typical values:
  α = 1.0    (delivery reward)
  β = 0.001  (per second penalty)
  γ = 0.1    (per hop penalty)
  δ = 10.0   (drop penalty)
  ε = 0.01   (per Wh penalty)
```

---

## Power Conversions

### dBm to Watts
```
P_mW = 10^(P_dBm/10)
P_W = P_mW / 1000
```

### Watts to dBm
```
P_dBm = 10 × log₁₀(P_mW)
      = 10 × log₁₀(P_W × 1000)
```

### Quick Reference
| dBm | Watts |
|-----|-------|
| 37 dBm | 5 W |
| 30 dBm | 1 W |
| 20 dBm | 100 mW |
| 10 dBm | 10 mW |
| 0 dBm | 1 mW |
| -30 dBm | 1 μW |
