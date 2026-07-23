#!/usr/bin/env python3
"""
AETHERIX Compact PDF Presentation Generator
Creates the 31-slide compact deck. Shares the deck_style.py design system
with the full generator so both decks look identical.
"""

import os
from reportlab.pdfgen import canvas

import deck_style as ds
from deck_style import (  # noqa: F401 \u2014 names used throughout the page code
    PAGE_W, PAGE_H,
    BG_DARK, ACCENT_BLUE, ACCENT_CYAN, ACCENT_PURPLE, ACCENT_ORANGE,
    ACCENT_RED, WHITE, LIGHT_GRAY, MED_GRAY, CARD_BG, CARD_BORDER, GREEN,
    TABLE_ROW_ALT,
    draw_bg, draw_starfield, draw_orbit_arc, draw_accent_line,
    draw_top_bar, draw_bottom_bar, draw_card, draw_text, draw_multiline,
    draw_image_safe, draw_table, draw_footer,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "presentation", "output")
CHARTS_DIR = os.path.join(BASE_DIR, "visualizations", "charts")
DIAGRAMS_DIR = os.path.join(BASE_DIR, "visualizations", "diagrams")

os.makedirs(OUTPUT_DIR, exist_ok=True)

TOTAL_SLIDES = 33

pdf_path = os.path.join(OUTPUT_DIR, "AETHERIX_Presentation_Compact.pdf")
c = canvas.Canvas(pdf_path, pagesize=(PAGE_W, PAGE_H))

# The compact deck carries no speaker-notes band.
ds.configure(TOTAL_SLIDES, {})


def draw_chart_page(c, chart_file, title, subtitle, caption, accent_color=ACCENT_BLUE, citations=None):
    ds.draw_chart_page(c, CHARTS_DIR, chart_file, title, subtitle, caption,
                       accent_color=accent_color, notes=None, citations=citations)


# ================================================================
# PAGE 1 — Title (Introduction)
# ================================================================
print("Creating Page 1: Introduction...")
draw_bg(c)
draw_starfield(c)
draw_orbit_arc(c)
draw_top_bar(c)
draw_bottom_bar(c)

draw_text(c, "AETHERIX", PAGE_W / 2, PAGE_H - 120, size=54, color=WHITE, bold=True, align="center")
draw_accent_line(c, PAGE_W / 2 - 100, PAGE_H - 140, 200, ACCENT_CYAN, 4)
draw_text(c, "Autonomous Extraterrestrial High-throughput Enhancing Routing", PAGE_W / 2, PAGE_H - 175, size=16, color=ACCENT_CYAN, align="center")
draw_text(c, "and Inter-planetary eXchange", PAGE_W / 2, PAGE_H - 195, size=16, color=ACCENT_CYAN, align="center")
draw_text(c, "Building an Interplanetary Communication Network with DTN,", PAGE_W / 2, PAGE_H - 235, size=13, color=LIGHT_GRAY, align="center")
draw_text(c, "Quantum Communication, and Space-Based Infrastructure for Mars Mission Support", PAGE_W / 2, PAGE_H - 250, size=13, color=LIGHT_GRAY, align="center")
draw_accent_line(c, PAGE_W / 2 - 150, PAGE_H - 275, 300, ACCENT_BLUE, 2)
draw_text(c, "Muhammad Abdullah Tariq", PAGE_W / 2, PAGE_H - 310, size=18, color=WHITE, bold=True, align="center")
draw_text(c, "EduQual Level 6 Diploma in AI Operations  |  Topic 59  |  September 2026", PAGE_W / 2, PAGE_H - 335, size=12, color=MED_GRAY, align="center")
draw_text(c, "matx104.github.io/AETHERIX  |  github.com/matx104/AETHERIX", PAGE_W / 2, PAGE_H - 390, size=11, color=ACCENT_BLUE, align="center")
c.showPage()


# ================================================================
# PAGE 2 — Agenda
# ================================================================
print("Creating Page 2: Agenda...")
draw_bg(c)
draw_text(c, "PRESENTATION AGENDA", 40, PAGE_H - 50, size=24, color=WHITE, bold=True)
draw_accent_line(c, 40, PAGE_H - 62, 200, ACCENT_CYAN)

agenda = [
    ("01", "The Challenge", "Why interplanetary communication is hard", ACCENT_BLUE),
    ("02", "AETHERIX Architecture", "DTN + AI Routing + Quantum Security", ACCENT_CYAN),
    ("03", "DTN & Bundle Protocol v7", "Store-and-forward networking foundation", ACCENT_PURPLE),
    ("04", "5-Tier Network Topology", "241 nodes across Earth and Mars", ACCENT_BLUE),
    ("05", "Optical Link Budget", "1550 nm laser performance analysis", ACCENT_ORANGE),
    ("06", "RL-Based Routing", "Multi-agent federated Q-learning", ACCENT_CYAN),
    ("07", "Quantum Security (QKD)", "BB84/E91 with repeater chains", ACCENT_PURPLE),
    ("08", "Orbital Mechanics", "Contact windows and synodic period", ACCENT_BLUE),
    ("09", "Mars Mission Scenario", "End-to-end simulation walkthrough", ACCENT_ORANGE),
    ("10", "Performance Comparison", "AETHERIX vs current systems", GREEN),
    ("11", "Roadmap & Standards", "CCSDS, IETF, deployment phases", ACCENT_CYAN),
    ("12", "Conclusion & Q&A", "Summary and live demo", WHITE),
]

col1_x = 40
col2_x = PAGE_W / 2 + 20
start_y = PAGE_H - 95

for i, (num, title, desc, color) in enumerate(agenda):
    cx = col1_x if i < 6 else col2_x
    cy = start_y - 80 * (i % 6)
    draw_card(c, cx, cy - 35, PAGE_W / 2 - 55, 70, color)
    draw_text(c, f"{num}  {title}", cx + 15, cy + 10, size=13, color=color, bold=True)
    draw_text(c, desc, cx + 15, cy - 10, size=10, color=MED_GRAY)

draw_footer(c, 2, citations="[A2] AETHERIX topology.py (241 nodes)  \u00b7  References slide at end")
c.showPage()


# ================================================================
# PAGE 3 — What is AETHERIX
# ================================================================
print("Creating Page 3: What is AETHERIX...")
draw_bg(c)
draw_text(c, "WHAT IS AETHERIX?", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_BLUE)

draw_card(c, 40, PAGE_H - 260, 420, 160, ACCENT_BLUE)
draw_text(c, "What is AETHERIX?", 55, PAGE_H - 110, size=14, color=ACCENT_BLUE, bold=True)
draw_text(c, "An architecture for delay-tolerant networking (DTN) between", 55, PAGE_H - 135, size=11, color=LIGHT_GRAY)
draw_text(c, "Earth and Mars, combining:", 55, PAGE_H - 150, size=11, color=LIGHT_GRAY)
what_lines = [
    "  \u2022  Bundle Protocol v7 (BPv7) via ION-DTN",
    "  \u2022  Reinforcement Learning routing (replacing static CGR)",
    "  \u2022  Quantum Key Distribution (QKD) for security",
    "  \u2022  Hybrid optical/RF communications",
    "  \u2022  5-tier topology with 241 nodes",
]
for i, line in enumerate(what_lines):
    draw_text(c, line, 55, PAGE_H - 175 - 17 * i, size=10, color=LIGHT_GRAY)

draw_card(c, 480, PAGE_H - 260, 380, 160, ACCENT_RED)
draw_text(c, "The Problem", 495, PAGE_H - 110, size=14, color=ACCENT_RED, bold=True)
prob_lines = [
    "  \u2022  Earth-Mars: 54.6M \u2013 401M km distance [3]",
    "  \u2022  One-way light delay: 3 \u2013 22 minutes [3]",
    "  \u2022  Solar conjunction: 2-week total blackout",
    "  \u2022  TCP/IP fundamentally cannot work [12]",
    "  \u2022  Current RF: 0.5 \u2013 6 Mbps (NASA MRO) [1]",
]
for i, line in enumerate(prob_lines):
    draw_text(c, line, 495, PAGE_H - 140 - 17 * i, size=10, color=LIGHT_GRAY)

draw_card(c, 40, PAGE_H - 380, 820, 80, ACCENT_CYAN)
draw_text(c, "AETHERIX delivers a complete interplanetary networking solution", 55, PAGE_H - 325, size=12, color=ACCENT_CYAN, bold=True)
draw_text(c, "combining DTN protocols, AI-driven routing, quantum-secure keys, and hybrid optical/RF links for Mars mission support.", 55, PAGE_H - 345, size=10, color=LIGHT_GRAY)

stats = [("10-100\u00d7", "Target \u2666", ACCENT_BLUE), (">95%", "Availability (target)", GREEN), ("241", "Nodes [A2]", ACCENT_ORANGE), ("480", "Tests", ACCENT_PURPLE)]
for i, (val, label, color) in enumerate(stats):
    x = 40 + 210 * i
    draw_card(c, x, 60, 195, 55, color)
    draw_text(c, val, x + 97, 95, size=18, color=color, bold=True, align="center")
    draw_text(c, label, x + 97, 72, size=10, color=LIGHT_GRAY, align="center")

draw_footer(c, 3, citations="[1] NASA MRN 2024  \u00b7  [3] JPL Horizons  \u00b7  [12] RFC 4838  \u00b7  [A2] topology.py")
c.showPage()


# ================================================================
# PAGE 4 — The Distance
# ================================================================
print("Creating Page 4: The Distance...")
draw_bg(c)
draw_text(c, "THE DISTANCE", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Why Space Communication is Fundamentally Different", 40, PAGE_H - 75, size=14, color=ACCENT_ORANGE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_ORANGE)

dist_data = [
    ["Earth \u2192 Mars", "Distance", "Light Time", "Data Rate"],
    ["Perihelion (closest)", "54.6M km", "~3 min", "100-200 Mbps"],
    ["Average", "225M km", "~12.5 min", "10-20 Mbps"],
    ["Aphelion (farthest)", "401M km", "~22 min", "2-5 Mbps"],
]
draw_table(c, dist_data, 40, PAGE_H - 100, [140, 100, 100, 120], ACCENT_BLUE)

tcp_data = [
    ["TCP/IP Assumption", "Space Reality", "Impact"],
    ["RTT < 1 second", "6 \u2013 44 min RTT [3]", "Timeout failure"],
    ["Always connected", "Scheduled contacts", "Connection drops"],
    ["End-to-end path", "No persistent path", "Routing impossible"],
    ["Fast acknowledgments", "ACKs take minutes [3]", "Window collapse"],
    ["Low packet loss", "High loss (optical)", "Retransmit storms"],
]
draw_table(c, tcp_data, 40, PAGE_H - 270, [160, 160, 140], ACCENT_RED)

draw_card(c, 460, PAGE_H - 460, 400, 90, ACCENT_ORANGE)
draw_text(c, '"At aphelion, a single ping-pong takes 44 minutes.', 475, PAGE_H - 395, size=11, color=ACCENT_ORANGE)
draw_text(c, 'No TCP session can survive that. We need an entirely', 475, PAGE_H - 412, size=11, color=ACCENT_ORANGE)
draw_text(c, 'different networking paradigm."', 475, PAGE_H - 429, size=11, color=ACCENT_ORANGE)

draw_footer(c, 4, citations="[3] JPL Horizons (distance/light-time)  \u00b7  [12] RFC 4838 (DTN rationale)  \u00b7  [1] NASA MRO data rate")
c.showPage()


# ================================================================
# PAGE 5 — The Answer (DTN)
# ================================================================
print("Creating Page 5: The Answer...")
draw_bg(c)
draw_text(c, "THE ANSWER: DELAY-TOLERANT NETWORKING", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Decouple Communication from Connectivity", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_CYAN)

flow_steps = ["CREATE\nBundle", "STORE\nLocally", "WAIT\nFor Link", "FORWARD\nNext Hop", "DELIVER\nDestination"]
step_colors = [ACCENT_BLUE, ACCENT_ORANGE, ACCENT_PURPLE, ACCENT_CYAN, GREEN]
for i, (step, col) in enumerate(zip(flow_steps, step_colors)):
    x = 40 + 175 * i
    draw_card(c, x, PAGE_H - 185, 160, 80, col)
    lines = step.split("\n")
    draw_text(c, lines[0], x + 80, PAGE_H - 125, size=12, color=col, bold=True, align="center")
    draw_text(c, lines[1], x + 80, PAGE_H - 145, size=10, color=LIGHT_GRAY, align="center")
    if i < len(flow_steps) - 1:
        draw_text(c, "\u2192", x + 163, PAGE_H - 140, size=18, color=MED_GRAY, bold=True)

stat_cards = [
    ("BPv7", "RFC 9171", "Store-and-forward\nCustody transfer", ACCENT_BLUE),
    ("AI Routing", "RL Agent", "Multi-agent federated\nQ-learning", ACCENT_CYAN),
    ("QKD", "BB84/E91", "Quantum key dist.\nFuture-proof security", ACCENT_PURPLE),
]
for i, (title, sub, desc, col) in enumerate(stat_cards):
    x = 40 + 280 * i
    draw_card(c, x, PAGE_H - 320, 260, 120, col)
    draw_text(c, title, x + 15, PAGE_H - 215, size=16, color=col, bold=True)
    draw_text(c, sub, x + 15, PAGE_H - 235, size=10, color=MED_GRAY)
    for j, line in enumerate(desc.split("\n")):
        draw_text(c, line, x + 15, PAGE_H - 258 - 15 * j, size=9, color=LIGHT_GRAY)

draw_card(c, 40, PAGE_H - 400, 820, 80, ACCENT_CYAN)
draw_text(c, "Key Insight: DTN moves reliability from end-to-end to hop-by-hop. Each custodian is responsible until", 55, PAGE_H - 350, size=11, color=ACCENT_CYAN, bold=True)
draw_text(c, "the next node accepts custody \u2014 enabling communication even with 44-minute round-trip delays.", 55, PAGE_H - 368, size=10, color=LIGHT_GRAY)

draw_footer(c, 5, citations="[9] RFC 9171 BPv7  \u00b7  [10] RFC 5326 LTP  \u00b7  [11] RFC 7242 TCPCL  \u00b7  [12] RFC 4838")
c.showPage()


# ================================================================
# PAGE 6 — System Architecture
# ================================================================
print("Creating Page 6: System Architecture...")
draw_bg(c)
draw_text(c, "SYSTEM ARCHITECTURE", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "5 Integrated Modules for Interplanetary Communication", 40, PAGE_H - 75, size=14, color=ACCENT_BLUE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_BLUE)

modules = [
    ("Infrastructure", "Link budget calculations, optical/RF analysis", ACCENT_ORANGE),
    ("Routing", "RL agents, BPv7 bundles, forwarding engine", ACCENT_CYAN),
    ("Security", "BB84/E91 QKD, repeater chains, privacy amplification", ACCENT_PURPLE),
    ("Orbital", "Contact windows, Doppler, celestial body database", ACCENT_BLUE),
    ("Simulation", "End-to-end scenario engine, policy routing", GREEN),
]
for i, (name, desc, col) in enumerate(modules):
    y = PAGE_H - 120 - 45 * i
    draw_card(c, 40, y - 30, 420, 40, col)
    draw_text(c, name, 55, y - 2, size=12, color=col, bold=True)
    draw_text(c, desc, 180, y - 2, size=10, color=MED_GRAY)

arch_data = [
    ["Layer", "Module", "Engine", "Showcase"],
    ["Infrastructure", "link_budget.py", "OpticalLinkBudget", "Earth-Mars scenarios"],
    ["Routing", "rl_agent.py", "RLRoutingAgent", "Federated Q-learning"],
    ["Security", "qkd.py", "BB84/E91", "Quantum key exchange"],
    ["Orbital", "contact_windows.py", "ContactPredictor", "Synodic period"],
    ["Simulation", "simulator.py", "SimEngine", "Full mission sim"],
]
draw_table(c, arch_data, 40, PAGE_H - 370, [100, 120, 120, 150], ACCENT_BLUE)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "protocol_stack.png"), 480, PAGE_H - 350, w=360)

draw_footer(c, 6, citations="[A1] rl_agent.py  \u00b7  [A2] topology.py  \u00b7  [A3] simulator.py  \u00b7  [A4] link_budget.py  \u00b7  [A5] qkd.py")
c.showPage()


# ================================================================
# PAGE 7 — Architecture Diagram
# ================================================================
print("Creating Page 7: Architecture Diagram...")
draw_bg(c)
draw_text(c, "SYSTEM ARCHITECTURE DIAGRAM", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_accent_line(c, 40, PAGE_H - 62, 200, ACCENT_BLUE)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "system_architecture.png"), 40, 90, w=PAGE_W - 80, h=PAGE_H - 195)

draw_footer(c, 7, citations="[A2] AETHERIX topology.py (5-tier, 241 nodes)  \u00b7  github.com/matx104/AETHERIX")
c.showPage()


# ================================================================
# PAGE 8 — BPv7 Deep Dive
# ================================================================
print("Creating Page 8: BPv7 Deep Dive...")
draw_bg(c)
draw_text(c, "BUNDLE PROTOCOL v7 \u2014 DEEP DIVE", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "RFC 9171 \u2014 The Foundation of Interplanetary Networking", 40, PAGE_H - 75, size=14, color=ACCENT_PURPLE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_PURPLE)

layers = [
    ("APPLICATION LAYER", "Science data, commands, imagery", ACCENT_BLUE),
    ("BUNDLE PROTOCOL v7 (RFC 9171)", "Store-and-Forward | Custody Transfer | Priority (P0\u2013P4)", ACCENT_CYAN),
    ("CONVERGENCE LAYERS", "LTP (deep space) | TCPCL (Earth) | UDP-CL (optical ISL)", ACCENT_PURPLE),
    ("PHYSICAL LAYER", "Optical 1550nm (2\u2013200 Mbps) | RF Ka-band | UHF (surface)", ACCENT_ORANGE),
]
for i, (title, desc, color) in enumerate(layers):
    y = PAGE_H - 130 - 60 * i
    draw_card(c, 40, y - 42, 410, 48, color)
    draw_text(c, title, 55, y - 5, size=11, color=color, bold=True)
    draw_text(c, desc, 55, y - 22, size=8, color=LIGHT_GRAY)

draw_text(c, "HOW IT WORKS", 480, PAGE_H - 100, size=13, color=ACCENT_CYAN, bold=True)
steps = [
    "1. Source creates bundle (payload + metadata + lifetime)",
    "2. Forward to next hop when link becomes available",
    "3. Store locally during outages and disruptions",
    "4. Custody transfer \u2014 next node accepts responsibility",
    "5. Repeat hop-by-hop until destination reached",
]
for i, step in enumerate(steps):
    draw_text(c, step, 480, PAGE_H - 128 - 22 * i, size=10, color=LIGHT_GRAY)

draw_text(c, "STANDARDS COMPLIANCE", 480, PAGE_H - 260, size=12, color=GREEN, bold=True)
standards = [
    "RFC 9171 \u2014 Bundle Protocol Version 7 [9]",
    "RFC 4838 \u2014 DTN Architecture [12]",
    "RFC 5326 \u2014 Licklider Transmission Protocol [10]",
    "RFC 9172 \u2014 Bundle Protocol Security (BPSec)",
    "CCSDS 734.2-B-1 \u2014 CCSDS Bundle Protocol [2]",
    "CCSDS 734.3-B-1 \u2014 Schedule-Aware Bundle Routing",
]
for i, s in enumerate(standards):
    draw_text(c, s, 480, PAGE_H - 288 - 18 * i, size=9, color=LIGHT_GRAY)

pri_data = [
    ["Priority", "Name", "Delay Target", "Example"],
    ["P0", "Emergency", "< 1 min", "Anomaly alerts"],
    ["P1", "Expedited", "< 30 min", "Solar storm warnings"],
    ["P2", "Standard", "< 24 hrs", "Science data"],
    ["P3", "Normal", "< 7 days", "Telemetry"],
    ["P4", "Bulk", "< 30 days", "Software updates"],
]
draw_table(c, pri_data, 40, PAGE_H - 420, [60, 80, 80, 120], ACCENT_BLUE)

draw_footer(c, 8, citations="[9] RFC 9171  \u00b7  [2] CCSDS 734.2-B-1  \u00b7  [10] RFC 5326 LTP  \u00b7  [11] RFC 7242 TCPCL  \u00b7  [12] RFC 4838")
c.showPage()


# ================================================================
# PAGE 9 — Network Topology
# ================================================================
print("Creating Page 9: Network Topology...")
draw_bg(c)
draw_text(c, "5-TIER NETWORK TOPOLOGY", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "241 Nodes \u2014 No Single Point of Failure", 40, PAGE_H - 75, size=14, color=GREEN)
draw_accent_line(c, 40, PAGE_H - 85, 180, GREEN)

tiers = [
    ("TIER 1", "Earth Ground", "6 nodes", "DSN Goldstone, Madrid, Canberra + Mission Control", ACCENT_BLUE),
    ("TIER 2", "Earth Orbital", "51 nodes", "3 GEO relays + 48 LEO laser constellation", GREEN),
    ("TIER 3", "Deep Space", "4 nodes", "ES-L4, ES-L5 Lagrange relays + Transfer orbit", ACCENT_PURPLE),
    ("TIER 4", "Mars Orbital", "4 nodes", "2 Areostationary + 2 polar orbiters", ACCENT_ORANGE),
    ("TIER 5", "Mars Surface", "176 nodes", "Bases, rovers, drones, sensor network", ACCENT_RED),
]

for i, (tier, name, count, desc, color) in enumerate(tiers):
    y = PAGE_H - 125 - 55 * i
    draw_card(c, 40, y - 38, 820, 45, color)
    c.setFillColor(color)
    c.rect(40, y - 38, 6, 45, fill=1, stroke=0)
    draw_text(c, f"{tier}: {name} ({count})", 60, y - 5, size=13, color=color, bold=True)
    draw_text(c, desc, 60, y - 22, size=10, color=MED_GRAY)

draw_card(c, 40, PAGE_H - 430, 820, 60, ACCENT_CYAN)
draw_text(c, "DESIGN PHILOSOPHY", 55, PAGE_H - 385, size=12, color=ACCENT_CYAN, bold=True)
draw_text(c, "Multiple redundant paths at every tier ensure no single point of failure. Lagrange point relays provide coverage", 55, PAGE_H - 402, size=10, color=LIGHT_GRAY)
draw_text(c, "during solar conjunction blackouts. Quantum repeaters co-located at L4/L5 enable end-to-end key distribution.", 55, PAGE_H - 418, size=10, color=LIGHT_GRAY)

draw_footer(c, 9, citations="[A2] AETHERIX topology.py (241 nodes, 5 tiers)  \u00b7  [1] NASA Deep Space Network (Goldstone/Madrid/Canberra)")
c.showPage()


# ================================================================
# PAGE 10 — 5-Tier Network Diagram
# ================================================================
print("Creating Page 10: 5-Tier Network Diagram...")
draw_bg(c)
draw_text(c, "5-TIER NETWORK DIAGRAM", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "241 Nodes from Earth to Mars Surface", 40, PAGE_H - 75, size=14, color=GREEN)
draw_accent_line(c, 40, PAGE_H - 85, 200, GREEN)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "5tier_network.png"), 40, 90, w=PAGE_W - 80, h=PAGE_H - 195)

draw_footer(c, 10, citations="[A2] AETHERIX topology.py  \u00b7  [3] JPL Horizons (Lagrange ES-L4/L5 geometry)")
c.showPage()


# ================================================================
# PAGE — Network Topology Graph
# ================================================================
print("Creating Page: Network Topology Graph...")
draw_bg(c)
draw_text(c, "NETWORK TOPOLOGY GRAPH", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "241 Nodes \u2014 BFS Pathfinding + RL-Optimized Routing", 40, PAGE_H - 75, size=14, color=ACCENT_BLUE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_BLUE)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "network_topology.png"), 40, 90, w=PAGE_W - 80, h=PAGE_H - 195)

draw_footer(c, citations="[A2] topology.py (241-node graph with BFS)  \u00b7  [A1] rl_agent.py (RL routing on graph)")
c.showPage()


# ================================================================
# PAGE 11 — Optical Communications
# ================================================================
print("Creating Page 11: Optical Communications...")
draw_bg(c)
draw_text(c, "OPTICAL COMMUNICATIONS", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "1550 nm Laser \u2014 10\u2013100\u00d7 Capability Over RF", 40, PAGE_H - 75, size=14, color=ACCENT_ORANGE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_ORANGE)

stat_cards = [
    ("200 Mbps", "Peak Data Rate", "At perihelion (54.6M km)", ACCENT_ORANGE),
    ("1550 nm", "Wavelength", "Telecom heritage lasers", ACCENT_BLUE),
    ("33\u00d7", "vs Current RF", "MRO peak: 6 Mbps", GREEN),
]
for i, (val, title, desc, col) in enumerate(stat_cards):
    x = 40 + 280 * i
    draw_card(c, x, PAGE_H - 195, 265, 90, col)
    draw_text(c, val, x + 15, PAGE_H - 125, size=20, color=col, bold=True)
    draw_text(c, title, x + 15, PAGE_H - 148, size=11, color=WHITE, bold=True)
    draw_text(c, desc, x + 15, PAGE_H - 165, size=9, color=MED_GRAY)

draw_text(c, "KEY EQUATIONS  (CCSDS 141.0-B-1 [5])", 40, PAGE_H - 220, size=12, color=ACCENT_CYAN, bold=True)
eqs = [
    "FSPL = (4\u03c0d/\u03bb)\u00b2          Free-Space Path Loss [5]",
    "G = (\u03c0D/\u03bb)\u00b2             Antenna Gain",
    "Pr = Pt \u00b7 Gt \u00b7 Gr / FSPL   Received Power [A4]",
]
for i, eq in enumerate(eqs):
    draw_text(c, eq, 40, PAGE_H - 248 - 18 * i, size=10, color=LIGHT_GRAY)

config_data = [
    ["Parameter", "Value", "Rationale"],
    ["TX Power", "5 W (37 dBm)", "Space-qualified laser"],
    ["TX Aperture", "22 cm", "Mars orbiter class"],
    ["RX Aperture", "1.0 m", "DSN-scale telescope"],
    ["Wavelength", "1550 nm", "Telecom heritage"],
    ["Efficiency", "0.55", "Conservative estimate"],
]
draw_table(c, config_data, 40, PAGE_H - 310, [100, 100, 140], ACCENT_ORANGE)

draw_footer(c, 11, citations="[5] CCSDS 141.0-B-1 (optical link)  \u00b7  [A4] AETHERIX link_budget.py  \u00b7  [1] NASA MRO (6 Mbps RF baseline)")
c.showPage()


# ================================================================
# PAGE 12 — Data Rate vs Distance Chart
# ================================================================
print("Creating Page 12: Data Rate vs Distance...")
draw_chart_page(c, "data_rate_vs_distance.png", "DATA RATE VS DISTANCE", "1550 nm Optical Link Performance", "200 Mbps at closest approach to 2 Mbps at maximum distance \u00b7 10\u2013100\u00d7 capability over RF [1]", ACCENT_ORANGE, citations="[5] CCSDS 141.0-B-1  \u00b7  [A4] AETHERIX link_budget.py (physics-derived capability)")


# ================================================================
# PAGE 13 — Earth-Mars Journey
# ================================================================
print("Creating Page 13: Earth-Mars Journey...")
draw_bg(c)
draw_text(c, "EARTH\u2013MARS DATA JOURNEY", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "7 Hops from Perseverance Rover to Mission Control", 40, PAGE_H - 75, size=14, color=ACCENT_ORANGE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_ORANGE)

journey_data = [
    ["Hop", "From", "To", "Link", "Time"],
    ["1", "Perseverance", "MRS-Alpha", "UHF", "~5s"],
    ["2", "MRS-Alpha", "MRS-Polar", "Optical ISL", "~1s"],
    ["3", "MRS-Polar", "ES-L5", "1550nm laser", "~12.5 min"],
    ["4", "ES-L5", "ES-L4", "Optical ISL", "~2s"],
    ["5", "ES-L4", "LEO Constellation", "1550nm laser", "~0.1s"],
    ["6", "LEO Constellation", "DSN Madrid", "Fiber downlink", "~1s"],
    ["7", "DSN Madrid", "JPL MOC", "Terrestrial fiber", "~0.5s"],
]
draw_table(c, journey_data, 40, PAGE_H - 100, [40, 110, 110, 90, 70], ACCENT_ORANGE)

metric_cards = [
    ("~13 min", "Total Transfer [3]", GREEN),
    ("98.7%", "Delivery (target)", ACCENT_BLUE),
    ("15 Mbps", "Throughput (target)", ACCENT_CYAN),
    ("7 hops", "Path Length [A2]", ACCENT_ORANGE),
]
for i, (val, label, col) in enumerate(metric_cards):
    x = 40 + 208 * i
    draw_card(c, x, PAGE_H - 310, 196, 55, col)
    draw_text(c, val, x + 98, PAGE_H - 272, size=16, color=col, bold=True, align="center")
    draw_text(c, label, x + 98, PAGE_H - 290, size=10, color=LIGHT_GRAY, align="center")

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "earth_mars_journey.png"), 40, 86, w=820, h=192)

draw_footer(c, 13, citations="[A2] topology.py (7-hop path)  \u00b7  [3] JPL Horizons (light-time)  \u00b7  delivery/throughput are design targets")
c.showPage()


# ================================================================
# PAGE 14 — RL Routing
# ================================================================
print("Creating Page 14: RL Routing...")
draw_bg(c)
draw_text(c, "RL-BASED ROUTING \u2014 AI INNOVATION", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Multi-Agent Federated Q-Learning Replaces Static CGR", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_CYAN)

draw_card(c, 40, PAGE_H - 230, 370, 130, ACCENT_RED)
draw_text(c, "CGR LIMITATIONS", 55, PAGE_H - 115, size=12, color=ACCENT_RED, bold=True)
cgr_lines = [
    "\u2022  Static contact plan \u2014 no adaptation",
    "\u2022  Manual reconfiguration on failure",
    "\u2022  Hours to reroute after disruption",
    "\u2022  Cannot learn from network history",
    "\u2022  No energy optimization",
]
for i, line in enumerate(cgr_lines):
    draw_text(c, line, 55, PAGE_H - 138 - 16 * i, size=9, color=LIGHT_GRAY)

draw_card(c, 430, PAGE_H - 230, 430, 130, GREEN)
draw_text(c, "RL AGENT ADVANTAGES", 445, PAGE_H - 115, size=12, color=GREEN, bold=True)
rl_lines = [
    "\u2022  Adaptive routing from network state",
    "\u2022  4 actions: FORWARD, STORE, DROP, SPLIT",
    "\u2022  R = \u03b1\u00b7del \u2212 \u03b2\u00b7delay \u2212 \u03b3\u00b7hops \u2212 \u03b4\u00b7drop \u2212 \u03b5\u00b7energy [A1]",
    "\u2022  Weights: \u03b1=1.0, \u03b4=10.0, \u03b5-greedy \u03b5-decay 0.995 [A1]",
    "\u2022  Federated learning across agents",
]
for i, line in enumerate(rl_lines):
    draw_text(c, line, 445, PAGE_H - 138 - 16 * i, size=9, color=LIGHT_GRAY)

result_cards = [
    ("713/800", "Forward Decisions [A3]", "Training run (Module 3)", GREEN),
    ("seconds", "Recovery vs hours", "Qualitative: auto vs manual [A1]", ACCENT_CYAN),
    ("Q-table", "Inspectable Policy", "Every Q-value human-auditable [A1]", ACCENT_ORANGE),
]
for i, (val, title, desc, col) in enumerate(result_cards):
    x = 40 + 280 * i
    draw_card(c, x, PAGE_H - 370, 265, 110, col)
    draw_text(c, val, x + 15, PAGE_H - 285, size=22, color=col, bold=True)
    draw_text(c, title, x + 15, PAGE_H - 308, size=12, color=WHITE, bold=True)
    draw_text(c, desc, x + 15, PAGE_H - 325, size=9, color=MED_GRAY)

draw_footer(c, 14, citations="[A1] rl_agent.py (reward fn, \u03b5-decay 0.995)  \u00b7  [A3] run_simulation Module 3 (training convergence 713/800)")
c.showPage()


# ================================================================
# PAGE 15 — RL Routing Heatmap Chart
# ================================================================
print("Creating Page 15: RL Routing Heatmap...")
draw_chart_page(c, "rl_routing_heatmap.png", "RL ROUTING Q-VALUE HEATMAP", "Convergence of Optimal Routing Decisions", "Warm colors = high-value actions \u00b7 Cool colors = poor choices the agent avoids [A1]", ACCENT_CYAN, citations="[A1] rl_agent.py  \u00b7  [A3] run_simulation Module 3 (training)")


# ================================================================
# PAGE 16 — Quantum Security
# ================================================================
print("Creating Page 16: Quantum Security...")
draw_bg(c)
draw_text(c, "QUANTUM SECURITY \u2014 FUTURE-PROOF", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "BB84/E91 QKD + Multi-Hop Repeaters + CASCADE", 40, PAGE_H - 75, size=14, color=ACCENT_PURPLE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_PURPLE)

draw_card(c, 40, PAGE_H - 250, 420, 150, ACCENT_CYAN)
draw_text(c, "BB84 PROTOCOL STEPS", 55, PAGE_H - 115, size=12, color=ACCENT_CYAN, bold=True)
bb84_steps = [
    "1. Alice sends qubits in random bases (rectilinear/diagonal)",
    "2. Bob measures each qubit in random basis",
    "3. Public reconciliation of basis choices (~50% retained)",
    "4. QBER estimation: < 11% = SECURE [15], \u2265 11% = ABORT",
    "5. CASCADE error reconciliation",
    "6. Privacy amplification via universal hashing",
    "7. Final shared secret key",
]
for i, step in enumerate(bb84_steps):
    draw_text(c, step, 55, PAGE_H - 140 - 17 * i, size=9, color=LIGHT_GRAY)

deploy_data = [
    ["Phase", "Segment", "Protocol", "Range"],
    ["Phase 1", "Earth \u2194 Orbit", "BB84 direct", "36,000 km"],
    ["Phase 2", "Earth \u2194 Lagrange", "1 repeater", "1.5M km"],
    ["Phase 3", "Earth \u2194 Mars", "3-hop chain", "225M km"],
]
draw_table(c, deploy_data, 480, PAGE_H - 100, [70, 120, 100, 80], ACCENT_PURPLE)

draw_card(c, 480, PAGE_H - 300, 380, 100, GREEN)
draw_text(c, "POST-QUANTUM CRYPTO (PQC)", 495, PAGE_H - 215, size=11, color=GREEN, bold=True)
draw_text(c, "Kyber (ML-KEM, FIPS 203) \u2014 Key encapsulation [16]", 495, PAGE_H - 238, size=10, color=LIGHT_GRAY)
draw_text(c, "Dilithium (ML-DSA, FIPS 204) \u2014 Digital signatures [17]", 495, PAGE_H - 255, size=10, color=LIGHT_GRAY)
draw_text(c, "Hybrid: QKD + PQC for defense in depth", 495, PAGE_H - 272, size=9, color=MED_GRAY)

draw_footer(c, 16, citations="[13] Bennett-Brassard 1984 BB84  \u00b7  [14] Ekert 1991 E91  \u00b7  [15] Shor-Preskill 2000 (QBER<11%)  \u00b7  [16][17] NIST FIPS 203/204  \u00b7  [A5] qkd.py")
c.showPage()


# ================================================================
# PAGE 17 — QKD Security Chart
# ================================================================
print("Creating Page 17: QKD Security Chart...")
draw_chart_page(c, "qkd_security.png", "QKD SECURITY ANALYSIS", "QBER vs Eavesdropper Detection", "QBER < 11% threshold ensures security [15] \u00b7 Any eavesdropping attempt is detected [13]", ACCENT_PURPLE, citations="[15] Shor-Preskill 2000 (11% threshold)  \u00b7  [13] BB84  \u00b7  [A5] AETHERIX qkd.py")


# ================================================================
# PAGE 18 — Orbital Mechanics
# ================================================================
print("Creating Page 18: Orbital Mechanics...")
draw_bg(c)
draw_text(c, "ORBITAL MECHANICS & CONTACT WINDOWS", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "780-Day Synodic Period \u2014 From Opposition to Conjunction", 40, PAGE_H - 75, size=14, color=ACCENT_BLUE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_BLUE)

params_data = [
    ["Parameter", "Value"],
    ["Semi-major axis", "1.524 AU (227.9M km)"],
    ["Orbital period", "686.98 days"],
    ["Synodic period", "779.94 days"],
    ["Min distance", "54.6M km (perihelion)"],
    ["Max distance", "401M km (aphelion)"],
    ["Eccentricity", "0.0934"],
]
draw_table(c, params_data, 40, PAGE_H - 100, [120, 160], ACCENT_BLUE)

windows_data = [
    ["Window", "Availability", "Duration", "Data Rate"],
    ["Optimal (opposition)", "99%", "8\u201312 hrs", "100\u2013200 Mbps"],
    ["Good", "95%", "6\u20138 hrs", "20\u2013100 Mbps"],
    ["Fair", "85%", "2\u20134 hrs", "5\u201320 Mbps"],
    ["Poor (aphelion)", "50%", "0\u20132 hrs", "1\u20135 Mbps"],
    ["Blackout (conjunction)", "0%", "N/A", "Lagrange relay only"],
]
draw_table(c, windows_data, 340, PAGE_H - 100, [130, 80, 80, 120], ACCENT_ORANGE)

draw_footer(c, 18, citations="[3] JPL Horizons (orbital ephemeris: synodic 779.94 d, 54.6M\u2013401M km)  \u00b7  [A2] topology.py  \u00b7  [A4] link_budget.py (windows)")
c.showPage()


# ================================================================
# PAGE — Radiation-Hardened Computing (Learning Objective e)
# ================================================================
print("Creating slide: Radiation-Hardened Computing...")
draw_bg(c)
draw_text(c, "RADIATION-HARDENED COMPUTING", 40, PAGE_H - 50, size=26, color=WHITE, bold=True)
draw_text(c, "Surviving the Space Radiation Environment (LO-e)", 40, PAGE_H - 75, size=14, color=ACCENT_ORANGE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_ORANGE)

eff_data = [
    ["Effect", "What it does", "Mitigation"],
    ["SEU (Single Event Upset)", "Bit flip in memory/register", "SECDED ECC"],
    ["MBU (Multiple Bit Upset)", "\u22652 adjacent bits flipped", "Bit interleaving"],
    ["SEL (Single Event Latchup)", "Parasitic short \u2014 destructive", "Current limit + cycle"],
    ["TID (Total Ionizing Dose)", "Cumulative degradation (krad)", "Rad-hard (RAD750) [18]"],
]
draw_table(c, eff_data, 40, PAGE_H - 105, [138, 158, 134], ACCENT_ORANGE)

draw_card(c, 480, PAGE_H - 210, 380, 105, ACCENT_RED)
draw_text(c, "DEFENSE-IN-DEPTH STACK", 495, PAGE_H - 122, size=12, color=ACCENT_RED, bold=True)
def_lines = [
    "1. TMR \u2014 3 replicas + majority voter masks single fault",
    "2. SECDED (39,32) ECC \u2014 corrects 1, detects 2 (21.9% OH)",
    "3. Memory scrubbing \u2014 rewrites before 2nd upset (Poisson race)",
    "4. FDIR + watchdog \u2014 detect \u2192 isolate \u2192 reload golden image",
    "5. SAFE-MODE after recovery budget exhausted",
]
for i, line in enumerate(def_lines):
    draw_text(c, line, 495, PAGE_H - 143 - 13 * i, size=9, color=LIGHT_GRAY)

draw_text(c, "DEMONSTRATED (run_simulation Module 6 [A6])", 40, PAGE_H - 230, size=12, color=GREEN, bold=True)
rad_cards = [
    ("37,159", "Raw upsets (210-day cruise)", ACCENT_ORANGE),
    ("200\u00d7", "Protection factor", GREEN),
    ("3,334\u00d7", "TMR gain (@ p=1e-4)", ACCENT_BLUE),
    ("2,127\u00d7", "RAD750 TID margin", ACCENT_PURPLE),
]
for i, (val, label, col) in enumerate(rad_cards):
    x = 40 + 210 * i
    draw_card(c, x, PAGE_H - 330, 195, 75, col)
    draw_text(c, val, x + 97, PAGE_H - 268, size=18, color=col, bold=True, align="center")
    draw_text(c, label, x + 97, PAGE_H - 290, size=9, color=LIGHT_GRAY, align="center")

draw_card(c, 40, PAGE_H - 430, 820, 60, ACCENT_CYAN)
draw_text(c, "HERITAGE: NASA RAD750 (Curiosity, Perseverance C&DH) [18]  \u00b7  ESA LEON3FT / GR712RC [19]  \u00b7  Code: src/computing/radiation.py [A6]", 55, PAGE_H - 385, size=10, color=ACCENT_CYAN, bold=True)
draw_text(c, "Result above: ~186 uncorrectable residuals vs 37,159 raw upsets over a 512 Mbit interplanetary cruise \u2014 ~0.9/day residual.", 55, PAGE_H - 402, size=9, color=LIGHT_GRAY)

draw_footer(c, citations="[A6] AETHERIX radiation.py (demonstrated Module 6)  \u00b7  [18] BAE RAD750  \u00b7  [19] ESA LEON3FT")
c.showPage()


# ================================================================
# PAGE — Mission-Critical Data Prioritization (Learning Objective f)
# ================================================================
print("Creating slide: Data Prioritization...")
draw_bg(c)
draw_text(c, "MISSION-CRITICAL DATA PRIORITIZATION", 40, PAGE_H - 50, size=24, color=WHITE, bold=True)
draw_text(c, "Bandwidth Triage on a Starved, Intermittent Link (LO-f)", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_CYAN)

pri_data = [
    ["Tier", "Class", "Examples", "BPv7 Priority"],
    ["P0", "Emergency / Safety", "Health, collision avoidance, faults", "EMERGENCY"],
    ["P1", "Mission-critical", "Command ACKs, time-sensitive science", "HIGH_SCIENCE"],
    ["P2", "High-priority", "Routine telemetry, scheduled science", "STANDARD"],
    ["P4", "Low / Bulk", "Housekeeping, file transfers, SW images", "BULK"],
]
draw_table(c, pri_data, 40, PAGE_H - 105, [45, 110, 180, 110], ACCENT_CYAN)

draw_text(c, "THREE LEVERS", 480, PAGE_H - 105, size=12, color=ACCENT_ORANGE, bold=True)
lever_lines = [
    "1. Compression (pre-transmit) [7][8]:",
    "   \u2022  Telemetry \u2192 CCSDS 121.0-B-3 (Rice) \u2248 3\u00d7 [7]",
    "   \u2022  Imagery \u2192 CCSDS 122.0-B-2 (wavelet) \u2248 10\u00d7 [8]",
    "2. Deadline-aware preemptive QoS [A7]:",
    "   strict priority \u2192 earliest deadline; defer if infeasible",
    "3. BPv7 fragmentation [9]:",
    "   send what fits this contact; defer the rest; link never idle",
]
for i, line in enumerate(lever_lines):
    draw_text(c, line, 480, PAGE_H - 128 - 16 * i, size=9, color=LIGHT_GRAY)

draw_text(c, "DEMONSTRATED SCENARIO (src/routing/prioritization.py [A7])", 40, PAGE_H - 280, size=12, color=GREEN, bold=True)
prio_cards = [
    ("5/6", "Items delivered (strict priority)", GREEN),
    ("100%", "Link utilisation (target)", ACCENT_CYAN),
    ("41%", "SW update fragmented (remainder deferred)", ACCENT_ORANGE),
    ("P0", "Emergency preempts to direct-to-Earth backup", ACCENT_RED),
]
for i, (val, label, col) in enumerate(prio_cards):
    x = 40 + 210 * i
    draw_card(c, x, PAGE_H - 380, 195, 80, col)
    draw_text(c, val, x + 97, PAGE_H - 318, size=16, color=col, bold=True, align="center")
    draw_text(c, label, x + 97, PAGE_H - 348, size=8, color=LIGHT_GRAY, align="center")

draw_footer(c, citations="[A7] AETHERIX prioritization.py  \u00b7  [7] CCSDS 121.0-B-3 lossless  \u00b7  [8] CCSDS 122.0-B-2 wavelet  \u00b7  [9] RFC 9171 (fragmentation)")
c.showPage()


# ================================================================
# PAGE 19 — Data Flow Diagram Visual
# ================================================================
print("Creating Page 19: Data Flow Diagram Visual...")
draw_bg(c)
draw_text(c, "DATA FLOW DIAGRAM", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Complete Data Path from Mars Surface to Earth Control", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 200, ACCENT_CYAN)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "data_flow.png"), 40, 90, w=PAGE_W - 80, h=PAGE_H - 195)

draw_footer(c, 19, citations="[A2] topology.py (full data path Mars\u2192Earth)")
c.showPage()


# ================================================================
# PAGE — Protocol Stack Diagram
# ================================================================
print("Creating Page: Protocol Stack Diagram...")
draw_bg(c)
draw_text(c, "PROTOCOL STACK", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "BPv7 + Three Convergence Layers \u2014 Standards-Compliant", 40, PAGE_H - 75, size=14, color=ACCENT_BLUE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_BLUE)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "protocol_stack.png"), 40, 90, w=PAGE_W - 80, h=PAGE_H - 195)

draw_footer(c, citations="[9] RFC 9171 (BPv7)  \u00b7  [10] RFC 5326 (LTP)  \u00b7  [11] RFC 7242 (TCPCL)  \u00b7  [A6] bundle.py")
c.showPage()


# ================================================================
# PAGE 20 — Performance
# ================================================================
print("Creating Page 20: Performance...")
draw_bg(c)
draw_text(c, "AETHERIX vs CURRENT SYSTEMS", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Head-to-Head Performance Comparison", 40, PAGE_H - 75, size=14, color=GREEN)
draw_accent_line(c, 40, PAGE_H - 85, 180, GREEN)

comp_data = [
    ["Metric", "Current (MRO) [1]", "AETHERIX [A4]", "Note"],
    ["Downlink rate", "0.5\u20136 Mbps", "2\u2013200 Mbps", "10\u2013100\u00d7 capability"],
    ["Daily volume", "5\u201310 GB", "50\u2013100 GB", "Est. (link-driven)"],
    ["Availability", "60\u201375%", ">95%", "Design target"],
    ["Routing", "Static (CGR)", "RL-adaptive", "Adaptive [A1]"],
    ["Security", "AES-256", "QKD + PQC", "Future-proof [16][17]"],
    ["Scalability", "5\u201310 assets", "241 nodes", "10\u2013100\u00d7 [A2]"],
    ["Conjunction", "Blackout", "50\u201370% via L4/L5", "+50\u201370% [A8]"],
    ["Recovery time", "Manual (hours)", "Auto (seconds)", "Auto [A1]"],
]
draw_table(c, comp_data, 40, PAGE_H - 100, [100, 100, 120, 110], GREEN)

draw_footer(c, 20, citations="[1] NASA MRO (0.5\u20136 Mbps)  \u00b7  [A4] link_budget.py (2\u2013200 Mbps capability)  \u00b7  [A2] topology.py  \u00b7  [A8] Module 4 conjunction  \u00b7  targets clearly labelled")
c.showPage()


# ================================================================
# PAGE 21 — Performance Comparison Chart
# ================================================================
print("Creating Page 21: Performance Comparison Chart...")
draw_chart_page(c, "performance_comparison.png", "AETHERIX vs CURRENT SYSTEMS", "Head-to-Head Performance Metrics", "10\u2013100\u00d7 data-rate capability (link budget [A4] vs [1]) \u00b7 availability/routing are design targets", GREEN, citations="[1] NASA MRO  \u00b7  [A4] AETHERIX link_budget.py  \u00b7  [A2] topology.py")


# ================================================================
# PAGE — Trade-off Analysis (Examiner gap analysis)
# ================================================================
print("Creating slide: Trade-off Analysis...")
draw_bg(c)
draw_text(c, "TRADE-OFF ANALYSIS \u2014 WHY THESE CHOICES", 40, PAGE_H - 50, size=24, color=WHITE, bold=True)
draw_text(c, "Every Decision Traded Performance for Auditability & Reproducibility", 40, PAGE_H - 75, size=13, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_CYAN)

trade_data = [
    ["Decision", "Choice", "Rationale (vs alternative)"],
    ["Optical vs RF", "Hybrid: 1550 nm primary + Ka-band fallback [4]", "10\u2013100\u00d7 throughput [A4]; RF survives clouds & corona"],
    ["Routing", "Custom Q-learning, not ION-DTN CGR [A1]", "Adapts to live state; CGR re-plans on 12-min-stale schedule"],
    ["RL model", "Q-tables now, DQN later (Phase 6)", "Every Q-value human-auditable; trains in seconds"],
    ["State space", "Discretised, 241 nodes [A2]", "Right-sized for a tabular policy; DQN path documented"],
    ["Reward weights", "\u03b1=1.0, \u03b4=10.0, \u03b5-decay 0.995 [A1]", "Drop penalty 10\u00d7 delivery to forbid bundle loss"],
]
draw_table(c, trade_data, 40, PAGE_H - 105, [110, 250, 320], ACCENT_CYAN)

draw_card(c, 40, PAGE_H - 320, 820, 70, GREEN)
draw_text(c, "BOTTOM LINE", 55, PAGE_H - 270, size=12, color=GREEN, bold=True)
draw_text(c, "Each choice sacrifices maximum theoretical performance for auditability and reproducibility \u2014 exactly what a defence and", 55, PAGE_H - 290, size=10, color=LIGHT_GRAY)
draw_text(c, "a research artefact require. DQN / ns-3 / ION-DTN are the documented production transition (Phases 7\u20139).", 55, PAGE_H - 306, size=10, color=LIGHT_GRAY)

draw_text(c, "DSOC heritage: NASA flew optical + RF side-by-side on Psyche [4] \u2014 AETHERIX mirrors that hybrid model.", 40, PAGE_H - 360, size=10, color=ACCENT_ORANGE, bold=True)

draw_footer(c, citations="[A1] rl_agent.py / training.py  \u00b7  [A4] link_budget.py  \u00b7  [4] NASA DSOC (Psyche)  \u00b7  [A2] topology.py")
c.showPage()


# ================================================================
# PAGE — Failure & Recovery (Examiner gap analysis)
# ================================================================
print("Creating slide: Failure & Recovery...")
draw_bg(c)
draw_text(c, "FAILURE & RECOVERY", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Autonomous Solar-Conjunction Link-Blackout Survival", 40, PAGE_H - 75, size=14, color=ACCENT_RED)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_RED)

draw_text(c, "SCENARIO: Earth\u2013Sun\u2013Mars conjunction \u2014 solar corona collapses the 1550 nm link below the 0.3 forward threshold [A1]", 40, PAGE_H - 108, size=10, color=LIGHT_GRAY)

path_data = [
    ["Path", "Band", "Link Quality", "Status", "Reward [A8]"],
    ["Direct Mars \u2192 Earth", "1550 nm optical", "0.05", "CLOSED", "\u22121.438"],
    ["Mars \u2192 ES-L4 \u2192 Earth", "Ka-band RF", "0.65", "OPEN", "\u22120.201"],
    ["Mars \u2192 ES-L5 \u2192 Earth", "Ka-band RF", "0.60", "OPEN", "\u22120.201"],
]
draw_table(c, path_data, 40, PAGE_H - 130, [170, 110, 90, 70, 80], ACCENT_RED)

draw_card(c, 40, PAGE_H - 300, 410, 150, ACCENT_CYAN)
draw_text(c, "HOW AETHERIX RECOVERS (automatically)", 55, PAGE_H - 165, size=11, color=ACCENT_CYAN, bold=True)
rec_lines = [
    "1. Detect \u2014 optical Q-value collapses (q<0.3 \u2192 no reward)",
    "2. Re-route \u2014 agent in exploit mode picks highest-Q:",
    "   ES-L4 (Ka-band RF), 60\u00b0 solar elongation, avoids corona",
    "3. Prioritise \u2014 policy engine fires two rules:",
    "   P0 EMERGENCY \u2192 forward on best (Ka-band) link",
    "   P4 BULK \u2192 store locally, defer past conjunction",
]
for i, line in enumerate(rec_lines):
    draw_text(c, line, 55, PAGE_H - 188 - 17 * i, size=9, color=LIGHT_GRAY)

draw_card(c, 480, PAGE_H - 300, 380, 150, ACCENT_PURPLE)
draw_text(c, "WHY LAGRANGE RELAYS [3][A2]", 495, PAGE_H - 165, size=11, color=ACCENT_PURPLE, bold=True)
lag_lines = [
    "ES-L4 / ES-L5 sit 60\u00b0 ahead/behind Earth in its orbit.",
    "At that separation they keep line-of-sight to Mars",
    "around the solar limb even at true conjunction.",
    "Direct Earth\u2013Mars link: 0% availability at conjunction.",
    "Via ES-L4/L5: 50\u201370% availability retained [A8].",
    "No Mars-orbit relay can solve this \u2014 geometry is Earth-side.",
]
for i, line in enumerate(lag_lines):
    draw_text(c, line, 495, PAGE_H - 188 - 16 * i, size=9, color=LIGHT_GRAY)

draw_text(c, "Outcome: throughput drops (optical\u2192RF) but no mission-critical data lost. Run live: python run_simulation.py --module 4", 40, PAGE_H - 360, size=10, color=GREEN, bold=True)

draw_footer(c, citations="[A8] run_simulation Module 4 (rewards \u22121.438 / \u22120.201)  \u00b7  [A1] rl_agent.py (0.3 threshold)  \u00b7  [3] JPL Horizons (Lagrange geometry)  \u00b7  [A2] topology.py")
c.showPage()


# ================================================================
# PAGE 22 — Implementation
# ================================================================
print("Creating Page 22: Implementation...")
draw_bg(c)
draw_text(c, "IMPLEMENTATION", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "25 Modules, 480 Tests, Full Python Stack", 40, PAGE_H - 75, size=14, color=ACCENT_BLUE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_BLUE)

impl_cards = [
    ("25", "Source Modules", ACCENT_BLUE),
    ("480", "Unit Tests", GREEN),
    ("241", "Network Nodes", ACCENT_ORANGE),
    ("12", "Interactive Demos", ACCENT_PURPLE),
]
for i, (val, label, col) in enumerate(impl_cards):
    x = 40 + 208 * i
    draw_card(c, x, PAGE_H - 180, 196, 75, col)
    draw_text(c, val, x + 98, PAGE_H - 128, size=24, color=col, bold=True, align="center")
    draw_text(c, label, x + 98, PAGE_H - 150, size=11, color=LIGHT_GRAY, align="center")

draw_text(c, "CORE MODULES", 40, PAGE_H - 205, size=13, color=ACCENT_CYAN, bold=True)
modules = [
    "link_budget.py \u2014 Optical/RF link analysis",
    "rl_agent.py \u2014 Q-learning routing agent",
    "bundle.py \u2014 BPv7 bundle protocol",
    "forwarding_engine.py \u2014 Store-and-forward",
    "qkd.py \u2014 BB84/E91 protocols",
    "contact_windows.py \u2014 Orbital mechanics",
    "topology.py \u2014 5-tier network (241 nodes)",
    "simulator.py \u2014 End-to-end simulation",
    "ltp.py \u2014 Licklider Transmission Protocol",
    "tcpcl.py \u2014 TCP Convergence Layer",
]
for i, mod in enumerate(modules):
    draw_text(c, f"\u2022  {mod}", 40, PAGE_H - 230 - 17 * i, size=9, color=LIGHT_GRAY)

std_data = [
    ["Standard", "Title", "Status"],
    ["RFC 9171 [9]", "Bundle Protocol v7", "Compliant"],
    ["RFC 4838 [12]", "DTN Architecture", "Compliant"],
    ["CCSDS 734.2-B-1 [2]", "CCSDS Bundle Protocol", "Compliant"],
    ["CCSDS 734.3-B-1", "SABR / contact routing", "Baseline"],
    ["CCSDS 141.0-B-1 [5]", "Optical Comm Physical", "Compliant"],
    ["RFC 9172", "BPSec (security)", "Referenced"],
    ["RFC 5326 [10]", "LTP (deep space)", "Compliant"],
    ["RFC 7242 [11]", "TCPCL (Earth)", "Compliant"],
]
draw_table(c, std_data, 480, PAGE_H - 210, [100, 140, 70], ACCENT_BLUE)

draw_footer(c, 22, citations="[9][10][11][12] IETF RFCs  \u00b7  [2][5] CCSDS standards  \u00b7  [A1]\u2013[A8] AETHERIX modules (github.com/matx104/AETHERIX)")
c.showPage()


# ================================================================
# PAGE 23 — Roadmap
# ================================================================
print("Creating Page 23: Roadmap...")
draw_bg(c)
draw_text(c, "ROADMAP & FUTURE WORK", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "From Proof-of-Concept to Production Deployment", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_CYAN)

phases = [
    ("Phase 1\u20132", "Foundation", "Topology + BPv7 + Convergence Layers", GREEN, "Complete"),
    ("Phase 3", "Intelligence", "RL Routing (Federated Q-learning)", GREEN, "Complete"),
    ("Phase 4", "Security", "QKD + Multi-hop Repeaters + CASCADE", GREEN, "Complete"),
    ("Phase 5\u20136", "Simulation", "Full Engine + Web Platform + Demos", GREEN, "Complete"),
]
for i, (phase, title, desc, col, status) in enumerate(phases):
    y = PAGE_H - 130 - 65 * i
    draw_card(c, 40, y - 45, 420, 55, col)
    draw_text(c, f"{phase}: {title}", 55, y - 5, size=13, color=col, bold=True)
    draw_text(c, desc, 55, y - 22, size=10, color=LIGHT_GRAY)
    draw_text(c, status, 448, y - 10, size=10, color=GREEN, bold=True, align="right")

future_data = [
    ["Phase", "Focus", "Technology", "Status"],
    ["7", "DQN Upgrade", "Deep Q-Network", "Remaining"],
    ["8", "HIL Simulation", "ns-3 integration", "Remaining"],
    ["9", "ION-DTN", "Production DTN stack", "Remaining"],
    ["10", "Flight Demo", "LEO optical test", "Future"],
    ["11", "Mars Deploy", "Full 5-tier network", "Future"],
]
draw_table(c, future_data, 480, PAGE_H - 100, [50, 100, 130, 70], ACCENT_ORANGE)

draw_footer(c, 23, citations="[A1]\u2013[A8] AETHERIX source modules  \u00b7  [4] NASA DSOC (Psyche) heritage for optical  \u00b7  DQN/ns-3/ION-DTN on production roadmap")
c.showPage()


# ================================================================
# PAGE 24 — Conclusion
# ================================================================
print("Creating Page 24: Conclusion...")
draw_bg(c)
draw_text(c, "CONCLUSION \u2014 AETHERIX DELIVERS", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Bridging the Interplanetary Communication Gap", 40, PAGE_H - 75, size=14, color=GREEN)
draw_accent_line(c, 40, PAGE_H - 85, 180, GREEN)

draw_card(c, 40, PAGE_H - 230, 400, 130, ACCENT_RED)
draw_text(c, "THE PROBLEM", 55, PAGE_H - 115, size=14, color=ACCENT_RED, bold=True)
problem_lines = [
    "\u2022  54.6\u2013401M km Earth-Mars distance [3]",
    "\u2022  3\u201322 min one-way light delay [3]",
    "\u2022  TCP/IP fundamentally broken in space [12]",
    "\u2022  Current RF: only 0.5\u20136 Mbps [1]",
    "\u2022  2-week solar conjunction blackouts [3]",
]
for i, line in enumerate(problem_lines):
    draw_text(c, line, 55, PAGE_H - 140 - 17 * i, size=10, color=LIGHT_GRAY)

draw_card(c, 460, PAGE_H - 230, 400, 130, GREEN)
draw_text(c, "THE SOLUTION", 475, PAGE_H - 115, size=14, color=GREEN, bold=True)
solution_lines = [
    "\u2022  BPv7 DTN: store-and-forward works [9]",
    "\u2022  RL routing: adaptive, auditable policy [A1]",
    "\u2022  Optical: 10\u2013100\u00d7 data-rate capability [A4]",
    "\u2022  QKD: future-proof quantum security [13][15]",
    "\u2022  Lagrange relays: conjunction coverage [A8]",
]
for i, line in enumerate(solution_lines):
    draw_text(c, line, 475, PAGE_H - 140 - 17 * i, size=10, color=LIGHT_GRAY)

stat_cards = [
    ("10\u2013100\u00d7", "Target Speedup \u2666", ACCENT_BLUE),
    (">95%", "Availability (target)", GREEN),
    ("AI-Driven", "Routing", ACCENT_CYAN),
    ("Quantum", "Security", ACCENT_PURPLE),
]
for i, (val, label, col) in enumerate(stat_cards):
    x = 40 + 210 * i
    draw_card(c, x, PAGE_H - 400, 200, 80, col)
    draw_text(c, val, x + 100, PAGE_H - 340, size=20, color=col, bold=True, align="center")
    draw_text(c, label, x + 100, PAGE_H - 362, size=12, color=WHITE, bold=True, align="center")

draw_text(c, "NOVEL CONTRIBUTIONS", 40, PAGE_H - 430, size=13, color=ACCENT_CYAN, bold=True)
contrib = "RL autonomous routing (auditable Q-table) [A1] | 5-tier DTN (241 nodes) [A2] | Optical/RF hybrid (10-100x capability) [A4] | Quantum links (future-proof) [A5] | Full simulation (480 tests)"
draw_text(c, contrib, 40, PAGE_H - 450, size=10, color=LIGHT_GRAY)

draw_footer(c, 24, citations="[1] NASA  \u00b7  [3] JPL Horizons  \u00b7  [9][12] IETF  \u00b7  [13][15] QKD  \u00b7  [A1][A2][A4][A5][A8] AETHERIX")
c.showPage()


# ================================================================
# PAGE — References (Industry & Scientific Sources)
# ================================================================
print("Creating slide: References (Industry)...")
draw_bg(c)
draw_text(c, "REFERENCES", 40, PAGE_H - 50, size=26, color=WHITE, bold=True)
draw_text(c, "Industry & Scientific Sources [1]\u2013[20]  \u00b7  Three-layer attribution: [N] industry \u00b7 [AN] this project", 40, PAGE_H - 73, size=11, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 83, 180, ACCENT_CYAN)

refs_left = [
    "[1] NASA JPL, \u201cMars Relay Network User's Guide,\u201d 2024. jpl.nasa.gov/marsrelay",
    "[2] CCSDS, \u201cBundle Protocol Spec.,\u201d 734.2-B-1, 2021. public.ccsds.org",
    "[3] JPL Horizons, \u201cEarth\u2013Mars Ephemeris,\u201d 2025. ssd.jpl.nasa.gov/horizons",
    "[4] NASA, \u201cDeep Space Optical Comm. (DSOC),\u201d Psyche, 2024. jpl.nasa.gov/missions/dsoc",
    "[5] CCSDS, \u201cOptical Comm. Coding & Sync.,\u201d 141.0-B-1, 2019. public.ccsds.org",
    "[6] CCSDS, \u201cTM Space Data Link Protocol,\u201d 131.0-B-3, 2017. public.ccsds.org",
    "[7] CCSDS, \u201cLossless Data Compression,\u201d 121.0-B-3, 2020. public.ccsds.org",
    "[8] CCSDS, \u201cImage Data Compression,\u201d 122.0-B-2, 2017. public.ccsds.org",
    "[9] IETF, \u201cBundle Protocol Version 7,\u201d RFC 9171, 2022. rfc-editor.org/rfc/rfc9171",
    "[10] IETF, \u201cLicklider Transmission Protocol,\u201d RFC 5326, 2008. rfc-editor.org/rfc/rfc5326",
]
refs_right = [
    "[11] IETF, \u201cDTN TCP Convergence Layer,\u201d RFC 7242, 2014. rfc-editor.org/rfc/rfc7242",
    "[12] IETF, \u201cDelay-Tolerant Networking Architecture,\u201d RFC 4838, 2007. rfc-editor.org/rfc/rfc4838",
    "[13] Bennett & Brassard, \u201cQuantum Cryptography,\u201d Proc. IEEE ICC, 1984.",
    "[14] Ekert, \u201cQuantum Cryptography Based on Bell's Theorem,\u201d PRL 67, 661, 1991.",
    "[15] Shor & Preskill, \u201cSimple Proof of Security of BB84,\u201d PRL 85, 441, 2000.",
    "[16] NIST, \u201cModule-Lattice-Based KEM,\u201d FIPS 203, 2024. csrc.nist.gov/pubs/fips/203",
    "[17] NIST, \u201cModule-Lattice-Based Digital Signature,\u201d FIPS 204, 2024. csrc.nist.gov/pubs/fips/204",
    "[18] BAE Systems, \u201cRAD750 Radiation-Hardened PowerPC,\u201d 2024. baesystems.com/rad750",
    "[19] ESA/Gaisler, \u201cLEON3FT Processor,\u201d 2023. gaisler.com/products/processors/leon3ft",
    "[20] IETF, RFC 4838 \u00a73.1, 2007 (long delay, intermittent connectivity challenges).",
]
for i, ref in enumerate(refs_left):
    draw_text(c, ref, 40, PAGE_H - 110 - 34 * i, size=8, color=LIGHT_GRAY)
for i, ref in enumerate(refs_right):
    draw_text(c, ref, 440, PAGE_H - 110 - 34 * i, size=8, color=LIGHT_GRAY)

draw_footer(c, citations="Full URLs on project site: github.com/matx104/AETHERIX  \u00b7  next slide: project sources [A1]\u2013[A8]")
c.showPage()


# ================================================================
# PAGE — References (Project Sources [A1]-[A8])
# ================================================================
print("Creating slide: References (Project)...")
draw_bg(c)
draw_text(c, "REFERENCES (cont.)", 40, PAGE_H - 50, size=26, color=WHITE, bold=True)
draw_text(c, "Project Sources [A1]\u2013[A8]  \u00b7  M. A. Tariq, AETHERIX, github.com/matx104/AETHERIX (2025)", 40, PAGE_H - 73, size=11, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 83, 180, ACCENT_CYAN)

proj_left = [
    "[A1] RL Routing Agent \u2014 src/routing/rl_agent.py",
    "[A2] Network Topology \u2014 src/orbital/topology.py",
    "[A3] End-to-End Simulation \u2014 run_simulation.py Module 3 (RL training)",
    "[A4] Optical Link Budget Calculator \u2014 src/infrastructure/link_budget.py",
]
proj_right = [
    "[A5] QKD Protocol Implementation \u2014 src/security/qkd.py",
    "[A6] Radiation Hardening Model \u2014 src/computing/radiation.py",
    "[A7] Data Prioritization Engine \u2014 src/routing/prioritization.py",
    "[A8] Failure & Recovery Simulation \u2014 run_simulation.py Module 4 (conjunction)",
]
for i, ref in enumerate(proj_left):
    draw_text(c, ref, 40, PAGE_H - 115 - 24 * i, size=9, color=LIGHT_GRAY)
for i, ref in enumerate(proj_right):
    draw_text(c, ref, 440, PAGE_H - 115 - 24 * i, size=9, color=LIGHT_GRAY)

draw_card(c, 40, PAGE_H - 290, 820, 120, ACCENT_PURPLE)
draw_text(c, "THREE-LAYER ATTRIBUTION (resolves the prior citation gap)", 55, PAGE_H - 190, size=12, color=ACCENT_PURPLE, bold=True)
attr_lines = [
    "Layer A \u2014 Industry/Scientific baseline [1]\u2013[20]: someone else's data (e.g. NASA MRO 0.5\u20136 Mbps [1]).",
    "Layer B \u2014 This project's design decision [A1]\u2013[A8]: cite the code (e.g. RL agent src/routing/rl_agent.py [A1]).",
    "Layer C \u2014 Demonstrated simulation results [A6][A8]: cite the specific run (e.g. radiation 200\u00d7 \u2014 Module 6 [A6]).",
    "Design targets (e.g. >95% availability, 2\u2013200 Mbps capability) are labelled as such, never presented as measured results.",
]
for i, line in enumerate(attr_lines):
    draw_text(c, line, 55, PAGE_H - 213 - 17 * i, size=9, color=LIGHT_GRAY)

draw_footer(c, citations="All results reproducible: python run_simulation.py  \u00b7  480 tests: python -m pytest tests/ -q  \u00b7  matx104.github.io/AETHERIX")
c.showPage()


# ================================================================
# PAGE 25 — Thank You
# ================================================================
print("Creating Page 25: Thank You...")
draw_bg(c)
draw_top_bar(c)
draw_bottom_bar(c)

draw_text(c, "THANK YOU", PAGE_W / 2, PAGE_H - 120, size=44, color=WHITE, bold=True, align="center")
draw_accent_line(c, PAGE_W / 2 - 80, PAGE_H - 140, 160, ACCENT_CYAN, 4)
draw_text(c, "Questions?", PAGE_W / 2, PAGE_H - 175, size=28, color=ACCENT_CYAN, align="center")

stat_cards = [
    ("10\u2013100\u00d7", "Faster", ACCENT_BLUE),
    (">95%", "Available (target)", GREEN),
    ("241", "Nodes", ACCENT_ORANGE),
    ("480", "Tests", ACCENT_PURPLE),
]
for i, (val, label, col) in enumerate(stat_cards):
    x = PAGE_W / 2 - 440 + 220 * i
    draw_card(c, x, PAGE_H - 290, 210, 60, col)
    draw_text(c, val, x + 105, PAGE_H - 248, size=18, color=col, bold=True, align="center")
    draw_text(c, label, x + 105, PAGE_H - 268, size=10, color=LIGHT_GRAY, align="center")

draw_text(c, "Muhammad Abdullah Tariq", PAGE_W / 2, PAGE_H - 340, size=18, color=WHITE, bold=True, align="center")
draw_text(c, "muhammad.atx@gmail.com", PAGE_W / 2, PAGE_H - 365, size=12, color=ACCENT_BLUE, align="center")

draw_card(c, PAGE_W / 2 - 200, 60, 400, 110, ACCENT_CYAN)
draw_text(c, "LIVE DEMO & RESOURCES", PAGE_W / 2, 148, size=13, color=ACCENT_CYAN, bold=True, align="center")
draw_text(c, "matx104.github.io/AETHERIX \u2014 Interactive simulations", PAGE_W / 2, 125, size=11, color=LIGHT_GRAY, align="center")
draw_text(c, "github.com/matx104/AETHERIX \u2014 Source code + documentation", PAGE_W / 2, 105, size=11, color=LIGHT_GRAY, align="center")
draw_text(c, "EduQual Level 6 Diploma in AI Operations | Topic 59 | September 2026", PAGE_W / 2, 82, size=9, color=MED_GRAY, align="center")

c.showPage()

c.save()
print(f"\n\u2713 Compact PDF saved: {pdf_path}")
print(f"  Pages: {TOTAL_SLIDES}")
