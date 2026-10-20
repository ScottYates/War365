#!/usr/bin/env python
"""Commit log maintenance for the War365 release history.

The release log in commits.js is a list of fake git commits that each document
one real-world conflict event. It is hand-written prose, so it needs a tool
that can validate an entry before it lands and prove the site still renders
after it does. This is that tool.

Subcommands:

    check    validate commits.js: parses as JS, schema, chronological order,
             duplicate hashes and subjects, conventional-commit prefix.
             Reports pre-existing style problems as warnings, never as
             failures, so it can gate a commit without blocking on history.

    add      insert one entry, given as JSON, at the end of the list.
             Validates the entry first and refuses it if anything is wrong.
             Writes transactionally: the file is restored if the result fails
             to parse.

    verify   serve the site, load it in a real browser, and assert the log
             renders, the row count matches the data, and nothing errored.

    list     print the log as a table, newest first. For eyeballing what is
             already covered before adding something.

Everything is Python 3 + Playwright, same as test/verify.py. The browser is
used to parse commits.js rather than a regex, because the file is JavaScript
and a regex is not a JavaScript parser.

Usage:

    python tools/commitlog.py check
    python tools/commitlog.py list
    python tools/commitlog.py add --file entry.json
    python tools/commitlog.py add --file entry.json --dry-run
    python tools/commitlog.py verify
"""

import argparse
import datetime
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(REPO, "commits.js")

# The prefixes app.js can colour a dot for. A subject outside this set still
# renders, it just falls back to the green feat dot.
PREFIXES = ("feat", "fix", "chore", "docs", "refactor", "perf", "test", "build", "ci")

SUBJECT_RE = re.compile(r"^([a-z]+)(?:\(([^)]*)\))?: (.+)$")
HASH_RE = re.compile(r"^[0-9a-f]{7}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"https?://\S+")

REQUIRED = ("hash", "date", "author", "authorEmail", "subject", "body")
OPTIONAL = ("tag", "headline", "summary", "breaking", "chips")


class Failure(Exception):
    """Something the operator needs to fix."""


# ---------------------------------------------------------------- playwright


def _playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "playwright is not installed. Run: pip install -r test/requirements.txt\n"
            "         then: python -m playwright install chromium"
        )
    return sync_playwright


def parse_log(path=LOG_PATH):
    """Parse commits.js with a real JS engine and return the commit list.

    Raises Failure if the file does not parse. A syntax error here is the
    failure mode that matters most, so it is never approximated with a regex.
    """
    src = open(path, encoding="utf-8").read()
    pw = _playwright()
    with pw() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.set_content("<!doctype html><html><body></body></html>")
            try:
                page.add_script_tag(content=src)
            except Exception as exc:
                raise Failure(f"commits.js does not parse: {exc}") from exc
            if errors:
                raise Failure("commits.js threw while loading: " + "; ".join(errors))
            data = page.evaluate("() => window.WAR365_COMMITS")
        finally:
            browser.close()

    if not isinstance(data, list):
        raise Failure("window.WAR365_COMMITS is not an array")
    return data


# ---------------------------------------------------------------- validation


def validate_entry(entry, existing, today=None):
    """Return a list of problems with a candidate entry. Empty means good."""
    problems = []

    if not isinstance(entry, dict):
        return ["entry is not a JSON object"]

    for key in REQUIRED:
        if key not in entry:
            problems.append(f"missing required field: {key}")

    unknown = set(entry) - set(REQUIRED) - set(OPTIONAL)
    if unknown:
        problems.append("unknown field(s): " + ", ".join(sorted(unknown)))

    h = entry.get("hash", "")
    if not isinstance(h, str) or not HASH_RE.match(h):
        problems.append(f"hash must be 7 lowercase hex chars, got {h!r}")
    elif any(c.get("hash") == h for c in existing):
        problems.append(f"duplicate hash: {h}")

    d = entry.get("date", "")
    if not isinstance(d, str) or not DATE_RE.match(d):
        problems.append(f"date must be YYYY-MM-DD, got {d!r}")
    else:
        try:
            when = datetime.date.fromisoformat(d)
        except ValueError:
            problems.append(f"date is not a real date: {d!r}")
        else:
            if today is not None and when > today + datetime.timedelta(days=1):
                problems.append(f"date is in the future: {d!r}")
            last = existing[-1].get("date") if existing else None
            if last:
                try:
                    if when < datetime.date.fromisoformat(last):
                        problems.append(
                            f"date {d} is before the last entry ({last}); "
                            "entries are appended newest-last, not inserted"
                        )
                except ValueError:
                    pass

    for key in ("author", "authorEmail"):
        val = entry.get(key, "")
        if not isinstance(val, str) or not val.strip():
            problems.append(f"{key} must be a non-empty string")
    email = entry.get("authorEmail", "")
    if isinstance(email, str) and email.strip() and not EMAIL_RE.match(email):
        problems.append(f"authorEmail is not an email address: {email!r}")

    subject = entry.get("subject", "")
    if not isinstance(subject, str) or not subject.strip():
        problems.append("subject must be a non-empty string")
    else:
        m = SUBJECT_RE.match(subject)
        if not m:
            problems.append(
                "subject must be a conventional commit, e.g. 'feat(scope): text', got "
                f"{subject!r}"
            )
        elif m.group(1) not in PREFIXES:
            problems.append(
                f"subject prefix {m.group(1)!r} is not one of: {', '.join(PREFIXES)}"
            )
        lowered = subject.strip().lower()
        if any(c.get("subject", "").strip().lower() == lowered for c in existing):
            problems.append(f"duplicate subject: {subject!r}")

    body = entry.get("body")
    if not isinstance(body, list) or not body:
        problems.append("body must be a non-empty list of strings")
    else:
        for i, line in enumerate(body):
            if not isinstance(line, str):
                problems.append(f"body[{i}] is not a string")
        if all(isinstance(x, str) for x in body):
            if not URL_RE.search("\n".join(body)):
                problems.append(
                    "body must cite the real event as a URL, on a 'Ref: ' line. "
                    "A release log nobody can check is a rumour."
                )

    for key in ("headline", "summary"):
        if key in entry and not isinstance(entry[key], str):
            problems.append(f"{key} must be a string")
    if "breaking" in entry and not isinstance(entry["breaking"], bool):
        problems.append("breaking must be true or false")
    if "chips" in entry:
        if not isinstance(entry["chips"], list) or not all(
            isinstance(c, str) for c in entry["chips"]
        ):
            problems.append("chips must be a list of strings")

    # New entries are ASCII only. The existing file carries some typographic
    # characters from before this rule; those are reported by check() as
    # warnings, not fixed here.
    for key, val in entry.items():
        if isinstance(val, str):
            bad = [c for c in val if ord(c) > 127]
            if bad:
                problems.append(
                    f"{key} contains non-ASCII characters: "
                    + ", ".join(sorted({repr(c) for c in bad}))
                )
        if key == "body" and isinstance(val, list):
            for i, line in enumerate(val):
                if isinstance(line, str):
                    bad = [c for c in line if ord(c) > 127]
                    if bad:
                        problems.append(
                            f"body[{i}] contains non-ASCII characters: "
                            + ", ".join(sorted({repr(c) for c in bad}))
                        )

    return problems


def check_existing(commits):
    """Integrity problems in the log as it stands. Empty means good."""
    problems = []
    warnings = []

    if not commits:
        return ["the log is empty"], warnings

    seen_hashes = {}
    seen_subjects = {}
    prev_date = None

    for i, c in enumerate(commits):
        where = f"entry {i}"
        for key in REQUIRED:
            if key not in c:
                problems.append(f"{where}: missing {key}")
        h = c.get("hash")
        if h in seen_hashes:
            problems.append(f"{where}: duplicate hash {h} (also entry {seen_hashes[h]})")
        else:
            seen_hashes[h] = i
        s = c.get("subject", "").strip().lower()
        if s in seen_subjects:
            problems.append(
                f"{where}: duplicate subject {c.get('subject')!r} "
                f"(also entry {seen_subjects[s]})"
            )
        else:
            seen_subjects[s] = i
        d = c.get("date")
        if d and DATE_RE.match(str(d)):
            if prev_date and str(d) < prev_date:
                problems.append(f"{where}: date {d} is earlier than the entry before it")
            prev_date = str(d)
        else:
            problems.append(f"{where}: bad date {d!r}")
        sub = c.get("subject", "")
        if sub and not SUBJECT_RE.match(sub):
            warnings.append(f"{where}: subject is not a conventional commit: {sub!r}")
        elif sub:
            m = SUBJECT_RE.match(sub)
            if m and m.group(1) not in PREFIXES:
                warnings.append(f"{where}: unusual prefix {m.group(1)!r}")
        body = c.get("body", "")
        if isinstance(body, str):
            for ch in sorted({ch for ch in body if ord(ch) > 127}):
                warnings.append(
                    f"{where}: body contains non-ASCII {ch!r} (pre-existing)"
                )
        if not URL_RE.search(str(body)):
            warnings.append(f"{where}: body cites no source URL (pre-existing)")

    return problems, warnings


# ---------------------------------------------------------------- rendering


def render_entry(entry, indent="  "):
    """Render a commit as JavaScript matching the style of commits.js."""
    head = []
    for key in ("hash", "date", "author", "authorEmail", "tag", "subject"):
        if entry.get(key) is not None:
            head.append(f"{indent}  {key}: {json.dumps(entry[key])},")

    body_lines = ",\n".join(f"{indent}    {json.dumps(line)}" for line in entry["body"])
    body = f"{indent}  body: [\n{body_lines}\n{indent}  ].join(\"\\n\")"

    meta = []
    for key in ("headline", "summary"):
        if entry.get(key) is not None:
            meta.append(f"{indent}  {key}: {json.dumps(entry[key])},")
    if "breaking" in entry:
        meta.append(f"{indent}  breaking: {'true' if entry['breaking'] else 'false'},")
    if "chips" in entry:
        chips = ", ".join(json.dumps(c) for c in entry["chips"])
        meta.append(f"{indent}  chips: [{chips}]")

    # body sits after subject and before the hero-card metadata, which is
    # where commits.js puts it.
    members = head + ([body + ","] if meta else [body]) + meta

    return "\n".join([f"{indent}{{"] + members + [f"{indent}}}"])


def insert_entry(src, entry):
    """Return src with entry appended to the commit array."""
    idx = src.rindex("\n];")
    brace = idx - 1
    if src[brace] != "}":
        raise Failure(f"unexpected commits.js layout at offset {brace}")
    rendered = render_entry(entry)
    return src[: brace + 1] + ",\n" + rendered + src[brace + 1:]


# ---------------------------------------------------------------- commands


def cmd_check(args):
    commits = parse_log()
    problems, warnings = check_existing(commits)
    print(f"parsed {len(commits)} commits from commits.js")
    for w in warnings:
        print(f"  warn  {w}")
    if problems:
        for p in problems:
            print(f"  FAIL  {p}")
        print(f"\n{len(problems)} problem(s) found")
        return 1
    print("ok: schema, order and uniqueness all clean")
    return 0


def cmd_list(args):
    commits = parse_log()
    for c in reversed(commits):
        print(f"{c.get('date')}  {c.get('hash')}  {c.get('subject')}")
    print(f"\n{len(commits)} commits")
    return 0


def cmd_add(args):
    raw = open(args.file, encoding="utf-8").read()
    try:
        entry = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise Failure(f"{args.file} is not valid JSON: {exc}") from exc

    commits = parse_log()
    problems = validate_entry(entry, commits, today=datetime.date.today())
    if problems:
        print("refusing to add this entry:")
        for p in problems:
            print(f"  - {p}")
        return 1

    src = open(LOG_PATH, encoding="utf-8").read()
    new_src = insert_entry(src, entry)

    if args.dry_run:
        print("dry run, nothing written. The entry would be appended as:")
        print()
        print(render_entry(entry))
        return 0

    # Transactional. Write it, prove it still parses, roll back if not.
    with open(LOG_PATH, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_src)
    try:
        after = parse_log()
    except Failure:
        with open(LOG_PATH, "w", encoding="utf-8", newline="") as fh:
            fh.write(src)
        raise Failure(
            "the rewritten file did not parse; commits.js has been restored"
        )
    if len(after) != len(commits) + 1:
        with open(LOG_PATH, "w", encoding="utf-8", newline="") as fh:
            fh.write(src)
        raise Failure(
            f"expected {len(commits) + 1} commits after insert, got {len(after)}; "
            "commits.js has been restored"
        )

    print(f"added {entry['hash']} ({entry['date']}) to commits.js")
    print(f"  {entry['subject']}")
    print(f"  {len(commits)} -> {len(after)} commits")
    return 0


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def cmd_verify(args):
    port = _free_port()
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}/"
    try:
        deadline = time.time() + 15
        while True:
            if server.poll() is not None:
                raise Failure("the test server exited early")
            try:
                with urllib.request.urlopen(url, timeout=2) as r:
                    if r.status == 200:
                        break
            except (urllib.error.URLError, OSError):
                pass
            if time.time() > deadline:
                raise Failure("the test server never came up")
            time.sleep(0.2)

        commits = parse_log()
        pw = _playwright()
        problems = []
        with pw() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                errs, failed = [], []
                page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.on("requestfailed", lambda r: failed.append(r.url))
                page.goto(url, wait_until="networkidle")

                rows = page.locator(".commit-row").count()
                if rows != len(commits):
                    problems.append(
                        f"{rows} commit rows rendered but the log holds {len(commits)}"
                    )
                newest = commits[-1].get("subject", "")
                if newest and newest not in page.content():
                    problems.append(f"the newest commit is not in the page: {newest!r}")
                if errs:
                    problems.append("console errors: " + "; ".join(errs[:3]))
                if failed:
                    problems.append("failed requests: " + "; ".join(failed[:3]))
            finally:
                browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    if problems:
        for p_ in problems:
            print(f"  FAIL  {p_}")
        return 1
    print(f"ok: {len(commits)} commits render, no console errors")
    return 0


# ---------------------------------------------------------------- cli


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="validate commits.js").set_defaults(fn=cmd_check)
    sub.add_parser("list", help="print the log, newest first").set_defaults(fn=cmd_list)
    sub.add_parser("verify", help="load the site and prove the log renders").set_defaults(
        fn=cmd_verify
    )

    p_add = sub.add_parser("add", help="append one entry from a JSON file")
    p_add.add_argument("--file", required=True, help="path to the entry JSON")
    p_add.add_argument("--dry-run", action="store_true", help="validate and show, do not write")
    p_add.set_defaults(fn=cmd_add)

    args = ap.parse_args()
    try:
        return args.fn(args)
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
