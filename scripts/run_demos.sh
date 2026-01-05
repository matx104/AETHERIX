#!/bin/bash
#
# AETHERIX - Demo Runner
# =======================
# Runs interactive demonstrations for the AETHERIX project.
#
# Usage: ./scripts/run_demos.sh [demo_number]
#
# Available demos:
#   1   Link Budget Demo
#   2   DTN Routing Demo
#   3   Orbital Mechanics Demo
#   4   Quantum Key Distribution Demo
#   5   Mars Mission Scenario
#   6   Integrated Presentation Demo
#   all Run all demos sequentially
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the root directory of the project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

show_menu() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🎮 AETHERIX Demo Suite                                     ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Available demos:"
    echo ""
    echo -e "  ${CYAN}1${NC}  📊 Link Budget Demo        - Optical link budget calculations"
    echo -e "  ${CYAN}2${NC}  🛰️  DTN Routing Demo       - Bundle Protocol v7 & RL routing"
    echo -e "  ${CYAN}3${NC}  🌍 Orbital Mechanics Demo  - Contact windows & orbital dynamics"
    echo -e "  ${CYAN}4${NC}  🔐 QKD Demo               - Quantum key distribution (BB84/E91)"
    echo -e "  ${CYAN}5${NC}  🔴 Mars Mission Scenario   - End-to-end Mars communication"
    echo -e "  ${CYAN}6${NC}  🚀 Integrated Demo         - Full presentation demonstration"
    echo ""
    echo -e "  ${CYAN}all${NC} Run all demos sequentially"
    echo -e "  ${CYAN}q${NC}   Quit"
    echo ""
}

run_demo() {
    local demo_num=$1
    local demo_path=""
    local demo_name=""

    case $demo_num in
        1)
            demo_path="demos/01_link_budget_demo/run_demo.py"
            demo_name="Link Budget Demo"
            ;;
        2)
            demo_path="demos/02_dtn_routing_demo/run_demo.py"
            demo_name="DTN Routing Demo"
            ;;
        3)
            demo_path="demos/03_orbital_mechanics_demo/run_demo.py"
            demo_name="Orbital Mechanics Demo"
            ;;
        4)
            demo_path="demos/04_quantum_key_demo/run_demo.py"
            demo_name="QKD Demo"
            ;;
        5)
            demo_path="demos/05_mars_mission_scenario/run_demo.py"
            demo_name="Mars Mission Scenario"
            ;;
        6)
            demo_path="demos/06_integrated_demo/presentation_demo.py"
            demo_name="Integrated Demo"
            ;;
        *)
            echo -e "${RED}Invalid demo number: $demo_num${NC}"
            return 1
            ;;
    esac

    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Running: $demo_name${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

    if [ -f "$PROJECT_ROOT/$demo_path" ]; then
        python "$PROJECT_ROOT/$demo_path"
    else
        echo -e "${RED}Demo not found: $demo_path${NC}"
        return 1
    fi
}

run_all_demos() {
    echo -e "${YELLOW}Running all demos...${NC}\n"
    for i in {1..6}; do
        run_demo $i
        if [ $i -lt 6 ]; then
            echo -e "\n${BLUE}Press Enter to continue to next demo...${NC}"
            read -r
        fi
    done
}

# Change to project root
cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set up PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# If argument provided, run that demo
if [ -n "$1" ]; then
    case $1 in
        all)
            run_all_demos
            ;;
        [1-6])
            run_demo $1
            ;;
        -h|--help)
            show_menu
            ;;
        *)
            echo -e "${RED}Invalid argument: $1${NC}"
            show_menu
            exit 1
            ;;
    esac
else
    # Interactive mode
    while true; do
        show_menu
        echo -n "Select demo (1-6, all, q): "
        read -r choice
        
        case $choice in
            q|Q)
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            all)
                run_all_demos
                ;;
            [1-6])
                run_demo $choice
                echo -e "\n${BLUE}Press Enter to return to menu...${NC}"
                read -r
                ;;
            *)
                echo -e "${RED}Invalid choice. Please try again.${NC}"
                sleep 1
                ;;
        esac
    done
fi
