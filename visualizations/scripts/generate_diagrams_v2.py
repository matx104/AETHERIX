#!/usr/bin/env python3
"""Generate 7 polished, professional SVG+PNG diagrams for AETHERIX v2.

Outputs to docs/img/diagrams/ (overwrites existing files).
Each diagram: dark theme (#0d1117), AETHERIX color scheme, 2x PNG.
"""
import os
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'docs', 'img', 'diagrams')

BG = '#0d1117'
CYAN = '#00d4ff'
PURPLE = '#7c5cf7'
ORANGE = '#ff6b35'
GREEN = '#3fb950'
MAGENTA = '#c84cff'
GOLD = '#d29922'
RED = '#f85149'
GRAY = '#8892a4'
DGRAY = '#5a6578'

FONT = "font-family=\"'SF Mono', 'Cascadia Code', 'Fira Code', monospace\""

_CNAME = {
    CYAN: 'Cyan', PURPLE: 'Purple', ORANGE: 'Orange', GREEN: 'Green',
    MAGENTA: 'Magenta', GOLD: 'Gold', RED: 'Red', GRAY: 'Gray', DGRAY: 'Gray',
}


def _arr(color):
    return f'arr{_CNAME[color]}'


def _grad(color):
    return f'grad{_CNAME[color]}'


def svg_header(w, h, title_text, extra_defs=''):
    title_y = 28
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<rect width="{w}" height="{h}" fill="{BG}"/>
<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="2" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="glowStrong">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <linearGradient id="gradCyan" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0.03"/>
  </linearGradient>
  <linearGradient id="gradPurple" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{PURPLE}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{PURPLE}" stop-opacity="0.03"/>
  </linearGradient>
  <linearGradient id="gradOrange" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{ORANGE}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{ORANGE}" stop-opacity="0.03"/>
  </linearGradient>
  <linearGradient id="gradGreen" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{GREEN}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{GREEN}" stop-opacity="0.03"/>
  </linearGradient>
  <linearGradient id="gradMagenta" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{MAGENTA}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{MAGENTA}" stop-opacity="0.03"/>
  </linearGradient>
  <linearGradient id="gradGold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{GOLD}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{GOLD}" stop-opacity="0.03"/>
  </linearGradient>
  <linearGradient id="gradRed" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{RED}" stop-opacity="0.03"/>
  </linearGradient>
  <linearGradient id="gradMarsEarth" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{ORANGE}" stop-opacity="0.3"/>
    <stop offset="50%" stop-color="{PURPLE}" stop-opacity="0.15"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0.3"/>
  </linearGradient>
  <marker id="arrCyan" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <path d="M0,0 L10,3.5 L0,7" fill="none" stroke="{CYAN}" stroke-width="1.2"/>
  </marker>
  <marker id="arrPurple" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <path d="M0,0 L10,3.5 L0,7" fill="none" stroke="{PURPLE}" stroke-width="1.2"/>
  </marker>
  <marker id="arrGray" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <path d="M0,0 L10,3.5 L0,7" fill="none" stroke="{DGRAY}" stroke-width="1.2"/>
  </marker>
  <marker id="arrGreen" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <path d="M0,0 L10,3.5 L0,7" fill="none" stroke="{GREEN}" stroke-width="1.2"/>
  </marker>
  <marker id="arrOrange" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <path d="M0,0 L10,3.5 L0,7" fill="none" stroke="{ORANGE}" stroke-width="1.2"/>
  </marker>
  <marker id="arrMagenta" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <path d="M0,0 L10,3.5 L0,7" fill="none" stroke="{MAGENTA}" stroke-width="1.2"/>
  </marker>
  <marker id="arrGold" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <path d="M0,0 L10,3.5 L0,7" fill="none" stroke="{GOLD}" stroke-width="1.2"/>
  </marker>
  <marker id="arrRed" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
    <path d="M0,0 L10,3.5 L0,7" fill="none" stroke="{RED}" stroke-width="1.2"/>
  </marker>
  {extra_defs}
</defs>
<text x="{w // 2}" y="{title_y}" text-anchor="middle" fill="{CYAN}" font-size="16" font-weight="700" {FONT} filter="url(#glow)">{title_text}</text>
<rect x="20" y="{title_y + 6}" width="{w - 40}" height="2" rx="1" fill="{CYAN}" fill-opacity="0.15"/>
'''


def svg_footer():
    return '</svg>\n'


def legend_box(x, y, w, h, items, title='LEGEND'):
    lines = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="rgba(13,17,23,0.92)" stroke="{DGRAY}" stroke-opacity="0.4"/>',
        f'<text x="{x + 10}" y="{y + 16}" fill="{GRAY}" font-size="11" font-weight="700" {FONT}>{title}</text>',
    ]
    cy = y + 32
    for color, label in items:
        lines.append(f'<rect x="{x + 10}" y="{cy - 5}" width="10" height="10" rx="2" fill="{color}"/>')
        lines.append(f'<text x="{x + 28}" y="{cy + 4}" fill="{GRAY}" font-size="10" {FONT}>{label}</text>')
        cy += 18
    return '\n'.join(lines)


def module_box(x, y, w, h, title, color, files, capabilities, standard):
    grad_id = f'grad{title[:3]}'
    color_map = {
        'INF': 'gradCyan', 'ROU': 'gradPurple', 'SEC': 'gradMagenta',
        'ORB': 'gradOrange', 'SIM': 'gradGreen',
    }
    gid = color_map.get(title[:3], 'gradCyan')
    lines = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="url(#{gid})" stroke="{color}" stroke-opacity="0.35"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="8" fill="{color}" fill-opacity="0.12"/>',
        f'<text x="{x + w // 2}" y="{y + 17}" text-anchor="middle" fill="{color}" font-size="12" font-weight="700" {FONT}>{title}</text>',
    ]
    ty = y + 38
    for f_name in files:
        lines.append(f'<text x="{x + 10}" y="{ty}" fill="{GRAY}" font-size="10" {FONT}>{f_name}</text>')
        ty += 14
    ty += 4
    for cap in capabilities:
        lines.append(f'<text x="{x + 10}" y="{ty}" fill="{DGRAY}" font-size="9" {FONT}>{cap}</text>')
        ty += 13
    ty += 4
    lines.append(f'<rect x="{x + 6}" y="{ty - 10}" width="{w - 12}" height="1" fill="{color}" fill-opacity="0.15"/>')
    lines.append(f'<text x="{x + 10}" y="{ty + 4}" fill="{DGRAY}" font-size="9" {FONT} font-style="italic">{standard}</text>')
    return '\n'.join(lines)


def generate_system_architecture():
    w, h = 1200, 700
    s = svg_header(w, h, 'AETHERIX SYSTEM ARCHITECTURE')

    box_w = 210
    box_h = 200
    gap = 16
    start_x = (w - 5 * box_w - 4 * gap) // 2
    top_y = 48

    modules = [
        ('INFRASTRUCTURE', CYAN,
         ['link_budget.py', 'rf_link_budget.py'],
         ['FSPL, EIRP, margin calc', 'Ka/X/S/UHF bands', 'Optical link budget'],
         'CCSDS 141.0-B-1'),
        ('ROUTING', PURPLE,
         ['rl_agent.py', 'bundle.py', 'ltp.py', 'tcpcl.py', 'udp_cl.py', 'forwarding_engine.py'],
         ['Q-learning, federated', 'BPv7 custody transfer', 'LTP/TCPCL/UDP-CL'],
         'RFC 9171 / RFC 5326'),
        ('SECURITY', MAGENTA,
         ['qkd.py', 'repeater_chain.py', 'privacy_amplification.py'],
         ['BB84, E91 protocols', 'CASCADE reconciliation', 'Entanglement purification'],
         'NIST FIPS 203/204'),
        ('ORBITAL', ORANGE,
         ['contact_windows.py', 'topology.py', 'doppler.py', 'bodies.py'],
         ['5-tier, 241 nodes', 'Synodic period model', 'Doppler compensation'],
         'CCSDS 734.2-B-1'),
        ('SIMULATION', GREEN,
         ['simulator.py', 'policy_engine.py', 'training.py', 'multi_agent.py'],
         ['Full sim engine', 'Policy routing', 'Federated Q-tables'],
         'RFC 4838'),
    ]

    for i, (title, color, files, caps, std) in enumerate(modules):
        bx = start_x + i * (box_w + gap)
        s += module_box(bx, top_y, box_w, box_h, title, color, files, caps, std) + '\n'

    arrow_y1 = top_y + box_h + 4
    arrow_y2 = arrow_y1 + 30
    mid_x = w // 2
    for i in range(5):
        bx = start_x + i * (box_w + gap) + box_w // 2
        s += f'<line x1="{bx}" y1="{arrow_y1}" x2="{mid_x}" y2="{arrow_y2}" stroke="{DGRAY}" stroke-width="1.5"/>\n'
    s += f'<circle cx="{mid_x}" cy="{arrow_y2}" r="4" fill="{ORANGE}" filter="url(#glow)"/>\n'

    sim_bar_y = arrow_y2 + 10
    s += f'<rect x="30" y="{sim_bar_y}" width="{w - 60}" height="48" rx="8" fill="url(#gradOrange)" stroke="{ORANGE}" stroke-opacity="0.35"/>\n'
    s += f'<text x="{mid_x}" y="{sim_bar_y + 20}" text-anchor="middle" fill="{ORANGE}" font-size="13" font-weight="700" {FONT} filter="url(#glow)">SIMULATION ENGINE</text>\n'
    s += f'<text x="{mid_x}" y="{sim_bar_y + 38}" text-anchor="middle" fill="{GRAY}" font-size="10" {FONT}>simulator.py &#183; policy_engine.py &#183; training.py &#183; multi_agent.py &#183; forwarding_engine.py</text>\n'

    web_bar_y = sim_bar_y + 68
    s += f'<line x1="{mid_x}" y1="{sim_bar_y + 48}" x2="{mid_x}" y2="{web_bar_y}" stroke="{DGRAY}" stroke-width="1.5" marker-end="url(#arrGray)"/>\n'
    s += f'<rect x="80" y="{web_bar_y}" width="{w - 160}" height="44" rx="8" fill="url(#gradGreen)" stroke="{GREEN}" stroke-opacity="0.35"/>\n'
    s += f'<text x="{mid_x}" y="{web_bar_y + 18}" text-anchor="middle" fill="{GREEN}" font-size="13" font-weight="700" {FONT} filter="url(#glow)">WEB SHOWCASE &#8212; 10 Interactive Demos</text>\n'
    s += f'<text x="{mid_x}" y="{web_bar_y + 36}" text-anchor="middle" fill="{GRAY}" font-size="10" {FONT}>FastAPI backend &#183; React frontend &#183; 149 tests &#183; 27 Python modules</text>\n'

    std_y = web_bar_y + 58
    half_w = (w - 80) // 2 - 10
    s += f'<rect x="30" y="{std_y}" width="{half_w}" height="28" rx="4" fill="{CYAN}" fill-opacity="0.04" stroke="{CYAN}" stroke-opacity="0.15"/>\n'
    s += f'<text x="{30 + half_w // 2}" y="{std_y + 18}" text-anchor="middle" fill="{DGRAY}" font-size="10" {FONT}>CCSDS 734.2-B-1 &#183; CCSDS 735.1-B-1 &#183; CCSDS 141.0-B-1</text>\n'
    s += f'<rect x="{50 + half_w}" y="{std_y}" width="{half_w}" height="28" rx="4" fill="{PURPLE}" fill-opacity="0.04" stroke="{PURPLE}" stroke-opacity="0.15"/>\n'
    s += f'<text x="{50 + half_w + half_w // 2}" y="{std_y + 18}" text-anchor="middle" fill="{DGRAY}" font-size="10" {FONT}>RFC 9171 &#183; RFC 5326 &#183; RFC 7242 &#183; NIST FIPS 203/204</text>\n'

    s += svg_footer()
    return s, w, h


def generate_5tier_network():
    w, h = 1200, 750
    s = svg_header(w, h, 'AETHERIX 5-TIER NETWORK TOPOLOGY')

    cx_left = 280
    cx_right = 920
    cx_mid = 600

    t1_y = 65
    s += f'<text x="{cx_left}" y="{t1_y}" text-anchor="middle" fill="{CYAN}" font-size="12" font-weight="700" {FONT} letter-spacing="2">EARTH GROUND</text>\n'
    s += f'<text x="{cx_left}" y="{t1_y + 14}" text-anchor="middle" fill="{DGRAY}" font-size="10" {FONT}>T1 &#183; 6 nodes</text>\n'
    t1_nodes = ['Goldstone', 'Madrid', 'Canberra', 'MOC', 'NOC', 'SOC']
    t1_x_start = cx_left - 230
    for i, name in enumerate(t1_nodes):
        nx = t1_x_start + i * 90
        ny = t1_y + 28
        s += f'<rect x="{nx}" y="{ny}" width="80" height="28" rx="4" fill="{CYAN}" fill-opacity="0.15" stroke="{CYAN}" stroke-opacity="0.4"/>\n'
        s += f'<text x="{nx + 40}" y="{ny + 18}" text-anchor="middle" fill="white" font-size="10" font-weight="600" {FONT}>{name}</text>\n'

    t2_y = 140
    s += f'<text x="{cx_left}" y="{t2_y}" text-anchor="middle" fill="{CYAN}" font-size="12" font-weight="700" {FONT} letter-spacing="2">EARTH ORBITAL</text>\n'
    s += f'<text x="{cx_left}" y="{t2_y + 14}" text-anchor="middle" fill="{DGRAY}" font-size="10" {FONT}>T2 &#183; 51 nodes</text>\n'
    geo_names = ['GEO-Relay-1', 'GEO-Relay-2', 'GEO-Relay-3']
    for i, name in enumerate(geo_names):
        nx = t1_x_start + i * 180
        ny = t2_y + 26
        s += f'<rect x="{nx}" y="{ny}" width="100" height="26" rx="4" fill="{CYAN}" fill-opacity="0.2" stroke="{CYAN}" stroke-opacity="0.5"/>\n'
        s += f'<text x="{nx + 50}" y="{ny + 17}" text-anchor="middle" fill="white" font-size="10" font-weight="600" {FONT}>{name}</text>\n'
    s += f'<rect x="{t1_x_start}" y="{t2_y + 60}" width="{540}" height="24" rx="4" fill="{CYAN}" fill-opacity="0.08" stroke="{CYAN}" stroke-opacity="0.2" stroke-dasharray="4,3"/>\n'
    s += f'<text x="{cx_left}" y="{t2_y + 76}" text-anchor="middle" fill="{CYAN}" font-size="10" {FONT}>+ 48 LEO laser mesh satellites (optical ISL, 10 Gbps interconnect)</text>\n'

    for i in range(6):
        nx = t1_x_start + i * 90 + 40
        s += f'<line x1="{nx}" y1="{t1_y + 56}" x2="{nx}" y2="{t2_y + 26}" stroke="{DGRAY}" stroke-width="1"/>\n'

    t3_y = 255
    s += f'<text x="{cx_mid}" y="{t3_y}" text-anchor="middle" fill="{PURPLE}" font-size="12" font-weight="700" {FONT} letter-spacing="2">DEEP SPACE TRANSIT</text>\n'
    s += f'<text x="{cx_mid}" y="{t3_y + 14}" text-anchor="middle" fill="{DGRAY}" font-size="10" {FONT}>T3 &#183; 4 nodes &#183; Lagrange point relays</text>\n'
    t3_nodes = ['ES-L4 Relay', 'ES-L5 Relay', 'Transfer-1', 'Transfer-2']
    for i, name in enumerate(t3_nodes):
        nx = cx_mid - 250 + i * 165
        ny = t3_y + 26
        s += f'<rect x="{nx}" y="{ny}" width="140" height="30" rx="6" fill="{PURPLE}" fill-opacity="0.15" stroke="{PURPLE}" stroke-opacity="0.4"/>\n'
        s += f'<text x="{nx + 70}" y="{ny + 20}" text-anchor="middle" fill="white" font-size="11" font-weight="600" {FONT}>{name}</text>\n'

    s += f'<text x="{cx_mid}" y="{t3_y + 80}" text-anchor="middle" fill="{DGRAY}" font-size="10" {FONT} font-style="italic">~225 million km average &#183; 12.5 min one-way light time</text>\n'

    path1_y = t3_y + 100
    path2_y = path1_y + 22
    path3_y = path2_y + 22
    paths = [
        (path1_y, CYAN, 'Path A: Goldstone → GEO-1 → ES-L4 → MRS-Alpha → Habitat-1 (primary)', '10-20 Mbps'),
        (path2_y, GREEN, 'Path B: Madrid → GEO-2 → ES-L5 → MRS-Beta → Rover-1 (redundant)', '5-15 Mbps'),
        (path3_y, GOLD, 'Path C: Canberra → GEO-3 → Transfer-1 → Polar-1 → Base-2 (backup)', '2-10 Mbps'),
    ]
    for py, color, label, rate in paths:
        s += f'<rect x="100" y="{py}" width="{w - 200}" height="18" rx="3" fill="{color}" fill-opacity="0.06" stroke="{color}" stroke-opacity="0.2"/>\n'
        s += f'<text x="110" y="{py + 13}" fill="{color}" font-size="10" {FONT}>{label}</text>\n'
        s += f'<text x="{w - 120}" y="{py + 13}" text-anchor="end" fill="{GRAY}" font-size="10" {FONT}>{rate}</text>\n'

    t4_y = path3_y + 35
    s += f'<text x="{cx_right}" y="{t4_y}" text-anchor="middle" fill="{ORANGE}" font-size="12" font-weight="700" {FONT} letter-spacing="2">MARS ORBITAL</text>\n'
    s += f'<text x="{cx_right}" y="{t4_y + 14}" text-anchor="middle" fill="{DGRAY}" font-size="10" {FONT}>T4 &#183; 13 nodes</text>\n'
    t4_nodes = ['Areostat-&#945;', 'Areostat-&#946;', 'Polar-1', 'Polar-2']
    for i, name in enumerate(t4_nodes):
        nx = cx_right - 230 + i * 120
        ny = t4_y + 26
        s += f'<rect x="{nx}" y="{ny}" width="110" height="28" rx="5" fill="{ORANGE}" fill-opacity="0.2" stroke="{ORANGE}" stroke-opacity="0.5"/>\n'
        s += f'<text x="{nx + 55}" y="{ny + 18}" text-anchor="middle" fill="white" font-size="10" font-weight="600" {FONT}>{name}</text>\n'
    s += f'<rect x="{cx_right - 230}" y="{t4_y + 62}" width="{460}" height="24" rx="4" fill="{ORANGE}" fill-opacity="0.08" stroke="{ORANGE}" stroke-opacity="0.2" stroke-dasharray="4,3"/>\n'
    s += f'<text x="{cx_right}" y="{t4_y + 78}" text-anchor="middle" fill="{ORANGE}" font-size="10" {FONT}>+ 9 relay satellites in equatorial &amp; polar orbits</text>\n'

    t5_y = t4_y + 100
    s += f'<text x="{cx_right}" y="{t5_y}" text-anchor="middle" fill="{GOLD}" font-size="12" font-weight="700" {FONT} letter-spacing="2">MARS SURFACE</text>\n'
    s += f'<text x="{cx_right}" y="{t5_y + 14}" text-anchor="middle" fill="{DGRAY}" font-size="10" {FONT}>T5 &#183; 167 nodes</text>\n'
    t5_labels = [
        ('Habitats', '12 bases'), ('Rovers', '24 mobile'), ('Drones', '18 aerial'),
        ('Sensors', '113 fixed'),
    ]
    for i, (name, count) in enumerate(t5_labels):
        nx = cx_right - 250 + i * 135
        ny = t5_y + 24
        s += f'<rect x="{nx}" y="{ny}" width="120" height="38" rx="5" fill="{GOLD}" fill-opacity="0.12" stroke="{GOLD}" stroke-opacity="0.3"/>\n'
        s += f'<text x="{nx + 60}" y="{ny + 16}" text-anchor="middle" fill="{GOLD}" font-size="10" font-weight="600" {FONT}>{name}</text>\n'
        s += f'<text x="{nx + 60}" y="{ny + 30}" text-anchor="middle" fill="{DGRAY}" font-size="9" {FONT}>{count}</text>\n'

    for i in range(3):
        nx = cx_right - 230 + i * 165 + 55
        s += f'<line x1="{nx}" y1="{t4_y + 90}" x2="{nx}" y2="{t5_y + 24}" stroke="{DGRAY}" stroke-width="1" stroke-dasharray="3,3"/>\n'

    mid_x_5t = w // 2
    s += f'<rect x="100" y="{h - 85}" width="{w - 200}" height="36" rx="6" fill="{CYAN}" fill-opacity="0.06" stroke="{CYAN}" stroke-opacity="0.2"/>\n'
    s += f'<text x="{mid_x_5t}" y="{h - 62}" text-anchor="middle" fill="{CYAN}" font-size="12" font-weight="700" {FONT}>241 Nodes &#183; 5 Tiers &#183; 3 Redundant Paths &#183; No Single Point of Failure</text>\n'

    s += svg_footer()
    return s, w, h


def generate_dtn_store_and_forward():
    w, h = 1200, 700
    s = svg_header(w, h, 'DTN STORE-AND-FORWARD vs TCP/IP')

    s += f'<text x="{w // 2}" y="56" text-anchor="middle" fill="{GRAY}" font-size="13" font-weight="600" {FONT} letter-spacing="2">TCP/IP: END-TO-END CONNECTION (FAILS IN SPACE)</text>\n'

    tcp_y = 72
    tcp_nodes = ['Source', 'Router A', 'Router B', 'Router C', 'Destination']
    tcp_x_start = 80
    tcp_gap = 210
    for i, name in enumerate(tcp_nodes):
        nx = tcp_x_start + i * tcp_gap
        is_last = i == len(tcp_nodes) - 1
        fill_op = '0.12' if not is_last else '0.12'
        stroke_col = CYAN if not is_last else RED
        stroke_dash = '' if not is_last else ' stroke-dasharray="4,3"'
        s += f'<rect x="{nx}" y="{tcp_y}" width="140" height="40" rx="6" fill="{stroke_col}" fill-opacity="{fill_op}" stroke="{stroke_col}" stroke-opacity="0.4"{stroke_dash}/>\n'
        s += f'<text x="{nx + 70}" y="{tcp_y + 25}" text-anchor="middle" fill="{stroke_col}" font-size="12" font-weight="600" {FONT}>{name}</text>\n'
        if i < len(tcp_nodes) - 1:
            lx1 = nx + 140
            lx2 = nx + tcp_gap
            mid_lx = (lx1 + lx2) // 2
            next_ok = i < len(tcp_nodes) - 2
            lcolor = CYAN if next_ok else RED
            ldash = '' if next_ok else ' stroke-dasharray="6,4"'
            s += f'<line x1="{lx1}" y1="{tcp_y + 20}" x2="{lx2}" y2="{tcp_y + 20}" stroke="{lcolor}" stroke-width="1.5"{ldash} marker-end="url(#{_arr(lcolor)})"/>\n'
            if not next_ok:
                s += f'<text x="{mid_lx}" y="{tcp_y + 12}" text-anchor="middle" fill="{RED}" font-size="11" {FONT} filter="url(#glow)">LINK LOST</text>\n'
                s += f'<text x="{mid_lx}" y="{tcp_y + 48}" text-anchor="middle" fill="{RED}" font-size="14" font-weight="700" {FONT}>&#x2717; TIMEOUT</text>\n'

    s += f'<text x="{w // 2}" y="{tcp_y + 80}" text-anchor="middle" fill="{RED}" font-size="12" {FONT}>TCP requires end-to-end connectivity &#8212; impossible with 3-22 min light-time delays</text>\n'

    sep_y = tcp_y + 100
    s += f'<rect x="40" y="{sep_y}" width="{w - 80}" height="1" fill="{DGRAY}" fill-opacity="0.3"/>\n'

    s += f'<text x="{w // 2}" y="{sep_y + 20}" text-anchor="middle" fill="{GREEN}" font-size="13" font-weight="600" {FONT} letter-spacing="2">DTN: STORE-AND-FORWARD (WORKS IN SPACE)</text>\n'

    dtn_y = sep_y + 38
    dtn_nodes = [
        ('SOURCE', GREEN, ['Create Bundle', 'Priority: P2', 'Lifetime: 24h', 'CUSTODY: Source']),
        ('NODE A', CYAN, ['Forward bundle', 'Custody accepted &#x2713;', 'RL route: Node B', 'STORE: 2 bundles']),
        ('NODE B', GOLD, ['Storing bundle...', 'Waiting for link...', 'No contact window', '&#x23F3; WAIT 14 min']),
        ('NODE C', CYAN, ['Forward bundle', 'Custody accepted &#x2713;', 'RL route: Dest', 'CUSTODY: Node C']),
        ('DESTINATION', GREEN, ['Reassemble', 'Verify integrity', 'Decrypt (QKD)', 'DELIVERED &#x2713;']),
    ]

    dtn_x_start = 60
    dtn_gap = 218
    node_w = 180
    node_h = 110

    for i, (name, color, details) in enumerate(dtn_nodes):
        nx = dtn_x_start + i * dtn_gap
        grad = _grad(color)
        s += f'<rect x="{nx}" y="{dtn_y}" width="{node_w}" height="{node_h}" rx="8" fill="url(#{grad})" stroke="{color}" stroke-opacity="0.4"/>\n'
        s += f'<rect x="{nx}" y="{dtn_y}" width="{node_w}" height="22" rx="8" fill="{color}" fill-opacity="0.15"/>\n'
        s += f'<text x="{nx + node_w // 2}" y="{dtn_y + 16}" text-anchor="middle" fill="{color}" font-size="11" font-weight="700" {FONT}>{name}</text>\n'
        for j, detail in enumerate(details):
            dy = dtn_y + 38 + j * 16
            dcolor = GRAY if j < 2 else (GREEN if '&#x2713;' in detail else DGRAY)
            if '&#x23F3;' in detail:
                dcolor = GOLD
            s += f'<text x="{nx + 8}" y="{dy}" fill="{dcolor}" font-size="10" {FONT}>{detail}</text>\n'

        if i < len(dtn_nodes) - 1:
            lx1 = nx + node_w
            lx2 = nx + dtn_gap
            mid_lx = (lx1 + lx2) // 2
            is_wait = name == 'NODE B'
            lcolor = GOLD if is_wait else CYAN
            ldash = ' stroke-dasharray="5,3"' if is_wait else ''
            s += f'<line x1="{lx1 + 2}" y1="{dtn_y + node_h // 2}" x2="{lx2 - 2}" y2="{dtn_y + node_h // 2}" stroke="{lcolor}" stroke-width="2"{ldash} marker-end="url(#{_arr(lcolor)})"/>\n'
            label = 'no link' if is_wait else 'link up'
            s += f'<text x="{mid_lx}" y="{dtn_y + node_h // 2 - 8}" text-anchor="middle" fill="{lcolor}" font-size="9" {FONT}>{label}</text>\n'
            if not is_wait:
                s += f'<text x="{mid_lx}" y="{dtn_y + node_h // 2 + 16}" text-anchor="middle" fill="{GREEN}" font-size="9" {FONT}>custody &#x2192;</text>\n'

    custody_y = dtn_y + node_h + 18
    custody_items = [
        (GREEN, 'Custody Transfer', 'Each node takes responsibility for the bundle'),
        (CYAN, 'Store &amp; Wait', 'Bundle stored safely until next hop available'),
        (GOLD, 'Link Status', 'Intermittent links handled gracefully'),
    ]
    cw = (w - 100) // 3 - 10
    for i, (color, title, desc) in enumerate(custody_items):
        cx = 50 + i * (cw + 15)
        s += f'<rect x="{cx}" y="{custody_y}" width="{cw}" height="46" rx="6" fill="{color}" fill-opacity="0.05" stroke="{color}" stroke-opacity="0.2"/>\n'
        s += f'<text x="{cx + cw // 2}" y="{custody_y + 18}" text-anchor="middle" fill="{color}" font-size="11" font-weight="600" {FONT}>{title}</text>\n'
        s += f'<text x="{cx + cw // 2}" y="{custody_y + 36}" text-anchor="middle" fill="{GRAY}" font-size="9" {FONT}>{desc}</text>\n'

    cl_y = custody_y + 60
    s += f'<rect x="40" y="{cl_y}" width="{w - 80}" height="42" rx="6" fill="{ORANGE}" fill-opacity="0.06" stroke="{ORANGE}" stroke-opacity="0.2"/>\n'
    s += f'<text x="{w // 2}" y="{cl_y + 16}" text-anchor="middle" fill="{ORANGE}" font-size="11" font-weight="600" {FONT}>THREE CONVERGENCE LAYERS</text>\n'
    cl_labels = [
        (w // 2 - 280, 'LTP (RFC 5326)', 'Deep space, retransmission'),
        (w // 2 - 40, 'TCPCL (RFC 7242)', 'Earth ground segment'),
        (w // 2 + 200, 'UDP-CL', 'Optical ISL, low latency'),
    ]
    for cx, title, desc in cl_labels:
        s += f'<text x="{cx}" y="{cl_y + 34}" fill="{GRAY}" font-size="10" font-weight="600" {FONT}>{title}</text>\n'
        s += f'<text x="{cx}" y="{cl_y + 34}" text-anchor="middle" fill="{GRAY}" font-size="10" {FONT} dx="40">{desc}</text>\n'

    s += svg_footer()
    return s, w, h


def generate_earth_mars_journey():
    w, h = 1200, 750
    extra_defs = '''
    <radialGradient id="marsGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ff6b35" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#ff6b35" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="earthGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00d4ff" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#00d4ff" stop-opacity="0"/>
    </radialGradient>
    '''
    s = svg_header(w, h, 'EARTH-MARS DATA JOURNEY: 7 HOPS', extra_defs)

    mars_x, mars_y = 100, 100
    earth_x, earth_y = 1100, 100

    s += f'<circle cx="{mars_x}" cy="{mars_y}" r="55" fill="url(#marsGlow)"/>\n'
    s += f'<circle cx="{mars_x}" cy="{mars_y}" r="40" fill="{ORANGE}" fill-opacity="0.15" stroke="{ORANGE}" stroke-width="1.5"/>\n'
    s += f'<text x="{mars_x}" y="{mars_y - 4}" text-anchor="middle" fill="{ORANGE}" font-size="14" font-weight="700" {FONT}>MARS</text>\n'
    s += f'<text x="{mars_x}" y="{mars_y + 12}" text-anchor="middle" fill="{GRAY}" font-size="10" {FONT}>Surface</text>\n'

    s += f'<circle cx="{earth_x}" cy="{earth_y}" r="65" fill="url(#earthGlow)"/>\n'
    s += f'<circle cx="{earth_x}" cy="{earth_y}" r="50" fill="{CYAN}" fill-opacity="0.15" stroke="{CYAN}" stroke-width="1.5"/>\n'
    s += f'<text x="{earth_x}" y="{earth_y - 4}" text-anchor="middle" fill="{CYAN}" font-size="14" font-weight="700" {FONT}>EARTH</text>\n'
    s += f'<text x="{earth_x}" y="{earth_y + 12}" text-anchor="middle" fill="{GRAY}" font-size="10" {FONT}>Ground</text>\n'

    s += f'<line x1="{mars_x + 50}" y1="{mars_y}" x2="{earth_x - 60}" y2="{earth_y}" stroke="{DGRAY}" stroke-width="0.8" stroke-dasharray="6,4"/>\n'
    s += f'<text x="{w // 2}" y="{mars_y - 52}" text-anchor="middle" fill="{DGRAY}" font-size="11" {FONT} font-style="italic">~225 million km &#183; 12.5 min one-way light time</text>\n'

    hop_positions = [
        mars_x + 100,
        mars_x + 220,
        mars_x + 340,
        mars_x + 460,
        mars_x + 560,
        mars_x + 680,
        mars_x + 800,
    ]
    hop_labels_top = ['Areostat', 'Polar Orb.', 'Mars Relay', 'ES-L4', 'Deep Space', 'LEO Mesh', 'DSN']
    hop_colors_top = [ORANGE, ORANGE, ORANGE, PURPLE, PURPLE, CYAN, CYAN]

    for i, (hx, label, color) in enumerate(zip(hop_positions, hop_labels_top, hop_colors_top)):
        s += f'<rect x="{hx - 38}" y="{mars_y - 18}" width="76" height="36" rx="6" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.4"/>\n'
        s += f'<text x="{hx}" y="{mars_y + 2}" text-anchor="middle" fill="{color}" font-size="9" font-weight="600" {FONT}>{label}</text>\n'
        if i > 0:
            s += f'<line x1="{hop_positions[i - 1] + 38}" y1="{mars_y}" x2="{hx - 38}" y2="{mars_y}" stroke="{color}" stroke-width="1.2" marker-end="url(#{_arr(color)})"/>\n'

    s += f'<text x="{w // 2}" y="{mars_y + 38}" text-anchor="middle" fill="{GRAY}" font-size="11" font-weight="600" {FONT} letter-spacing="2">HOP DETAIL CARDS</text>\n'
    s += f'<rect x="40" y="{mars_y + 44}" width="{w - 80}" height="1" fill="{DGRAY}" fill-opacity="0.2"/>\n'

    hop_cards = [
        ('HOP 1', ORANGE, 'Rover &#x2192; Areostationary', 'UHF 400 MHz', '~400 km', '2 Mbps'),
        ('HOP 2', ORANGE, 'Areostat &#x2192; Polar Orbiter', 'UHF 400 MHz', '17,032 km alt', '256 kbps'),
        ('HOP 3', ORANGE, 'Polar Orb. &#x2192; Mars Relay', 'Optical ISL', 'Mars orbit', '10 Gbps'),
        ('HOP 4-5', PURPLE, 'Mars Relay &#x2192; ES-L4 &#x2192; Deep Space', '1550nm laser', '225M km', '10-20 Mbps'),
        ('HOP 6', CYAN, 'Deep Space &#x2192; LEO Mesh', 'Optical ISL', 'Earth orbit', '10 Gbps'),
        ('HOP 7', GREEN, 'LEO &#x2192; DSN Goldstone &#x2192; JPL', 'Ka-band downlink', '~384,000 km', 'DELIVERED &#x2713;'),
    ]

    card_w = 175
    card_h = 100
    card_start_x = 35
    card_gap = 7
    card_y = mars_y + 52

    for i, (title, color, route, tech, dist, rate) in enumerate(hop_cards):
        cx = card_start_x + i * (card_w + card_gap)
        grad = _grad(color)
        s += f'<rect x="{cx}" y="{card_y}" width="{card_w}" height="{card_h}" rx="6" fill="url(#{grad})" stroke="{color}" stroke-opacity="0.35"/>\n'
        s += f'<rect x="{cx}" y="{card_y}" width="{card_w}" height="20" rx="6" fill="{color}" fill-opacity="0.12"/>\n'
        s += f'<text x="{cx + card_w // 2}" y="{card_y + 15}" text-anchor="middle" fill="{color}" font-size="11" font-weight="700" {FONT}>{title}</text>\n'
        s += f'<text x="{cx + 6}" y="{card_y + 35}" fill="{GRAY}" font-size="9" {FONT}>{route}</text>\n'
        s += f'<text x="{cx + 6}" y="{card_y + 50}" fill="{DGRAY}" font-size="9" {FONT}>{tech}</text>\n'
        s += f'<text x="{cx + 6}" y="{card_y + 65}" fill="{DGRAY}" font-size="9" {FONT}>{dist}</text>\n'
        rate_color = GREEN if 'DELIVERED' in rate else GRAY
        s += f'<text x="{cx + 6}" y="{card_y + 82}" fill="{rate_color}" font-size="10" font-weight="600" {FONT}>{rate}</text>\n'
        if i < len(hop_cards) - 1:
            s += f'<line x1="{cx + card_w}" y1="{card_y + card_h // 2}" x2="{cx + card_w + card_gap}" y2="{card_y + card_h // 2}" stroke="{DGRAY}" stroke-width="1" marker-end="url(#arrGray)"/>\n'

    summary_y = card_y + card_h + 18
    summary_items = [
        (CYAN, 'Total Transit: ~13 min', 'vs 12.5 min light-time delay'),
        (GREEN, 'DTN Overhead: &lt;5%', 'Store-and-forward adds minimal latency'),
        (MAGENTA, 'QKD Secured', 'End-to-end quantum encryption (BB84)'),
    ]
    sw = (w - 100) // 3 - 10
    for i, (color, title, desc) in enumerate(summary_items):
        sx = 50 + i * (sw + 15)
        s += f'<rect x="{sx}" y="{summary_y}" width="{sw}" height="48" rx="6" fill="{color}" fill-opacity="0.06" stroke="{color}" stroke-opacity="0.25"/>\n'
        s += f'<text x="{sx + sw // 2}" y="{summary_y + 20}" text-anchor="middle" fill="{color}" font-size="11" font-weight="600" {FONT}>{title}</text>\n'
        s += f'<text x="{sx + sw // 2}" y="{summary_y + 38}" text-anchor="middle" fill="{GRAY}" font-size="9" {FONT}>{desc}</text>\n'

    info_y = summary_y + 60
    s += f'<rect x="40" y="{info_y}" width="{w - 80}" height="34" rx="6" fill="{RED}" fill-opacity="0.05" stroke="{RED}" stroke-opacity="0.15"/>\n'
    s += f'<text x="{w // 2}" y="{info_y + 22}" text-anchor="middle" fill="{RED}" font-size="11" font-weight="600" {FONT}>&#x26A1; If any link drops mid-transfer, the bundle is stored safely &#8212; zero data loss guaranteed</text>\n'

    s += svg_footer()
    return s, w, h


def generate_data_flow():
    w, h = 1200, 750
    s = svg_header(w, h, 'AETHERIX DATA FLOW ARCHITECTURE')

    layers = [
        {
            'label': 'APPLICATION LAYER',
            'label_y': 56,
            'color': CYAN,
            'y': 66,
            'boxes': [
                ('SOURCE NODE', 'Science data (500 MB)', CYAN, 50),
                ('BUNDLE PROTOCOL (BPv7)', 'Wraps data + metadata + routing', PURPLE, 270),
                ('RL ROUTING AGENT', 'Q-learning selects next hop', GREEN, 490),
                ('QKD ENCRYPT', 'BB84/E91 key (256-bit AES)', MAGENTA, 710),
                ('BUNDLE READY', 'Encrypted + routed bundle', CYAN, 930),
            ],
            'box_h': 50,
            'box_w': 200,
        },
        {
            'label': 'CONVERGENCE LAYER',
            'label_y': 176,
            'color': ORANGE,
            'y': 186,
            'boxes': [
                ('LTP SEGMENTATION', 'Reed-Solomon encoding', ORANGE, 100),
                ('STORE &amp; WAIT', 'Buffer until link available', GOLD, 340),
                ('FORWARD + CUSTODY', 'Transmit + custody transfer', GREEN, 580),
                ('RETRY LOOP', 'If no ACK, retransmit', RED, 820),
            ],
            'box_h': 48,
            'box_w': 210,
        },
        {
            'label': 'PHYSICAL LAYER',
            'label_y': 296,
            'color': GOLD,
            'y': 306,
            'boxes': [
                ('MARS UHF', '400 MHz &#183; 2 Mbps', GOLD, 30),
                ('Optical ISL', 'Mars orbit &#183; 10 Gbps', CYAN, 250),
                ('DEEP SPACE 1550nm', '225M km &#183; 10-20 Mbps', ORANGE, 470),
                ('Earth Optical ISL', 'LEO mesh &#183; 10 Gbps', CYAN, 690),
                ('DSN Ka-band', '384,000 km &#183; downlink', GREEN, 910),
            ],
            'box_h': 48,
            'box_w': 190,
        },
        {
            'label': 'DELIVERY',
            'label_y': 416,
            'color': GREEN,
            'y': 426,
            'boxes': [
                ('LTP REASSEMBLY', 'Reconstruct from segments', ORANGE, 140),
                ('QKD DECRYPT', 'Verify key + AES decrypt', MAGENTA, 380),
                ('APPLICATION', 'Data delivered &#x2713;', GREEN, 620),
                ('ACKNOWLEDGE', 'Custody ACK back to source', CYAN, 860),
            ],
            'box_h': 46,
            'box_w': 210,
        },
    ]

    for layer in layers:
        s += f'<text x="{w // 2}" y="{layer["label_y"]}" text-anchor="middle" fill="{layer["color"]}" font-size="12" font-weight="600" {FONT} letter-spacing="2">{layer["label"]}</text>\n'

        for i, (title, desc, color, x_pos) in enumerate(layer['boxes']):
            grad = _grad(color)
            bw = layer['box_w']
            bh = layer['box_h']
            s += f'<rect x="{x_pos}" y="{layer["y"]}" width="{bw}" height="{bh}" rx="6" fill="url(#{grad})" stroke="{color}" stroke-opacity="0.35"/>\n'
            s += f'<text x="{x_pos + bw // 2}" y="{layer["y"] + bh // 2 - 4}" text-anchor="middle" fill="{color}" font-size="11" font-weight="700" {FONT}>{title}</text>\n'
            s += f'<text x="{x_pos + bw // 2}" y="{layer["y"] + bh // 2 + 12}" text-anchor="middle" fill="{GRAY}" font-size="9" {FONT}>{desc}</text>\n'

            if i < len(layer['boxes']) - 1:
                next_x = layer['boxes'][i + 1][3]
                s += f'<line x1="{x_pos + bw + 2}" y1="{layer["y"] + bh // 2}" x2="{next_x - 2}" y2="{layer["y"] + bh // 2}" stroke="{DGRAY}" stroke-width="1.5" marker-end="url(#arrGray)"/>\n'

        if layer != layers[-1]:
            next_layer = layers[layers.index(layer) + 1]
            s += f'<rect x="40" y="{layer["y"] + layer["box_h"] + 4}" width="{w - 80}" height="1" fill="{DGRAY}" fill-opacity="0.15"/>\n'
            last_box = layer['boxes'][-1]
            first_next = next_layer['boxes'][0]
            from_x = last_box[3] + layer['box_w'] // 2
            to_x = first_next[3] + layer['box_w'] // 2
            from_y = layer['y'] + layer['box_h']
            to_y = next_layer['y']
            s += f'<line x1="{from_x}" y1="{from_y}" x2="{to_x}" y2="{to_y}" stroke="{DGRAY}" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrGray)"/>\n'

    cycle_y = 500
    s += f'<rect x="40" y="{cycle_y}" width="{w - 80}" height="42" rx="6" fill="{CYAN}" fill-opacity="0.05" stroke="{CYAN}" stroke-opacity="0.2"/>\n'
    s += f'<text x="{w // 2}" y="{cycle_y + 16}" text-anchor="middle" fill="{CYAN}" font-size="11" font-weight="600" {FONT}>PER-HOP CYCLE (repeats at each DTN node)</text>\n'
    s += f'<text x="{w // 2}" y="{cycle_y + 34}" text-anchor="middle" fill="{GRAY}" font-size="10" {FONT}>Receive &#x2192; Store &#x2192; RL Route &#x2192; QKD Re-key &#x2192; LTP Segment &#x2192; Transmit &#x2192; Wait for Custody ACK &#x2192; Next Hop</text>\n'

    flow_y = cycle_y + 56
    flow_steps = [
        ('Receive', CYAN), ('Store', GOLD), ('RL Route', PURPLE),
        ('QKD Key', MAGENTA), ('LTP Seg.', ORANGE), ('Transmit', GREEN),
        ('ACK Wait', GOLD), ('Next Hop', CYAN),
    ]
    step_w = 120
    step_gap = 14
    total_flow_w = len(flow_steps) * step_w + (len(flow_steps) - 1) * step_gap
    flow_start = (w - total_flow_w) // 2
    for i, (label, color) in enumerate(flow_steps):
        fx = flow_start + i * (step_w + step_gap)
        s += f'<rect x="{fx}" y="{flow_y}" width="{step_w}" height="32" rx="5" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.3"/>\n'
        s += f'<text x="{fx + step_w // 2}" y="{flow_y + 20}" text-anchor="middle" fill="{color}" font-size="10" font-weight="600" {FONT}>{label}</text>\n'
        if i < len(flow_steps) - 1:
            s += f'<line x1="{fx + step_w}" y1="{flow_y + 16}" x2="{fx + step_w + step_gap}" y2="{flow_y + 16}" stroke="{DGRAY}" stroke-width="1" marker-end="url(#arrGray)"/>\n'

    s += svg_footer()
    return s, w, h


def generate_protocol_stack():
    w, h = 1200, 750
    s = svg_header(w, h, 'AETHERIX PROTOCOL STACK')

    stack_x = 60
    stack_w = 780
    layer_h = 95
    layer_gap = 10
    start_y = 52

    layers = [
        {
            'name': 'APPLICATION LAYER',
            'color': CYAN,
            'details': [
                ('Science Data', 'Telemetry, imagery, spectral analysis'),
                ('Commands', 'Uplink instructions, configuration'),
                ('Telemetry', 'Spacecraft health, navigation data'),
            ],
            'std': '',
        },
        {
            'name': 'BUNDLE PROTOCOL v7 (RFC 9171)',
            'color': PURPLE,
            'details': [
                ('P0 EMERGENCY', 'Life-critical, immediate delivery'),
                ('P1-2 PRIORITY', 'Command &amp; control, high-value science'),
                ('P3 NORMAL', 'Routine data, standard telemetry'),
                ('P4 BULK', 'Archive data, software updates'),
            ],
            'std': 'RFC 9171 / CCSDS 734.2-B-1',
        },
        {
            'name': 'CONVERGENCE LAYER',
            'color': ORANGE,
            'details': [
                ('LTP (RFC 5326)', 'Deep space links', 'Reliable, retransmission'),
                ('TCPCL (RFC 7242)', 'Earth ground segment', 'Session-based'),
                ('UDP-CL', 'Optical ISL', 'Low-latency, fragmented'),
            ],
            'std': 'RFC 5326 / RFC 7242',
            'sub_cols': True,
        },
        {
            'name': 'SECURITY LAYER',
            'color': MAGENTA,
            'details': [
                ('QKD: BB84/E91', 'Quantum key distribution'),
                ('Post-Quantum: ML-KEM', 'NIST FIPS 203 lattice-based'),
                ('AES-256-GCM', 'Symmetric encryption'),
            ],
            'std': 'NIST FIPS 203 / FIPS 197',
        },
        {
            'name': 'PHYSICAL LAYER',
            'color': GOLD,
            'details': [
                ('UHF 400 MHz', 'Mars surface, short range'),
                ('X-band 8.4 GHz', 'Near-Earth telemetry'),
                ('Ka-band 32 GHz', 'High-rate downlink'),
                ('1550nm Optical', 'Deep space, 10-200 Mbps'),
            ],
            'std': 'CCSDS 141.0-B-1',
        },
    ]

    for i, layer in enumerate(layers):
        ly = start_y + i * (layer_h + layer_gap)
        color = layer['color']
        grad = _grad(color)

        s += f'<rect x="{stack_x}" y="{ly}" width="{stack_w}" height="{layer_h}" rx="8" fill="url(#{grad})" stroke="{color}" stroke-opacity="0.4"/>\n'
        s += f'<rect x="{stack_x}" y="{ly}" width="{stack_w}" height="22" rx="8" fill="{color}" fill-opacity="0.12"/>\n'
        s += f'<text x="{stack_x + 12}" y="{ly + 16}" fill="{color}" font-size="12" font-weight="700" {FONT}>{layer["name"]}</text>\n'

        if layer.get('std'):
            s += f'<text x="{stack_x + stack_w - 10}" y="{ly + 16}" text-anchor="end" fill="{DGRAY}" font-size="9" {FONT}>{layer["std"]}</text>\n'

        if layer.get('sub_cols'):
            sub_w = (stack_w - 40) // 3
            for j, detail in enumerate(layer['details']):
                sx = stack_x + 10 + j * (sub_w + 5)
                s += f'<rect x="{sx}" y="{ly + 28}" width="{sub_w}" height="{layer_h - 36}" rx="4" fill="{color}" fill-opacity="0.06" stroke="{color}" stroke-opacity="0.15"/>\n'
                s += f'<text x="{sx + 6}" y="{ly + 44}" fill="{color}" font-size="10" font-weight="600" {FONT}>{detail[0]}</text>\n'
                s += f'<text x="{sx + 6}" y="{ly + 58}" fill="{GRAY}" font-size="9" {FONT}>{detail[1]}</text>\n'
                s += f'<text x="{sx + 6}" y="{ly + 72}" fill="{DGRAY}" font-size="9" {FONT}>{detail[2]}</text>\n'
        else:
            detail_y = ly + 38
            for detail in layer['details']:
                if len(detail) == 2:
                    s += f'<text x="{stack_x + 16}" y="{detail_y}" fill="{color}" font-size="10" font-weight="600" {FONT}>{detail[0]}</text>\n'
                    s += f'<text x="{stack_x + 160}" y="{detail_y}" fill="{GRAY}" font-size="10" {FONT}>{detail[1]}</text>\n'
                    detail_y += 16
                else:
                    s += f'<text x="{stack_x + 16}" y="{detail_y}" fill="{color}" font-size="10" font-weight="600" {FONT}>{detail[0]}</text>\n'
                    s += f'<text x="{stack_x + 160}" y="{detail_y}" fill="{GRAY}" font-size="10" {FONT}>{detail[1]}</text>\n'
                    detail_y += 16

        if i < len(layers) - 1:
            next_color = layers[i + 1]['color']
            arrow_x = stack_x + stack_w // 2
            arrow_y1 = ly + layer_h
            arrow_y2 = arrow_y1 + layer_gap
            s += f'<line x1="{arrow_x - 30}" y1="{arrow_y1}" x2="{arrow_x - 30}" y2="{arrow_y2}" stroke="{DGRAY}" stroke-width="1.5" marker-end="url(#arrGray)"/>\n'
            s += f'<line x1="{arrow_x + 30}" y1="{arrow_y2}" x2="{arrow_x + 30}" y2="{arrow_y1}" stroke="{DGRAY}" stroke-width="1.5" marker-end="url(#arrGray)"/>\n'

    s += svg_footer()
    return s, w, h


def generate_network_topology():
    w, h = 1200, 750
    s = svg_header(w, h, 'AETHERIX NETWORK TOPOLOGY &amp; BFS PATHFINDING')

    cx = 500
    tier_centers = {
        'T1': (cx, 90, CYAN),
        'T2': (cx, 190, CYAN),
        'T3': (cx, 310, PURPLE),
        'T4': (cx + 200, 420, ORANGE),
        'T5': (cx + 200, 530, GOLD),
    }

    tiers = {
        'T1': [
            ('Goldstone', -200), ('Madrid', -80), ('Canberra', 40),
            ('MOC', 140), ('NOC', 220),
        ],
        'T2': [
            ('GEO-1', -220), ('GEO-2', -120), ('GEO-3', -20),
            ('LEO*', 80), ('LEO*', 180), ('LEO*', 260),
        ],
        'T3': [
            ('ES-L4', -160), ('ES-L5', -40), ('Transfer-1', 80), ('Transfer-2', 200),
        ],
        'T4': [
            ('Areostat-A', -120), ('Areostat-B', 0), ('Polar-1', 120), ('Polar-2', 240),
        ],
        'T5': [
            ('Habitat-1', -120), ('Rover-1', 0), ('Drone-1', 120),
        ],
    }

    node_positions = {}
    node_r = 16

    for tier_id, (tcx, tcy, color) in tier_centers.items():
        nodes = tiers[tier_id]
        for name, offset in nodes:
            nx = tcx + offset
            ny = tcy
            node_positions[f'{tier_id}:{name}'] = (nx, ny, color)

            s += f'<circle cx="{nx}" cy="{ny}" r="{node_r}" fill="{color}" fill-opacity="0.2" stroke="{color}" stroke-opacity="0.5"/>\n'
            label = name if len(name) < 10 else name[:9]
            s += f'<text x="{nx}" y="{ny + 4}" text-anchor="middle" fill="white" font-size="7" font-weight="600" {FONT}>{label}</text>\n'

    edges = [
        ('T1:Goldstone', 'T2:GEO-1'), ('T1:Goldstone', 'T2:GEO-2'),
        ('T1:Madrid', 'T2:GEO-2'), ('T1:Madrid', 'T2:GEO-3'),
        ('T1:Canberra', 'T2:GEO-3'), ('T1:Canberra', 'T2:GEO-1'),
        ('T2:GEO-1', 'T2:GEO-2'), ('T2:GEO-2', 'T2:GEO-3'), ('T2:GEO-1', 'T2:GEO-3'),
        ('T2:GEO-1', 'T3:ES-L4'), ('T2:GEO-2', 'T3:ES-L4'), ('T2:GEO-3', 'T3:ES-L5'),
        ('T3:ES-L4', 'T3:ES-L5'), ('T3:ES-L4', 'T3:Transfer-1'),
        ('T3:ES-L5', 'T3:Transfer-2'), ('T3:Transfer-1', 'T3:Transfer-2'),
        ('T3:ES-L4', 'T4:Areostat-A'), ('T3:ES-L5', 'T4:Areostat-B'),
        ('T3:Transfer-1', 'T4:Polar-1'), ('T3:Transfer-2', 'T4:Polar-2'),
        ('T4:Areostat-A', 'T4:Areostat-B'), ('T4:Polar-1', 'T4:Polar-2'),
        ('T4:Areostat-A', 'T5:Habitat-1'), ('T4:Areostat-B', 'T5:Rover-1'),
        ('T4:Polar-1', 'T5:Drone-1'), ('T4:Polar-2', 'T5:Habitat-1'),
    ]

    bfs_path = [
        'T1:Goldstone', 'T2:GEO-1', 'T3:ES-L4', 'T4:Areostat-A', 'T5:Habitat-1',
    ]
    bfs_edges = set()
    for i in range(len(bfs_path) - 1):
        e1 = (bfs_path[i], bfs_path[i + 1])
        e2 = (bfs_path[i + 1], bfs_path[i])
        bfs_edges.add(e1)
        bfs_edges.add(e2)

    for n1, n2 in edges:
        x1, y1, _ = node_positions[n1]
        x2, y2, _ = node_positions[n2]
        is_bfs = (n1, n2) in bfs_edges or (n2, n1) in bfs_edges
        if is_bfs:
            s += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{GREEN}" stroke-width="2.5" filter="url(#glow)"/>\n'
        else:
            s += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{DGRAY}" stroke-width="0.8" stroke-opacity="0.4"/>\n'

    for i, name in enumerate(bfs_path):
        nx, ny, _ = node_positions[name]
        short = name.split(':')[1]
        s += f'<circle cx="{nx}" cy="{ny}" r="{node_r + 3}" fill="none" stroke="{GREEN}" stroke-width="2" filter="url(#glow)"/>\n'
        s += f'<text x="{nx}" y="{ny - node_r - 8}" text-anchor="middle" fill="{GREEN}" font-size="9" font-weight="700" {FONT} filter="url(#glow)">&#x2605; {short}</text>\n'

    tier_label_x = 20
    tier_labels = [
        (90, 'T1: Earth Ground', CYAN),
        (190, 'T2: Earth Orbital', CYAN),
        (310, 'T3: Deep Space', PURPLE),
        (420, 'T4: Mars Orbital', ORANGE),
        (530, 'T5: Mars Surface', GOLD),
    ]
    for ly, label, color in tier_labels:
        s += f'<text x="{tier_label_x}" y="{ly}" fill="{color}" font-size="10" font-weight="600" {FONT}>{label}</text>\n'
        s += f'<rect x="10" y="{ly - 10}" width="5" height="12" rx="1" fill="{color}"/>\n'

    heatmap_x = 880
    heatmap_y = 80
    heatmap_w = 280
    heatmap_h = 200
    s += f'<rect x="{heatmap_x}" y="{heatmap_y}" width="{heatmap_w}" height="{heatmap_h}" rx="6" fill="rgba(13,17,23,0.95)" stroke="{DGRAY}" stroke-opacity="0.4"/>\n'
    s += f'<text x="{heatmap_x + 10}" y="{heatmap_y + 18}" fill="{PURPLE}" font-size="11" font-weight="700" {FONT}>RL Q-Table Heatmap</text>\n'
    s += f'<text x="{heatmap_x + heatmap_w - 10}" y="{heatmap_y + 18}" text-anchor="end" fill="{DGRAY}" font-size="9" {FONT}>Q(s,a) values</text>\n'

    grid_x = heatmap_x + 20
    grid_y = heatmap_y + 30
    cell_w = 34
    cell_h = 22
    cols = 6
    rows = 7
    col_labels = ['Fwd', 'Store', 'Drop', 'Split', 'Reroute', 'Wait']
    row_labels = ['N-A', 'N-B', 'N-C', 'ES-L4', 'ES-L5', 'MRS', 'DSN']

    heat_data = [
        [0.92, 0.15, 0.02, 0.08, 0.12, 0.05],
        [0.45, 0.78, 0.03, 0.10, 0.25, 0.35],
        [0.20, 0.85, 0.01, 0.12, 0.30, 0.40],
        [0.88, 0.20, 0.05, 0.15, 0.10, 0.08],
        [0.35, 0.30, 0.02, 0.18, 0.72, 0.25],
        [0.90, 0.10, 0.01, 0.05, 0.08, 0.03],
        [0.15, 0.60, 0.01, 0.05, 0.10, 0.55],
    ]

    for i, label in enumerate(col_labels):
        lx = grid_x + i * cell_w + cell_w // 2
        s += f'<text x="{lx}" y="{grid_y - 2}" text-anchor="middle" fill="{GRAY}" font-size="7" {FONT}>{label}</text>\n'
    for j, label in enumerate(row_labels):
        ly = grid_y + j * cell_h + cell_h // 2 + 3
        s += f'<text x="{grid_x - 4}" y="{ly}" text-anchor="end" fill="{DGRAY}" font-size="7" {FONT}>{label}</text>\n'

    for j in range(rows):
        for i in range(cols):
            val = heat_data[j][i]
            if val > 0.7:
                cell_color = GREEN
                opacity = val * 0.8
            elif val > 0.4:
                cell_color = GOLD
                opacity = val * 0.7
            else:
                cell_color = DGRAY
                opacity = val * 0.5 + 0.05
            cx_pos = grid_x + i * cell_w
            cy_pos = grid_y + j * cell_h
            s += f'<rect x="{cx_pos}" y="{cy_pos}" width="{cell_w - 2}" height="{cell_h - 2}" rx="2" fill="{cell_color}" fill-opacity="{opacity:.2f}"/>\n'
            s += f'<text x="{cx_pos + cell_w // 2}" y="{cy_pos + cell_h // 2 + 3}" text-anchor="middle" fill="white" font-size="7" {FONT}>{val:.2f}</text>\n'

    s += f'<rect x="{grid_x}" y="{grid_y + rows * cell_h + 6}" width="{cols * cell_w}" height="14" rx="2" fill="{DGRAY}" fill-opacity="0.3"/>\n'
    s += f'<text x="{grid_x + cols * cell_w // 2}" y="{grid_y + rows * cell_h + 16}" text-anchor="middle" fill="{GRAY}" font-size="8" {FONT}>Low &#x2192; High Q-value (learned policy)</text>\n'

    bfs_box_y = heatmap_y + heatmap_h + 20
    s += f'<rect x="{heatmap_x}" y="{bfs_box_y}" width="{heatmap_w}" height="100" rx="6" fill="rgba(13,17,23,0.95)" stroke="{DGRAY}" stroke-opacity="0.4"/>\n'
    s += f'<text x="{heatmap_x + 10}" y="{bfs_box_y + 18}" fill="{GREEN}" font-size="11" font-weight="700" {FONT}>BFS Shortest Path</text>\n'
    path_str = ' &#x2192; '.join([n.split(':')[1] for n in bfs_path])
    s += f'<text x="{heatmap_x + 10}" y="{bfs_box_y + 38}" fill="{GREEN}" font-size="9" {FONT}>{path_str}</text>\n'
    s += f'<text x="{heatmap_x + 10}" y="{bfs_box_y + 56}" fill="{GRAY}" font-size="9" {FONT}>Hops: 4 | Latency: ~13 min</text>\n'
    s += f'<text x="{heatmap_x + 10}" y="{bfs_box_y + 72}" fill="{DGRAY}" font-size="9" {FONT}>RL agent improves on BFS via</text>\n'
    s += f'<text x="{heatmap_x + 10}" y="{bfs_box_y + 86}" fill="{DGRAY}" font-size="9" {FONT}>learned link-quality weights</text>\n'

    s += f'<rect x="30" y="{h - 70}" width="{w - 60}" height="34" rx="6" fill="{CYAN}" fill-opacity="0.06" stroke="{CYAN}" stroke-opacity="0.2"/>\n'
    s += f'<text x="{w // 2}" y="{h - 48}" text-anchor="middle" fill="{CYAN}" font-size="12" font-weight="600" {FONT}>241 Nodes &#183; 5 Tiers &#183; RL-Optimized Routing &#183; BFS Baseline + Q-Learning Enhancement</text>\n'

    s += svg_footer()
    return s, w, h


DIAGRAMS = {
    'system_architecture': generate_system_architecture,
    '5tier_network': generate_5tier_network,
    'dtn_store_and_forward': generate_dtn_store_and_forward,
    'earth_mars_journey': generate_earth_mars_journey,
    'data_flow': generate_data_flow,
    'protocol_stack': generate_protocol_stack,
    'network_topology': generate_network_topology,
}


def main():
    import cairosvg

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f'AETHERIX Diagram Generator v2')
    print(f'Output: {OUTPUT_DIR}')
    print(f'Generating {len(DIAGRAMS)} diagrams...\n')

    for name, gen_func in DIAGRAMS.items():
        print(f'  [{name}] Generating...')
        svg_content, svg_w, svg_h = gen_func()

        svg_path = os.path.join(OUTPUT_DIR, f'{name}.svg')
        png_path = os.path.join(OUTPUT_DIR, f'{name}.png')

        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f'    SVG: {svg_path} ({svg_w}x{svg_h})')

        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=png_path,
            output_width=svg_w * 2,
            output_height=svg_h * 2,
        )
        print(f'    PNG: {png_path} ({svg_w * 2}x{svg_h * 2})')

    print(f'\nDone! {len(DIAGRAMS)} diagrams generated in {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
