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

---

## LTP Segment Count

```
N_red = ceil(bundle_size / red_block_size)
N_green = ceil(remaining_size / green_block_size)
N_total = N_red + N_green

Where:
  bundle_size = total BPv7 bundle payload (bytes)
  red_block_size = reliable segment size (configurable, typically 1024 bytes)
  green_block_size = best-effort segment size (typically 4096 bytes)
  N_red segments require checkpoint/acknowledgment
  N_green segments are fire-and-forget
```

---

## Q-Learning Update Rule

```
Q(s, a) ← Q(s, a) + α × [r + γ × max_a' Q(s', a') - Q(s, a)]

Where:
  s = current state (node, neighbors, link quality, buffer)
  a = action taken (forward, store, drop, split)
  r = reward received: α(delivery) - β(delay) - γ(hops) - δ(drops) - ε(energy)
  α = learning rate (decays as 1/visit_count(s,a))
  γ = discount factor (0.95 in AETHERIX)
  s' = next state after action
  max_a' Q(s', a') = estimated optimal future value
```

---

## Binary Entropy Function

```
h(p) = -p × log₂(p) - (1 - p) × log₂(1 - p)

Where:
  p = error probability (QBER in QKD context)

Key values:
  h(0) = 0      (no errors, no information leakage)
  h(0.11) ≈ 0.5 (Shor-Preskill threshold)
  h(0.5) = 1    (maximum entropy, no useful information)
```

---

## Csiszár-Körner Bound (Privacy Amplification)

```
l_secure < n × (1 - h(QBER) - δ_leak)

Where:
  l_secure = length of final secure key after privacy amplification
  n = length of sifted key after CASCADE error correction
  h(QBER) = binary entropy of the quantum bit error rate
  δ_leak = fraction of key information leaked during error correction

This bounds the maximum extractable secret key length.
AETHERIX applies Toeplitz-matrix hashing to achieve this bound.
```

---

## CASCADE Block Size

```
k_init = 0.73 / QBER_estimate

Where:
  k_init = initial block size for CASCADE first pass
  QBER_estimate = estimated error rate from sample comparison

Subsequent passes: k_pass = 2 × k_previous
Typical: QBER = 5% → k_init ≈ 15 bits
CASCADE achieves reconciliation efficiency f_EC ≈ 1.05-1.15
```

---

## Federated Averaging (FedAvg for Q-Tables)

```
Q_global = Σ_i (n_i / N) × Q_i

Where:
  Q_global = aggregated global Q-table
  Q_i = local Q-table from node i
  n_i = number of training episodes at node i
  N = Σ_i n_i (total episodes across all nodes)

Aggregation occurs every K contact windows.
Communication cost per round: O(|S| × |A|) per node.
AETHERIX uses K=10 contact windows between aggregation rounds.
```
