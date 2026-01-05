#!/bin/bash
#
# AETHERIX - Initialization Script
# =================================
# Sets up the development environment for the AETHERIX project.
#
# Usage: ./scripts/init.sh [--dev]
#   --dev   Install development dependencies (linting, etc.)
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

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🚀 AETHERIX Environment Setup                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Parse arguments
DEV_MODE=false
for arg in "$@"; do
    case $arg in
        --dev)
            DEV_MODE=true
            shift
            ;;
    esac
done

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python not found. Please install Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo -e "${RED}Error: Python 3.9+ required. Found Python $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip -q

# Install requirements
echo -e "\n${YELLOW}Installing requirements...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓ Requirements installed${NC}"
else
    echo -e "${YELLOW}⚠ No requirements.txt found (using standard library only)${NC}"
fi

# Install development dependencies
if [ "$DEV_MODE" = true ]; then
    echo -e "\n${YELLOW}Installing development dependencies...${NC}"
    pip install flake8 mypy black isort -q
    echo -e "${GREEN}✓ Development dependencies installed${NC}"
fi

# Set up PYTHONPATH
echo -e "\n${YELLOW}Setting up PYTHONPATH...${NC}"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
echo -e "${GREEN}✓ PYTHONPATH configured${NC}"

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
VERIFY_FAILED=false

verify_import() {
    local module=$1
    local name=$2
    if $PYTHON_CMD -c "from $module import $name" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $name"
    else
        echo -e "  ${RED}✗${NC} $name (import failed)"
        VERIFY_FAILED=true
    fi
}

verify_import "infrastructure.link_budget" "LinkBudgetCalculator"
verify_import "routing.rl_agent" "RLRoutingAgent"
verify_import "routing.bundle" "Bundle"
verify_import "security.qkd" "BB84Protocol"
verify_import "orbital.contact_windows" "calculate_earth_mars_distance"

if [ "$VERIFY_FAILED" = true ]; then
    echo -e "\n${YELLOW}⚠ Some modules failed to import. Check for syntax errors.${NC}"
fi

echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Environment Setup Complete!                             ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "To activate the environment in a new terminal, run:"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo -e ""
echo -e "Quick commands:"
echo -e "  ${BLUE}./scripts/run_tests.sh${NC}     - Run all tests"
echo -e "  ${BLUE}./scripts/run_demos.sh${NC}     - Run interactive demos"
echo -e "  ${BLUE}python src/infrastructure/link_budget.py${NC} - Run link budget demo"
echo ""
