#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()   { echo -e "${CYAN}[aetherix]${NC} $*"; }
ok()    { echo -e "${GREEN}[aetherix]${NC} $*"; }
warn()  { echo -e "${YELLOW}[aetherix]${NC} $*"; }
err()   { echo -e "${RED}[aetherix]${NC} $*" >&2; }

check_pm2() {
    if ! command -v pm2 &>/dev/null; then
        err "pm2 not found. Install with: npm install -g pm2"
        exit 1
    fi
}

check_node() {
    if ! command -v node &>/dev/null; then
        err "Node.js not found. Install Node.js 18+ first."
        exit 1
    fi
}

check_python() {
    if ! command -v python3 &>/dev/null; then
        err "Python 3 not found. Install Python 3.9+ first."
        exit 1
    fi
}

setup_backend() {
    log "Setting up backend..."
    cd "$PROJECT_DIR"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q -r requirements.txt 2>/dev/null || true
    pip install -q -r backend/requirements.txt
    ok "Backend dependencies installed"
}

setup_frontend() {
    log "Setting up frontend..."
    cd "$PROJECT_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    ok "Frontend dependencies installed"
}

start_dev() {
    log "Starting AETHERIX in development mode..."
    setup_backend
    setup_frontend
    cd "$PROJECT_DIR"
    check_pm2
    pm2 start ecosystem.config.js
    pm2 save
    ok "AETHERIX started!"
    echo ""
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo ""
    echo "  Use './scripts/dev.sh logs' to view logs"
    echo "  Use './scripts/dev.sh stop' to stop all services"
}

stop_dev() {
    log "Stopping AETHERIX..."
    check_pm2
    pm2 stop ecosystem.config.js 2>/dev/null || pm2 delete ecosystem.config.js 2>/dev/null || true
    ok "Stopped"
}

restart_dev() {
    log "Restarting AETHERIX..."
    check_pm2
    pm2 restart ecosystem.config.js
    ok "Restarted"
}

status_dev() {
    check_pm2
    pm2 status
}

logs_dev() {
    check_pm2
    local service="${1:-}"
    if [ -n "$service" ]; then
        pm2 logs "aetherix-${service}" --lines 50
    else
        pm2 logs --lines 50
    fi
}

build_frontend() {
    log "Building frontend for production..."
    cd "$PROJECT_DIR/frontend"
    npm run build
    ok "Frontend built to frontend/dist/"
}

case "${1:-}" in
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    restart)
        restart_dev
        ;;
    status)
        status_dev
        ;;
    logs)
        logs_dev "${2:-}"
        ;;
    setup)
        setup_backend
        setup_frontend
        ok "Setup complete"
        ;;
    build)
        build_frontend
        ;;
    docker-up)
        log "Starting Docker Compose..."
        cd "$PROJECT_DIR"
        docker compose up -d --build
        ok "Docker containers started!"
        echo "  Frontend:  http://localhost:${FRONTEND_PORT:-3000}"
        echo "  Backend:   http://localhost:${BACKEND_PORT:-8000}"
        echo "  API Docs:  http://localhost:${BACKEND_PORT:-8000}/docs"
        echo "  Postgres:  localhost:${POSTGRES_PORT:-5432}"
        ;;
    docker-down)
        log "Stopping Docker Compose..."
        cd "$PROJECT_DIR"
        docker compose down
        ok "Docker containers stopped"
        ;;
    docker-logs)
        cd "$PROJECT_DIR"
        docker compose logs -f "${2:-}"
        ;;
    docker-ps)
        cd "$PROJECT_DIR"
        docker compose ps
        ;;
    *)
        echo "AETHERIX Development Utility"
        echo ""
        echo "Usage: ./scripts/dev.sh <command>"
        echo ""
        echo "Local (PM2):"
        echo "  start        Install deps + start backend & frontend via PM2"
        echo "  stop         Stop all PM2 processes"
        echo "  restart      Restart all PM2 processes"
        echo "  status       Show PM2 process status"
        echo "  logs [svc]   Tail logs (svc: backend|frontend)"
        echo "  setup        Install all dependencies"
        echo "  build        Build frontend for production"
        echo ""
        echo "Docker:"
        echo "  docker-up    Build & start all containers (postgres + backend + frontend)"
        echo "  docker-down  Stop & remove containers"
        echo "  docker-logs  Tail container logs"
        echo "  docker-ps    Show container status"
        ;;
esac
