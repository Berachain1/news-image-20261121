[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Berachain1/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Berachain1/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# The World in One Day — Saturday 21 November 2026

Entry for the make.fun bounty
[news-image-20261121](https://make.fun/bounty/news-image-20261121):
one image summing up the world's news on 21 November 2026.

`entry.png` (1024×1024) is a newspaper front page drawn by
`paint_front.py` (Pillow, no network): 36 stories across 6 regions —
the coalition downing three Houthi missiles over Riyadh, BepiColombo
reaching Mercury after eight years, COP31 running into overtime in
Antalya, Rutte in Warsaw, the Kryvyi Rih strike, and 23 more briefs —
plus a numbers ticker, a world map with numbered pins, and a date
check naming what was kept out as other days' news.

Every word sits on solid cream or white with dark navy ink, so the
page stays legible at thumbnail size; the three hero pictures live in
their own boxes and no text is ever drawn over an illustration.

`main.ts` (Node 22, standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output`). The picture is
deterministic: every run produces the same bytes.

Sources: Reuters, AP, AFP, BBC, ESA, JAXA, UN, European Commission.
Illustrations are original flat drawings.
