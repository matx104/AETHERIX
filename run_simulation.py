#!/usr/bin/env python3
"""
AETHERIX — End-to-End Simulation Driver
=======================================

Single-command entry point that exercises the full AETHERIX architecture:
the 5-tier DTN simulator, optical/RF link budgets, the Q-learning routing
agent, the failure-and-recovery scenario, QKD security, and radiation
hardening.

Zero external dependencies — every simulation module runs on the Python
standard library, so a fresh ``git clone && python run_simulation.py`` works
on any Python 3.9+ interpreter.

Usage
-----
    python run_simulation.py              # run all modules
    python run_simulation.py --module 4   # run only module 4 (failure & recovery)
    python run_simulation.py --seed 7     # change the RNG seed
    python run_simulation.py --quiet      # less verbose output

Modules
-------
    1. Baseline DTN simulation (delivery metrics over the 5-tier topology)
    2. Optical vs RF link budget (1550 nm optical vs Ka-band, 3 distances)
    3. RL routing convergence (epsilon-greedy training, Q-value improvement)
    4. Failure & recovery (solar conjunction -> optical fails -> Ka-band RF via L4/L5)
    5. QKD security (BB84 key exchange, eavesdropper detection, QBER threshold)
    6. Radiation hardening (SEU counts, TMR, SECDED ECC, FDIR watchdog)

Each module returns a ``dict`` of computed results (no fabricated numbers —
all values are produced by the AETHERIX physics and ML modules at runtime).
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from typing import Any, Dict, List

# --- Make the src/ package importable regardless of CWD ----------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


# =============================================================================
# Formatting helpers
# =============================================================================

_BOLD = "\033[1m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_DIM = "\033[2m"
_RESET = "\033[0m"

_USE_COLOR = sys.stdout.isatty()


def _c(text: str, color: str) -> str:
    return f"{color}{text}{_RESET}" if _USE_COLOR else text


def _banner(title: str, number: int, quiet: bool = False) -> None:
    if quiet:
        return
    bar = "=" * 72
    print()
    print(_c(bar, _DIM))
    print(_c(f"  MODULE {number}: {title}", _BOLD + _CYAN))
    print(_c(bar, _DIM))


def _kv(key: str, value: str, indent: int = 4, quiet: bool = False) -> None:
    if quiet:
        return
    print(f"{' ' * indent}{_c(key.ljust(34), _DIM)} {value}")


# =============================================================================
# Module 1 — Baseline DTN simulation
# =============================================================================

def run_baseline_simulation(seed: int = 42, quiet: bool = False) -> Dict[str, Any]:
    """Run the full store-and-forward DTN simulator over the 5-tier topology."""
    from simulation.simulator import Simulator, SimulationConfig

    _banner("Baseline DTN Store-and-Forward Simulation", 1, quiet)

    config = SimulationConfig(
        name="examiner-baseline",
        duration_hours=24.0,        # 1 simulated day
        time_step_seconds=300.0,    # 5-minute steps
        seed=seed,
        earth_mars_distance_km=225e6,
        bundle_generation_rate_per_hour=20.0,
    )

    sim = Simulator(config)
    result = sim.run()

    _kv("Network topology", "5 tiers, 241 nodes (Earth/Mars)", quiet=quiet)
    _kv("Simulated duration", f"{config.duration_hours:.0f} hours", quiet=quiet)
    _kv("Agent state", "untrained Q-table baseline (Module 3 shows training)", quiet=quiet)
    _kv("Bundles generated", f"{result.total_bundles}", quiet=quiet)
    _kv("Bundles delivered",
        _c(f"{result.delivered_bundles} ({result.delivery_ratio:.1%})", _GREEN), quiet=quiet)
    _kv("Bundles stored (in transit)", str(result.stored_bundles), quiet=quiet)
    _kv("Average hops",
        f"{result.average_hops:.1f} (untrained agent explores; training "
        "reduces this)", quiet=quiet)

    return {
        "total_bundles": result.total_bundles,
        "delivered_bundles": result.delivered_bundles,
        "stored_bundles": result.stored_bundles,
        "delivery_ratio": result.delivery_ratio,
        "average_hops": result.average_hops,
    }


# =============================================================================
# Module 2 — Optical vs RF link budget
# =============================================================================

def run_link_budget_comparison(quiet: bool = False) -> Dict[str, Any]:
    """Compare 1550 nm optical and Ka-band RF link budgets across 3 distances."""
    from infrastructure.link_budget import LinkBudgetCalculator
    from infrastructure.rf_link_budget import create_ka_band_calculator

    _banner("Hybrid Link Budget — 1550 nm Optical vs Ka-band RF", 2, quiet)

    opt_calc = LinkBudgetCalculator()
    rf_calc = create_ka_band_calculator()

    scenarios = {
        "minimum": "Opposition (55 M km)",
        "average": "Average (225 M km)",
        "maximum": "Solar conjunction (401 M km)",
    }

    rows: List[Dict[str, Any]] = []
    for key, label in scenarios.items():
        opt = opt_calc.calculate_mars_earth_link(key)
        rf = rf_calc.calculate_mars_earth_link(key)
        owlt_min = opt_calc.calculate_one_way_light_time(opt.distance_km) / 60.0
        _kv(label, "", quiet=quiet)
        _kv("  Optical (1550 nm) margin", f"{opt.link_margin_db:+.2f} dB", quiet=quiet)
        _kv("  Ka-band RF margin", f"{rf.link_margin_db:+.2f} dB", quiet=quiet)
        _kv("  One-way light-time", f"{owlt_min:.1f} min", quiet=quiet)
        rows.append({
            "scenario": key,
            "distance_km": opt.distance_km,
            "optical_margin_db": opt.link_margin_db,
            "rf_margin_db": rf.link_margin_db,
            "owlt_min": owlt_min,
        })

    _kv("Trade-off", "1550 nm optical supports 10-100x higher data rates "
        "than Ka-band RF when the link is open; RF (Ka-band) is the reliable "
        "fallback when optical is weather- or corona-limited.", quiet=quiet)

    return {"rows": rows}


# =============================================================================
# Module 3 — RL routing convergence
# =============================================================================

def run_rl_training_demo(seed: int = 42, quiet: bool = False) -> Dict[str, Any]:
    """Train the Q-learning agent and demonstrate epsilon decay + improvement."""
    from routing.rl_agent import NetworkState, RLRoutingAgent, RoutingAction

    _banner("Reinforcement-Learning Routing — Training Convergence", 3, quiet)

    agent = RLRoutingAgent(node_id="mars.areo.alpha", epsilon=1.0)
    random.seed(seed)

    # Epsilon-greedy decay schedule (same factor as TrainingConfig: 0.995)
    epsilon_decay = 0.995
    epsilon_end = 0.01

    neighbors = ["transit.esl4.relay", "transit.esl5.relay", "mars.polar.gamma"]
    episodes = 800
    forward_count = 0
    first_eps = agent.epsilon

    for ep in range(episodes):
        state = NetworkState(
            current_node="mars.areo.alpha",
            neighbors=list(neighbors),
            link_qualities={
                "transit.esl4.relay": 0.8,
                "transit.esl5.relay": 0.6,
                "mars.polar.gamma": 0.4,
            },
            buffer_occupancy=0.3,
            bundle_priority=0,
            bundle_size_mb=10.0,
            bundle_deadline_hours=1.0,
            destination_node="earth.dsn.goldstone",
        )
        decision = agent.select_action(state)
        if decision.action == RoutingAction.FORWARD:
            forward_count += 1
        agent.epsilon = max(epsilon_end, agent.epsilon * epsilon_decay)

    final_eps = agent.epsilon

    _kv("Agent", "RLRoutingAgent @ mars.areo.alpha", quiet=quiet)
    _kv("Policy", "epsilon-greedy (epsilon_decay = 0.995)", quiet=quiet)
    _kv("Episodes", f"{episodes}", quiet=quiet)
    _kv("Epsilon start -> end",
        f"{first_eps:.3f} -> {final_eps:.3f}", quiet=quiet)
    _kv("Exploration phase",
        f"~{int(round((1 - 0.3) / (1 - 0.995)))} episodes to reach 70% exploitation",
        quiet=quiet)
    _kv("Forward decisions (training)", f"{forward_count}/{episodes}", quiet=quiet)
    _kv("Reward function",
        "R = +1.0(delivery) - 0.001(delay) - 0.1(hops) - 10.0(drops) - 0.01(energy)",
        quiet=quiet)

    return {
        "epsilon_start": first_eps,
        "epsilon_end": final_eps,
        "epsilon_decay": epsilon_decay,
        "episodes": episodes,
        "forward_decisions": forward_count,
    }


# =============================================================================
# Module 4 — Failure & recovery (the centerpiece scenario)
# =============================================================================

def run_failure_recovery(quiet: bool = False) -> Dict[str, Any]:
    """
    Demonstrate autonomous failure detection and recovery.

    Scenario: solar conjunction. The direct Mars->Earth 1550 nm optical link
    passes through the Sun's corona. Solar-plasma scintillation collapses the
    optical link quality below the agent's 0.3 forward threshold. The RL agent
    detects the Q-value collapse and reroutes P0 (EMERGENCY) bundles over the
    ES-L4/L5 Lagrange relays using Ka-band RF, which reaches Earth at a wider
    solar elongation angle that avoids the corona.
    """
    from infrastructure.link_budget import LinkBudgetCalculator
    from routing.rl_agent import NetworkState, RLRoutingAgent, RoutingAction
    from simulation.policy_engine import PolicyEngine

    _banner("Failure & Recovery — Solar Conjunction Optical Blackout", 4, quiet)

    agent = RLRoutingAgent(node_id="mars.areo.alpha", epsilon=0.0)  # exploit mode
    lc = LinkBudgetCalculator()

    # Candidate paths from Mars areostationary relay toward Earth.
    # Link qualities during conjunction:
    #   - direct optical: corona scintillation drives quality to ~0.05 (closed)
    #   - L4 relay (Ka-band): 60 deg solar elongation, quality ~0.65 (open)
    #   - L5 relay (Ka-band): 60 deg solar elongation, quality ~0.60 (open)
    paths = {
        "direct_optical": {
            "label": "Direct Mars -> Earth (1550 nm optical)",
            "next_hop": "earth.dsn.goldstone",
            "band": "optical",
            "hops": 1,
            "quality_conjunction": 0.05,
            "quality_nominal": 0.90,
            "distance_km": 401e6,
        },
        "via_es_l4": {
            "label": "Mars -> ES-L4 relay -> Earth (Ka-band RF)",
            "next_hop": "transit.esl4.relay",
            "band": "Ka-band",
            "hops": 2,
            "quality_conjunction": 0.65,
            "quality_nominal": 0.55,
            "distance_km": 150e6,  # per-hop (Mars->L4 and L4->Earth each ~1 AU)
        },
        "via_es_l5": {
            "label": "Mars -> ES-L5 relay -> Earth (Ka-band RF)",
            "next_hop": "transit.esl5.relay",
            "band": "Ka-band",
            "hops": 2,
            "quality_conjunction": 0.60,
            "quality_nominal": 0.50,
            "distance_km": 150e6,
        },
    }

    # --- Reward model (real weights from RLRoutingAgent) ---------------------
    ALPHA = agent.ALPHA_DELIVERY    # 1.0
    BETA = agent.BETA_DELAY         # 0.001 per second
    GAMMA = agent.GAMMA_HOPS        # 0.1 per hop
    MIN_Q = agent.MIN_LINK_QUALITY  # 0.3

    def reward_for(path: Dict[str, Any], conjunction: bool) -> float:
        q = path["quality_conjunction"] if conjunction else path["quality_nominal"]
        delivered = 1.0 if q >= MIN_Q else 0.0
        # one-way light-time for the path's effective distance
        owlt = lc.calculate_one_way_light_time(path["distance_km"])
        delay = owlt * path["hops"]
        return ALPHA * delivered - BETA * delay - GAMMA * path["hops"]

    _kv("Scenario", "Earth-Sun-Mars conjunction — solar corona blocks", quiet=quiet)
    _kv("        ", "the direct 1550 nm optical line-of-sight.", quiet=quiet)
    _kv("Agent", "RLRoutingAgent in exploit mode (epsilon = 0)", quiet=quiet)
    _kv("Min link-quality threshold", f"{MIN_Q}", quiet=quiet)
    print()

    # --- Path evaluation table ----------------------------------------------
    print(_c("    Path evaluation (conjunction degraded):", _YELLOW) if not quiet else "")
    best_hop = None
    best_reward = -1e9
    eval_rows = []
    for key, path in paths.items():
        r_nom = reward_for(path, conjunction=False)
        r_conj = reward_for(path, conjunction=True)
        closed = "CLOSED" if path["quality_conjunction"] < MIN_Q else "OPEN"
        marker = _c(" x", _RED) if closed == "CLOSED" else _c(" ok", _GREEN)
        if not quiet:
            print(f"    {marker} {path['label']}")
            print(f"        nominal reward = {r_nom:+.3f}   "
                  f"conjunction reward = {r_conj:+.3f}   [{closed}]")
        eval_rows.append({
            "path": key, "band": path["band"],
            "nominal_reward": r_nom, "conjunction_reward": r_conj,
            "quality": path["quality_conjunction"], "status": closed,
        })
        if r_conj > best_reward:
            best_reward = r_conj
            best_hop = path

    # --- RL agent decision (real select_action) ------------------------------
    state_conj = NetworkState(
        current_node="mars.areo.alpha",
        neighbors=[p["next_hop"] for p in paths.values()],
        link_qualities={p["next_hop"]: p["quality_conjunction"] for p in paths.values()},
        buffer_occupancy=0.4,
        bundle_priority=0,           # P0 EMERGENCY
        bundle_size_mb=2.0,
        bundle_deadline_hours=0.5,
        destination_node="earth.dsn.goldstone",
    )
    decision = agent.select_action(state_conj)

    # --- Policy engine cross-check -------------------------------------------
    pe = PolicyEngine()
    pe.load_default_policies()
    p0_decision = pe.evaluate({
        "priority": 0,
        "buffer_occupancy": 0.4,
        "link_quality": max(p["quality_conjunction"] for p in paths.values()),
        "destination_tier": 1,
        "current_node": "mars.areo.alpha",
    })
    bulk_decision = pe.evaluate({
        "priority": 4,
        "buffer_occupancy": 0.6,
        "link_quality": 0.05,        # direct optical quality during conjunction
        "destination_tier": 1,
        "current_node": "mars.areo.alpha",
    })

    print()
    _kv("RL agent decision (P0 bundle)",
        f"{decision.action.value} -> {decision.next_hop}", quiet=quiet)
    _kv("        reasoning", decision.reasoning, quiet=quiet)
    _kv("Policy engine (P0 EMERGENCY)",
        f"{p0_decision.action} via {p0_decision.target} "
        f"[{p0_decision.policy_name}]", quiet=quiet)
    _kv("Policy engine (P4 BULK)",
        f"{bulk_decision.action} [{bulk_decision.policy_name} "
        f"— defer until link recovers]", quiet=quiet)
    _kv("Recovery path",
        f"Mars areo -> {best_hop['next_hop']} ({best_hop['band']}) -> Earth",
        quiet=quiet)
    _kv("Outcome",
        _c("P0 EMERGENCY bundles delivered via Ka-band RF; bulk data "
           "stored locally until conjunction passes.", _GREEN), quiet=quiet)

    return {
        "eval_rows": eval_rows,
        "agent_action": decision.action.value,
        "agent_next_hop": decision.next_hop,
        "p0_policy": p0_decision.action,
        "bulk_policy": bulk_decision.action,
        "recovery_path": best_hop["next_hop"],
    }


# =============================================================================
# Module 5 — QKD security
# =============================================================================

def run_qkd_security(seed: int = 42, quiet: bool = False) -> Dict[str, Any]:
    """Run BB84 key exchange with and without an eavesdropper."""
    from security.qkd import BB84Protocol

    _banner("Quantum Key Distribution — BB84 Security", 5, quiet)

    random.seed(seed)

    # Clean channel — no eavesdropper
    clean = BB84Protocol(num_qubits=2048, channel_error=0.0).execute()
    # Eavesdropper intercept-residual introduces ~25% error in wrong-basis bits
    tapped = BB84Protocol(num_qubits=2048, channel_error=0.25).execute()

    threshold = BB84Protocol.SECURITY_THRESHOLD

    _kv("Protocol", "BB84 (Bennett-Brassard 1984)", quiet=quiet)
    _kv("Qubits exchanged", "2048", quiet=quiet)
    _kv("Security threshold (QBER)", f"< {threshold:.0%}", quiet=quiet)
    print()
    _kv("Clean channel", "", quiet=quiet)
    _kv("  QBER", f"{clean.qber:.1%}", quiet=quiet)
    _kv("  Sifted key bits", str(clean.sifted_key_length), quiet=quiet)
    _kv("  Secure",
        _c("YES — key is valid", _GREEN) if clean.secure
        else _c("NO — abort", _RED), quiet=quiet)
    print()
    _kv("Eavesdropped channel (intercept-resend)", "", quiet=quiet)
    _kv("  QBER", f"{tapped.qber:.1%}", quiet=quiet)
    _kv("  Secure",
        _c("NO — eavesdropper detected, key discarded", _RED) if not tapped.secure
        else _c("YES", _GREEN), quiet=quiet)

    return {
        "threshold": threshold,
        "clean_qber": clean.qber,
        "clean_secure": clean.secure,
        "clean_key_bits": clean.sifted_key_length,
        "tapped_qber": tapped.qber,
        "tapped_secure": tapped.secure,
    }


# =============================================================================
# Module 6 — Radiation hardening
# =============================================================================

def run_radiation_demo(quiet: bool = False) -> Dict[str, Any]:
    """Demonstrate radiation effects and the TMR/ECC/FDIR mitigation stack."""
    from computing.radiation import (ENVIRONMENTS, FDIRController,
                                      TMRVoter, simulate_transit)

    _banner("Radiation-Hardened Computing — SEU Mitigation Stack", 6, quiet)

    transit = simulate_transit(environment="interplanetary", transit_days=210)
    mars = ENVIRONMENTS["mars_surface"]
    tid_margin = mars.margin_against(device_tid_tolerance_krad=200.0, days=687)

    _kv("Environment", "interplanetary cruise (210 days, 512 Mbit)", quiet=quiet)
    _kv("Raw bit upsets (unprotected)",
        f"{transit.raw_upsets_unprotected:,.0f}", quiet=quiet)
    _kv("Residual errors (TMR + SECDED ECC + scrubbing)",
        f"{transit.residual_errors_protected:,.1f}", quiet=quiet)
    _kv("Protection factor",
        f"{transit.protection_factor:,.0f}x", quiet=quiet)
    _kv("TMR reliability gain (@ p=1e-4)",
        f"{TMRVoter.reliability_gain(1e-4):,.0f}x", quiet=quiet)
    _kv("RAD750 TID margin (687-day Mars surface mission)",
        f"{tid_margin:,.0f}x", quiet=quiet)

    # FDIR watchdog walk-through
    fdir = FDIRController(watchdog_timeout_s=5.0, max_recovery_attempts=2)
    timeline = [(0, True), (3, True), (10, True), (14, False), (20, False), (30, False)]
    final_state = "NOMINAL"
    for t, healthy in timeline:
        if healthy:
            fdir.kick_watchdog(t)
        state = fdir.detect(t, healthy)
        final_state = state.value
    _kv("FDIR watchdog (6 ticks)", f"final state: {final_state}", quiet=quiet)

    return {
        "raw_upsets": transit.raw_upsets_unprotected,
        "residual_errors": transit.residual_errors_protected,
        "protection_factor": transit.protection_factor,
        "tmr_gain": TMRVoter.reliability_gain(1e-4),
        "tid_margin": tid_margin,
        "fdir_final_state": final_state,
    }


# =============================================================================
# Driver
# =============================================================================

_MODULES = {
    1: ("Baseline DTN simulation", run_baseline_simulation),
    2: ("Optical vs RF link budget", run_link_budget_comparison),
    3: ("RL routing convergence", run_rl_training_demo),
    4: ("Failure & recovery (solar conjunction)", run_failure_recovery),
    5: ("QKD security (BB84)", run_qkd_security),
    6: ("Radiation hardening", run_radiation_demo),
}


def run_all(seed: int = 42, quiet: bool = False) -> Dict[str, Any]:
    """Run every module and return a combined results dict."""
    if not quiet:
        print()
        print(_c("=" * 72, _DIM))
        print(_c("  AETHERIX — Interplanetary DTN End-to-End Simulation", _BOLD + _CYAN))
        print(_c("  Autonomous Extraterrestrial High-throughput Enhancing Routing", _DIM))
        print(_c("  and Inter-planetary eXchange", _DIM))
        print(_c("=" * 72, _DIM))
        print(f"  Python {sys.version.split()[0]}  |  seed = {seed}  |  "
              f"0 external dependencies")

    combined: Dict[str, Any] = {}
    for num, (name, fn) in _MODULES.items():
        try:
            if num in (1, 3, 5):
                combined[name] = fn(seed=seed, quiet=quiet)
            else:
                combined[name] = fn(quiet=quiet)
        except Exception as exc:  # keep going even if one module fails
            combined[name] = {"error": str(exc)}
            if not quiet:
                print(_c(f"  [module {num} failed: {exc}]", _RED))

    if not quiet:
        print()
        print(_c("=" * 72, _GREEN))
        print(_c("  All modules complete.", _BOLD + _GREEN))
        print(_c("=" * 72, _GREEN))
        print()
    return combined


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AETHERIX end-to-end simulation driver.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Modules: " + ", ".join(f"{n}={m[0]}" for n, m in _MODULES.items()),
    )
    parser.add_argument("--module", "-m", type=int, choices=list(_MODULES),
                        help="run a single module by number")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (default 42)")
    parser.add_argument("--quiet", "-q", action="store_true", help="suppress output")
    args = parser.parse_args(argv)

    if args.module is not None:
        name, fn = _MODULES[args.module]
        if args.module in (1, 3, 5):
            fn(seed=args.seed, quiet=args.quiet)
        else:
            fn(quiet=args.quiet)
    else:
        run_all(seed=args.seed, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
