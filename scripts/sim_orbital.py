#!/usr/bin/env python3

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from orbital.contact_windows import (
    AU_KM,
    SPEED_OF_LIGHT_KM_S,
    SYNODIC_PERIOD_DAYS,
    calculate_earth_mars_distance,
    calculate_light_time,
    estimate_data_rate,
    get_distance_timeline,
    predict_contact_windows,
)


def main():
    parser = argparse.ArgumentParser(
        description="AETHERIX Orbital Mechanics Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s --start-day 0 --duration 30\n"
               "  %(prog)s --start-day 390 --duration 90 --num-points 90\n"
               "  %(prog)s --start-day 100 --duration 60\n",
    )
    parser.add_argument("--start-day", type=int, default=0, help="Start day of synodic period 0-779 (default: 0)")
    parser.add_argument("--duration", type=int, default=30, help="Duration in days (default: 30)")
    parser.add_argument("--num-points", type=int, default=None, help="Number of timeline sample points (default: duration)")

    args = parser.parse_args()
    num_points = args.num_points or args.duration

    try:
        timeline = get_distance_timeline(num_points=args.start_day + args.duration)
        relevant = [t for t in timeline if args.start_day <= t[0] < args.start_day + args.duration]

        if not relevant:
            print("  No timeline data for the specified range.")
            sys.exit(0)

        distances = [d for _, d, _ in relevant]
        min_dist = min(distances)
        max_dist = max(distances)
        start_dist = relevant[0][1]
        end_dist = relevant[-1][1]

        start_lt = calculate_light_time(start_dist)
        end_lt = calculate_light_time(end_dist)
        min_lt = calculate_light_time(min_dist)
        max_lt = calculate_light_time(max_dist)

        start_rate = estimate_data_rate(start_dist)
        end_rate = estimate_data_rate(end_dist)
        min_rate = estimate_data_rate(min_dist)
        max_rate = estimate_data_rate(max_dist)

        windows = predict_contact_windows(args.start_day, args.duration)
        total_contact_hours = sum(w.duration_hours for w in windows)
        avg_window_rate = sum(w.max_data_rate_mbps for w in windows) / len(windows) if windows else 0

        print()
        print("  ╔══════════════════════════════════════════════════════════════════╗")
        print("  ║           AETHERIX ORBITAL MECHANICS SIMULATION                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ PARAMETERS                                                      ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  Synodic Period:   {SYNODIC_PERIOD_DAYS:.2f} days{' ' * 38}  ║")
        print(f"  ║  1 AU:             {AU_KM / 1e6:.3f} million km{' ' * 30}  ║")
        print(f"  ║  c:                {SPEED_OF_LIGHT_KM_S:.3f} km/s{' ' * 36}  ║")
        print("  ║                                                                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ DISTANCE ANALYSIS (day {start_day} to day {end_day})".format(start_day=args.start_day, end_day=args.start_day + args.duration))
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  Start Distance:   {start_dist / 1e6:>10.2f} M km                         ║")
        print(f"  ║  End Distance:     {end_dist / 1e6:>10.2f} M km                         ║")
        print(f"  ║  Min Distance:     {min_dist / 1e6:>10.2f} M km                         ║")
        print(f"  ║  Max Distance:     {max_dist / 1e6:>10.2f} M km                         ║")
        print("  ║                                                                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ LIGHT-TIME DELAY                                                ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  Start:           {start_lt:>8.1f} s  ({start_lt / 60:>6.1f} min)                ║")
        print(f"  ║  End:             {end_lt:>8.1f} s  ({end_lt / 60:>6.1f} min)                ║")
        print(f"  ║  Minimum:         {min_lt:>8.1f} s  ({min_lt / 60:>6.1f} min)                ║")
        print(f"  ║  Maximum:         {max_lt:>8.1f} s  ({max_lt / 60:>6.1f} min)                ║")
        print("  ║                                                                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ ESTIMATED DATA RATES (Optical, 1550 nm)                         ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  At Start:        {start_rate:>8.1f} Mbps                              ║")
        print(f"  ║  At End:          {end_rate:>8.1f} Mbps                              ║")
        print(f"  ║  Best (min dist): {min_rate:>8.1f} Mbps                              ║")
        print(f"  ║  Worst (max dist):{max_rate:>8.1f} Mbps                              ║")
        print("  ║                                                                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ CONTACT WINDOWS ({duration} days from day {start_day})".format(duration=args.duration, start_day=args.start_day))
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  Total Windows:       {len(windows):<8d}                                  ║")
        print(f"  ║  Total Contact Time:  {total_contact_hours:>8.1f} hours                            ║")
        print(f"  ║  Avg Data Rate:       {avg_window_rate:>8.1f} Mbps                             ║")
        if windows:
            print("  ║                                                                 ║")
            print("  ║  Top Windows:                                                   ║")
            for i, w in enumerate(sorted(windows, key=lambda x: x.max_data_rate_mbps, reverse=True)[:5]):
                print(
                    f"  ║    {i + 1}. {w.duration_hours:>5.1f} hrs  "
                    f"{w.max_data_rate_mbps:>6.1f} Mbps  "
                    f"dist {w.average_distance_km / 1e6:>6.1f}M km       ║"
                )
        print("  ╚══════════════════════════════════════════════════════════════════╝")
        print()

    except Exception as e:
        print(f"\n  ERROR: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
