#!/usr/bin/env python
"""Score news candidates for War365 release-log relevance using MiniMax.

The daily news scan collects up to 20 candidate events from the public web.
This tool submits them to MiniMax, which scores each one for how well it
would work as an entry in the War365 release log, and prints the ranking.
The top 3 by score are the ones the job writes up and ships.

Relevance here means one thing: would this event earn a line in a release
history that reads like a git log of product launches? A new theatre going
GA, a ceasefire deployed or collapsing, a regime change, a first-of-kind
strike, a record displacement figure, an attack on critical infrastructure.
A routine strike, a diplomatic statement, an aid appeal and a general's
opinion are all patch notes, and patch notes do not belong in this log.

Credentials come from the local MiniMax Code runtime, the same place the
agent itself authenticates from. Nothing is written to disk and no token is
ever printed. Stdlib only, on purpose: the runtime has no httpx, and this
tool has to run unattended.

Usage:

    python tools/rank_candidates.py --file candidates.json
    python tools/rank_candidates.py --file candidates.json --top 5
    python tools/rank_candidates.py --file candidates.json --dry-run
    python tools/rank_candidates.py --file candidates.json --model minimax/MiniMax-M3.1-Flash
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

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


def data_dir() -> Path:
    for var in ("__MAVIS_PARENT_DATA_DIR", "MINIMAX_DATA_DIR"):
        val = os.environ.get(var)
        if val:
            return Path(val)
    return Path.home() / ".minimax"


def read_config() -> tuple[str, str]:
    """Return (base_url, default_model) from the runtime config."""
    path = Path(os.environ.get("MINIMAX_CONFIG", data_dir() / "config.yaml"))
    if not path.exists():
        raise SystemExit(
            f"error: MiniMax config not found at {path}.\n"
            "       The scorer needs the provider baseURL from it."
        )
    text = path.read_text(encoding="utf-8")
    m = re.search(r"baseURL:\s*(\S+)", text)
    if not m:
        raise SystemExit(f"error: no baseURL in {path}")
    base = m.group(1).strip("'\"")
    dm = re.search(r"defaultModel:\s*(\S+)", text)
    model = dm.group(1).strip("'\"") if dm else "minimax/MiniMax-M3.1-Flash"
    return base, model


def read_token() -> str:
    """Return the runtime access token used to authorize LLM calls."""
    path = Path(
        os.environ.get(
            "MINIMAX_RUNTIME_AUTH", data_dir() / "local-runtime.auth.json"
        )
    )
    if not path.exists():
        raise SystemExit(
            f"error: runtime auth not found at {path}.\n"
            "       Fall back to scoring with a subagent, or sign in to the "
            "MiniMax Code runtime."
        )
    try:
        auth = json.loads(path.read_text(encoding="utf-8")).get("auth", {})
    except (ValueError, OSError) as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}")
    token = auth.get("accessToken") or ""
    if not token:
        raise SystemExit(f"error: no accessToken in {path}")
    return token


def _post(url: str, token: str, body: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=body.pop("_timeout", 300)) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise _HttpError(exc.code, detail) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"error: cannot reach MiniMax: {exc.reason}")


class _HttpError(Exception):
    def __init__(self, code: int, detail: str):
        super().__init__(f"HTTP {code}: {detail}")
        self.code = code
        self.detail = detail


def call_minimax(
    base_url: str,
    model: str,
    system: str,
    prompt: str,
    timeout: int,
    thinking: bool = False,
    max_tokens: int = 16000,
) -> str:
    """Call the provider and return the assistant text.

    Thinking is off by default because scoring 20 candidates is a
    classification job. MiniMax-M3.1-Flash refuses to run without adaptive
    thinking, so if the model rejects thinking.type=disabled the call is
    retried with the model's own default and a bigger output budget.
    """
    token = read_token()
    body = {
        "model": model.split("/", 1)[-1],
        "max_tokens": max_tokens,
        "temperature": 0,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    url = base_url.rstrip("/") + "/messages"

    if not thinking:
        body["thinking"] = {"type": "disabled"}
    try:
        data = _post(url, token, dict(body, _timeout=timeout))
    except _HttpError as exc:
        if "thinking" not in exc.detail.lower():
            raise SystemExit(f"error: MiniMax returned {exc}")
        print(
            "note: model requires adaptive thinking, retrying with it enabled.",
            file=sys.stderr,
        )
        body.pop("thinking", None)
        body["max_tokens"] = max(max_tokens, 32000)
        try:
            data = _post(url, token, dict(body, _timeout=timeout))
        except _HttpError as exc2:
            raise SystemExit(f"error: MiniMax returned {exc2}") from exc2

    if isinstance(data, dict) and isinstance(data.get("content"), list):
        # MiniMax returns reasoning blocks alongside the answer. Some blocks
        # carry a "thinking" key and no "type" at all, so match on the text
        # field rather than on the type discriminator.
        text = "".join(
            b.get("text", "")
            for b in data["content"]
            if isinstance(b, dict) and isinstance(b.get("text"), str)
        )
        if text.strip():
            return text
        blocks = [sorted(b.keys()) for b in data["content"] if isinstance(b, dict)]
        raise SystemExit(
            "error: no text block in the response.\n"
            f"       content block keys: {blocks}\n"
            f"       raw: {json.dumps(data)[:400]}"
        )
    raise SystemExit(f"error: unexpected response shape: {json.dumps(data)[:300]}")


def parse_scores(text: str) -> list[dict]:
    """Pull the JSON array of scores out of the model response."""
    fenced = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    blob = fenced.group(1) if fenced else text
    start = blob.find("[")
    end = blob.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise SystemExit(
            "error: the model did not return a JSON array.\n"
            f"       raw response was:\n{text[:800]}"
        )
    try:
        data = json.loads(blob[start : end + 1])
    except ValueError as exc:
        raise SystemExit(f"error: model returned invalid JSON: {exc}")
    if not isinstance(data, list):
        raise SystemExit("error: model returned JSON that is not an array")

    scores = []
    for item in data:
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
    return scores


def existing_subjects() -> list[str]:
    """Subjects already in the log, so the scorer can judge fit and overlap."""
    try:
        src = LOG_PATH.read_text(encoding="utf-8")
    except OSError:
        return []
    return re.findall(r'^\s*subject:\s*"(.+?)",\s*$', src, re.M)


def build_prompt(candidates: list[dict], subjects: list[str]) -> str:
    listing = "\n".join(
        f"{c['id']}. {c.get('date', '?')} | {c.get('theatre', '?')} | {c.get('headline', '')}\n"
        f"   {c.get('summary', '')}\n"
        f"   {c.get('url', '')}"
        for c in candidates
    )
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
                "headline": c.get("headline", ""),
                "summary": c.get("summary", ""),
                "url": c.get("url", ""),
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
    ap.add_argument(
        "--thinking",
        action="store_true",
        help="let the model reason before answering (off by default)",
    )
    ap.add_argument("--dry-run", action="store_true", help="print the prompt, do not call")
    ap.add_argument("--out", default=None, help="write the full ranking to this JSON file")
    args = ap.parse_args()

    candidates = load_candidates(args.file)
    base_url, default_model = read_config()
    model = args.model or default_model
    prompt = build_prompt(candidates, existing_subjects())

    if args.dry_run:
        print(f"model: {model}")
        print(f"url:   {base_url.rstrip('/')}/messages")
        print(f"candidates: {len(candidates)}")
        print()
        print(prompt)
        return 0

    print(f"scoring {len(candidates)} candidates with {model} ...")
    text = call_minimax(base_url, model, RUBRIC, prompt, args.timeout, thinking=args.thinking)
    scores = parse_scores(text)

    by_id = {c["id"]: c for c in candidates}
    for s in scores:
        s["candidate"] = by_id.get(s["id"], {})
    scores.sort(key=lambda s: s["score"], reverse=True)

    print()
    print(f"{'rank':<5}{'id':<6}{'score':<8}headline")
    for i, s in enumerate(scores, 1):
        mark = "*" if i <= args.top else " "
        head = s["candidate"].get("headline", "")
        print(f"{mark}{i:<4}{s['id']:<6}{s['score']:<8.1f}{head[:74]}")
        if s["reason"]:
            print(f"{'':<19}{s['reason']}")

    print()
    print(f"top {args.top} selected: " + ", ".join(s["id"] for s in scores[: args.top]))

    if args.out:
        Path(args.out).write_text(
            json.dumps({"model": model, "ranking": scores}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"full ranking written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
