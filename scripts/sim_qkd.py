#!/usr/bin/env python3

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from security.qkd import BB84Protocol, E91Protocol, calculate_key_rate


def print_result(result, protocol_name, eavesdrop):
    print()
    print("  ╔══════════════════════════════════════════════════════════════════╗")
    print(f"  ║         AETHERIX QKD SIMULATION — {protocol_name:^22s}        ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    print("  ║ PROTOCOL EXECUTION                                              ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    print(f"  ║  Protocol:          {protocol_name:<42s}  ║")
    print(f"  ║  Raw Qubits/Pairs:  {result.raw_key_length:<42d}  ║")
    print(f"  ║  Sifted Key Length: {result.sifted_key_length:<42d}  ║")
    print(f"  ║  Efficiency:        {result.efficiency:>6.1%}{' ' * 40}  ║")
    print("  ║                                                                 ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    print("  ║ SECURITY ANALYSIS                                               ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    qber_bar_len = int(min(result.qber / 0.25, 1.0) * 20)
    qber_bar = "█" * qber_bar_len + "░" * (20 - qber_bar_len)
    print(f"  ║  QBER:              {result.qber:>6.2%}  [{qber_bar}]  Threshold: 11%  ║")
    print(f"  ║  Secure:            {'YES' if result.secure else 'NO — EAVESDROPPER DETECTED':<30s}    ║")
    if eavesdrop:
        print("  ║  Eavesdropper:      SIMULATED (added channel error)            ║")
    print("  ║                                                                 ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    print("  ║ KEY RATE ESTIMATES AT VARIOUS DISTANCES                         ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    distances = [
        (500, "LEO"),
        (36000, "GEO"),
        (400000, "Lunar"),
        (55e6, "Mars (min)"),
        (225e6, "Mars (avg)"),
    ]
    for dist_km, label in distances:
        rate = calculate_key_rate(dist_km, protocol_name)
        if rate >= 1000:
            rate_str = f"{rate:.0f} bps"
        elif rate >= 1:
            rate_str = f"{rate:.1f} bps"
        else:
            rate_str = f"{rate:.2f} bps"
        if dist_km >= 1e6:
            dist_str = f"{dist_km / 1e6:.0f}M km"
        else:
            dist_str = f"{dist_km:.0f} km"
        print(f"  ║  {label:<12s} {dist_str:>12s}  ->  {rate_str:>12s}              ║")
    print("  ╚══════════════════════════════════════════════════════════════════╝")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="AETHERIX Quantum Key Distribution Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s --protocol bb84 --qubits 1000\n"
               "  %(prog)s --protocol e91 --qubits 2000 --channel-error 5\n"
               "  %(prog)s --protocol bb84 --qubits 500 --eavesdrop\n",
    )
    parser.add_argument("--protocol", choices=["bb84", "e91"], default="bb84", help="QKD protocol (default: bb84)")
    parser.add_argument("--qubits", type=int, default=1000, help="Number of qubits/pairs (default: 1000)")
    parser.add_argument("--channel-error", type=float, default=0.0, help="Channel error rate in percent 0-50 (default: 0)")
    parser.add_argument("--eavesdrop", action="store_true", help="Simulate eavesdropper (adds ~25%% channel error)")

    args = parser.parse_args()

    channel_error = args.channel_error / 100.0
    if args.eavesdrop:
        channel_error = max(channel_error, 0.25)

    try:
        if args.protocol == "bb84":
            protocol = BB84Protocol(num_qubits=args.qubits, channel_error=channel_error)
            result = protocol.execute()
            print_result(result, "BB84", args.eavesdrop)
        else:
            protocol = E91Protocol(num_pairs=args.qubits, channel_error=channel_error)
            result = protocol.execute()
            print_result(result, "E91", args.eavesdrop)

    except Exception as e:
        print(f"\n  ERROR: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
