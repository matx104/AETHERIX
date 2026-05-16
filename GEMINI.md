# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Operating contract**: This file follows the sovereign template at
> `~/PROJECTS/CLAUDE_SOVEREIGN_TEMPLATE.md`. The sovereign rules apply
> (additive enhancement, invent nothing, evidence before conclusion).

> **Classification**: research / proof-of-concept (delay-tolerant
> networking simulation — Bundle Protocol v7, RL routing, QKD,
> hybrid optical/RF). Demo-stage Python project with modules under
> `src/{infrastructure,orbital,routing,security,simulation}`.
> Treat scientific results sections of any work as **strict**: cite
> the sample/run, the seed, and the simulation config. No mocked
> physics, no fabricated latency numbers. The pre-existing
> Gemini API integration docs are at `docs/GEMINI_INTEGRATION.md`
> (moved from the repo-root `GEMINI.md` to make room for the
> agent-file convention).

## Project Overview

AETHERIX (Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange) is an architecture for delay-tolerant networking (DTN) between Earth and Mars. The project is currently in the **Demo/Proof-of-Concept phase** with working implementations of core modules.

**Key Technologies:**
- Bundle Protocol v7 (BPv7) via ION-DTN
- Reinforcement Learning routing (replacing static Contact Graph Routing)
- Quantum Key Distribution (QKD) for security
- Hybrid optical/RF communications

## Commands

### Quick Start
```bash
# Initialize the development environment
./scripts/init.sh

# Run all tests
./scripts/run_tests.sh

# Run interactive demos
./scripts/run_demos.sh
```

### Available Scripts
| Script | Description |
|--------|-------------|
| `./scripts/init.sh` | Set up virtual environment and install dependencies |
| `./scripts/init.sh --dev` | Include development tools (linting, formatting) |
| `./scripts/run_tests.sh` | Run the test suite |
| `./scripts/run_tests.sh -v` | Run tests with verbose output |
| `./scripts/run_demos.sh` | Interactive demo menu |
| `./scripts/run_demos.sh 1-6` | Run specific demo |
| `./scripts/link_budget_demo.sh` | Run link budget demo |
| `./scripts/lint.sh` | Run code quality checks |
| `./scripts/lint.sh --fix` | Auto-fix code style issues |
| `./scripts/clean.sh` | Clean up build artifacts and caches |

### Running Individual Modules
```bash
# Link budget calculations
python src/infrastructure/link_budget.py

# RL routing agent demo
python src/routing/rl_agent.py

# QKD protocol simulation
python src/security/qkd.py

# Orbital mechanics / contact windows
python src/orbital/contact_windows.py

# Bundle protocol demo
python src/routing/bundle.py
```

### Future Commands (Not Yet Implemented)
```bash
# When implemented:
./scripts/setup-ion-dtn.sh
python src/routing/train_agent.py --config config/training.yaml
python src/simulation/run_scenario.py --config config/earth-mars-baseline.yaml
```

## Architecture

### Project Structure
```
AETHERIX/
├── scripts/           # Shell scripts for development tasks
│   ├── init.sh        # Environment setup
│   ├── run_tests.sh   # Test runner
│   ├── run_demos.sh   # Demo runner
│   ├── lint.sh        # Code quality checks
│   └── clean.sh       # Cleanup script
├── src/
│   ├── infrastructure/    # Link budget calculations
│   │   └── link_budget.py # OpticalLinkBudget + LinkBudgetCalculator
│   ├── routing/           # RL-based DTN routing
│   │   ├── rl_agent.py    # RLRoutingAgent, NetworkState, RoutingDecision
│   │   └── bundle.py      # BPv7 Bundle, EndpointID, BundlePriority
│   ├── security/          # QKD protocols
│   │   └── qkd.py         # BB84Protocol, E91Protocol, QuantumRepeater
│   ├── orbital/           # Orbital mechanics
│   │   └── contact_windows.py # Contact prediction, distance calculations
│   └── simulation/        # ns-3/OMNeT++ simulation APIs (PLANNED)
├── demos/             # Interactive demonstrations (6 demos)
│   ├── 01_link_budget_demo/
│   ├── 02_dtn_routing_demo/
│   ├── 03_orbital_mechanics_demo/
│   ├── 04_quantum_key_demo/
│   ├── 05_mars_mission_scenario/
│   └── 06_integrated_demo/
├── tests/             # Test suite
├── visualizations/    # Charts and visualization scripts
├── docs/              # Documentation
├── presentation/      # Presentation materials
├── interview_prep/    # Interview preparation materials
└── requirements.txt   # Python dependencies
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

## Implemented Modules

### Infrastructure (`src/infrastructure/link_budget.py`)
Full implementation of optical link budget calculations:
- `OpticalLinkBudget` - dataclass for link budget results
- `LinkBudgetCalculator` - calculates free-space loss, EIRP, received power, link margin
- `calculate_mars_earth_link(scenario)` - convenience method for "minimum", "average", "maximum" scenarios

### Routing (`src/routing/`)
Demo-level implementations:
- **`rl_agent.py`**: Q-learning based routing agent
  - `RLRoutingAgent` - epsilon-greedy policy with Q-table
  - `NetworkState` - state representation (node, neighbors, link quality, buffer)
  - `RoutingAction` - forward/store/drop/split actions
  - Reward function: R = α(delivery) - β(delay) - γ(hops) - δ(drops) - ε(energy)
- **`bundle.py`**: BPv7 bundle protocol implementation
  - `Bundle` - full bundle with primary block, lifetime, custody tracking
  - `EndpointID` - DTN endpoint identifiers (scheme://node/service)
  - `BundlePriority` - 5 priority levels (EMERGENCY to BULK)

### Security (`src/security/qkd.py`)
QKD protocol simulations:
- `BB84Protocol` - Bennett-Brassard 1984 protocol with QBER detection
- `E91Protocol` - Entanglement-based protocol (Ekert 1991)
- `QuantumRepeater` - entanglement swapping for extended range
- Security threshold: QBER < 11% indicates no eavesdropper

### Orbital (`src/orbital/contact_windows.py`)
Orbital mechanics calculations:
- `calculate_earth_mars_distance()` - distance from true anomaly
- `calculate_light_time()` - one-way light delay
- `predict_contact_windows()` - communication opportunity prediction
- `get_distance_timeline()` - synodic period distance variation
- Handles solar conjunction blackouts

## Development Notes

### Test Coverage
Currently only `tests/test_link_budget.py` exists. Tests needed for:
- RL routing agent
- QKD protocols
- Orbital mechanics
- Bundle protocol

### Production Upgrades Needed
The current implementations are demo-level. Production would require:
- **RL Agent**: Replace Q-table with Deep Q-Network (DQN), experience replay, neural network weights
- **QKD**: Actual photon counting, detector modeling, privacy amplification
- **Orbital**: JPL Horizons API integration for precise ephemeris
- **Simulation**: Integration with ns-3 or OMNeT++ for network simulation

### Prerequisites
- Python 3.9+
- For future simulation: ns-3.38+ or OMNeT++ 6.0+
- For DTN integration: ION-DTN 4.1.2+
- For precise ephemeris: JPL Horizons API access

---

## Agent skills

### Issue tracker

GitHub Issues at `matx104/AETHERIX`, via the `gh` CLI. Simulation issues should attach seed + config for reproducibility. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical roles plus research-flavour labels (`module:<n>`, `qkd`, `rl-policy`, `bpv7`, `demo`, `paper`, `reproducibility`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — `CONTEXT.md` + `docs/adr/` at the repo root (create lazily). Existing project docs include `docs/GEMINI_INTEGRATION.md`. See `docs/agents/domain.md`.

