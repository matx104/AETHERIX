# Earth-Mars Interplanetary Network Topology

## Overview
This document outlines the network topology architecture for the AETHERIX Mars interplanetary communication system, implementing a tiered, delay-tolerant networking (DTN) infrastructure compliant with CCSDS standards and LNIS v5.

## Network Architecture

### 1. Network Tiers

#### Tier 1: Earth Ground Segment
**Primary Nodes:**
- **Deep Space Network (DSN) Stations**
  - Goldstone Complex (California, USA) - 34° 12' N, 116° 54' W
  - Madrid Deep Space Communications Complex (Spain) - 40° 26' N, 4° 15' W
  - Canberra Deep Space Communications Complex (Australia) - 35° 24' S, 148° 59' E
  - Node IDs: `earth.dsn.goldstone`, `earth.dsn.madrid`, `earth.dsn.canberra`
  
- **Ground Control Centers**
  - Mission Operations Center (MOC)
  - Network Operations Center (NOC)
  - Science Operations Center (SOC)
  - Node IDs: `earth.control.moc`, `earth.control.noc`, `earth.control.soc`

**Characteristics:**
- Always-on connectivity
- High-bandwidth terrestrial backhaul
- Coordinated scheduling for Mars contact windows
- Aggregate downlink capacity: 2-6 Mbps (depending on Mars distance)
- Aggregate uplink capacity: 500 kbps - 2 Mbps

#### Tier 2: Earth Orbital Assets
**Relay Nodes:**
- **Geosynchronous (GEO) Relay Satellites**
  - GEO-Relay-1 (Atlantic) - Node ID: `earth.geo.atlantic`
  - GEO-Relay-2 (Pacific) - Node ID: `earth.geo.pacific`
  - GEO-Relay-3 (Indian) - Node ID: `earth.geo.indian`
  
- **Low Earth Orbit (LEO) Constellation**
  - Laser Comm Constellation (48 satellites, 550 km altitude)
  - Node IDs: `earth.leo.lasersat-[001-048]`

**Characteristics:**
- Cross-link capabilities between GEO and LEO
- Optical inter-satellite links (ISL) at 10-100 Gbps
- RF backup channels
- Support for QKD infrastructure

#### Tier 3: Deep Space Transit/Relay
**Relay Nodes:**
- **Lagrange Point Relays**
  - Earth-Sun L4 Relay - Node ID: `transit.esl4.relay`
  - Earth-Sun L5 Relay - Node ID: `transit.esl5.relay`
  - Mars-Sun L4 Relay - Node ID: `transit.msl4.relay` (future)
  - Mars-Sun L5 Relay - Node ID: `transit.msl5.relay` (future)

- **Mars Transfer Orbit Relays**
  - Deep Space Relay-1 (Hohmann orbit) - Node ID: `transit.relay-1`
  - Deep Space Relay-2 (Fast transit) - Node ID: `transit.relay-2`

**Characteristics:**
- Strategic positioning for continuous Earth-Mars visibility
- Long contact periods (months to years)
- Optical/RF dual mode
- Bundle protocol store-and-forward capability
- Light-time delay: 4-24 minutes (variable)

#### Tier 4: Mars Orbital Assets
**Primary Relay Satellites:**
- **Mars Relay Satellite (MRS) Constellation**
  - MRS-Alpha (Areostationary) - Node ID: `mars.areo.alpha`
  - MRS-Beta (Areostationary) - Node ID: `mars.areo.beta`
  - MRS-Gamma (Polar orbit, 400 km) - Node ID: `mars.polar.gamma`
  - MRS-Delta (Polar orbit, 400 km) - Node ID: `mars.polar.delta`

**Characteristics:**
- Mars orbiters provide relay services for surface assets
- Areostationary orbit: ~17,032 km altitude
- Polar orbits provide complete surface coverage
- Inter-satellite crosslinks
- Data rates: 2-10 Mbps to Earth, 100+ Mbps to surface

#### Tier 5: Mars Surface Network
**Surface Nodes:**
- **Mars Base Station (MBS)**
  - Primary Base - Node ID: `mars.surface.base-alpha`
  - Secondary Base - Node ID: `mars.surface.base-beta`
  
- **Mobile Assets**
  - Rovers: Node IDs: `mars.surface.rover-[01-10]`
  - Aerial drones: Node IDs: `mars.surface.drone-[01-05]`
  
- **Distributed Sensor Networks**
  - Seismic network nodes: `mars.surface.seismic-[001-100]`
  - Weather stations: `mars.surface.weather-[001-050]`

**Characteristics:**
- Limited power (solar/nuclear)
- Intermittent orbital relay contact
- Local mesh networking (UHF/optical)
- Data rates: 128 kbps - 2 Mbps to orbiters

## Connectivity Matrix

### Link Types and Availability

| Source Tier | Destination Tier | Link Type | Availability | Latency |
|------------|------------------|-----------|--------------|---------|
| Earth Ground | Earth GEO | RF/Optical | 99.9% | ~120 ms |
| Earth GEO | Earth LEO | Optical ISL | 95% | ~10 ms |
| Earth Ground | Mars Orbit | Optical/RF | 85% (solar conj.) | 4-24 min |
| Earth Ground | Deep Space Relay | Optical | 90% | 2-20 min |
| Deep Space Relay | Mars Orbit | Optical | 95% | 2-10 min |
| Mars Orbit | Mars Surface | RF/Optical | 70-90% | 2-40 ms |
| Mars Orbit | Mars Orbit | Optical ISL | 98% | 1-5 ms |
| Mars Surface | Mars Surface | UHF/Optical | 60-80% | 0.1-10 ms |

### Solar Conjunction Handling
During solar conjunction (~2 weeks every 26 months), direct Earth-Mars links are degraded or unavailable. Mitigation strategies:
1. **Pre-positioning**: Buffer critical data before conjunction
2. **Relay utilization**: Route through Lagrange point relays
3. **Store-and-forward**: DTN bundle protocol automatically handles delays
4. **Autonomous operations**: Mars assets operate independently

## Orbital Mechanics & Geometry

### Earth-Mars Distance Dynamics
- **Perihelion (closest approach)**: ~54.6 million km (0.365 AU)
- **Aphelion (farthest)**: ~401 million km (2.68 AU)
- **Average distance**: ~225 million km (1.5 AU)
- **Light-time delay**: 
  - Minimum: ~182 seconds (3.03 minutes)
  - Maximum: ~1,342 seconds (22.37 minutes)
  - Average: ~750 seconds (12.5 minutes)

### Launch Windows
- **Synodic period**: ~780 days (26 months)
- **Optimal launch windows**: Every 26 months
- **Transit time**: 150-300 days (depending on trajectory)

### Visibility Windows
Mars-Earth visibility depends on:
- **Opposition**: Best communication (Mars at closest approach)
- **Conjunction**: Worst communication (Mars behind Sun)
- **Quadrature**: Moderate communication conditions

## Protocol Stack

### Bundle Protocol v7 (BPv7) - RFC 9171
- **Convergence Layer**: 
  - TCP Convergence Layer (TCPCL) for Earth segment
  - LTP (Licklider Transmission Protocol) for deep space
  - UDP Convergence Layer for high-speed optical links

- **Bundle Processing**:
  - Store-and-forward at each tier
  - Custody transfer enabled
  - Priority-based scheduling
  - Contact Graph Routing (CGR) → RL-enhanced routing

### CCSDS Standards Compliance
- **CCSDS 734.2-B-1**: Delay-Tolerant Networking (DTN) Architecture
- **CCSDS 735.1-B-1**: Bundle Protocol Specification
- **CCSDS 142.0-B-2**: Space Link Identifiers (LNIS v5)
- **CCSDS 141.0-B-1**: Optical Communications Coding and Synchronization
- **CCSDS 131.0-B-3**: TM Synchronization and Channel Coding

## Routing Architecture

### Traditional Contact Graph Routing (CGR)
- Pre-computed contact plans based on orbital mechanics
- Dijkstra-based shortest path with delay metric
- Static schedule updates (daily/weekly)

### RL-Enhanced Autonomous Routing (AETHERIX Innovation)
**Objective**: Replace static CGR with adaptive RL agents

**Agent Architecture**:
- **State Space**: 
  - Current node position and velocity
  - Neighbor node visibility and link quality
  - Bundle priority, size, and deadline
  - Buffer occupancy levels
  - Historical link performance metrics
  
- **Action Space**:
  - Forward to neighbor N
  - Store locally (defer)
  - Drop (if expired/low priority)
  - Split bundle (multipath)
  
- **Reward Function**:
  - R = α(delivered) - β(delay) - γ(hops) - δ(drops) - ε(energy)
  - Bonus for meeting deadlines
  - Penalty for missed science opportunities

**Training Approach**:
- Multi-agent reinforcement learning (MARL)
- Distributed training on historical telemetry
- Federated learning across network tiers
- Simulation-based pre-training with JPL Horizons data

## Quality of Service (QoS)

### Traffic Classes
1. **Emergency/Critical**: Spacecraft health, safety alerts
2. **High-Priority Science**: Time-sensitive observations
3. **Standard Science**: Regular telemetry and data
4. **Housekeeping**: Status updates, logs
5. **Bulk Data**: Archived datasets, software updates

### Resource Allocation
- Dynamic bandwidth allocation based on link availability
- Pre-emption for emergency traffic
- Fair queuing for science data
- Background transfer for bulk data

## Scalability Considerations

### Future Expansion
- Additional Mars surface bases
- Phobos/Deimos relay stations
- Mars satellite constellation (100+ satellites)
- Human settlement infrastructure
- Asteroid belt relays (for outer solar system)

### Network Growth Model
- Modular addition of nodes
- Backward compatible with legacy assets
- Incremental RL agent deployment
- Graceful degradation to CGR if RL unavailable

## References
1. CCSDS 734.2-B-1: "Delay-Tolerant Networking (DTN) Architecture"
2. RFC 9171: "Bundle Protocol Version 7"
3. JPL Horizons System: https://ssd.jpl.nasa.gov/horizons/
4. ION-DTN: https://sourceforge.net/projects/ion-dtn/
5. NASA Deep Space Network: https://deepspace.jpl.nasa.gov/

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-05  
**Author**: AETHERIX AI-Ops & Space Comms Architecture Team
