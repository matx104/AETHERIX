# AETHERIX Quick Reference Guide

## Network at a Glance

### Five-Tier Architecture
```
Earth Ground (DSN) → Earth Orbital (GEO/LEO) → Deep Space Relay → Mars Orbital → Mars Surface
     ↑                      ↑                        ↑                  ↑              ↑
  6 nodes              51 nodes                  4 nodes           4 nodes       167 nodes
```

### Key Performance Metrics

| Metric | Value |
|--------|-------|
| **Total Nodes** | 232 |
| **Max Downlink** | 200 Mbps (Mars perihelion) |
| **Typical Downlink** | 10-20 Mbps (average distance) |
| **Min Downlink** | 2-5 Mbps (Mars aphelion) |
| **Uplink** | 1-10 Mbps (distance-dependent) |
| **Round-Trip Latency** | 6-44 minutes |
| **Network Availability** | >99% (with diversity) |

## Protocol Stack (Quick View)

```
┌─────────────────────────────────────────┐
│        Application Layer                │
│  (Science Data, Commands, Telemetry)    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   Bundle Protocol v7 (BPv7) - RFC 9171  │
│  - Store and Forward                    │
│  - Custody Transfer                     │
│  - RL-Enhanced Routing (replaces CGR)   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Convergence Layer                   │
│  - LTP (deep space)                     │
│  - TCPCL (Earth segment)                │
│  - UDP-CL (optical ISL)                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Physical/Data Link Layer            │
│  - Optical (1550nm): 2-200 Mbps         │
│  - RF Ka-band: 500 kbps - 10 Mbps       │
│  - UHF: 128 kbps - 2 Mbps               │
└─────────────────────────────────────────┘
```

## Link Budget Summary

### Earth-Mars Optical Links

**Transmitter (Mars):**
- Power: 5W @ 1550nm
- Aperture: 30 cm
- Gain: +105.7 dBi

**Receiver (Earth):**
- Aperture: 10 m
- Gain: +134.0 dBi
- Type: APD/SNSPD

**Performance:**
| Distance | FSPL | Data Rate |
|----------|------|-----------|
| 54.6M km | -352.9 dB | 100-200 Mbps |
| 225M km  | -365.0 dB | 10-20 Mbps |
| 401M km  | -370.0 dB | 2-5 Mbps |

### Inter-Satellite Links (ISL)

**Mars Orbital Network:**
- Distance: 1,000-10,000 km
- Power: 1W @ 1550nm
- Aperture: 10 cm (both ends)
- Data Rate: 1-2 Gbps
- Availability: >99%

**Earth LEO Constellation:**
- Distance: 500-2,000 km
- Data Rate: 10-100 Gbps
- Technology: Optical crosslinks
- Availability: >99.5%

## RL Routing Agent (Quick Specs)

### Agent Architecture
```
State → Neural Network → Q-values → Action Selection
  ↑                                         ↓
  └─────────── Reward Feedback ─────────────┘
```

**State Space (inputs):**
- Node position & velocity (6 DOF)
- Neighbor visibility & link quality (SNR, BER)
- Bundle metadata (size, priority, deadline)
- Buffer occupancy (current load)
- Historical performance (success rates)

**Action Space (outputs):**
- Forward to neighbor N (where N = visible neighbors)
- Store locally (defer routing decision)
- Drop bundle (if expired/undeliverable)
- Split bundle (multipath routing)

**Reward Function:**
```
R = α(delivered) - β(delay) - γ(hops) - δ(drops) - ε(energy)

Where:
α = delivery weight (1.0)
β = delay penalty (0.001 per second)
γ = hop penalty (0.1 per hop)
δ = drop penalty (10.0 per drop)
ε = energy penalty (0.01 per watt-hour)
```

**Training Approach:**
- Algorithm: Multi-Agent Deep Q-Network (MADQN)
- Experience Replay: 1M transitions
- Training Data: JPL Horizons + historical telemetry
- Update Frequency: Every 1000 steps
- Deployment: Federated learning across nodes

## Quantum Security (Overview)

### QKD Protocols

**Earth-LEO Links:**
- Protocol: BB84 (prepare-and-measure)
- Key Rate: 1-10 kbps
- Distance: <2,000 km
- Status: Demonstrated technology

**Earth-GEO Links:**
- Protocol: BB84 or E91
- Key Rate: 100-1000 bps
- Distance: ~36,000 km
- Status: Challenging but feasible

**Earth-Mars Links:**
- Protocol: E91 (entanglement-based)
- Key Rate: 1-10 bps
- Distance: 54-401 million km
- Quantum Repeaters: Required (Lagrange points)
- Status: Future deployment (Phase 3)

### Entanglement Distribution
```
Earth ←─── Entangled Photons ────→ Mars
        ↑                       ↑
        └─ Lagrange Relay ──────┘
           (Source + Repeater)
```

## Standards Compliance Checklist

### CCSDS Standards
- ✅ **CCSDS 734.2-B-1**: DTN Architecture
- ✅ **CCSDS 735.1-B-1**: Bundle Protocol v7
- ✅ **CCSDS 142.0-B-2**: Space Link Identifiers (LNIS v5)
- ✅ **CCSDS 141.0-B-1**: Optical Communications
- ✅ **CCSDS 131.0-B-3**: TM Synchronization and Channel Coding

### IETF Standards
- ✅ **RFC 9171**: Bundle Protocol Version 7
- ✅ **RFC 5326**: Licklider Transmission Protocol
- ✅ **RFC 7242**: Delay-Tolerant Networking TCP Convergence Layer

## Node Identifier Quick Lookup

### Earth Segment
```
earth.dsn.goldstone         # California DSN station
earth.dsn.madrid            # Spain DSN station
earth.dsn.canberra          # Australia DSN station
earth.control.moc           # Mission Operations Center
earth.control.noc           # Network Operations Center
earth.control.soc           # Science Operations Center
earth.geo.atlantic          # GEO relay (30°W)
earth.geo.pacific           # GEO relay (150°E)
earth.geo.indian            # GEO relay (60°E)
earth.leo.lasersat-001      # LEO constellation (48 total)
```

### Deep Space
```
transit.esl4.relay          # Earth-Sun L4 relay
transit.esl5.relay          # Earth-Sun L5 relay
transit.relay-1             # Transfer orbit relay
transit.relay-2             # Transfer orbit relay
```

### Mars Segment
```
mars.areo.alpha             # Areostationary (0° lon)
mars.areo.beta              # Areostationary (180° lon)
mars.polar.gamma            # Polar orbiter
mars.polar.delta            # Polar orbiter
mars.surface.base-alpha     # Primary base (Jezero)
mars.surface.base-beta      # Secondary base
mars.surface.rover-01       # Science rover
mars.surface.drone-01       # Aerial vehicle
mars.surface.seismic-001    # Seismic sensor
mars.surface.weather-001    # Weather station
```

## Traffic Classes & QoS

### Priority Levels
1. **Emergency** (P0): Spacecraft health, safety alerts
   - Max delay: <1 minute
   - Bandwidth: Guaranteed
   - Example: Anomaly alerts, critical telemetry

2. **High-Priority Science** (P1): Time-sensitive observations
   - Max delay: <30 minutes
   - Bandwidth: High priority
   - Example: Solar events, atmospheric phenomena

3. **Standard Science** (P2): Regular telemetry and data
   - Max delay: <24 hours
   - Bandwidth: Fair share
   - Example: Daily science data, rover images

4. **Housekeeping** (P3): Status updates, logs
   - Max delay: <7 days
   - Bandwidth: Low priority
   - Example: System logs, diagnostics

5. **Bulk Data** (P4): Archived datasets, software updates
   - Max delay: <30 days
   - Bandwidth: Opportunistic
   - Example: Complete dataset dumps, OS updates

## Contact Windows (Typical)

### Earth-Mars Direct
- **Optimal (opposition)**: 8-12 hours/day, 100-200 Mbps
- **Average**: 6-8 hours/day, 10-20 Mbps
- **Poor (quadrature)**: 2-4 hours/day, 2-5 Mbps
- **Conjunction**: 0 hours/day (use Lagrange relays)

### Mars Orbital → Mars Surface
- **Areostationary**: Continuous (base stations), 2-100 Mbps
- **Polar orbit**: 10-30 min every 2 hours, 2-50 Mbps
- **Combined availability**: >90%

## Power Budget (Typical Node)

### Mars Orbital Relay
| Component | Power | Duty Cycle | Average |
|-----------|-------|------------|---------|
| Laser TX | 50W | 10% | 5W |
| Pointing | 20W | 100% | 20W |
| RX Electronics | 15W | 100% | 15W |
| Thermal | 30W | 100% | 30W |
| Computer | 25W | 100% | 25W |
| **Total** | | | **95W** |

**Power Source**: 3 kW solar + 100Ah battery

## Common Operations

### Add New Bundle to Network
1. Application generates bundle
2. Bundle agent assigns priority
3. RL agent selects next hop
4. Convergence layer transmits
5. Next node stores and repeats

### Handle Link Outage
1. RL agent detects link failure
2. Store bundle locally (DTN)
3. RL agent recomputes route
4. Forward when link available
5. Update link quality metrics

### Solar Conjunction Procedure
1. Pre-position critical data (T-14 days)
2. Switch to Lagrange relays (T-7 days)
3. Mars autonomous ops (T-0 to T+14 days)
4. Resume direct links (T+14 days)
5. Transmit buffered data

## Simulation Parameters

### ns-3 Configuration
- **Simulator**: ns-3.38+
- **Propagation Model**: Free space + Friis
- **Orbital Dynamics**: SGP4/SDP4 from JPL Horizons
- **DTN Module**: ION-DTN 4.1.2+
- **Traffic Model**: Poisson arrivals, mixed priorities
- **Simulation Duration**: 780 days (full synodic period)

### OMNeT++ Configuration
- **Simulator**: OMNeT++ 6.0+
- **Framework**: INET 4.4+
- **Mobility Model**: JPL Horizons ephemeris
- **Channel Model**: Optical + RF with atmospheric effects
- **DTN Module**: Custom BPv7 implementation
- **Visualization**: 3D orbital display

## Troubleshooting Quick Guide

### High Latency (>30 min end-to-end)
- ✓ Check Earth-Mars distance (expect 3-22 min light time)
- ✓ Verify no excessive buffering at relays
- ✓ Check RL agent routing decisions
- ✓ Ensure priority setting correct

### Low Data Rate (<1 Mbps at average distance)
- ✓ Check optical link weather conditions
- ✓ Verify pointing accuracy (<10 μrad)
- ✓ Check solar panel power output
- ✓ Confirm RF backup not engaged
- ✓ Inspect link budget margins

### Bundle Drops
- ✓ Check buffer occupancy levels
- ✓ Verify bundle lifetime (TTL) adequate
- ✓ Check priority vs QoS policy
- ✓ Review RL agent reward function

### Lost Connectivity
- ✓ Check solar conjunction calendar
- ✓ Verify ground station schedule
- ✓ Check spacecraft solar panel sun-pointing
- ✓ Confirm no emergency safing mode

## Key Equations

### Free Space Path Loss
```
FSPL (dB) = 20 × log₁₀(4π × R / λ)

Where:
R = distance (meters)
λ = wavelength (meters)
```

### Link Budget
```
Pr = Pt + Gt + Gr - FSPL - Latm - Lpoint - Lother

Where all terms in dB or dBm
```

### Data Rate (Shannon-Hartley)
```
C = B × log₂(1 + SNR)

Where:
C = channel capacity (bps)
B = bandwidth (Hz)
SNR = signal-to-noise ratio (linear)
```

### Light Time Delay
```
Δt = R / c

Where:
R = distance (meters)
c = speed of light (3×10⁸ m/s)
```

## Useful Constants

| Constant | Value |
|----------|-------|
| Speed of light | 299,792,458 m/s |
| Earth-Sun distance (1 AU) | 149,597,870,700 m |
| Mars orbit semi-major axis | 1.524 AU |
| Mars-Earth min distance | 0.365 AU (54.6M km) |
| Mars-Earth max distance | 2.68 AU (401M km) |
| Mars-Earth synodic period | 780 days |
| Mars sidereal day | 24.623 hours |
| Areostationary orbit | 17,032 km altitude |

## Contact Information

**Network Operations Center (NOC):**
- Node ID: `earth.control.noc`
- Email: noc@aetherix.space (placeholder)
- Emergency: 24/7 monitoring

**Documentation Updates:**
- Repository: https://github.com/matx104/AETHERIX
- Issues: https://github.com/matx104/AETHERIX/issues

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-05  
**Quick Reference**: Print this guide for operational reference
