#!/usr/bin/env python3
"""Paint the v2 front page for news-image-20261121.

A newspaper front page summing up Saturday 21 November 2026, drawn
from scratch with Pillow: 35 stories across 7 regions, three hero
stories, a ten-cell grid, a world map built from the Natural Earth
110m land outline bundled in assets/, and 22 short briefs.

Every word sits on solid cream or white. Nothing is drawn over an
illustration, a gradient or the map. Any headline, deck or brief that
does not fit its box raises an error and the script exits non-zero.

Run:  python3 paint_front_v2.py   (writes entry.png beside this file)
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
GEOJSON = HERE / "assets" / "ne_110m_land.geojson"
OUT = HERE / "entry.png"

W = H = 1024
MARGIN = 16
LEFT = MARGIN
RIGHT = W - MARGIN
CW = RIGHT - LEFT  # 992 usable width

PAPER = (246, 241, 227)   # cream
WHITE = (255, 255, 255)
NAVY = (20, 36, 62)       # ink
BODY = (31, 42, 58)
RED = (176, 30, 36)       # banner red
TEAL = (46, 125, 122)
DARKNAVY = (22, 50, 79)   # map ocean
TAN = (216, 196, 154)     # map land
TAN_LINE = (138, 122, 82)
GREY = (90, 96, 104)

FONT_DIR = Path("/usr/share/fonts/truetype")


def pick_font(names, size):
    """First existing font file from names, else DejaVu Sans."""
    for name in names:
        path = FONT_DIR / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.truetype(str(FONT_DIR / "dejavu/DejaVuSans.ttf"), size)


def sans(size, bold=False):
    if bold:
        return pick_font(["dejavu/DejaVuSans-Bold.ttf"], size)
    return pick_font(["dejavu/DejaVuSans.ttf"], size)


def serif(size, bold=False):
    if bold:
        return pick_font(["noto/NotoSerif-Bold.ttf",
                          "dejavu/DejaVuSerif-Bold.ttf"], size)
    return pick_font(["noto/NotoSerif-Regular.ttf",
                      "dejavu/DejaVuSerif.ttf"], size)


def serif_italic(size):
    return pick_font(["noto/NotoSerif-Italic.ttf",
                      "dejavu/DejaVuSerif.ttf"], size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines, each <= max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, font, fill, lh, align="left", box_w=None):
    """Draw lines starting at (x, y); returns the y just past the last."""
    for line in lines:
        lx = x
        if align == "center" and box_w is not None:
            lx = x + (box_w - text_w(draw, line, font)) / 2
        elif align == "right" and box_w is not None:
            lx = x + box_w - text_w(draw, line, font)
        draw.text((lx, y), line, font=font, fill=fill)
        y += lh
    return y


def fit_or_die(draw, text, font, max_w, max_lines, what):
    """Wrap text and fail loudly if it needs more than max_lines."""
    lines = wrap(draw, text, font, max_w)
    if len(lines) > max_lines:
        raise SystemExit(
            "OVERFLOW in %s: %d lines for %r (max %d)"
            % (what, len(lines), text, max_lines))
    return lines


# ---------------------------------------------------------------- content

TOP_LEFT = "THE WORLD IN ONE DAY"
TOP_RIGHT = "35 STORIES · 7 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
MASTHEAD = "Saturday 21 November 2026"
STANDFIRST = ("Climate summit runs past its deadline · Five missiles shot "
              "down over Saudi Arabia · Strong quake shakes Peru")

NUMBERS = [
    ("13", "Day of a COP31 summit planned to close on day 12"),
    ("5", "missiles shot down over Riyadh and Jizan"),
    ("6.7", "magnitude of the quake in Junín, Peru"),
    ("146", "people safe after a jet's emergency landing"),
    ("$58,983", "bitcoin early Saturday, down 3.9% in a day"),
    ("124*", "K L Rahul's score at tea in Wellington"),
]

# (label, count, colour) -- counts sum to 35 stories.
REGIONS = [
    ("Europe", 4, (46, 95, 138)),
    ("Asia", 9, (176, 30, 36)),
    ("Middle East", 5, (192, 122, 26)),
    ("Africa", 1, (74, 122, 58)),
    ("Americas", 11, (20, 36, 62)),
    ("Oceania", 3, (46, 138, 122)),
    ("Global", 2, (106, 90, 138)),
]

HEROES = [
    dict(banner="COP31: OVERTIME", chip="No deal · day 13",
         kicker="ANTALYA, TÜRKIYE · CLIMATE",
         head="Climate summit runs into Saturday with no deal",
         deck=("COP31 missed its Friday close. A draft with no mention of "
               "fossil fuels splits nearly 200 countries; a third text is "
               "promised. (AFP, Al Jazeera)"),
         art="cop31"),
    dict(banner="SAUDI: MISSILES", chip="5 shot down",
         kicker="RIYADH · JIZAN · WAR",
         head="Five Houthi missiles shot down over Saudi Arabia",
         deck=("The coalition said three were destroyed over Riyadh before "
               "dawn and two over Jizan on Friday evening, after it struck "
               "Hodeidah port. (AFP, Dawn)"),
         art="riyadh"),
    dict(banner="PERU: QUAKE 6.7", chip="00:09 UTC · 108 km deep",
         kicker="JUNÍN, PERU · EARTHQUAKE",
         head="Magnitude 6.7 earthquake shakes central Peru",
         deck=("The deep quake near Carhuamayo was felt in Lima and along "
               "the coast. Peru's institute reported no deaths and no "
               "tsunami risk. (USGS, IGP)"),
         art="quake"),
]

GRID = [
    dict(banner="KYIV: WARNING", kicker="KYIV · WAR",
         head="Zelensky: Crimea bridge 'will not stay'",
         deck="He warns of more double-tap strikes.", art="bridge"),
    dict(banner="HORMUZ: DRONE", kicker="STRAIT OF HORMUZ · WAR",
         head="Iran says it shot down a US drone",
         deck="No confirmation from Washington.", art="drone"),
    dict(banner="IRAN: URANIUM", kicker="TEHRAN · DIPLOMACY",
         head="Iran: uranium stock stays in the country",
         deck="Minister still seeks a “fair solution”.", art="atom"),
    dict(banner="TRUMP: AI TAX", kicker="WASHINGTON · TECHNOLOGY",
         head="Trump vows tax on data centres abroad",
         deck="“Tremendous” penalty; no details yet.", art="servers"),
    dict(banner="CHINA–JAPAN", kicker="BEIJING · DIPLOMACY",
         head="China warns Japan over Taiwan",
         deck="Beijing: “correct” its Taiwan words.", art="flags"),
    dict(banner="DAVAO: 146 SAFE", kicker="DAVAO · AVIATION",
         head="Jet lands safely after engine fire alert",
         deck="Air Niugini 767 diverts after midnight.", art="plane"),
    dict(banner="CANBERRA: AI", kicker="CANBERRA · DIPLOMACY",
         head="Australia and China agree to AI talks",
         deck="Albanese ends an 11-day trip.", art="chip"),
    dict(banner="BITCOIN: $58,983", kicker="WORLD · MARKETS",
         head="Bitcoin trades below $59,000 on Saturday",
         deck="Down 3.9% in 24 hours; ether $1,625.", art="coin"),
    dict(banner="RUSSELL: P1", kicker="LAS VEGAS · FORMULA ONE",
         head="Russell fastest in Las Vegas practice",
         deck="1:34.041 in a messy final session.", art="flag"),
    dict(banner="RAHUL: 124*", kicker="WELLINGTON · CRICKET",
         head="Rahul hits a century against New Zealand",
         deck="India 344 for 2 at tea, replying to 368.", art="bat"),
]

# (number, place, text, source) -- briefs 14..35.
BRIEFS = [
    (14, "Kryvyi Rih", "Double strike kills 2, injures 42", "Kyiv Indep."),
    (15, "Copenhagen", "Russian attaché expelled over a plot", "Al Jazeera"),
    (16, "Antalya", "EU warns COP31 risks a “fossil summit”", "AFP"),
    (17, "Antalya", "Panama threatens to block climate text", "Al Jazeera"),
    (18, "Antalya", "Indonesia's PLN signs clean-power deals", "Antara"),
    (19, "Yemen", "Houthis threaten Jeddah and Red Sea ports", "Al Jazeera"),
    (20, "Washington", "Vance: Iran strikes were Trump's decision", "Reuters"),
    (21, "Washington", "Lawmaker threatens SpaceX's funding", "CNN"),
    (22, "Texas", "Execution of a man of 70 takes 63 minutes", "ABC"),
    (23, "Los Angeles", "Jury convicts man of starting Palisades fire", "ABC"),
    (24, "Missouri", "Judge approves $7.25bn Roundup settlement", "AFP"),
    (25, "Vancouver", "Canada rests defence in youth climate trial", "AFP"),
    (26, "Pyongyang", "Kim tours factories after no Trump meeting", "AFP"),
    (27, "Mercury", "BepiColombo due in Mercury orbit tonight", "ESA"),
    (28, "Taipei", "Budget and cash payout are passed", "Taipei Times"),
    (29, "Bangkok", "Six-point plan on arsenic in two rivers", "The Nation"),
    (30, "New Delhi", "Pakistani minister joins SCO forum in India", "Dawn"),
    (31, "Eastern India", "Rain alerts as Akvan's remnants move inland", "ETV"),
    (32, "Myanmar", "Rights groups urge sanctions after court ruling", "AP"),
    (33, "Port Louis", "African rating agency talks to 15 states", "Al Jazeera"),
    (34, "Melbourne", "Cummins keeps the Australian captaincy", "ABC"),
    (35, "Las Vegas", "Verstappen sent to stewards after contact", "Autosport"),
]

DATE_CHECK = (
    "Left out as Friday 20 November's news: Wall Street's fall into a "
    "correction, the Russian barrage that hit Kyiv's bridges, the Russian "
    "missiles that landed in Poland, the UK–EU deal and Cyclone Akvan's "
    "landfall. Older still: Voyager 1's light-day (18 Nov). Not confirmed "
    "when drawn, so not shown: a final COP31 text.")

FOOTER_1 = ("Every story here happened, or was first reported, on Saturday "
            "21 November 2026. Officials' counts and claims are attributed.")
FOOTER_2 = "Sources named beside each story · original drawings"

MAP_NOTE = ("Each number is the story with that number on this page. "
            "11 · Bitcoin trades everywhere, so it has no pin.")

# Story number -> (lon, lat) of the place it happened. 11 (Bitcoin) is
# global and has no pin; 2 covers Riyadh (the Jizan intercepts are the
# same story). Small nudges keep the dense Europe / Gulf pins apart.
PINS = {
    1: (30.7, 36.9, -4, 2),     # Antalya
    2: (46.7, 24.6, -6, 5),     # Riyadh
    3: (-76.0, -10.9, 0, 0),    # Carhuamayo, Junín
    4: (30.5, 50.45, -6, -3),   # Kyiv
    5: (56.5, 27.1, 9, 7),      # Strait of Hormuz
    6: (51.4, 35.7, 3, -3),     # Tehran
    7: (-77.0, 38.9, 0, 0),     # Washington
    8: (116.4, 39.9, 0, 0),     # Beijing
    9: (125.6, 7.1, 0, 0),      # Davao
    10: (149.1, -35.3, 0, 0),   # Canberra
    12: (-115.1, 36.2, 0, 0),   # Las Vegas
    13: (174.8, -41.3, -6, -2),  # Wellington
}

# ---------------------------------------------------------------- artwork
# All pictures are flat original drawings made of rectangles, circles,
# arcs and polygons. No text ever goes inside a picture box.

def _star_burst(d, cx, cy, r, colour, rays=12):
    import math
    for i in range(rays):
        a = math.pi * 2 * i / rays
        d.line([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))],
               fill=colour, width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=colour)


def draw_cop31(d, x, y, w, h):
    """A red thermometer over a teal hall, flags along the bottom."""
    d.rectangle([x, y, x + w, y + h], fill=TEAL)
    # sun, top right
    sx, sy = x + w - 26, y + 18
    d.ellipse([sx - 11, sy - 11, sx + 11, sy + 11], fill=(240, 200, 60))
    for a in range(0, 360, 45):
        import math
        r1, r2 = 14, 20
        d.line([(sx + r1 * math.cos(math.radians(a)),
                 sy + r1 * math.sin(math.radians(a))),
                (sx + r2 * math.cos(math.radians(a)),
                 sy + r2 * math.sin(math.radians(a)))],
               fill=(240, 200, 60), width=2)
    # thermometer tube, centred
    tx = x + w // 2 - 13
    d.rounded_rectangle([tx, y + 6, tx + 26, y + h - 30],
                        radius=13, fill=WHITE, outline=(200, 210, 205))
    d.rounded_rectangle([tx + 5, y + 12, tx + 21, y + h - 36],
                        radius=8, fill=(232, 236, 238))
    fill_top = y + 12 + int((h - 48) * 0.20)  # mercury to ~80%
    d.rounded_rectangle([tx + 5, fill_top, tx + 21, y + h - 36],
                        radius=8, fill=RED)
    d.ellipse([tx - 2, y + h - 38, tx + 28, y + h - 16], fill=RED)
    d.ellipse([tx - 2, y + h - 38, tx + 28, y + h - 16],
              outline=(140, 20, 24), width=2)
    for i in range(5):  # white ticks on the tube
        ty = y + 14 + i * 8
        d.line([(tx + 21, ty), (tx + 28, ty)], fill=WHITE, width=2)
    # four small flags, two at each bottom corner, clear of the bulb
    cols = [RED, (46, 95, 138), (74, 122, 58), (240, 200, 60)]
    flag_x = [x + 12, x + 36, x + w - 54, x + w - 30]
    for fx, c in zip(flag_x, cols):
        d.line([(fx, y + h - 26), (fx, y + h - 8)], fill=WHITE, width=2)
        d.polygon([(fx, y + h - 26), (fx + 18, y + h - 22),
                   (fx, y + h - 18)], fill=c)


def draw_riyadh(d, x, y, w, h):
    """Night sky, three interceptor trails ending in bursts over a city."""
    d.rectangle([x, y, x + w, y + h], fill=(22, 35, 61))
    import random
    rnd = random.Random(21)
    for _ in range(26):
        px, py = x + rnd.randint(4, w - 4), y + rnd.randint(4, h - 30)
        d.ellipse([px, py, px + 1, py + 1], fill=WHITE)
    # crescent moon, top right
    mx, my = x + w - 30, y + 16
    d.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=(245, 222, 130))
    d.ellipse([mx - 5, my - 12, mx + 14, my + 10], fill=(22, 35, 61))
    # city skyline along the bottom
    base = y + h
    heights = [26, 40, 22, 34, 46, 28, 38, 24]
    bw = w // len(heights)
    for i, bh in enumerate(heights):
        bx = x + i * bw
        d.rectangle([bx + 1, base - bh, bx + bw - 1, base],
                    fill=(10, 18, 34))
        for wy in range(base - bh + 5, base - 4, 9):
            for wx in (bx + 5, bx + bw - 8):
                d.rectangle([wx, wy, wx + 2, wy + 3], fill=(240, 200, 90))
    # three steep interceptor trails, each ending in a bright burst
    bursts = [(x + 52, y + 16), (x + w // 2 + 8, y + 10),
              (x + w - 58, y + 20)]
    for bx, by in bursts:
        d.arc([bx - 46, by - 8, bx + 46, by + 52], start=210, end=330,
              fill=(255, 150, 40), width=3)
        d.arc([bx - 30, by - 2, bx + 30, by + 40], start=210, end=330,
              fill=(255, 220, 120), width=2)
        _star_burst(d, bx, by, 11, (255, 240, 160))
        d.ellipse([bx - 14, by - 14, bx + 14, by + 14],
                  outline=(255, 200, 90), width=1)


def draw_quake(d, x, y, w, h):
    """Andes ridges, a seismograph trace and a cracked street."""
    d.rectangle([x, y, x + w, y + h], fill=(207, 227, 238))
    # mountain ridge
    d.polygon([(x, y + h - 34), (x + 60, y + 10), (x + 120, y + h - 34)],
              fill=(122, 96, 70))
    d.polygon([(x + 100, y + h - 34), (x + 190, y + 2), (x + 280, y + h - 34)],
              fill=(96, 74, 52))
    d.polygon([(x + 52, y + 18), (x + 60, y + 10), (x + 68, y + 18)],
              fill=WHITE)
    d.polygon([(x + 182, y + 12), (x + 190, y + 2), (x + 198, y + 12)],
              fill=WHITE)
    # ground band with a zigzag crack
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(138, 111, 77))
    d.line([(x + 8, y + h - 30), (x + 90, y + h - 12),
            (x + 150, y + h - 26), (x + 220, y + h - 8),
            (x + w - 8, y + h - 20)], fill=(40, 26, 16), width=3)
    # small houses on the ground
    for hx, hw in ((x + 20, 26), (x + 250, 30)):
        d.rectangle([hx, y + h - 52, hx + hw, y + h - 34],
                    fill=(240, 230, 205), outline=(90, 70, 50))
        d.polygon([(hx - 3, y + h - 52), (hx + hw // 2, y + h - 62),
                   (hx + hw + 3, y + h - 52)], fill=RED)
    # seismograph trace across the sky
    pts = [(x + 10, y + 44), (x + 40, y + 44), (x + 55, y + 30),
           (x + 70, y + 58), (x + 85, y + 40), (x + 100, y + 48),
           (x + 130, y + 48), (x + 145, y + 24), (x + 160, y + 62),
           (x + 175, y + 44), (x + 210, y + 44), (x + 225, y + 34),
           (x + 240, y + 52), (x + 260, y + 46), (x + w - 10, y + 46)]
    d.line(pts, fill=RED, width=2, joint="curve")


ART = {"cop31": draw_cop31, "riyadh": draw_riyadh, "quake": draw_quake}


def draw_grid_icon(d, kind, x, y, w, h):
    """One bold pictogram per grid cell, drawn on its own tinted strip."""
    tints = {"bridge": (38, 62, 110), "drone": (46, 110, 110),
             "atom": (96, 84, 120), "servers": (30, 48, 80),
             "flags": (150, 40, 44), "plane": (90, 140, 190),
             "chip": (52, 110, 70), "coin": (200, 130, 30),
             "flag": (24, 24, 28), "bat": (52, 110, 70)}
    d.rectangle([x, y, x + w, y + h], fill=tints[kind])
    cx, cy = x + w // 2, y + h // 2
    if kind == "bridge":
        d.arc([cx - 26, cy - 14, cx + 26, cy + 16], start=180, end=360,
              fill=(240, 200, 60), width=3)
        d.line([(cx - 26, cy + 8), (cx + 26, cy + 8)],
               fill=(240, 200, 60), width=3)
        d.line([(cx, cy - 14), (cx, cy - 24)], fill=(240, 200, 60), width=2)
    elif kind == "drone":
        d.ellipse([cx - 9, cy - 5, cx + 9, cy + 5], fill=WHITE)
        for dx in (-20, 20):
            d.line([(cx + dx - 11, cy - 8), (cx + dx + 11, cy - 8)],
                   fill=WHITE, width=3)
            d.line([(cx, cy - 2), (cx + dx, cy - 8)], fill=WHITE, width=2)
        d.ellipse([cx - 2, cy + 6, cx + 2, cy + 9], fill=WHITE)
    elif kind == "atom":
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 220, 120))
        for ang in (0, 60, 120):
            d.arc([cx - 17, cy - 8, cx + 17, cy + 8], start=ang,
                  end=ang + 300, fill=WHITE, width=2)
    elif kind == "servers":
        for i, sy in enumerate((cy - 8, cy - 1, cy + 6)):
            d.rectangle([cx - 14, sy, cx + 14, sy + 5],
                        outline=WHITE, width=1)
            d.ellipse([cx - 11, sy + 2, cx - 9, sy + 4], fill=(120, 200, 255))
    elif kind == "flags":
        d.rectangle([cx - 22, cy - 7, cx - 4, cy + 7], fill=WHITE)
        d.ellipse([cx - 17, cy - 4, cx - 9, cy + 4], fill=RED)
        d.rectangle([cx + 4, cy - 7, cx + 22, cy + 7], fill=(200, 40, 40))
        d.ellipse([cx + 9, cy - 4, cx + 17, cy + 4], fill=WHITE)
    elif kind == "plane":
        d.polygon([(cx - 18, cy), (cx + 14, cy - 4), (cx + 20, cy),
                   (cx + 14, cy + 4)], fill=WHITE)
        d.polygon([(cx - 2, cy - 8), (cx + 2, cy - 8), (cx + 4, cy),
                   (cx - 4, cy)], fill=WHITE)
    elif kind == "chip":
        d.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=WHITE)
        d.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=(52, 110, 70))
        for px in (-8, -3, 2, 7):
            d.line([(cx + px, cy - 11), (cx + px, cy - 8)], fill=WHITE, width=2)
            d.line([(cx + px, cy + 8), (cx + px, cy + 11)], fill=WHITE, width=2)
    elif kind == "coin":
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=WHITE)
        d.text((cx - 4, cy - 8), "B", font=sans(13, True),
               fill=(200, 130, 30))
    elif kind == "flag":
        for r in range(2):
            for c in range(4):
                if (r + c) % 2 == 0:
                    d.rectangle([cx - 16 + c * 8, cy - 8 + r * 8,
                                 cx - 9 + c * 8, cy - 1 + r * 8],
                                fill=WHITE)
        d.line([(cx - 20, cy - 8), (cx - 20, cy + 9)], fill=WHITE, width=2)
    elif kind == "bat":
        d.line([(cx - 12, cy + 8), (cx + 6, cy - 8)], fill=(240, 220, 180),
               width=5)
        d.ellipse([cx + 8, cy - 10, cx + 16, cy - 2], fill=RED)


# ---------------------------------------------------------------- map

def load_land():
    with open(GEOJSON, encoding="utf-8") as fh:
        data = json.load(fh)
    polys = []
    for feat in data["features"]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            polys.extend(geom["coordinates"])
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                polys.append(poly)
    return polys


def project(lon, lat, fw, fh):
    """Equirectangular: lon -180..180 across, lat 84..-60 down."""
    px = (lon + 180.0) / 360.0 * fw
    py = (84.0 - lat) / 144.0 * fh
    return px, py


def paint_map(fw, fh):
    """Dark navy ocean, beige land from the bundled Natural Earth file."""
    img = Image.new("RGB", (fw, fh), DARKNAVY)
    d = ImageDraw.Draw(img)
    for ring in load_land():
        pts = [project(lon, lat, fw, fh) for lon, lat in ring]
        if len(pts) > 2:
            d.polygon(pts, fill=TAN, outline=TAN_LINE)
    return img

# ---------------------------------------------------------------- assembly

def paint():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top band ------------------------------------------------------
    d.rectangle([0, 0, W, 28], fill=RED)
    f_left = sans(15, True)
    d.text((LEFT, 6), TOP_LEFT, font=f_left, fill=WHITE)
    f_right = sans(12, True)
    draw_lines(d, [TOP_RIGHT], LEFT, 8, f_right, WHITE, 12,
               align="right", box_w=CW)

    # --- masthead + standfirst ----------------------------------------
    f_mast = serif(52, True)
    mw = text_w(d, MASTHEAD, f_mast)
    if mw > CW:
        raise SystemExit("OVERFLOW: masthead %d px wide" % mw)
    d.text(((W - mw) / 2, 32), MASTHEAD, font=f_mast, fill=NAVY)
    f_stand = None
    for size in (18, 17, 16):
        cand = serif_italic(size)
        if text_w(d, STANDFIRST, cand) <= CW:
            f_stand = cand
            break
    if f_stand is None:
        raise SystemExit("OVERFLOW: standfirst too wide at 16px")
    sw = text_w(d, STANDFIRST, f_stand)
    d.text(((W - sw) / 2, 88), STANDFIRST, font=f_stand, fill=NAVY)

    # --- numbers strip -------------------------------------------------
    ny0, ny1 = 112, 168
    gap = 8
    pw = (CW - gap * 5) // 6
    for i, (value, caption) in enumerate(NUMBERS):
        x0 = LEFT + i * (pw + gap)
        d.rectangle([x0, ny0, x0 + pw, ny1], fill=WHITE,
                    outline=(200, 192, 170))
        f_val = sans(20, True)
        vw = text_w(d, value, f_val)
        d.text((x0 + (pw - vw) / 2, ny0 + 4), value, font=f_val, fill=RED)
        lines = fit_or_die(d, caption, sans(10), pw - 12, 2,
                           "numbers caption %d" % i)
        draw_lines(d, lines, x0 + 6, ny0 + 30, sans(10), NAVY, 11,
                   align="center", box_w=pw - 12)

    # --- region bar ----------------------------------------------------
    ry0, ry1 = 172, 196
    total = sum(c for _, c, _ in REGIONS)
    raw = [CW * c / total for _, c, _ in REGIONS]
    widths = [max(46, int(round(r))) for r in raw]
    widths[3] = max(widths[3], 58)  # Africa (1 story) still needs its label
    over = sum(widths) - CW
    if over > 0:  # trim the biggest segments back to fit, never Africa
        order = sorted((i for i in range(len(widths)) if i != 3),
                       key=lambda i: -widths[i])
        j = 0
        while over > 0:
            widths[order[j % len(order)]] -= 1
            over -= 1
            j += 1
    x = LEFT
    for (label, count, colour), seg_w in zip(REGIONS, widths):
        d.rectangle([x, ry0, x + seg_w, ry1], fill=colour)
        tag = "%s %d" % (label, count)
        f_tag = sans(10, True)
        if text_w(d, tag, f_tag) > seg_w - 4:
            f_tag = sans(9, True)
        tw = text_w(d, tag, f_tag)
        if tw <= seg_w - 4:
            d.text((x + (seg_w - tw) / 2, ry0 + 7), tag, font=f_tag,
                   fill=WHITE)
        x += seg_w

    # --- heroes --------------------------------------------------------
    hy0, hh = 200, 224
    hw, hgap = 320, 16
    for i, hero in enumerate(HEROES):
        x0 = LEFT + i * (hw + hgap)
        d.rectangle([x0, hy0, x0 + hw, hy0 + hh], fill=WHITE,
                    outline=(200, 192, 170))
        # red banner title
        d.rectangle([x0, hy0, x0 + hw, hy0 + 26], fill=RED)
        f_ban = sans(16, True)
        bw = text_w(d, hero["banner"], f_ban)
        d.text((x0 + (hw - bw) / 2, hy0 + 5), hero["banner"], font=f_ban,
               fill=WHITE)
        # white subtitle chip
        f_chip = sans(11, True)
        cw2 = text_w(d, hero["chip"], f_chip) + 22
        cx0 = x0 + (hw - cw2) / 2
        d.rounded_rectangle([cx0, hy0 + 29, cx0 + cw2, hy0 + 49],
                            radius=10, fill=WHITE, outline=RED, width=1)
        d.text((cx0 + 11, hy0 + 32), hero["chip"], font=f_chip, fill=RED)
        # illustration
        ART[hero["art"]](d, x0 + 8, hy0 + 52, hw - 16, 72)
        # kicker / headline / deck
        f_kick = sans(11, True)
        d.text((x0 + 10, hy0 + 127), hero["kicker"], font=f_kick, fill=RED)
        lines = fit_or_die(d, hero["head"], sans(19, True), hw - 20, 2,
                           "hero %d headline" % i)
        draw_lines(d, lines, x0 + 10, hy0 + 141, sans(19, True), NAVY, 20)
        lines = fit_or_die(d, hero["deck"], sans(11), hw - 20, 3,
                           "hero %d deck" % i)
        draw_lines(d, lines, x0 + 10, hy0 + 183, sans(11), BODY, 13)

    # --- grid ----------------------------------------------------------
    gy0, gh = 428, 104
    gw, ggap = 190, 10
    for i, cell in enumerate(GRID):
        row, col = divmod(i, 5)
        x0 = LEFT + col * (gw + ggap)
        y0 = gy0 + row * gh
        d.rectangle([x0, y0, x0 + gw, y0 + gh], fill=WHITE,
                    outline=(200, 192, 170))
        d.rectangle([x0, y0, x0 + gw, y0 + 18], fill=RED)
        f_gban = sans(10, True)
        bw = text_w(d, cell["banner"], f_gban)
        if bw > gw - 6:
            raise SystemExit("OVERFLOW: grid banner %r" % cell["banner"])
        d.text((x0 + (gw - bw) / 2, y0 + 4), cell["banner"], font=f_gban,
               fill=WHITE)
        draw_grid_icon(d, cell["art"], x0, y0 + 18, gw, 18)
        f_gkick = sans(10, True)
        d.text((x0 + 6, y0 + 38), cell["kicker"], font=f_gkick, fill=RED)
        lines = fit_or_die(d, cell["head"], sans(15, True), gw - 12, 2,
                           "grid %d headline" % i)
        draw_lines(d, lines, x0 + 6, y0 + 50, sans(15, True), NAVY, 15)
        lines = fit_or_die(d, cell["deck"], sans(11), gw - 12, 2,
                           "grid %d deck" % i)
        draw_lines(d, lines, x0 + 6, y0 + 81, sans(11), BODY, 11)

    # --- bottom band: map + date check (left), briefs (right) ----------
    by0 = 640
    # map panel
    f_sec = sans(13, True)
    d.text((LEFT, by0), "WHERE IT HAPPENED", font=f_sec, fill=RED)
    map_w, map_h = 400, 160
    map_img = paint_map(map_w, map_h)
    img.paste(map_img, (LEFT, by0 + 14))
    d.rectangle([LEFT, by0 + 14, LEFT + map_w, by0 + 14 + map_h],
                outline=NAVY, width=1)
    # numbered pins, placed by true city coordinates
    f_pin = sans(10, True)
    for num, (lon, lat, dx, dy) in PINS.items():
        px, py = project(lon, lat, map_w, map_h)
        px += LEFT + dx
        py += by0 + 14 + dy
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED,
                  outline=WHITE, width=2)
        label = str(num)
        lw = text_w(d, label, f_pin)
        d.text((px - lw / 2, py - 7), label, font=f_pin, fill=WHITE)
    lines = fit_or_die(d, MAP_NOTE, sans(10), map_w, 2, "map note")
    draw_lines(d, lines, LEFT, by0 + 178, sans(10), BODY, 12)
    # date check box under the map
    dc_y0, dc_y1 = by0 + 204, 956
    d.rectangle([LEFT, dc_y0, LEFT + map_w, dc_y1], fill=WHITE,
                outline=RED, width=2)
    d.text((LEFT + 10, dc_y0 + 6), "DATE CHECK", font=sans(12, True),
           fill=RED)
    lines = fit_or_die(d, DATE_CHECK, sans(11), map_w - 20, 6, "date check")
    draw_lines(d, lines, LEFT + 10, dc_y0 + 24, sans(11), BODY, 13)

    # briefs panel
    bx0 = 428
    d.text((bx0, by0),
           "ALSO ON SATURDAY 21 NOVEMBER — 22 MORE STORIES",
           font=f_sec, fill=RED)
    f_num = sans(11, True)
    f_br = sans(11)
    col_w = 286
    for j, (num, place, text, src) in enumerate(BRIEFS):
        col = j // 11
        row = j % 11
        x0 = bx0 + col * (col_w + 8)
        y0 = by0 + 22 + row * 27
        d.text((x0, y0), str(num), font=f_num, fill=RED)
        rest = "%s — %s (%s)" % (place, text, src)
        lines = fit_or_die(d, rest, f_br, col_w - 24, 2,
                           "brief %d" % num)
        draw_lines(d, lines, x0 + 24, y0, f_br, BODY, 12)

    # --- footer --------------------------------------------------------
    f_foot = sans(11)
    for j, line in enumerate((FOOTER_1, FOOTER_2)):
        lw = text_w(d, line, f_foot)
        d.text(((W - lw) / 2, 970 + j * 16), line, font=f_foot, fill=NAVY)

    img.save(OUT, optimize=True)
    print("wrote %s (%d bytes)" % (OUT, OUT.stat().st_size))


if __name__ == "__main__":
    paint()
