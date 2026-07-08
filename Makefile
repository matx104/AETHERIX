# AETHERIX Makefile
# Consolidated targets for common development tasks.
#
# Usage:
#   make test         Run the full test suite
#   make test-v       Verbose test output
#   make lint         Run code quality checks
#   make run          Run the end-to-end simulation driver
#   make scenario     Run a specific YAML scenario (SCENARIO=...)
#   make train        Train the RL routing agent (EPISODES=...)
#   make slides       Generate presentation PPTX + PDF
#   make backend      Start backend dev server
#   make frontend     Start frontend dev server
#   make docker-up    Start all containers
#   make docker-down  Stop all containers
#   make clean        Clean build artifacts
#   make help         Show this help

.PHONY: help test test-v lint lint-fix run scenario train slides backend frontend docker-up docker-down clean

PYTHON ?= python
SCENARIO ?= config/earth-mars-baseline.yaml
EPISODES ?= 1000

help:
	@echo "AETHERIX Makefile Targets:"
	@echo ""
	@echo "  make test         Run the full test suite"
	@echo "  make test-v       Verbose test output"
	@echo "  make lint         Run code quality checks"
	@echo "  make lint-fix     Auto-fix code style issues"
	@echo "  make run          Run the end-to-end simulation driver"
	@echo "  make scenario     Run a YAML scenario (SCENARIO=config/...)"
	@echo "  make train        Train RL agent (EPISODES=5000)"
	@echo "  make slides       Generate presentation PPTX + PDF"
	@echo "  make backend      Start backend dev server"
	@echo "  make frontend     Start frontend dev server"
	@echo "  make docker-up    Start all Docker containers"
	@echo "  make docker-down  Stop all Docker containers"
	@echo "  make clean        Clean build artifacts"
	@echo ""

test:
	$(PYTHON) -m pytest --tb=short -q

test-v:
	$(PYTHON) -m pytest -v --tb=short

lint:
	./scripts/lint.sh

lint-fix:
	./scripts/lint.sh --fix

run:
	$(PYTHON) run_simulation.py

scenario:
	$(PYTHON) src/simulation/run_scenario.py --config $(SCENARIO)

train:
	$(PYTHON) src/routing/train_agent.py --episodes $(EPISODES)

slides:
	$(PYTHON) presentation/generate_pptx.py
	$(PYTHON) presentation/generate_pdf.py

backend:
	cd backend && $(PYTHON) run.py

frontend:
	cd frontend && npm run dev

docker-up:
	./scripts/dev.sh docker-up

docker-down:
	./scripts/dev.sh docker-down

clean:
	./scripts/clean.sh
