#!/usr/bin/env python3
"""Generate AETHERIX presentation script markdown files (Full + Compact)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "docs" / "downloads"

FULL_SLIDES = [
    (1, "Introduction", 30,
     "Good morning. I'm Muhammad Abdullah Tariq, presenting AETHERIX — an architecture for interplanetary communication supporting Mars missions. AETHERIX stands for Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange. Today I'll walk you through how we solve the fundamental challenges of communicating across millions of kilometers of space."),
    (2, "Agenda", 20,
     "Here's our roadmap for the next 18 minutes. We'll cover the challenge, the architecture, DTN protocols, network topology, link budgets, AI routing, quantum security, orbital mechanics, radiation hardening, data prioritization, and close with a live demo and performance comparison."),
    (3, "What is AETHERIX", 90,
     "AETHERIX addresses these challenges through four integrated innovations. First, Bundle Protocol version 7 provides delay-tolerant networking via store-and-forward. Second, reinforcement learning agents replace static routing with autonomous adaptive decisions. Third, quantum key distribution provides information-theoretically secure encryption. And fourth, hybrid optical-radio frequency links deliver 10 to 100 times higher data rates with RF backup for reliability."),
    (4, "The Distance", 90,
     "The distance to Mars varies from 55 million kilometers at closest approach to over 400 million kilometers when Earth and Mars are on opposite sides of the Sun. At the speed of light, that's a one-way delay of 3 to 22 minutes. TCP/IP expects millisecond round-trip times — it simply cannot work with 6 to 44 minute round-trips. Current Mars missions achieve only 0.5 to 6 megabits per second. And every 780 days, during solar conjunction, direct communication is impossible for about two weeks."),
    (5, "Distance Over Time Chart", 20,
     "Distance over the synodic period showing the 7x variation. At opposition, 55 million km. At conjunction, over 400 million km with the Sun blocking direct communication."),
    (6, "Light-Time Delay Chart", 20,
     "Light-time delay ranges from 3 minutes at closest approach to 22 minutes at maximum distance. TCP/IP expects sub-second round trips — this is why we need DTN."),
    (7, "The Answer", 90,
     "The Bundle Protocol works like a postal service rather than a phone call. Instead of requiring a live connection between sender and receiver, each bundle is stored at every intermediate node until the next link becomes available. Custody transfer is critical: each node that accepts a bundle takes legal responsibility for its delivery. The previous custodian can then free its buffer."),
    (8, "System Architecture", 60,
     "The architecture has five core modules feeding into a simulation engine. Infrastructure handles optical and RF link budget calculations. Routing implements the RL agent, BPv7 bundles, and the store-and-forward engine. Security covers QKD protocols and repeater chains. Orbital computes contact windows and Doppler shifts. And Simulation integrates everything for end-to-end scenario analysis."),
    (9, "Architecture Diagram", 60,
     "This diagram shows how the source modules feed into the simulation engine and web demos. Each module is independently testable — we have 189 automated tests validating correctness."),
    (10, "Network Tier Distribution Chart", 20,
     "The tier distribution shows where the 241 nodes sit. Mars Surface dominates with 167 nodes — habitats, rovers, drones, sensors. The 4 deep space nodes at Lagrange points are few but critical for conjunction survival."),
    (11, "BPv7 Deep Dive", 120,
     "BPv7 is the postal service protocol. Walk through the stack: Application at top, BPv7 as the store-and-forward layer, three convergence layers for different link types, physical at bottom. Custody transfer is the key innovation — each node takes legal responsibility. Priority P0 emergency to P4 bulk. We use three convergence layers: LTP for deep space, TCPCL for Earth-segment connections, and UDP-CL for inter-satellite optical links."),
    (12, "DTN Store-and-Forward", 120,
     "Walk through the store-and-forward process. Bundle arrives, gets stored, node waits for next contact opportunity, then forwards. If link drops, bundle stays stored and retries. No data loss. This is fundamentally different from TCP's end-to-end retransmission. LTP handles the deep-space hop with reliable segments. TCPCL manages Earth-segment distribution. UDP-CL models optical inter-satellite links."),
    (13, "DTN Diagram", 20,
     "DTN diagram showing store-and-forward with custody transfer."),
    (14, "Bundle Priority Chart", 20,
     "The priority class distribution shows how bandwidth is allocated. Emergency traffic preempts everything. The deadline-aware scheduler ensures no bandwidth is wasted while respecting priority constraints."),
    (15, "Network Topology", 120,
     "The network spans five tiers with 241 nodes. Earth's ground segment with DSN stations in Goldstone, Madrid, and Canberra — spaced 120 degrees apart for 24/7 coverage. Tier 2 has GEO relays and a 48-satellite LEO laser constellation. Tier 3 has Lagrange point relays at ES-L4 and ES-L5 — critical because they maintain communication around the Sun during conjunction. Tier 4 is Mars orbital with areostationary relays at 17,032 km. Tier 5 is the Mars surface network."),
    (16, "5-Tier Network Diagram", 60,
     "Earth-to-deep-space links at 100 Mbps via 1550 nm laser. Deep-space-to-Mars is distance-dependent at 2 to 200 Mbps. Mars orbital to surface uses UHF S-band at 2 Mbps. LEO inter-satellite mesh runs at 10 Gbps with laser links."),
    (17, "Network Diagram", 20,
     "This visualization shows the full 5-tier topology with three redundant paths. No single link failure can sever Earth-Mars communication."),
    (18, "DSN Coverage Chart", 20,
     "DSN coverage showing three stations spaced 120 degrees apart for continuous coverage of any deep space asset."),
    (19, "Orbital Positions Chart", 20,
     "Orbital positions over the synodic period showing how Earth and Mars move relative to each other, determining contact quality."),
    (20, "Optical Communications", 120,
     "Let me demonstrate the link budget calculations live. At closest approach — 54.6 million kilometers — our 5-watt laser with a 22-centimeter transmit aperture and 1-meter ground receive telescope achieves 100 to 200 megabits per second. That's over 30 times faster than the current Mars Reconnaissance Orbiter. Even at maximum distance of 401 million kilometers, we maintain 2 to 5 megabits per second."),
    (21, "Data Rate vs Distance Chart", 20,
     "Data rate degrades from 200 Mbps at closest approach to 2 Mbps at maximum distance — but even minimum is competitive with current RF."),
    (22, "Link Budget Breakdown Chart", 20,
     "Link budget breakdown showing where the decibels go — free-space path loss is the dominant factor, compensated by high-gain optical apertures."),
    (23, "Earth-Mars Journey", 60,
     "Here's the 7-hop journey. 500 MB from Perseverance to JPL. Total transit about 13 minutes versus 12.5 minutes light-time — near speed of light! DTN overhead under 5 percent. 98.7 percent delivery ratio."),
    (24, "Earth-Mars Journey Diagram", 20,
     "Visual diagram of the 7-hop Earth-Mars data journey."),
    (25, "Latency Comparison Chart", 20,
     "Latency comparison showing TCP failing catastrophically, while DTN adds under 5% overhead beyond the physical light-time limit."),
    (26, "Data Volume Chart", 20,
     "AETHERIX delivers 10 to 20 times more data per day than current Mars missions."),
    (27, "RL Routing", 120,
     "Traditional Contact Graph Routing requires pre-computed contact schedules that cannot adapt to unexpected conditions. Our reinforcement learning agent learns from experience. It observes state variables including link quality, buffer occupancy, bundle priority, and deadline. It selects from four actions: forward, store, drop, or split. The reward function balances delivery success against delay, hop count, and energy consumption."),
    (28, "RL Routing Heatmap Chart", 20,
     "The Q-value heatmap shows how the RL agent converges on optimal routing decisions. Warm colors represent high-value routes the agent has learned work best. Cool colors are poor choices the agent avoids."),
    (29, "Quantum Security", 120,
     "Quantum key distribution provides security based on the laws of physics, not computational difficulty. In the BB84 protocol, Alice sends quantum bits in random bases. Bob measures in random bases. They publicly compare a sample to estimate the Quantum Bit Error Rate. If the QBER is below 11 percent, the key is secure. We deploy QKD in three phases: Earth-to-LEO, GEO, and ultimately quantum repeaters at Lagrange points for Earth-Mars security."),
    (30, "QKD Security Chart", 20,
     "QBER analysis showing the security threshold. Below 11% QBER, no eavesdropper can have intercepted the key without detection."),
    (31, "QKD Key Rate Chart", 20,
     "Key generation rates decrease with distance, which is why we deploy quantum repeaters at Lagrange points to extend range."),
    (32, "Orbital Mechanics", 90,
     "The 780-day synodic period means we cycle from best-case opposition through worst-case conjunction. During the roughly two-week conjunction window, direct communication is impossible. AETHERIX's Lagrange point relays at ES-L4 and ES-L5 maintain a path around the Sun, providing 50 to 70 percent availability even during conjunction. Doppler shift of 15 gigahertz at 1550 nm requires real-time compensation."),
    (33, "Contact Windows Chart", 20,
     "Contact window availability over the full synodic period. Notice the solar conjunction gap where direct communication drops to zero — that is exactly where our Lagrange relay chain maintains 50 to 70 percent capacity."),
    (34, "Radiation Hardening", 90,
     "Space radiation is relentless. Single-event upsets flip bits constantly — about 37,000 during a Mars transit. Our defense-in-depth: triple modular redundancy masks logic faults with a 3,334x reliability gain. SECDED ECC corrects single-bit errors. Scrubbing prevents double-bit accumulation. And FDIR with a watchdog catches everything else. The RAD750 processor can tolerate 200 kilorads — far above what a Mars mission needs."),
    (35, "Data Prioritization", 60,
     "Like an emergency room. P0 emergency gets sent immediately — it can even preempt an in-progress transfer. P1 mission-critical next. P2 routine science. P4 bulk data fills remaining bandwidth. Compression multiplies effective capacity: 3x for telemetry, 10x for images, 50x for video. Our scheduler keeps the link at 100 percent utilization."),
    (36, "End-to-End Mission", 90,
     "Let's walk through a complete mission scenario — transferring 500 megabytes from the Perseverance rover to JPL. The bundle traverses 7 hops. Total time: about 13 minutes. The fundamental light-time is 12.5 minutes, so DTN processing overhead is less than 5 percent. If the deep space link drops at any point, the bundle is NOT lost — it's stored at the last custodian node and the RL agent reroutes."),
    (37, "Data Flow Diagram", 60,
     "This shows the end-to-end bundle journey through all protocol layers. From application data, through BPv7 wrapping, RL routing, QKD encryption, LTP segmentation, physical transmission, and finally reassembly and delivery."),
    (38, "Data Flow Diagram Visual", 20,
     "The visual data flow through the complete protocol stack."),
    (39, "Protocol Stack Diagram", 20,
     "Protocol stack showing BPv7 with three convergence layers."),
    (40, "Network Topology Diagram", 20,
     "Network topology graph with BFS pathfinding and RL enhancement."),
    (41, "Performance", 60,
     "The bottom line: AETHERIX delivers 10 to 100 times higher data rates with greater than 95 percent availability at one-tenth the cost per megabyte. Our architecture scales to 241 nodes compared to the 5 to 10 assets currently connected. The routing is autonomous. The security is quantum-ready."),
    (42, "Performance Comparison Chart", 20,
     "Head-to-head comparison showing AETHERIX outperforming current systems across every metric."),
    (43, "Optical vs RF Radar Chart", 20,
     "Radar chart showing why we chose optical as primary with RF backup — optical dominates bandwidth and efficiency, while RF provides reliability."),
    (44, "Implementation", 60,
     "This is real, working code. 27 Python modules, 189 tests, 12 interactive demos. All the physics is real — no mocked data. The showcase site has live calculators you can use right now. Standards compliance is complete — seven CCSDS Blue Books and four IETF RFCs."),
    (45, "Bandwidth Evolution Chart", 20,
     "Bandwidth evolution from Mariner at 8.3 bps to MRO at 6 Mbps to AETHERIX targeting 200 Mbps — a 30 million times improvement."),
    (46, "Energy Efficiency Chart", 20,
     "Energy efficiency comparison showing optical links use significantly less energy per transmitted bit than RF alternatives."),
    (47, "Mission Timeline Chart", 20,
     "Mission timeline showing development milestones from proof-of-concept to production deployment."),
    (48, "Roadmap", 60,
     "Phases 1 through 4 are done — this is what you see today. Phase 5 adds ns-3 simulation for realistic network modeling. Phase 6 upgrades to a Deep Q-Network and integrates with NASA's ION-DTN implementation. Phase 7 moves to hardware prototypes with software-defined radios and optical ground station demonstrations."),
    (49, "Conclusion", 60,
     "In summary, AETHERIX delivers four key outcomes: 10 to 100 times faster communications through optical links, over 95 percent availability through multi-path redundancy, AI-driven autonomous routing replacing static schedules, and quantum-secured future-proof encryption."),
    (50, "Thank You", 30,
     "Thank you. I welcome your questions. All simulations are available live at matx104.github.io/AETHERIX."),
]

COMPACT_ORIGINAL_NUMBERS = [1, 2, 3, 4, 7, 8, 9, 11, 15, 16, 20, 21, 23, 27, 28, 29, 30, 32, 38, 41, 42, 44, 48, 49, 50]

SLIDE_MAP = {s[0]: s for s in FULL_SLIDES}


def format_duration(seconds):
    if seconds < 60:
        return f"{seconds} seconds"
    mins = seconds // 60
    secs = seconds % 60
    if secs == 0:
        return f"{mins} minute{'s' if mins != 1 else ''}"
    return f"{mins} minute{'s' if mins != 1 else ''} {secs} seconds"


def format_timestamp(total_seconds):
    mins = int(total_seconds) // 60
    secs = int(total_seconds) % 60
    return f"{mins}:{secs:02d}"


def generate_markdown(slides, title, duration_text, slide_count_label):
    lines = [
        f"# AETHERIX Presentation Script ({title})",
        "",
        "> **Student:** Muhammad Abdullah Tariq  ",
        f"> **Programme:** Diploma in AI Operations  ",
        f"> **Topic:** EduQual Level 6 — Topic 59  ",
        f"> **Duration:** {duration_text}  ",
        f"> **Slides:** {slide_count_label}  ",
        "",
        "---",
        "",
    ]

    cumulative = 0
    for display_num, (_, title_text, duration_secs, script) in enumerate(slides, 1):
        start_ts = format_timestamp(cumulative)
        cumulative += duration_secs
        dur_text = format_duration(duration_secs)

        lines.append(f"## Slide {display_num}: {title_text}")
        lines.append("")
        lines.append(f"**[{start_ts} — {dur_text}]**")
        lines.append("")
        lines.append(script)
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    full_md = generate_markdown(
        FULL_SLIDES,
        "Full — 50 Slides",
        "~18 minutes",
        "50",
    )
    full_path = OUTPUT_DIR / "AETHERIX_Presentation_Script_Full.md"
    full_path.write_text(full_md, encoding="utf-8")

    compact_slides = [SLIDE_MAP[n] for n in COMPACT_ORIGINAL_NUMBERS]
    compact_md = generate_markdown(
        compact_slides,
        "Compact — 25 Slides",
        "~10 minutes",
        "25",
    )
    compact_path = OUTPUT_DIR / "AETHERIX_Presentation_Script_Compact.md"
    compact_path.write_text(compact_md, encoding="utf-8")

    print(f"Full:    {full_path}  ({full_path.stat().st_size:,} bytes)")
    print(f"Compact: {compact_path}  ({compact_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
