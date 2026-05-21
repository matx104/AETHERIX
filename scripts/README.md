# AETHERIX Scripts

> Automation, simulation, and development utilities for the **Autonomous
> Extraterrestrial High-throughput Enhancing Routing and Inter-planetary
> eXchange** project.

---

## Quick Start

```bash
# 1. Set up the development environment
./scripts/init.sh

# 2. Run the test suite
./scripts/run_tests.sh

# 3. Explore the demos
./scripts/run_demos.sh
```

## Prerequisites

| Requirement | Version  | Notes                                      |
|-------------|----------|--------------------------------------------|
| Python      | 3.9+     | 3.9 minimum; 3.11+ recommended             |
| Bash        | 4.0+     | Required by all shell scripts              |
| Docker      | 20.10+   | Only needed for `deploy.sh`                |

---

## File Structure

```
scripts/
├── init.sh                  # Environment setup
├── run_tests.sh             # Test runner
├── run_demos.sh             # Interactive demo menu
├── link_budget_demo.sh      # Quick link-budget demo
├── lint.sh                  # Code quality checks
├── clean.sh                 # Cache & artifact cleanup
├── deploy.sh                # Docker build & deploy
│
├── sim_link_budget.py       # Optical link-budget simulation
├── sim_rf_budget.py         # RF link-budget simulation
├── sim_routing.py           # RL routing agent simulation
├── sim_qkd.py               # QKD protocol simulation
├── sim_orbital.py           # Orbital mechanics & contact windows
├── sim_topology.py          # Network topology analysis
├── sim_full_mission.py      # Full integrated mission simulation
│
└── README.md                # This file
```

---

## Environment Notes

### Virtual Environment

All shell scripts automatically detect and activate `venv/` at the project
root. If no virtual environment exists, run `./scripts/init.sh` first.

### PYTHONPATH

Every script exports `PYTHONPATH` to include `<project_root>/src`, so Python
modules under `src/` are importable without installation:

```
PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
```

If you invoke Python scripts directly, ensure this is set:

```bash
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
python scripts/sim_routing.py --help
```

---

## 1. Setup & Environment

### `init.sh` -- Environment Setup

Creates the virtual environment, installs dependencies, and verifies that
core modules import correctly.

**Usage:**

```bash
./scripts/init.sh [--dev]
```

**Options:**

| Flag     | Description                                          |
|----------|------------------------------------------------------|
| `--dev`  | Also install development tools (flake8, black, isort, mypy) |

**What it does:**

1. Checks Python >= 3.9
2. Creates `venv/` if it does not exist
3. Upgrades pip
4. Installs `requirements.txt`
5. Installs dev tools when `--dev` is passed
6. Exports `PYTHONPATH`
7. Verifies imports of five core modules (`LinkBudgetCalculator`,
   `RLRoutingAgent`, `Bundle`, `BB84Protocol`,
   `calculate_earth_mars_distance`)

**Example:**

```bash
$ ./scripts/init.sh --dev

  🚀 AETHERIX Environment Setup

Checking Python version...
✓ Found Python 3.11.5
✓ Virtual environment created
✓ Requirements installed
✓ Development dependencies installed
✓ PYTHONPATH configured
✓ LinkBudgetCalculator
✓ RLRoutingAgent
✓ Bundle
✓ BB84Protocol
✓ calculate_earth_mars_distance

  ✅ Environment Setup Complete!
```

---

## 2. Testing

### `run_tests.sh` -- Test Runner

Runs the full test suite (149 tests across 10 test files). Uses **pytest**
when available, falls back to **unittest**.

**Usage:**

```bash
./scripts/run_tests.sh [--verbose | -v] [--coverage] [--help | -h]
```

**Options:**

| Flag          | Description                                            |
|---------------|--------------------------------------------------------|
| `--verbose`, `-v` | Verbose test output                                |
| `--coverage`  | Run with `pytest-cov` coverage reporting (term-missing)|
| `--help`, `-h`| Show help message                                      |

**Examples:**

```bash
# Standard test run
./scripts/run_tests.sh

# Verbose with coverage
./scripts/run_tests.sh -v --coverage
```

**Expected output:**

```
  🧪 AETHERIX Test Suite

Using pytest...
tests/test_link_budget.py ......
tests/test_rl_agent.py .........
tests/test_qkd.py ........
tests/test_orbital.py ..........
tests/test_bundle.py .......
tests/test_topology.py .........
tests/test_forwarding.py ........
tests/test_training.py .......
tests/test_quantum_extended.py ........
tests/test_policy_engine.py .......

  ✅ All Tests Passed!
```

---

## 3. Demos

### `run_demos.sh` -- Interactive Demo Menu

Presents a menu of six interactive demonstrations covering the full AETHERIX
stack.

**Usage:**

```bash
./scripts/run_demos.sh [DEMO]
```

**Arguments:**

| Argument  | Description                                |
|-----------|--------------------------------------------|
| *(none)*  | Launch interactive menu                    |
| `1`       | Link Budget Demo                           |
| `2`       | DTN Routing Demo (BPv7 & RL routing)      |
| `3`       | Orbital Mechanics Demo                     |
| `4`       | Quantum Key Distribution Demo (BB84/E91)   |
| `5`       | Mars Mission Scenario                      |
| `6`       | Integrated Presentation Demo               |
| `all`     | Run all six demos sequentially             |
| `-h`      | Show help                                  |

**Examples:**

```bash
# Interactive menu
./scripts/run_demos.sh

# Run just the QKD demo
./scripts/run_demos.sh 4

# Run everything
./scripts/run_demos.sh all
```

**Demo source paths:**

| # | Path                                         |
|---|----------------------------------------------|
| 1 | `demos/01_link_budget_demo/run_demo.py`      |
| 2 | `demos/02_dtn_routing_demo/run_demo.py`      |
| 3 | `demos/03_orbital_mechanics_demo/run_demo.py`|
| 4 | `demos/04_quantum_key_demo/run_demo.py`      |
| 5 | `demos/05_mars_mission_scenario/run_demo.py` |
| 6 | `demos/06_integrated_demo/presentation_demo.py`|

### `link_budget_demo.sh` -- Quick Link Budget Demo

Convenience wrapper that runs `src/infrastructure/link_budget.py` with
`PYTHONPATH` configured. No arguments.

**Usage:**

```bash
./scripts/link_budget_demo.sh
```

**Expected output:** Prints optical link-budget results for minimum, average,
and maximum Earth-Mars distances including free-space loss, received power,
link margin, and achievable data rates.

---

## 4. Simulation Scripts

### `sim_link_budget.py` -- Optical Link Budget Simulation

Simulates a 1550 nm optical communications link between Earth and Mars.
Wraps `src/infrastructure/link_budget.py`.

**Usage:**

```bash
python scripts/sim_link_budget.py [OPTIONS]
```

**Arguments:**

| Argument         | Type   | Default     | Description                          |
|------------------|--------|-------------|--------------------------------------|
| `--scenario`     | str    | `average`   | Preset: `minimum`, `average`, `maximum` |
| `--distance`     | float  | *(preset)*  | Override distance (million km)       |
| `--tx-power`     | float  | 5.0         | Transmit power (W)                   |
| `--tx-aperture`  | float  | 0.22        | Transmitter aperture diameter (m)    |
| `--rx-aperture`  | float  | 5.0         | Receiver aperture diameter (m)       |
| `--data-rate`    | float  | 10.0        | Target data rate (Mbps)              |

**Examples:**

```bash
# Average-distance scenario
python scripts/sim_link_budget.py --scenario average

# Custom distance and power
python scripts/sim_link_budget.py --distance 225 --tx-power 10 --data-rate 100
```

**Expected output:** Scenario header, Earth-Mars distance, free-space path
loss (dB), EIRP (dBm), received power (dBm), link margin (dB), and
achievable vs. requested data rate.

---

### `sim_rf_budget.py` -- RF Link Budget Simulation

Simulates RF communications across Ka, X, S, and UHF bands. Wraps
`src/infrastructure/rf_link_budget.py`.

**Usage:**

```bash
python scripts/sim_rf_budget.py [OPTIONS]
```

**Arguments:**

| Argument      | Type   | Default   | Description                              |
|---------------|--------|-----------|------------------------------------------|
| `--band`      | str    | `Ka-band` | Band: `Ka-band`, `X-band`, `S-band`, `UHF-band` |
| `--distance`  | float  | 225.0     | Distance (million km)                    |
| `--tx-power`  | float  | 20.0      | Transmit power (W)                       |
| `--tx-dish`   | float  | 5.0       | Transmit dish diameter (m)               |
| `--rx-dish`   | float  | 34.0      | Receive dish diameter (m)                |
| `--data-rate` | float  | 1.0       | Target data rate (Mbps)                  |

**Examples:**

```bash
# Ka-band at average distance
python scripts/sim_rf_budget.py --band Ka-band --distance 225

# X-band with custom dishes
python scripts/sim_rf_budget.py --band X-band --tx-dish 3 --rx-dish 70 --distance 225
```

**Expected output:** Band selection, frequency, wavelength, antenna gains
(dBi), EIRP, free-space loss, system noise, received SNR, link margin, and
maximum achievable data rate.

---

### `sim_routing.py` -- RL Routing Agent Simulation

Runs the Q-learning-based routing agent to find optimal paths through the
DTN network. Wraps `src/routing/rl_agent.py`.

**Usage:**

```bash
python scripts/sim_routing.py [OPTIONS]
```

**Arguments:**

| Argument         | Type   | Default                  | Description                    |
|------------------|--------|--------------------------|--------------------------------|
| `--node`         | str    | `mars.surface.rover-01`  | Source node ID                 |
| `--destination`  | str    | `earth.control.moc`      | Destination node ID            |
| `--priority`     | int    | 0                        | Bundle priority (0-4)          |
| `--buffer`       | float  | 0.5                      | Buffer occupancy (0.0-1.0)     |
| `--episodes`     | int    | 1000                     | Training episodes              |

**Examples:**

```bash
# Default route from Mars rover to Earth MOC
python scripts/sim_routing.py --node mars.surface.rover-01 --destination earth.control.moc --priority 0

# High-priority bundle with more training
python scripts/sim_routing.py --priority 4 --episodes 5000 --buffer 0.8
```

**Expected output:** Training progress (reward convergence), Q-table
statistics, best route found (node sequence), estimated latency, hop count,
and delivery probability.

---

### `sim_qkd.py` -- QKD Protocol Simulation

Simulates quantum key distribution using BB84 or E91 protocols with optional
eavesdropper detection. Wraps `src/security/qkd.py`.

**Usage:**

```bash
python scripts/sim_qkd.py [OPTIONS]
```

**Arguments:**

| Argument         | Type    | Default | Description                          |
|------------------|---------|---------|--------------------------------------|
| `--protocol`     | str     | `bb84`  | Protocol: `bb84` or `e91`            |
| `--qubits`       | int     | 1000    | Number of qubits to simulate         |
| `--channel-error`| float   | 0.02    | Channel error rate (0.0-1.0)         |
| `--eavesdrop`    | flag    | False   | Simulate an eavesdropper (Eve)       |

**Examples:**

```bash
# Clean BB84 run
python scripts/sim_qkd.py --protocol bb84 --qubits 2000

# BB84 with eavesdropper
python scripts/sim_qkd.py --protocol bb84 --qubits 2000 --eavesdrop

# E91 entanglement-based protocol
python scripts/sim_qkd.py --protocol e91 --qubits 500 --channel-error 0.05 --eavesdrop
```

**Expected output:** Protocol header, qubits transmitted, sifted key length,
Quantum Bit Error Rate (QBER), eavesdropper detection result (QBER < 11% =
secure), and final shared key length after privacy amplification.

---

### `sim_orbital.py` -- Orbital Mechanics & Contact Windows

Computes Earth-Mars distances, light-time delays, and predicts communication
contact windows over a given time period. Wraps `src/orbital/contact_windows.py`.

**Usage:**

```bash
python scripts/sim_orbital.py [OPTIONS]
```

**Arguments:**

| Argument      | Type  | Default | Description                       |
|---------------|-------|---------|-----------------------------------|
| `--start-day` | int   | 0       | Start day (mission day 0 = t=0)   |
| `--duration`  | int   | 780     | Duration in days (default ~1 synodic period) |
| `--num-points`| int   | 100     | Number of sample points           |

**Examples:**

```bash
# Full synodic period (default)
python scripts/sim_orbital.py

# First 90 days
python scripts/sim_orbital.py --start-day 0 --duration 90

# High-resolution 30-day window
python scripts/sim_orbital.py --start-day 400 --duration 30 --num-points 500
```

**Expected output:** Distance timeline (min/avg/max km), light-time delays,
contact window list with start/end times, duration, and distance at window
center. Flags solar conjunction blackout periods.

---

### `sim_topology.py` -- Network Topology Analysis

Analyzes the 5-tier, 241-node DTN network topology. Supports route-finding
between any two nodes. Wraps `src/orbital/topology.py`.

**Usage:**

```bash
python scripts/sim_topology.py [OPTIONS]
```

**Arguments:**

| Argument        | Type  | Default                  | Description              |
|-----------------|-------|--------------------------|--------------------------|
| `--source`      | str   | `mars.surface.rover-01`  | Source node ID           |
| `--destination` | str   | `earth.dsn.goldstone`    | Destination node ID      |

**Examples:**

```bash
# Default route: Mars rover to Goldstone DSN
python scripts/sim_topology.py --source mars.surface.rover-01 --destination earth.dsn.goldstone

# Mars drone to Madrid DSN
python scripts/sim_topology.py --source mars.surface.drone-03 --destination earth.dsn.madrid

# Print full topology summary (no route args)
python scripts/sim_topology.py
```

**Expected output:** Topology summary (nodes per tier, total links), BFS
shortest-path route from source to destination with hop-by-hop node IDs,
inter-tier link types, and estimated total latency.

---

### `sim_full_mission.py` -- Full Integrated Mission Simulation

End-to-end simulation combining topology, orbital mechanics, routing,
forwarding, and bundle generation. Wraps `src/simulation/simulator.py`.

**Usage:**

```bash
python scripts/sim_full_mission.py [OPTIONS]
```

**Arguments:**

| Argument      | Type   | Default | Description                            |
|---------------|--------|---------|----------------------------------------|
| `--duration`  | float  | 168.0   | Simulation duration (hours)            |
| `--step`      | float  | 1.0     | Time step (hours)                      |
| `--rate`      | float  | 10.0    | Bundle generation rate (bundles/hour)  |
| `--seed`      | int    | 42      | Random seed for reproducibility        |
| `--name`      | str    | `mission` | Simulation run name                  |

**Examples:**

```bash
# 1-week simulation at 10 bundles/hour
python scripts/sim_full_mission.py --duration 168 --rate 10 --seed 42

# 24-hour high-resolution run
python scripts/sim_full_mission.py --duration 24 --step 0.25 --rate 50 --seed 7

# Named run for reproducibility
python scripts/sim_full_mission.py --duration 336 --name "mars-ops-phase-2" --seed 123
```

**Expected output:** Simulation progress log, bundle statistics (generated,
delivered, dropped, stored), average end-to-end latency, per-tier throughput,
route diversity, and a summary table. Results are seed + config reproducible.

> **Reproducibility note:** Always report `--seed` and `--duration`/`--rate`
> when citing simulation results.

---

## 5. Code Quality

### `lint.sh` -- Code Quality Checks

Runs four linters sequentially: **flake8**, **black**, **isort**, **mypy**.
Exits non-zero if any tool reports issues.

**Usage:**

```bash
./scripts/lint.sh [--fix] [--check] [--help | -h]
```

**Options:**

| Flag       | Description                                      |
|------------|--------------------------------------------------|
| *(none)*   | Check only -- no file modifications (default)     |
| `--fix`    | Auto-fix formatting (black) and import order (isort) |
| `--check`  | Explicit check-only mode (default behavior)       |
| `--help`   | Show help                                        |

**Tools & configuration:**

| Tool    | Scope           | Configuration                               |
|---------|-----------------|---------------------------------------------|
| flake8  | `src/`, `tests/`| `--max-line-length=100`, ignore `E501,W503` |
| black   | `src/`, `tests/`| `--line-length=100`                         |
| isort   | `src/`, `tests/`| default profile                             |
| mypy    | `src/`          | `--ignore-missing-imports`                  |

**Examples:**

```bash
# Check only
./scripts/lint.sh

# Auto-fix formatting and import order
./scripts/lint.sh --fix
```

> Requires dev dependencies. Run `./scripts/init.sh --dev` first.

### `clean.sh` -- Cleanup

Removes Python caches, pytest/mypy caches, coverage artifacts, and build
directories.

**Usage:**

```bash
./scripts/clean.sh [--all] [--help | -h]
```

**Options:**

| Flag     | Description                                  |
|----------|----------------------------------------------|
| *(none)* | Clean caches and artifacts only              |
| `--all`  | Also remove `venv/`                          |
| `--help` | Show help                                    |

**What it removes:**

- `__pycache__/`, `*.pyc`, `*.pyo`
- `.pytest_cache/`, `.coverage`, `htmlcov/`
- `.mypy_cache/`
- `build/`, `dist/`, `*.egg-info`
- `venv/` (only with `--all`)

**Example:**

```bash
# Quick clean
./scripts/clean.sh

# Full reset (also removes venv)
./scripts/clean.sh --all
```

---

## 6. Deployment

### `deploy.sh` -- Docker Build & Deploy

Builds and manages the AETHERIX showcase site container.

**Usage:**

```bash
./scripts/deploy.sh [COMMAND]
```

**Commands:**

| Flag       | Description                          |
|------------|--------------------------------------|
| `--build`  | Build the Docker image               |
| `--up`     | Start the container                  |
| `--down`   | Stop and remove the container        |
| `--logs`   | Tail container logs                  |

**Examples:**

```bash
# Build and start
./scripts/deploy.sh --build && ./scripts/deploy.sh --up

# Check logs
./scripts/deploy.sh --logs

# Tear down
./scripts/deploy.sh --down
```

> Requires Docker 20.10+ and a `Dockerfile` at the project root.

---

## Tips & Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure `PYTHONPATH` includes `src/`. Scripts set this automatically, but direct `python` invocations may need `export PYTHONPATH="$(pwd)/src:$PYTHONPATH"`. |
| `python: command not found` | Install Python 3.9+ or use `python3` explicitly. |
| `Permission denied` on scripts | `chmod +x scripts/*.sh` |
| pytest not found | Tests fall back to unittest automatically, or run `./scripts/init.sh` to install pytest. |
| Linting tools not found | Run `./scripts/init.sh --dev` to install flake8, black, isort, and mypy. |
| Stale imports or weird test failures | Run `./scripts/clean.sh` to clear all caches, then re-run. |
| Simulation results vary between runs | Pass `--seed` for deterministic, reproducible output. Always report seed + config when citing results. |

---

## Summary Table

| Script | Type | Category | One-liner |
|--------|------|----------|-----------|
| `init.sh` | Shell | Setup | Create venv, install deps, verify imports |
| `run_tests.sh` | Shell | Testing | Run 149 tests via pytest or unittest |
| `run_demos.sh` | Shell | Demos | Interactive menu for 6 demo modules |
| `link_budget_demo.sh` | Shell | Demos | Quick optical link-budget demo |
| `lint.sh` | Shell | Quality | flake8 + black + isort + mypy |
| `clean.sh` | Shell | Quality | Remove caches, artifacts, optionally venv |
| `deploy.sh` | Shell | Deploy | Docker build/up/down/logs |
| `sim_link_budget.py` | Python | Simulation | 1550 nm optical link budget |
| `sim_rf_budget.py` | Python | Simulation | Ka/X/S/UHF RF link budget |
| `sim_routing.py` | Python | Simulation | RL routing agent & pathfinding |
| `sim_qkd.py` | Python | Simulation | BB84/E91 quantum key distribution |
| `sim_orbital.py` | Python | Simulation | Earth-Mars orbital mechanics |
| `sim_topology.py` | Python | Simulation | 241-node, 5-tier topology analysis |
| `sim_full_mission.py` | Python | Simulation | End-to-end integrated mission sim |
