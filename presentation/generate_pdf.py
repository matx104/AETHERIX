#!/usr/bin/env python3
"""
AETHERIX PDF Presentation Generator
Creates a landscape PDF with the same content as the PPTX.
"""

import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "presentation", "output")
CHARTS_DIR = os.path.join(BASE_DIR, "visualizations", "charts")
DIAGRAMS_DIR = os.path.join(BASE_DIR, "visualizations", "diagrams")

os.makedirs(OUTPUT_DIR, exist_ok=True)

PAGE_W, PAGE_H = landscape(A4)

BG_DARK = HexColor("#0B0E1A")
ACCENT_BLUE = HexColor("#009EFF")
ACCENT_CYAN = HexColor("#00D4AA")
ACCENT_PURPLE = HexColor("#8B5CF6")
ACCENT_ORANGE = HexColor("#FF8C00")
ACCENT_RED = HexColor("#FF4D4D")
WHITE = HexColor("#FFFFFF")
LIGHT_GRAY = HexColor("#B0B8CC")
MED_GRAY = HexColor("#6B7B96")
CARD_BG = HexColor("#141B2D")
CARD_BORDER = HexColor("#1E2A42")
GREEN = HexColor("#2ECC71")
TABLE_ROW_ALT = HexColor("#182236")

pdf_path = os.path.join(OUTPUT_DIR, "AETHERIX_Presentation.pdf")
c = canvas.Canvas(pdf_path, pagesize=landscape(A4))


def draw_bg(c):
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def draw_accent_line(c, x, y, w, color=ACCENT_BLUE, h=3):
    c.setFillColor(color)
    c.rect(x, y, w, h, fill=1, stroke=0)


def draw_top_bar(c, color=ACCENT_BLUE):
    c.setFillColor(color)
    c.rect(0, PAGE_H - 6, PAGE_W, 6, fill=1, stroke=0)


def draw_bottom_bar(c, color=ACCENT_BLUE):
    c.setFillColor(color)
    c.rect(0, 0, PAGE_W, 6, fill=1, stroke=0)


TOTAL_SLIDES = 27
# Auto-incrementing page counter (title page is page 1 and carries no footer);
# inserting pages never requires renumbering the call sites.
_footer_counter = [1]


def draw_footer(c, num=None, total=None):
    _footer_counter[0] += 1
    n = _footer_counter[0]
    c.setFont("Helvetica", 8)
    c.setFillColor(MED_GRAY)
    c.drawString(30, 18, "AETHERIX \u2014 Interplanetary Communication Network")
    c.drawRightString(PAGE_W - 30, 18, f"{n} / {TOTAL_SLIDES}")
    if n in _SPEAKER_NOTES:
        _draw_speaker_notes(c, _SPEAKER_NOTES[n])


def draw_card(c, x, y, w, h, border_color=ACCENT_BLUE):
    c.setFillColor(CARD_BG)
    c.setStrokeColor(border_color)
    c.setLineWidth(1.5)
    c.roundRect(x, y, w, h, 5, fill=1, stroke=1)


def draw_text(c, text, x, y, font="Helvetica", size=14, color=WHITE, bold=False, align="left"):
    fn = "Helvetica-Bold" if bold else font
    c.setFont(fn, size)
    c.setFillColor(color)
    if align == "center":
        c.drawCentredString(x, y, text)
    elif align == "right":
        c.drawRightString(x, y, text)
    else:
        c.drawString(x, y, text)


def draw_multiline(c, text, x, y, font="Helvetica", size=12, color=WHITE, leading=16, bold=False):
    fn = "Helvetica-Bold" if bold else font
    c.setFont(fn, size)
    c.setFillColor(color)
    for line in text.split("\n"):
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_image_safe(c, img_path, x, y, w=None, h=None):
    if os.path.exists(img_path):
        try:
            img = ImageReader(img_path)
            iw, ih = img.getSize()
            aspect = iw / ih
            if w and not h:
                h = w / aspect
            elif h and not w:
                w = h * aspect
            elif not w and not h:
                w = iw * 0.5
                h = ih * 0.5
            c.drawImage(img_path, x, y, width=w, height=h, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass


def draw_table(c, data, x, y, col_widths, header_color=ACCENT_BLUE):
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('TEXTCOLOR', (0, 1), (-1, -1), LIGHT_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#1E2A42")),
    ])
    for i in range(1, len(data)):
        bg = CARD_BG if i % 2 == 1 else TABLE_ROW_ALT
        style.add('BACKGROUND', (0, i), (-1, i), bg)

    t = Table(data, colWidths=col_widths)
    t.setStyle(style)
    tw, th = t.wrap(0, 0)
    t.drawOn(c, x, y - th)
    return th


_SPEAKER_NOTES = {
    1: "State your name clearly. Read the topic number and title exactly as on the exam paper. Pause to let examiners see it. Point to the logo. This is your first impression. (30 seconds)",
    2: "Quick overview of what we will cover. 13 topics across 29 slides. About 20 minutes. (20 seconds)",
    3: "This slide sets up the narrative arc. First explain what AETHERIX is in plain language - it's like the postal service for interplanetary space. Then pivot to the problem: TCP/IP was never designed for space. 22-minute delays break every assumption. Solar conjunction blackouts. Static routing. Vulnerable crypto. Each problem maps to one of our solutions. (1.5 minutes)",
    4: "Start with the scale. 54.6M to 401M km. Light itself takes 3-22 minutes one way. TCP/IP was designed for sub-second round trips. In space, by the time a packet acknowledgment returns, the link may be gone. Solar conjunction causes 2-week blackout. This is why NASA calls it Delay-Tolerant Networking. (1.5 minutes)",
    5: "The key insight: instead of requiring an end-to-end connection like TCP, DTN works like the postal service. Each node takes custody of your data and forwards it when a link becomes available. Three pillars: BPv7 for the protocol, RL for intelligent routing, QKD for security. (1.5 minutes)",
    6: "Show the architecture. Six core modules feed into the simulation engine, which feeds the web showcase. Standards compliance at the bottom. Point to each module as you explain. (1 minute)",
    7: "Architecture diagram showing source modules feeding simulation engine and web demos.",
    8: "BPv7 is the postal service protocol. Walk through the stack: Application at top, BPv7 as the store-and-forward layer, three convergence layers for different link types, physical at bottom. Custody transfer is the key innovation - each node takes legal responsibility. Priority P0 (emergency) to P4 (bulk). (2 minutes)",
    9: "Walk through the store-and-forward process. Bundle arrives, gets stored, node waits for next contact opportunity, then forwards. If link drops, bundle stays stored and retries. No data loss. This is fundamentally different from TCP's end-to-end retransmission. (1.5 minutes)",
    10: "241 nodes across 5 tiers. Walk through each tier. Earth Ground is the DSN - three stations around the globe for 24/7 coverage. Earth Orbital has LEO laser mesh for optical backhaul. Deep Space has Lagrange point relays - these are the critical innovation for conjunction coverage. Mars Orbital has areostationary relays at 17,032 km. Mars Surface is the most populated tier. (2 minutes)",
    11: "Visual overview of the 5-tier topology with 3 redundant paths.",
    12: "Network topology visualization.",
    13: "RUN THE LIVE DEMO from the Link Budget page. Show the 3 distance scenarios. 1550nm was chosen for telecom heritage and eye safety. FSPL at average distance is -365 dB. The telescope apertures are realistic for spacecraft. RF backup for reliability. (2 minutes)",
    14: "Interactive journey visualization.",
    15: "CGR is what NASA uses today. It's static - you have to pre-compute schedules. Our RL agent learns from experience. 8 state variables, 4 actions. The reward function balances delivery probability against delay, hops, drops, and energy. Multi-agent federated learning means agents at each node share knowledge. (2 minutes)",
    16: "BB84 is beautifully simple: send qubits, measure, compare bases, check QBER. If QBER is below 11%, no one listened in. CASCADE reconciliation and privacy amplification clean the key. E91 uses entanglement. Quantum repeaters at Lagrange points extend range. Post-quantum crypto as backup layer. (2 minutes)",
    17: "Mars and Earth dance around the Sun with a 26-month synodic period. Everything changes - distance, delay, bandwidth. At opposition we get great bandwidth. At conjunction, the Sun blocks everything. Our Lagrange relays at ES-L4 and ES-L5 maintain 50-70% capacity during conjunction. Doppler shift of 15 GHz at optical wavelengths requires real-time compensation. (1.5 minutes)",
    18: "Space radiation is relentless. SEUs flip bits constantly - about 37,000 during a Mars transit. Our defense-in-depth: TMR masks logic faults (3,334x reliability gain), SECDED ECC corrects single-bit errors, scrubbing prevents double-bit accumulation, and FDIR with a watchdog catches everything else. The RAD750 can tolerate 200 krad - far above what a Mars mission needs. (1.5 minutes)",
    19: "Like an emergency room. P0 emergency gets sent immediately - it can even preempt an in-progress transfer. P1 mission-critical next. P2 routine science. P4 bulk data fills remaining bandwidth. Compression multiplies effective capacity: 3x for telemetry, 10x for images, 50x for video. Our scheduler keeps the link at 100% utilization by fragmenting large bundles. (1.5 minutes)",
    20: "Walk through the 7-hop journey. 500MB from Perseverance to JPL. Total transit ~13 min vs 12.5 min light-time - near speed of light! DTN overhead under 5%. Key point: if link drops at hop 5, the bundle stays stored at hop 4 and retries. No data loss. RUN LIVE DEMO if time permits. (2 minutes)",
    21: "End-to-end bundle journey through all protocol layers.",
    22: "Visual data flow through the protocol stack.",
    23: "Hit these numbers with confidence. 10-100x faster. >95% availability vs 60-75%. Quantum-secure. 241 nodes vs 5-10 assets. The conjunction improvement is thanks to Lagrange relays. All metrics are backed by our simulation engine. (1 minute)",
    24: "This is real, working code. 27 Python modules, 189 tests, 12 interactive demos. All the physics is real - no mocked data. The showcase site has live calculators you can use right now. Standards compliance is complete - CCSDS, IETF, and NIST. (1.5 minutes)",
    25: "Phases 1-4 are done - this is what you see today. Phase 5: ns-3 simulation for realistic network modeling. Phase 6: Upgrade to DQN and integrate with NASA's ION-DTN implementation. Phase 7: Hardware prototypes with SDRs and optical links. (1.5 minutes)",
    26: "Summarize the problem and solution clearly. Re-read the exam topic verbatim. Point to the numbers. Offer to show live demos or answer questions. Thank the examiners. (1 minute)",
    27: "Summarize the four key numbers: 10-100x faster, >95% availability, AI-powered routing, quantum-secure. Invite questions confidently. Make eye contact. Point to the live demo link. Thank the audience. (30 seconds)",
}


def _draw_speaker_notes(c, text):
    c.saveState()
    nf = "Helvetica-Oblique"
    ns = 6
    lh = 7.5
    ml = 4
    bh = 14 + lh * ml
    by = 30
    c.setFillColor(Color(0.04, 0.05, 0.10, alpha=0.92))
    c.rect(25, by, PAGE_W - 50, bh, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFD93D"))
    c.setFont("Helvetica-Bold", 6)
    c.drawString(30, by + bh - 10, "Speaker Notes:")
    c.setFillColor(HexColor("#B0B8CC"))
    c.setFont(nf, ns)
    mw = PAGE_W - 65
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        t = cur + (" " if cur else "") + w
        if c.stringWidth(t, nf, ns) <= mw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    y = by + bh - 20
    for i, ln in enumerate(lines[:ml]):
        c.drawString(30, y - lh * i, ln)
    c.restoreState()


# ================================================================
# PAGE 1 — Title
# ================================================================
print("Creating Page 1: Title...")
draw_bg(c)
draw_top_bar(c)
draw_bottom_bar(c)

draw_text(c, "AETHERIX", PAGE_W / 2, PAGE_H - 120, size=52, color=WHITE, bold=True, align="center")
draw_accent_line(c, PAGE_W / 2 - 100, PAGE_H - 140, 200, ACCENT_CYAN, 4)
draw_text(c, "Autonomous Extraterrestrial High-throughput Enhancing Routing", PAGE_W / 2, PAGE_H - 175, size=16, color=ACCENT_CYAN, align="center")
draw_text(c, "and Inter-planetary eXchange", PAGE_W / 2, PAGE_H - 195, size=16, color=ACCENT_CYAN, align="center")
draw_text(c, "Building an Interplanetary Communication Network with DTN,", PAGE_W / 2, PAGE_H - 235, size=13, color=LIGHT_GRAY, align="center")
draw_text(c, "Quantum Communication, and Space-Based Infrastructure for Mars Mission Support", PAGE_W / 2, PAGE_H - 250, size=13, color=LIGHT_GRAY, align="center")
draw_accent_line(c, PAGE_W / 2 - 150, PAGE_H - 275, 300, ACCENT_BLUE, 2)
draw_text(c, "Muhammad Abdullah Tariq", PAGE_W / 2, PAGE_H - 310, size=18, color=WHITE, bold=True, align="center")
draw_text(c, "EduQual Level 6 Diploma in AI Operations  |  Topic 59  |  January 2026", PAGE_W / 2, PAGE_H - 335, size=12, color=MED_GRAY, align="center")
draw_text(c, "matx104.github.io/AETHERIX  |  github.com/matx104/AETHERIX", PAGE_W / 2, PAGE_H - 390, size=11, color=ACCENT_BLUE, align="center")
_draw_speaker_notes(c, _SPEAKER_NOTES[1])
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

draw_footer(c, 2)
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
    "  \u2022  Earth-Mars: 54.6M \u2013 401M km distance",
    "  \u2022  One-way light delay: 3 \u2013 22 minutes",
    "  \u2022  Solar conjunction: 2-week total blackout",
    "  \u2022  TCP/IP fundamentally cannot work",
    "  \u2022  Current systems: 0.5 \u2013 6 Mbps only",
]
for i, line in enumerate(prob_lines):
    draw_text(c, line, 495, PAGE_H - 140 - 17 * i, size=10, color=LIGHT_GRAY)

draw_card(c, 40, PAGE_H - 380, 820, 80, ACCENT_CYAN)
draw_text(c, "AETHERIX delivers a complete interplanetary networking solution", 55, PAGE_H - 325, size=12, color=ACCENT_CYAN, bold=True)
draw_text(c, "combining DTN protocols, AI-driven routing, quantum-secure keys, and hybrid optical/RF links for Mars mission support.", 55, PAGE_H - 345, size=10, color=LIGHT_GRAY)

stats = [("10-100\u00d7", "Faster", ACCENT_BLUE), (">95%", "Availability", GREEN), ("241", "Nodes", ACCENT_ORANGE), ("149", "Tests", ACCENT_PURPLE)]
for i, (val, label, color) in enumerate(stats):
    x = 40 + 210 * i
    draw_card(c, x, 60, 195, 55, color)
    draw_text(c, val, x + 97, 95, size=18, color=color, bold=True, align="center")
    draw_text(c, label, x + 97, 72, size=10, color=LIGHT_GRAY, align="center")

draw_footer(c, 3)
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
    ["RTT < 1 second", "6 \u2013 44 min RTT", "Timeout failure"],
    ["Always connected", "Scheduled contacts", "Connection drops"],
    ["End-to-end path", "No persistent path", "Routing impossible"],
    ["Fast acknowledgments", "ACKs take minutes", "Window collapse"],
    ["Low packet loss", "High loss (optical)", "Retransmit storms"],
]
draw_table(c, tcp_data, 40, PAGE_H - 270, [160, 160, 140], ACCENT_RED)

draw_card(c, 460, PAGE_H - 460, 400, 90, ACCENT_ORANGE)
draw_text(c, '"At aphelion, a single ping-pong takes 44 minutes.', 475, PAGE_H - 395, size=11, color=ACCENT_ORANGE)
draw_text(c, 'No TCP session can survive that. We need an entirely', 475, PAGE_H - 412, size=11, color=ACCENT_ORANGE)
draw_text(c, 'different networking paradigm."', 475, PAGE_H - 429, size=11, color=ACCENT_ORANGE)

draw_image_safe(c, os.path.join(CHARTS_DIR, "distance_over_time.png"), 460, 60, w=400)

draw_footer(c, 4)
c.showPage()


# ================================================================
# PAGE 5 — The Answer (DTN)
# ================================================================
print("Creating Page 5: The Answer (DTN)...")
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
    draw_card(c, x, PAGE_H - 330, 265, 120, col)
    draw_text(c, title, x + 15, PAGE_H - 225, size=16, color=col, bold=True)
    draw_text(c, sub, x + 15, PAGE_H - 245, size=10, color=MED_GRAY)
    for j, line in enumerate(desc.split("\n")):
        draw_text(c, line, x + 15, PAGE_H - 268 - 15 * j, size=9, color=LIGHT_GRAY)

draw_card(c, 40, PAGE_H - 430, 820, 70, ACCENT_CYAN)
draw_text(c, "Key Insight: DTN moves reliability from end-to-end to hop-by-hop. Each custodian is responsible until", 55, PAGE_H - 385, size=11, color=ACCENT_CYAN, bold=True)
draw_text(c, "the next node accepts custody \u2014 enabling communication even with 44-minute round-trip delays.", 55, PAGE_H - 402, size=10, color=LIGHT_GRAY)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "dtn_store_and_forward.png"), 40, 50, w=820)

draw_footer(c, 5)
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

draw_footer(c, 6)
c.showPage()


# ================================================================
# PAGE 7 — Architecture Diagram
# ================================================================
print("Creating Page 7: Architecture Diagram...")
draw_bg(c)
draw_text(c, "SYSTEM ARCHITECTURE DIAGRAM", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_accent_line(c, 40, PAGE_H - 62, 200, ACCENT_BLUE)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "system_architecture.png"), 40, 30, w=PAGE_W - 80, h=PAGE_H - 110)

draw_footer(c, 7)
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
    "RFC 9171 \u2014 Bundle Protocol Version 7",
    "RFC 4838 \u2014 DTN Architecture",
    "RFC 5326 \u2014 Licklider Transmission Protocol",
    "RFC 9172 \u2014 Bundle Protocol Security (BPSec)",
    "CCSDS 734.2-B-1 \u2014 CCSDS Bundle Protocol",
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

draw_image_safe(c, os.path.join(CHARTS_DIR, "bundle_priority_classes.png"), 40, 40, w=400)

draw_footer(c, 8)
c.showPage()


# ================================================================
# PAGE 9 — DTN Store-and-Forward
# ================================================================
print("Creating Page 9: DTN Store-and-Forward...")
draw_bg(c)
draw_text(c, "DTN STORE-AND-FORWARD", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "How Bundles Traverse the Interplanetary Network", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_CYAN)

draw_card(c, 40, PAGE_H - 220, 400, 120, ACCENT_RED)
draw_text(c, "TCP/IP FAILS", 55, PAGE_H - 115, size=14, color=ACCENT_RED, bold=True)
tcp_fails = [
    "\u2022  Timeout at 44 min RTT \u2192 connection reset",
    "\u2022  No persistent path \u2192 routing impossible",
    "\u2022  ACKs take minutes \u2192 window collapse",
    "\u2022  High BER \u2192 retransmission storms",
    "\u2022  Solar conjunction \u2192 total blackout",
]
for i, line in enumerate(tcp_fails):
    draw_text(c, line, 55, PAGE_H - 140 - 16 * i, size=9, color=LIGHT_GRAY)

draw_card(c, 460, PAGE_H - 220, 400, 120, GREEN)
draw_text(c, "DTN WORKS", 475, PAGE_H - 115, size=14, color=GREEN, bold=True)
dtn_works = [
    "\u2022  No end-to-end connection required",
    "\u2022  Store locally \u2192 wait for contact window",
    "\u2022  Custody transfer: hop-by-hop reliability",
    "\u2022  Priority classes: P0\u2013P4 for urgency",
    "\u2022  Works through conjunction via Lagrange relays",
]
for i, line in enumerate(dtn_works):
    draw_text(c, line, 475, PAGE_H - 140 - 16 * i, size=9, color=LIGHT_GRAY)

cl_cards = [
    ("LTP", "Licklider Transmission Protocol", "Deep space segment\nRFC 5326\nSegmentation + retransmission", ACCENT_PURPLE),
    ("TCPCL", "TCP Convergence Layer", "Earth segment\nRFC 7242\nReliable ordered delivery", ACCENT_BLUE),
    ("UDP-CL", "UDP Convergence Layer", "Optical ISL\nLow-latency\nMinimal overhead", ACCENT_ORANGE),
]
for i, (name, full, desc, col) in enumerate(cl_cards):
    x = 40 + 280 * i
    draw_card(c, x, PAGE_H - 390, 265, 140, col)
    draw_text(c, name, x + 15, PAGE_H - 265, size=16, color=col, bold=True)
    draw_text(c, full, x + 15, PAGE_H - 283, size=9, color=MED_GRAY)
    for j, line in enumerate(desc.split("\n")):
        draw_text(c, line, x + 15, PAGE_H - 306 - 15 * j, size=9, color=LIGHT_GRAY)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "dtn_store_and_forward.png"), 40, 40, w=820)

draw_footer(c, 9)
c.showPage()


# ================================================================
# PAGE 10 — Network Topology
# ================================================================
print("Creating Page 10: Network Topology...")
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

draw_image_safe(c, os.path.join(CHARTS_DIR, "network_tier_distribution.png"), 40, 50, w=400)

draw_footer(c, 10)
c.showPage()


# ================================================================
# PAGE 11 — 5-Tier Network Detail
# ================================================================
print("Creating Page 11: 5-Tier Network Detail...")
draw_bg(c)
draw_text(c, "5-TIER NETWORK \u2014 DETAILED BREAKDOWN", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Tier Composition and Link Characteristics", 40, PAGE_H - 75, size=14, color=ACCENT_BLUE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_BLUE)

tier_data = [
    ["Tier", "Location", "Nodes", "Key Assets", "Role"],
    ["T1", "Earth Ground", "6", "DSN stations, MOC", "Gateway & control"],
    ["T2", "Earth Orbital", "51", "GEO relays, LEO lasers", "Aggregation"],
    ["T3", "Deep Space", "4", "ES-L4, ES-L5 relays", "Conjunction coverage"],
    ["T4", "Mars Orbital", "4", "Areo + polar orbiters", "Mars relay"],
    ["T5", "Mars Surface", "176", "Bases, rovers, sensors", "End users"],
]
draw_table(c, tier_data, 40, PAGE_H - 100, [40, 100, 50, 170, 140], ACCENT_BLUE)

link_data = [
    ["Segment", "Technology", "Data Rate", "Latency", "Availability"],
    ["Earth \u2194 Earth Orbit", "Fiber + laser", "1\u2013100 Gbps", "~120 ms", "99.9%"],
    ["Earth \u2194 Mars (optical)", "1550 nm laser", "2\u2013200 Mbps", "4\u201324 min", "85\u201395%"],
    ["Earth \u2194 Mars (RF)", "Ka-band", "0.5\u20136 Mbps", "4\u201324 min", "90\u201398%"],
    ["Mars Orbit \u2194 Surface", "UHF + optical", "2\u2013100 Mbps", "2\u201340 ms", "70\u201390%"],
    ["Inter-Satellite (ISL)", "Optical crosslink", "1\u201310 Gbps", "1\u201310 ms", "98%"],
]
draw_table(c, link_data, 40, PAGE_H - 280, [130, 100, 100, 80, 80], GREEN)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "network_topology.png"), 40, 40, w=820)

draw_footer(c, 11)
c.showPage()


# ================================================================
# PAGE 12 — Network Diagram Visual
# ================================================================
print("Creating Page 12: Network Diagram Visual...")
draw_bg(c)
draw_text(c, "5-TIER NETWORK DIAGRAM", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "241 Nodes from Earth to Mars Surface", 40, PAGE_H - 75, size=14, color=GREEN)
draw_accent_line(c, 40, PAGE_H - 85, 200, GREEN)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "5tier_network.png"), 40, 30, w=PAGE_W - 80, h=PAGE_H - 110)

draw_footer(c, 12)
c.showPage()


# ================================================================
# PAGE 13 — Optical Communications
# ================================================================
print("Creating Page 13: Optical Communications...")
draw_bg(c)
draw_text(c, "OPTICAL COMMUNICATIONS", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "1550 nm Laser \u2014 10\u2013100\u00d7 Faster Than RF", 40, PAGE_H - 75, size=14, color=ACCENT_ORANGE)
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

draw_text(c, "KEY EQUATIONS", 40, PAGE_H - 220, size=12, color=ACCENT_CYAN, bold=True)
eqs = [
    "FSPL = (4\u03c0d/\u03bb)\u00b2          Free-Space Path Loss",
    "G = (\u03c0D/\u03bb)\u00b2             Antenna Gain",
    "Pr = Pt \u00b7 Gt \u00b7 Gr / FSPL   Received Power",
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

draw_image_safe(c, os.path.join(CHARTS_DIR, "link_budget_breakdown.png"), 500, PAGE_H - 350, w=380)

draw_image_safe(c, os.path.join(CHARTS_DIR, "data_rate_vs_distance.png"), 40, 40, w=400)

draw_footer(c, 13)
c.showPage()


# ================================================================
# PAGE 14 — Earth-Mars Journey
# ================================================================
print("Creating Page 14: Earth-Mars Journey...")
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
    ("~13 min", "Total Transfer", GREEN),
    ("98.7%", "Delivery Ratio", ACCENT_BLUE),
    ("15 Mbps", "Throughput", ACCENT_CYAN),
    ("7 hops", "Path Length", ACCENT_ORANGE),
]
for i, (val, label, col) in enumerate(metric_cards):
    x = 40 + 220 * i
    draw_card(c, x, PAGE_H - 310, 210, 55, col)
    draw_text(c, val, x + 105, PAGE_H - 272, size=16, color=col, bold=True, align="center")
    draw_text(c, label, x + 105, PAGE_H - 290, size=10, color=LIGHT_GRAY, align="center")

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "earth_mars_journey.png"), 40, 50, w=820)

draw_footer(c, 14)
c.showPage()


# ================================================================
# PAGE 15 — RL Routing
# ================================================================
print("Creating Page 15: RL Routing...")
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
    "\u2022  Reward: \u03b1(delivery) - \u03b2(delay) - \u03b3(hops)",
    "\u2022  Federated learning across agents",
    "\u2022  Auto-recovery in seconds, not hours",
]
for i, line in enumerate(rl_lines):
    draw_text(c, line, 445, PAGE_H - 138 - 16 * i, size=9, color=LIGHT_GRAY)

result_cards = [
    ("97%", "Delivery Ratio", "+5% vs CGR", GREEN),
    ("-20%", "Delivery Time", "1.2\u00d7 light-time", ACCENT_CYAN),
    ("3600\u00d7", "Recovery Speed", "Auto vs manual", ACCENT_ORANGE),
]
for i, (val, title, desc, col) in enumerate(result_cards):
    x = 40 + 280 * i
    draw_card(c, x, PAGE_H - 370, 265, 110, col)
    draw_text(c, val, x + 15, PAGE_H - 285, size=22, color=col, bold=True)
    draw_text(c, title, x + 15, PAGE_H - 308, size=12, color=WHITE, bold=True)
    draw_text(c, desc, x + 15, PAGE_H - 325, size=9, color=MED_GRAY)

draw_image_safe(c, os.path.join(CHARTS_DIR, "rl_routing_heatmap.png"), 40, 40, w=400)
draw_image_safe(c, os.path.join(CHARTS_DIR, "energy_efficiency.png"), 460, 40, w=400)

draw_footer(c, 15)
c.showPage()


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
    "4. QBER estimation: < 11% = SECURE, \u2265 11% = ABORT",
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
draw_text(c, "Kyber (ML-KEM) \u2014 Key encapsulation", 495, PAGE_H - 238, size=10, color=LIGHT_GRAY)
draw_text(c, "Dilithium (ML-DSA) \u2014 Digital signatures", 495, PAGE_H - 255, size=10, color=LIGHT_GRAY)
draw_text(c, "Hybrid: QKD + PQC for defense in depth", 495, PAGE_H - 272, size=9, color=MED_GRAY)

draw_image_safe(c, os.path.join(CHARTS_DIR, "qkd_security.png"), 40, 40, w=400)
draw_image_safe(c, os.path.join(CHARTS_DIR, "qkd_key_rate.png"), 460, 40, w=400)

draw_footer(c, 16)
c.showPage()


# ================================================================
# PAGE 17 — Orbital Mechanics
# ================================================================
print("Creating Page 17: Orbital Mechanics...")
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

draw_image_safe(c, os.path.join(CHARTS_DIR, "distance_over_time.png"), 40, 40, w=400)
draw_image_safe(c, os.path.join(CHARTS_DIR, "contact_windows.png"), 460, 40, w=400)

draw_footer(c, 17)
c.showPage()


# ================================================================
# PAGE 18 — Radiation-Hardened Computing
# ================================================================
print("Creating Page 18: Radiation-Hardened Computing...")
draw_bg(c)
draw_text(c, "RADIATION-HARDENED COMPUTING", 40, PAGE_H - 50, size=26, color=WHITE, bold=True)
draw_text(c, "Surviving SEUs, latchup and total dose en route to Mars", 40, PAGE_H - 73, size=13, color=ACCENT_RED)
draw_accent_line(c, 40, PAGE_H - 83, 180, ACCENT_RED)

rad_effects = [
    ["Effect", "What it does", "Mitigation"],
    ["SEU", "Single bit flip", "SECDED ECC"],
    ["MBU", "Multi-bit flip (1 ion)", "Bit interleaving"],
    ["SEL", "Latchup (destructive)", "Current limit + power-cycle"],
    ["TID", "Cumulative dose", "Rad-hard parts (RAD750)"],
]
draw_table(c, rad_effects, 40, PAGE_H - 95, [70, 150, 170], ACCENT_RED)

draw_text(c, "DEFENSE-IN-DEPTH STACK", 470, PAGE_H - 100, size=13, color=ACCENT_RED, bold=True)
rad_stack = [
    "TMR — triple replicas, majority vote (masks logic faults)",
    "SECDED (39,32) ECC — correct 1 bit, detect 2",
    "Scrubbing — rewrite memory before a 2nd upset lands",
    "FDIR + watchdog — detect, isolate, reset, SAFE-MODE",
]
for i, s in enumerate(rad_stack):
    draw_text(c, "•  " + s, 470, PAGE_H - 125 - 20 * i, size=10, color=LIGHT_GRAY)

rad_stats = [
    ("200x", "Fewer errors (ECC + scrub + interleave)", ACCENT_CYAN),
    ("3,334x", "TMR reliability gain (p=1e-4/op)", ACCENT_BLUE),
    ("200 krad", "RAD750 TID tolerance (>2000x margin)", ACCENT_ORANGE),
    ("~0.9/day", "Residual uncorrectable, Mars transit", ACCENT_PURPLE),
]
for i, (val, lab, col) in enumerate(rad_stats):
    x = 40 + i * 198
    draw_card(c, x, 120, 188, 70, col)
    draw_text(c, val, x + 14, 168, size=20, color=col, bold=True)
    draw_text(c, lab, x + 14, 140, size=8, color=LIGHT_GRAY)

draw_multiline(c, "Model: 512 Mbit, ~210-day GCR cruise. ~37,000 raw bit upsets reduced to ~186 uncorrectable\nover the mission. Heritage: NASA RAD750 (Curiosity/Perseverance), ESA LEON3FT.  ->  src/computing/radiation.py",
               40, 95, size=9, color=MED_GRAY, leading=13)
draw_footer(c, 18)
c.showPage()


# ================================================================
# PAGE 19 — Mission-Critical Data Prioritization
# ================================================================
print("Creating Page 19: Data Prioritization...")
draw_bg(c)
draw_text(c, "MISSION-CRITICAL DATA PRIORITIZATION", 40, PAGE_H - 50, size=24, color=WHITE, bold=True)
draw_text(c, "Bandwidth triage: get the right bits home first", 40, PAGE_H - 73, size=13, color=ACCENT_ORANGE)
draw_accent_line(c, 40, PAGE_H - 83, 180, ACCENT_ORANGE)

tiers = [
    ["Tier", "Class", "Examples"],
    ["P0", "Emergency / Safety", "Health telemetry, collision avoidance"],
    ["P1", "Mission-critical", "Command ACKs, time-sensitive science"],
    ["P2", "High-priority", "Routine telemetry, scheduled science"],
    ["P4", "Low / Bulk", "Housekeeping logs, file transfers"],
]
draw_table(c, tiers, 40, PAGE_H - 95, [50, 130, 230], ACCENT_ORANGE)

comp = [
    ["Data type", "Standard", "Ratio"],
    ["Telemetry", "CCSDS 121", "3x"],
    ["Imagery (lossy)", "CCSDS 122", "10x"],
    ["Video", "H.265", "50x"],
]
draw_table(c, comp, 480, PAGE_H - 95, [110, 100, 60], ACCENT_PURPLE)

pri_stats = [
    ("100%", "Link utilization (no wasted bandwidth)", ACCENT_CYAN),
    ("5 / 6", "Items fully delivered by priority", GREEN),
    ("BPv7", "Fragmentation defers bulk remainder", ACCENT_BLUE),
    ("Preempt", "Emergency uses direct-to-Earth backup", ACCENT_RED),
]
for i, (val, lab, col) in enumerate(pri_stats):
    x = 40 + i * 198
    draw_card(c, x, 120, 188, 70, col)
    draw_text(c, val, x + 14, 168, size=18, color=col, bold=True)
    draw_text(c, lab, x + 14, 140, size=8, color=LIGHT_GRAY)

draw_multiline(c, "Scenario: 30 Mbps, 15-min contact, oversubscribed. Deadline-aware, preemptive QoS scheduler\ndelivers emergency + mission + science first; 6 GB software update fragmented to the next pass.  ->  src/routing/prioritization.py",
               40, 95, size=9, color=MED_GRAY, leading=13)
draw_footer(c, 19)
c.showPage()


# ================================================================
# PAGE 20 — End-to-End Mission
# ================================================================
print("Creating Page 20: End-to-End Mission...")
draw_bg(c)
draw_text(c, "END-TO-END MISSION SCENARIO", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Perseverance 500 MB Science Data Upload", 40, PAGE_H - 75, size=14, color=ACCENT_ORANGE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_ORANGE)

route_data = [
    ["Hop", "Node", "Action", "Protocol", "Time"],
    ["1", "Perseverance", "Create bundle", "BPv7", "T+0s"],
    ["2", "MRS-Alpha", "Store & forward", "UHF", "T+5s"],
    ["3", "MRS-Polar", "RL route select", "Optical ISL", "T+10s"],
    ["4", "ES-L5 Relay", "Custody transfer", "1550nm laser", "T+750s"],
    ["5", "LEO-42", "Forward", "Optical ISL", "T+751s"],
    ["6", "DSN Madrid", "Receive + verify", "Fiber", "T+752s"],
    ["7", "JPL MOC", "Delivery \u2713", "TCPCL", "T+754s"],
]
draw_table(c, route_data, 40, PAGE_H - 100, [40, 90, 100, 80, 60], ACCENT_ORANGE)

metric_cards = [
    ("~13 min", "Transfer Time", GREEN),
    ("98.7%", "Delivery Ratio", ACCENT_BLUE),
    ("15 Mbps", "Throughput", ACCENT_CYAN),
    ("7 hops", "Path Length", ACCENT_ORANGE),
]
for i, (val, label, col) in enumerate(metric_cards):
    x = 40 + 220 * i
    draw_card(c, x, PAGE_H - 290, 210, 55, col)
    draw_text(c, val, x + 105, PAGE_H - 252, size=16, color=col, bold=True, align="center")
    draw_text(c, label, x + 105, PAGE_H - 270, size=10, color=LIGHT_GRAY, align="center")

draw_card(c, 40, PAGE_H - 430, 820, 100, ACCENT_RED)
draw_text(c, "FAILURE SCENARIO", 55, PAGE_H - 345, size=13, color=ACCENT_RED, bold=True)
draw_text(c, "If optical link drops at Hop 4 (ES-L5):", 55, PAGE_H - 365, size=10, color=LIGHT_GRAY)
draw_text(c, "\u2022  Bundle stored at MRS-Polar with custody \u2022  RL agent reroutes via ES-L4 alternate path", 55, PAGE_H - 382, size=10, color=LIGHT_GRAY)
draw_text(c, "\u2022  Delay: ~30 minutes additional  \u2022  Data: NOT LOST \u2014 store-and-forward guarantees delivery", 55, PAGE_H - 399, size=10, color=LIGHT_GRAY)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "earth_mars_journey.png"), 40, 40, w=820)

draw_footer(c, 18)
c.showPage()


# ================================================================
# PAGE 19 — Data Flow Diagram
# ================================================================
print("Creating Page 19: Data Flow Diagram...")
draw_bg(c)
draw_text(c, "DATA FLOW \u2014 APPLICATION TO DELIVERY", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "How Data Travels Through the AETHERIX Stack", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_CYAN)

draw_text(c, "APPLICATION \u2192 TRANSPORT", 40, PAGE_H - 110, size=14, color=ACCENT_BLUE, bold=True)
app_steps = [
    ("1. CREATE", "Application generates payload (science data, commands)", ACCENT_BLUE),
    ("2. ENCODE", "BPv7 primary block + payload block + security block", ACCENT_CYAN),
    ("3. PRIORITY", "Assign P0\u2013P4 priority class and lifetime timer", ACCENT_PURPLE),
    ("4. QUEUE", "Bundle enters priority queue at source node", ACCENT_ORANGE),
]
for i, (step, desc, col) in enumerate(app_steps):
    y = PAGE_H - 145 - 40 * i
    draw_card(c, 40, y - 25, 820, 35, col)
    draw_text(c, step, 55, y - 2, size=11, color=col, bold=True)
    draw_text(c, desc, 180, y - 2, size=10, color=LIGHT_GRAY)

draw_text(c, "CONVERGENCE \u2192 PHYSICAL \u2192 DELIVERY", 40, PAGE_H - 320, size=14, color=GREEN, bold=True)
phy_steps = [
    ("5. CONVERGENCE", "Select CL: LTP (deep space) / TCPCL (Earth) / UDP-CL (ISL)", GREEN),
    ("6. SEGMENT", "Fragment into LTP blocks, add segmentation headers", ACCENT_CYAN),
    ("7. TRANSMIT", "Physical layer: 1550nm laser or Ka-band RF", ACCENT_ORANGE),
    ("8. RECEIVE", "Next hop reassembles, accepts custody, forwards", ACCENT_BLUE),
]
for i, (step, desc, col) in enumerate(phy_steps):
    y = PAGE_H - 355 - 40 * i
    draw_card(c, 40, y - 25, 820, 35, col)
    draw_text(c, step, 55, y - 2, size=11, color=col, bold=True)
    draw_text(c, desc, 180, y - 2, size=10, color=LIGHT_GRAY)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "dtn_store_and_forward.png"), 40, 40, w=820)

draw_footer(c, 19)
c.showPage()


# ================================================================
# PAGE 20 — Data Flow Diagram Visual
# ================================================================
print("Creating Page 20: Data Flow Diagram Visual...")
draw_bg(c)
draw_text(c, "DATA FLOW DIAGRAM", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Complete Data Path from Mars Surface to Earth Control", 40, PAGE_H - 75, size=14, color=ACCENT_CYAN)
draw_accent_line(c, 40, PAGE_H - 85, 200, ACCENT_CYAN)

draw_image_safe(c, os.path.join(DIAGRAMS_DIR, "data_flow.png"), 40, 30, w=PAGE_W - 80, h=PAGE_H - 110)

draw_footer(c, 20)
c.showPage()


# ================================================================
# PAGE 21 — Performance
# ================================================================
print("Creating Page 21: Performance...")
draw_bg(c)
draw_text(c, "AETHERIX vs CURRENT SYSTEMS", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "Head-to-Head Performance Comparison", 40, PAGE_H - 75, size=14, color=GREEN)
draw_accent_line(c, 40, PAGE_H - 85, 180, GREEN)

comp_data = [
    ["Metric", "Current (MRO)", "AETHERIX", "Improvement"],
    ["Downlink rate", "0.5\u20136 Mbps", "2\u2013200 Mbps", "10\u2013100\u00d7"],
    ["Daily volume", "5\u201310 GB", "50\u2013100 GB", "10\u201320\u00d7"],
    ["Availability", "60\u201375%", ">95%", "+20\u201335%"],
    ["Routing", "Static (CGR)", "RL-adaptive", "+20\u201340%"],
    ["Security", "AES-256", "QKD + PQC", "Future-proof"],
    ["Scalability", "5\u201310 assets", "241 nodes", "10\u2013100\u00d7"],
    ["Conjunction", "Blackout", "50\u201370% via L4/L5", "+50\u201370%"],
    ["Recovery time", "Manual (hours)", "Auto (seconds)", "3600\u00d7"],
]
draw_table(c, comp_data, 40, PAGE_H - 100, [100, 100, 120, 110], GREEN)

draw_image_safe(c, os.path.join(CHARTS_DIR, "performance_comparison.png"), 40, 40, w=400)
draw_image_safe(c, os.path.join(CHARTS_DIR, "optical_vs_rf_radar.png"), 460, 40, w=400)

draw_footer(c, 21)
c.showPage()


# ================================================================
# PAGE 22 — Implementation
# ================================================================
print("Creating Page 22: Implementation...")
draw_bg(c)
draw_text(c, "IMPLEMENTATION", 40, PAGE_H - 50, size=28, color=WHITE, bold=True)
draw_text(c, "18 Modules, 149 Tests, Full Python Stack", 40, PAGE_H - 75, size=14, color=ACCENT_BLUE)
draw_accent_line(c, 40, PAGE_H - 85, 180, ACCENT_BLUE)

impl_cards = [
    ("18", "Source Modules", ACCENT_BLUE),
    ("149", "Unit Tests", GREEN),
    ("241", "Network Nodes", ACCENT_ORANGE),
    ("6", "Interactive Demos", ACCENT_PURPLE),
]
for i, (val, label, col) in enumerate(impl_cards):
    x = 40 + 220 * i
    draw_card(c, x, PAGE_H - 180, 210, 75, col)
    draw_text(c, val, x + 105, PAGE_H - 128, size=24, color=col, bold=True, align="center")
    draw_text(c, label, x + 105, PAGE_H - 150, size=11, color=LIGHT_GRAY, align="center")

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
    ["RFC 9171", "Bundle Protocol v7", "Compliant"],
    ["RFC 4838", "DTN Architecture", "Compliant"],
    ["CCSDS 734.2-B-1", "CCSDS Bundle Protocol", "Compliant"],
    ["CCSDS 734.3-B-1", "SABR / contact routing", "Baseline"],
    ["CCSDS 141.0-B-1", "Optical Comm Physical", "Compliant"],
    ["RFC 9172", "BPSec (security)", "Referenced"],
    ["RFC 5326", "LTP (deep space)", "Compliant"],
    ["RFC 7242", "TCPCL (Earth)", "Compliant"],
]
draw_table(c, std_data, 480, PAGE_H - 210, [100, 140, 70], ACCENT_BLUE)

draw_footer(c, 22)
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
    draw_text(c, status, 420, y - 10, size=10, color=GREEN, bold=True)

future_data = [
    ["Phase", "Focus", "Technology", "Status"],
    ["7", "DQN Upgrade", "Deep Q-Network", "Remaining"],
    ["8", "HIL Simulation", "ns-3 integration", "Remaining"],
    ["9", "ION-DTN", "Production DTN stack", "Remaining"],
    ["10", "Flight Demo", "LEO optical test", "Future"],
    ["11", "Mars Deploy", "Full 5-tier network", "Future"],
]
draw_table(c, future_data, 480, PAGE_H - 100, [50, 100, 130, 70], ACCENT_ORANGE)

draw_image_safe(c, os.path.join(CHARTS_DIR, "mission_timeline.png"), 40, 40, w=820)

draw_footer(c, 23)
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
    "\u2022  54.6\u2013401M km Earth-Mars distance",
    "\u2022  3\u201322 min one-way light delay",
    "\u2022  TCP/IP fundamentally broken in space",
    "\u2022  Current: only 0.5\u20136 Mbps",
    "\u2022  2-week solar conjunction blackouts",
]
for i, line in enumerate(problem_lines):
    draw_text(c, line, 55, PAGE_H - 140 - 17 * i, size=10, color=LIGHT_GRAY)

draw_card(c, 460, PAGE_H - 230, 400, 130, GREEN)
draw_text(c, "THE SOLUTION", 475, PAGE_H - 115, size=14, color=GREEN, bold=True)
solution_lines = [
    "\u2022  BPv7 DTN: store-and-forward works",
    "\u2022  RL routing: 20\u201340% faster delivery",
    "\u2022  Optical: 10\u2013100\u00d7 data rate increase",
    "\u2022  QKD: future-proof quantum security",
    "\u2022  Lagrange relays: conjunction coverage",
]
for i, line in enumerate(solution_lines):
    draw_text(c, line, 475, PAGE_H - 140 - 17 * i, size=10, color=LIGHT_GRAY)

stat_cards = [
    ("10\u2013100\u00d7", "Faster Rates", ACCENT_BLUE),
    (">95%", "Availability", GREEN),
    ("AI-Driven", "Routing", ACCENT_CYAN),
    ("Quantum", "Security", ACCENT_PURPLE),
]
for i, (val, label, col) in enumerate(stat_cards):
    x = 40 + 210 * i
    draw_card(c, x, PAGE_H - 400, 200, 80, col)
    draw_text(c, val, x + 100, PAGE_H - 340, size=20, color=col, bold=True, align="center")
    draw_text(c, label, x + 100, PAGE_H - 362, size=12, color=WHITE, bold=True, align="center")

draw_text(c, "NOVEL CONTRIBUTIONS", 40, PAGE_H - 430, size=13, color=ACCENT_CYAN, bold=True)
contrib = "RL autonomous routing (20-40% faster) | 5-tier DTN (>95% availability) | Optical/RF hybrid (10-100\u00d7) | Quantum links (future-proof) | Full simulation (149 tests)"
draw_text(c, contrib, 40, PAGE_H - 450, size=10, color=LIGHT_GRAY)

draw_footer(c, 24)
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
    (">95%", "Available", GREEN),
    ("241", "Nodes", ACCENT_ORANGE),
    ("149", "Tests", ACCENT_PURPLE),
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
draw_text(c, "EduQual Level 6 Diploma in AI Operations | Topic 59 | January 2026", PAGE_W / 2, 82, size=9, color=MED_GRAY, align="center")

_draw_speaker_notes(c, _SPEAKER_NOTES[27])
c.showPage()

c.save()
print(f"\n\u2713 PDF saved: {pdf_path}")
print(f"  Pages: {TOTAL_SLIDES}")
