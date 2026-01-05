# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AETHERIX (Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange) is an architecture for delay-tolerant networking (DTN) between Earth and Mars. The project is currently in the **Initial Architecture Design phase** with completed topology and link budget analysis.

**Key Technologies:**
- Bundle Protocol v7 (BPv7) via ION-DTN
- Reinforcement Learning routing (replacing static Contact Graph Routing)
- Quantum Key Distribution (QKD) for security
- Hybrid optical/RF communications

## Commands

### Running Tests
```bash
python -m pytest tests/
# or
python -m unittest discover tests/
```

### Running the Link Budget Demo
```bash
python src/infrastructure/link_budget.py
```

### Future Commands (Not Yet Implemented)
```bash
# When implemented:
pip install -r requirements.txt
./scripts/setup-ion-dtn.sh
python src/link-budget/calculator.py --scenario mars-average
python src/routing/train_agent.py --config config/training.yaml
python src/simulation/run_scenario.py --config config/earth-mars-baseline.yaml
```

## Architecture

### Source Code Structure
```
src/
├── infrastructure/    # Link budget calculations (IMPLEMENTED)
│   └── link_budget.py # OpticalLinkBudget dataclass + LinkBudgetCalculator
├── routing/          # RL-based DTN routing (PLANNED - AETHERIX Relay)
├── security/         # QKD protocols (PLANNED - AETHERIX Quantum)
└── simulation/       # ns-3/OMNeT++ simulation APIs (PLANNED - AETHERIX Sim)
```

### Network Topology (5 Tiers)
1. **Earth Ground** - DSN stations (Goldstone, Madrid, Canberra)
2. **Earth Orbital** - GEO relays + LEO laser constellation (48 satellites)
3. **Deep Space Transit** - Lagrange point relays (ES-L4, ES-L5)
4. **Mars Orbital** - Areostationary + polar orbit relays
5. **Mars Surface** - Bases, rovers, drones, sensors

### Key Constants and Parameters
- **Wavelength**: 1550 nm (optical communications)
- **Mars distance range**: 54.6M km (perihelion) to 401M km (aphelion)
- **Data rates**: 2-200 Mbps downlink (distance-dependent)
- **Light-time delay**: 3-22 minutes one-way

## Standards Compliance

The project follows these standards:
- **CCSDS 734.2-B-1**: DTN Architecture
- **CCSDS 735.1-B-1**: Bundle Protocol
- **CCSDS 142.0-B-2**: LNIS v5 (Space Link Identifiers)
- **CCSDS 141.0-B-1**: Optical Communications
- **RFC 9171**: Bundle Protocol Version 7
- **RFC 5326**: Licklider Transmission Protocol (LTP)

## Development Notes

### Current Implementation
Only `src/infrastructure/link_budget.py` is implemented. It provides:
- `LinkBudgetCalculator` - calculates optical link budgets
- `OpticalLinkBudget` - dataclass for link budget results
- `calculate_mars_earth_link(scenario)` - convenience method for "minimum", "average", "maximum" scenarios

### Planned RL Agent Architecture
State space includes: node position/velocity, link quality, bundle metadata, buffer occupancy
Action space: forward/store/drop/split decisions
Reward: delivery success - delay - hops - energy consumption

### Prerequisites (for future implementation)
- Python 3.9+
- ns-3.38+ or OMNeT++ 6.0+
- ION-DTN 4.1.2+
- JPL Horizons API access
