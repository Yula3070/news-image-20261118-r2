#!/usr/bin/env python3
"""One Day, the Whole World - front page for Wednesday 18 November 2026.

A single-page newspaper (1024x1024) drawn entirely with PIL. Every picture
on the page is a flat vector shape drawn in this file: no photos, no copied
art, no external images. Output is deterministic: entry.png.

Layout, top to bottom:
  navy masthead with gold kicker -> 3 illustrated lead stories
  -> 6 middle stories with icons -> BY THE NUMBERS strip
  -> dotted world map with numbered pins + ALSO list of 26 short stories
  -> sources footer. 35 stories in total.
"""

import os
from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 24
CONTENT_W = PAGE - 2 * MARGIN

# ---- palette ------------------------------------------------------------
PAPER = (246, 240, 223)
INK = (30, 30, 28)
NAVY = (20, 38, 66)
NAVY_DEEP = (13, 26, 46)
GOLD = (201, 162, 39)
GOLD_SOFT = (222, 206, 150)
RED = (176, 32, 32)
TEAL = (16, 106, 106)
GREY = (112, 108, 96)
RULE = (198, 188, 160)
SKY_PALE = (214, 228, 236)
SEA = (24, 64, 96)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _pick(names):
    for name in names:
        path = os.path.join(FONT_DIR, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(names[0])


def serif(size, bold=False, italic=False):
    if bold:
        return ImageFont.truetype(_pick(["DejaVuSerif-Bold.ttf"]), size)
    if italic:
        return ImageFont.truetype(
            _pick(["DejaVuSerif-Italic.ttf", "DejaVuSerif.ttf"]), size)
    return ImageFont.truetype(_pick(["DejaVuSerif.ttf"]), size)


def sans(size, bold=False, italic=False):
    if bold:
        return ImageFont.truetype(_pick(["DejaVuSans-Bold.ttf"]), size)
    if italic:
        return ImageFont.truetype(
            _pick(["DejaVuSans-Oblique.ttf", "DejaVuSans.ttf"]), size)
    return ImageFont.truetype(_pick(["DejaVuSans.ttf"]), size)


# ---- text helpers -------------------------------------------------------

def wrap_words(draw, text, font, max_w):
    """Greedy word wrap by pixel width. Returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # a single word wider than the column: split it by characters
            while draw.textlength(word, font=font) > max_w and len(word) > 1:
                cut = len(word) // 2
                while cut > 1 and draw.textlength(
                        word[:cut], font=font) > max_w:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def text_block(draw, x, y, text, font, fill, max_w, leading, max_lines=None):
    lines = wrap_words(draw, text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    return draw_lines(draw, x, y, lines, font, fill, leading), lines


def badge(draw, cx, cy, number, radius=10):
    """Red circle with a white number, centred on (cx, cy)."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=RED)
    f = sans(radius + 2, bold=True)
    w = draw.textlength(str(number), font=f)
    h = f.getbbox(str(number))[3]
    draw.text((cx - w / 2, cy - h / 2 - 1), str(number), font=f,
              fill=(255, 255, 255))


# ---- dotted world map ---------------------------------------------------
# Coarse equirectangular land mask: row -> list of (first_col, last_col),
# 72 columns of 5 degrees longitude, 25 rows of 6 degrees latitude,
# row 0 = 84..90 N, row 24 = 54..60 S. Hand-drawn, approximate on purpose:
# at dot size the continents stay recognisable.
LAND_ROWS = {
    1: [(26, 29)],
    2: [(8, 15), (25, 30)],
    3: [(2, 8), (9, 20), (25, 30), (36, 40), (42, 70)],
    4: [(2, 9), (10, 22), (26, 30), (33, 33), (36, 41), (42, 71)],
    5: [(9, 24), (33, 34), (37, 41), (42, 71)],
    6: [(10, 26), (33, 44), (45, 71)],
    7: [(12, 28), (33, 45), (46, 66), (68, 68)],
    8: [(12, 28), (34, 45), (46, 64), (68, 70)],
    9: [(13, 27), (34, 44), (45, 50), (52, 66), (69, 70)],
    10: [(13, 25), (33, 45), (47, 51), (53, 58), (60, 65)],
    11: [(14, 21), (32, 46), (54, 57), (60, 64)],
    12: [(16, 20), (32, 46), (60, 65), (66, 66)],
    13: [(17, 19), (31, 47), (60, 68)],
    14: [(20, 26), (33, 46), (61, 69), (70, 71)],
    15: [(20, 27), (34, 45), (62, 70)],
    16: [(21, 27), (35, 44), (60, 66)],
    17: [(21, 26), (36, 43), (47, 47), (59, 66)],
    18: [(22, 25), (36, 42), (47, 47), (58, 67)],
    19: [(22, 25), (36, 41), (58, 66)],
    20: [(22, 24), (37, 40), (59, 65), (69, 70)],
    21: [(22, 24), (69, 69)],
    22: [(22, 23)],
    23: [(22, 23)],
    24: [(22, 22)],
}

# (story number, grid column, grid row) - nudged where pins would collide.
PINS = [
    (1, 46, 11),   # Bahrain / Qeshm, Gulf
    (2, 43, 7),    # Kerch Strait
    (3, 61, 13),   # Manila
    (4, 12, 9),    # Silicon Valley
    (5, 42, 10),   # Jerusalem
    (6, 37, 7),    # Brussels
    (7, 52, 12),   # Andhra Pradesh
    (8, 21, 8),    # New York
    (9, 58, 10),   # Shenzhen
]


def paint_map(draw, x0, y0, w, h):
    """Dotted continents with red numbered pins for stories 1-9."""
    cols, rows = 72, 25
    sx, sy = w / cols, h / rows
    for r in range(rows):
        for a, b in LAND_ROWS.get(r, []):
            for c in range(a, b + 1):
                cx = x0 + (c + 0.5) * sx
                cy = y0 + (r + 0.5) * sy
                draw.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6],
                             fill=(96, 110, 128))
    for num, c, r in PINS:
        cx = x0 + (c + 0.5) * sx
        cy = y0 + (r + 0.5) * sy
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                     outline=(255, 255, 255), width=1)
        f = sans(10, bold=True)
        t = str(num)
        tw = draw.textlength(t, font=f)
        th = f.getbbox(t)[3]
        draw.text((cx - tw / 2, cy - th / 2 - 1), t, font=f,
                  fill=(255, 255, 255))


# ---- lead illustrations (flat vector, drawn here) -----------------------

def paint_gulf(draw, x, y, w, h):
    """Night over the Strait of Hormuz: radar dome, jets, missile trails."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY_DEEP)
    # stars
    for sx, sy, r in [(0.08, 0.14, 1.5), (0.22, 0.08, 1.2), (0.4, 0.2, 1.5),
                      (0.55, 0.1, 1.2), (0.72, 0.18, 1.5), (0.88, 0.09, 1.2),
                      (0.95, 0.3, 1.4), (0.3, 0.28, 1.1)]:
        draw.ellipse([x + sx * w - r, y + sy * h - r,
                      x + sx * w + r, y + sy * h + r], fill=(255, 255, 255))
    # crescent moon
    mx, my, mr = x + 0.82 * w, y + 0.24 * h, 15
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=GOLD_SOFT)
    draw.ellipse([mx - mr + 7, my - mr - 2, mx + mr + 7, my + mr - 2],
                 fill=NAVY_DEEP)
    # missile trails
    draw.line([(x + 0.10 * w, y + 0.42 * h), (x + 0.34 * w, y + 0.18 * h)],
              fill=(240, 140, 60), width=3)
    draw.line([(x + 0.16 * w, y + 0.50 * h), (x + 0.42 * w, y + 0.30 * h)],
              fill=(240, 140, 60), width=3)
    for tx, ty in [(0.34, 0.18), (0.42, 0.30)]:
        draw.ellipse([x + tx * w - 4, y + ty * h - 4,
                      x + tx * w + 4, y + ty * h + 4], fill=(255, 200, 90))
    # two jet silhouettes (simple delta shapes)
    for jx, jy, s in [(0.60, 0.28, 1.25), (0.74, 0.42, 1.0)]:
        px, py = x + jx * w, y + jy * h
        draw.polygon([(px - 16 * s, py), (px + 16 * s, py - 3 * s),
                      (px + 10 * s, py + 4 * s), (px - 6 * s, py + 5 * s)],
                     fill=(210, 214, 220))
    # sea
    sea_y = y + 0.62 * h
    draw.rectangle([x, sea_y, x + w, y + h], fill=SEA)
    for wy in (0.70, 0.80, 0.90):
        for k in range(4):
            ax = x + (0.06 + k * 0.24) * w
            ay = y + wy * h
            draw.arc([ax, ay - 3, ax + 22, ay + 5], 200, 340,
                     fill=(140, 180, 210), width=2)
    # radar dome on a headland
    draw.polygon([(x + 0.06 * w, y + h), (x + 0.06 * w, y + 0.78 * h),
                  (x + 0.16 * w, y + 0.78 * h), (x + 0.16 * w, y + h)],
                 fill=(52, 58, 66))
    draw.pieslice([x + 0.055 * w, y + 0.60 * h, x + 0.165 * w, y + 0.80 * h],
                  180, 360, fill=(235, 235, 228))


def paint_bridge(draw, x, y, w, h):
    """The Kerch crossing: deck in two pieces, the fallen arch in the water."""
    draw.rectangle([x, y, x + w, y + h], fill=SKY_PALE)
    # sun and clouds
    draw.ellipse([x + 0.78 * w, y + 0.10 * h, x + 0.78 * w + 26,
                  y + 0.10 * h + 26], fill=(240, 190, 80))
    for cx, cy, s in [(0.18, 0.16, 1.0), (0.55, 0.10, 0.8)]:
        px, py = x + cx * w, y + cy * h
        draw.ellipse([px, py, px + 34 * s, py + 12 * s], fill=(255, 255, 255))
        draw.ellipse([px + 10 * s, py - 6 * s, px + 40 * s, py + 8 * s],
                     fill=(255, 255, 255))
    # sea
    sea_y = y + 0.60 * h
    draw.rectangle([x, sea_y, x + w, y + h], fill=(64, 122, 158))
    for wy in (0.72, 0.84, 0.94):
        for k in range(4):
            ax = x + (0.05 + k * 0.25) * w
            ay = y + wy * h
            draw.arc([ax, ay - 3, ax + 22, ay + 5], 200, 340,
                     fill=(190, 215, 230), width=2)
    # deck, split in the middle
    deck_y = y + 0.46 * h
    draw.rectangle([x, deck_y, x + 0.42 * w, deck_y + 8], fill=(70, 74, 80))
    draw.rectangle([x + 0.58 * w, deck_y, x + w, deck_y + 8],
                   fill=(70, 74, 80))
    # standing arch (right half) and broken stub (left half)
    draw.arc([x + 0.60 * w, deck_y - 34, x + 0.98 * w, deck_y + 22], 180, 360,
             fill=(70, 74, 80), width=5)
    draw.arc([x + 0.02 * w, deck_y - 30, x + 0.40 * w, deck_y + 20], 180, 270,
             fill=(70, 74, 80), width=5)
    # piers
    for px in (0.12, 0.30, 0.68, 0.88):
        draw.rectangle([x + px * w, deck_y + 8, x + px * w + 6, sea_y + 26],
                       fill=(88, 92, 98))
    # fallen arch segment, tilted, half-submerged
    draw.polygon([(x + 0.42 * w, y + 0.72 * h), (x + 0.56 * w, y + 0.66 * h),
                  (x + 0.60 * w, y + 0.80 * h), (x + 0.46 * w, y + 0.86 * h)],
                 fill=(96, 100, 106))
    draw.arc([x + 0.44 * w, y + 0.62 * h, x + 0.60 * w, y + 0.82 * h],
             200, 340, fill=(60, 64, 70), width=4)
    # smoke puffs over the gap
    for sx, sy, r in [(0.47, 0.34, 9), (0.51, 0.28, 12), (0.55, 0.35, 8)]:
        draw.ellipse([x + sx * w - r, y + sy * h - r,
                      x + sx * w + r, y + sy * h + r], fill=(150, 150, 148))
    # small boat
    bx, by = x + 0.72 * w, y + 0.88 * h
    draw.polygon([(bx, by), (bx + 34, by), (bx + 28, by + 8), (bx + 6, by + 8)],
                 fill=(40, 44, 50))


def paint_quad(draw, x, y, w, h):
    """Manila at dusk: skyline, four flags, warm sun."""
    draw.rectangle([x, y, x + w, y + h], fill=(250, 214, 150))
    draw.ellipse([x + 0.70 * w, y + 0.08 * h, x + 0.70 * w + 30,
                  y + 0.08 * h + 30], fill=(238, 120, 60))
    # skyline silhouettes, back row lighter, front row darker
    for bx, bw, bh in [(0.00, 0.10, 0.42), (0.09, 0.07, 0.55),
                       (0.16, 0.09, 0.36), (0.25, 0.06, 0.50),
                       (0.31, 0.10, 0.40), (0.41, 0.08, 0.58),
                       (0.49, 0.07, 0.34), (0.56, 0.10, 0.46),
                       (0.66, 0.08, 0.38), (0.74, 0.09, 0.52),
                       (0.83, 0.08, 0.40), (0.91, 0.09, 0.48)]:
        draw.rectangle([x + bx * w, y + (1 - bh) * h, x + (bx + bw) * w,
                        y + h], fill=(120, 110, 120))
    # windows
    for wx in range(6):
        for wy in range(3):
            px = x + (0.03 + wx * 0.16) * w
            py = y + (0.62 + wy * 0.09) * h
            draw.rectangle([px, py, px + 5, py + 6], fill=(250, 214, 150))
    # four flag poles with schematic flags
    poles = [(0.10, "us"), (0.34, "jp"), (0.58, "in"), (0.82, "au")]
    for fx, kind in poles:
        px = x + fx * w
        py = y + 0.52 * h
        draw.rectangle([px, y + 0.16 * h, px + 3, py], fill=(60, 60, 60))
        fw, fh = 34, 22
        if kind == "us":
            for s in range(4):
                draw.rectangle([px + 3, y + 0.16 * h + s * 5.5,
                                px + 3 + fw, y + 0.16 * h + (s + 1) * 5.5],
                               fill=RED if s % 2 == 0 else (255, 255, 255))
            draw.rectangle([px + 3, y + 0.16 * h, px + 15,
                            y + 0.16 * h + 11], fill=NAVY)
        elif kind == "jp":
            draw.rectangle([px + 3, y + 0.16 * h, px + 3 + fw,
                            y + 0.16 * h + fh], fill=(255, 255, 255))
            draw.ellipse([px + 13, y + 0.16 * h + 5, px + 25,
                          y + 0.16 * h + 17], fill=RED)
        elif kind == "in":
            draw.rectangle([px + 3, y + 0.16 * h, px + 3 + fw,
                            y + 0.16 * h + 7], fill=(255, 153, 51))
            draw.rectangle([px + 3, y + 0.16 * h + 7, px + 3 + fw,
                            y + 0.16 * h + 15], fill=(255, 255, 255))
            draw.rectangle([px + 3, y + 0.16 * h + 15, px + 3 + fw,
                            y + 0.16 * h + 22], fill=(19, 136, 8))
            draw.ellipse([px + 14, y + 0.16 * h + 8, px + 22,
                          y + 0.16 * h + 16], fill=NAVY)
        else:  # australia: blue field, canton star, southern stars
            draw.rectangle([px + 3, y + 0.16 * h, px + 3 + fw,
                            y + 0.16 * h + fh], fill=(0, 40, 104))
            draw.ellipse([px + 7, y + 0.16 * h + 3, px + 12,
                          y + 0.16 * h + 8], fill=(255, 255, 255))
            for sx, sy in [(26, 6), (28, 15), (22, 12)]:
                draw.ellipse([px + sx, y + 0.16 * h + sy, px + sx + 3,
                              y + 0.16 * h + sy + 3], fill=(255, 255, 255))
    # birds
    for bx, by in [(0.24, 0.12), (0.46, 0.08), (0.64, 0.14)]:
        px, py = x + bx * w, y + by * h
        draw.arc([px - 6, py - 3, px, py + 3], 200, 340, fill=INK, width=2)
        draw.arc([px, py - 3, px + 6, py + 3], 200, 340, fill=INK, width=2)


# ---- middle-story icons (60x60, flat) -----------------------------------

def icon_chip(draw, x, y, s):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8,
                           fill=(14, 92, 54))
    draw.rectangle([x + 18, y + 20, x + 42, y + 40], fill=(255, 255, 255))
    draw.rectangle([x + 26, y + 27, x + 34, y + 33], fill=(14, 92, 54))
    for px in (22, 30, 38):
        draw.rectangle([x + px, y + 12, x + px + 2, y + 20],
                       fill=(255, 255, 255))
        draw.rectangle([x + px, y + 40, x + px + 2, y + 48],
                       fill=(255, 255, 255))
    draw.line([(x + 10, y + 46), (x + 24, y + 34), (x + 32, y + 38),
               (x + 50, y + 14)], fill=(120, 220, 130), width=3)
    draw.polygon([(x + 50, y + 14), (x + 42, y + 14), (x + 50, y + 22)],
                 fill=(120, 220, 130))


def icon_storm(draw, x, y, s):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=TEAL)
    for r in (18, 13, 8):
        draw.arc([x + 30 - r, y + 28 - r, x + 30 + r, y + 28 + r],
                 30, 300, fill=(255, 255, 255), width=3)
    for lx, ly in [(14, 46), (24, 50), (36, 48), (46, 44)]:
        draw.line([(x + lx, y + ly), (x + lx - 3, y + ly + 7)],
                  fill=(180, 220, 220), width=2)


def icon_parliament(draw, x, y, s):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8,
                           fill=(88, 60, 128))
    draw.polygon([(x + 12, y + 24), (x + 30, y + 12), (x + 48, y + 24)],
                 fill=(255, 255, 255))
    draw.rectangle([x + 12, y + 24, x + 48, y + 28], fill=(255, 255, 255))
    for cx in (16, 24, 32, 40):
        draw.rectangle([x + cx, y + 30, x + cx + 4, y + 44],
                       fill=(255, 255, 255))
    draw.rectangle([x + 12, y + 44, x + 48, y + 48], fill=(255, 255, 255))


def icon_euro(draw, x, y, s):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=NAVY)
    f = serif(30, bold=True)
    draw.text((x + 15, y + 12), "\u20ac", font=f, fill=GOLD)
    for k in range(8):
        import math
        a = math.radians(k * 45)
        sx = x + 30 + 20 * math.cos(a)
        sy = y + 30 + 20 * math.sin(a)
        draw.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=GOLD)


def icon_market(draw, x, y, s):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8,
                           fill=(122, 28, 28))
    draw.line([(x + 10, y + 16), (x + 24, y + 26), (x + 32, y + 22),
               (x + 50, y + 44)], fill=(255, 255, 255), width=3)
    draw.polygon([(x + 50, y + 44), (x + 50, y + 34), (x + 40, y + 44)],
                 fill=(255, 200, 90))


def icon_summit(draw, x, y, s):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8,
                           fill=(24, 84, 150))
    draw.ellipse([x + 12, y + 10, x + 48, y + 46], outline=(255, 255, 255),
                 width=2)
    draw.ellipse([x + 22, y + 10, x + 38, y + 46], outline=(255, 255, 255),
                 width=2)
    draw.line([(x + 12, y + 28), (x + 48, y + 28)], fill=(255, 255, 255),
              width=2)
    draw.line([(x + 30, y + 10), (x + 30, y + 46)], fill=(255, 255, 255),
              width=2)
    for bx, bh in [(14, 8), (24, 13), (34, 10), (44, 15)]:
        draw.rectangle([x + bx, y + 50 - bh, x + bx + 5, y + 50],
                       fill=GOLD)


# ---- story data (all facts verified from 18 Nov 2026 reporting) ---------

LEADS = [
    {
        "num": 1, "kicker": "MIDDLE EAST \u00b7 CONFLICT",
        "caption": "SHEIKH ISA BASE \u00b7 QESHM ISLAND",
        "headline": "US jets hit Iran after drones target Bahrain",
        "deck": "Guard drones hit the US radar at Sheikh Isa base; US jets "
                "answered by striking a missile site on Qeshm Island. "
                "Bahrain says it shot the drones down.",
        "paint": paint_gulf,
    },
    {
        "num": 2, "kicker": "EUROPE \u00b7 WAR IN UKRAINE",
        "caption": "KERCH STRAIT \u00b7 19-KM CROSSING",
        "headline": "A span of the Kerch bridge falls into the sea",
        "deck": "Kyiv says strikes on two days in a row brought down the "
                "road arch; the rail arch stands, damaged. Russia hit "
                "Kyiv's bridges in reply.",
        "paint": paint_bridge,
    },
    {
        "num": 3, "kicker": "ASIA \u00b7 DIPLOMACY",
        "caption": "MANILA \u00b7 FIRST QUAD IN TWO YEARS",
        "headline": "Trump meets the Quad, then flies to Shenzhen",
        "deck": "First Quad summit in two years brings the US, India, "
                "Japan and Australia together. A first trilateral with "
                "Xi and Putin is set for Thursday.",
        "paint": paint_quad,
    },
]

MIDDLES = [
    {
        "num": 4, "kicker": "UNITED STATES \u00b7 BUSINESS",
        "headline": "Nvidia's revenue doubles to $115.8bn",
        "deck": "Data-centre sales hit $107.6bn, up 110%. First results "
                "since Huang resigned; Kress guides to $130bn next quarter.",
        "icon": icon_chip,
    },
    {
        "num": 5, "kicker": "SOUTH ASIA \u00b7 WEATHER",
        "headline": "Cyclone Akvan bears down on Andhra Pradesh",
        "deck": "Landfall is forecast for Friday, with gusts to 145 km/h. "
                "Odisha has marked 204,070 people to move from the coast.",
        "icon": icon_storm,
    },
    {
        "num": 6, "kicker": "ISRAEL \u00b7 POLITICS",
        "headline": "Knesset elects Kahana as speaker, 66\u201352",
        "deck": "Kahana, an ally of Gadi Eisenkot, replaces Amir Ohana "
                "after a seven-hour debate. Arab votes proved decisive.",
        "icon": icon_parliament,
    },
    {
        "num": 7, "kicker": "EUROPE \u00b7 UKRAINE",
        "headline": "EU proposes a \u20ac45bn loan for Ukraine",
        "deck": "The loan would cover about two-thirds of Kyiv's \u20ac70bn "
                "2027 gap and be repaid only if Russia pays reparations.",
        "icon": icon_euro,
    },
    {
        "num": 8, "kicker": "UNITED STATES \u00b7 MARKETS",
        "headline": "Wall Street slides; Dow drops 849 points",
        "deck": "The S&P 500 closed at its lowest since July in a fourth "
                "straight fall. Reports of an NSA outage weighed on shares.",
        "icon": icon_market,
    },
    {
        "num": 9, "kicker": "CHINA \u00b7 SUMMIT",
        "headline": "APEC opens in Shenzhen with Xi keynote",
        "deck": "Leaders of 21 Pacific economies meet today and tomorrow. "
                "Trump and South Korea's Lee arrive for the sessions.",
        "icon": icon_summit,
    },
]

NUMBERS = [
    ("66\u201352", "Kahana's margin for speaker"),
    ("$115.8bn", "Nvidia revenue, up 103%"),
    ("145 km/h", "Akvan's forecast gusts"),
    ("204,070", "People Odisha will move"),
]

# 26 short items, numbered 10-35. Lead in bold, detail in regular.
ALSO = [
    ("Settler sanctions", "Australia lists 7, UK 8 firms"),
    ("Gaza warning", "Board of Peace fears truce fails"),
    ("Siberia crash", "An-12 down; all 19 aboard killed"),
    ("Voyager 1", "First craft one light-day from Earth"),
    ("Anthropic IPO", "Priced today; ANT trades Thursday"),
    ("Measles status lost", "US loses it after 26 years"),
    ("Telegram blocked", "Jordan and Iraq block the app"),
    ("China\u2013Canada deal", "Tariff cuts on pork, seafood"),
    ("Dhoni retires", "Ends 19-year IPL career"),
    ("Tokyo scrambles jets", "Two planes suspected"),
    ("NSA network down", "No hack seen"),
    ("Apple outage", "Update hits iCloud, App Store, Pay"),
    ("Tech bets slashed", "Biggest cut since 2006"),
    ("Amazon's $7bn plan", "Indian renewables by 2030"),
    ("Senegal qualify", "First team into AFCON 2027"),
    ("Estonia border", "To shut Russia border on 1 Dec"),
    ("Sudan drone toll", "UN: drones killed 1,630 civilians"),
    ("Rodr\u00edguez shot dead", "First in 25 years"),
    ("Fishermen sue US", "16 sue over drone strike"),
    ("Guinea crackdown", "224 jailed over illegal mining"),
    ("AI bubble", "Baidu chief warns ahead of APEC"),
    ("Taiwan flights", "US presses UN agency"),
    ("ASX falls", "Steepest drop in six weeks"),
    ("Black Sea strike", "Gas Husky hit; 19 crew rescued"),
    ("Hormuz mines", "Tankers hit; third in 24 hours"),
    ("Romania quake", "5.3 magnitude strikes"),
]


# ---- page assembly ------------------------------------------------------

def paint_masthead(draw):
    draw.rectangle([0, 0, PAGE, 118], fill=NAVY)
    kf = sans(13, bold=True)
    draw.text((MARGIN, 15), "THE DAY IN WORLD NEWS", font=kf, fill=GOLD)
    right = "35 STORIES \u00b7 6 CONTINENTS \u00b7 ONE PAGE"
    draw.text((PAGE - MARGIN - draw.textlength(right, font=kf), 15), right,
              font=kf, fill=GOLD)
    draw.text((MARGIN, 36), "Wednesday 18 November 2026",
              font=serif(52, bold=True), fill=(255, 255, 255))
    draw.text((MARGIN, 96),
              "Every story on this page happened, or was first reported, "
              "on this day.",
              font=serif(15, italic=True), fill=GOLD_SOFT)
    draw.rectangle([0, 118, PAGE, 122], fill=GOLD)


def paint_lead(draw, x, y, w, story):
    draw.rectangle([x, y, x + w, y + 146], fill=NAVY_DEEP)
    story["paint"](draw, x, y, w, 146)
    # caption strip at the foot of the picture
    draw.rectangle([x, y + 124, x + w, y + 146], fill=TEAL)
    draw.text((x + 8, y + 130), story["caption"], font=sans(11, bold=True),
              fill=(255, 255, 255))
    # badge + kicker
    badge(draw, x + 10, y + 166, story["num"], radius=10)
    draw.text((x + 26, y + 158), story["kicker"], font=sans(12, bold=True),
              fill=RED)
    # headline, two lines
    _, hlines = text_block(draw, x, y + 182, story["headline"],
                           serif(24, bold=True), INK, w, 30, max_lines=2)
    dy = y + 182 + len(hlines) * 30 + 6
    text_block(draw, x, dy, story["deck"], sans(12), (52, 52, 48), w, 15,
               max_lines=3)


def paint_middle(draw, x, y, w, story):
    story["icon"](draw, x, y + 4, 60)
    tx = x + 72
    tw = w - 72
    badge(draw, tx + 8, y + 8, story["num"], radius=8)
    draw.text((tx + 22, y + 1), story["kicker"], font=sans(11, bold=True),
              fill=RED)
    _, hlines = text_block(draw, tx, y + 20, story["headline"],
                           serif(17, bold=True), INK, tw, 21, max_lines=2)
    text_block(draw, tx, y + 64, story["deck"], sans(12), (52, 52, 48), tw,
               14, max_lines=3)


def paint_numbers(draw):
    draw.line([(MARGIN, 692), (PAGE - MARGIN, 692)], fill=RULE, width=1)
    draw.text((MARGIN, 706), "BY THE", font=sans(12, bold=True), fill=RED)
    draw.text((MARGIN, 722), "NUMBERS", font=sans(12, bold=True), fill=RED)
    col_x, col_w = 190, 200
    for i, (big, small) in enumerate(NUMBERS):
        cx = col_x + i * col_w
        if i:
            draw.line([(cx - 12, 700), (cx - 12, 742)], fill=RULE, width=1)
        draw.text((cx, 700), big, font=serif(28, bold=True), fill=NAVY)
        draw.text((cx, 732), small, font=sans(11), fill=GREY)
    draw.line([(MARGIN, 750), (PAGE - MARGIN, 750)], fill=RULE, width=1)


def paint_bottom(draw):
    # --- map, left ---
    draw.text((MARGIN, 764), "WHERE THE NEWS HAPPENED",
              font=sans(13, bold=True), fill=NAVY)
    paint_map(draw, MARGIN + 6, 788, 300, 176)
    draw.text((MARGIN, 968), "Numbered dots mark stories 1\u20139.",
              font=serif(11, italic=True), fill=GREY)
    # --- ALSO list, right ---
    ax = 346
    draw.text((ax, 764), "ALSO ON WEDNESDAY 18 NOVEMBER \u2014 26 MORE STORIES",
              font=sans(13, bold=True), fill=NAVY)
    draw.rectangle([ax, 784, PAGE - MARGIN, 786], fill=RED)
    col_w = 322
    lead_f = sans(11, bold=True)
    body_f = sans(11)
    for i, (lead, detail) in enumerate(ALSO):
        col = 0 if i < 13 else 1
        row = i % 13
        x = ax + col * (col_w + 12)
        y = 794 + row * 15
        num = f"{10 + i}. "
        draw.text((x, y), num, font=lead_f, fill=RED)
        nx = x + draw.textlength(num, font=lead_f)
        draw.text((nx, y), lead, font=lead_f, fill=INK)
        lx = nx + draw.textlength(lead, font=lead_f)
        draw.text((lx, y), f" \u2014 {detail}", font=body_f, fill=(52, 52, 48))


def build_page():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)
    paint_masthead(draw)
    cols = [MARGIN, MARGIN + 329, MARGIN + 658]
    for x, story in zip(cols, LEADS):
        paint_lead(draw, x, 132, 318, story)
    draw.line([(MARGIN, 440), (PAGE - MARGIN, 440)], fill=RULE, width=1)
    for r in range(2):
        for c in range(3):
            story = MIDDLES[r * 3 + c]
            paint_middle(draw, cols[c], 460 + r * 114, 318, story)
    paint_numbers(draw)
    paint_bottom(draw)
    # footer
    draw.text((MARGIN, 992),
              "All stories on this page happened, or were first reported, "
              "on Wednesday 18 November 2026. Disputed claims are "
              "attributed to their source.",
              font=sans(10), fill=GREY)
    draw.text((MARGIN, 1006),
              "Sources: Reuters, AP, Al Jazeera, BBC, CNN, IMD, NASA, UN. "
              "All drawings are original flat-vector art made for this page.",
              font=sans(10), fill=GREY)
    # thin frame
    draw.rectangle([4, 4, PAGE - 5, PAGE - 5], outline=(186, 158, 74), width=2)
    return img


def check_widths():
    """Warn about any ALSO line wider than its column (would wrap)."""
    probe = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(probe)
    lead_f, body_f = sans(11, bold=True), sans(11)
    for i, (lead, detail) in enumerate(ALSO):
        total = (d.textlength(f"{10 + i}. ", font=lead_f)
                 + d.textlength(lead, font=lead_f)
                 + d.textlength(f" \u2014 {detail}", font=body_f))
        if total > 322:
            print(f"WARN also {10 + i} too wide: {total:.0f}px")


if __name__ == "__main__":
    check_widths()
    page = build_page()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    page.save(out)
    print("wrote", out, page.size, "stories:", 3 + 6 + len(ALSO))
