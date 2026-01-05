#!/bin/bash
#
# AETHERIX - Link Budget Demo
# ============================
# Quick script to run the link budget demonstration.
#
# Usage: ./scripts/link_budget_demo.sh
#

set -e

# Get the root directory of the project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set up PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Run the link budget demo
python src/infrastructure/link_budget.py
