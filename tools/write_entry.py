#!/usr/bin/env python
"""Write one War365 release-log entry from a ranked candidate.

The ranker decides which events are worth a release. This turns the winning
candidate into the entry itself: the subject, the body, the author, in the
voice of the log, grounded in the source text that was fetched with the
candidate.

The model is given the voice rules, the candidate, and the last few entries
as a reference. It is told, in as many words, that it may only use facts
present in the source. The result is then validated by the same rules
tools/commitlog.py applies, so a malformed entry is refused before it can
reach the log.

The hash is generated here, not by the model, so it is always 7 hex
characters and always unique.

Usage:

    python tools/write_entry.py --candidates c.json --candidate c01 --out e.json
    python tools/write_entry.py --candidates c.json --candidate c01 --dry-run
"""

import argparse
import json
import re
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from commitlog import EMAIL_RE, parse_log, validate_entry  # noqa: E402
from minimax_client import MiniMaxError, call, parse_json_object  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
VOICE_PATH = REPO / "tools" / "voice.md"

SYSTEM = """\
You write entries for War365, a satirical site that documents real conflicts
as if they were SaaS releases. The release history is a fake git log.

Here are the voice rules. Follow them exactly.

{voice}

---

Now write ONE entry for the candidate you are given.

Hard rules, in priority order:

1. Use only facts that appear in the CANDIDATE below. The candidate carries a
   headline, a summary, and usually a slice of the source article. If a
   number, a date, a place, a name, a unit or a quote is not in there, it
   does not go in the entry. Do not reason from what you know about the
   conflict. You do not know it. The candidate is the only source.
2. The body must contain the candidate URL on its own line, prefixed
   "Ref: ".
3. ASCII only. No em-dashes, no curly quotes, no unicode of any kind.
4. The body is a list of strings, one line each. Keep it between 5 and 14
   lines. A short body is fine. Do not pad it.
5. The subject is a conventional commit line: "feat(scope): what happened".
   Scope is the theatre or subsystem. One line, no trailing period.

Reply with JSON only, no prose, in exactly this shape:

{{"author": "houthi.media", "authorEmail": "ops@houthi.example", "subject": "feat(scope): short literal description", "body": ["line one", "", "line two"]}}

Do not include the hash, the date, or any hero metadata. Those are filled in
by the tool."""


def load_voice() -> str:
    if not VOICE_PATH.exists():
        raise SystemExit(f"error: voice rules not found at {VOICE_PATH}")
    return VOICE_PATH.read_text(encoding="utf-8")


def load_candidate(path: str, wanted: str) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"error: cannot read candidates from {path}: {exc}")
    if isinstance(data, dict):
        data = data.get("candidates", [])
    for c in data or []:
        if isinstance(c, dict) and str(c.get("id")) == wanted:
            return c
    raise SystemExit(f"error: no candidate with id {wanted} in {path}")


def reference_entries(commits: list[dict], count: int = 4) -> str:
    """The last few entries, oldest first, as a voice reference."""
    picks = commits[-count:] if len(commits) >= count else commits
    out = []
    for c in picks:
        out.append(f"    {c.get('date')}  {c.get('subject')}")
        body = c.get("body", "")
        if isinstance(body, str):
            for line in body.split("\n"):
                out.append(f"      {line}")
        out.append("")
    return "\n".join(out)


def build_prompt(candidate: dict, reference: str) -> str:
    blob = [
        f"CANDIDATE {candidate.get('id')}",
        f"date: {candidate.get('date')}",
        f"theatre: {candidate.get('theatre')}",
        f"headline: {candidate.get('title') or candidate.get('headline')}",
        f"url: {candidate.get('url') or candidate.get('link')}",
        "",
        "summary:",
        candidate.get("summary", ""),
    ]
    text = (candidate.get("text") or "").strip()
    if text:
        blob += ["", "source text:", text]
    else:
        blob += [
            "",
            "There is no source text beyond the summary. Use only what the "
            "summary states.",
        ]
    blob += [
        "",
        "ENTRIES ALREADY IN THE LOG (voice reference, and the bar for length "
        "and register). Do not duplicate any of them.",
        "",
        reference,
    ]
    return "\n".join(blob)


def new_hash(used: set[str]) -> str:
    while True:
        h = secrets.token_hex(4)[:7]
        if h not in used:
            return h


def clean_body(body) -> list[str]:
    if isinstance(body, str):
        body = [ln for ln in body.split("\n")]
    if not isinstance(body, list):
        return []
    out = []
    for line in body:
        if not isinstance(line, str):
            continue
        line = line.replace("\u2014", "-").replace("\u2013", "-")
        line = re.sub(r"[\u2018\u2019]", "'", line)
        line = re.sub(r"[\u201c\u201d]", '"', line)
        line = re.sub(r"\u2026", "...", line)
        if any(ord(c) > 127 for c in line):
            line = line.encode("ascii", "ignore").decode("ascii")
        out.append(line.rstrip())
    while out and not out[-1].strip():
        out.pop()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--candidates", required=True, help="candidates JSON file")
    ap.add_argument("--candidate", required=True, help="candidate id, e.g. c01")
    ap.add_argument("--out", default=None, help="write the entry JSON here")
    ap.add_argument("--model", default=None, help="provider/model override")
    ap.add_argument("--timeout", type=int, default=300, help="request timeout seconds")
    ap.add_argument("--dry-run", action="store_true", help="print the prompt, do not call")
    args = ap.parse_args()

    candidate = load_candidate(args.candidates, args.candidate)
    voice = load_voice()
    system = SYSTEM.replace("{voice}", voice)

    commits = parse_log()
    reference = reference_entries(commits)
    prompt = build_prompt(candidate, reference)

    if args.dry_run:
        print("=== SYSTEM ===")
        print(system)
        print()
        print("=== USER ===")
        print(prompt)
        return 0

    print(f"writing an entry for {args.candidate} ...")
    try:
        text = call(system, prompt, model=args.model, timeout=args.timeout)
    except MiniMaxError as exc:
        raise SystemExit(f"error: {exc}")

    try:
        draft = parse_json_object(text)
    except MiniMaxError as exc:
        raise SystemExit(f"error: {exc}")

    url = candidate.get("url") or candidate.get("link") or ""
    body = clean_body(draft.get("body"))
    if url and not any("Ref:" in ln for ln in body):
        body.append("")
        body.append(f"Ref: {url}")

    used_hashes = {c.get("hash") for c in commits}
    author = str(draft.get("author", "ci-bot")).strip() or "ci-bot"
    email = str(draft.get("authorEmail", "")).strip()
    if not EMAIL_RE.match(email):
        # The model gets the shape wrong often enough to be worth repairing
        # here. The log's own convention is ops@<handle>.example.
        email = f"ops@{author}.example"

    entry = {
        "hash": new_hash(used_hashes),
        "date": candidate.get("date"),
        "author": author,
        "authorEmail": email,
        "subject": str(draft.get("subject", "")).strip(),
        "body": body,
    }

    print(f"  {entry['hash']} {entry['date']} {entry['subject']}")
    for line in entry["body"]:
        print(f"    {line}")

    problems = validate_entry(entry, commits)
    if problems:
        print("refusing this entry:")
        for p in problems:
            print(f"  - {p}")
        return 1

    if args.out:
        Path(args.out).write_text(
            json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
