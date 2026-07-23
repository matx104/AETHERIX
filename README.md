# AETHERIX

**A**utonomous **E**xtraterrestrial **T**hrough-space **H**igh-throughput **E**nhancing **R**outing and **I**nterplanetary e**X**change

[![Tests](https://img.shields.io/badge/Tests-202_passing-00d4aa?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.9+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-Research-00d4aa?style=for-the-badge)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-00d4aa?style=for-the-badge&logo=github&logoColor=white)](https://matx104.github.io/AETHERIX/)

Research / proof-of-concept architecture for delay-tolerant networking (DTN) between Earth and Mars. Implements Bundle Protocol v7, reinforcement-learning routing, quantum key distribution, hybrid optical/RF link budgets, radiation-hardened computing, and mission data prioritization across a 5-tier, 241-node interplanetary topology.

---

## Table of Contents

- [Overview](#overview)
- [Key Technologies](#key-technologies)
- [Architecture](#architecture)
- [Network Topology](#network-topology)
- [Getting Started / Basic Usage](#getting-started)
  - **[Full Usage Guide &amp; Design Rationale →](docs/USAGE_GUIDE.md)**
- [Modules](#modules)
- [Testing](#testing)
- [Web Showcase](#web-showcase)
- [Presentation](#presentation)
- [Standards Compliance](#standards-compliance)
- [Interview Preparation](#interview-preparation)
- [License](#license)

---

## Overview

AETHERIX is a demo-stage Python project simulating an interplanetary DTN. It replaces static Contact Graph Routing with Q-learning agents, secures command links via BB84/E91 QKD, models hybrid 1550 nm optical and Ka/X/S/UHF RF links, and adds radiation-hardened computing and deadline-aware data prioritization. All modules are accompanied by browser-based interactive demos and a 29-slide presentation package.

---

## Key Technologies

- **Bundle Protocol v7 (BPv7)** — store-and-forward DTN with custody tracking, LTP/TCPCL/UDP convergence layers (RFC 9171, RFC 5326, RFC 7242)
- **Reinforcement Learning routing** — Q-learning agent with epsilon-greedy policy, multi-agent federated learning, experience replay, convergence detection
- **Quantum Key Distribution** — BB84 and E91 protocols, quantum repeater chains with entanglement purification, CASCADE reconciliation and privacy amplification
- **Hybrid optical/RF communications** — 1550 nm optical link budgets (CCSDS 141.0-B-1), RF link budgets for Ka/X/S/UHF bands
- **Radiation-hardened computing** — SEU/SEL/TID modelling, Triple Modular Redundancy, SECDED ECC, memory scrubbing, FDIR state machine
- **Data prioritization** — 4-tier mission QoS scheduler, CCSDS lossless/wavelet compression, deadline-aware preemption

---

## Architecture

```
AETHERIX/
├── src/
│   ├── infrastructure/        # Optical and RF link budget calculators
│   ├── routing/               # BPv7 bundles, RL agent, forwarding, convergence layers
│   ├── security/              # QKD protocols, repeater chains, privacy amplification
│   ├── orbital/               # Contact windows, celestial bodies, Doppler, topology
│   ├── computing/             # Radiation-hardened computing models
│   └── simulation/            # Simulation engine, policy-based routing
├── tests/                     # 202 unit tests across 13 test files
├── run_simulation.py          # one-command end-to-end driver (zero deps)
├── demos/                     # 6 interactive Python demos
├── docs/                      # Web showcase (GitHub Pages SPA)
├── presentation/              # 29-slide PPTX/PDF/web presentation with speaker notes
├── visualizations/            # Charts and diagrams
├── interview_prep/            # Technical Q&A, cheat sheets, topic summaries
├── references/                # Academic references and standards documents
├── scripts/                   # init, test, demo, lint, clean
├── web/                       # Dockerfile (nginx:alpine)
├── docker-compose.yml
└── requirements.txt
```

---

## Network Topology

5-tier hierarchical delay-tolerant network, 241 nodes total:

| Tier | Segment | Assets |
|:----:|---------|--------|
| 1 | Earth Ground | DSN stations (Goldstone, Madrid, Canberra) |
| 2 | Earth Orbital | GEO relays + LEO laser constellation (48 satellites) |
| 3 | Deep Space Transit | Lagrange point relays (ES-L4, ES-L5) |
| 4 | Mars Orbital | Areostationary + polar orbit relays |
| 5 | Mars Surface | Bases, rovers, drones, distributed sensor network |

Key parameters: 54.6 M km (perihelion) to 401 M km (aphelion), 3--22 min one-way light-time, 2--200 Mbps downlink.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Tier 1: Earth Ground Segment                      │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      │
│  │ DSN Goldstone│◄────►│  DSN Madrid  │◄────►│ DSN Canberra │      │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘      │
└─────────┼─────────────────────┼─────────────────────┼───────────────┘
          ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Tier 2: Earth Orbital Assets                       │
│     GEO relays  ◄──►  LEO Laser Constellation (48 satellites)       │
└─────────────────────────────┼───────────────────────────────────────┘
                              │ Optical/RF (3-22 min)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 Tier 3: Deep Space Transit Relays                    │
│  ┌────────────┐         ┌────────────┐         ┌────────────┐      │
│  │ ES-L4 Relay│◄───────►│ ES-L5 Relay│◄───────►│Transit Sats│      │
│  └─────┬──────┘         └─────┬──────┘         └─────┬──────┘      │
└─────────┼─────────────────────┼─────────────────────┼───────────────┘
          ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Tier 4: Mars Orbital Assets                       │
│  MRS-Alpha (Areostat) ◄──► MRS-Beta (Areostat) ◄──► MRS-Gamma     │
└────────┼─────────────────────┼─────────────────────┼───────────────┘
         ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Tier 5: Mars Surface Network                      │
│  Base-α  ◄──►  Base-β  ◄──►  Rovers  ◄──►  Drones / Sensors       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Getting Started

### Prerequisites

- **Python 3.9+** (only requirement for the simulation core)
- Node.js 18+ *(optional — only for the web dashboard)*
- Docker & Docker Compose *(optional — only for containerized deployment)*

### Basic Usage

The fastest path — clone and run the full simulation with **zero dependencies**:

```bash
git clone https://github.com/matx104/AETHERIX.git
cd AETHERIX
python run_simulation.py
```

That single command runs all six modules end-to-end (baseline DTN, optical/RF
link budgets, RL routing, **failure & recovery**, QKD security, radiation
hardening) using only the Python standard library — no `pip install` needed.

The other commands you'll use most:

```bash
python run_simulation.py -m 4      # run just the failure & recovery scenario
python -m pytest tests/ -q         # run the 480-test suite (needs: pip install pytest)
./scripts/init.sh                  # set up venv + dev tools (linting, etc.)
./scripts/dev.sh docker-up         # launch the full-stack web app in Docker
```

> **Full reference** → every command, every flag, plus the complete design
> rationale (trade-offs, selection criteria, decision matrices) is in the
> **[Usage Guide](docs/USAGE_GUIDE.md)**. For the exhaustive architectural
> defense — Core Flight System mapping, whiteboarding scenarios, quantitative
> derivations, and "why-not" rebuttals — see the
> **[Design Rationale](docs/DESIGN_RATIONALE.md)**.

### Full Setup

```bash
# Set up virtual environment and install test/dev dependencies
./scripts/init.sh

# Run all tests (480 tests)
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
| `./scripts/run_tests.sh -v` | Verbose test output |
| `./scripts/run_demos.sh` | Interactive demo menu |
| `./scripts/lint.sh` | Code quality checks |
| `./scripts/lint.sh --fix` | Auto-fix code style issues |
| `./scripts/clean.sh` | Clean build artifacts and caches |

### Running Individual Modules

```bash
python src/infrastructure/link_budget.py     # Optical link budget
python src/infrastructure/rf_link_budget.py  # RF link budget
python src/routing/rl_agent.py               # RL routing agent
python src/routing/bundle.py                 # Bundle protocol
python src/security/qkd.py                   # QKD simulation
python src/orbital/contact_windows.py        # Orbital mechanics
python src/computing/radiation.py            # Radiation hardening
```

### End-to-End Simulation Driver

```bash
# All six modules at once
python run_simulation.py

# Individual modules:  1 baseline | 2 link budget | 3 RL training
#                      4 failure&recovery | 5 QKD | 6 radiation
python run_simulation.py -m 4        # solar-conjunction optical blackout recovery
python run_simulation.py --seed 7    # change the RNG seed
```

| Module | Demonstrates |
|--------|-------------|
| 1 | Baseline DTN store-and-forward over the 241-node topology |
| 2 | 1550 nm optical vs Ka-band RF link budgets at 3 distances |
| 3 | Q-learning convergence (ε-greedy decay = 0.995) |
| 4 | **Failure & recovery**: solar conjunction → optical fails → Ka-band RF via ES-L4/L5 |
| 5 | BB84 key exchange + eavesdropper detection (QBER < 11%) |
| 6 | SEU mitigation: TMR, SECDED ECC, scrubbing, FDIR watchdog |

### Scenario Runner & Agent Training (YAML-config driven)

```bash
# List available scenarios
python src/simulation/run_scenario.py --list-scenarios

# Run a simulation from a YAML config
python src/simulation/run_scenario.py --config config/earth-mars-baseline.yaml
python src/simulation/run_scenario.py --config config/solar_conjunction.yaml

# Train the RL routing agent from a YAML config
python src/routing/train_agent.py --config config/training.yaml
python src/routing/train_agent.py --episodes 5000
```

| Config File | Description |
|-------------|-------------|
| `config/earth-mars-baseline.yaml` | 30-day baseline at average distance (225 M km) |
| `config/solar_conjunction.yaml` | 14-day conjunction blackout with RF fallback |
| `config/perihelion_aphelion.yaml` | Best-case vs worst-case distance comparison |
| `config/training.yaml` | RL hyperparameters for agent training |
| `config/topology_presets.yaml` | Node counts and link parameters per tier |

---

## Modules

### `src/infrastructure/` — Link Budgets

| File | Description |
|------|-------------|
| `link_budget.py` | `OpticalLinkBudget` dataclass + `LinkBudgetCalculator` — free-space loss, EIRP, received power, link margin (CCSDS 141.0-B-1). Convenience method `calculate_mars_earth_link(scenario)` for minimum/average/maximum distance. |
| `rf_link_budget.py` | RF link budget calculator for Ka/X/S/UHF bands (CCSDS 401.0-B-30). |

### `src/routing/` — DTN Routing and AI

| File | Description |
|------|-------------|
| `bundle.py` | BPv7 bundle data structures — `Bundle`, `EndpointID`, `BundlePriority` (5 levels: EMERGENCY to BULK). RFC 9171. |
| `rl_agent.py` | `RLRoutingAgent` with epsilon-greedy policy and Q-table. `NetworkState` representation, `RoutingAction` (forward/store/drop/split). Reward: R = alpha\*delivery - beta\*delay - gamma\*hops - delta\*drops - epsilon\*energy. |
| `node.py` | `DTNNode` with `NodeType`, `NodeCapabilities`, buffer management. |
| `contact_graph.py` | Contact graph with BFS pathfinding. |
| `forwarding_engine.py` | Store-and-forward engine — `BundleQueue` priority queue, custody transfer. |
| `ltp.py` | Licklider Transmission Protocol convergence layer — segmentation, retransmission, reports. RFC 5326. |
| `tcpcl.py` | TCP Convergence Layer — session management for Earth segment. RFC 7242. |
| `udp_cl.py` | UDP Convergence Layer — optical ISL fragmentation with loss simulation. |
| `training.py` | RL training loop — `ExperienceReplay`, `TrainingEnvironment`, convergence detection. |
| `train_agent.py` | YAML-config-driven RL agent trainer — `--config config/training.yaml`, `--episodes N`. |
| `multi_agent.py` | Multi-agent federated learning — Q-table aggregation across distributed agents. |
| `prioritization.py` | Mission data prioritization — `DataCategory` (4-tier classification), `Compressor` (CCSDS 121.0-B-3 lossless, 122.0-B-2 wavelet), `QoSScheduler` (deadline-aware, preemptive), `EmergencyProtocol` (safe-mode + preemption). |

### `src/security/` — Quantum Security

| File | Description |
|------|-------------|
| `qkd.py` | `BB84Protocol` (Bennett-Brassard 1984) and `E91Protocol` (Ekert 1991) with QBER detection. `QuantumRepeater` — entanglement swapping for extended range. Security threshold: QBER < 11%. |
| `repeater_chain.py` | Multi-hop quantum repeater chain with entanglement purification. |
| `privacy_amplification.py` | CASCADE reconciliation, universal hashing, Csiszar-Korner bound. |

### `src/orbital/` — Orbital Mechanics

| File | Description |
|------|-------------|
| `contact_windows.py` | `calculate_earth_mars_distance()` (true anomaly), `calculate_light_time()`, `predict_contact_windows()`, `get_distance_timeline()` (synodic period). Handles solar conjunction blackouts. |
| `bodies.py` | Celestial body database (Sun, Earth, Mars, Moon) with orbital parameters and velocities. |
| `doppler.py` | Classical and relativistic Doppler shift calculations. |
| `topology.py` | Full 5-tier network topology (241 nodes) with inter-tier links and BFS routing. |

### `src/computing/` — Radiation-Hardened Computing

| File | Description |
|------|-------------|
| `radiation.py` | Radiation environment simulation — SEU, MBU, SEL, SET, TID, DD effects. Mitigations: TMR (Triple Modular Redundancy), SECDED ECC (Hamming), memory scrubbing, FDIR state machine with watchdog timer. |

### `src/simulation/` — Simulation Engine

| File | Description |
|------|-------------|
| `simulator.py` | Full simulation engine integrating topology, forwarding, and bundle generation. |
| `policy_engine.py` | Policy-based routing engine with 5 default policies (congestion control, emergency fast-path, etc.). |
| `run_scenario.py` | YAML-config-driven scenario runner — `--list-scenarios`, `--config config/*.yaml`. |

---

## Testing

480 unit tests across 22 test files, all passing.

```bash
./scripts/run_tests.sh        # run all tests
./scripts/run_tests.sh -v     # verbose output
make test                     # via Makefile
```

| Test File | Covers |
|-----------|--------|
| `tests/test_link_budget.py` | Optical and RF link budgets |
| `tests/test_rf_link_budget.py` | RF link budget (Ka/X/S/UHF) — FSPL, antenna gain, noise, margin |
| `tests/test_bundle.py` | BPv7 bundle data structures |
| `tests/test_rl_agent.py` | RL routing agent |
| `tests/test_training.py` | RL training loop |
| `tests/test_forwarding.py` | Store-and-forward engine |
| `tests/test_topology.py` | 5-tier topology and contact graph |
| `tests/test_contact_graph.py` | Contact graph BFS pathfinding, reachability, active contacts |
| `tests/test_simulator.py` | Simulation engine: setup, generation, stepping, run, failure recovery |
| `tests/test_qkd.py` | BB84 and E91 QKD protocols |
| `tests/test_quantum_extended.py` | Repeater chains and privacy amplification |
| `tests/test_orbital.py` | Orbital mechanics, Doppler, celestial bodies |
| `tests/test_orbital_extended.py` | Celestial body database, classical/relativistic Doppler |
| `tests/test_policy_engine.py` | Routing policy engine |
| `tests/test_radiation.py` | Radiation effects, TMR, SECDED ECC, scrubbing, FDIR |
| `tests/test_prioritization.py` | Data prioritization, compression, QoS scheduler |
| `tests/test_run_simulation.py` | End-to-end driver: all 6 modules + failure & recovery decision |
| `tests/test_ltp.py` | LTP convergence layer (RFC 5326) — segmentation, reassembly, sessions, retransmission |
| `tests/test_tcpcl.py` | TCP convergence layer (RFC 7242) — endpoints, sessions, bundle transfer |
| `tests/test_udp_cl.py` | UDP convergence layer — optical ISL fragmentation, loss simulation, reassembly |
| `tests/test_node.py` | DTN node model — buffer management, capabilities, reachability |
| `tests/test_api.py` | Backend API integration — all 7 routers via FastAPI TestClient |

---

## Web Showcase

Live at [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/). Runs entirely client-side — all simulations execute in the browser via JavaScript ports of the Python modules.

### 12 Interactive Demos

| Demo | Description |
|------|-------------|
| Mission Control Dashboard | System overview with telemetry ticker and topology visualization |
| Optical Link Budget | Calculate optical link performance for any Earth-Mars distance |
| RF Link Budget | Ka/X/S/UHF band link budget analysis |
| RL Routing Agent | Train and visualize Q-learning agent across 5-tier network |
| QKD Protocol | BB84/E91 simulation with eavesdropper detection |
| Orbital Mechanics | Earth-Mars distance timeline, contact windows, light-time delay |
| Bundle Protocol | Create BPv7 bundles, custody transfer, store-and-forward |
| DTN Engine | Full store-and-forward simulation |
| Simulation | Policy-driven simulation engine |
| Mars Mission | End-to-end mission scenario with timeline and throughput |
| Radiation Simulator | SEU/SEL/TID effects, TMR, ECC, scrubbing, FDIR |
| Priority Scheduler | 4-tier QoS scheduling with CCSDS compression and preemption |

### Learn Pages (12 topics)

What is DTN, How It Works, Journey to Mars, The Network, Space Security, Optical Communications, Deep Space Standards, Science Behind QKD, Reinforcement Learning, Radiation Hardening, Data Prioritization, Why It Matters.

### Other Pages

- **Glossary** — 90+ technical terms defined
- **Study Resources** — curated reference material
- **Usage Guide** — how to use the platform
- **Presentation Viewer** — embedded slide deck with speaker notes

### Run Locally

```bash
# Docker
docker compose up --build
# Open http://localhost:8080

# Or any static file server
python -m http.server 8080 --directory docs/
```

---

## Presentation

29-slide presentation package in `presentation/`:

- **PPTX** — animated PowerPoint with charts and diagrams (`presentation/output/AETHERIX_Presentation.pptx`)
- **PDF** — landscape PDF export (`presentation/output/AETHERIX_Presentation.pdf`)
- **Web** — embedded in the web showcase with speaker notes
- **Speaker notes** — detailed per-slide notes in `presentation/speaker_notes/`
- **Handouts** — examiner handouts in `presentation/handouts/`

### Generate

```bash
# PPTX
python presentation/generate_pptx.py

# PDF
python presentation/generate_pdf.py
```

Slide content is authored in `presentation/slides/` (Markdown per slide) and compiled by the generators.

---

## Standards Compliance

| Standard | Description |
|----------|-------------|
| CCSDS 734.2-B-1 | CCSDS Bundle Protocol Specification |
| CCSDS 735.1-B-1 | Schedule-Aware Bundle Routing (SABR) |
| CCSDS 141.0-B-1 | Optical Communications Physical Layer |
| CCSDS 131.0-B-4 | TM Space Data Link Protocol |
| CCSDS 121.0-B-3 | Lossless Data Compression |
| CCSDS 122.0-B-2 | Image Data Compression |
| RFC 9171 | Bundle Protocol Version 7 (BPv7) |
| RFC 5326 | Licklider Transmission Protocol (LTP) |
| RFC 7242 | DTN TCP Convergence Layer (TCPCL) |
| RFC 4838 | Delay-Tolerant Networking Architecture |
| NIST FIPS 203 | Module-Lattice-Based Key Encapsulation (ML-KEM) |
| NIST FIPS 204 | Module-Lattice-Based Digital Signature (ML-DSA) |

---

## Interview Preparation

The `interview_prep/` directory contains materials for technical interviews and oral examinations:

| Directory | Contents |
|-----------|----------|
| `question_bank/` | Technical Q&A organized by topic |
| `cheat_sheets/` | Formulas, constants, and quick-reference cards |
| `topic_summaries/` | Deep-dive summaries of key topics |
| `practice/` | Practice exercises and worked examples |

> **For the oral defense** — the exhaustive architectural defense covering
> Core Flight System (cFS) mapping, six whiteboarding failure scenarios,
> quantitative threshold derivations, and "why-not" alternative rebuttals is in
> **[docs/DESIGN_RATIONALE.md](docs/DESIGN_RATIONALE.md)**.

---

## License

Research / proof-of-concept. See [LICENSE](LICENSE).
