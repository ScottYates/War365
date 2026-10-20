"""Collect candidate events for the War365 release log from public RSS feeds.

The server has no agent, so the news has to arrive by feed rather than by a
model's web_search. This pulls the configured feeds, keeps the items inside
the window, and writes them out in the shape tools/rank_candidates.py reads.

Where it can reach the article, it also pulls a readable slice of the body
text. The writer downstream is grounded in that text, so a thin headline
becomes a well-sourced entry and a blocked site degrades to the feed
description rather than to nothing.

Stdlib only. No third-party feed library, no headless browser.

Usage:

    python tools/collect_candidates.py --days 7 --out candidates.json
    python tools/collect_candidates.py --check-feeds
    python tools/collect_candidates.py --days 3 --max 20 --no-fetch
"""

import argparse
import datetime
import gzip
import io
import json
import re
import sys
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

REPO = Path(__file__).resolve().parent.parent
DEFAULT_FEEDS = REPO / "tools" / "feeds.txt"
USER_AGENT = "War365/1.0 (release-log bot; +https://github.com/ScottYates/War365)"

# Rough theatre guess, used only as a hint for the writer. The model refines
# it. Ordered: first match wins.
THEATRE_KEYWORDS = [
    ("Ukraine and Russia", r"ukrain|russia|kremlin|moscow|kyiv|kharkiv|donetsk|putin|zelensk|luhn|bryansk|belgorod|sverdlov|kirovohrad|nato"),
    ("Gaza and Israel", r"gaza|israel|hamas|idf|west bank|settler|rafah|netanyahu|jerusalem|tel aviv|palestin"),
    ("Lebanon and Hezbollah", r"lebanon|hezbollah|beirut|litani|nahariyya|nabatieh|jemzine|hermel"),
    ("Iran", r"iran|iranian|tehran|irgc|khamenei|isfahan|bushehr|aftab|persian gulf|strait of hormuz"),
    ("Sudan", r"sudan|khartoum|darfur|omdurman|el fasher|nyala|wau|kordofan|darfur"),
    ("Syria", r"syria|syrian|damascus|aleppo|idlib|homs|raqqa|assad|nusra"),
    ("Myanmar", r"myanmar|burma|rakhine|shan|junta|rohingya|mandalay|thonpyi|naypyidaw"),
    ("Sahel", r"mali|burkina|niger|chad|sahel|jnim|wagner|bamako|niamey|tillaberi"),
    ("Yemen", r"yemen|yemeni|houthi|sanaa|hodeidah|marib|taiz|shabwa|aden|saudi arabia"),
    ("Haiti", r"haiti|port-au-prince|gang|msc|m viv ansanm"),
    ("Korea", r"korea|north korea|pyongyang|dprk|kim jong"),
    ("India and Pakistan", r"india|pakistan|new delhi|islamabad|kashmir|india-pakistan"),
]

CONFLICT_RE = re.compile(
    r"strike|struck|attack|attacked|shelling|shelled|bomb|bombed|missile|drone|airstrike|"
    r"troops|offensive|ceasefire|truce|coup|regime|killed|dead|death|casualt|"
    r"invasion|war\b|conflict|clash|shelling|occupation|withdraw|talks|hostage|"
    r"jihadi|militia|rebel|army|troop|frontline|front line|artillery|drone",
    re.I,
)


class _TextExtractor(HTMLParser):
    """Pull readable text out of an article page."""

    SKIP = {"script", "style", "noscript", "svg", "head", "nav", "footer", "aside"}
    BLOCK = {
        "p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6",
        "section", "article", "blockquote", "tr", "figcaption",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts)
        raw = re.sub(r"[ \t\r\f\v]+", " ", raw)
        lines = [ln.strip() for ln in raw.split("\n")]
        out = [ln for ln in lines if ln]
        # Drop the boilerplate block that sits above the story.
        joined = "\n".join(out)
        for marker in ("Sign up", "Subscribe", "Newsletter", "Copyright", "All rights reserved"):
            idx = joined.find(marker)
            if 0 < idx < 400:
                joined = joined[idx:]
                break
        return joined.strip()


def fetch(url: str, timeout: int = 25) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            data = gzip.GzipFile(fileobj=io.BytesIO(data)).read()
        return data


def parse_date(raw: str):
    if not raw:
        return None
    raw = raw.strip()
    try:
        return parsedate_to_datetime(raw).date()
    except (TypeError, ValueError):
        pass
    try:
        return datetime.datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(raw[: len(fmt) + 4].strip(), fmt).date()
        except ValueError:
            continue
    return None


def _text_of(node, names):
    for name in names:
        found = node.find(name)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def parse_feed(raw: bytes):
    """Return [(title, link, summary, date)] from an RSS or Atom payload."""
    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError:
        return []

    items = []
    tag = root.tag.split("}")[-1].lower()

    if tag == "feed":
        ns = "{http://www.w3.org/2005/Atom}"
        for entry in root.findall(f"{ns}entry") or root.findall("entry"):
            title = _text_of(entry, [f"{ns}title", "title"])
            link = ""
            for link_el in entry.findall(f"{ns}link") + entry.findall("link"):
                href = link_el.get("href")
                if href:
                    link = href
                    break
            summary = _text_of(entry, [f"{ns}summary", f"{ns}content", "summary", "content"])
            when = _text_of(entry, [f"{ns}updated", f"{ns}published", "updated", "published"])
            items.append((title, link, summary, parse_date(when)))
        return items

    for item in root.iter():
        if item.tag.split("}")[-1].lower() != "item":
            continue
        title = _text_of(item, ["title"])
        link = _text_of(item, ["link", "guid"])
        if not link:
            for link_el in item.iter():
                if link_el.tag.split("}")[-1].lower() == "link" and link_el.get("href"):
                    link = link_el.get("href")
                    break
        summary = _text_of(item, ["description", "summary", "encoded"])
        when = _text_of(item, ["pubDate", "published", "date"])
        items.append((title, link, summary, parse_date(when)))
    return items


def guess_theatre(text: str) -> str:
    for theatre, pattern in THEATRE_KEYWORDS:
        if re.search(pattern, text, re.I):
            return theatre
    return "Unassigned"


def load_feeds(path: Path):
    feeds = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            url, theatre = line.split("|", 1)
            feeds.append((url.strip(), theatre.strip()))
        else:
            feeds.append((line, ""))
    return feeds


def check_feeds(path: Path):
    print(f"{'ok':<4}{'items':<7}{'feed'}")
    bad = 0
    for url, theatre in load_feeds(path):
        try:
            items = parse_feed(fetch(url, timeout=20))
        except Exception as exc:
            print(f"FAIL  -      {url}  ({type(exc).__name__}: {exc})")
            bad += 1
            continue
        print(f"ok    {len(items):<7}{url}  [{theatre or 'auto'}]")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--feeds", default=str(DEFAULT_FEEDS), help="feed list file")
    ap.add_argument("--days", type=int, default=7, help="how far back to look")
    ap.add_argument("--max", type=int, default=20, help="candidate ceiling")
    ap.add_argument("--out", default=None, help="write candidates JSON here")
    ap.add_argument("--no-fetch", action="store_true", help="skip article body fetches")
    ap.add_argument("--check-feeds", action="store_true", help="just test the feed list")
    args = ap.parse_args()

    feed_path = Path(args.feeds)
    if not feed_path.exists():
        raise SystemExit(f"error: feed list not found: {feed_path}")

    if args.check_feeds:
        return check_feeds(feed_path)

    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=args.days)

    buckets = []
    seen = set()
    for url, feed_theatre in load_feeds(feed_path):
        try:
            items = parse_feed(fetch(url, timeout=25))
        except Exception as exc:
            print(f"note: {url} failed ({type(exc).__name__}), skipping", file=sys.stderr)
            buckets.append([])
            continue
        keep = []
        for title, link, summary, when in items:
            if not title or not link:
                continue
            key = link.split("?")[0]
            if key in seen:
                continue
            seen.add(key)
            if when and when < cutoff:
                continue
            if when and when > today:
                continue
            blob = f"{title} {summary}"
            theatre = feed_theatre or guess_theatre(blob)
            if theatre == "Unassigned":
                # Outside every theatre the log covers. Not a candidate.
                continue
            keep.append(
                {
                    "title": title,
                    "link": link,
                    "url": link,
                    "summary": re.sub(r"\s+", " ", summary)[:1200],
                    "date": (when or today).isoformat(),
                    "theatre": theatre,
                    "source": url,
                    "signal": bool(CONFLICT_RE.search(blob)),
                }
            )
        buckets.append(keep)

    # Interleave the feeds so a chatty one cannot take the whole pool, and
    # prefer items that read like conflict over items that merely name a
    # country. The ranker is the real relevance filter; this just keeps the
    # pool from being 20 Guardian headlines.
    def interleave(selected_only: bool):
        out = []
        idx = 0
        while True:
            progressed = False
            for bucket in buckets:
                if idx >= len(bucket):
                    continue
                if selected_only and not bucket[idx]["signal"]:
                    continue
                out.append(bucket[idx])
                progressed = True
            if not progressed:
                break
            idx += 1
        return out

    pool = interleave(True)
    if len(pool) < args.max:
        pool += [c for c in interleave(False) if c not in pool]
    pool = pool[: args.max]
    pool.sort(key=lambda c: (c["date"], c["signal"]), reverse=True)

    for i, cand in enumerate(pool, 1):
        cand["id"] = f"c{i:02d}"
        if not args.no_fetch:
            try:
                page = fetch(cand["link"], timeout=20).decode("utf-8", "replace")
                parser = _TextExtractor()
                parser.feed(page)
                text = parser.text()[:4000]
                if len(text) > 400:
                    cand["text"] = text
            except Exception:
                pass  # feed description is the fallback

    print(f"collected {len(pool)} candidates from {len(load_feeds(feed_path))} feeds")
    for cand in pool:
        have = "full" if cand.get("text") else "headline only"
        src = cand["source"].split("/")[2]
        print(
            f"  {cand['id']} {cand['date']} [{cand['theatre']}] ({have}, {src}) "
            f"{cand['title'][:64]}"
        )

    if args.out:
        Path(args.out).write_text(
            json.dumps({"candidates": pool}, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"wrote {args.out}")
    else:
        json.dump({"candidates": pool}, sys.stdout, indent=2, ensure_ascii=False)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
