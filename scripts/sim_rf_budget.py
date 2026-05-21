#!/usr/bin/env python3

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from infrastructure.rf_link_budget import (
    KA_BAND_FREQ_HZ,
    MARS_EARTH_DISTANCES_KM,
    RFLinkBudgetCalculator,
    S_BAND_FREQ_HZ,
    UHF_FREQ_HZ,
    X_BAND_FREQ_HZ,
)

BAND_FREQ = {
    "Ka": KA_BAND_FREQ_HZ,
    "X": X_BAND_FREQ_HZ,
    "S": S_BAND_FREQ_HZ,
    "UHF": UHF_FREQ_HZ,
}

DEFAULT_DISTANCE = {"Ka": 225e6, "X": 225e6, "S": 225e6, "UHF": 1000e3}
DEFAULT_POWER = {"Ka": 20.0, "X": 20.0, "S": 10.0, "UHF": 10.0}
DEFAULT_TX_DISH = {"Ka": 3.0, "X": 3.0, "S": 2.0, "UHF": 0.3}
DEFAULT_RX_DISH = {"Ka": 34.0, "X": 34.0, "S": 10.0, "UHF": 5.0}
DEFAULT_RATE = {"Ka": 10e6, "X": 2e6, "S": 1e6, "UHF": 256e3}


def main():
    parser = argparse.ArgumentParser(
        description="AETHERIX RF Link Budget Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s --band Ka --distance 225\n"
               "  %(prog)s --band X --distance 225 --tx-power 20 --tx-dish 3 --rx-dish 34\n"
               "  %(prog)s --band UHF --distance 1000 --tx-power 10 --data-rate 256000\n",
    )
    parser.add_argument("--band", choices=["Ka", "X", "S", "UHF"], default="Ka", help="RF band (default: Ka)")
    parser.add_argument("--distance", type=float, help="Distance in million km (default varies by band)")
    parser.add_argument("--tx-power", type=float, help="Transmitter power in Watts")
    parser.add_argument("--tx-dish", type=float, help="Transmit dish diameter in meters")
    parser.add_argument("--rx-dish", type=float, help="Receive dish diameter in meters")
    parser.add_argument("--data-rate", type=float, help="Data rate in bps")

    args = parser.parse_args()
    band = args.band

    distance_km = (args.distance * 1e6) if args.distance else DEFAULT_DISTANCE[band]
    tx_power = args.tx_power or DEFAULT_POWER[band]
    tx_dish = args.tx_dish or DEFAULT_TX_DISH[band]
    rx_dish = args.rx_dish or DEFAULT_RX_DISH[band]
    data_rate = args.data_rate or DEFAULT_RATE[band]

    try:
        calc = RFLinkBudgetCalculator(BAND_FREQ[band])
        budget = calc.calculate_rf_link_budget(
            distance_km=distance_km,
            tx_power_watts=tx_power,
            tx_antenna_diameter_m=tx_dish,
            rx_antenna_diameter_m=rx_dish,
            data_rate_bps=data_rate,
        )
        print(budget)

        verdict = "CLOSED (positive margin)" if budget.link_margin_db >= 0 else "OPEN (negative margin)"
        print(f"  Verdict: {verdict}")
        print(f"  Band: {band} | Freq: {budget.frequency_hz / 1e9:.1f} GHz" if budget.frequency_hz >= 1e9 else f"  Band: {band} | Freq: {budget.frequency_hz / 1e6:.1f} MHz")
        print()

    except Exception as e:
        print(f"\n  ERROR: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
