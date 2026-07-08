# Contributing to AETHERIX

Thank you for your interest in improving AETHERIX! This document covers the
development workflow, coding standards, and review process.

## Quick Start

```bash
# Clone and set up
git clone https://github.com/matx104/AETHERIX.git
cd AETHERIX
./scripts/init.sh

# Activate the virtual environment
source venv/bin/activate

# Run the test suite
python -m pytest

# Or via Makefile
make test
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use conventional prefixes: `feature/`, `bugfix/`, `docs/`, `test/`, `refactor/`.

### 2. Write Code

Follow the existing patterns:

- **Python core** (`src/`): pure standard library, no external dependencies.
  Every module must work with `python run_simulation.py` on a clean checkout.
- **Backend** (`backend/`): FastAPI + SQLAlchemy + Pydantic.
- **Frontend** (`frontend/`): React + TypeScript + Vite.

### 3. Write Tests

Every new module or feature must include tests:

```bash
# Tests live in tests/ and follow the naming convention test_<module>.py
# Run the full suite:
python -m pytest

# Run a specific file:
python -m pytest tests/test_rf_link_budget.py -v

# Run with coverage:
python -m pytest --cov=src --cov-report=term-missing
```

### 4. Lint

```bash
./scripts/lint.sh          # check
./scripts/lint.sh --fix    # auto-fix
```

### 5. Commit

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add X-band link budget calculation
fix: simulator bundle expiry using sim-time instead of wall-clock
docs: add RL hyperparameter defense to interview prep
test: add contact graph BFS pathfinding tests
refactor: consolidate duplicate YAML parser into shared utility
```

### 6. Verify

Before submitting a PR:

```bash
make test          # all tests pass
make lint          # no linting errors
python run_simulation.py  # end-to-end driver works
```

## Coding Standards

### Python

- **No external dependencies** in `src/` — pure standard library only.
  External packages (FastAPI, Pydantic) are acceptable in `backend/`.
- **Type hints** on all public functions.
- **Docstrings** on all classes and public methods.
- **Dataclasses** for structured data (not bare dicts).
- **No comments** in code unless explaining a non-obvious algorithmic decision.
  Prefer self-documenting names.
- **Test files** use `unittest.TestCase` (matching the existing convention).

### Frontend (TypeScript/React)

- Functional components with hooks.
- Typed props via interfaces.
- API calls go through `src/api/client.ts`.

### Shell Scripts

- Always quote variables containing paths.
- Use `set -euo pipefail` at the top.
- Check for dependencies before using them.

## Project Structure

```
src/           # Core simulation (pure Python stdlib)
backend/       # FastAPI web API
frontend/      # React SPA
tests/         # Test suite (unittest)
config/        # YAML scenario/training configs
scripts/       # Shell utilities
docs/          # Documentation
presentation/  # Slides and handouts
interview_prep/ # Oral exam preparation materials
```

## Reporting Issues

Use [GitHub Issues](https://github.com/matx104/AETHERIX/issues) with the
appropriate label:

| Label | Use for |
|-------|---------|
| `bug` | Something doesn't work as expected |
| `enhancement` | Feature request |
| `module:link-budget` | Link budget module issues |
| `module:routing` | RL routing / forwarding issues |
| `module:security` | QKD / cryptography issues |
| `module:orbital` | Orbital mechanics issues |
| `module:simulation` | Simulator engine issues |
| `reproducibility` | Cannot reproduce simulation results |
| `paper` | Documentation / paper concerns |

For simulation-related bugs, include: seed, config file, expected vs actual
output. Reproducibility is critical for scientific results.

## License

This project does not currently have an open-source license. All rights
reserved by the author.
