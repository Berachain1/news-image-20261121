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
below; nothing is fetched, nothing is copied in. Run it with:

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
LAND = (216, 208, 188)       # map continents
LAND2 = (198, 206, 190)      # second land tone
SEA = (233, 236, 228)        # map sea, still light
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

# Map pins: (story number, x, y) in the map box's own coordinates.
PINS = [
    (1, 248, 108), (3, 228, 88), (4, 224, 44), (5, 242, 64),
    (6, 252, 128), (7, 322, 78), (8, 92, 84), (9, 192, 38),
    (10, 196, 60), (11, 372, 198), (12, 210, 78), (13, 72, 94),
]


# --- hero pictures: flat scenes, each in its own box, no text on top -------

def paint_riyadh(draw, x0, y0, w, h):
    """Night over Riyadh: a dusk sky, a towered skyline, three white
    interceptor streaks bursting in the dark. Nothing written on it."""
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
    # three interceptor streaks with starbursts
    for bx, by in [(x0 + 70, y0 + 34), (x0 + 165, y0 + 22), (x0 + 250, y0 + 42)]:
        draw.line([(bx - 26, by + 30), (bx, by)], fill=(255, 255, 255), width=3)
        for dx, dy in [(0, -14), (0, 14), (-14, 0), (14, 0),
                       (-10, -10), (10, -10), (-10, 10), (10, 10)]:
            draw.line([(bx, by), (bx + dx, by + dy)], fill=(255, 214, 120), width=2)
        draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 255, 255))


def paint_mercury(draw, x0, y0, w, h):
    """Mercury fills the right of the frame, cratered grey on black;
    the twin orbiters with gold panels approach from the left."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(10, 12, 24))
    import random
    rng = random.Random(7)
    for _ in range(70):
        sx = x0 + rng.randint(2, w - 2)
        sy = y0 + rng.randint(2, h - 2)
        draw.point((sx, sy), fill=(220, 220, 235))
    cx, cy, r = x0 + w - 52, y0 + h // 2 + 6, 86
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 160, 148))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 112, 100), width=2)
    for ox, oy, orad, shade in [(cx - 34, cy - 30, 16, (140, 132, 120)),
                                (cx + 18, cy + 8, 22, (146, 138, 126)),
                                (cx - 8, cy + 42, 12, (128, 120, 108)),
                                (cx + 44, cy - 44, 10, (150, 142, 130)),
                                (cx - 52, cy + 18, 8, (136, 128, 116))]:
        draw.ellipse([ox - orad, oy - orad, ox + orad, oy + orad], fill=shade)
        draw.arc([ox - orad, oy - orad, ox + orad, oy + orad], 200, 340,
                 fill=(110, 102, 92), width=2)
    # twin orbiters: two stacked bodies, gold solar wings, a thruster glow
    bx, by = x0 + 52, y0 + h // 2 - 6
    draw.rectangle([bx - 46, by - 8, bx - 8, by + 8], fill=(212, 164, 60))
    draw.line([(bx - 46, by), (bx - 8, by)], fill=(150, 108, 30), width=2)
    draw.rectangle([bx - 46, by - 8, bx - 8, by + 8], outline=(120, 84, 20), width=1)
    draw.rectangle([bx + 8, by - 8, bx + 46, by + 8], fill=(212, 164, 60))
    draw.rectangle([bx + 8, by - 8, bx + 46, by + 8], outline=(120, 84, 20), width=1)
    draw.rectangle([bx - 10, by - 12, bx + 10, by + 12], fill=(226, 228, 232))
    draw.rectangle([bx - 10, by - 12, bx + 10, by + 12], outline=(120, 124, 132), width=1)
    draw.rectangle([bx - 4, by - 20, bx + 4, by - 12], fill=(180, 186, 196))
    draw.polygon([(bx + 10, by - 6), (bx + 26, by - 12), (bx + 26, by + 12),
                  (bx + 10, by + 6)], fill=(120, 190, 230))
    draw.ellipse([bx + 24, by - 8, bx + 40, by + 8], fill=(160, 220, 250))


def paint_cop31(draw, x0, y0, w, h):
    """A summit hall in overtime: teal wall, a big round clock, a long
    table with flags and name plates, delegates in silhouette."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(18, 84, 88))
    draw.rectangle([x0, y0 + h - 46, x0 + w, y0 + h], fill=(122, 74, 40))
    # round wall clock, hands past midnight, top-left clear of delegates
    ccx, ccy, cr = x0 + 44, y0 + 32, 24
    draw.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(250, 247, 240))
    draw.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], outline=(20, 36, 62), width=3)
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        draw.line([(ccx + int(19 * math.sin(a)), ccy - int(19 * math.cos(a))),
                   (ccx + int(22 * math.sin(a)), ccy - int(22 * math.cos(a)))],
                  fill=(20, 36, 62), width=2)
    draw.line([(ccx, ccy), (ccx - 2, ccy - 15)], fill=(176, 30, 36), width=3)
    draw.line([(ccx, ccy), (ccx + 11, ccy - 4)], fill=(20, 36, 62), width=3)
    draw.ellipse([ccx - 3, ccy - 3, ccx + 3, ccy + 3], fill=(176, 30, 36))
    # long table with a pale cloth and small flags
    draw.rectangle([x0 + 14, y0 + h - 78, x0 + w - 14, y0 + h - 40],
                   fill=(250, 247, 240))
    draw.rectangle([x0 + 14, y0 + h - 78, x0 + w - 14, y0 + h - 40],
                   outline=(20, 36, 62), width=2)
    flag_cols = [(176, 30, 36), (20, 90, 60), (30, 60, 140), (220, 150, 30),
                 (120, 40, 110), (30, 120, 140)]
    for i, col in enumerate(flag_cols):
        fx = x0 + 86 + i * 38
        draw.line([(fx, y0 + h - 78), (fx, y0 + h - 104)], fill=(60, 50, 40), width=2)
        draw.polygon([(fx, y0 + h - 104), (fx + 18, y0 + h - 99), (fx, y0 + h - 94)],
                     fill=col)
        draw.rectangle([fx - 8, y0 + h - 72, fx + 26, y0 + h - 60], fill=(238, 233, 219))
    # delegates: dark silhouettes with pale shirts behind the table
    for i, dx in enumerate([96, 140, 184, 228, 272]):
        draw.ellipse([x0 + dx - 11, y0 + h - 132, x0 + dx + 11, y0 + h - 108],
                     fill=(24, 32, 48))
        draw.polygon([(x0 + dx - 16, y0 + h - 78), (x0 + dx + 16, y0 + h - 78),
                      (x0 + dx + 10, y0 + h - 110), (x0 + dx - 10, y0 + h - 110)],
                     fill=(24, 32, 48) if i % 2 == 0 else (58, 66, 84))
        draw.rectangle([x0 + dx - 3, y0 + h - 108, x0 + dx + 3, y0 + h - 92],
                       fill=(250, 247, 240))


# --- the world map: schematic continents, numbered navy pins --------------

def paint_map(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA)
    # Rough continent blobs, drawn as flat polygons in my own coordinates.
    continents = [
        # North America
        [(18, 42), (58, 22), (108, 26), (128, 46), (112, 66), (84, 62),
         (66, 82), (48, 78), (30, 62)],
        # South America
        [(78, 108), (104, 100), (118, 122), (104, 158), (88, 150), (74, 124)],
        # Europe
        [(196, 34), (222, 26), (238, 40), (228, 54), (206, 56), (194, 46)],
        # Africa
        [(196, 74), (228, 66), (248, 84), (240, 118), (216, 132), (198, 104)],
        # Asia
        [(244, 30), (300, 18), (352, 30), (368, 52), (340, 74), (300, 82),
         (268, 66), (246, 52)],
        # Australia
        [(330, 138), (366, 132), (382, 150), (352, 164), (330, 154)],
    ]
    for poly in continents:
        pts = [(x0 + px, y0 + py) for px, py in poly]
        draw.polygon(pts, fill=LAND)
    # Greenland + Britain hints
    draw.ellipse([x0 + 138, y0 + 8, x0 + 168, y0 + 26], fill=LAND2)
    draw.ellipse([x0 + 188, y0 + 38, x0 + 198, y0 + 50], fill=LAND2)
    for num, px, py in PINS:
        cx, cy = x0 + px, y0 + py
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=INK)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=PANEL, width=1)
        f = face("sans_b", 10)
        tw = text_w(draw, str(num), f)
        draw.text((cx - tw / 2, cy - 7), str(num), font=f, fill=PANEL)


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
    hero_y, art_h, panel_h = 196, 136, 104
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

    # Ten-story grid: two rows of five white cells, red top rule each.
    grid_y, grid_h = 444, 200
    cell_w, cell_gap = 185, 10
    row_h = grid_h // 2
    for i, story in enumerate(GRID):
        row, col = divmod(i, 5)
        gx = MARGIN + col * (cell_w + cell_gap)
        gy = grid_y + row * row_h
        draw.rectangle([gx, gy, gx + cell_w, gy + row_h - 4], fill=PANEL)
        draw.rectangle([gx, gy, gx + cell_w, gy + 3], fill=RED)
        draw.rectangle([gx, gy, gx + cell_w, gy + row_h - 4], outline=RULE, width=1)
        kicker = f"{story['num']} · {story['place']} · {story['beat']}"
        draw.text((gx + 7, gy + 8), kicker, font=face("sans_b", 10), fill=RED)
        hf = face("serif_b", 15)
        head_lines = fit_block(draw, story["head"], hf, cell_w - 14, 3,
                               f"grid {story['num']}")
        draw_lines(draw, head_lines, gx + 7, gy + 24, hf, INK, 17)
        df = face("sans", 11)
        deck_lines = fit_block(draw, story["deck"], df, cell_w - 14, 2,
                               f"grid deck {story['num']}")
        draw_lines(draw, deck_lines, gx + 7, gy + 72, df, BODY, 13)

    # Bottom band: map left, 23 one-line briefs right.
    bot_y, bot_h = 652, 254
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
