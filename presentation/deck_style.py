"""
AETHERIX deck style — shared design system for the PDF deck generators.

Both generate_pdf.py (full, 50 slides) and generate_pdf_compact.py (31 slides)
import their page geometry, color tokens, typography and drawing helpers from
here so the two decks stay visually identical.

Design notes:
- Page is 900 x 595.28 pt (~3:2). The deck's layout grid spans x=40..860;
  page width 900 gives symmetric 40 pt margins and puts PAGE_W/2 at the
  grid center (450), so centered elements align with fixed-coordinate cards.
- Bottom architecture (reserved zone, content floor at y=82):
    y 16   footer line: citations (left, italic) + page number (right)
    y 28   hairline rule
    y 32..74  speaker-notes band (full deck only)
- Typography: Lato (system TTF, embedded) — Black for display, Bold/Semibold
  for emphasis, Regular for body, Italic for notes. Callers keep passing the
  legacy "Helvetica*" names; they are mapped to Lato at draw time.
"""

import os
import random

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ----------------------------------------------------------------- geometry
PAGE_W, PAGE_H = 900.0, 595.28
MARGIN = 40
CONTENT_W = PAGE_W - 2 * MARGIN          # 820 — the classic grid width
CONTENT_FLOOR = 82                       # nothing but footer/notes below this

# ------------------------------------------------------------------- colors
BG_DARK = HexColor("#0A0E1A")
BG_HIGH = HexColor("#131C33")            # top of background gradient
ACCENT_BLUE = HexColor("#009EFF")
ACCENT_CYAN = HexColor("#00D4AA")
ACCENT_PURPLE = HexColor("#8B5CF6")
ACCENT_ORANGE = HexColor("#FF8C00")
ACCENT_RED = HexColor("#FF4D4D")
WHITE = HexColor("#FFFFFF")
LIGHT_GRAY = HexColor("#B8C1D4")
MED_GRAY = HexColor("#6B7B96")
CARD_BG = HexColor("#131A2E")
CARD_BORDER = HexColor("#1E2A42")
GREEN = HexColor("#2ECC71")
TABLE_ROW_ALT = HexColor("#182236")
HAIRLINE = HexColor("#223052")
NOTES_GOLD = HexColor("#FFD93D")

# --------------------------------------------------------------- typography
_LATO_DIR = "/usr/share/fonts/truetype/lato"
_FONTS = {
    "Lato": "Lato-Regular.ttf",
    "Lato-Bold": "Lato-Bold.ttf",
    "Lato-Black": "Lato-Black.ttf",
    "Lato-Semibold": "Lato-Semibold.ttf",
    "Lato-Italic": "Lato-Italic.ttf",
}
_lato_ok = True
try:
    for name, fn in _FONTS.items():
        pdfmetrics.registerFont(TTFont(name, os.path.join(_LATO_DIR, fn)))
except Exception:
    _lato_ok = False

# Legacy font names used throughout the page code, mapped to the deck faces.
if _lato_ok:
    FONT_MAP = {
        "Helvetica": "Lato",
        "Helvetica-Bold": "Lato-Bold",
        "Helvetica-Oblique": "Lato-Italic",
        "Helvetica-BoldOblique": "Lato-Bold",
    }
    FONT_DISPLAY = "Lato-Black"
    FONT_SEMI = "Lato-Semibold"
    FONT_ITALIC = "Lato-Italic"
else:  # graceful fallback if the system fonts move
    FONT_MAP = {}
    FONT_DISPLAY = "Helvetica-Bold"
    FONT_SEMI = "Helvetica-Bold"
    FONT_ITALIC = "Helvetica-Oblique"


def _map_font(font, bold):
    fn = "Helvetica-Bold" if bold else font
    return FONT_MAP.get(fn, fn)


def with_alpha(color, alpha):
    return Color(color.red, color.green, color.blue, alpha=alpha)


# ------------------------------------------------------------ deck registry
_deck = {"total": 0, "counter": [1], "notes": {}}


def configure(total_slides, speaker_notes=None):
    """Called once by each generator before drawing pages."""
    _deck["total"] = total_slides
    _deck["counter"] = [1]
    _deck["notes"] = speaker_notes if speaker_notes is not None else {}
    return _deck["notes"]


def page_counter():
    return _deck["counter"]


# ----------------------------------------------------------------- backdrop
def draw_bg(c):
    """Deep-space backdrop: subtle vertical gradient, dark base."""
    try:
        c.saveState()
        p = c.beginPath()
        p.rect(0, 0, PAGE_W, PAGE_H)
        c.clipPath(p, stroke=0, fill=0)
        c.linearGradient(0, 0, 0, PAGE_H, (BG_DARK, BG_HIGH), extend=False)
        c.restoreState()
    except Exception:
        c.setFillColor(BG_DARK)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def draw_starfield(c, seed=59, n=110):
    """Seeded starfield for the title/closing pages (deterministic)."""
    rng = random.Random(seed)
    c.saveState()
    for _ in range(n):
        x = rng.uniform(0, PAGE_W)
        y = rng.uniform(0, PAGE_H)
        r = rng.choice((0.4, 0.55, 0.75, 1.0))
        a = rng.uniform(0.18, 0.6)
        c.setFillColor(Color(1, 1, 1, alpha=a))
        c.circle(x, y, r, fill=1, stroke=0)
    c.restoreState()


def draw_orbit_arc(c, cy_offset=-330):
    """Signature motif: a faint Earth-to-Mars transfer arc across the page."""
    c.saveState()
    cx, cy = PAGE_W / 2, cy_offset
    r = 560
    c.setStrokeColor(Color(0.0, 0.62, 1.0, alpha=0.28))
    c.setLineWidth(1.0)
    c.setDash(1, 4)
    c.circle(cx, cy, r, fill=0, stroke=1)
    c.setDash()
    # Earth (cyan, left) and Mars (orange, right) riding the arc
    import math
    for ang, col, pr in ((118, ACCENT_CYAN, 3.2), (62, ACCENT_ORANGE, 2.6)):
        px = cx + r * math.cos(math.radians(ang))
        py = cy + r * math.sin(math.radians(ang))
        c.setFillColor(with_alpha(col, 0.9))
        c.circle(px, py, pr, fill=1, stroke=0)
        c.setStrokeColor(with_alpha(col, 0.25))
        c.setLineWidth(0.75)
        c.circle(px, py, pr + 2.6, fill=0, stroke=1)
    c.restoreState()


def draw_accent_line(c, x, y, w, color=ACCENT_BLUE, h=3):
    c.setFillColor(color)
    c.rect(x, y, w, h, fill=1, stroke=0)


def draw_top_bar(c, color=ACCENT_BLUE):
    try:
        c.saveState()
        p = c.beginPath()
        p.rect(0, PAGE_H - 4, PAGE_W, 4)
        c.clipPath(p, stroke=0, fill=0)
        c.linearGradient(0, PAGE_H, PAGE_W, PAGE_H, (ACCENT_BLUE, ACCENT_CYAN), extend=False)
        c.restoreState()
    except Exception:
        c.setFillColor(color)
        c.rect(0, PAGE_H - 4, PAGE_W, 4, fill=1, stroke=0)


def draw_bottom_bar(c, color=ACCENT_BLUE):
    try:
        c.saveState()
        p = c.beginPath()
        p.rect(0, 0, PAGE_W, 4)
        c.clipPath(p, stroke=0, fill=0)
        c.linearGradient(0, 0, PAGE_W, 0, (ACCENT_CYAN, ACCENT_BLUE), extend=False)
        c.restoreState()
    except Exception:
        c.setFillColor(color)
        c.rect(0, 0, PAGE_W, 4, fill=1, stroke=0)


# ------------------------------------------------------------------- shapes
def draw_card(c, x, y, w, h, border_color=ACCENT_BLUE):
    c.setFillColor(CARD_BG)
    c.setStrokeColor(with_alpha(border_color, 0.55))
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 7, fill=1, stroke=1)


def draw_text(c, text, x, y, font="Helvetica", size=14, color=WHITE, bold=False, align="left"):
    fn = _map_font(font, bold)
    # Display face + gentle tracking for large headings
    tracking = 0.0
    if bold and size >= 22 and _lato_ok:
        fn = FONT_DISPLAY
        tracking = size * 0.02
    c.setFillColor(color)
    if tracking:
        # Char spacing lives on the text object, so render tracked text there.
        adv = c.stringWidth(text, fn, size) + tracking * max(0, len(text) - 1)
        if align == "center":
            x -= adv / 2
        elif align == "right":
            x -= adv
        t = c.beginText(x, y)
        t.setFont(fn, size)
        t.setCharSpace(tracking)
        t.setFillColor(color)
        t.textOut(text)
        c.drawText(t)
        return
    c.setFont(fn, size)
    if align == "center":
        c.drawCentredString(x, y, text)
    elif align == "right":
        c.drawRightString(x, y, text)
    else:
        c.drawString(x, y, text)


def draw_multiline(c, text, x, y, font="Helvetica", size=12, color=WHITE, leading=16, bold=False):
    fn = _map_font(font, bold)
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
    body_font = FONT_MAP.get("Helvetica", "Helvetica")
    head_font = FONT_MAP.get("Helvetica-Bold", "Helvetica-Bold")
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), with_alpha(header_color, 0.16)),
        ('TEXTCOLOR', (0, 0), (-1, 0), header_color),
        ('FONTNAME', (0, 0), (-1, 0), head_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 1), (-1, -1), body_font),
        ('TEXTCOLOR', (0, 1), (-1, -1), LIGHT_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, HAIRLINE),
        ('LINEABOVE', (0, 0), (-1, 0), 0.75, with_alpha(header_color, 0.6)),
    ])
    for i in range(1, len(data)):
        bg = CARD_BG if i % 2 == 1 else TABLE_ROW_ALT
        style.add('BACKGROUND', (0, i), (-1, i), bg)

    t = Table(data, colWidths=col_widths)
    t.setStyle(style)
    tw, th = t.wrap(0, 0)
    t.drawOn(c, x, y - th)
    return th


# ------------------------------------------------------- footer & notes band
def draw_footer(c, num=None, total=None, citations=None):
    _deck["counter"][0] += 1
    n = _deck["counter"][0]
    tt = _deck["total"]
    # hairline rule above the footer strip
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.5)
    c.line(MARGIN, 28, PAGE_W - MARGIN, 28)
    # left: citations when present, otherwise the wordmark
    c.setFillColor(MED_GRAY)
    if citations:
        c.setFont(FONT_ITALIC, 6.5)
        c.drawString(MARGIN, 16, citations)
    else:
        t = c.beginText(MARGIN, 16)
        t.setFont(FONT_SEMI, 6.8)
        t.setCharSpace(0.7)
        t.setFillColor(MED_GRAY)
        t.textOut("AETHERIX  —  INTERPLANETARY COMMUNICATION NETWORK")
        c.drawText(t)
    c.setFont(FONT_SEMI, 8)
    c.drawRightString(PAGE_W - MARGIN, 16, f"{n} / {tt}")
    notes = _deck["notes"]
    if n in notes:
        draw_speaker_notes(c, notes[n])


def draw_speaker_notes(c, text):
    """Compact notes band that lives inside the reserved bottom zone (32..74)."""
    c.saveState()
    nf, ns, lh, ml = FONT_ITALIC, 6.5, 8.0, 4
    by, bh = 32, 42
    c.setFillColor(Color(0.05, 0.07, 0.13, alpha=0.96))
    c.roundRect(MARGIN - 8, by, PAGE_W - 2 * (MARGIN - 8), bh, 4, fill=1, stroke=0)
    c.setFillColor(NOTES_GOLD)
    c.rect(MARGIN - 8, by, 2.5, bh, fill=1, stroke=0)
    c.setFont(FONT_SEMI, 6)
    c.drawString(MARGIN + 2, by + bh - 9, "SPEAKER NOTES")
    c.setFillColor(LIGHT_GRAY)
    c.setFont(nf, ns)
    mw = PAGE_W - 2 * MARGIN - 100
    words = text.split()
    lines, cur = [], ""
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
    y = by + bh - 10
    for i, ln in enumerate(lines[:ml]):
        c.drawString(MARGIN + 96, y - lh * i, ln)
    c.restoreState()


# ------------------------------------------------------------- chart pages
def draw_chart_page(c, charts_dir, chart_file, title, subtitle, caption,
                    accent_color=ACCENT_BLUE, notes=None, citations=None):
    """Full-page chart slide: matplotlib PNG matted on a white rounded panel."""
    draw_bg(c)
    draw_text(c, title, MARGIN, PAGE_H - 50, size=22, color=WHITE, bold=True)
    if subtitle:
        draw_text(c, subtitle, MARGIN, PAGE_H - 75, size=13, color=accent_color)
    draw_accent_line(c, MARGIN, PAGE_H - 85, 180, accent_color)

    img_path = os.path.join(charts_dir, chart_file)
    panel_x, panel_y = 90, 104
    panel_w, panel_h = PAGE_W - 2 * panel_x, PAGE_H - 104 - 120
    if os.path.exists(img_path):
        c.setFillColor(WHITE)
        c.setStrokeColor(with_alpha(accent_color, 0.35))
        c.setLineWidth(1)
        c.roundRect(panel_x, panel_y, panel_w, panel_h, 8, fill=1, stroke=1)
        try:
            img = ImageReader(img_path)
            iw, ih = img.getSize()
            pad = 10
            aw, ah = panel_w - 2 * pad, panel_h - 2 * pad
            scale = min(aw / iw, ah / ih)
            dw, dh = iw * scale, ih * scale
            c.drawImage(img_path,
                        panel_x + (panel_w - dw) / 2,
                        panel_y + (panel_h - dh) / 2,
                        width=dw, height=dh, mask='auto')
        except Exception:
            pass
    if caption:
        draw_text(c, caption, PAGE_W / 2, 88, size=9, color=MED_GRAY, align="center")
    if notes is not None and _deck["notes"] is not None:
        _deck["notes"][_deck["counter"][0] + 1] = notes
    draw_footer(c, citations=citations)
    c.showPage()
