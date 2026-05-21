#!/bin/bash
#
# AETHERIX - Deployment Script
# ==============================
# Manages Docker-based deployment for the AETHERIX project.
#
# Usage: ./scripts/deploy.sh [command]
#
# Commands:
#   build      Build the Docker image
#   up         Build and start the container (detached)
#   down       Stop and remove the container
#   logs       Tail container logs
#   restart    Stop, rebuild, and start
#   status     Show container status
#   --help,-h  Show this help message
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

show_help() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 AETHERIX Deployment Manager                             ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Usage: ./scripts/deploy.sh <command>"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}build${NC}      Build the Docker image"
    echo -e "  ${GREEN}up${NC}         Build and start the container (detached)"
    echo -e "  ${GREEN}down${NC}       Stop and remove the container"
    echo -e "  ${GREEN}logs${NC}       Tail container logs"
    echo -e "  ${GREEN}restart${NC}    Stop, rebuild, and start"
    echo -e "  ${GREEN}status${NC}     Show container status"
    echo -e "  ${GREEN}--help, -h${NC} Show this help message"
    echo ""
    echo "Docker Compose file: $COMPOSE_FILE"
    echo ""
}

check_prerequisites() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed or not in PATH${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker found${NC}"

    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo -e "${RED}✗ Docker Compose is not installed or not in PATH${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose found${NC}"

    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}✗ docker-compose.yml not found at $COMPOSE_FILE${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ docker-compose.yml found${NC}"
}

do_build() {
    echo -e "\n${YELLOW}Building Docker image...${NC}"
    $COMPOSE_CMD -f "$COMPOSE_FILE" build
    echo -e "${GREEN}✓ Build complete${NC}"
}

do_up() {
    echo -e "\n${YELLOW}Building and starting container...${NC}"
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d --build
    echo -e "${GREEN}✓ Container started${NC}"
    echo -e "\n${BLUE}Application available at:${NC} http://localhost:8080"
}

do_down() {
    echo -e "\n${YELLOW}Stopping and removing container...${NC}"
    $COMPOSE_CMD -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✓ Container stopped and removed${NC}"
}

do_logs() {
    echo -e "\n${YELLOW}Tailing container logs (Ctrl+C to exit)...${NC}"
    $COMPOSE_CMD -f "$COMPOSE_FILE" logs -f
}

do_restart() {
    echo -e "\n${YELLOW}Restarting deployment...${NC}"
    do_down
    do_up
    echo -e "${GREEN}✓ Restart complete${NC}"
}

do_status() {
    echo -e "\n${YELLOW}Container status:${NC}"
    $COMPOSE_CMD -f "$COMPOSE_FILE" ps
}

COMMAND="${1:-}"

case "$COMMAND" in
    build|--build)
        echo -e "${BLUE}"
        echo "╔══════════════════════════════════════════════════════════════════════════════╗"
        echo "║                    🚀 AETHERIX Build                                         ║"
        echo "╚══════════════════════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
        check_prerequisites
        do_build
        ;;
    up|--up)
        echo -e "${BLUE}"
        echo "╔══════════════════════════════════════════════════════════════════════════════╗"
        echo "║                    🚀 AETHERIX Deploy                                        ║"
        echo "╚══════════════════════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
        check_prerequisites
        do_up
        ;;
    down|--down)
        echo -e "${BLUE}"
        echo "╔══════════════════════════════════════════════════════════════════════════════╗"
        echo "║                    🚀 AETHERIX Teardown                                      ║"
        echo "╚══════════════════════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
        check_prerequisites
        do_down
        ;;
    logs|--logs)
        check_prerequisites
        do_logs
        ;;
    restart|--restart)
        echo -e "${BLUE}"
        echo "╔══════════════════════════════════════════════════════════════════════════════╗"
        echo "║                    🚀 AETHERIX Restart                                       ║"
        echo "╚══════════════════════════════════════════════════════════════════════════════╝"
        echo -e "${NC}"
        check_prerequisites
        do_restart
        ;;
    status|--status)
        check_prerequisites
        do_status
        ;;
    --help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}\n"
        show_help
        exit 1
        ;;
esac
