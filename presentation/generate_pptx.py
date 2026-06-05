#!/usr/bin/env python3
"""
AETHERIX Animated Presentation Generator
Creates a professional PPTX with animations, charts, and diagrams.
"""

import os
import sys

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn, nsmap
from pptx.oxml import parse_xml
import copy
from lxml import etree

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "presentation", "output")
CHARTS_DIR = os.path.join(BASE_DIR, "visualizations", "charts")
DIAGRAMS_DIR = os.path.join(BASE_DIR, "visualizations", "diagrams")
IMG_DIR = os.path.join(BASE_DIR, "docs", "img")

os.makedirs(OUTPUT_DIR, exist_ok=True)

BG_DARK = RGBColor(0x0B, 0x0E, 0x1A)
BG_SLIDE = RGBColor(0x0D, 0x12, 0x22)
ACCENT_BLUE = RGBColor(0x00, 0x9E, 0xFF)
ACCENT_CYAN = RGBColor(0x00, 0xD4, 0xAA)
ACCENT_PURPLE = RGBColor(0x8B, 0x5C, 0xF6)
ACCENT_ORANGE = RGBColor(0xFF, 0x8C, 0x00)
ACCENT_RED = RGBColor(0xFF, 0x4D, 0x4D)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xB0, 0xB8, 0xCC)
MED_GRAY = RGBColor(0x6B, 0x7B, 0x96)
CARD_BG = RGBColor(0x14, 0x1B, 0x2D)
CARD_BORDER = RGBColor(0x1E, 0x2A, 0x42)
GREEN = RGBColor(0x2E, 0xCC, 0x71)
YELLOW = RGBColor(0xFF, 0xD9, 0x3D)

SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_WIDTH
prs.slide_height = SLIDE_HEIGHT


def set_slide_bg(slide, color=BG_DARK):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape(slide, left, top, width, height, fill_color=None, border_color=None, border_width=Pt(1), shape_type=MSO_SHAPE.ROUNDED_RECTANGLE):
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.shadow.inherit = False
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = border_width
    else:
        shape.line.fill.background()
    return shape


def add_textbox(slide, left, top, width, height, text="", font_size=18, color=WHITE, bold=False, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_paragraph(text_frame, text="", font_size=16, color=WHITE, bold=False, alignment=PP_ALIGN.LEFT, space_before=Pt(4), space_after=Pt(4), font_name="Calibri"):
    p = text_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    p.space_before = space_before
    p.space_after = space_after
    return p


def add_card(slide, left, top, width, height, title="", body_lines=None, title_color=ACCENT_BLUE, body_color=LIGHT_GRAY, title_size=16, body_size=13, fill=CARD_BG, border=CARD_BORDER):
    shape = add_shape(slide, left, top, width, height, fill_color=fill, border_color=border)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.1)
    tf.margin_bottom = Inches(0.1)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(title_size)
    p.font.color.rgb = title_color
    p.font.bold = True
    p.font.name = "Calibri"
    if body_lines:
        for line in body_lines:
            add_paragraph(tf, line, font_size=body_size, color=body_color, space_before=Pt(2), space_after=Pt(2))
    return shape


def add_accent_line(slide, left, top, width, color=ACCENT_BLUE, height=Pt(3)):
    return add_shape(slide, left, top, width, height, fill_color=color, shape_type=MSO_SHAPE.RECTANGLE)


def add_image_safe(slide, img_path, left, top, width=None, height=None):
    if os.path.exists(img_path):
        if width and height:
            return slide.shapes.add_picture(img_path, left, top, width, height)
        elif width:
            return slide.shapes.add_picture(img_path, left, top, width=width)
        elif height:
            return slide.shapes.add_picture(img_path, left, top, height=height)
        else:
            return slide.shapes.add_picture(img_path, left, top)
    return None


def add_table(slide, left, top, width, height, rows, cols, data, header_color=ACCENT_BLUE, col_widths=None):
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = w
    for row_idx in range(rows):
        for col_idx in range(cols):
            cell = table.cell(row_idx, col_idx)
            cell.text = data[row_idx][col_idx] if row_idx < len(data) and col_idx < len(data[row_idx]) else ""
            cell.fill.solid()
            if row_idx == 0:
                cell.fill.fore_color.rgb = header_color
                for p in cell.text_frame.paragraphs:
                    p.font.color.rgb = WHITE
                    p.font.bold = True
                    p.font.size = Pt(12)
                    p.font.name = "Calibri"
                    p.alignment = PP_ALIGN.CENTER
            else:
                cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 1 else RGBColor(0x18, 0x22, 0x36)
                for p in cell.text_frame.paragraphs:
                    p.font.color.rgb = LIGHT_GRAY
                    p.font.size = Pt(11)
                    p.font.name = "Calibri"
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
    return table_shape


def add_entrance_animation(slide, shape, delay_ms=0, duration_ms=500, anim_type="fade"):
    slide_element = slide._element
    timing = slide_element.find(qn('p:timing'))
    if timing is None:
        timing = parse_xml(
            '<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
            '<p:childTnLst/>'
            '</p:cTn></p:par></p:tnLst>'
            '</p:timing>'
        )
        slide_element.append(timing)
    child_tn_lst = timing.find('.//' + qn('p:childTnLst'))
    shape_id = shape.shape_id
    seq_id = len(child_tn_lst) + 2
    if anim_type == "fade":
        anim_xml = f'<p:par xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cTn id="{seq_id}" fill="hold"><p:stCondLst><p:cond delay="{delay_ms}"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{seq_id+1}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{seq_id+2}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" nodeType="afterEffect"><p:stCondLst><p:cond delay="{delay_ms}"/></p:stCondLst><p:childTnLst><p:set><p:cBhvr><p:cTn id="{seq_id+3}" dur="{duration_ms}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{shape_id}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set><p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{seq_id+4}" dur="{duration_ms}"/><p:tgtEl><p:spTgt spid="{shape_id}"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
    else:
        anim_xml = f'<p:par xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cTn id="{seq_id}" fill="hold"><p:stCondLst><p:cond delay="{delay_ms}"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{seq_id+1}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{seq_id+2}" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" nodeType="clickEffect"><p:stCondLst><p:cond delay="{delay_ms}"/></p:stCondLst><p:childTnLst><p:set><p:cBhvr><p:cTn id="{seq_id+3}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{shape_id}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
    child_tn_lst.append(parse_xml(anim_xml))


def add_slide_transition(slide, transition_type="fade", duration_ms=700):
    slide_element = slide._element
    trans = {
        "fade": '<p:fade/>',
        "push": '<p:push dir="l"/>',
        "wipe": '<p:wipe dir="d"/>',
        "cover": '<p:cover dir="l"/>',
    }
    inner = trans.get(transition_type, '<p:fade/>')
    trans_xml = f'<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" advClick="1">{inner}</p:transition>'
    existing = slide_element.find(qn('p:transition'))
    if existing is not None:
        slide_element.remove(existing)
    slide_element.insert(1, parse_xml(trans_xml))


def add_footer(slide, slide_num, total=25):
    add_textbox(slide, Inches(0.5), Inches(7.0), Inches(5), Inches(0.4),
                "AETHERIX — Interplanetary Communication Network", font_size=10, color=MED_GRAY)
    add_textbox(slide, Inches(11.0), Inches(7.0), Inches(2), Inches(0.4),
                f"{slide_num} / {total}", font_size=10, color=MED_GRAY, alignment=PP_ALIGN.RIGHT)


def add_stat_card(slide, x, y, w, h, value, label, value_color=ACCENT_BLUE, val_size=24):
    card = add_shape(slide, x, y, w, h, fill_color=CARD_BG, border_color=value_color)
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.1)
    tf.margin_top = Inches(0.05)
    p = tf.paragraphs[0]
    p.text = value
    p.font.size = Pt(val_size)
    p.font.color.rgb = value_color
    p.font.bold = True
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    add_paragraph(tf, label, font_size=10, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER, space_before=Pt(2))
    return card


def new_slide():
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    set_slide_bg(slide)
    return slide

# ============================================================
# SLIDES 1–8
# ============================================================

# --- SLIDE 1 — Introduction (Title Hero) ---
print("Creating Slide 1: Introduction...")
slide = new_slide()
add_slide_transition(slide, "fade")
add_shape(slide, Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.06), fill_color=ACCENT_BLUE, shape_type=MSO_SHAPE.RECTANGLE)
add_textbox(slide, Inches(1.5), Inches(1.2), Inches(10.3), Inches(1.5), "AETHERIX", font_size=72, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
add_accent_line(slide, Inches(4.5), Inches(2.5), Inches(4.3), ACCENT_CYAN, Pt(4))
add_textbox(slide, Inches(1.0), Inches(2.8), Inches(11.3), Inches(1.0), "Autonomous Extraterrestrial High-throughput Enhancing Routing\nand Inter-planetary eXchange", font_size=22, color=ACCENT_CYAN, alignment=PP_ALIGN.CENTER)
add_textbox(slide, Inches(2.0), Inches(4.0), Inches(9.3), Inches(0.5), "EduQual Level 6 Diploma in AI Operations  |  Topic 59", font_size=16, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)
add_textbox(slide, Inches(2.0), Inches(4.5), Inches(9.3), Inches(0.5), "Building an Interplanetary Communication Network with DTN,\nQuantum Communication, and Space-Based Infrastructure for Mars Mission Support", font_size=14, color=MED_GRAY, alignment=PP_ALIGN.CENTER)
add_accent_line(slide, Inches(3.5), Inches(5.3), Inches(6.3), ACCENT_BLUE, Pt(2))
add_textbox(slide, Inches(2.0), Inches(5.6), Inches(9.3), Inches(0.5), "Muhammad Abdullah Tariq", font_size=20, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
add_textbox(slide, Inches(2.0), Inches(6.1), Inches(9.3), Inches(0.5), "January 2026", font_size=14, color=MED_GRAY, alignment=PP_ALIGN.CENTER)
add_textbox(slide, Inches(2.0), Inches(6.7), Inches(9.3), Inches(0.4), "matx104.github.io/AETHERIX  |  github.com/matx104/AETHERIX", font_size=12, color=ACCENT_BLUE, alignment=PP_ALIGN.CENTER)
add_shape(slide, Inches(0), Inches(7.44), SLIDE_WIDTH, Inches(0.06), fill_color=ACCENT_BLUE, shape_type=MSO_SHAPE.RECTANGLE)

# --- SLIDE 2 — Agenda ---
print("Creating Slide 2: Agenda...")
slide = new_slide()
add_slide_transition(slide, "push")
add_textbox(slide, Inches(0.7), Inches(0.3), Inches(11.0), Inches(0.7), "PRESENTATION AGENDA", font_size=36, color=WHITE, bold=True, alignment=PP_ALIGN.LEFT)
add_accent_line(slide, Inches(0.7), Inches(0.95), Inches(3.0), ACCENT_CYAN, Pt(3))
add_footer(slide, 2)

agenda_items = [
    ("01", "The Challenge", "Why space breaks the internet", ACCENT_BLUE),
    ("02", "Architecture", "DTN + AI + Quantum Security", ACCENT_CYAN),
    ("03", "DTN & BPv7", "Store-and-forward foundation", ACCENT_PURPLE),
    ("04", "Topology", "241 nodes across two worlds", ACCENT_BLUE),
    ("05", "Link Budget", "1550nm laser analysis", ACCENT_ORANGE),
    ("06", "RL Routing", "Multi-agent federated Q-learning", ACCENT_CYAN),
    ("07", "Quantum Security", "BB84/E91 + repeater chains", ACCENT_PURPLE),
    ("08", "Orbital Mechanics", "Contact windows & synodic period", ACCENT_BLUE),
    ("09", "Mars Mission", "End-to-end simulation walkthrough", ACCENT_ORANGE),
    ("10", "Performance", "AETHERIX vs current systems", GREEN),
    ("11", "Roadmap", "CCSDS, IETF, deployment phases", ACCENT_CYAN),
    ("12", "Q&A", "Summary and live demo", WHITE),
]

for i, (num, title, desc, color) in enumerate(agenda_items):
    col_x = Inches(0.7) if i < 6 else Inches(6.8)
    row_y = Inches(1.3) + Inches(0.92) * (i % 6)
    card = add_card(slide, col_x, row_y, Inches(5.8), Inches(0.82), border=color)
    add_textbox(slide, col_x + Inches(0.15), row_y + Inches(0.08), Inches(5.5), Inches(0.35), f"{num}  {title}", font_size=14, color=WHITE, bold=True)
    add_textbox(slide, col_x + Inches(0.15), row_y + Inches(0.42), Inches(5.5), Inches(0.35), desc, font_size=11, color=LIGHT_GRAY)
    add_entrance_animation(slide, card, delay_ms=100 * i, anim_type="fade")

# --- SLIDE 3 — What is AETHERIX ---
print("Creating Slide 3: What is AETHERIX...")
slide = new_slide()
add_slide_transition(slide, "fade")
add_textbox(slide, Inches(0.7), Inches(0.3), Inches(11.0), Inches(0.7), "WHAT IS AETHERIX?", font_size=36, color=WHITE, bold=True, alignment=PP_ALIGN.LEFT)
add_accent_line(slide, Inches(0.7), Inches(0.95), Inches(3.0), ACCENT_CYAN, Pt(3))
add_textbox(slide, Inches(0.7), Inches(1.05), Inches(11.0), Inches(0.4), "Overview & The Problem", font_size=16, color=MED_GRAY)
add_footer(slide, 3)

card_left = add_card(slide, Inches(0.7), Inches(1.6), Inches(5.6), Inches(3.8), border=ACCENT_BLUE)
add_textbox(slide, Inches(0.9), Inches(1.7), Inches(5.2), Inches(0.45), "What is AETHERIX?", font_size=18, color=ACCENT_BLUE, bold=True)
add_accent_line(slide, Inches(0.9), Inches(2.1), Inches(2.0), ACCENT_BLUE, Pt(2))
what_lines = [
    "Autonomous Extraterrestrial High-throughput Enhancing\nRouting and Inter-planetary eXchange",
    "An architecture for delay-tolerant networking (DTN)\nbetween Earth and Mars",
    "Replaces static Contact Graph Routing with\nreinforcement-learning-based adaptive routing",
    "Secures links via Quantum Key Distribution\n(BB84 & E91 protocols with repeater chains)",
    "Hybrid optical/RF communications across\na 5-tier, 241-node interplanetary topology",
    "Open-source, standards-compliant (CCSDS, IETF)\nresearch platform for deep-space networking",
]
for j, line in enumerate(what_lines):
    add_textbox(slide, Inches(0.9), Inches(2.2) + Inches(0.5) * j, Inches(5.2), Inches(0.5), line, font_size=10, color=LIGHT_GRAY)

card_right = add_card(slide, Inches(6.7), Inches(1.6), Inches(5.6), Inches(3.8), border=ACCENT_RED)
add_textbox(slide, Inches(6.9), Inches(1.7), Inches(5.2), Inches(0.45), "The Problem", font_size=18, color=ACCENT_RED, bold=True)
add_accent_line(slide, Inches(6.9), Inches(2.1), Inches(2.0), ACCENT_RED, Pt(2))
problem_lines = [
    "Earth–Mars distance varies from 54.6M to 401M km\n— a 7x range swing every 780 days",
    "One-way light delay is 3–22 minutes;\nround-trip TCP ACK is 6–44 minutes",
    "Solar conjunction causes ~2-week communication\nblackouts twice per synodic period",
    "Deep-space links are inherently intermittent:\nno continuous end-to-end path exists",
    "Static routing cannot adapt to dynamic\ncontact schedules and link degradation",
    "Classical key exchange is infeasible across\ninterplanetary distances",
]
for j, line in enumerate(problem_lines):
    add_textbox(slide, Inches(6.9), Inches(2.2) + Inches(0.5) * j, Inches(5.2), Inches(0.5), line, font_size=10, color=LIGHT_GRAY)

callout_shape = add_shape(slide, Inches(0.7), Inches(5.7), Inches(11.6), Inches(0.9), fill_color=ACCENT_BLUE, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE)
add_textbox(slide, Inches(1.0), Inches(5.8), Inches(11.0), Inches(0.7), "AETHERIX addresses every one of these challenges — harnessing DTN store-and-forward, AI-driven adaptive routing, quantum-secured key distribution, and hybrid optical/RF links to enable reliable interplanetary communication.", font_size=13, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

# --- SLIDE 4 — The Distance ---
print("Creating Slide 4: The Distance...")
slide = new_slide()
add_slide_transition(slide, "push")
add_textbox(slide, Inches(0.7), Inches(0.3), Inches(11.0), Inches(0.7), "THE DISTANCE", font_size=36, color=WHITE, bold=True, alignment=PP_ALIGN.LEFT)
add_accent_line(slide, Inches(0.7), Inches(0.95), Inches(3.0), ACCENT_RED, Pt(3))
add_textbox(slide, Inches(0.7), Inches(1.05), Inches(11.0), Inches(0.4), "Why Space Breaks the Internet", font_size=16, color=MED_GRAY)
add_footer(slide, 4)

left_headers = ["Parameter", "Value"]
left_rows = [
    ["Closest approach", "54.6 million km"],
    ["Farthest distance", "401 million km"],
    ["Distance variation", "7.3× (735%)"],
    ["One-way light time", "3 – 22 minutes"],
    ["Synodic period", "780 days (26 months)"],
    ["Solar conjunction blackout", "~2 weeks (twice/period)"],
]
_d1 = [left_headers] + left_rows
add_table(slide, Inches(0.7), Inches(1.5), Inches(5.6), Inches(3.2), len(_d1), len(left_headers), _d1, header_color=ACCENT_RED)

right_headers = ["TCP/IP Assumption", "Deep-Space Reality"]
right_rows = [
    ["Low latency (< 200 ms)", "6 – 44 min round trip"],
    ["Continuous connectivity", "Scheduled contact windows only"],
    ["End-to-end path exists", "No simultaneous path possible"],
    ["Reliable ACKs in seconds", "ACKs take minutes to hours"],
]
_d2 = [right_headers] + right_rows
add_table(slide, Inches(6.7), Inches(1.5), Inches(5.6), Inches(2.2), len(_d2), len(right_headers), _d2, header_color=ACCENT_ORANGE)

quote_card = add_card(slide, Inches(6.7), Inches(4.0), Inches(5.6), Inches(1.3), border=ACCENT_ORANGE)
add_textbox(slide, Inches(6.9), Inches(4.1), Inches(5.2), Inches(1.1), '"TCP/IP assumes the network is fast, reliable, and always connected.\nDeep space is none of those things."', font_size=12, color=ACCENT_ORANGE, bold=True, alignment=PP_ALIGN.CENTER)

stat_y = Inches(5.6)
stat_labels = ["54.6M km", "401M km", "780 days", "0.5–6 Mbps"]
stat_sublabels = ["Min Distance", "Max Distance", "Synodic Period", "Current DSN Rate"]
stat_colors = [ACCENT_BLUE, ACCENT_RED, ACCENT_ORANGE, ACCENT_CYAN]
for k in range(4):
    sx = Inches(0.7) + Inches(3.0) * k
    add_shape(slide, sx, stat_y, Inches(2.7), Inches(1.1), fill_color=CARD_BG, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE)
    add_accent_line(slide, sx, stat_y, Inches(2.7), stat_colors[k], Pt(3))
    add_textbox(slide, sx + Inches(0.15), stat_y + Inches(0.15), Inches(2.4), Inches(0.45), stat_labels[k], font_size=22, color=stat_colors[k], bold=True, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, sx + Inches(0.15), stat_y + Inches(0.6), Inches(2.4), Inches(0.35), stat_sublabels[k], font_size=11, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

# --- SLIDE 5 — The Answer ---
print("Creating Slide 5: The Answer...")
slide = new_slide()
add_slide_transition(slide, "wipe")
add_textbox(slide, Inches(0.7), Inches(0.3), Inches(11.0), Inches(0.7), "THE ANSWER", font_size=36, color=WHITE, bold=True, alignment=PP_ALIGN.LEFT)
add_accent_line(slide, Inches(0.7), Inches(0.95), Inches(3.0), ACCENT_CYAN, Pt(3))
add_textbox(slide, Inches(0.7), Inches(1.05), Inches(11.0), Inches(0.4), "Delay-Tolerant Networking", font_size=16, color=MED_GRAY)
add_footer(slide, 5)

flow_labels = ["Bundle", "Store", "Wait", "Forward", "Deliver"]
flow_colors = [ACCENT_BLUE, ACCENT_PURPLE, ACCENT_ORANGE, ACCENT_CYAN, GREEN]
flow_descs = [
    "Create data\nbundle (BPv7)",
    "Buffer at\nlocal node",
    "Hold until\ncontact window",
    "Transmit to\nnext hop",
    "Reach final\ndestination",
]
card_w = Inches(2.0)
card_h = Inches(1.6)
start_x = Inches(0.5)
gap = Inches(0.35)
arrow_w = Inches(0.3)
flow_y = Inches(1.6)

for idx, (label, color, desc) in enumerate(zip(flow_labels, flow_colors, flow_descs)):
    cx = start_x + (card_w + arrow_w + gap) * idx
    card = add_card(slide, cx, flow_y, card_w, card_h, border=color)
    add_textbox(slide, cx + Inches(0.1), flow_y + Inches(0.1), card_w - Inches(0.2), Inches(0.35), label, font_size=16, color=color, bold=True, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, cx + Inches(0.1), flow_y + Inches(0.5), card_w - Inches(0.2), Inches(0.9), desc, font_size=10, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)
    add_entrance_animation(slide, card, delay_ms=150 * idx, anim_type="fade")
    if idx < len(flow_labels) - 1:
        arrow_x = cx + card_w + Inches(0.05)
        add_textbox(slide, arrow_x, flow_y + Inches(0.5), arrow_w, Inches(0.5), "→", font_size=28, color=MED_GRAY, alignment=PP_ALIGN.CENTER)

stat_card_data = [
    ("BPv7", "Bundle Protocol v7\nRFC 9171 — store &\nforward with custody", ACCENT_BLUE),
    ("AI Routing", "Multi-agent federated\nQ-learning adapts in\nreal time to contacts", ACCENT_PURPLE),
    ("QKD", "BB84 & E91 quantum\nkey distribution with\nrepeater chains", ACCENT_CYAN),
]
stat_y = Inches(3.5)
for idx, (title, desc, color) in enumerate(stat_card_data):
    sx = Inches(0.7) + Inches(4.0) * idx
    add_stat_card(slide, sx, stat_y, Inches(3.6), Inches(1.4), title, desc, value_color=color)

postal_card = add_card(slide, Inches(0.7), Inches(5.2), Inches(11.6), Inches(1.0), border=ACCENT_BLUE)
add_textbox(slide, Inches(1.0), Inches(5.3), Inches(11.0), Inches(0.8), 'Think of it like the postal service: you don\'t need a continuous connection between sender and receiver — each post office (node) stores the letter (bundle) until the next truck (contact window) is available, then forwards it one hop closer to the destination.', font_size=12, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)

# --- SLIDE 6 — System Architecture ---
print("Creating Slide 6: System Architecture...")
slide = new_slide()
add_slide_transition(slide, "cover")
add_textbox(slide, Inches(0.7), Inches(0.3), Inches(11.0), Inches(0.7), "SYSTEM ARCHITECTURE", font_size=36, color=WHITE, bold=True, alignment=PP_ALIGN.LEFT)
add_accent_line(slide, Inches(0.7), Inches(0.95), Inches(3.0), ACCENT_CYAN, Pt(3))
add_textbox(slide, Inches(0.7), Inches(1.05), Inches(11.0), Inches(0.4), "Five Core Modules", font_size=16, color=MED_GRAY)
add_footer(slide, 6)

modules = [
    ("1", "Infrastructure", "Link budget & RF/optical analysis", ACCENT_BLUE),
    ("2", "Routing", "RL agent, BPv7, store-and-forward", ACCENT_PURPLE),
    ("3", "Security", "QKD (BB84/E91) & repeater chains", ACCENT_CYAN),
    ("4", "Orbital", "Contact windows & Doppler analysis", ACCENT_ORANGE),
    ("5", "Simulation", "Full network simulation engine", GREEN),
]

for idx, (num, name, desc, color) in enumerate(modules):
    my = Inches(1.6) + Inches(0.95) * idx
    circle = add_shape(slide, Inches(0.7), my, Inches(0.6), Inches(0.6), fill_color=color, shape_type=MSO_SHAPE.OVAL)
    add_textbox(slide, Inches(0.7), my + Inches(0.08), Inches(0.6), Inches(0.45), num, font_size=18, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, Inches(1.5), my + Inches(0.0), Inches(4.0), Inches(0.35), name, font_size=16, color=color, bold=True)
    add_textbox(slide, Inches(1.5), my + Inches(0.35), Inches(4.0), Inches(0.35), desc, font_size=11, color=LIGHT_GRAY)

table_headers = ["Module", "Engine", "Showcase"]
table_rows = [
    ["Infrastructure", "OpticalLinkBudget + RFLinkBudget", "Earth-Mars link analysis"],
    ["Routing", "RLRoutingAgent + ForwardingEngine", "Multi-hop DTN delivery"],
    ["Security", "BB84Protocol + E91Protocol", "Quantum-secured key exchange"],
    ["Orbital", "ContactWindows + Doppler", "Synodic contact prediction"],
    ["Simulation", "Simulator + PolicyEngine", "End-to-end scenario runs"],
]
_d4 = [table_headers] + table_rows
add_table(slide, Inches(6.4), Inches(1.6), Inches(6.0), Inches(4.5), len(_d4), len(table_headers), _d4, header_color=ACCENT_BLUE)

# --- SLIDE 7 — Architecture Diagram ---
print("Creating Slide 7: Architecture Diagram...")
slide = new_slide()
add_slide_transition(slide, "fade")
add_textbox(slide, Inches(0.7), Inches(0.3), Inches(11.0), Inches(0.7), "ARCHITECTURE DIAGRAM", font_size=36, color=WHITE, bold=True, alignment=PP_ALIGN.LEFT)
add_accent_line(slide, Inches(0.7), Inches(0.95), Inches(3.0), ACCENT_CYAN, Pt(3))
add_footer(slide, 7)

arch_img_path = os.path.join(DIAGRAMS_DIR, "system_architecture.png")
add_image_safe(slide, arch_img_path, Inches(0.7), Inches(1.2), Inches(11.6), Inches(5.8))

# --- SLIDE 8 — BPv7 Deep Dive ---
print("Creating Slide 8: BPv7 Deep Dive...")
slide = new_slide()
add_slide_transition(slide, "push")
add_textbox(slide, Inches(0.7), Inches(0.3), Inches(11.0), Inches(0.7), "BPv7 DEEP DIVE", font_size=36, color=WHITE, bold=True, alignment=PP_ALIGN.LEFT)
add_accent_line(slide, Inches(0.7), Inches(0.95), Inches(3.0), ACCENT_CYAN, Pt(3))
add_textbox(slide, Inches(0.7), Inches(1.05), Inches(11.0), Inches(0.4), "The Foundation", font_size=16, color=MED_GRAY)
add_footer(slide, 8)

stack_layers = [
    ("Application Layer", "User data, commands, telemetry", ACCENT_BLUE),
    ("Bundle Protocol v7", "Routing, custody, fragmentation, TTL", ACCENT_PURPLE),
    ("Convergence Layer", "LTP (space), TCPCL (Earth), UDPCL (ISL)", ACCENT_CYAN),
    ("Physical Layer", "Optical 1550nm / Ka-band RF links", ACCENT_ORANGE),
]
for idx, (layer, desc, color) in enumerate(stack_layers):
    ly = Inches(1.6) + Inches(1.05) * idx
    card = add_card(slide, Inches(0.7), ly, Inches(5.6), Inches(0.9), border=color, fill=CARD_BG)
    add_textbox(slide, Inches(0.9), ly + Inches(0.05), Inches(5.2), Inches(0.35), layer, font_size=14, color=color, bold=True)
    add_textbox(slide, Inches(0.9), ly + Inches(0.42), Inches(5.2), Inches(0.4), desc, font_size=10, color=LIGHT_GRAY)
    if idx < len(stack_layers) - 1:
        add_textbox(slide, Inches(3.1), ly + Inches(0.85), Inches(1.0), Inches(0.25), "▼", font_size=14, color=MED_GRAY, alignment=PP_ALIGN.CENTER)

prio_headers = ["Priority", "Class", "Use Case"]
prio_rows = [
    ["P0", "EMERGENCY", "Life-critical alerts, abort commands"],
    ["P1", "URGENT", "Navigation corrections, hazard warnings"],
    ["P2", "NORMAL", "Telemetry, science data, commands"],
    ["P3", "LOW", "Software updates, bulk file transfer"],
    ["P4", "BULK", "Background sync, archival data"],
]
_d5 = [prio_headers] + prio_rows
add_table(slide, Inches(6.7), Inches(1.6), Inches(5.6), Inches(2.6), len(_d5), len(prio_headers), _d5, header_color=ACCENT_PURPLE)

snf_title_y = Inches(4.4)
add_textbox(slide, Inches(6.7), snf_title_y, Inches(5.6), Inches(0.35), "Store-and-Forward Steps", font_size=14, color=ACCENT_CYAN, bold=True)
add_accent_line(slide, Inches(6.7), snf_title_y + Inches(0.32), Inches(2.0), ACCENT_CYAN, Pt(2))
snf_steps = [
    "1. Bundle created at source with destination EID + TTL",
    "2. Node stores bundle in priority queue (buffer mgmt)",
    "3. Contact window opens → best next-hop selected by RL",
    "4. Bundle transmitted via convergence layer (LTP/TCPCL)",
    "5. Custody transfer confirms; repeat until destination",
]
for j, step in enumerate(snf_steps):
    add_textbox(slide, Inches(6.7), snf_title_y + Inches(0.4) + Inches(0.3) * j, Inches(5.6), Inches(0.3), step, font_size=10, color=LIGHT_GRAY)

standards_y = Inches(6.2)
standards_card = add_card(slide, Inches(0.7), standards_y, Inches(11.6), Inches(0.7), border=ACCENT_BLUE)
add_textbox(slide, Inches(0.9), standards_y + Inches(0.1), Inches(11.2), Inches(0.5), "Standards: RFC 9171 (BPv7)  •  RFC 4838 (DTN Arch)  •  RFC 5326 (LTP)  •  CCSDS 734.2-B-1 (Bundle Protocol)  •  CCSDS 734.3-B-1 (SABR)", font_size=11, color=ACCENT_BLUE, alignment=PP_ALIGN.CENTER)
# ── SLIDE 9 ── DTN Store-and-Forward ──────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "fade")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "DTN STORE-AND-FORWARD"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

txBox2 = add_textbox(slide, Inches(0.6), Inches(0.9), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "How It Works"
p2.font.size = Pt(16)
p2.font.color.rgb = ACCENT_CYAN
p2.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(1.35), Inches(2.5))

tcp_bullets = [
    "Requires continuous end-to-end connection",
    "Round-trip time > 40 minutes breaks ACKs",
    "Packet loss triggers aggressive retransmission",
    "Congestion control collapses at interplanetary scale",
]
add_card(
    slide, Inches(0.4), Inches(1.6), Inches(4.4), Inches(2.8),
    "TCP/IP in Space — Fails",
    tcp_bullets,
    border=ACCENT_RED,
)

dtn_bullets = [
    "Store-and-forward: custody transfer at each hop",
    "Bundle Protocol v7 (RFC 9171) — no end-to-end session",
    "Opportunistic contacts exploited automatically",
    "Tolerates hours-to-days of link disruption",
]
add_card(
    slide, Inches(5.2), Inches(1.6), Inches(4.4), Inches(2.8),
    "DTN Works",
    dtn_bullets,
    border=ACCENT_CYAN,
)

ltp_bullets = [
    "Licklider Transmission Protocol",
    "RFC 5326 — deep-space links",
    "Reliable segments + retransmission",
    "Handles long light-time delays",
]
add_card(
    slide, Inches(0.3), Inches(4.65), Inches(3.0), Inches(2.6),
    "LTP (RFC 5326)",
    ltp_bullets,
    border=ACCENT_CYAN,
)

tcpcl_bullets = [
    "TCP Convergence Layer",
    "RFC 7242 — Earth segment",
    "Session management over TCP",
    "Reliable terrestrial backhaul",
]
add_card(
    slide, Inches(3.5), Inches(4.65), Inches(3.0), Inches(2.6),
    "TCPCL (RFC 7242)",
    tcpcl_bullets,
    border=GREEN,
)

udpcl_bullets = [
    "UDP Convergence Layer",
    "Optical inter-satellite links",
    "Fragmentation + loss simulation",
    "Low-latency mesh forwarding",
]
add_card(
    slide, Inches(6.7), Inches(4.65), Inches(3.0), Inches(2.6),
    "UDP-CL",
    udpcl_bullets,
    border=ACCENT_ORANGE,
)

add_footer(slide, 9)

# ── SLIDE 10 ── Network Topology ──────────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "push")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "NETWORK TOPOLOGY"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

txBox2 = add_textbox(slide, Inches(0.6), Inches(0.9), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "241 Nodes, 5 Tiers"
p2.font.size = Pt(16)
p2.font.color.rgb = ACCENT_CYAN
p2.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(1.35), Inches(2.5))

tiers = [
    ("T1  Earth Ground", "6 nodes", "DSN stations: Goldstone, Madrid, Canberra", ACCENT_BLUE),
    ("T2  Earth Orbital", "51 nodes", "GEO relays + 48 LEO laser constellation", ACCENT_PURPLE),
    ("T3  Deep Space Transit", "4 nodes", "Lagrange point relays (ES-L4, ES-L5)", ACCENT_ORANGE),
    ("T4  Mars Orbital", "4 nodes", "Areostationary + polar orbit relays", ACCENT_RED),
    ("T5  Mars Surface", "176 nodes", "Bases, rovers, drones, sensor networks", YELLOW),
]

tier_y = Inches(1.6)
for tier_name, node_count, desc, color in tiers:
    bar = add_shape(
        slide, Inches(0.4), tier_y, Inches(0.08), Inches(0.65),
        fill_color=color, shape_type=MSO_SHAPE.RECTANGLE,
    )
    row_bg = add_shape(
        slide, Inches(0.48), tier_y, Inches(4.9), Inches(0.65),
        fill_color=CARD_BG, border_color=color, shape_type=MSO_SHAPE.RECTANGLE,
    )
    row_bg.line.color.rgb = color
    row_bg.line.width = Pt(1)

    tf = row_bg.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(8)
    tf.margin_top = Pt(2)
    p_name = tf.paragraphs[0]
    p_name.text = tier_name
    p_name.font.size = Pt(11)
    p_name.font.bold = True
    p_name.font.color.rgb = WHITE

    p_nodes = add_paragraph(tf)
    p_nodes.text = f"{node_count} — {desc}"
    p_nodes.font.size = Pt(8)
    p_nodes.font.color.rgb = LIGHT_GRAY

    tier_y += Inches(0.78)

add_image_safe(slide, os.path.join(DIAGRAMS_DIR, "5tier_network.png"), Inches(5.6), Inches(1.5), Inches(4.2), Inches(3.5))

callout_bg = add_shape(
    slide, Inches(0.4), Inches(5.7), Inches(9.2), Inches(0.65),
    fill_color=CARD_BG, border_color=ACCENT_BLUE, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
)
callout_bg.line.color.rgb = ACCENT_BLUE
callout_bg.line.width = Pt(1)
ctf = callout_bg.text_frame
ctf.word_wrap = True
ctf.margin_left = Pt(12)
cp = ctf.paragraphs[0]
cp.text = "Multiple redundant paths · No single point of failure · Lagrange relays for conjunction coverage"
cp.font.size = Pt(11)
cp.font.color.rgb = ACCENT_CYAN
cp.alignment = PP_ALIGN.CENTER

add_footer(slide, 10)

# ── SLIDE 11 ── 5-Tier Network Diagram ────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "wipe")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "5-TIER NETWORK DIAGRAM"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(0.95), Inches(2.5))

tier_headers = ["Tier", "Nodes", "Description"]
tier_rows = [
    ["T1 — Earth Ground", "6", "DSN stations (Goldstone, Madrid, Canberra)"],
    ["T2 — Earth Orbital", "51", "3 GEO relays + 48 LEO laser satellites"],
    ["T3 — Deep Space", "4", "ES-L4, ES-L5 Lagrange point relays"],
    ["T4 — Mars Orbital", "4", "Areostationary relay + polar orbit relays"],
    ["T5 — Mars Surface", "176", "Habitats, rovers, drones, sensor networks"],
]
_d1 = [tier_headers] + tier_rows
add_table(
    slide, Inches(0.4), Inches(1.2), Inches(9.2), Inches(2.3), len(_d1), len(tier_headers), _d1,
    header_color=ACCENT_BLUE,
)

link_headers = ["Segment", "Data Rate", "Technology"]
link_rows = [
    ["Earth ↔ Deep Space", "100 Mbps", "1550 nm optical laser"],
    ["Deep Space ↔ Mars", "2–200 Mbps", "Optical (distance-dependent)"],
    ["Mars Orbital ↔ Surface", "2 Mbps", "UHF S-band radio"],
    ["LEO Inter-Satellite", "10 Gbps", "Laser ISL mesh"],
]
_d2 = [link_headers] + link_rows
add_table(
    slide, Inches(0.4), Inches(3.8), Inches(9.2), Inches(1.9), len(_d2), len(link_headers), _d2,
    header_color=ACCENT_BLUE,
)

add_footer(slide, 11)

# ── SLIDE 12 ── Network Diagram Visual ────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "cover")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "NETWORK DIAGRAM"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(0.95), Inches(2.5))

add_image_safe(
    slide, os.path.join(DIAGRAMS_DIR, "5tier_network.png"),
    Inches(0.5), Inches(1.2), Inches(9.0), Inches(5.3),
)

add_footer(slide, 12)

# ── SLIDE 13 ── Optical Communications ────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "fade")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "OPTICAL COMMUNICATIONS"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

txBox2 = add_textbox(slide, Inches(0.6), Inches(0.9), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "10–100x Faster Than RF"
p2.font.size = Pt(16)
p2.font.color.rgb = ACCENT_CYAN
p2.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(1.35), Inches(2.5))

add_stat_card(slide, Inches(0.3), Inches(1.55), Inches(3.1), Inches(1.2), "100–200", "Mbps at closest approach", GREEN)
add_stat_card(slide, Inches(3.55), Inches(1.55), Inches(3.1), Inches(1.2), "10–20", "Mbps average distance", ACCENT_BLUE)
add_stat_card(slide, Inches(6.8), Inches(1.55), Inches(3.1), Inches(1.2), "2–5", "Mbps at farthest point", ACCENT_RED)

eq_bullets = [
    "FSPL = 20·log₁₀(4πd/λ)  — free-space path loss",
    "Gain = 10·log₁₀(η·(πD/λ)²)  — antenna gain",
    "Pr = Pt + Gt + Gr − FSPL  — received power",
]
add_card(
    slide, Inches(0.3), Inches(2.9), Inches(4.8), Inches(1.8),
    "Key Equations",
    eq_bullets,
    border=ACCENT_BLUE,
)

config_headers = ["Parameter", "Value"]
config_rows = [
    ["Wavelength", "1550 nm"],
    ["Tx Power", "5 W"],
    ["Tx Aperture", "22 cm"],
    ["Rx Aperture", "1.0 m"],
]
_d3 = [config_headers] + config_rows
add_table(
    slide, Inches(5.3), Inches(2.9), Inches(4.4), Inches(1.8), len(_d3), len(config_headers), _d3,
    header_color=ACCENT_BLUE,
)

add_image_safe(
    slide, os.path.join(CHARTS_DIR, "link_budget_breakdown.png"),
    Inches(0.4), Inches(4.9), Inches(9.2), Inches(2.3),
)

add_footer(slide, 13)

# ── SLIDE 14 ── Earth-Mars Journey ────────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "push")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "EARTH-MARS JOURNEY"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

txBox2 = add_textbox(slide, Inches(0.6), Inches(0.9), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "500 MB in 7 Hops"
p2.font.size = Pt(16)
p2.font.color.rgb = ACCENT_CYAN
p2.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(1.35), Inches(2.5))

hop_headers = ["Hop", "Path", "Link"]
hop_rows = [
    ["1", "Rover → UHF Relay", "UHF S-band"],
    ["2", "UHF Relay → Areostationary", "UHF uplink"],
    ["3", "Areostationary → Polar Orbiter", "Crosslink"],
    ["4–5", "Polar Orbiter → LEO Constellation", "1550 nm laser"],
    ["6", "LEO Mesh → DSN Ground Station", "Optical downlink"],
    ["7", "DSN → Mission Operations Center", "TCP/IP fiber"],
]
_d4 = [hop_headers] + hop_rows
add_table(
    slide, Inches(0.3), Inches(1.5), Inches(9.4), Inches(2.7), len(_d4), len(hop_headers), _d4,
    header_color=ACCENT_BLUE,
)

add_stat_card(slide, Inches(0.2), Inches(4.4), Inches(2.35), Inches(1.1), "~13min", "End-to-end latency", ACCENT_BLUE)
add_stat_card(slide, Inches(2.65), Inches(4.4), Inches(2.35), Inches(1.1), "<5%", "Protocol overhead", GREEN)
add_stat_card(slide, Inches(5.1), Inches(4.4), Inches(2.35), Inches(1.1), "98.7%", "Delivery ratio", ACCENT_PURPLE)
add_stat_card(slide, Inches(7.55), Inches(4.4), Inches(2.35), Inches(1.1), "7 hops", "Store-and-forward", ACCENT_ORANGE)

add_image_safe(
    slide, os.path.join(CHARTS_DIR, "data_rate_vs_distance.png"),
    Inches(0.4), Inches(5.65), Inches(9.2), Inches(1.65),
)

add_footer(slide, 14)

# ── SLIDE 15 ── RL Routing ────────────────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "wipe")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "RL-BASED ROUTING"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

txBox2 = add_textbox(slide, Inches(0.6), Inches(0.9), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "AI Innovation"
p2.font.size = Pt(16)
p2.font.color.rgb = ACCENT_CYAN
p2.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(1.35), Inches(2.5))

cgr_bullets = [
    "Pre-computed contact plans required",
    "Cannot adapt to unexpected link failures",
    "Computational cost grows O(n³) per route",
    "No learning from historical performance",
    "Single-path — ignores multipath opportunity",
]
add_card(
    slide, Inches(0.3), Inches(1.55), Inches(4.6), Inches(2.5),
    "Contact Graph Routing",
    cgr_bullets,
    border=ACCENT_RED,
)

rl_bullets = [
    "State: (node, neighbors, link quality, buffer)",
    "Actions: forward | store | drop | split",
    "Reward: R = α(delivery) − β(delay) − γ(hops) − δ(drops) − ε(energy)",
    "ε-greedy exploration with decay",
    "Q-table + federated aggregation across nodes",
]
add_card(
    slide, Inches(5.1), Inches(1.55), Inches(4.6), Inches(2.5),
    "RL Agent",
    rl_bullets,
    border=ACCENT_CYAN,
)

add_stat_card(slide, Inches(0.3), Inches(4.25), Inches(3.1), Inches(1.1), "+20–40%", "Faster delivery vs CGR", GREEN)
add_stat_card(slide, Inches(3.55), Inches(4.25), Inches(3.1), Inches(1.1), "3600×", "Recovery speed", ACCENT_BLUE)
add_stat_card(slide, Inches(6.8), Inches(4.25), Inches(3.1), Inches(1.1), "Federated", "Multi-agent learning", ACCENT_PURPLE)

add_image_safe(
    slide, os.path.join(CHARTS_DIR, "rl_routing_heatmap.png"),
    Inches(0.4), Inches(5.55), Inches(9.2), Inches(1.8),
)

add_footer(slide, 15)

# ── SLIDE 16 ── Quantum Security ──────────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "cover")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "QUANTUM SECURITY"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

txBox2 = add_textbox(slide, Inches(0.6), Inches(0.9), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "Future-Proof"
p2.font.size = Pt(16)
p2.font.color.rgb = ACCENT_CYAN
p2.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(1.35), Inches(2.5))

bb84_bullets = [
    "1. Alice sends random polarized photons (H/V, D/A bases)",
    "2. Bob measures each photon in a random basis",
    "3. Public reconciliation — keep matching-basis bits",
    "4. Error estimation — sample subset for QBER",
    "5. Privacy amplification — universal hashing",
    "6. QBER < 11% → SECURE key established",
]
add_card(
    slide, Inches(0.3), Inches(1.55), Inches(4.8), Inches(2.5),
    "BB84 Protocol",
    bb84_bullets,
    border=ACCENT_PURPLE,
)

pqc_bullets = [
    "Kyber (ML-KEM) — key encapsulation",
    "Dilithium (ML-DSA) — digital signatures",
    "NIST PQC standard — quantum-resistant",
    "Hybrid classical-quantum key exchange",
]
add_card(
    slide, Inches(5.3), Inches(1.55), Inches(4.4), Inches(2.5),
    "Post-Quantum Cryptography",
    pqc_bullets,
    border=ACCENT_ORANGE,
)

deploy_headers = ["Phase", "Protocol", "Key Rate"]
deploy_rows = [
    ["Phase 1 — LEO", "BB84", "1–10 kbps"],
    ["Phase 2 — GEO", "BB84 + E91", "10–100 kbps"],
    ["Phase 3 — Mars", "E91 + Repeaters", "1+ kbps"],
]
_d5 = [deploy_headers] + deploy_rows
add_table(
    slide, Inches(0.3), Inches(4.25), Inches(9.4), Inches(1.5), len(_d5), len(deploy_headers), _d5,
    header_color=ACCENT_PURPLE,
)

add_image_safe(
    slide, os.path.join(CHARTS_DIR, "qkd_security.png"),
    Inches(0.4), Inches(5.9), Inches(9.2), Inches(1.5),
)

add_footer(slide, 16)

# ── SLIDE 17 ── Orbital Mechanics ─────────────────────────────────────────────
slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "fade")

txBox = add_textbox(slide, Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "ORBITAL MECHANICS"
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = WHITE
p.alignment = PP_ALIGN.LEFT

txBox2 = add_textbox(slide, Inches(0.6), Inches(0.9), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "Contact Windows"
p2.font.size = Pt(16)
p2.font.color.rgb = ACCENT_CYAN
p2.alignment = PP_ALIGN.LEFT

add_accent_line(slide, Inches(0.6), Inches(1.35), Inches(2.5))

mars_headers = ["Parameter", "Value"]
mars_rows = [
    ["Semi-major axis", "1.524 AU"],
    ["Synodic period", "779.94 days"],
    ["Distance range", "54.6M – 401M km"],
    ["Areostationary altitude", "17,032 km"],
    ["One-way light time", "3 – 22 minutes"],
]
_d6 = [mars_headers] + mars_rows
add_table(
    slide, Inches(0.3), Inches(1.55), Inches(4.7), Inches(2.3), len(_d6), len(mars_headers), _d6,
    header_color=ACCENT_ORANGE,
)

window_headers = ["Window", "Availability", "Duration", "Data Rate"]
window_rows = [
    ["Optimal", "99%", "8–12 hrs", "100–200 Mbps"],
    ["Good", "95%", "6–8 hrs", "20–100 Mbps"],
    ["Fair", "85%", "4–6 hrs", "5–20 Mbps"],
    ["Blackout", "0%", "2–4 weeks", "—"],
]
_d7 = [window_headers] + window_rows
add_table(
    slide, Inches(5.1), Inches(1.55), Inches(4.6), Inches(2.3), len(_d7), len(window_headers), _d7,
    header_color=ACCENT_BLUE,
)

add_image_safe(
    slide, os.path.join(CHARTS_DIR, "distance_over_time.png"),
    Inches(0.4), Inches(4.1), Inches(9.2), Inches(3.3),
)

add_footer(slide, 17)
# ── SLIDE 18 — End-to-End Mission ──────────────────────────────────────────────

slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "push")

txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "END-TO-END MISSION"
p.font.size, p.font.bold, p.font.color.rgb, p.alignment = Pt(28), True, WHITE, PP_ALIGN.LEFT

txBox2 = slide.shapes.add_textbox(Inches(0.6), Inches(0.95), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "Mars Surface \u2192 Earth"
p2.font.size, p2.font.color.rgb, p2.alignment = Pt(14), ACCENT_CYAN, PP_ALIGN.LEFT

hops = [
    "Rover", "UHF", "Areostationary", "Polar",
    "Deep Space 1550 nm", "LEO", "DSN / MOC",
]
hop_x_start = 0.4
hop_spacing = (SLIDE_WIDTH - Inches(2 * hop_x_start)) / len(hops)
for i, hop in enumerate(hops):
    cx = Inches(hop_x_start) + int(hop_spacing * i) + int(hop_spacing / 2) - Inches(0.45)
    cy = Inches(1.7)
    shape = add_shape(
        slide, Inches(0.4), Inches(0.4), Inches(0.9), Inches(0.45),
        fill_color=ACCENT_BLUE, border_color=CARD_BORDER, shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
    )
    tf = shape.text_frame
    tf.word_wrap = True
    pp = tf.paragraphs[0]
    pp.text = hop
    pp.font.size, pp.font.bold, pp.font.color.rgb, pp.alignment = Pt(9), True, WHITE, PP_ALIGN.CENTER
    if i < len(hops) - 1:
        arrow_left = int(cx) + Inches(0.9)
        arrow_top = int(cy) + Inches(0.15)
        arrow = slide.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW, arrow_left, arrow_top, Inches(0.2), Inches(0.15))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = ACCENT_CYAN
        arrow.line.fill.background()

stats_18 = [
    ("~13 min", "End-to-End Latency", ACCENT_BLUE),
    ("<5%", "Packet Loss", GREEN),
    ("98.7%", "Delivery Rate", ACCENT_PURPLE),
    ("7 hops", "Network Path", ACCENT_ORANGE),
]
stat_w = Inches(2.1)
stat_h = Inches(1.1)
stat_gap = Inches(0.25)
total_w = 4 * stat_w + 3 * stat_gap
stat_x0 = (SLIDE_WIDTH - total_w) // 2
for idx, (val, label, color) in enumerate(stats_18):
    sx = stat_x0 + int((stat_w + stat_gap) * idx)
    add_stat_card(slide, sx, Inches(2.55), stat_w, stat_h, val, label, color)

fail_x = Inches(0.6)
fail_y = Inches(4.0)
fail_w = SLIDE_WIDTH - Inches(1.2)
fail_h = Inches(1.2)
fail_card = add_card(slide, fail_x, fail_y, fail_w, fail_h)
fail_card.line.color.rgb = ACCENT_RED
fail_card.line.width = Pt(2.5)
tf_fail = fail_card.text_frame
tf_fail.word_wrap = True
p_fail_title = tf_fail.paragraphs[0]
p_fail_title.text = "\u26a0 FAILURE SCENARIO"
p_fail_title.font.size, p_fail_title.font.bold, p_fail_title.font.color.rgb = Pt(12), True, ACCENT_RED
p_fail_body = tf_fail.add_paragraph()
p_fail_body.text = (
    "Solar flare at T+400s \u2192 stored at MRS-Polar \u2192 "
    "rerouted via ES-L4 \u2192 delayed ~30 min NOT LOST"
)
p_fail_body.font.size, p_fail_body.font.color.rgb = Pt(11), WHITE

add_footer(slide, 18)

# ── SLIDE 19 — Data Flow Diagram (Text) ────────────────────────────────────────

slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "wipe")

txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "DATA FLOW DIAGRAM"
p.font.size, p.font.bold, p.font.color.rgb, p.alignment = Pt(28), True, WHITE, PP_ALIGN.LEFT

card_w = Inches(4.3)
card_h = Inches(3.8)
card_y = Inches(1.3)

left_card = add_card(slide, Inches(0.5), card_y, card_w, card_h)
tf_l = left_card.text_frame
tf_l.word_wrap = True
p_title_l = tf_l.paragraphs[0]
p_title_l.text = "Application \u2192 Transport"
p_title_l.font.size, p_title_l.font.bold, p_title_l.font.color.rgb = Pt(14), True, ACCENT_CYAN
p_title_l.space_after = Pt(10)

left_steps = [
    ("1. Source Node", "Science data generated"),
    ("2. Bundle Protocol", "BPv7 wraps data + metadata"),
    ("3. RL Routing", "Agent evaluates state, selects hop"),
    ("4. QKD Encrypt", "BB84 shared key applied"),
]
for step_title, step_desc in left_steps:
    p_t = tf_l.add_paragraph()
    p_t.text = step_title
    p_t.font.size, p_t.font.bold, p_t.font.color.rgb = Pt(11), True, WHITE
    p_t.space_before = Pt(6)
    p_d = tf_l.add_paragraph()
    p_d.text = step_desc
    p_d.font.size, p_d.font.color.rgb = Pt(9), LIGHT_GRAY

right_card = add_card(slide, Inches(5.2), card_y, card_w, card_h)
tf_r = right_card.text_frame
tf_r.word_wrap = True
p_title_r = tf_r.paragraphs[0]
p_title_r.text = "Convergence \u2192 Physical \u2192 Delivery"
p_title_r.font.size, p_title_r.font.bold, p_title_r.font.color.rgb = Pt(14), True, ACCENT_CYAN
p_title_r.space_after = Pt(10)

right_steps = [
    ("1. LTP Segmentation", "Bundle split into blocks"),
    ("2. Store & Wait", "Buffer until link available"),
    ("3. Physical TX", "UHF \u2192 Optical ISL \u2192 1550 nm \u2192 Ka-band"),
    ("4. LTP Reassemble", "Reassemble \u2192 Decrypt \u2192 Deliver"),
]
for step_title, step_desc in right_steps:
    p_t = tf_r.add_paragraph()
    p_t.text = step_title
    p_t.font.size, p_t.font.bold, p_t.font.color.rgb = Pt(11), True, WHITE
    p_t.space_before = Pt(6)
    p_d = tf_r.add_paragraph()
    p_d.text = step_desc
    p_d.font.size, p_d.font.color.rgb = Pt(9), LIGHT_GRAY

add_footer(slide, 19)

# ── SLIDE 20 — Data Flow Visual ────────────────────────────────────────────────

slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "cover")

txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "DATA FLOW DIAGRAM"
p.font.size, p.font.bold, p.font.color.rgb, p.alignment = Pt(28), True, WHITE, PP_ALIGN.LEFT

img_path_20 = os.path.join(DIAGRAMS_DIR, "data_flow.png")
add_image_safe(
    slide, img_path_20,
    Inches(0.4), Inches(1.2), Inches(9.2), Inches(5.5),
)

add_footer(slide, 20)

# ── SLIDE 21 — Performance ─────────────────────────────────────────────────────

slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "fade")

txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.3), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "PERFORMANCE COMPARISON"
p.font.size, p.font.bold, p.font.color.rgb, p.alignment = Pt(28), True, WHITE, PP_ALIGN.LEFT

txBox2 = slide.shapes.add_textbox(Inches(0.6), Inches(0.8), Inches(9), Inches(0.35))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "AETHERIX vs Current"
p2.font.size, p2.font.color.rgb, p2.alignment = Pt(14), ACCENT_CYAN, PP_ALIGN.LEFT

perf_data = [
    ["Metric", "Current (MRO)", "AETHERIX", "Improvement"],
    ["Downlink Rate", "0.5-6 Mbps", "2-200 Mbps", "10-100\u00d7"],
    ["Daily Volume", "5-10 GB", "50-100 GB", "10-20\u00d7"],
    ["Availability", "60-75%", ">95%", "+20-35%"],
    ["Routing", "Static (CGR)", "RL-adaptive", "Autonomous"],
    ["Security", "AES-256", "QKD + PQC", "Quantum-proof"],
    ["Scalability", "5-10 assets", "241 nodes", "24-48\u00d7"],
    ["Cost per MB", "$0.10", "$0.01", "10\u00d7 cheaper"],
    ["Conjunction", "Blackout", "50-70% via L4/L5", "+50-70%"],
]
add_table(
    slide, Inches(0.4), Inches(1.25), Inches(9.2), Inches(3.4), len(perf_data), len(perf_data[0]) if perf_data else 0, perf_data,
    header_color=GREEN,
)

chart1 = os.path.join(CHARTS_DIR, "performance_comparison.png")
add_image_safe(
    slide, chart1,
    Inches(0.3), Inches(4.8), Inches(4.7), Inches(2.0),
)
chart2 = os.path.join(CHARTS_DIR, "optical_vs_rf_radar.png")
add_image_safe(
    slide, chart2,
    Inches(5.1), Inches(4.8), Inches(4.7), Inches(2.0),
)

add_footer(slide, 21)

# ── SLIDE 22 — Implementation ──────────────────────────────────────────────────

slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "push")

txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "IMPLEMENTATION"
p.font.size, p.font.bold, p.font.color.rgb, p.alignment = Pt(28), True, WHITE, PP_ALIGN.LEFT

txBox2 = slide.shapes.add_textbox(Inches(0.6), Inches(0.95), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "What We Built"
p2.font.size, p2.font.color.rgb, p2.alignment = Pt(14), ACCENT_CYAN, PP_ALIGN.LEFT

impl_stats = [
    ("27", "Modules", GREEN),
    ("149", "Tests", ACCENT_BLUE),
    ("10", "Demos", ACCENT_PURPLE),
    ("5", "Policies", ACCENT_ORANGE),
]
stat_w = Inches(2.1)
stat_h = Inches(0.95)
stat_gap = Inches(0.25)
total_w_impl = 4 * stat_w + 3 * stat_gap
stat_x0_impl = (SLIDE_WIDTH - total_w_impl) // 2
for idx, (val, label, color) in enumerate(impl_stats):
    sx = stat_x0_impl + int((stat_w + stat_gap) * idx)
    add_stat_card(slide, sx, Inches(1.55), stat_w, stat_h, val, label, color)

modules_card = add_card(slide, Inches(0.5), Inches(2.8), Inches(4.3), Inches(1.7))
tf_mod = modules_card.text_frame
tf_mod.word_wrap = True
p_mod_title = tf_mod.paragraphs[0]
p_mod_title.text = "Core Modules"
p_mod_title.font.size, p_mod_title.font.bold, p_mod_title.font.color.rgb = Pt(13), True, ACCENT_CYAN
p_mod_title.space_after = Pt(6)
for mod_name in ["Link Budget", "RL Agent", "QKD", "Bundle Protocol", "Topology", "Simulation"]:
    p_mod = tf_mod.add_paragraph()
    p_mod.text = f"\u2022  {mod_name}"
    p_mod.font.size, p_mod.font.color.rgb = Pt(11), WHITE

std_card = add_card(slide, Inches(5.1), Inches(2.8), Inches(4.6), Inches(1.7))
tf_std = std_card.text_frame
tf_std.word_wrap = True
p_std_title = tf_std.paragraphs[0]
p_std_title.text = "Standards Compliance"
p_std_title.font.size, p_std_title.font.bold, p_std_title.font.color.rgb = Pt(13), True, ACCENT_CYAN
p_std_title.space_after = Pt(6)
standards_data = [
    ["Standard", "Title"],
    ["RFC 9171", "Bundle Protocol v7"],
    ["RFC 4838", "DTN Architecture"],
    ["RFC 5326", "LTP (deep space)"],
    ["RFC 9172", "BPSec (security)"],
    ["CCSDS 734.2-B-1", "CCSDS Bundle Protocol"],
    ["CCSDS 734.3-B-1", "SABR (contact routing)"],
    ["CCSDS 141.0-B-1", "Optical comms phys."],
]
std_tbl = add_table(
    slide, Inches(5.2), Inches(3.35), Inches(4.4), Inches(1.1), len(standards_data), len(standards_data[0]) if standards_data else 0, standards_data,
    header_color=ACCENT_BLUE,
)

add_footer(slide, 22)

# ── SLIDE 23 — Roadmap ────────────────────────────────────────────────────────

slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "wipe")

txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "ROADMAP"
p.font.size, p.font.bold, p.font.color.rgb, p.alignment = Pt(28), True, WHITE, PP_ALIGN.LEFT

txBox2 = slide.shapes.add_textbox(Inches(0.6), Inches(0.95), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "From Demo to Deployment"
p2.font.size, p2.font.color.rgb, p2.alignment = Pt(14), ACCENT_CYAN, PP_ALIGN.LEFT

phases = [
    ("Phase 1-4  \u2713 Complete", "Topology \u2022 RL \u2022 QKD \u2022 Web UI \u2022 149 tests", GREEN),
    ("Phase 5  Network Sim", "ns-3 integration, realistic channel models", ACCENT_BLUE),
    ("Phase 6  Production", "DQN agent, ION-DTN stack, hardware-in-loop", ACCENT_PURPLE),
    ("Phase 7  Hardware", "SDR prototyping, optical ground station demo", ACCENT_ORANGE),
]
phase_w = Inches(4.6)
phase_h = Inches(0.7)
phase_gap = Inches(0.15)
phase_x = Inches(0.5)
for idx, (title, desc, color) in enumerate(phases):
    py = Inches(1.55) + int((phase_h + phase_gap) * idx)
    card = add_card(slide, phase_x, py, phase_w, phase_h)
    card.line.color.rgb = color
    card.line.width = Pt(2)
    accent_bar = add_shape(
        slide, Inches(0.4), Inches(0.4), Inches(0.08), Inches(0.2), shape_type=MSO_SHAPE.RECTANGLE,
        fill_color=color,
    )
    tf_ph = card.text_frame
    tf_ph.word_wrap = True
    p_ph = tf_ph.paragraphs[0]
    p_ph.text = title
    p_ph.font.size, p_ph.font.bold, p_ph.font.color.rgb = Pt(12), True, color
    p_ph2 = tf_ph.add_paragraph()
    p_ph2.text = desc
    p_ph2.font.size, p_ph2.font.color.rgb = Pt(9), LIGHT_GRAY

chart_23 = os.path.join(CHARTS_DIR, "mission_timeline.png")
add_image_safe(
    slide, chart_23,
    Inches(5.3), Inches(1.55), Inches(4.4), Inches(2.7),
)

add_footer(slide, 23)

# ── SLIDE 24 — Conclusion ──────────────────────────────────────────────────────

slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "cover")

txBox = slide.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(9), Inches(0.6))
p = txBox.text_frame.paragraphs[0]
p.text = "CONCLUSION"
p.font.size, p.font.bold, p.font.color.rgb, p.alignment = Pt(28), True, WHITE, PP_ALIGN.LEFT

txBox2 = slide.shapes.add_textbox(Inches(0.6), Inches(0.95), Inches(9), Inches(0.4))
p2 = txBox2.text_frame.paragraphs[0]
p2.text = "AETHERIX Delivers"
p2.font.size, p2.font.color.rgb, p2.alignment = Pt(14), ACCENT_CYAN, PP_ALIGN.LEFT

concl_card_w = Inches(4.3)
concl_card_h = Inches(1.7)

problem_card = add_card(slide, Inches(0.5), Inches(1.6), concl_card_w, concl_card_h)
problem_card.line.color.rgb = ACCENT_RED
problem_card.line.width = Pt(2.5)
tf_prob = problem_card.text_frame
tf_prob.word_wrap = True
p_prob_t = tf_prob.paragraphs[0]
p_prob_t.text = "Problem Solved"
p_prob_t.font.size, p_prob_t.font.bold, p_prob_t.font.color.rgb = Pt(14), True, ACCENT_RED
p_prob_t.space_after = Pt(8)
p_prob_b = tf_prob.add_paragraph()
p_prob_b.text = "TCP/IP can\u2019t work at interplanetary distances"
p_prob_b.font.size, p_prob_b.font.color.rgb = Pt(12), WHITE

built_card = add_card(slide, Inches(5.2), Inches(1.6), concl_card_w, concl_card_h)
built_card.line.color.rgb = GREEN
built_card.line.width = Pt(2.5)
tf_built = built_card.text_frame
tf_built.word_wrap = True
p_built_t = tf_built.paragraphs[0]
p_built_t.text = "What We Built"
p_built_t.font.size, p_built_t.font.bold, p_built_t.font.color.rgb = Pt(14), True, GREEN
p_built_t.space_after = Pt(8)
p_built_b = tf_built.add_paragraph()
p_built_b.text = "BPv7 \u2022 RL Routing \u2022 QKD \u2022 Optical/RF Hybrid"
p_built_b.font.size, p_built_b.font.color.rgb = Pt(12), WHITE

conc_stats = [
    ("10-100\u00d7", "Data Rate", GREEN),
    (">95%", "Availability", ACCENT_BLUE),
    ("RL", "Adaptive Routing", ACCENT_PURPLE),
    ("QKD", "Quantum Security", ACCENT_ORANGE),
]
stat_w_c = Inches(2.1)
stat_h_c = Inches(1.1)
stat_gap_c = Inches(0.25)
total_w_c = 4 * stat_w_c + 3 * stat_gap_c
stat_x0_c = (SLIDE_WIDTH - total_w_c) // 2
for idx, (val, label, color) in enumerate(conc_stats):
    sx = stat_x0_c + int((stat_w_c + stat_gap_c) * idx)
    add_stat_card(slide, sx, Inches(3.7), stat_w_c, stat_h_c, val, label, color)

add_footer(slide, 24)

# ── SLIDE 25 — Thank You ──────────────────────────────────────────────────────

slide = new_slide()
set_slide_bg(slide, BG_DARK)
add_slide_transition(slide, "fade")

top_bar = add_shape(
    slide, Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.08), shape_type=MSO_SHAPE.RECTANGLE,
    fill_color=ACCENT_BLUE,
)

ty_box = slide.shapes.add_textbox(
    Inches(0.5), Inches(0.6), SLIDE_WIDTH - Inches(1), Inches(0.9)
)
p_ty = ty_box.text_frame.paragraphs[0]
p_ty.text = "THANK YOU"
p_ty.font.size, p_ty.font.bold, p_ty.font.color.rgb, p_ty.alignment = (
    Pt(64), True, WHITE, PP_ALIGN.CENTER,
)

add_accent_line(slide, Inches(3.6), Inches(1.7), Inches(2.8), ACCENT_CYAN)

q_box = slide.shapes.add_textbox(
    Inches(0.5), Inches(2.0), SLIDE_WIDTH - Inches(1), Inches(0.6)
)
p_q = q_box.text_frame.paragraphs[0]
p_q.text = "Questions?"
p_q.font.size, p_q.font.bold, p_q.font.color.rgb, p_q.alignment = (
    Pt(36), True, ACCENT_CYAN, PP_ALIGN.CENTER,
)

ty_stats = [
    ("10-100\u00d7", "Data Rate", GREEN),
    (">95%", "Availability", ACCENT_BLUE),
    ("RL", "Adaptive Routing", ACCENT_PURPLE),
    ("QKD", "Quantum Security", ACCENT_ORANGE),
]
stat_w_ty = Inches(2.1)
stat_h_ty = Inches(0.95)
stat_gap_ty = Inches(0.25)
total_w_ty = 4 * stat_w_ty + 3 * stat_gap_ty
stat_x0_ty = (SLIDE_WIDTH - total_w_ty) // 2
for idx, (val, label, color) in enumerate(ty_stats):
    sx = stat_x0_ty + int((stat_w_ty + stat_gap_ty) * idx)
    add_stat_card(slide, sx, Inches(3.0), stat_w_ty, stat_h_ty, val, label, color)

contact_box = slide.shapes.add_textbox(
    Inches(0.5), Inches(4.4), SLIDE_WIDTH - Inches(1), Inches(0.5)
)
p_contact = contact_box.text_frame.paragraphs[0]
p_contact.text = "Muhammad Abdullah Tariq"
p_contact.font.size, p_contact.font.bold, p_contact.font.color.rgb, p_contact.alignment = (
    Pt(20), True, WHITE, PP_ALIGN.CENTER,
)

links_box = slide.shapes.add_textbox(
    Inches(0.5), Inches(4.9), SLIDE_WIDTH - Inches(1), Inches(0.4)
)
p_links = links_box.text_frame.paragraphs[0]
p_links.text = "matx104.github.io/AETHERIX  |  github.com/matx104/AETHERIX"
p_links.font.size, p_links.font.color.rgb, p_links.alignment = (
    Pt(12), MED_GRAY, PP_ALIGN.CENTER,
)

bottom_bar = add_shape(
    slide, Inches(0), SLIDE_HEIGHT - Inches(0.08), SLIDE_WIDTH, Inches(0.08), shape_type=MSO_SHAPE.RECTANGLE,
    fill_color=ACCENT_BLUE,
)

# ── SAVE BLOCK ─────────────────────────────────────────────────────────────────

pptx_path = os.path.join(OUTPUT_DIR, "AETHERIX_Presentation.pptx")
prs.save(pptx_path)
print(f"\n\u2713 PPTX saved: {pptx_path}")
print(f"  Slides: {len(prs.slides)}")
