#!/usr/bin/env python3
"""
AETHERIX Integrated Presentation Demo
Runs all demos sequentially with professional formatting for exam presentation.

Usage:
    python presentation_demo.py           # Run all demos
    python presentation_demo.py --quick   # Run abbreviated version
"""

import sys
import os
import time
import argparse

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def print_banner(title: str, subtitle: str = ""):
    """Print a formatted section banner."""
    width = 80
    print("\n" + "╔" + "═" * (width-2) + "╗")
    print("║" + title.center(width-2) + "║")
    if subtitle:
        print("║" + subtitle.center(width-2) + "║")
    print("╚" + "═" * (width-2) + "╝")


def print_separator():
    """Print a section separator."""
    print("\n" + "─" * 80)


def pause(message: str = "Press Enter to continue...", skip: bool = False):
    """Pause for presenter interaction."""
    if not skip:
        input(f"\n>>> {message}")


def run_integrated_demo(quick: bool = False):
    """Run the complete integrated demonstration."""

    print_banner(
        "AETHERIX INTEGRATED DEMONSTRATION",
        "Interplanetary Communication Network for Mars Mission Support"
    )

    print("""
    Welcome to the AETHERIX demonstration suite.

    This integrated demo showcases:
    1. Optical Link Budget Calculations
    2. DTN Bundle Protocol Routing
    3. Orbital Mechanics & Contact Windows
    4. Quantum Key Distribution (BB84)
    5. End-to-End Mars Mission Scenario

    Student: Muhammad Abdullah Tariq
    Topic: Building Interplanetary Communication Network
    EduQual Level 6 Diploma in AI Operations
    """)

    pause("Press Enter to begin the demonstration...", quick)

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 1: Link Budget
    # ═══════════════════════════════════════════════════════════════════════════
    print_banner("DEMO 1: OPTICAL LINK BUDGET", "Learning Objective 2d: Link Budget Calculations")

    from demos.link_budget_demo import run_demo as link_budget_demo

    try:
        from importlib import import_module
        demo1 = import_module('01_link_budget_demo.run_demo')
        demo1.run_demo()
    except ImportError:
        # Fallback to direct import
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '01_link_budget_demo'))
        from run_demo import run_demo
        run_demo()

    pause("Demo 1 complete. Continue to DTN Routing?", quick)

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 2: DTN Routing
    # ═══════════════════════════════════════════════════════════════════════════
    print_banner("DEMO 2: DTN ROUTING", "Learning Objective 2a: Bundle Protocol & Store-Forward")

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '02_dtn_routing_demo'))
    from run_demo import run_demo as dtn_demo
    dtn_demo()

    pause("Demo 2 complete. Continue to Orbital Mechanics?", quick)

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 3: Orbital Mechanics
    # ═══════════════════════════════════════════════════════════════════════════
    print_banner("DEMO 3: ORBITAL MECHANICS", "Learning Objective 2d: Orbital Propagation & Windows")

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '03_orbital_mechanics_demo'))
    from run_demo import run_demo as orbital_demo
    orbital_demo()

    pause("Demo 3 complete. Continue to Quantum Key Distribution?", quick)

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 4: Quantum Key Distribution
    # ═══════════════════════════════════════════════════════════════════════════
    print_banner("DEMO 4: QUANTUM KEY DISTRIBUTION", "Learning Objective 2b: QKD Protocols")

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '04_quantum_key_demo'))
    from run_demo import run_demo as qkd_demo
    qkd_demo()

    pause("Demo 4 complete. Continue to Mars Mission Scenario?", quick)

    # ═══════════════════════════════════════════════════════════════════════════
    # DEMO 5: Mars Mission Scenario
    # ═══════════════════════════════════════════════════════════════════════════
    print_banner("DEMO 5: MARS MISSION SCENARIO", "Learning Objective 2f: Mission-Critical Data")

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '05_mars_mission_scenario'))
    from run_demo import run_demo as mission_demo
    mission_demo()

    # ═══════════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════
    print_banner("DEMONSTRATION COMPLETE", "Summary & Key Achievements")

    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                         AETHERIX KEY ACHIEVEMENTS                            ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                              ║
    ║  ▸ 10-100x faster data rates through optical communications                  ║
    ║  ▸ >95% network availability through multi-path redundancy                   ║
    ║  ▸ AI-driven routing replacing static contact schedules                      ║
    ║  ▸ Quantum-secured communications for future-proof security                  ║
    ║  ▸ Full CCSDS/IETF standards compliance                                      ║
    ║  ▸ Scalable architecture supporting Mars settlements                         ║
    ║                                                                              ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║                         LEARNING OBJECTIVES COVERED                          ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                              ║
    ║  ✓ 2a. DTN Protocols - Bundle Protocol, store-and-forward, adaptive routing  ║
    ║  ✓ 2b. Quantum Communication - QKD, BB84, entanglement concepts              ║
    ║  ✓ 2c. Space Infrastructure - 5-tier architecture, satellite constellations  ║
    ║  ✓ 2d. Orbital Mechanics - Link budgets, contact windows, Doppler            ║
    ║  ✓ 2e. Radiation-Hardened Computing - Error correction, fault tolerance      ║
    ║  ✓ 2f. Mission-Critical Prioritization - Traffic scheduling, compression     ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝

    Thank you for attending this demonstration.

    Questions?
    """)


def main():
    parser = argparse.ArgumentParser(description='AETHERIX Integrated Presentation Demo')
    parser.add_argument('--quick', action='store_true', help='Run without pauses')
    args = parser.parse_args()

    try:
        run_integrated_demo(quick=args.quick)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Thank you!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError running demo: {e}")
        print("Try running individual demos from their directories.")
        sys.exit(1)


if __name__ == "__main__":
    main()
