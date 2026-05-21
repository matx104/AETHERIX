#!/usr/bin/env python3

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from infrastructure.link_budget import LinkBudgetCalculator


def print_budget(budget):
    print()
    print(budget)
    verdict = "POSITIVE (link closed)" if budget.link_margin_db >= 0 else "NEGATIVE (link open)"
    interpretation = (
        "Link has sufficient margin for reliable communication."
        if budget.link_margin_db >= 3
        else (
            "Link margin is tight but usable with adaptive coding."
            if budget.link_margin_db >= 0
            else "Link margin insufficient — reduce data rate or increase power."
        )
    )
    print(f"  Verdict:  {verdict}")
    print(f"  Note:     {interpretation}")
    print()


def print_scenario_comparison():
    calc = LinkBudgetCalculator()
    print()
    print("  ╔══════════════════════════════════════════════════════════════════╗")
    print("  ║          MARS-EARTH SCENARIO COMPARISON (1550 nm Optical)       ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    print("  ║  Scenario       Distance       Margin      Rx Power    Delay    ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    for scenario in ("minimum", "average", "maximum"):
        b = calc.calculate_mars_earth_link(scenario)
        delay_min = calc.calculate_one_way_light_time(b.distance_km) / 60
        print(
            f"  ║  {scenario:<14s} {b.distance_km / 1e6:>6.0f}M km  "
            f"{b.link_margin_db:>+8.2f} dB  {b.received_power_dbm:>+8.2f} dBm  "
            f"{delay_min:>5.1f} min ║"
        )
    print("  ╚══════════════════════════════════════════════════════════════════╝")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="AETHERIX Optical Link Budget Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s --scenario average\n"
               "  %(prog)s --scenario maximum\n"
               "  %(prog)s --distance 225 --tx-power 5 --tx-aperture 0.22 --rx-aperture 1.0 --data-rate 10\n",
    )
    parser.add_argument(
        "--scenario",
        choices=["minimum", "average", "maximum"],
        help="Predefined Mars-Earth distance scenario",
    )
    parser.add_argument("--distance", type=float, help="Custom distance in million km")
    parser.add_argument("--tx-power", type=float, default=5.0, help="Transmitter power in Watts (default: 5)")
    parser.add_argument("--tx-aperture", type=float, default=0.22, help="Transmitter aperture diameter in meters (default: 0.22)")
    parser.add_argument("--rx-aperture", type=float, default=1.0, help="Receiver aperture diameter in meters (default: 1.0)")
    parser.add_argument("--data-rate", type=float, default=10.0, help="Target data rate in Mbps (default: 10)")

    args = parser.parse_args()

    if not args.scenario and args.distance is None:
        args.scenario = "average"

    try:
        calc = LinkBudgetCalculator()

        if args.distance is not None:
            distance_km = args.distance * 1e6
            budget = calc.calculate_optical_link_budget(
                distance_km=distance_km,
                tx_power_watts=args.tx_power,
                tx_aperture_m=args.tx_aperture,
                rx_aperture_m=args.rx_aperture,
                data_rate_mbps=args.data_rate,
            )
            print_budget(budget)
        else:
            budget = calc.calculate_mars_earth_link(args.scenario)
            print_budget(budget)

        print_scenario_comparison()

    except Exception as e:
        print(f"\n  ERROR: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
