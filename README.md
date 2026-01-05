# AETHERIX

**Autonomous, Quantum-Secure AI Ops for Space Communications**

AETHERIX is a comprehensive platform for designing, simulating, and optimizing deep-space communication networks using AI-driven Delay-Tolerant Networking (DTN) and Quantum Communication systems for interplanetary missions.

## Overview

AETHERIX provides:

- **AI-Driven Routing**: Reinforcement Learning-based routing to replace static Contact Graph Routing (CGR)
- **Quantum Security**: Quantum Key Distribution (QKD) and entanglement-based protocols for secure command links
- **Infrastructure Modeling**: Tiered architecture design for interplanetary communication networks
- **Link Budget Analysis**: Comprehensive optical and RF link budget calculations
- **Simulation Integration**: Support for ns-3/OMNeT++ with JPL Horizons ephemeris data

## Project Structure

```
AETHERIX/
├── src/
│   ├── infrastructure/    # Infrastructure modeling and link budget
│   ├── routing/          # AI-driven DTN routing
│   ├── security/         # Quantum security modules
│   └── simulation/       # Simulation APIs and tools
├── docs/
│   └── network_topology.md  # Network architecture documentation
└── tests/
    └── test_link_budget.py  # Unit tests
```

## Quick Start

### Link Budget Calculation

```python
from src.infrastructure import LinkBudgetCalculator

# Create calculator instance
calculator = LinkBudgetCalculator()

# Calculate link budget for Mars-Earth at maximum distance
budget = calculator.calculate_optical_link_budget(
    distance_km=390_000_000,      # 390 million km
    tx_power_watts=5.0,           # 5W laser
    tx_aperture_m=0.22,           # 22 cm aperture
    rx_aperture_m=1.0,            # 1m ground telescope
    data_rate_mbps=10.0           # 10 Mbps target
)

print(budget)
```

### Running the Demo

```bash
python src/infrastructure/link_budget.py
```

### Running Tests

```bash
python -m pytest tests/
# or
python -m unittest discover tests/
```

## Network Architecture

The AETHERIX platform supports a tiered communication architecture:

1. **Earth Ground Stations**: DSN (Goldstone, Madrid, Canberra) and ESTRACK
2. **Deep-Space Relay Satellites**: Lagrange point relays for continuous coverage
3. **Mars Orbital Relays**: MRO, MAVEN, Mars Express
4. **Mars Surface Nodes**: Habitats, rovers, and sensor networks

See [Network Topology Documentation](docs/network_topology.md) for details.

## Technical Specifications

### Protocol Support
- Bundle Protocol version 7 (BPv7) with CBOR serialization
- Licklider Transmission Protocol (LTP)
- CCSDS Space Link Protocols

### Standards Compliance
- LunaNet Interoperability Specifications (LNIS v5)
- CCSDS Blue Books
- NASA Deep Space Network Interface Requirements

## License

This project is part of the AETHERIX platform for space communications research.