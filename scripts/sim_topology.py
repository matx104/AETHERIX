#!/usr/bin/env python3

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from orbital.topology import NetworkTopology, create_default_topology

TIER_NAMES = {
    1: "Earth Ground",
    2: "Earth Orbital",
    3: "Deep Space Transit",
    4: "Mars Orbital",
    5: "Mars Surface",
}


def main():
    parser = argparse.ArgumentParser(
        description="AETHERIX Network Topology Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s\n"
               "  %(prog)s --source dsn-goldstone --destination base-jezero\n"
               "  %(prog)s --source rover-01 --destination earth-moc\n",
    )
    parser.add_argument("--source", help="Source node ID for route finding")
    parser.add_argument("--destination", help="Destination node ID for route finding")

    args = parser.parse_args()

    try:
        topo = create_default_topology()
        tier_summary = topo.get_tier_summary()
        inter_links = topo.get_inter_tier_links()

        print()
        print("  ╔══════════════════════════════════════════════════════════════════╗")
        print("  ║           AETHERIX NETWORK TOPOLOGY ANALYSIS                    ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ OVERVIEW                                                        ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print(f"  ║  Total Nodes:           {topo.get_node_count():<8d}                              ║")
        print(f"  ║  Inter-Tier Links:      {len(inter_links):<8d}                              ║")
        print("  ║                                                                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ TIER SUMMARY                                                     ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        for tier, count in sorted(tier_summary.items()):
            name = TIER_NAMES.get(tier, f"Tier {tier}")
            print(f"  ║  Tier {tier}: {name:<22s} {count:>4d} nodes                        ║")
        print("  ║                                                                 ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        print("  ║ INTER-TIER LINKS BY TYPE                                         ║")
        print("  ╠══════════════════════════════════════════════════════════════════╣")
        link_types = {}
        for link in inter_links:
            key = f"T{link.source_tier}-T{link.dest_tier} ({link.link_type})"
            link_types[key] = link_types.get(key, 0) + 1
        for key, count in sorted(link_types.items()):
            print(f"  ║  {key:<30s}  {count:>4d} links                        ║")
        print("  ║                                                                 ║")

        if args.source and args.destination:
            print("  ╠══════════════════════════════════════════════════════════════════╣")
            print("  ║ ROUTE FINDING                                                   ║")
            print("  ╠══════════════════════════════════════════════════════════════════╣")
            print(f"  ║  Source:      {args.source:<46s}  ║")
            print(f"  ║  Destination: {args.destination:<46s}  ║")

            src_node = topo.get_node(args.source)
            dst_node = topo.get_node(args.destination)

            if not src_node:
                print(f"  ║  ERROR: Source node '{args.source}' not found in topology.            ║")
            elif not dst_node:
                print(f"  ║  ERROR: Destination node '{args.destination}' not found in topology.   ║")
            else:
                route = topo.find_route(args.source, args.destination)
                if route:
                    print(f"  ║  Hops:        {len(route) - 1:<46d}  ║")
                    print("  ║  Path:                                                          ║")
                    for i, node_id in enumerate(route):
                        arrow = " -> " if i > 0 else "    "
                        node = topo.get_node(node_id)
                        tier_str = f" [T{node.tier}]" if node else ""
                        print(f"  ║  {arrow}{node_id}{tier_str}")
                else:
                    print("  ║  No route found between specified nodes.                        ║")
            print("  ║                                                                 ║")

        elif args.source or args.destination:
            node_id = args.source or args.destination
            node = topo.get_node(node_id)
            if node:
                neighbors = topo.get_neighbors(node_id)
                print("  ╠══════════════════════════════════════════════════════════════════╣")
                print(f"  ║ NODE: {node_id:<52s}  ║")
                print("  ╠══════════════════════════════════════════════════════════════════╣")
                print(f"  ║  Tier:     {node.tier:<46d}  ║")
                print(f"  ║  Type:     {node.node_type.value:<46s}  ║")
                print(f"  ║  Neighbors ({len(neighbors)}):{' ' * 43}  ║")
                for nbr in sorted(neighbors)[:10]:
                    print(f"  ║    - {nbr:<54s}  ║")
                if len(neighbors) > 10:
                    print(f"  ║    ... and {len(neighbors) - 10} more{' ' * 42}  ║")
                print("  ║                                                                 ║")
            else:
                print(f"  ║  ERROR: Node '{node_id}' not found in topology.                       ║")

        print("  ╚══════════════════════════════════════════════════════════════════╝")
        print()

    except Exception as e:
        print(f"\n  ERROR: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
