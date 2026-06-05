# AETHERIX Usage Guide

## Prerequisites

- Python 3.9+
- Git
- pip

## Quick Start

```bash
git clone https://github.com/matx104/AETHERIX.git
cd AETHERIX
./scripts/init.sh
```

## Scripts Reference

| Script | Description |
|--------|-------------|
| `./scripts/init.sh` | Set up virtual environment, install dependencies |
| `./scripts/init.sh --dev` | Include dev tools (linting, formatting) |
| `./scripts/run_tests.sh` | Run the full test suite (189 tests) |
| `./scripts/run_tests.sh -v` | Verbose output |
| `./scripts/run_demos.sh` | Interactive demo menu (6 demos) |
| `./scripts/run_demos.sh 1-6` | Run specific demo |
| `./scripts/link_budget_demo.sh` | Link budget demo |
| `./scripts/lint.sh` | Code quality checks (ruff) |
| `./scripts/lint.sh --fix` | Auto-fix code style |
| `./scripts/clean.sh` | Clean artifacts and caches |

## Running Individual Modules

| Command | Description |
|---------|-------------|
| `python src/infrastructure/link_budget.py` | Optical link budget calculations |
| `python src/infrastructure/rf_link_budget.py` | RF link budget (Ka/X/S/UHF) |
| `python src/routing/rl_agent.py` | RL routing agent demo |
| `python src/routing/bundle.py` | BPv7 bundle protocol demo |
| `python src/routing/prioritization.py` | Data prioritization scheduler demo |
| `python src/routing/forwarding_engine.py` | Store-and-forward demo |
| `python src/routing/training.py` | RL training loop demo |
| `python src/security/qkd.py` | QKD protocol simulation |
| `python src/security/repeater_chain.py` | Quantum repeater chain demo |
| `python src/security/privacy_amplification.py` | CASCADE reconciliation demo |
| `python src/orbital/contact_windows.py` | Contact window prediction |
| `python src/orbital/doppler.py` | Doppler shift calculations |
| `python src/orbital/topology.py` | 5-tier network topology demo |
| `python src/computing/radiation.py` | Radiation hardening simulation |
| `python src/simulation/simulator.py` | Full simulation engine |
| `python src/simulation/policy_engine.py` | Policy-based routing demo |

## Web Showcase

```bash
cd docs
python -m http.server 8080
# Open http://localhost:8080
```

The showcase includes 12 interactive demos:

1. Mission Control Dashboard
2. Optical Link Budget
3. RF Link Budget
4. RL Routing Agent
5. QKD Protocol
6. Orbital Mechanics
7. Bundle Protocol
8. DTN Engine
9. Simulation
10. Mars Mission
11. Radiation Simulator
12. Priority Scheduler

## Presentation Generation

```bash
cd presentation
pip install python-pptx reportlab  # if not installed
python generate_pptx.py   # -> AETHERIX_Presentation.pptx
python generate_pdf.py    # -> AETHERIX_Presentation.pdf
```

## Docker

```bash
docker-compose up -d
```

## GitHub Pages

The `docs/` directory is served via GitHub Pages at `https://matx104.github.io/AETHERIX/`.

## Project Structure

```
AETHERIX/
├── src/                # Python source modules (6 packages)
│   ├── infrastructure/ # Link budget calculations
│   ├── routing/        # RL-based DTN routing
│   ├── security/       # QKD protocols
│   ├── orbital/        # Orbital mechanics
│   ├── computing/      # Radiation hardening
│   └── simulation/     # Simulation engine
├── tests/              # 189 unit tests across 12 test files
├── docs/               # Web showcase site (single-page app)
│   └── js/             # JavaScript engine and app logic
├── presentation/       # PPTX/PDF generation scripts
├── demos/              # 6 interactive Python demos
├── scripts/            # Shell scripts for development tasks
├── interview_prep/     # Question bank and study materials
└── visualizations/     # Chart and visualization scripts
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ImportError` | Run `./scripts/init.sh` to install dependencies |
| Tests failing | Ensure virtual environment is activated (`source venv/bin/activate`) |
| Site not loading | Must serve `docs/` via HTTP (not `file://`) for JS modules |
| PPTX generation fails | Install `python-pptx` (`pip install python-pptx`) |
