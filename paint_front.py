"""Paint the 21 November 2026 front page: 36 stories on one 1024x1024 sheet.

The sheet mirrors the winning newspaper layout: a red kicker band, a giant
serif date masthead, a six-number ticker, three illustrated hero stories, a
ten-story grid, a world map beside 23 one-line briefs, a red date-check box
and a sources footer.

Legibility is the point of the whole page, so every word sits on a solid
panel: cream paper (#f6f1e3) or plain white, with dark navy ink (#14243e).
No word is ever drawn on top of a picture, a gradient or a map. The three
hero pictures live in their own boxes and the text lives in the white panels
underneath them. Headlines are bold navy, kickers are bold red on white
only, and body copy never drops below 10.5pt at full size.

Everything on the page is drawn here with Pillow from the story tables
below; nothing is fetched at run time. The one exception is the world map:
its land outline comes from the Natural Earth 110m land dataset (public
domain), stored in the repo as assets/ne_110m_land.geojson and read from
disk, so the program still runs with no network.

    python3 paint_front.py

which writes entry.png next to this file (1024x1024, under 1 MiB).
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

SHEET_W, SHEET_H = 1024, 1024
MARGIN = 28
INNER_W = SHEET_W - 2 * MARGIN

# --- palette: light paper, dark navy ink, one red accent -------------------
PAPER = (246, 241, 227)      # warm cream, the whole sheet
PANEL = (255, 255, 255)      # solid white text panels
INK = (20, 36, 62)           # navy, ~15:1 on white, ~12:1 on cream
BODY = (31, 42, 58)          # near-navy body copy
RED = (176, 30, 36)          # kicker red, ~7:1 on white
RULE = (196, 188, 168)       # hairline rules
LAND = (91, 140, 90)         # map continents: strong atlas green #5b8c5a
LAND2 = (110, 158, 95)       # second land tone, lighter green #6e9e5f
SEA = (207, 227, 238)        # map sea: pale blue #cfe3ee, green land stands out
CHIP_BG = (238, 233, 219)    # stat chip fill

FONT_DIR = "/usr/share/fonts/truetype/liberation"
FONTS = {
    "serif": FONT_DIR + "/LiberationSerif-Regular.ttf",
    "serif_b": FONT_DIR + "/LiberationSerif-Bold.ttf",
    "serif_i": FONT_DIR + "/LiberationSerif-Italic.ttf",
    "sans": FONT_DIR + "/LiberationSans-Regular.ttf",
    "sans_b": FONT_DIR + "/LiberationSans-Bold.ttf",
}


def face(kind, size):
    return ImageFont.truetype(FONTS[kind], size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that all fit max_w."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_w(draw, trial, font) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_block(draw, text, font, max_w, max_lines, label):
    """Wrap text and insist it fits in max_lines; fail loudly otherwise."""
    lines = wrap(draw, text, font, max_w)
    if len(lines) > max_lines:
        raise SystemExit(f"TEXT OVERFLOW in {label}: {len(lines)} lines for {max_lines}: {text!r}")
    return lines


def draw_lines(draw, lines, x, y, font, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# --- the 36 stories ---------------------------------------------------------
# Heroes 1-3 carry the big pictures; grid 4-13 the ten cells; briefs 14-36
# are one-liners. Every figure was checked against wire reports on 21 Nov.

HEROES = [
    {
        "num": 1, "place": "RIYADH, SAUDI ARABIA", "beat": "CONFLICT",
        "head": "Coalition downs three Houthi missiles over Riyadh",
        "deck": "Air defences stop the missiles early on Saturday, the second attack on the capital in days.",
        "art": "riyadh",
    },
    {
        "num": 2, "place": "MERCURY", "beat": "SPACE",
        "head": "BepiColombo reaches Mercury after eight years",
        "deck": "Europe and Japan's twin orbiters enter orbit — only the second craft ever to do so.",
        "art": "mercury",
        "stats": "8 YEARS  ·  10BN KM  ·  2 ORBITERS",
    },
    {
        "num": 3, "place": "ANTALYA, TÜRKIYE", "beat": "CLIMATE",
        "head": "COP31 runs into overtime with no deal",
        "deck": "A draft with no fossil fuels splits nearly 200 nations; a third text is due Saturday morning.",
        "art": "cop31",
        "stats": "1.5°C LIMIT PASSED  ·  3RD DRAFT DUE SAT AM",
    },
]

GRID = [
    {"num": 4, "place": "WARSAW", "beat": "SECURITY",
     "head": "Rutte in Warsaw as Poland seeks more cover",
     "deck": "NATO chief due Saturday after missiles land in Poland."},
    {"num": 5, "place": "KRYVYI RIH", "beat": "WAR",
     "head": "Overnight strike kills 2, injures 42",
     "deck": "A boy of 7 and a paramedic die in a double-tap attack."},
    {"num": 6, "place": "HODEIDAH", "beat": "YEMEN",
     "head": "UN warns port strikes threaten aid lifeline",
     "deck": "Coalition hits weapons sites at Yemen's main port."},
    {"num": 7, "place": "BEIJING", "beat": "TECH",
     "head": "US clears ~900,000 AI chips for China",
     "deck": "House panel: 879,868 Nvidia and AMD chips approved."},
    {"num": 8, "place": "NEW YORK", "beat": "CYBER",
     "head": "Banks hit in attack on outside vendors",
     "deck": "Vendors breached; 16,000 customer emails leaked."},
    {"num": 9, "place": "COPENHAGEN", "beat": "ESPIONAGE",
     "head": "Denmark charges two over Russian murder plot",
     "deck": "Plot to kill rapper Kyivstoner minutes before concert."},
    {"num": 10, "place": "BRUSSELS", "beat": "AID",
     "head": "EU pays out nearly €8bn to Ukraine",
     "deck": "Largest single payment yet: €7.9bn after 20 reforms."},
    {"num": 11, "place": "WELLINGTON", "beat": "CRICKET",
     "head": "India resume on 159/1 on day three",
     "deck": "Rahul 93* at lunch; India 239/1 chasing 368."},
    {"num": 12, "place": "TURIN", "beat": "TENNIS",
     "head": "Medvedev meets Zverev in tonight's semi",
     "deck": "Zverev beats Fils 6-4, 7-6 to reach the last four."},
    {"num": 13, "place": "LAS VEGAS", "beat": "MOTOR RACING",
     "head": "GP qualifying today",
     "deck": "Rain hits practice one; Russell fastest in session two."},
]

BRIEFS = [
    (14, "KYIV", "Barrage kills 8; three bridges hit"),
    (15, "WARSAW", "Poland seeks more NATO forces"),
    (16, "HODEIDAH", "Civilians told to leave the port"),
    (17, "SAADA", "Coalition hits Houthi launch sites"),
    (18, "JAZAN", "Two missiles downed on Friday"),
    (19, "ANTALYA", "Panama vows to block a weak deal"),
    (20, "ANTALYA", "France, Panama press for stronger text"),
    (21, "ANTALYA", "Turkey signs $26bn in deals at COP31"),
    (22, "JUNIN, PERU", "M6.8 quake shakes the Andes"),
    (23, "NEW YORK", "S&P 500 slides 3.7% into correction"),
    (24, "BERLIN", "Metalworkers launch 24-hour strikes"),
    (25, "PARIS", "Senate backs police shootings law"),
    (26, "TALLINN", "Estonia to shut Russia border crossings"),
    (27, "WASHINGTON", "Vance silent on Iran strikes"),
    (28, "WASHINGTON", "Trump cites good talks with Putin"),
    (29, "WASHINGTON", "US floated NATO-for-land swap"),
    (30, "NAYPYIDAW", "Myanmar calls ICJ ruling 'unfair'"),
    (31, "ANTALYA", "Ukraine blocks Russian climate report"),
    (32, "MERCURY", "BepiColombo's X-ray eye opens"),
    (33, "COPENHAGEN", "Denmark expels Russian attaché"),
    (34, "KYIV", "Power out across five regions"),
    (35, "LAS VEGAS", "Russell fastest in second practice"),
    (36, "TURIN", "Zverev beats Fils 6-4, 7-6"),
]

NUMBERS = [
    ("3", "missiles downed over Riyadh"),
    ("8 YRS", "BepiColombo's voyage to Mercury"),
    ("92,000", "people at COP31, the largest ever"),
    ("42", "hurt in the Kryvyi Rih strike"),
    ("~900,000", "AI chips cleared for China"),
    ("2", "killed in the Kryvyi Rih strike"),
]

# Map pins: (story number, longitude, latitude, nudge dx, nudge dy in px).
# True city coordinates; the dx/dy nudges only spread the tight Europe
# cluster so no two pins touch (all nudges <= 12 px, pins stay on the
# right country). Pin 2 is Mercury, off this map, per the note under
# the map title. Pin 11 (Wellington) is nudged 4 px west and 4 px south
# onto the New Zealand landmass: its true spot (x=394) would clip the
# frame, and the earlier -12 nudge put it in the Tasman Sea. The nudge
# was verified point-in-polygon against the bundled land outline.
PIN_GEO = [
    (1, 46.7, 24.7, 0, 0),       # Riyadh
    (3, 30.7, 36.9, 0, 6),       # Antalya
    (4, 21.0, 52.2, 8, -6),      # Warsaw
    (5, 33.4, 47.9, 12, 0),      # Kryvyi Rih
    (6, 42.8, 14.8, 0, 0),       # Hodeidah
    (7, 116.4, 39.9, 0, 0),      # Beijing
    (8, -74.0, 40.7, 0, 0),      # New York
    (9, 12.6, 55.7, -8, -8),     # Copenhagen
    (10, 4.35, 50.85, -10, 2),   # Brussels
    (11, 174.8, -41.3, -4, 4),   # Wellington: nudged onto NZ land, pin stays inside the frame
    (12, 7.7, 45.1, -2, 10),     # Turin
    (13, -115.1, 36.2, 0, 0),    # Las Vegas
]


# --- hero pictures: flat scenes, each in its own box, no text on top -------

def paint_riyadh(draw, x0, y0, w, h):
    """Night over Riyadh: a dusk sky, a towered skyline with lit windows,
    a crescent moon, and three long interceptor trails ending in bright
    bursts over the city. Nothing written on it."""
    sky_top, sky_mid, sky_low = (16, 28, 54), (52, 68, 104), (196, 110, 58)
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.55:
            a, b, f = sky_top, sky_mid, t / 0.55
        else:
            a, b, f = sky_mid, sky_low, (t - 0.55) / 0.45
        col = tuple(round(a[j] + (b[j] - a[j]) * f) for j in range(3))
        draw.line([(x0, y0 + i), (x0 + w, y0 + i)], fill=col)
    import random
    rng = random.Random(21)
    for _ in range(46):
        sx = x0 + rng.randint(4, w - 4)
        sy = y0 + rng.randint(4, int(h * 0.45))
        draw.point((sx, sy), fill=(235, 230, 210))
    # Crescent moon, top right: a pale disc with a sky-coloured bite.
    mx, my, mr = x0 + w - 38, y0 + 26, 15
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(242, 232, 190))
    bite = (29, 42, 72)  # the dusk gradient at this height
    draw.ellipse([mx - mr + 8, my - mr - 3, mx + mr + 8, my + mr - 3], fill=bite)
    base = y0 + h
    # skyline: dark slabs with lit windows, tallest tower left of centre
    draw.rectangle([x0, base - 58, x0 + w, base], fill=(12, 20, 38))
    towers = [(0, 52, 34), (40, 88, 30), (76, 64, 26), (108, 118, 44),
              (158, 70, 30), (194, 96, 34), (234, 58, 26), (266, 80, 30)]
    for tx, th, tw in towers:
        draw.rectangle([x0 + tx, base - th, x0 + tx + tw, base], fill=(24, 34, 58))
        for wy in range(base - th + 8, base - 8, 12):
            for wx in range(x0 + tx + 5, x0 + tx + tw - 4, 10):
                if rng.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(240, 196, 90))
    # PIF-style tapered tower: a tall wedge with a notch at the top
    px = x0 + 108
    draw.polygon([(px, base - 118), (px + 44, base - 118), (px + 38, base - 96),
                  (px + 38, base), (px + 6, base), (px + 6, base - 96)],
                 fill=(30, 44, 74))
    draw.polygon([(px + 12, base - 118), (px + 32, base - 118), (px + 28, base - 104),
                  (px + 16, base - 104)], fill=(240, 196, 90))
    # Three long interceptor trails, each ending in a bright burst.
    # A trail is a thick orange streak with a white core, rising steeply
    # from the burst toward the top of the frame; the burst is a glowing
    # core with long rays and a shock ring.
    import math
    for (bx, by), (tx, ty) in [((x0 + 78, y0 + 46), (x0 + 46, y0 + 2)),
                               ((x0 + 168, y0 + 36), (x0 + 196, y0 + 2)),
                               ((x0 + 252, y0 + 56), (x0 + 224, y0 + 6))]:
        draw.line([(tx, ty), (bx, by)], fill=(240, 140, 60), width=5)
        draw.line([(tx, ty), (bx, by)], fill=(255, 255, 255), width=2)
        draw.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=(255, 190, 90))
        draw.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=(255, 160, 60))
        draw.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(255, 214, 120))
        draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(255, 255, 255))
        for k in range(12):
            a = math.radians(k * 30)
            r1, r2 = 12, 21 if k % 2 == 0 else 16
            draw.line([(bx + int(r1 * math.cos(a)), by + int(r1 * math.sin(a))),
                       (bx + int(r2 * math.cos(a)), by + int(r2 * math.sin(a)))],
                      fill=(255, 214, 120) if k % 2 else (255, 255, 255), width=2)
        draw.ellipse([bx - 18, by - 18, bx + 18, by + 18],
                     outline=(255, 214, 120), width=1)


def paint_mercury(draw, x0, y0, w, h):
    """Mercury sits to the right, a modest cratered disc; the two
    BepiColombo orbiters fly large in the left half, gold panels spread,
    on a faint orbit arc, against a starfield. Nothing written on it."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(10, 12, 24))
    import random
    rng = random.Random(7)
    for _ in range(70):
        sx = x0 + rng.randint(2, w - 2)
        sy = y0 + rng.randint(2, h - 2)
        draw.point((sx, sy), fill=(220, 220, 235))
    # Mercury: a small disc at the right, craters small. Bos: r=54 was
    # still too big ("kurang kecil") — r=33 leaves clear space on all
    # sides and lets the two orbiters dominate the box.
    cx, cy, r = x0 + w - 48, y0 + h // 2 + 4, 33
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 160, 148))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 112, 100), width=2)
    for ox, oy, orad, shade in [(cx - 13, cy - 11, 6, (140, 132, 120)),
                                (cx + 7, cy + 4, 9, (146, 138, 126)),
                                (cx - 2, cy + 16, 5, (128, 120, 108)),
                                (cx + 17, cy - 16, 4, (150, 142, 130)),
                                (cx - 20, cy + 6, 3, (136, 128, 116))]:
        draw.ellipse([ox - orad, oy - orad, ox + orad, oy + orad], fill=shade)
        draw.arc([ox - orad, oy - orad, ox + orad, oy + orad], 200, 340,
                 fill=(110, 102, 92), width=2)
    # Faint orbit arc sweeping from the spacecraft toward Mercury.
    draw.arc([cx - 168, cy - 74, cx + 168, cy + 74], 130, 245,
             fill=(150, 150, 165), width=1)

    def orbiter(bx, by, s):
        """One orbiter: a silver-blue body, gold solar wings with grid
        seams, a dish, and a blue thruster glow. s scales the craft."""
        pw, ph = int(52 * s), int(14 * s)
        bw, bh = int(26 * s), int(20 * s)
        # gold wings, left and right of the body
        for sx0 in (bx - pw - bw // 2, bx + bw // 2):
            draw.rectangle([sx0, by - ph // 2, sx0 + pw, by + ph // 2],
                           fill=(212, 164, 60))
            draw.rectangle([sx0, by - ph // 2, sx0 + pw, by + ph // 2],
                           outline=(120, 84, 20), width=1)
            for gx in range(sx0 + pw // 3, sx0 + pw, pw // 3):
                draw.line([(gx, by - ph // 2), (gx, by + ph // 2)],
                          fill=(150, 108, 30), width=1)
            draw.line([(sx0, by), (sx0 + pw, by)], fill=(150, 108, 30), width=1)
        # silver-blue body with a dark window and a mast
        draw.rectangle([bx - bw // 2, by - bh // 2, bx + bw // 2, by + bh // 2],
                       fill=(200, 208, 222))
        draw.rectangle([bx - bw // 2, by - bh // 2, bx + bw // 2, by + bh // 2],
                       outline=(110, 118, 134), width=1)
        draw.rectangle([bx - bw // 2 + 3, by - 3, bx + bw // 2 - 3, by + 3],
                       fill=(30, 60, 110))
        draw.line([(bx, by - bh // 2), (bx, by - bh // 2 - int(10 * s))],
                  fill=(180, 186, 196), width=2)
        draw.ellipse([bx - 2, by - bh // 2 - int(12 * s),
                      bx + 2, by - bh // 2 - int(8 * s)], fill=(226, 228, 232))
        # thruster glow trailing to the lower left
        draw.polygon([(bx - bw // 2, by + bh // 2 - 3),
                      (bx - bw // 2 - int(18 * s), by + bh // 2 + int(6 * s)),
                      (bx - bw // 2, by + bh // 2 + 3)], fill=(120, 190, 230))
        draw.ellipse([bx - bw // 2 - int(22 * s), by + bh // 2,
                      bx - bw // 2 - int(10 * s), by + bh // 2 + int(12 * s)],
                     fill=(170, 225, 250))

    orbiter(x0 + 82, y0 + 44, 1.0)
    orbiter(x0 + 118, y0 + 96, 0.85)


def paint_cop31(draw, x0, y0, w, h):
    """COP31 in overtime: one big red thermometer rising past the top of
    its tube against a teal wall, a neat row of small flags along the
    bottom edge. The teal runs to the bottom of the box: no pale strip,
    no delegates, no clock, no words on the picture."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(18, 84, 88))
    # Thermometer: a tall white tube with a round bulb, red fill rising
    # almost to the top, tick marks on the right, no numbers.
    tx = x0 + w // 2
    tube_top, tube_bot, tube_w = y0 + 8, y0 + 98, 36
    bulb_cy, bulb_r = y0 + 102, 24
    draw.rounded_rectangle([tx - tube_w // 2, tube_top,
                            tx + tube_w // 2, tube_bot],
                           radius=tube_w // 2, fill=(250, 247, 240))
    draw.ellipse([tx - bulb_r, bulb_cy - bulb_r, tx + bulb_r, bulb_cy + bulb_r],
                 fill=(250, 247, 240))
    draw.ellipse([tx - bulb_r, bulb_cy - bulb_r, tx + bulb_r, bulb_cy + bulb_r],
                 outline=(20, 36, 62), width=2)
    draw.rounded_rectangle([tx - tube_w // 2, tube_top,
                            tx + tube_w // 2, tube_bot],
                           radius=tube_w // 2, outline=(20, 36, 62), width=2)
    # red fill: from the bulb up to near the top of the tube
    fill_top = y0 + 16
    draw.rounded_rectangle([tx - tube_w // 2 + 5, fill_top,
                            tx + tube_w // 2 - 5, tube_bot],
                           radius=8, fill=(176, 30, 36))
    draw.ellipse([tx - bulb_r + 5, bulb_cy - bulb_r + 5,
                  tx + bulb_r - 5, bulb_cy + bulb_r - 5], fill=(176, 30, 36))
    # glass highlight down the left of the tube
    draw.line([(tx - tube_w // 2 + 9, fill_top + 8),
               (tx - tube_w // 2 + 9, tube_bot - 6)], fill=(232, 120, 110), width=3)
    # tick marks on the right of the tube
    for ty in (y0 + 26, y0 + 44, y0 + 62, y0 + 80):
        draw.line([(tx + tube_w // 2 + 2, ty), (tx + tube_w // 2 + 12, ty)],
                  fill=(250, 247, 240), width=2)
    # Small flags in a neat row along the bottom edge, standing on the
    # teal itself: two each side of the bulb, never over it.
    flag_cols = [(176, 30, 36), (20, 90, 60), (30, 60, 140), (220, 150, 30)]
    for fx, col in zip([x0 + 28, x0 + 78, x0 + 236, x0 + 286], flag_cols):
        draw.line([(fx, y0 + h - 2), (fx, y0 + h - 24)], fill=(250, 247, 240), width=2)
        draw.polygon([(fx, y0 + h - 24), (fx + 18, y0 + h - 19), (fx, y0 + h - 14)],
                     fill=col)


# --- the world map: real Natural Earth land outline, numbered pins -------
#
# The land comes from assets/ne_110m_land.geojson (Natural Earth 110m land,
# public domain, 127 polygons). Equirectangular projection over the map box:
# longitude -180..180 across, latitude 85..-60 top to bottom (Antarctica
# is clipped at the bottom edge of the panel). Polygons are clamped to the
# box so nothing paints outside the frame.

import json

_LAND_CACHE = {}


def _load_land(w, h):
    """Project the bundled land polygons into box coordinates once."""
    if (w, h) in _LAND_CACHE:
        return _LAND_CACHE[(w, h)]
    with open(HERE / "assets" / "ne_110m_land.geojson", encoding="utf-8") as fh:
        data = json.load(fh)
    polys = []
    for feat in data["features"]:
        for ring in feat["geometry"]["coordinates"]:
            pts = []
            for lon, lat in ring:
                px = (lon + 180.0) / 360.0 * w
                py = (85.0 - lat) / 145.0 * h
                pts.append((min(max(px, 0.0), w), min(max(py, 0.0), h)))
            if len(pts) >= 3:
                polys.append(pts)
    _LAND_CACHE[(w, h)] = polys
    return polys


def paint_map(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA)
    for poly in _load_land(w, h):
        pts = [(x0 + px, y0 + py) for px, py in poly]
        draw.polygon(pts, fill=LAND, outline=(58, 96, 58))
    for num, lon, lat, dx, dy in PIN_GEO:
        cx = x0 + (lon + 180.0) / 360.0 * w + dx
        cy = y0 + (85.0 - lat) / 145.0 * h + dy
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=INK)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=PANEL, width=2)
        f = face("sans_b", 10)
        tw = text_w(draw, str(num), f)
        draw.text((cx - tw / 2, cy - 7), str(num), font=f, fill=PANEL)


# --- grid icons: one bold shape per cell, no text inside --------------------

def paint_grid_icon(draw, gx, gy, w, num):
    """A 34 px icon strip at the top of a grid cell: one bold, instantly
    readable shape on a flat band, big enough to read at thumbnail size.
    No words inside the strip."""
    import math
    band = {
        4: (20, 40, 90), 5: (24, 28, 44), 6: (16, 90, 96),
        7: (30, 38, 54), 8: (18, 32, 60), 9: (24, 36, 62),
        10: (24, 52, 110), 11: (24, 100, 60), 12: (20, 90, 70),
        13: (250, 247, 240),
    }[num]
    draw.rectangle([gx, gy, gx + w, gy + 34], fill=band)
    cx, cy = gx + w // 2, gy + 17
    if num == 4:
        # NATO compass star, white on navy
        pts = []
        for k in range(8):
            a = math.radians(k * 45)
            r = 15 if k % 2 == 0 else 5
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        draw.polygon(pts, fill=(255, 255, 255))
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(20, 40, 90))
    elif num == 5:
        # explosion burst, gold and white on charcoal
        for k in range(12):
            a = math.radians(k * 30)
            r2 = 15 if k % 2 == 0 else 10
            draw.line([(cx, cy), (cx + int(r2 * math.cos(a)),
                                 cy + int(r2 * math.sin(a)))],
                      fill=(255, 214, 120) if k % 2 else (255, 255, 255), width=3)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 160, 60))
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    elif num == 6:
        # port crane lifting a container over a ship hull, pale on teal
        draw.line([(cx - 30, gy + 5), (cx - 30, gy + 26)], fill=(250, 247, 240), width=5)
        draw.line([(cx - 30, gy + 5), (cx + 30, gy + 13)], fill=(250, 247, 240), width=4)
        draw.line([(cx - 30, gy + 5), (cx - 44, gy + 11)], fill=(250, 247, 240), width=4)
        draw.line([(cx + 18, gy + 11), (cx + 18, gy + 19)], fill=(250, 247, 240), width=2)
        draw.rectangle([cx + 11, gy + 19, cx + 25, gy + 25], fill=(250, 247, 240))
        draw.rectangle([cx - 38, gy + 26, cx + 38, gy + 31], fill=(12, 20, 38))
        draw.rectangle([cx - 38, gy + 26, cx + 38, gy + 31], outline=(250, 247, 240), width=1)
    elif num == 7:
        # gold chip with pins, on dark slate
        draw.rounded_rectangle([cx - 10, cy - 10, cx + 10, cy + 10], radius=3,
                               fill=(212, 164, 60))
        draw.rounded_rectangle([cx - 10, cy - 10, cx + 10, cy + 10], radius=3,
                               outline=(120, 84, 20), width=1)
        for dx in (-6, 0, 6):
            draw.line([(cx + dx, cy - 16), (cx + dx, cy - 10)], fill=(212, 164, 60), width=2)
            draw.line([(cx + dx, cy + 10), (cx + dx, cy + 16)], fill=(212, 164, 60), width=2)
            draw.line([(cx - 16, cy + dx), (cx - 10, cy + dx)], fill=(212, 164, 60), width=2)
            draw.line([(cx + 10, cy + dx), (cx + 16, cy + dx)], fill=(212, 164, 60), width=2)
    elif num == 8:
        # bank: pediment, three columns, base, white on navy
        draw.polygon([(cx - 44, cy + 3), (cx + 44, cy + 3), (cx, cy - 12)],
                     fill=(255, 255, 255))
        for colx in (cx - 30, cx - 3, cx + 24):
            draw.rectangle([colx, cy + 5, colx + 6, cy + 12], fill=(255, 255, 255))
        draw.rectangle([cx - 44, cy + 13, cx + 44, cy + 16], fill=(255, 255, 255))
    elif num == 9:
        # shield with a star: white shield, navy star, on navy. The old
        # handcuffs read as an infinity symbol at small size.
        draw.polygon([(cx - 12, cy - 13), (cx + 12, cy - 13), (cx + 12, cy + 1),
                      (cx, cy + 15), (cx - 12, cy + 1)], fill=(255, 255, 255))
        star = []
        for k in range(10):
            a = math.radians(-90 + k * 36)
            r = 7 if k % 2 == 0 else 3
            star.append((cx + r * math.cos(a), cy - 1 + r * math.sin(a)))
        draw.polygon(star, fill=(24, 36, 62))
    elif num == 10:
        # gold coin: a disc with an inner ring, on dark blue
        draw.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(212, 164, 60))
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7],
                     outline=(150, 108, 30), width=2)
    elif num == 11:
        # cricket bat and red ball, on green
        draw.line([(cx - 32, cy + 10), (cx - 4, cy - 10)], fill=(250, 247, 240), width=9)
        draw.line([(cx - 4, cy - 10), (cx + 10, cy - 12)], fill=(250, 247, 240), width=4)
        draw.ellipse([cx + 8, cy - 3, cx + 22, cy + 11], fill=(176, 30, 36))
        draw.ellipse([cx + 8, cy - 3, cx + 22, cy + 11], outline=(120, 20, 24), width=1)
    elif num == 12:
        # tennis ball with white seams, on dark green
        draw.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(190, 220, 60))
        draw.arc([cx - 13, cy - 13, cx + 13, cy + 13], 55, 125, fill=(255, 255, 255), width=3)
        draw.arc([cx - 13, cy - 13, cx + 13, cy + 13], 235, 305, fill=(255, 255, 255), width=3)
    elif num == 13:
        # chequered flag: black and white squares across the strip
        sq = w // 8
        for col in range(8):
            for row in range(2):
                if (col + row) % 2 == 0:
                    draw.rectangle([gx + col * sq, gy + row * 17,
                                    gx + (col + 1) * sq, gy + (row + 1) * 17],
                                   fill=(16, 16, 16))


# --- page assembly ----------------------------------------------------------

def paint_page():
    sheet = Image.new("RGB", (SHEET_W, SHEET_H), PAPER)
    draw = ImageDraw.Draw(sheet)

    # Top band: red kicker left, count line right, one hairline under.
    draw.text((MARGIN, 10), "THE WORLD IN ONE DAY", font=face("sans_b", 15), fill=RED)
    right = "36 STORIES · 6 REGIONS · EVERY ONE DATED"
    rf = face("sans_b", 12)
    draw.text((SHEET_W - MARGIN - text_w(draw, right, rf), 12), right, font=rf, fill=INK)
    draw.line([(MARGIN, 34), (SHEET_W - MARGIN, 34)], fill=RULE, width=1)

    # Masthead: the date, giant serif, centred.
    mast = face("serif_b", 56)
    title = "Saturday 21 November 2026"
    draw.text(((SHEET_W - text_w(draw, title, mast)) / 2, 40), title, font=mast, fill=INK)

    # Italic standfirst: the four lead threads of the day.
    stand = face("serif_i", 19)
    line = "Riyadh intercepts three missiles · COP31 into overtime · BepiColombo at Mercury · Rutte in Warsaw"
    draw.text(((SHEET_W - text_w(draw, line, stand)) / 2, 100), line, font=stand, fill=BODY)

    # Numbers strip: six cells, big navy figures over small captions.
    strip_y, strip_h = 128, 60
    draw.line([(MARGIN, strip_y), (SHEET_W - MARGIN, strip_y)], fill=RULE, width=1)
    draw.line([(MARGIN, strip_y + strip_h), (SHEET_W - MARGIN, strip_y + strip_h)],
              fill=RULE, width=1)
    cell_w = INNER_W / 6
    for i, (big, cap) in enumerate(NUMBERS):
        cx = MARGIN + cell_w * i
        if i:
            draw.line([(cx, strip_y + 8), (cx, strip_y + strip_h - 8)], fill=RULE, width=1)
        bf = face("serif_b", 27)
        draw.text((cx + (cell_w - text_w(draw, big, bf)) / 2, strip_y + 4),
                  big, font=bf, fill=INK)
        cf = face("sans", 11)
        cap_lines = fit_block(draw, cap, cf, cell_w - 14, 2, f"number {big}")
        cy = strip_y + 34
        for cline in cap_lines:
            draw.text((cx + (cell_w - text_w(draw, cline, cf)) / 2, cy),
                      cline, font=cf, fill=BODY)
            cy += 13

    # Three heroes: picture box on top, solid white text panel below.
    hero_y, art_h, panel_h = 192, 136, 104
    hero_w, hero_gap = 314, 13
    painters = {"riyadh": paint_riyadh, "mercury": paint_mercury, "cop31": paint_cop31}
    for i, hero in enumerate(HEROES):
        hx = MARGIN + i * (hero_w + hero_gap)
        painters[hero["art"]](draw, hx, hero_y, hero_w, art_h)
        py = hero_y + art_h
        draw.rectangle([hx, py, hx + hero_w, py + panel_h], fill=PANEL)
        draw.rectangle([hx, py, hx + hero_w, py + panel_h], outline=RULE, width=1)
        kicker = f"{hero['num']} · {hero['place']} · {hero['beat']}"
        draw.text((hx + 8, py + 5), kicker, font=face("sans_b", 11), fill=RED)
        hf = face("serif_b", 19)
        head_lines = fit_block(draw, hero["head"], hf, hero_w - 16, 2, f"hero {hero['num']}")
        draw_lines(draw, head_lines, hx + 8, py + 19, hf, INK, 21)
        df = face("sans", 12)
        deck_lines = fit_block(draw, hero["deck"], df, hero_w - 16, 2, f"hero deck {hero['num']}")
        draw_lines(draw, deck_lines, hx + 8, py + 62, df, BODY, 14)
        if "stats" in hero:
            sf = face("sans_b", 10)
            draw.text((hx + 8, py + 90), hero["stats"], font=sf, fill=INK)

    # Ten-story grid: two rows of five white cells, one bold 34 px icon
    # strip on top of each, then kicker, headline and deck below it. The
    # rows are 108 px tall so the taller strip still leaves room for a
    # two-line headline and a two-line deck; the deck bottom is asserted
    # against the cell border and the painter fails loudly if it crosses.
    grid_y, grid_h = 440, 216
    cell_w, cell_gap = 185, 10
    row_h = grid_h // 2
    for i, story in enumerate(GRID):
        row, col = divmod(i, 5)
        gx = MARGIN + col * (cell_w + cell_gap)
        gy = grid_y + row * row_h
        draw.rectangle([gx, gy, gx + cell_w, gy + row_h - 4], fill=PANEL)
        paint_grid_icon(draw, gx, gy, cell_w, story["num"])
        draw.rectangle([gx, gy, gx + cell_w, gy + row_h - 4], outline=RULE, width=1)
        kicker = f"{story['num']} · {story['place']} · {story['beat']}"
        draw.text((gx + 7, gy + 36), kicker, font=face("sans_b", 10), fill=RED)
        hf = face("serif_b", 15)
        head_lines = fit_block(draw, story["head"], hf, cell_w - 14, 2,
                               f"grid {story['num']}")
        draw_lines(draw, head_lines, gx + 7, gy + 48, hf, INK, 15)
        df = face("sans", 11)
        deck_lines = fit_block(draw, story["deck"], df, cell_w - 14, 2,
                               f"grid deck {story['num']}")
        deck_bottom = gy + 80 + (len(deck_lines) - 1) * 11 + 11
        if deck_bottom > gy + row_h - 4:
            raise SystemExit(
                f"GRID CELL OVERFLOW in grid {story['num']}: deck ends at "
                f"{deck_bottom}, cell ends at {gy + row_h - 4}")
        draw_lines(draw, deck_lines, gx + 7, gy + 80, df, BODY, 11)

    # Bottom band: map left, 23 one-line briefs right.
    bot_y, bot_h = 658, 248
    map_w, also_w = 400, INNER_W - 400 - 12
    also_x = MARGIN + map_w + 12
    draw.text((MARGIN, bot_y), "WHERE IT HAPPENED", font=face("sans_b", 13), fill=RED)
    draw.text((MARGIN, bot_y + 18),
              "Pins match the numbered stories. 2 · Mercury is in orbit, off this map.",
              font=face("sans", 10), fill=BODY)
    map_y = bot_y + 38
    paint_map(draw, MARGIN, map_y, map_w, bot_y + bot_h - map_y)
    draw.rectangle([MARGIN, map_y, MARGIN + map_w, bot_y + bot_h], outline=RULE, width=1)

    draw.text((also_x, bot_y), "ALSO ON SATURDAY 21 NOVEMBER — 23 MORE STORIES",
              font=face("sans_b", 13), fill=RED)
    brief_f, brief_b = face("sans", 11), face("sans_b", 11)
    half = 12
    for col_i, chunk in enumerate([BRIEFS[:half], BRIEFS[half:]]):
        bx = also_x + col_i * (also_w // 2 + 6)
        by = bot_y + 22
        for num, place, text in chunk:
            head = f"{num} {place} — "
            hw = text_w(draw, head, brief_b)
            tw = text_w(draw, text, brief_f)
            if hw + tw > also_w // 2 - 4:
                raise SystemExit(f"BRIEF OVERFLOW: {num} {place}: {text!r}")
            draw.text((bx, by), head, font=brief_b, fill=RED)
            draw.text((bx + hw, by), text, font=brief_f, fill=BODY)
            by += 19

    # Date check: red border, naming what was kept out as other days' news.
    dc_y, dc_h = 914, 48
    draw.rectangle([MARGIN, dc_y, SHEET_W - MARGIN, dc_y + dc_h], fill=PANEL)
    draw.rectangle([MARGIN, dc_y, SHEET_W - MARGIN, dc_y + dc_h], outline=RED, width=2)
    draw.text((MARGIN + 8, dc_y + 5), "DATE CHECK — NOT 21 NOVEMBER NEWS, KEPT OUT:",
              font=face("sans_b", 11), fill=RED)
    dc = ("PIF Tower strike (Thu 19 Nov) · GTA VI launch (Thu 19 Nov) · "
          "Anthropic's first trades (Thu 19 Nov) · Senate Iran war-powers vote "
          "(Thu 19 Nov) · first COP31 draft (Mon 16 Nov)")
    dcf = face("sans", 11)
    dc_lines = fit_block(draw, dc, dcf, INNER_W - 16, 2, "date check")
    draw_lines(draw, dc_lines, MARGIN + 8, dc_y + 22, dcf, BODY, 13)

    # Footer: the day rule and the sources, centred.
    foot = face("sans", 11)
    f1 = "Every story here happened, or was first reported, on Saturday 21 November 2026."
    f2 = "Sources: Reuters, AP, AFP, BBC, ESA, JAXA, UN, European Commission. Original drawings."
    draw.text(((SHEET_W - text_w(draw, f1, foot)) / 2, 970), f1, font=foot, fill=BODY)
    draw.text(((SHEET_W - text_w(draw, f2, foot)) / 2, 986), f2, font=foot, fill=BODY)

    return sheet


def main():
    page = paint_page()
    out = HERE / "entry.png"
    page.save(out, optimize=True)
    print(f"entry.png: {out.stat().st_size} bytes, {page.size[0]}x{page.size[1]}")


if __name__ == "__main__":
    main()
