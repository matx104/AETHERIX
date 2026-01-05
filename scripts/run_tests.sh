#!/bin/bash
#
# AETHERIX - Test Runner
# =======================
# Runs the test suite for the AETHERIX project.
#
# Usage: ./scripts/run_tests.sh [options]
#
# Options:
#   --verbose, -v    Verbose output
#   --coverage       Run with coverage reporting
#   --unit           Run only unit tests
#   --help, -h       Show this help message
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
VERBOSE=""
COVERAGE=false

# Parse arguments
show_help() {
    echo "Usage: ./scripts/run_tests.sh [options]"
    echo ""
    echo "Options:"
    echo "  --verbose, -v    Verbose output"
    echo "  --coverage       Run with coverage reporting"
    echo "  --unit           Run only unit tests"
    echo "  --help, -h       Show this help message"
    exit 0
}

for arg in "$@"; do
    case $arg in
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --help|-h)
            show_help
            ;;
    esac
done

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🧪 AETHERIX Test Suite                                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set up PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Check if pytest is available
if python -c "import pytest" 2>/dev/null; then
    USE_PYTEST=true
else
    USE_PYTEST=false
fi

echo -e "${YELLOW}Running tests...${NC}\n"

if [ "$USE_PYTEST" = true ]; then
    # Run with pytest
    if [ "$COVERAGE" = true ]; then
        if python -c "import coverage" 2>/dev/null; then
            echo -e "${BLUE}Using pytest with coverage...${NC}\n"
            python -m pytest tests/ $VERBOSE --cov=src --cov-report=term-missing
        else
            echo -e "${YELLOW}⚠ Coverage not installed. Running without coverage.${NC}\n"
            python -m pytest tests/ $VERBOSE
        fi
    else
        echo -e "${BLUE}Using pytest...${NC}\n"
        python -m pytest tests/ $VERBOSE
    fi
else
    # Fall back to unittest
    echo -e "${BLUE}Using unittest (pytest not available)...${NC}\n"
    if [ -n "$VERBOSE" ]; then
        python -m unittest discover tests/ -v
    else
        python -m unittest discover tests/
    fi
fi

echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ All Tests Passed!                                       ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
