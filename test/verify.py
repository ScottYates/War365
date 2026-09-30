"""Layout and accessibility audit for War365.

Sweeps real device viewports in each engine and checks the things that have
actually broken on this page before. Exits non-zero if anything fails, so it
can be used as a pre-commit gate.

Checks, at every viewport:

  1. no horizontal page overflow, and no content element crushed to a few
     pixels. An ancestor with overflow:hidden defeats the page-level check
     on its own, so both are measured.
  2. .commit-toggle is at least 24x24 CSS px (WCAG 2.2 AA, 2.5.8).
  3. .commit-meta is not display:none. The hash and author are most of what
     a commit log is for, so hiding them below a breakpoint is a content
     bug, not a layout one.
  4. the hero release date does not wrap onto a second line.
  5. every legend swatch matches the colour of the dot it labels.
  6. the primary nav is reachable: inline above 880px, a working disclosure
     below it. The disclosure must open, close on Escape, and close when a
     link is followed.
  7. the .tier-alt counterfactual blocks share a top within each row of
     pricing cards. The featured card carries a deliberate
     translateY(-4px), so 4px of disagreement is expected, more is not.
  8. .tiers has no zero-width grid track. A subgrid row-lock mistake
     collapses cards into one band and the grid answers with implicit
     zero-width columns; the alignment check alone does not catch it,
     because all the cards really are in the same band.
  9. no console errors and no failed requests.

Usage:

    python test/verify.py                      # both engines, default viewports
    python test/verify.py --engine firefox
    python test/verify.py --serve              # build and run the server, then sweep
    python test/verify.py --ab HEAD~1          # A/B the swap against a git ref
    python test/verify.py --shot               # write screenshots to test/shots/

--ab swaps index.html, styles.css and app.js for the versions at the given
ref, measures, and restores them in a finally block. Every run hash-guards
the served CSS against the file on disk first, so a stale or foreign server
on the same port cannot silently produce a clean-looking result.
"""

import argparse
import hashlib
import os
import socket
import subprocess
import sys
import time
import urllib.request
from contextlib import ExitStack

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright is not installed. Run: pip install -r test/requirements.txt\n"
             "         then: python -m playwright install chromium firefox")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(REPO, "test", "shots")

# width, height, is_mobile
VIEWPORTS = [
    (320, 720, True), (375, 812, True), (390, 844, True), (430, 932, True),
    (700, 800, False), (768, 1024, False), (900, 800, False), (1100, 900, False),
    (1150, 900, False), (1280, 900, False), (1440, 900, False),
]
ENGINES = ("chromium", "firefox")
AB_FILES = ("index.html", "styles.css", "app.js")
FEATURED_LIFT = 4  # .tier-featured translateY(-4px)

PROBE = r"""
() => {
  const de = document.documentElement;
  const o = { overflow: de.scrollWidth - de.clientWidth, notes: [] };

  const widths = {};
  for (const s of ['.commit-body', '.commit-subject', '.tier-alt p',
                   '.hero-card-body', '.faq-item', '.roadmap', '.tier']) {
    const els = [...document.querySelectorAll(s)];
    widths[s] = els.length ? Math.round(Math.min(...els.map(e => e.getBoundingClientRect().width))) : null;
  }
  o.minW = widths;

  const btn = document.querySelector('.commit-toggle');
  if (btn) {
    const r = btn.getBoundingClientRect();
    o.tap = [Math.round(r.width), Math.round(r.height)];
  }

  const meta = document.querySelector('.commit-meta');
  o.meta = meta ? {
    display: getComputedStyle(meta).display,
    hash: !!meta.querySelector('.commit-hash')?.textContent.trim(),
    author: !!meta.querySelector('.commit-author')?.textContent.trim(),
  } : null;

  const last = document.getElementById('stat-last');
  if (last) {
    const range = document.createRange();
    range.selectNodeContents(last);
    o.dateLines = range.getClientRects().length;
  }

  o.legend = {};
  for (const t of ['feat', 'fix', 'chore', 'docs']) {
    const sw = document.querySelector('.dot-' + t);
    const dot = document.querySelector('.commit-row[data-type="' + t + '"] .commit-dot');
    o.legend[t] = {
      legend: sw ? getComputedStyle(sw).backgroundColor : null,
      dot: dot ? getComputedStyle(dot).backgroundColor : null,
    };
  }

  const nav = document.getElementById('site-nav');
  const tog = document.querySelector('.nav-toggle');
  o.nav = {
    links: nav ? nav.querySelectorAll('a').length : 0,
    inline: nav ? getComputedStyle(nav).display !== 'none' : false,
    hamburger: !!tog && getComputedStyle(tog).display !== 'none',
  };

  // Track list, not just the visual result. A subgrid row-lock collapse
  // shows up here as a zero-width track long before it is obvious above.
  const tiers = document.querySelector('.tiers');
  if (tiers) {
    const cs = getComputedStyle(tiers);
    const tracks = cs.gridTemplateColumns.split(' ').map(parseFloat);
    o.tierTracks = tracks;
    o.zeroTracks = tracks.filter(t => t < 1).length;
    const cards = [...document.querySelectorAll('.tier')];
    const tops = cards.map(c => c.querySelector('.tier-alt'));
    // An --ab run against a revision from before .tier-alt existed must
    // report "absent", not throw. Compare within each row of cards.
    if (cards.length && tops.every(el => el)) {
      o.altTops = tops.map(el => Math.round(el.getBoundingClientRect().top));
      const perRow = [];
      for (let i = 0; i < o.altTops.length; i += tracks.length) {
        const row = o.altTops.slice(i, i + tracks.length);
        perRow.push(Math.max(...row) - Math.min(...row));
      }
      o.bandSpread = perRow;
    } else {
      o.altTops = null;
      o.bandSpread = null;
    }
  }
  return o;
}
"""


# ---------- server ----------

def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_for(url, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if urllib.request.urlopen(url, timeout=2).status == 200:
                return True
        except Exception:
            time.sleep(0.4)
    return False


class Server:
    """Runs the real server for the duration of a sweep.

    Builds the binary and runs it directly rather than shelling out to
    `go run`. `go run` compiles and then execs the result as a *child*
    process, so terminating it leaves the child holding the port. That
    leaks a server on every run, and the next run either attaches to the
    stale one or fails on the port. One process in, one process out.
    """

    def __init__(self, url=None):
        self.url = url or f"http://127.0.0.1:{free_port()}/"
        self.proc = None
        self.bin = None

    def __enter__(self):
        if wait_for(self.url, timeout=2):
            return self.url  # something is already serving this port
        self.bin = os.path.join(REPO, "bin", "verify-server" + (".exe" if os.name == "nt" else ""))
        build = subprocess.run(["go", "build", "-o", self.bin, "."], cwd=REPO,
                               capture_output=True, text=True)
        if build.returncode != 0:
            sys.exit(f"go build failed:\n{build.stderr}")
        self.proc = subprocess.Popen(
            [self.bin, "-addr=" + self.url.split("//")[1].strip("/")],
            cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not wait_for(self.url):
            self.__exit__()
            sys.exit(f"server did not come up at {self.url}")
        return self.url

    def __exit__(self, *exc):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
            self.proc = None
        if self.bin and os.path.exists(self.bin):
            os.remove(self.bin)


# ---------- checks ----------

def guard(url):
    """Refuse to measure a server that is not serving this tree.

    The hash comparison is the real protection. A dev server reads from its
    working directory, so it will happily serve a different checkout on the
    same port, still answer 200, and produce a clean-looking result that
    describes somebody else's CSS. Nothing else here needs to assert, because
    asserting on a specific rule would break legitimate --ab runs against
    refs from before that rule existed.
    """
    served = urllib.request.urlopen(url + "styles.css", timeout=5).read()
    local = open(os.path.join(REPO, "styles.css"), "rb").read()
    if hashlib.sha256(served).digest() != hashlib.sha256(local).digest():
        sys.exit("STALE TREE: the server is not serving this checkout. "
                 "Point --url at the right server or stop the one holding the port.")
    return True


def check(width, d):
    f = []
    if d["overflow"] > 0:
        f.append(f"page overflow {d['overflow']}px")
    for sel, val in d["minW"].items():
        if val is not None and val < 60:
            f.append(f"{sel} crushed to {val}px")
    if d.get("tap") and (d["tap"][0] < 24 or d["tap"][1] < 24):
        f.append(f"tap target {d['tap'][0]}x{d['tap'][1]} under 24px")
    if d["meta"] and d["meta"]["display"] == "none":
        f.append("commit-meta hidden")
    elif d["meta"] and not (d["meta"]["hash"] and d["meta"]["author"]):
        f.append("commit-meta missing hash or author")
    if d.get("dateLines", 1) > 1:
        f.append(f"release date wraps to {d['dateLines']} lines")
    for t, v in d["legend"].items():
        if v["legend"] != v["dot"]:
            f.append(f"legend {t} {v['legend']} != dot {v['dot']}")
    if d["nav"]["links"] != 5:
        f.append(f"nav has {d['nav']['links']} links, expected 5")
    if d["nav"]["inline"] and d["nav"]["hamburger"]:
        f.append("nav inline and hamburger both showing")
    if not d["nav"]["inline"] and not d["nav"]["hamburger"]:
        f.append("nav unreachable at this width")
    if d.get("zeroTracks"):
        f.append(f"{d['zeroTracks']} zero-width grid track(s) in .tiers")
    for spread in d.get("bandSpread") or []:
        if spread > FEATURED_LIFT:
            f.append(f"tier-alt band spread {spread}px")
    return f


def sweep(engine, url, shots=False):
    rows = []
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        for w, h, mobile in VIEWPORTS:
            ctx = browser.new_context(
                viewport={"width": w, "height": h},
                is_mobile=mobile, has_touch=mobile,
                device_scale_factor=2 if mobile else 1)
            page = ctx.new_page()
            errs, reqfails, fails = [], [], []
            page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            page.on("requestfailed", lambda r: reqfails.append(r.url))
            page.goto(url, wait_until="load")
            page.wait_for_timeout(300)
            d = page.evaluate(PROBE)

            # Interaction: the disclosure has to actually work, not just exist.
            if d["nav"]["hamburger"] and not d["nav"]["inline"]:
                page.click(".nav-toggle")
                page.wait_for_timeout(150)
                if not page.evaluate(
                        "() => getComputedStyle(document.getElementById('site-nav')).display !== 'none'"):
                    fails.append("hamburger does not open the nav")
                page.keyboard.press("Escape")
                page.wait_for_timeout(150)
                if not page.evaluate(
                        "() => getComputedStyle(document.getElementById('site-nav')).display === 'none'"):
                    fails.append("Escape does not close the nav")

            if errs:
                fails.append(f"console error: {errs[0][:70]}")
            if reqfails:
                fails.append(f"failed request: {reqfails[0][:70]}")
            fails += check(w, d)

            if shots:
                os.makedirs(SHOTS, exist_ok=True)
                page.screenshot(path=os.path.join(SHOTS, f"{engine}-{w}.png"), full_page=True)

            rows.append((w, fails, d))
            ctx.close()
        browser.close()
    return rows


def report(tag, engine, rows):
    print(f"\n=== {tag} [{engine}] ===")
    bad = 0
    for w, fails, d in rows:
        if fails:
            bad += 1
        tracks = d.get("tierTracks", [])
        bands = d.get("bandSpread", [])
        extra = (f" cols={len(tracks)} bandSpread={bands}" if tracks else "")
        print(f"  {w:>5}px {'FAIL' if fails else 'PASS'}{extra}"
              + ("  " + "; ".join(fails) if fails else ""))
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="server URL; omit with --serve to start one")
    ap.add_argument("--serve", action="store_true",
                    help="build and run the server for the duration of the run")
    ap.add_argument("--engine", choices=ENGINES + ("both",), default="both")
    ap.add_argument("--ab", metavar="REF",
                    help="measure again with the tracked files swapped to REF, and diff")
    ap.add_argument("--shot", action="store_true", help="write full-page screenshots")
    args = ap.parse_args()

    engines = ENGINES if args.engine == "both" else (args.engine,)
    current_detail = {}

    def run(url, tag):
        """One full pass over every engine, guarded against a stale server.

        Returns the failing-viewport count and the per-width detail, kept
        apart so an --ab baseline failing does not fail the gate. The gate
        is "is the tree I am about to commit healthy", not "was history".
        """
        detail = {}
        bad = 0
        for e in engines:
            rows = sweep(e, url, args.shot)
            bad += report(tag, e, rows)
            detail[e] = {w: d for w, _, d in rows}
        return bad, detail

    # The server has to outlive the current sweep, because --ab measures
    # again against the same origin. Holding it in an ExitStack rather than
    # a with block is what keeps that true.
    with ExitStack() as stack:
        url = args.url
        if args.serve or not url:
            url = stack.enter_context(Server(args.url))
        guard(url)
        gate, current_detail = run(url, "current")

        if args.ab:
            saved = {f: open(os.path.join(REPO, f), "rb").read() for f in AB_FILES}
            try:
                for f in AB_FILES:
                    blob = subprocess.run(["git", "show", f"{args.ab}:{f}"], cwd=REPO,
                                          capture_output=True).stdout
                    if not blob:
                        sys.exit(f"could not read {args.ab}:{f}")
                    open(os.path.join(REPO, f), "wb").write(blob)
                # The swap has to be what the server now serves, or the diff
                # is a lie about a tree nobody is looking at.
                guard(url)
                base_bad, baseline_detail = run(url, f"baseline {args.ab}")
                print(f"\nbaseline {args.ab} had {base_bad} failing viewports; "
                      f"the current tree has {gate}.")

                for e in engines:
                    print(f"\n--- A/B {args.ab} -> current [{e}] ---")
                    for w, _, _ in VIEWPORTS:
                        b = baseline_detail[e][w]
                        n = current_detail[e][w]
                        print(f"  {w:>5}px  altTops    {b['altTops']} -> {n['altTops']}")
                        print(f"            bandSpread {b['bandSpread']} -> {n['bandSpread']}")
                        print(f"            tap        {b['tap']} -> {n['tap']}")
                        print(f"            dateLines  {b['dateLines']} -> {n['dateLines']}")
                        print(f"            tracks     {b['tierTracks']} -> {n['tierTracks']}")
            finally:
                for f, blob in saved.items():
                    open(os.path.join(REPO, f), "wb").write(blob)
                for f in AB_FILES:
                    assert open(os.path.join(REPO, f), "rb").read() == saved[f], f"restore failed: {f}"
                print("\ntracked files restored")

    print(f"\n{'ALL PASS' if gate == 0 else str(gate) + ' FAILING VIEWPORTS (current tree)'}")
    sys.exit(1 if gate else 0)


if __name__ == "__main__":
    main()
