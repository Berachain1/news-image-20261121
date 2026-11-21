[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Berachain1/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Berachain1/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# The World in One Day — Saturday 21 November 2026

Entry for the make.fun bounty
[news-image-20261121](https://make.fun/bounty/news-image-20261121): one
image summing up the world's news on 21 November 2026.

`entry.png` (1024×1024) is a newspaper front page drawn by
`paint_front_v2.py` (Pillow, no network): 35 stories across 7 regions —
COP31 running into overtime in Antalya, five Houthi missiles shot down
over Saudi Arabia, the 6.7 quake in Junín, Peru, plus a ten-cell grid
(Kyiv, Hormuz, Tehran, Washington, Beijing, Davao, Canberra, bitcoin,
Las Vegas, Wellington) and 22 more briefs — plus a numbers ticker, a
region bar, a navy-and-tan world map with numbered pins, and a date
check naming what was kept out as other days' news. Every figure was
checked against live reporting on 21 November 2026 before drawing; the
BepiColombo orbit insertion, due at 19:24 CET that evening, is listed
as due tonight rather than as done.

Every word sits on solid cream or white with dark navy ink, so the
page stays legible at thumbnail size; the three hero pictures live in
their own boxes and no text is ever drawn over an illustration.

`main.ts` (Node 22, standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output`). The picture is
deterministic: every run produces the same bytes.

Sources: Reuters, AP, AFP, Al Jazeera, Dawn, USGS, IGP, ESA, ABC, CNN.
Illustrations are original flat drawings.
