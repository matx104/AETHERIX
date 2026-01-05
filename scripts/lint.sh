#!/bin/bash
#
# AETHERIX - Lint Script
# =======================
# Runs code quality checks on the AETHERIX codebase.
#
# Usage: ./scripts/lint.sh [options]
#
# Options:
#   --fix        Auto-fix issues where possible
#   --check      Check only (no modifications) - default
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
FIX_MODE=false
EXIT_CODE=0

# Parse arguments
show_help() {
    echo "Usage: ./scripts/lint.sh [options]"
    echo ""
    echo "Options:"
    echo "  --fix        Auto-fix issues where possible"
    echo "  --check      Check only (no modifications) - default"
    echo "  --help, -h   Show this help message"
    exit 0
}

for arg in "$@"; do
    case $arg in
        --fix)
            FIX_MODE=true
            shift
            ;;
        --check)
            FIX_MODE=false
            shift
            ;;
        --help|-h)
            show_help
            ;;
    esac
done

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🔍 AETHERIX Code Quality Checks                            ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check for flake8
if python -c "import flake8" 2>/dev/null; then
    echo -e "\n${YELLOW}Running flake8...${NC}"
    if python -m flake8 src/ tests/ --max-line-length=100 --ignore=E501,W503; then
        echo -e "${GREEN}✓ flake8 passed${NC}"
    else
        echo -e "${RED}✗ flake8 found issues${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${YELLOW}⚠ flake8 not installed. Run 'pip install flake8' to enable.${NC}"
fi

# Check for black
if python -c "import black" 2>/dev/null; then
    echo -e "\n${YELLOW}Running black...${NC}"
    if [ "$FIX_MODE" = true ]; then
        if python -m black src/ tests/ --line-length=100; then
            echo -e "${GREEN}✓ black formatting applied${NC}"
        else
            echo -e "${RED}✗ black failed${NC}"
            EXIT_CODE=1
        fi
    else
        if python -m black src/ tests/ --line-length=100 --check --diff; then
            echo -e "${GREEN}✓ black check passed${NC}"
        else
            echo -e "${YELLOW}⚠ black found formatting issues (run with --fix to apply)${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ black not installed. Run 'pip install black' to enable.${NC}"
fi

# Check for isort
if python -c "import isort" 2>/dev/null; then
    echo -e "\n${YELLOW}Running isort...${NC}"
    if [ "$FIX_MODE" = true ]; then
        if python -m isort src/ tests/; then
            echo -e "${GREEN}✓ isort applied${NC}"
        else
            echo -e "${RED}✗ isort failed${NC}"
            EXIT_CODE=1
        fi
    else
        if python -m isort src/ tests/ --check-only --diff; then
            echo -e "${GREEN}✓ isort check passed${NC}"
        else
            echo -e "${YELLOW}⚠ isort found import ordering issues (run with --fix to apply)${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ isort not installed. Run 'pip install isort' to enable.${NC}"
fi

# Check for mypy
if python -c "import mypy" 2>/dev/null; then
    echo -e "\n${YELLOW}Running mypy type checking...${NC}"
    if python -m mypy src/ --ignore-missing-imports --no-error-summary 2>/dev/null; then
        echo -e "${GREEN}✓ mypy passed${NC}"
    else
        echo -e "${YELLOW}⚠ mypy found type issues${NC}"
    fi
else
    echo -e "${YELLOW}⚠ mypy not installed. Run 'pip install mypy' to enable.${NC}"
fi

# Summary
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ Code Quality Checks Passed                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
else
    echo -e "${RED}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    ❌ Code Quality Issues Found                               ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
fi

echo -e "\nTo install linting tools, run:"
echo -e "  ${BLUE}./scripts/init.sh --dev${NC}"
echo ""

exit $EXIT_CODE
