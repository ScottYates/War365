# War365

> "Folks, it's not WW3, no matter what anyone says. After WW2, we moved away from official release versions and switched to a mandatory lifetime subscription model with endless updates instead."
>
> - @ztwang87
>
> "War365, now with Copilot."
>
> - @tino.munic

A satirical single-page web site that riffs on the Microsoft 365 / Copilot meme by recasting real-world conflicts as if they were SaaS releases. The release history is the centerpiece: a fake git commit log that documents real events from 2022 to today, in the voice of an enterprise engineering team.

This project lives at `C:\Users\Scott\.mavis\agents\coder\workspace\war365\`. It is its own root, not a subdirectory of `email-notetoself`.

## Stack

Plain HTML, CSS, JavaScript. No framework, no build.

```
index.html    # page structure
styles.css    # Microsoft-365 marketing aesthetic
commits.js    # fake release-history data (the release log)
app.js        # render + filter the log
main.go       # dev server (stdlib only, serves this directory)
scripts/      # Linux helpers: build, start, stop, restart, update
deploy/       # War365.service + War365.logrotate
test/         # layout audit (Python + Playwright), not shipped with the site
tools/        # release-log maintenance (Python + Playwright), not shipped
```

## Run

Open `index.html` in any browser, or serve from this directory:

- `python -m http.server` (built-in)
- `go run .` (bundled `main.go` dev server, default port `:8000`, override with `-addr=:8765`)

Server flags:

```
-addr=:8000        listen address
-log-format=text   text or json
-log-level=info    debug, info, warn, error
-log-file=         also append to this file, still mirrored to stdout
-quiet            suppress the per-request access log
```

Logs go to stdout via `log/slog`: one line per request with method, path,
status, bytes, `took_ms` and client IP. 5xx is logged at ERROR, the rest at
INFO. `SIGINT`/`SIGTERM` trigger a graceful drain (10s, matching
`TimeoutStopSec` in the unit) and log the shutdown.

With `-log-file`, the sink becomes `io.MultiWriter(file, stdout)`. The file is
opened `O_APPEND|O_CREATE|O_WRONLY`, never `O_TRUNC`, so a restart adds to the
existing log instead of wiping it, and each write is atomic so concurrent lines
cannot interleave. Parent directories are created on demand. The unit points
this at `/var/log/war365/access.log`; `deploy/War365.logrotate` rotates it.

On Linux, the scripts wrap the same server for long-running use:

```
scripts/build.sh     # compile bin/war365 (chowns it to war365 when run as root)
scripts/start.sh     # start in background, writes .war365.pid + .war365.log
scripts/stop.sh      # stop by pid, escalate to SIGKILL after 5s
scripts/restart.sh   # stop + build + start
scripts/update.sh    # git pull --ff-only + build + restart
```

`build.sh` hands `bin/war365` to the `war365` service account so the systemd
unit can execute it, but only when run as root *and* the account exists; local
dev builds just say so and move on. Override the account with `WAR365_USER`.
A failed chown is a warning, not a build failure. Root-owned 0755 already
satisfies the unit's needs.

Set `WAR365_ADDR` to change the listen address (default `:8000`). `start.sh`,
`stop.sh` and `restart.sh` are all idempotent. `update.sh` refuses to run with a
dirty working tree.

## Deploy

Drop the directory on any static host.

For a long-running Linux box, `deploy/War365.service` is a systemd unit that
assumes the repo lives at `/opt/War365`:

```
sudo useradd --system --no-create-home --shell /usr/sbin/nologin war365
sudo chown -R war365:war365 /opt/War365
sudo /opt/War365/scripts/build.sh
sudo cp deploy/War365.service /etc/systemd/system/war365.service
sudo systemctl daemon-reload && sudo systemctl enable --now war365
```

Override the port without editing the unit via `systemctl edit war365` and
setting `Environment=WAR365_ADDR=:9000`. Logs go to the journal
(`journalctl -u war365 -f`). The unit runs unprivileged and is hardened with
`ProtectSystem=strict` plus friends; it deliberately has no `SystemCallFilter`,
because restrictive seccomp allowlists break the Go runtime.

## Verifying a layout change

Any change to `styles.css` or `index.html` should be measured, not eyeballed:

```bash
python test/verify.py --serve          # both engines, 11 viewports, exits non-zero on failure
python test/verify.py --serve --ab HEAD~1   # prove the change actually mattered
```

`test/README.md` explains what each check exists for. The short version: a
page that was never broken and a page that is now fixed look identical in a
screenshot, so `--ab` is the part that carries the evidence. It swaps
`index.html`, `styles.css` and `app.js` for an older revision, measures, and
restores them in a `finally` block.

## Adding to the release log

`commits.js` is the source of truth for the release history. Do not hand-edit
it. Use the tool, which validates the entry and refuses bad input:

```bash
python tools/commitlog.py list              # what is already covered
python tools/commitlog.py check              # data integrity gate
python tools/commitlog.py add --file e.json  # append one entry
python tools/commitlog.py add --file e.json --dry-run
python tools/commitlog.py verify             # the site still renders it
python tools/commitlog.py doctor             # does the toolchain work here
```

`add` refuses a wrong hash format, a duplicate hash or subject, a date
earlier than the last entry or in the future, a subject that is not a
conventional commit, a body with no source URL, and any non-ASCII character.
It writes transactionally: the file is restored if the result fails to parse.

The file is parsed with a real JavaScript engine (Chromium, via Playwright)
rather than a regex. The file is JavaScript, and a regex is not a JavaScript
parser.

That browser is a separate download from the package that drives it, and it
lands in a per-user cache. On the server it lives in
`/var/lib/war365/browsers`, and the unit points `PLAYWRIGHT_BROWSERS_PATH`
at that directory, because a browser installed as root lands in `/root/.cache`
where the service account cannot see it. `doctor` reports the paths and
proves a browser starts. The scan runs it before it spends a model call, so
a missing browser is one clear line rather than three stack traces.

`check` reports pre-existing style problems as warnings rather than failures,
so it can gate a commit without blocking on history. New entries are held to
the stricter rule.

### The news scan job

A scheduled job runs daily at 07:00 America/Chicago on the server. It scans
the public news feeds for real conflict events worth entries, has MiniMax
rank them, writes the winners in voice, verifies, commits and pushes to
`origin/master`.

The pipeline: collect up to 20 candidates, score them with MiniMax, write the
top 3 in voice, ship.

```bash
python tools/collect_candidates.py --days 3 --max 20 --out c.json
python tools/rank_candidates.py --file c.json --out ranking.json
python tools/write_entry.py --candidates c.json --candidate c01 --out e.json
```

`scripts/scan.sh` runs the whole thing, in that order, and then commits and
pushes. `deploy/War365-scan.service` and `deploy/War365-scan.timer` are the
systemd units. `scripts/install-scan.sh` installs all of it on a server and
asks for the MiniMax key. The key lives in `/etc/war365/minimax.env`,
root-owned and group-readable by `war365`. The README has the details.

The scorer sends the candidates, the subjects already in the log, and the
relevance rubric to MiniMax, and prints the ranking with the top 3 marked.
The rubric is the bar from "Conventions" below, written out as a scoring
instruction: a GA release, not a patch note.

The writer is given the voice rules from `tools/voice.md`, the candidate, and
the source text, and is told to use no fact that is not in the source. Its
output goes through the same validator as a hand-written entry, so a
malformed one is refused before it can reach the log.

Credentials come from `MINIMAX_API_KEY` in the environment on the server, and
from the local MiniMax Code runtime on a desktop. Nothing is written to disk
and no credential is ever printed. Stdlib only, because the runtime has no
`httpx` and this has to run unattended. If it cannot reach MiniMax the run
stops rather than falling back to picking candidates by eye.

No credential goes in the repository. The key lives in
`/etc/war365/minimax.env`, outside the checkout, root-owned and mode 0640.
`.githooks/pre-commit` refuses a commit that adds anything secret-shaped,
and `.gitignore` covers `*.env`, `*.pem`, `*.key` and the key files.

The full procedure for the agent-side job is `tools/news-scan-prompt.md`,
version-controlled here so it can be reviewed and edited without recreating
the job.

The job stops without touching the tree if the working tree is dirty or if
`git pull --ff-only` fails, so it can never stomp on work in progress. If
your local `master` is ahead of `origin/master` with unpushed commits, the
job does not push them for you: it stops and reports instead.

Only one writer at a time. The server job and the agent-side job both push to
`origin/master`, so do not run both against the same branch.

## Conventions

- Append new entries to `commits.js` (chronological order, newest at the end).
- Use conventional commit prefixes: `feat`, `fix`, `chore`, `docs`. The legend and dot colors in the commit log infer from the prefix.
- Real events only. Keep the satire tethered to facts. Cite the real event in the body so future-me can verify.
- The bar for an entry is a GA release, not a patch note. Qualifying: a new theatre, a ceasefire deployed or collapsing, a regime or leadership change, a first-of-kind strike, a record displacement figure, an attack on supply chains or critical infrastructure, a peace deal signed or collapsing. Not qualifying: a routine strike, a diplomatic statement, an aid appeal, a court ruling, an anniversary retrospective. This is the same rubric `tools/rank_candidates.py` scores against.
- Dry, not cruel. Render casualties the way the log already does, in the register of a metric or a hardware fault, then move on to the operational facts. The satire is aimed at the people running the war as a product, never at the people being killed. Nobody's death is the punchline.
- The footer links to UNHCR, MSF, ICRC and Doctors Without Borders. Keep those; the joke doesn't punch at the aid orgs.

## What is real, what isn't

Nothing on this page is real. The conflicts it documents are. Please donate.