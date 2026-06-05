# AETHERIX Usage Guide

AETHERIX can be used through three interfaces: **Web** (full-stack app), **CLI** (command line), and **Docker** (containerized). Choose the one that fits your workflow.

## Prerequisites

- Python 3.9+
- Node.js 18+ (Web interface only)
- Docker & Docker Compose (Docker interface only)
- Git

---

## Web Interface

The web interface provides a React dashboard with real-time visualizations, a command terminal, and API-driven calculations for all modules.

### Quick Start (PM2 + SQLite)

```bash
git clone https://github.com/matx104/AETHERIX.git
cd AETHERIX
./scripts/dev.sh setup    # install all deps (Python + Node.js)
./scripts/dev.sh start    # start backend + frontend via PM2
```

| URL | Service |
|-----|---------|
| http://localhost:3000 | Frontend Dashboard |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Swagger API Docs |

### Web Pages

| Page | Features |
|------|----------|
| **Dashboard** | System health, module status, network overview |
| **Link Budget** | Optical/RF calculations, history, scenario comparison |
| **RL Routing** | Routing decisions, confidence scores, decision history |
| **Orbital** | Distance timeline, light-time delay, contact windows |
| **QKD Security** | BB84/E91 simulation, QBER analysis, session history |
| **Simulations** | Create/manage simulation runs with seeds |
| **Command Reference** | Copy the exact command for any script/module, with expected output |

### Command Reference

The Command Reference page is a read-only catalog of all 23 commands. For each one it shows the exact command to copy, what it does, and the output to expect:

- **Shell Scripts**: init, test, lint, clean (with variants)
- **Python Modules**: all 16 module demos (link budget, routing, QKD, orbital, simulation)

Select a command from the sidebar, read the description and expected output, then click **Copy** and run it in your own terminal from the project root. Nothing is executed by the browser or the server.

### PM2 Management

| Command | Description |
|---------|-------------|
| `./scripts/dev.sh start` | Install deps + start backend & frontend |
| `./scripts/dev.sh stop` | Stop all PM2 processes |
| `./scripts/dev.sh restart` | Restart all processes |
| `./scripts/dev.sh status` | Show PM2 process status |
| `./scripts/dev.sh logs [backend\|frontend]` | Tail logs |
| `./scripts/dev.sh build` | Build frontend for production |

---

## CLI (Command Line)

For direct Python module execution. Requires only Python 3.9+ with a virtual environment.

### Environment Setup

```bash
git clone https://github.com/matx104/AETHERIX.git
cd AETHERIX
./scripts/init.sh          # set up venv + install deps
./scripts/run_tests.sh     # verify: 189 tests pass
```

### Utility Scripts

| Script | Description |
|--------|-------------|
| `./scripts/init.sh` | Set up virtual environment and install dependencies |
| `./scripts/init.sh --dev` | Include development tools (linting, formatting) |
| `./scripts/run_tests.sh` | Run the full test suite (189 tests) |
| `./scripts/run_tests.sh -v` | Verbose test output |
| `./scripts/run_demos.sh` | Interactive demo menu (6 Python demos) |
| `./scripts/run_demos.sh 1-6` | Run specific demo |
| `./scripts/lint.sh` | Code quality checks (ruff) |
| `./scripts/lint.sh --fix` | Auto-fix code style issues |
| `./scripts/clean.sh` | Clean artifacts and caches |

### Python Modules

| Command | Module |
|---------|--------|
| `python src/infrastructure/link_budget.py` | Optical link budget calculations |
| `python src/infrastructure/rf_link_budget.py` | RF link budget (Ka/X/S/UHF) |
| `python src/routing/rl_agent.py` | RL routing agent demo |
| `python src/routing/bundle.py` | BPv7 bundle protocol demo |
| `python src/routing/prioritization.py` | Data prioritization scheduler |
| `python src/routing/forwarding_engine.py` | Store-and-forward demo |
| `python src/routing/training.py` | RL training loop |
| `python src/security/qkd.py` | QKD protocol simulation (BB84/E91) |
| `python src/security/repeater_chain.py` | Quantum repeater chain |
| `python src/security/privacy_amplification.py` | CASCADE reconciliation |
| `python src/orbital/contact_windows.py` | Contact window prediction |
| `python src/orbital/doppler.py` | Doppler shift calculations |
| `python src/orbital/topology.py` | 5-tier network topology |
| `python src/computing/radiation.py` | Radiation hardening simulation |
| `python src/simulation/simulator.py` | Full simulation engine |
| `python src/simulation/policy_engine.py` | Policy-based routing |

---

## Docker (Containerized)

For production or isolated environments. Runs PostgreSQL, backend, and frontend in separate containers.

### Quick Start

```bash
./scripts/dev.sh docker-up    # build & start all containers
```

| URL | Service |
|-----|---------|
| http://localhost:3000 | Frontend (nginx) |
| http://localhost:8000 | Backend API (FastAPI) |
| localhost:5432 | PostgreSQL database |

### Docker Management

| Command | Description |
|---------|-------------|
| `./scripts/dev.sh docker-up` | Build & start all containers (postgres + backend + frontend) |
| `./scripts/dev.sh docker-down` | Stop & remove containers |
| `./scripts/dev.sh docker-logs [service]` | Tail container logs |
| `./scripts/dev.sh docker-ps` | Show container status |

### Configuration

Environment variables are set in `.env` (copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./aetherix.db` | Database connection (auto-set to PostgreSQL in Docker) |
| `POSTGRES_DB` | `aetherix` | PostgreSQL database name |
| `POSTGRES_USER` | `aetherix` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `aetherix_dev` | PostgreSQL password |
| `BACKEND_PORT` | `8000` | Backend API port |
| `FRONTEND_PORT` | `3000` | Frontend port |
| `DEBUG` | `true` | Debug mode |

---

## Showcase Site

The standalone showcase site runs without a backend:

```bash
cd docs
python -m http.server 8080
# Open http://localhost:8080
```

Live at [matx104.github.io/AETHERIX](https://matx104.github.io/AETHERIX/)

The showcase includes 12 interactive browser demos plus the Command Terminal (requires the full-stack backend running).

---

## Presentation

```bash
cd presentation
pip install python-pptx reportlab   # if not installed
python generate_pptx.py             # -> AETHERIX_Presentation.pptx
python generate_pdf.py              # -> AETHERIX_Presentation.pdf
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ImportError` | Run `./scripts/init.sh` to install dependencies |
| Tests failing | Ensure virtual environment is activated (`source venv/bin/activate`) |
| `pm2 not found` | Install with `npm install -g pm2` |
| Docker DB connection refused | Wait for PostgreSQL healthcheck to pass, or run `docker compose ps` |
| Site not loading | Must serve `docs/` via HTTP (not `file://`) |
| PPTX generation fails | Install `python-pptx` (`pip install python-pptx`) |
| Frontend build errors | Delete `frontend/node_modules` and run `npm install` again |
