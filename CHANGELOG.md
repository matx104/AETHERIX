# Changelog

All notable changes to the AETHERIX project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-07-09

### Added
- **End-to-end simulation driver** (`run_simulation.py`): zero-dependency,
  clone-and-run entry point exercising all six AETHERIX modules
  (DTN baseline, link budgets, RL convergence, failure & recovery, QKD,
  radiation hardening)
- **Scenario runner** (`src/simulation/run_scenario.py`): YAML-config-driven
  simulation with `--list-scenarios` support
- **RL training CLI** (`src/routing/train_agent.py`): YAML-config-driven
  agent training with hyperparameter overrides
- **Config files** (`config/`): 5 scenario YAMLs (earth-mars-baseline,
  solar-conjunction, perihelion-aphelion, training, topology-presets)
- **Failure & recovery logic** in simulator: solar conjunction triggers
  optical failure, Ka-band RF fallback via Lagrange relays
- **Tier-aware routing**: `NetworkState` gains `current_tier` and
  `neighbor_tiers` fields for Earth-ward preference in forwarding decisions
- **Design rationale document** (`docs/DESIGN_RATIONALE.md`): exhaustive
  defense covering cFS mapping, tooling honesty, whiteboarding scenarios,
  quantitative derivations, "why-not" rebuttals, and a master decision matrix
- **Usage guide** (`docs/USAGE_GUIDE.md`): comprehensive reference for all
  CLI/web/Docker interfaces plus 14 design-decision subsections
- **RL hyperparameter defense** (`interview_prep/question_bank/rl_hyperparameters.md`):
  per-knob justification for epsilon, learning rate, discount, buffer, and
  reward weights
- **Trade-off analysis** slide (`presentation/slides/16_trade_off_analysis.md`)
- **Failure & recovery** slide (`presentation/slides/17_failure_recovery.md`)
- **Rendered diagrams** (`docs/diagrams/`): 5 PNGs alongside `.mmd` sources
- **API reference** (`docs/API_REFERENCE.md`): full endpoint documentation
- **Link budget topic summary** (`interview_prep/topic_summaries/link_budget.md`)
- **RL topic summary** (`interview_prep/topic_summaries/reinforcement_learning.md`)
- **`.env.example`**: backend environment template
- **`CONTRIBUTING.md`**: contribution guidelines
- **`Makefile`**: consolidated test/lint/slides/run targets
- **Contact graph tests** (`tests/test_contact_graph.py`): BFS pathfinding,
  reachability, active-contact queries (30 tests)
- **Simulator tests** (`tests/test_simulator.py`): setup, generation,
  stepping, run, progress, inject, failure recovery (38 tests)
- **RF link budget tests** (`tests/test_rf_link_budget.py`): FSPL, antenna
  gain, noise, full link budget, multi-band comparison (42 tests)
- **Run simulation tests** (`tests/test_run_simulation.py`): end-to-end
  driver + failure-recovery assertions (13 tests)

### Changed
- **Simulator propagation bug fixed**: forwarded bundles now reach neighbor
  engines via `_propagate_forwarded()` with `_active_bundles` tracking
- **Simulator expiry bug fixed**: bundles compared against sim-time birth
  via `_bundle_sim_birth` dict instead of wall-clock `time.time()`
- **`requirements.txt` rewritten**: pinned versions, honest zero-dep
  explanation, optional presentation-gen deps separated
- **`README.md` restructured**: new Basic Usage section, table of contents,
  test counts updated to 311, design-rationale link added

### Removed
- Stale "Future Commands" references to nonexistent scripts in
  AGENTS.md, CLAUDE.md, GEMINI.md, .github/copilot-instructions.md
  (scripts now exist and are documented under "Scenario Runner & Training")

## [2.0.0] - 2026-06-15

### Added
- FastAPI backend with 7 routers (health, simulations, link-budget, routing,
  orbital, security, cmd)
- React + Vite + TypeScript frontend with 9 pages
- Docker Compose configuration (PostgreSQL + backend + frontend)
- PM2 process management (`scripts/dev.sh`)
- RL multi-agent federated learning (`src/routing/multi_agent.py`)
- LTP convergence layer (`src/routing/ltp.py`)
- TCPCL convergence layer (`src/routing/tcpcl.py`)
- UDP convergence layer (`src/routing/udp_cl.py`)
- Quantum repeater chain (`src/security/repeater_chain.py`)
- Privacy amplification (`src/security/privacy_amplification.py`)
- RF link budget calculator (`src/infrastructure/rf_link_budget.py`)
- Policy-based routing engine (`src/simulation/policy_engine.py`)
- Orbital Doppler calculations (`src/orbital/doppler.py`)
- Celestial body database (`src/orbital/bodies.py`)
- Full 5-tier network topology with 241 nodes (`src/orbital/topology.py`)
- Presentation generator scripts (PPTX + PDF, full + compact)
- Interview prep question bank with 125+ questions

## [1.0.0] - 2026-05-01

### Added
- Core modules: optical link budget, RL routing agent, BPv7 bundle protocol,
  BB84/E91 QKD protocols, orbital contact windows
- DTN node model with buffer management
- Contact graph with BFS pathfinding
- Forwarding engine with custody transfer
- Basic test suite (149 tests)
- Initial project structure and documentation
