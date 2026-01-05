#!/usr/bin/env python3
"""
AETHERIX Link Budget Demo
Interactive demonstration of optical link budget calculations for Mars-Earth communications.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.infrastructure.link_budget import LinkBudgetCalculator


def run_demo():
    """Run the link budget demonstration."""
    print("\n" + "="*80)
    print("       AETHERIX LINK BUDGET DEMONSTRATION")
    print("       Optical Communications: Mars Orbiter to Earth Ground Station")
    print("="*80)

    calculator = LinkBudgetCalculator()

    # Define scenarios
    scenarios = [
        ("PERIHELION (Closest)", 54_600_000, "100-200 Mbps"),
        ("AVERAGE Distance", 225_000_000, "10-20 Mbps"),
        ("APHELION (Farthest)", 401_000_000, "2-5 Mbps"),
    ]

    print("\n" + "-"*80)
    print("SYSTEM CONFIGURATION")
    print("-"*80)
    print(f"  Transmitter (Mars Orbiter):")
    print(f"    - Laser Power: 5W (36.99 dBm)")
    print(f"    - Wavelength: 1550 nm (Near-IR)")
    print(f"    - Aperture: 22 cm diameter")
    print(f"    - Pointing Loss: -1.0 dB")
    print(f"")
    print(f"  Receiver (Earth Ground Station):")
    print(f"    - Aperture: 1.0 m diameter")
    print(f"    - Detector: APD (Avalanche Photodiode)")
    print(f"    - Atmospheric Loss: -3.0 dB (clear sky)")
    print("-"*80)

    print("\n" + "="*80)
    print("LINK BUDGET ANALYSIS BY DISTANCE")
    print("="*80)

    for name, distance_km, expected_rate in scenarios:
        budget = calculator.calculate_optical_link_budget(
            distance_km=distance_km,
            tx_power_watts=5.0,
            tx_aperture_m=0.22,
            rx_aperture_m=1.0,
            data_rate_mbps=10.0
        )

        light_time = calculator.calculate_one_way_light_time(distance_km)

        print(f"\n{name}")
        print(f"  Distance: {distance_km/1e6:,.1f} million km")
        print(f"  One-way light time: {light_time/60:.1f} minutes")
        print(f"  Free Space Path Loss: {budget.free_space_loss_db:.1f} dB")
        print(f"  EIRP: {budget.eirp_dbm:.1f} dBm")
        print(f"  Received Power: {budget.received_power_dbm:.1f} dBm")
        print(f"  Link Margin: {budget.link_margin_db:+.1f} dB")
        print(f"  Expected Data Rate: {expected_rate}")

        # Status indicator
        if budget.link_margin_db > 3:
            status = "EXCELLENT - Strong link"
        elif budget.link_margin_db > 0:
            status = "GOOD - Adequate margin"
        else:
            status = "MARGINAL - Consider backup"
        print(f"  Status: {status}")

    print("\n" + "="*80)
    print("COMPARISON: AETHERIX vs CURRENT SYSTEMS")
    print("="*80)
    print(f"  {'Metric':<25} {'Current (MRO)':<20} {'AETHERIX':<20}")
    print(f"  {'-'*25} {'-'*20} {'-'*20}")
    print(f"  {'Link Type':<25} {'X-band RF':<20} {'Optical (1550nm)':<20}")
    print(f"  {'Max Data Rate':<25} {'6 Mbps':<20} {'200 Mbps':<20}")
    print(f"  {'Typical Rate':<25} {'2 Mbps':<20} {'10-20 Mbps':<20}")
    print(f"  {'Improvement':<25} {'':<20} {'10-100x':<20}")

    print("\n" + "="*80)
    print("KEY EQUATIONS USED")
    print("="*80)
    print("  Free Space Path Loss: FSPL = 20 * log10(4*pi*d/lambda)")
    print("  Antenna Gain: G = eta * (pi*D/lambda)^2")
    print("  Link Margin: Pr - Sensitivity - Required_SNR")
    print("="*80 + "\n")

    return budget


if __name__ == "__main__":
    run_demo()
