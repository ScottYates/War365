# Layout verification

`verify.py` is the audit used to check every CSS and layout change on this
site. It is a real tool rather than a pile of one-off scripts, because the
defects it catches are the kind that look fine in a screenshot and are
invisible in code review.

## Setup

```bash
pip install -r test/requirements.txt
python -m playwright install chromium firefox
```

Python only. There is no npm dependency and no build step.

## Run it

```bash
python test/verify.py --serve        # builds the server, sweeps, shuts it down
python test/verify.py --engine firefox
python test/verify.py --shot         # full-page screenshots into test/shots/
```

`--serve` compiles the binary and runs it directly rather than shelling out
to `go run`. `go run` execs its result as a child process, so terminating it
leaves the child holding the port, and every run leaks a server that the next
run then trips over.

Or against a server you already have running:

```bash
python test/verify.py --url http://127.0.0.1:8000/
```

Exit code is 0 only if every viewport passes, so it works as a pre-commit
gate.

## Prove a change mattered

`--ab` re-measures with the tracked files swapped for an older git revision
and prints the numbers either side. This is the part that matters: a page
that was never broken and a page that is now fixed can look identical, and
eyeballing cannot tell them apart.

```bash
python test/verify.py --serve --ab HEAD~1
```

It restores the files in a `finally` block, so an interrupted run still
leaves the working tree intact.

## What it checks

| # | Check | The bug it exists for |
| --- | --- | --- |
| 1 | Page overflow, plus width of content elements | An ancestor with `overflow: hidden` makes page-level overflow read 0 while the content inside is crushed to a few pixels. Both are measured. |
| 2 | `.commit-toggle` at least 24x24 CSS px | WCAG 2.2 AA 2.5.8 target size. The button once measured 61x22. |
| 3 | `.commit-meta` visible, carrying hash and author | Responsive-by-deletion: a `display: none` below a breakpoint silently removed the hash and author on every phone. |
| 4 | Hero release date on one line | It broke as `2026-` / `09-30` in the 881-1150px band, where the stats sat four across in a 410px column. |
| 5 | Legend swatch colour matches the dot it labels | `.dot-docs` was `#58a6ff` while the docs dot was `#8957e5`. No layout test can see this. |
| 6 | Nav reachable, and the disclosure opens and closes | `.topnav` was `display: none` under 880px with no replacement, so all five primary links were unreachable on a phone. Checks the click, Escape, and navigate-away behaviour. |
| 7 | `.tier-alt` tops share a row within each row of cards | `margin-top: auto` bottom-anchored each block, so taller text started higher and the four dashed rules were staggered by 156px. |
| 8 | No zero-width grid track in `.tiers` | A subgrid row-lock mistake collapses all four cards into one band and the grid answers with implicit zero-width columns. Check 7 still passes in that state, so this one exists to catch it. |
| 9 | No console errors, no failed requests | Catches broken scripts and missing assets that a screenshot of a rendered page hides. |

The featured pricing card carries a deliberate `translateY(-4px)`, so check 7
allows 4px of disagreement between cards and fails above it.

## Why Playwright and not a headless screenshot

`msedge --headless --screenshot --window-size=390,900` is not a 390px render.
Headless Edge enforces a roughly 492px minimum layout viewport, so it renders
492px wide and crops the result to 390. That produces both false alarms and
false confidence. This tool uses real device contexts instead, with
`is_mobile` and `has_touch` set under 700px so media queries and tap targets
are exercised the way a phone exercises them.

Every run hash-guards the served `styles.css` against the file on disk before
measuring anything, and exits if they differ. A dev server that reads from its
working directory will happily serve a different checkout on the same port,
still return 200, and produce a clean-looking result that describes somebody
else's CSS.
