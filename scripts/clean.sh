#!/bin/bash
#
# AETHERIX - Clean Script
# ========================
# Cleans up build artifacts, cache files, and temporary files.
#
# Usage: ./scripts/clean.sh [options]
#
# Options:
#   --all        Remove everything including venv
#   --help, -h   Show this help message
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the root directory of the project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default options
CLEAN_ALL=false

# Parse arguments
show_help() {
    echo "Usage: ./scripts/clean.sh [options]"
    echo ""
    echo "Options:"
    echo "  --all        Remove everything including venv"
    echo "  --help, -h   Show this help message"
    exit 0
}

for arg in "$@"; do
    case $arg in
        --all)
            CLEAN_ALL=true
            shift
            ;;
        --help|-h)
            show_help
            ;;
    esac
done

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🧹 AETHERIX Cleanup                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$PROJECT_ROOT"

# Clean Python cache
echo -e "${YELLOW}Cleaning Python cache...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✓ Python cache cleaned${NC}"

# Clean pytest cache
echo -e "${YELLOW}Cleaning pytest cache...${NC}"
rm -rf .pytest_cache 2>/dev/null || true
rm -rf .coverage 2>/dev/null || true
rm -rf htmlcov 2>/dev/null || true
echo -e "${GREEN}✓ pytest cache cleaned${NC}"

# Clean mypy cache
echo -e "${YELLOW}Cleaning mypy cache...${NC}"
rm -rf .mypy_cache 2>/dev/null || true
echo -e "${GREEN}✓ mypy cache cleaned${NC}"

# Clean build artifacts
echo -e "${YELLOW}Cleaning build artifacts...${NC}"
rm -rf build 2>/dev/null || true
rm -rf dist 2>/dev/null || true
rm -rf *.egg-info 2>/dev/null || true
echo -e "${GREEN}✓ Build artifacts cleaned${NC}"

# Clean virtual environment if --all
if [ "$CLEAN_ALL" = true ]; then
    echo -e "${YELLOW}Removing virtual environment...${NC}"
    rm -rf venv 2>/dev/null || true
    echo -e "${GREEN}✓ Virtual environment removed${NC}"
fi

echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Cleanup Complete                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ "$CLEAN_ALL" = true ]; then
    echo -e "Run ${BLUE}./scripts/init.sh${NC} to set up the environment again."
fi
echo ""
