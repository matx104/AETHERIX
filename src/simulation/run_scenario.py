#!/usr/bin/env python3
"""
AETHERIX Scenario Runner
========================

Runs a DTN simulation from a YAML configuration file.

    python src/simulation/run_scenario.py --config config/earth-mars-baseline.yaml
    python src/simulation/run_scenario.py --config config/solar_conjunction.yaml
    python src/simulation/run_scenario.py --list-scenarios

The scenario YAML specifies simulation duration, bundle generation rate,
seed, link parameters, and output options.  This script maps those keys to
:class:`~simulation.simulator.SimulationConfig` and prints a results summary.

Zero external dependencies — a minimal YAML parser handles the subset of
YAML used in ``config/*.yaml``.  If PyYAML is available it is preferred.
"""

from __future__ import annotations

import argparse
import os
import pprint
import sys
from typing import Any, Dict, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..")
_ROOT = os.path.join(_SRC, "..")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from simulation.simulator import SimulationConfig, SimulationResult, Simulator


# ---------------------------------------------------------------------------
# Minimal YAML parser (stdlib only)
# ---------------------------------------------------------------------------

def _try_import_yaml():
    try:
        import yaml  # type: ignore
        return yaml.safe_load, True
    except ImportError:
        return None, False


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.lower() in ("true", "yes"):
        return True
    if value.lower() in ("false", "no"):
        return False
    if value.lower() in ("null", "~", "none"):
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def _parse_yaml(text: str) -> Dict[str, Any]:
    yaml_safe_load, has_yaml = _try_import_yaml()
    if has_yaml:
        result = yaml_safe_load(text)
        return result if isinstance(result, dict) else {}

    result: Dict[str, Any] = {}
    stack: list[tuple[int, dict]] = [(0, result)]

    for line in text.splitlines():
        stripped = line.split("#")[0].rstrip()
        if not stripped.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key_value = stripped.strip()

        while stack and stack[-1][0] > indent:
            stack.pop()

        if ":" in key_value:
            key, _, val = key_value.partition(":")
            key = key.strip()
            val = val.strip()
            if val:
                stack[-1][1][key] = _parse_scalar(val)
            else:
                new_dict: Dict[str, Any] = {}
                stack[-1][1][key] = new_dict
                stack.append((indent + 2, new_dict))
        elif key_value.startswith("- "):
            item_val = key_value[2:].strip()
            parent_key = None
            for k, v in stack[-1][1].items():
                if isinstance(v, list):
                    parent_key = k
                    break
            if parent_key is None:
                pass
            else:
                stack[-1][1][parent_key].append(_parse_scalar(item_val))

    return result


def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r") as f:
        text = f.read()
    return _parse_yaml(text)


# ---------------------------------------------------------------------------
# Scenario execution
# ---------------------------------------------------------------------------

def build_sim_config(cfg: Dict[str, Any]) -> SimulationConfig:
    sim = cfg.get("simulation", {})
    scenario = cfg.get("scenario", {})
    return SimulationConfig(
        name=scenario.get("name", sim.get("name", "custom-scenario")),
        duration_hours=float(sim.get("duration_hours", 720.0)),
        time_step_seconds=float(sim.get("time_step_seconds", 60.0)),
        seed=int(sim.get("seed", 42)),
        earth_mars_distance_km=float(
            scenario.get("earth_mars_distance_km", sim.get("earth_mars_distance_km", 225e6))
        ),
        bundle_generation_rate_per_hour=float(
            sim.get("bundle_generation_rate_per_hour", 10.0)
        ),
    )


def run_scenario(config_path: str, verbose: bool = True) -> SimulationResult:
    cfg = load_config(config_path)

    if verbose:
        print(f"  Scenario: {cfg.get('scenario', {}).get('name', 'unknown')}")
        print(f"  Config:   {config_path}")

    sim_config = build_sim_config(cfg)
    sim = Simulator(sim_config)
    result = sim.run()

    if verbose:
        _print_summary(result)

    return result


def _print_summary(result: SimulationResult) -> None:
    print(f"\n{'=' * 60}")
    print(f"  SCENARIO: {result.config.name}")
    print(f"{'=' * 60}")
    print(f"  Duration:             {result.config.duration_hours:.0f} hours")
    print(f"  Seed:                 {result.config.seed}")
    print(f"  Time step:            {result.config.time_step_seconds:.0f} s")
    print(f"  Bundle rate:          {result.config.bundle_generation_rate_per_hour:.1f}/hr")
    print(f"{'─' * 60}")
    print(f"  Bundles generated:    {result.total_bundles}")
    print(f"  Bundles delivered:    {result.delivered_bundles}")
    print(f"  Bundles dropped:      {result.dropped_bundles}")
    print(f"  Bundles expired:      {result.expired_bundles}")
    print(f"  Bundles stored:       {result.stored_bundles}")
    print(f"{'─' * 60}")
    print(f"  Delivery ratio:       {result.delivery_ratio:.1%}")
    print(f"  Average delay:        {result.average_delay_seconds:.1f} s")
    print(f"  Average hops:         {result.average_hops:.1f}")
    print(f"  Throughput:           {result.throughput_mb:.1f} MB")
    print(f"  Total events:         {len(result.events)}")

    if result.per_priority_stats:
        print(f"{'─' * 60}")
        print(f"  Per-priority breakdown:")
        for prio, stats in sorted(result.per_priority_stats.items()):
            print(
                f"    {prio:<20s}  "
                f"delivered={stats['delivered']:>5d}  "
                f"dropped={stats['dropped']:>5d}"
            )
    print(f"{'=' * 60}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_CONFIG_DIR = os.path.join(_ROOT, "config")


def list_scenarios() -> None:
    print("Available scenarios:\n")
    if not os.path.isdir(_CONFIG_DIR):
        print(f"  (no config directory at {_CONFIG_DIR})")
        return
    for fname in sorted(os.listdir(_CONFIG_DIR)):
        if fname.endswith(".yaml") or fname.endswith(".yml"):
            fpath = os.path.join(_CONFIG_DIR, fname)
            try:
                cfg = load_config(fpath)
                name = cfg.get("scenario", {}).get("name", "?")
                desc = cfg.get("scenario", {}).get("description", "")
                print(f"  {fname:<40s}  {desc}")
            except Exception:
                print(f"  {fname:<40s}  (parse error)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an AETHERIX DTN simulation scenario from a YAML config file."
    )
    parser.add_argument(
        "--config", "-c",
        default=os.path.join(_CONFIG_DIR, "earth-mars-baseline.yaml"),
        help="Path to scenario YAML file (default: config/earth-mars-baseline.yaml)",
    )
    parser.add_argument(
        "--list-scenarios", "-l",
        action="store_true",
        help="List available scenario files and exit",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress detailed output",
    )
    args = parser.parse_args()

    if args.list_scenarios:
        list_scenarios()
        return

    if not os.path.isfile(args.config):
        print(f"Error: config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    run_scenario(args.config, verbose=not args.quiet)


if __name__ == "__main__":
    main()
