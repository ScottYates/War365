#!/usr/bin/env python
"""Score news candidates for War365 release-log relevance using MiniMax.

The daily scan collects up to 20 candidate events from public news feeds.
This tool submits them to MiniMax, which scores each one for how well it
would work as an entry in the War365 release log, and prints the ranking.
The top 3 by score are the ones the job writes up and ships.

Relevance here means one thing: would this event earn a line in a release
history that reads like a git log of product launches? A new theatre going
GA, a ceasefire deployed or collapsing, a regime change, a first-of-kind
strike, a record displacement figure, an attack on critical infrastructure.
A routine strike, a diplomatic statement, an aid appeal and a general's
opinion are all patch notes, and patch notes do not belong in this log.

Credentials come from the environment on a server (MINIMAX_API_KEY) and from
the local MiniMax Code runtime on a desktop. See tools/minimax_client.py.
Nothing is written to disk and no credential is ever printed.

Usage:

    python tools/rank_candidates.py --file candidates.json
    python tools/rank_candidates.py --file candidates.json --top 5
    python tools/rank_candidates.py --file candidates.json --dry-run
    python tools/rank_candidates.py --file candidates.json --out ranking.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from minimax_client import MiniMaxError, call, parse_json_array  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
LOG_PATH = REPO / "commits.js"
MAX_CANDIDATES = 20

# The theatres the release log already covers. A candidate outside this list
# is not automatically out, but it has to be a very big deal to displace
# something that is already in the log.
THEATRES = [
    "Ukraine and Russia",
    "Gaza and Israel",
    "Lebanon and Hezbollah",
    "Iran",
    "Sudan",
    "Syria",
    "Myanmar",
    "Sahel",
    "Yemen",
    "Haiti",
    "Korea",
    "India and Pakistan",
]

RUBRIC = """\
Score each candidate event for RELEVANCE to the War365 release log.

The log is a fake git history of a SaaS product whose releases are real
conflicts. Every entry documents one discrete, datable, notable moment, told
in the voice of an enterprise engineering team: a new theatre going GA, a
ceasefire deployed or one collapsing, a regime or leadership change, a
first-of-kind strike or operation, a record displacement or casualty figure,
an attack on supply chains or critical infrastructure, a peace deal signed or
a peace deal collapsing.

Score high (80-100) for:
- a discrete moment with a date and a place that the log could ship as a
  release, especially one that changes the shape of a theatre
- a first-of-kind event, a record, a regime change, a ceasefire breaking
- something in one of the theatres the log already tracks

Score low (0-40) for:
- a routine strike, a routine offensive, a battlefield update
- a diplomatic statement, a warning, a threat, a negotiation
- an aid appeal, a humanitarian report, a statistic with no new event
- a court ruling, an election result, a court appearance
- a commentary, an analysis, an anniversary retrospective
- anything already covered by the log

Score in the middle (41-79) for genuine but narrower events: a notable
single incident, a significant escalation inside an existing theatre, or an
event with a strong hook that is not quite a release.

A candidate with no verifiable date, no place, or no specific event is a
patch note. Score it low.

Be strict. A run that ships nothing is a healthy run. Do not inflate scores
to fill the quota."""


def existing_subjects() -> list[str]:
    """Subjects already in the log, so the scorer can judge fit and overlap."""
    try:
        src = LOG_PATH.read_text(encoding="utf-8")
    except OSError:
        return []
    return re.findall(r'^\s*subject:\s*"(.+?)",\s*$', src, re.M)


def build_prompt(candidates: list[dict], subjects: list[str]) -> str:
    blocks = []
    for c in candidates:
        blob = f"{c['id']}. {c.get('date', '?')} | {c.get('theatre', '?')} | {c.get('title', '')}\n"
        blob += f"   {c.get('summary', '')}\n"
        text = (c.get("text") or "").strip()
        if text:
            blob += f"   source text: {text[:1200]}\n"
        blob += f"   {c.get('url', '')}"
        blocks.append(blob)
    listing = "\n".join(blocks)
    prior = "\n".join(f"- {s}" for s in subjects) if subjects else "(none)"
    return (
        f"CANDIDATES ({len(candidates)}):\n\n{listing}\n\n"
        f"ENTRIES ALREADY IN THE LOG (do not score anything that duplicates one "
        f"of these):\n\n{prior}\n\n"
        "Score every candidate. Reply with JSON only, no prose, in exactly "
        "this shape:\n"
        '[{"id": "c01", "score": 87, "reason": "one line, under 20 words"}]\n'
        "The id must match the candidate id exactly. Include every candidate."
    )


def load_candidates(path: str) -> list[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"error: cannot read candidates from {path}: {exc}")
    if isinstance(data, dict):
        data = data.get("candidates", [])
    if not isinstance(data, list) or not data:
        raise SystemExit(f"error: {path} holds no candidates")

    cands = []
    for i, c in enumerate(data, 1):
        if not isinstance(c, dict):
            continue
        cands.append(
            {
                "id": str(c.get("id") or f"c{i:02d}"),
                "date": c.get("date", ""),
                "theatre": c.get("theatre", ""),
                "title": c.get("title", c.get("headline", "")),
                "summary": c.get("summary", ""),
                "text": c.get("text", ""),
                "url": c.get("url", c.get("link", "")),
            }
        )
    if len(cands) > MAX_CANDIDATES:
        print(
            f"note: {len(cands)} candidates supplied, scoring the first "
            f"{MAX_CANDIDATES}.",
            file=sys.stderr,
        )
        cands = cands[:MAX_CANDIDATES]
    return cands


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", required=True, help="candidates JSON file")
    ap.add_argument("--top", type=int, default=3, help="how many to mark as selected")
    ap.add_argument("--model", default=None, help="provider/model override")
    ap.add_argument("--timeout", type=int, default=300, help="request timeout seconds")
    ap.add_argument("--dry-run", action="store_true", help="print the prompt, do not call")
    ap.add_argument("--out", default=None, help="write the full ranking to this JSON file")
    args = ap.parse_args()

    candidates = load_candidates(args.file)
    prompt = build_prompt(candidates, existing_subjects())

    if args.dry_run:
        print(f"candidates: {len(candidates)}")
        print()
        print(prompt)
        return 0

    print(f"scoring {len(candidates)} candidates with MiniMax ...")
    try:
        text = call(RUBRIC, prompt, model=args.model, timeout=args.timeout)
    except MiniMaxError as exc:
        raise SystemExit(f"error: {exc}")

    scores = []
    for item in parse_json_array(text):
        if not isinstance(item, dict):
            continue
        cid = item.get("id")
        try:
            score = float(item.get("score"))
        except (TypeError, ValueError):
            continue
        if cid is None:
            continue
        scores.append(
            {
                "id": str(cid),
                "score": max(0.0, min(100.0, score)),
                "reason": str(item.get("reason", "")).strip(),
            }
        )
    if not scores:
        raise SystemExit("error: no usable scores in the model response")

    by_id = {c["id"]: c for c in candidates}
    for s in scores:
        s["candidate"] = by_id.get(s["id"], {})
    scores.sort(key=lambda s: s["score"], reverse=True)

    print()
    print(f"{'rank':<5}{'id':<6}{'score':<8}headline")
    for i, s in enumerate(scores, 1):
        mark = "*" if i <= args.top else " "
        head = s["candidate"].get("title", "")
        print(f"{mark}{i:<4}{s['id']:<6}{s['score']:<8.1f}{head[:74]}")
        if s["reason"]:
            print(f"{'':<19}{s['reason']}")

    print()
    print(f"top {args.top} selected: " + ", ".join(s["id"] for s in scores[: args.top]))

    if args.out:
        Path(args.out).write_text(
            json.dumps({"ranking": scores}, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"full ranking written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
