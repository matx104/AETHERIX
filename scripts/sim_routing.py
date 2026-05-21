#!/usr/bin/env python3

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from routing.rl_agent import NetworkState, RLRoutingAgent, RoutingAction


PRIORITY_NAMES = {0: "EMERGENCY", 1: "HIGH_SCIENCE", 2: "STANDARD", 3: "HOUSEKEEPING", 4: "BULK"}

DEFAULT_NEIGHBORS = [
    "mars.areo.alpha",
    "transit.esl4.relay",
    "mars.polar.gamma",
]

DEFAULT_LINK_QUALITIES = {
    "mars.areo.alpha": 0.85,
    "transit.esl4.relay": 0.72,
    "mars.polar.gamma": 0.60,
}


def print_decision(state, decision, episodes, agent):
    print()
    print("  ╔══════════════════════════════════════════════════════════════════╗")
    print("  ║            AETHERIX RL ROUTING DECISION SIMULATION             ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    print("  ║ NETWORK STATE                                                  ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    print(f"  ║  Current Node:     {state.current_node:<42s}  ║")
    print(f"  ║  Destination:      {state.destination_node:<42s}  ║")
    print(f"  ║  Buffer Occupancy: {state.buffer_occupancy * 100:>5.1f}%{' ' * 35}║")
    print(f"  ║  Bundle Priority:  {state.bundle_priority} ({PRIORITY_NAMES.get(state.bundle_priority, 'UNKNOWN'):>14s}){' ' * 20}║")
    print(f"  ║  Bundle Size:      {state.bundle_size_mb:>8.1f} MB{' ' * 32}║")
    print(f"  ║  Deadline:         {state.bundle_deadline_hours:>8.1f} hrs{' ' * 30}║")
    print("  ║                                                                 ║")
    print("  ║ NEIGHBORS & LINK QUALITY                                        ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    for nbr in state.neighbors:
        q = state.link_qualities.get(nbr, 0.0)
        bar_len = int(q * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  ║  {nbr:<28s} [{bar}] {q:.2f}  ║")
    print("  ║                                                                 ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    print("  ║ ROUTING DECISION                                                ║")
    print("  ╠══════════════════════════════════════════════════════════════════╣")
    action_str = decision.action.value.upper()
    print(f"  ║  Action:       {action_str:<46s}  ║")
    print(f"  ║  Next Hop:     {(decision.next_hop or 'N/A'):<46s}  ║")
    print(f"  ║  Confidence:   {decision.confidence:>6.1%}{' ' * 40}  ║")
    print(f"  ║  Reasoning:    {decision.reasoning:<46s}  ║")
    if episodes > 0:
        print("  ║                                                                 ║")
        print(f"  ║  Training Episodes: {episodes:<6d}  Q-Table Entries: {len(agent.q_table):<12d}  ║")
    print("  ╚══════════════════════════════════════════════════════════════════╝")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="AETHERIX RL Routing Agent Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s --node mars.areo.alpha --destination earth.control.moc\n"
               "  %(prog)s --node transit.esl4.relay --destination earth.dsn.goldstone --priority 0\n"
               "  %(prog)s --episodes 200\n",
    )
    parser.add_argument("--node", default="mars.areo.alpha", help="Current node ID (default: mars.areo.alpha)")
    parser.add_argument("--destination", default="earth.control.moc", help="Destination node ID")
    parser.add_argument("--priority", type=int, default=2, choices=range(5), help="Bundle priority 0-4 (default: 2)")
    parser.add_argument("--buffer", type=float, default=0.35, help="Buffer occupancy 0-1 (default: 0.35)")
    parser.add_argument("--episodes", type=int, default=0, help="Number of training episodes (default: 0)")

    args = parser.parse_args()

    try:
        agent = RLRoutingAgent(node_id=args.node, epsilon=0.1)

        state = NetworkState(
            current_node=args.node,
            neighbors=list(DEFAULT_NEIGHBORS),
            link_qualities=dict(DEFAULT_LINK_QUALITIES),
            buffer_occupancy=max(0.0, min(1.0, args.buffer)),
            bundle_priority=args.priority,
            bundle_size_mb=500.0,
            bundle_deadline_hours=24.0,
            destination_node=args.destination,
        )

        for _ in range(args.episodes):
            decision = agent.select_action(state)
            reward = agent.calculate_reward(
                delivered=decision.action in (RoutingAction.FORWARD, RoutingAction.STORE),
                delay_seconds=120.0,
                hops=3,
                dropped=decision.action == RoutingAction.DROP,
                energy_wh=0.5,
            )
            agent.update(state, decision.action, reward, state)

        decision = agent.select_action(state)
        print_decision(state, decision, args.episodes, agent)

    except Exception as e:
        print(f"\n  ERROR: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
