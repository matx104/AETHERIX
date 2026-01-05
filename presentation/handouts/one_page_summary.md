# AETHERIX - One Page Summary
## Interplanetary Communication Network for Mars Mission Support

**Student**: Muhammad Abdullah Tariq | **Topic 59** | **EduQual Level 6**

---

## The Challenge
| Problem | Impact |
|---------|--------|
| Distance: 54.6M - 401M km | 3-22 min one-way light time |
| Current RF: 0.5-6 Mbps | Limited science data return |
| Solar conjunction | 2-week complete blackout |
| TCP/IP fails | Requires 6-44 min RTT |

## The Solution: AETHERIX Architecture

### 5-Tier Network (232 nodes)
1. **Earth Ground**: DSN stations (Goldstone, Madrid, Canberra)
2. **Earth Orbital**: GEO relays + 48 LEO laser satellites
3. **Deep Space**: Lagrange point relays (ES-L4, ES-L5)
4. **Mars Orbital**: 2 Areostationary + 2 Polar orbiters
5. **Mars Surface**: Bases, rovers, drones, sensors

### Key Technologies
| Technology | Function |
|------------|----------|
| **Bundle Protocol v7** | Store-and-forward DTN |
| **RL Routing** | AI replaces static CGR |
| **Optical Links** | 2-200 Mbps (10-100x improvement) |
| **QKD Security** | Quantum-secure communications |

## Performance Comparison

| Metric | Current (MRO) | AETHERIX | Improvement |
|--------|---------------|----------|-------------|
| Downlink | 0.5-6 Mbps | 2-200 Mbps | **10-100x** |
| Daily Data | 5-10 GB | 50-100 GB | **10-20x** |
| Availability | 60-75% | >95% | **+20-35%** |
| Routing | Static | AI-Adaptive | **Autonomous** |

## Standards Compliance
- CCSDS 734.2-B-1 (DTN) | CCSDS 735.1-B-1 (Bundle Protocol)
- CCSDS 141.0-B-1 (Optical) | RFC 9171 (BPv7) | RFC 5326 (LTP)

## Key Equations
- **FSPL**: 20 × log₁₀(4π × d / λ) dB
- **Light Time**: t = d / c (299,792 km/s)
- **RL Reward**: R = α(delivered) - β(delay) - γ(hops) - δ(drops)

## Critical Constants
| Parameter | Value |
|-----------|-------|
| Mars perihelion | 54.6M km (3 min light-time) |
| Mars aphelion | 401M km (22 min light-time) |
| Synodic period | 779.94 days |
| Optical wavelength | 1550 nm |
| QKD threshold | QBER < 11% |

---

**Repository**: github.com/matx104/AETHERIX | **Contact**: muhammad.atx@gmail.com
