# AETHERIX Network Node Registry

## Overview
This document provides a complete registry of all network nodes in the AETHERIX Mars interplanetary network, including node identifiers, coordinates, capabilities, and operational parameters.

## Node Naming Convention

### Format
`<tier>.<segment>.<identifier>`

### Tiers
- `earth` - Earth-based assets (ground and orbital)
- `transit` - Deep space relay/transit nodes
- `mars` - Mars-based assets (orbital and surface)

### Segments
- Ground: `dsn`, `control`
- Orbital: `geo`, `leo`, `areo`, `polar`
- Transit: `esl4`, `esl5`, `msl4`, `msl5`, `relay`
- Surface: `surface`

## Tier 1: Earth Ground Segment

### Deep Space Network (DSN) Stations

#### earth.dsn.goldstone
- **Location**: Goldstone, California, USA
- **Coordinates**: 35.426667°N, 116.89°W
- **Altitude**: 1,001 m
- **Antenna**: 70m + 34m dishes, 10m optical telescope
- **Capabilities**: 
  - RF: Ka-band (32 GHz), X-band (8.4 GHz)
  - Optical: 1550nm laser receiver
  - Data Rate: 2-200 Mbps (distance-dependent)
- **Availability**: 99.5%
- **Primary Function**: Deep space communications, Mars relay

#### earth.dsn.madrid
- **Location**: Robledo de Chavela, Spain
- **Coordinates**: 40.431389°N, 4.248056°W
- **Altitude**: 834 m
- **Antenna**: 70m + 34m dishes, 10m optical telescope
- **Capabilities**: 
  - RF: Ka-band (32 GHz), X-band (8.4 GHz)
  - Optical: 1550nm laser receiver
  - Data Rate: 2-200 Mbps (distance-dependent)
- **Availability**: 99.5%
- **Primary Function**: Deep space communications, Mars relay

#### earth.dsn.canberra
- **Location**: Tidbinbilla, Australia
- **Coordinates**: 35.401389°S, 148.981944°E
- **Altitude**: 688 m
- **Antenna**: 70m + 34m dishes, 10m optical telescope
- **Capabilities**: 
  - RF: Ka-band (32 GHz), X-band (8.4 GHz)
  - Optical: 1550nm laser receiver
  - Data Rate: 2-200 Mbps (distance-dependent)
- **Availability**: 99.5%
- **Primary Function**: Deep space communications, Mars relay

### Ground Control Centers

#### earth.control.moc
- **Name**: Mission Operations Center
- **Location**: JPL, Pasadena, California
- **Primary Function**: Mission command and control
- **Capabilities**: 
  - Command uplink generation
  - Telemetry monitoring
  - Anomaly resolution
  - Mission planning

#### earth.control.noc
- **Name**: Network Operations Center
- **Location**: JPL, Pasadena, California
- **Primary Function**: Network monitoring and management
- **Capabilities**: 
  - Network health monitoring
  - Contact scheduling
  - Resource allocation
  - RL agent training and deployment

#### earth.control.soc
- **Name**: Science Operations Center
- **Location**: Distributed (multiple institutions)
- **Primary Function**: Science planning and data processing
- **Capabilities**: 
  - Science observation planning
  - Data analysis and archival
  - Instrument commanding
  - Science product generation

## Tier 2: Earth Orbital Assets

### Geosynchronous Earth Orbit (GEO) Relay Satellites

#### earth.geo.atlantic
- **Orbit**: GEO, 35,786 km altitude
- **Longitude**: 30°W
- **Coverage**: Americas, Europe, Africa
- **Capabilities**:
  - RF relay: 1-10 Gbps
  - Optical ISL: 10-100 Gbps
  - QKD-capable
- **Power**: 5 kW solar arrays
- **Mass**: 3,500 kg

#### earth.geo.pacific
- **Orbit**: GEO, 35,786 km altitude
- **Longitude**: 150°E
- **Coverage**: Asia, Oceania, Americas
- **Capabilities**:
  - RF relay: 1-10 Gbps
  - Optical ISL: 10-100 Gbps
  - QKD-capable
- **Power**: 5 kW solar arrays
- **Mass**: 3,500 kg

#### earth.geo.indian
- **Orbit**: GEO, 35,786 km altitude
- **Longitude**: 60°E
- **Coverage**: Asia, Africa, Europe
- **Capabilities**:
  - RF relay: 1-10 Gbps
  - Optical ISL: 10-100 Gbps
  - QKD-capable
- **Power**: 5 kW solar arrays
- **Mass**: 3,500 kg

### Low Earth Orbit (LEO) Laser Constellation

#### earth.leo.lasersat-[001-048]
- **Orbit**: LEO, 550 km altitude, 53° inclination
- **Constellation**: Walker Delta pattern (8 planes × 6 satellites)
- **Coverage**: Global, multiple simultaneous passes
- **Capabilities**:
  - Optical ISL: 10-100 Gbps
  - Ground optical links: 1-10 Gbps
  - QKD backbone
- **Power**: 2 kW solar arrays per satellite
- **Mass**: 250 kg per satellite
- **Total Constellation**: 48 satellites

**Representative Nodes**:
- `earth.leo.lasersat-001` to `earth.leo.lasersat-008`: Plane 1
- `earth.leo.lasersat-009` to `earth.leo.lasersat-016`: Plane 2
- `earth.leo.lasersat-017` to `earth.leo.lasersat-024`: Plane 3
- `earth.leo.lasersat-025` to `earth.leo.lasersat-032`: Plane 4
- `earth.leo.lasersat-033` to `earth.leo.lasersat-040`: Plane 5
- `earth.leo.lasersat-041` to `earth.leo.lasersat-048`: Plane 6-8

## Tier 3: Deep Space Transit/Relay

### Lagrange Point Relays

#### transit.esl4.relay
- **Position**: Earth-Sun L4 Lagrange point
- **Distance from Earth**: ~150 million km (1 AU)
- **Distance from Mars**: Variable (100-400 million km)
- **Capabilities**:
  - Optical relay: 1-100 Mbps to Earth/Mars
  - RF backup: 100-1000 kbps
  - Quantum repeater station
  - Large data buffer: 1 TB
- **Power**: Nuclear RTG + solar, 500 W
- **Mass**: 2,000 kg
- **Mission Duration**: 10+ years

#### transit.esl5.relay
- **Position**: Earth-Sun L5 Lagrange point
- **Distance from Earth**: ~150 million km (1 AU)
- **Distance from Mars**: Variable (100-400 million km)
- **Capabilities**:
  - Optical relay: 1-100 Mbps to Earth/Mars
  - RF backup: 100-1000 kbps
  - Quantum repeater station
  - Large data buffer: 1 TB
- **Power**: Nuclear RTG + solar, 500 W
- **Mass**: 2,000 kg
- **Mission Duration**: 10+ years

#### transit.msl4.relay (Future)
- **Position**: Mars-Sun L4 Lagrange point
- **Status**: Planned for Phase 3 deployment
- **Purpose**: Maintain continuous Earth-Mars visibility during conjunction

#### transit.msl5.relay (Future)
- **Position**: Mars-Sun L5 Lagrange point
- **Status**: Planned for Phase 3 deployment
- **Purpose**: Maintain continuous Earth-Mars visibility during conjunction

### Mars Transfer Orbit Relays

#### transit.relay-1
- **Orbit**: Hohmann transfer orbit (Earth-Mars)
- **Period**: ~780 days (synodic period)
- **Capabilities**:
  - Optical: 1-50 Mbps
  - RF: 100-1000 kbps
  - Data buffer: 500 GB
- **Power**: Solar + battery, 200 W
- **Mass**: 800 kg
- **Purpose**: Provide relay during Mars approach/departure phases

#### transit.relay-2
- **Orbit**: Fast transfer orbit (Earth-Mars)
- **Period**: ~780 days (synodic period)
- **Capabilities**:
  - Optical: 1-50 Mbps
  - RF: 100-1000 kbps
  - Data buffer: 500 GB
- **Power**: Solar + battery, 200 W
- **Mass**: 800 kg
- **Purpose**: Provide relay during Mars approach/departure phases

## Tier 4: Mars Orbital Assets

### Areostationary Orbit Satellites

#### mars.areo.alpha
- **Orbit**: Areostationary, 17,032 km altitude above 0° longitude
- **Period**: 24.623 hours (synchronous with Mars rotation)
- **Coverage**: Western hemisphere of Mars
- **Capabilities**:
  - Earth link: 2-200 Mbps (optical), 500 kbps (RF backup)
  - Mars surface link: 2-100 Mbps (optical/RF)
  - ISL to other Mars orbiters: 1-10 Gbps
  - Data buffer: 1 TB
- **Power**: 3 kW solar arrays
- **Mass**: 2,500 kg

#### mars.areo.beta
- **Orbit**: Areostationary, 17,032 km altitude above 180° longitude
- **Period**: 24.623 hours (synchronous with Mars rotation)
- **Coverage**: Eastern hemisphere of Mars
- **Capabilities**:
  - Earth link: 2-200 Mbps (optical), 500 kbps (RF backup)
  - Mars surface link: 2-100 Mbps (optical/RF)
  - ISL to other Mars orbiters: 1-10 Gbps
  - Data buffer: 1 TB
- **Power**: 3 kW solar arrays
- **Mass**: 2,500 kg

### Polar Orbit Satellites

#### mars.polar.gamma
- **Orbit**: Polar, 400 km altitude, 90° inclination
- **Period**: ~2 hours
- **Coverage**: Complete Mars surface coverage
- **Capabilities**:
  - Mars surface link: 2-50 Mbps (UHF/optical)
  - ISL to areo satellites: 1-10 Gbps
  - Earth link (via areo relay): N/A (relayed)
  - Data buffer: 500 GB
- **Power**: 1.5 kW solar arrays
- **Mass**: 1,200 kg
- **Primary Function**: Surface asset relay, reconnaissance

#### mars.polar.delta
- **Orbit**: Polar, 400 km altitude, 90° inclination, 180° phase offset from gamma
- **Period**: ~2 hours
- **Coverage**: Complete Mars surface coverage
- **Capabilities**:
  - Mars surface link: 2-50 Mbps (UHF/optical)
  - ISL to areo satellites: 1-10 Gbps
  - Earth link (via areo relay): N/A (relayed)
  - Data buffer: 500 GB
- **Power**: 1.5 kW solar arrays
- **Mass**: 1,200 kg
- **Primary Function**: Surface asset relay, reconnaissance

## Tier 5: Mars Surface Network

### Mars Base Stations

#### mars.surface.base-alpha
- **Location**: Jezero Crater region
- **Coordinates**: 18.5°N, 77.4°E
- **Type**: Permanent habitat and research station
- **Capabilities**:
  - Orbital link: 2-100 Mbps (optical/UHF)
  - Surface mesh: 1-10 Mbps (UHF/optical)
  - Data storage: 10 TB
  - RL routing node
- **Power**: Nuclear reactor + solar, 10 kW
- **Crew**: 6-12 (future)
- **Primary Function**: Main Mars base, science operations

#### mars.surface.base-beta
- **Location**: Deuteronilus Mensae region
- **Coordinates**: 45°N, 23°E
- **Type**: Secondary outpost
- **Capabilities**:
  - Orbital link: 2-50 Mbps (UHF)
  - Surface mesh: 1-10 Mbps (UHF)
  - Data storage: 5 TB
  - RL routing node
- **Power**: Solar + battery, 5 kW
- **Crew**: 0-4 (future)
- **Primary Function**: Secondary research station

### Mobile Surface Assets

#### mars.surface.rover-[01-10]
- **Type**: Large science rovers (Perseverance-class)
- **Mobility**: 100+ km range
- **Capabilities**:
  - Orbital link: 128-500 kbps (UHF)
  - Surface mesh: 100-500 kbps (UHF)
  - Data storage: 100 GB
  - Science instruments
- **Power**: RTG, 110 W
- **Mass**: 1,000 kg
- **Primary Function**: Science exploration, sample collection

**Active Nodes**:
- `mars.surface.rover-01` to `mars.surface.rover-10`

#### mars.surface.drone-[01-05]
- **Type**: Mars helicopter/aerial vehicles
- **Mobility**: 1+ km per flight
- **Capabilities**:
  - Link to rover/base: 10-100 kbps (UHF)
  - Data storage: 10 GB
  - Imaging/reconnaissance
- **Power**: Battery + solar, 20 W
- **Mass**: 5 kg
- **Primary Function**: Aerial reconnaissance, relay extension

**Active Nodes**:
- `mars.surface.drone-01` to `mars.surface.drone-05`

### Distributed Sensor Networks

#### mars.surface.seismic-[001-100]
- **Type**: Seismometer network
- **Distribution**: Grid pattern, 10-50 km spacing
- **Capabilities**:
  - Link to base/relay: 1-10 kbps (UHF)
  - Data storage: 1 GB
  - Seismic monitoring
- **Power**: Battery + solar, 5 W
- **Mass**: 10 kg
- **Primary Function**: Mars interior studies

**Network Size**: 100 nodes covering major geological regions

#### mars.surface.weather-[001-050]
- **Type**: Automated weather stations
- **Distribution**: Regional coverage
- **Capabilities**:
  - Link to base/relay: 1-10 kbps (UHF)
  - Data storage: 1 GB
  - Weather monitoring (pressure, temp, wind, dust)
- **Power**: Battery + solar, 5 W
- **Mass**: 15 kg
- **Primary Function**: Weather forecasting, climate studies

**Network Size**: 50 nodes covering diverse climate zones

## Network Summary Statistics

### Total Node Count
- **Earth Ground**: 6 nodes (3 DSN + 3 control centers)
- **Earth Orbital**: 51 nodes (3 GEO + 48 LEO)
- **Deep Space Transit**: 4 nodes (2 Lagrange + 2 transfer orbit)
- **Mars Orbital**: 4 nodes (2 areostationary + 2 polar)
- **Mars Surface Fixed**: 2 nodes (2 bases)
- **Mars Surface Mobile**: 15 nodes (10 rovers + 5 drones)
- **Mars Surface Sensors**: 150 nodes (100 seismic + 50 weather)
- **TOTAL**: **232 nodes**

### Aggregate Network Capacity
- **Earth-Mars Downlink**: 2-200 Mbps (distance-dependent)
- **Earth-Mars Uplink**: 1-10 Mbps (distance-dependent)
- **Mars Orbital ISL**: 1-10 Gbps
- **Earth LEO ISL**: 10-100 Gbps
- **Mars Surface Links**: 128 kbps - 100 Mbps (per asset)

### Geographic Coverage
- **Earth**: Global (via GEO + LEO)
- **Mars**: Complete surface coverage
- **Deep Space**: Continuous Earth-Mars corridor
- **Solar Conjunction**: Lagrange relays maintain connectivity

## Node Addition Procedure

### New Node Registration
1. Assign unique node ID following naming convention
2. Register with NOC (earth.control.noc)
3. Obtain LNIS v5 identifier (CCSDS 142.0-B-2)
4. Configure BPv7 endpoint ID
5. Deploy RL routing agent
6. Test connectivity with neighbors
7. Update contact graph
8. Activate operational service

### Node Decommissioning
1. Notify NOC of planned decommission
2. Migrate traffic to alternate paths
3. Transfer custody of stored bundles
4. Update contact graph
5. Remove from active routing
6. Archive node telemetry and logs

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-05  
**Maintained by**: AETHERIX Network Operations Center (earth.control.noc)  
**Next Review**: 2026-04-05
