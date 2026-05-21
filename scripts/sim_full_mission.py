#!/usr/bin/env python3

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from simulation.simulator import SimulationConfig, Simulator


def main():
    parser = argparse.ArgumentParser(
        description="AETHERIX Full Mission Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s --duration 24 --step 60 --rate 10\n"
               "  %(prog)s --duration 720 --step 300 --rate 5 --seed 42 --name mars-baseline\n"
               "  %(prog)s --duration 1 --step 10 --rate 100\n",
    )
    parser.add_argument("--duration", type=float, default=24.0, help="Simulation duration in hours (default: 24)")
    parser.add_argument("--step", type=float, default=60.0, help="Time step in seconds (default: 60)")
    parser.add_argument("--rate", type=float, default=10.0, help="Bundle generation rate per hour (default: 10)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--name", default="earth-mars-baseline", help="Simulation name (default: earth-mars-baseline)")

    args = parser.parse_args()

    try:
        config = SimulationConfig(
            name=args.name,
            duration_hours=args.duration,
            time_step_seconds=args.step,
            seed=args.seed,
            bundle_generation_rate_per_hour=args.rate,
        )

        print()
        print("  ╔══════════════════════════════════════════════════════════════════╗")
        print("  ║           AETHERIX FULL MISSION SIMULATION                      ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ CONFIGURATION                                                   ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  Name:              {config.name:<42s}  ║")
        print(f"  ║  Duration:          {config.duration_hours:>8.1f} hours{' ' * 32}  ║")
        print(f"  ║  Time Step:         {config.time_step_seconds:>8.1f} seconds{' ' * 30}  ║")
        print(f"  ║  Bundle Rate:       {config.bundle_generation_rate_per_hour:>8.1f} /hour{' ' * 32}  ║")
        print(f"  ║  Seed:              {config.seed:<42d}  ║")
        print(f"  ║  Earth-Mars Dist:   {config.earth_mars_distance_km / 1e6:>8.1f} M km{' ' * 30}  ║")
        print("  ║                                                                 ║")
        print("  ║  Running simulation...", end="", flush=True)

        sim = Simulator(config)
        result = sim.run()

        print(" DONE.                                  ║")

        total_steps = int((config.duration_hours * 3600) / config.time_step_seconds)
        print("  ║                                                                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ RESULTS SUMMARY                                                  ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  Total Bundles:     {result.total_bundles:<8d}                                  ║")
        print(f"  ║  Delivered:         {result.delivered_bundles:<8d}                                  ║")
        print(f"  ║  Dropped:           {result.dropped_bundles:<8d}                                  ║")
        print(f"  ║  Stored:            {result.stored_bundles:<8d}                                  ║")
        print(f"  ║  Expired:           {result.expired_bundles:<8d}                                  ║")
        print(f"  ║  Forwarded:         {result.forwarded_bundles:<8d}                                  ║")
        print("  ║                                                                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ PERFORMANCE METRICS                                              ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  Delivery Ratio:    {result.delivery_ratio:>8.1%}                                    ║")
        print(f"  ║  Throughput:        {result.throughput_mb:>10.2f} MB                              ║")
        print(f"  ║  Avg Delay:         {result.average_delay_seconds:>10.1f} seconds{' ' * 28}  ║")
        print(f"  ║  Avg Hops:          {result.average_hops:>10.2f}{' ' * 36}  ║")
        print(f"  ║  Sim Steps:         {total_steps:<8d}                                  ║")
        print("  ║                                                                 ║")

        if result.per_priority_stats:
            print("  ╠══════════════════════════════════════════════════════════════════╣")
            print("  ║ PER-PRIORITY BREAKDOWN                                            ║")
            print("  ╠══════════════════════════════════════════════════════════════════╣")
            print("  ║  Priority          Delivered    Dropped    Avg Delay             ║")
            for prio_name, stats in sorted(result.per_priority_stats.items()):
                avg_d = stats.get("avg_delay", 0.0)
                if avg_d >= 3600:
                    delay_str = f"{avg_d / 3600:.1f} hrs"
                else:
                    delay_str = f"{avg_d:.1f} s"
                print(
                    f"  ║  {prio_name:<18s}  {stats['delivered']:>8d}  "
                    f"{stats['dropped']:>8d}    {delay_str:>10s}          ║"
                )
            print("  ║                                                                 ║")

        print("  ╚══════════════════════════════════════════════════════════════════╝")
        print()

    except Exception as e:
        print(f"\n  ERROR: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
