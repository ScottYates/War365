# War365

> "Folks, it's not WW3, no matter what anyone says. After WW2, we moved away from official release versions and switched to a mandatory lifetime subscription model with endless updates instead."
>
> - @ztwang87
>
> "War365, now with Copilot."
>
> - @tino.munic

A satirical single-page web site that riffs on the Microsoft 365 / Copilot meme by recasting real-world conflicts as if they were SaaS releases. The release history is the centerpiece: a fake git commit log that documents real events from 2022 to today, in the voice of an enterprise engineering team.

Nothing here is real. The conflicts it documents are. Please donate to the victims.

## Stack

- Plain HTML, CSS, and JavaScript (no framework, no build).
- Open `index.html` in any browser, or serve with `python -m http.server`.
- A tiny Go dev server (`main.go`, stdlib only) is included: `go run .`.

## The Go dev server

```bash
go run .                    # http://localhost:8000
go run . -addr=:8765        # different port
go run . -quiet             # no per-request access log
go run . -log-format=json   # structured, for log shipping
```

| Flag | Default | Meaning |
| --- | --- | --- |
| `-addr` | `:8000` | listen address |
| `-log-format` | `text` | `text` or `json` |
| `-log-level` | `info` | `debug`, `info`, `warn`, `error` |
| `-log-file` | none | also append to this file (mirrored to stdout) |
| `-quiet` | off | suppress per-request access logs |

It logs one line per request via `log/slog` to stdout:

```
time=2026-09-30T13:29:42.558-05:00 level=INFO msg=request method=GET path=/ status=200 bytes=14359 took_ms=15 remote=127.0.0.1
```

5xx responses log at ERROR, everything else at INFO. `SIGINT`/`SIGTERM` start a
graceful drain (10s) and log the shutdown, which is what `systemctl stop` sends.

Add `-log-file=/path/to/access.log` to write the same lines to a file as well
as stdout. It appends: stop the server, start it again, and the earlier lines
are still there.

Serving is restricted to the project directory: `os.DirFS(".")` refuses any
path with parent-dir segments, so `..` traversal cannot escape upward.

## File layout

```
War365/
  index.html    # page structure
  styles.css    # Microsoft-365 marketing aesthetic
  commits.js    # fake release-history data
  app.js        # render + filter the log
  main.go       # dev server
  scripts/      # build, start, stop, restart, update, scan (Linux)
  deploy/       # systemd units + logrotate snippet (Linux)
  test/         # layout audit (Python + Playwright), not needed to serve
  tools/        # release-log pipeline (Python + Playwright), not needed to serve
```

Inside `tools/`:

| File | What it does |
| --- | --- |
| `commitlog.py` | validate, insert and render-check the log |
| `collect_candidates.py` | pull the news feeds, fetch article text |
| `rank_candidates.py` | score candidates with MiniMax, pick the top 3 |
| `write_entry.py` | write an entry in voice, grounded in the source |
| `minimax_client.py` | the MiniMax call, and where the credential comes from |
| `voice.md` | the voice rules, in one place |
| `feeds.txt` | the feed list |
| `news-scan-prompt.md` | the full procedure for the agent-side job |

## Adding an entry to the release log

`commits.js` holds the release history: one entry per real conflict event,
written in the voice of an enterprise engineering team. Do not hand-edit it.
`tools/commitlog.py` validates an entry and refuses bad input:

```bash
python tools/commitlog.py list              # what is already covered
python tools/commitlog.py check              # data integrity gate
python tools/commitlog.py add --file e.json  # append one entry
python tools/commitlog.py verify             # the site still renders it
python tools/commitlog.py doctor             # does the toolchain work here
```

`add` refuses a wrong hash format, a duplicate hash or subject, a date
earlier than the last entry, a subject that is not a conventional commit, a
body with no source URL, and any non-ASCII character. It writes
transactionally, restoring the file if the result fails to parse.

The file is parsed with a real JavaScript engine rather than a regex, because
the file is JavaScript. That engine is a browser Playwright downloads
separately from the package that drives it, so it lands in a per-user cache.
`doctor` reports where it is looking and whether one starts, which is the
first thing to check when the tooling will not run.

The voice rules live in `tools/voice.md`, in one place, so the writer and the
job cannot drift apart.

## The news scan job

A scheduled job scans the public news for real conflict events worth a
release-log entry, has MiniMax rank them, writes the winners in voice, and
ships them. It runs unattended on the server.

The pipeline, end to end:

| Step | Tool | What it does |
| --- | --- | --- |
| 1 | `collect_candidates.py` | Pulls the public news feeds, keeps the items that belong to a theatre the log covers, fetches the article text. Up to 20 candidates. |
| 2 | `rank_candidates.py` | Sends the candidates, the subjects already in the log and the relevance rubric to MiniMax. Prints the ranking, marks the top 3. |
| 3 | `write_entry.py` | Turns the winning candidates into entries, in voice, grounded in the source text. |
| 4 | `commitlog.py` | Validates, inserts, and proves the site still renders. |
| 5 | `scripts/scan.sh` | Wires it together, commits and pushes. |

The rubric is the bar: a GA release, not a patch note. A new theatre, a
ceasefire deployed or collapsing, a regime change, a first-of-kind strike, a
record displacement figure, an attack on critical infrastructure. A routine
strike, a diplomatic statement and an aid appeal are patch notes and score
low.

Nothing ships unless the top candidate beats `WAR365_SCAN_MIN_SCORE` (60 by
default). A day where nothing clears the bar is a normal day.

By hand:

```bash
export MINIMAX_API_KEY=...        # or source /etc/war365/minimax.env

python tools/collect_candidates.py --days 3 --max 20 --out /tmp/c.json
python tools/rank_candidates.py --file /tmp/c.json --out /tmp/r.json
python tools/write_entry.py --candidates /tmp/c.json --candidate c01 --out /tmp/e.json
python tools/commitlog.py add --file /tmp/e.json
python tools/commitlog.py check && python tools/commitlog.py verify
```

`scripts/scan.sh` does all of that in the right order and then commits and
pushes. It refuses to run if a tracked file has uncommitted changes, so it
cannot stomp on work in progress. An untracked file is reported and the run
carries on, because the scan only writes `commits.js`. On the server it is
the whole job:

```bash
sudo systemctl start war365-scan
journalctl -u war365-scan -f
```

The candidate list comes from `tools/feeds.txt`, one URL per line, with an
optional theatre after a `|`. Twenty-five feeds are configured and all of
them are checked by `python tools/collect_candidates.py --check-feeds`.

### Installing the news scan on the server

One command does the lot, including asking for your MiniMax key:

```bash
cd /opt/War365
sudo ./scripts/install-scan.sh
```

It is safe to re-run. Every step is skipped if it is already done, so it
doubles as the repair tool after a change. The full script is
`scripts/install-scan.sh`; this is what it does.

| Step | What it does |
| --- | --- |
| 1 | Checks the machine: root, git, ssh-keygen, systemd. |
| 2 | Makes sure the checkout is at `/opt/War365`, and marks it safe for git. |
| 3 | Creates the unprivileged `war365` account, `/etc/war365` and `/var/lib/war365`, and hands the checkout to the account so the scan can commit to it. |
| 4 | **Asks for the MiniMax API key**, hidden, and confirms it. |
| 5 | Writes `/etc/war365/minimax.env` from the template, root-owned, mode 0640. |
| 6 | Generates a write-enabled deploy key, records the github.com host key, and either adds the deploy key through the API or prints it for you to paste in. Points `origin` at SSH so the push uses it, then proves the key can push. |
| 7 | Creates a venv, installs Playwright and Chromium into `/var/lib/war365/browsers`, and proves a browser starts as the `war365` account, both on its own and inside the unit's sandbox. |
| 8 | Installs `war365-scan.service` and `war365-scan.timer`. |
| 9 | Enables the timer, and prints what to do next. |

Options:

```bash
sudo ./scripts/install-scan.sh --key KEY    # supply the key, do not prompt
sudo ./scripts/install-scan.sh --yes        # never prompt, fail if there is no key
sudo ./scripts/install-scan.sh --repo DIR    # checkout somewhere else
```

`MINIMAX_API_KEY` in the environment is used instead of prompting, and
`GITHUB_TOKEN`, if set, lets step 6 register the deploy key through the API
instead of printing it for you to paste in by hand.

#### The key

The scan calls the MiniMax API to rank the candidates and write the entries.
Get a key from the MiniMax platform:

- pay-as-you-go: <https://platform.minimax.io/user-center/basic-information/interface-key>
  (API Keys, Create new secret key)
- M Plan seat: <https://platform.minimax.io/user-center/payment/token-plan>
  (Billing, M Plan, Subscription Key)

Either one works. It is a long string, and it goes in exactly one place:

```
/etc/war365/minimax.env      MINIMAX_API_KEY=your-key-here
```

Root owns the file, the `war365` group can read it, and nobody else can:

```bash
sudo chown root:war365 /etc/war365/minimax.env
sudo chmod 0640 /etc/war365/minimax.env
```

The tooling never prints the key and never writes it to disk.
`deploy/war365-scan.env.example` documents every variable in the file, and
the install script writes the file from that template, so the two cannot
drift apart.

#### The push key

The scan commits and pushes its own work, so it needs a write-enabled deploy
key rather than a personal one. The install script generates it at
`/etc/war365/scan_key` and either registers it through the GitHub API or
prints the public key for you to add:

**Settings, Deploy keys, Add deploy key**, with **Allow write access**
ticked.

The install script points `origin` at SSH and sets `core.sshCommand` on the
checkout, so the deploy key is used by every git command in that repo, from
any shell and any user:

```bash
git -C /opt/War365 pull
git -C /opt/War365 status
```

The checkout belongs to the `war365` service account, so git refuses to work
in it for anyone else unless the directory is marked safe. The install
script does that for the account you ran it under. If you need it for
another user:

```bash
sudo -u otheruser git config --global --add safe.directory /opt/War365
```

Doing it by hand instead, the equivalent is:

```bash
git -C /opt/War365 config --local core.sshCommand \
  "ssh -i /etc/war365/scan_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/etc/war365/known_hosts -o StrictHostKeyChecking=accept-new"
```

Without that, a plain `git pull` in the checkout fails with a publickey or
host key error, because the key lives in `/etc/war365` and not in your own
`~/.ssh`.

#### The secret guard

The key never goes in the repository, and there is a commit hook that makes
sure it cannot. `.githooks/pre-commit` scans the lines a commit is adding and
refuses the commit if any of them look like a provider key, a JWT, a private
key block, a GitHub token, or a credential file. The install script turns it
on for the checkout:

```bash
git -C /opt/War365 config core.hooksPath .githooks
```

The hook is version-controlled here, so a fresh clone gets it. It is not
enough on its own, and `.gitignore` also covers `*.env`, `*.pem`, `*.key`,
`id_rsa*` and `scan_key*`. The key lives in `/etc/war365/minimax.env`, which
is outside the repository, root-owned, and mode 0640.

#### Doing it by hand

If you would rather not run the script, the same steps are:

```bash
# 1. the service account and the directories
sudo useradd --system --no-create-home --shell /usr/sbin/nologin war365
sudo mkdir -p /etc/war365 /var/lib/war365
sudo chown -R war365:war365 /opt/War365 /var/lib/war365

# 2. the credential
sudo cp deploy/war365-scan.env.example /etc/war365/minimax.env
sudo editor /etc/war365/minimax.env       # paste the key into MINIMAX_API_KEY
sudo chown root:war365 /etc/war365/minimax.env
sudo chmod 0640 /etc/war365/minimax.env

# 3. a write-enabled deploy key
sudo ssh-keygen -t ed25519 -N '' -f /etc/war365/scan_key
sudo ssh-keyscan github.com > /etc/war365/known_hosts
sudo chown root:war365 /etc/war365/scan_key /etc/war365/known_hosts
sudo chmod 0640 /etc/war365/scan_key
# add /etc/war365/scan_key.pub to the repo as a deploy key, write access ticked
git -C /opt/War365 remote set-url origin git@github.com:ScottYates/War365.git

# 4. python and playwright
# The browser goes in /var/lib/war365/browsers, not in root's cache. The
# unit points PLAYWRIGHT_BROWSERS_PATH at that directory, because the
# service account cannot read /root.
sudo apt-get install -y python3 python3-venv
sudo python3 -m venv /opt/War365/.venv
sudo /opt/War365/.venv/bin/pip install -r test/requirements.txt
sudo mkdir -p /var/lib/war365/browsers
sudo chown war365:war365 /var/lib/war365/browsers
sudo PLAYWRIGHT_BROWSERS_PATH=/var/lib/war365/browsers \
  /opt/War365/.venv/bin/python -m playwright install --with-deps chromium
sudo chown -R war365:war365 /var/lib/war365/browsers

# check it as the service account, which is where it has to run
sudo -u war365 env HOME=/var/lib/war365 \
  PLAYWRIGHT_BROWSERS_PATH=/var/lib/war365/browsers \
  /opt/War365/.venv/bin/python /opt/War365/tools/commitlog.py doctor

# 5. the units
sudo cp deploy/War365-scan.service /etc/systemd/system/war365-scan.service
sudo cp deploy/War365-scan.timer   /etc/systemd/system/war365-scan.timer
sudo chmod +x /opt/War365/scripts/scan.sh
sudo systemctl daemon-reload
sudo systemctl enable --now war365-scan.timer
```

Then run it once by hand before trusting the timer:

```bash
sudo systemctl start war365-scan
journalctl -u war365-scan -f
```

A successful run ends with `done: N entries added`. A run that finds nothing
worth shipping says so and changes nothing. Both are good outcomes. A run
that fails prints the reason it stopped, and the tree is left alone.

Check the schedule:

```bash
systemctl list-timers war365-scan.timer
```

#### When a run fails

The first thing the scan does, before it talks to the model, is check that
the browser the tooling needs actually starts. If it does not, the run stops
there with the reason, instead of failing three times with a stack trace.
The same check runs by hand:

```bash
sudo -u war365 env HOME=/var/lib/war365 \
  PLAYWRIGHT_BROWSERS_PATH=/var/lib/war365/browsers \
  /opt/War365/.venv/bin/python /opt/War365/tools/commitlog.py doctor
```

It prints the account it is running as, the directory it expects the browser
in, and the exact executable that is missing if it is missing. The usual
cause is a browser installed as root, which lands in `/root/.cache` where the
service account cannot see it. The fix is to install it into the directory
the unit points at:

```bash
sudo PLAYWRIGHT_BROWSERS_PATH=/var/lib/war365/browsers \
  /opt/War365/.venv/bin/python -m playwright install chromium
sudo chown -R war365:war365 /var/lib/war365/browsers
```

`scripts/install-scan.sh` does all of that, and then proves the browser
starts as the service account, both on its own and inside the unit's
sandbox, before it enables the timer. Re-running it is safe: it reuses the
key, the venv and the push key, and only redoes what is missing.

The timer fires daily at 07:00 America/Chicago, with up to ten minutes of
randomised delay so a fleet of boxes does not all hit the feeds and the model
at the same second. `Persistent=true` means a machine that was off at 07:00
runs the scan at the next boot instead of skipping the day.

Change the time without editing the unit:

```bash
sudo systemctl edit war365-scan.timer
# [Timer]
# OnCalendar=*-*-* 06:30:00 America/Chicago
```

#### Tuning

`/etc/war365/minimax.env` carries the knobs:

| Variable | Default | Meaning |
| --- | --- | --- |
| `MINIMAX_API_KEY` | none | required. The MiniMax credential. |
| `MINIMAX_BASE_URL` | `https://api.minimax.io/anthropic` | the endpoint |
| `MINIMAX_AUTH_STYLE` | `bearer` | `bearer` or `x-api-key` |
| `MINIMAX_MODEL` | `MiniMax-M3.1-Flash` | the ranking and writing model |
| `MINIMAX_EFFORT` | `low` | thinking effort |
| `WAR365_SCAN_TOP` | `3` | entries one run may add |
| `WAR365_SCAN_DAYS` | `3` | how far back to look |
| `WAR365_SCAN_MIN_SCORE` | `60` | score the top candidate must beat |

The environment file is read when the service starts, so a change lands on
the next run without restarting anything. If a key is repeated in the file,
the last value wins, so appending a setting overrides the template default.

### One writer, not two

The server job is the only thing that should write to `commits.js` on a
schedule. If you also run the agent-side job from the desktop runtime, pause
it first: two writers pushing to the same branch will collide, and the second
one will stop with a failed pull rather than clobber the first.

The agent-side job reads `tools/news-scan-prompt.md`, which carries the same
bar and the same voice rules, and is useful for writing an entry by hand when
the server is down.

## Checking a layout change

The site is plain HTML and CSS, so there is no build to break, but there is
plenty to break quietly at other widths. `test/verify.py` sweeps 11 viewports
in two engines and checks the things that have actually gone wrong here:

```bash
pip install -r test/requirements.txt
python -m playwright install chromium firefox

python test/verify.py --serve                # exits non-zero if anything fails
python test/verify.py --serve --ab HEAD~1    # prove the change mattered
```

It is worth the setup. Headless-browser screenshots are not a substitute:
`msedge --headless --screenshot --window-size=390,900` renders at a ~492px
minimum layout viewport and crops the image, which both invents breakage and
hides it. See `test/README.md` for what each check is there to catch.

## Deploy

Drop the directory on any static host. That's it.

### Running it as a service on Linux

`deploy/War365.service` is a ready-made systemd unit that runs the Go server
unprivileged from `/opt/War365`. From a clean machine:

```bash
# 1. Put the repo where the unit expects it
sudo git clone https://github.com/ScottYates/War365.git /opt/War365
cd /opt/War365

# 2. Create the unprivileged service account
sudo useradd --system --no-create-home --shell /usr/sbin/nologin war365
sudo chown -R war365:war365 /opt/War365

# 3. Build the binary (the unit refuses to start without it)
sudo /opt/War365/scripts/build.sh

# 4. Install and start the unit
# The destination name is deliberately lowercase. systemd takes the unit name
# from the installed filename, so copying to .../War365.service would register
# the unit as `War365` and every `systemctl ... war365` below would fail.
sudo cp deploy/War365.service /etc/systemd/system/war365.service
sudo systemctl daemon-reload
sudo systemctl enable --now war365
```

Check on it:

```bash
systemctl status war365     # is it up
journalctl -u war365 -f     # follow the log
tail -f /var/log/war365/access.log   # same lines, as a file
curl -s localhost:8000 | head -5
```

The unit sets `WAR365_LOG_FILE=/var/log/war365/access.log`. The file is opened
in append mode, so restarts add to it rather than truncating it, and every
line still reaches the journal. `LogsDirectory=war365` creates the directory
owned by the service account, which `ProtectSystem=strict` would otherwise
block. To rotate it:

```bash
sudo cp deploy/War365.logrotate /etc/logrotate.d/War365
sudo logrotate -d /etc/logrotate.d/War365   # dry run
```

Updating it later:

```bash
cd /opt/War365
sudo ./scripts/update.sh    # git pull --ff-only, build, restart
```

Change the port without editing the unit:

```bash
sudo systemctl edit war365
# [Service]
# Environment=WAR365_ADDR=:9000
sudo systemctl restart war365
```

Behind nginx, bind to loopback only:

```bash
# Environment=WAR365_ADDR=127.0.0.1:8000
```

If nginx is already writing access logs, you can turn off the server's own
access log to avoid duplicating every request:

```bash
sudo systemctl edit war365
# [Service]
# ExecStart=
# ExecStart=/opt/War365/bin/war365 -addr=${WAR365_ADDR} -quiet
```

The unit runs as the unprivileged `war365` service account with
`ProtectSystem=strict` and friends, so it can read the repo but not write to
it. It has no `SystemCallFilter=` on purpose: restrictive seccomp allowlists
break the Go runtime, which needs a syscall set that shifts between Go and
kernel versions.

## Dev server scripts (Linux)

For long-running local use, the scripts wrap the Go server:

| Script | What it does |
| --- | --- |
| `scripts/build.sh` | Compiles `bin/war365`, chowns it to the service account |
| `scripts/start.sh` | Starts in background, writes `.war365.pid` / `.war365.log` |
| `scripts/stop.sh` | Stops by pid, escalates to `SIGKILL` after 5s |
| `scripts/restart.sh` | Stop, build, start |
| `scripts/update.sh` | `git pull --ff-only`, build, restart |
| `scripts/scan.sh` | The news scan: collect, rank, write, verify, commit, push |
| `scripts/install-scan.sh` | Installs the news scan on this machine, and asks for the MiniMax key |

Set `WAR365_ADDR` to change the listen address (default `:8000`).

`build.sh` chowns `bin/war365` to the `war365` service account so the systemd
unit can execute it. That only happens when you build as root and the account
exists, so on a dev box it just prints a note and leaves the binary alone. Set
`WAR365_USER` if you named the account something else.

```bash
./scripts/start.sh          # http://localhost:8000
tail -f .war365.log         # follow the log
./scripts/stop.sh
```

`scan.sh` is the only script that writes to `commits.js`. It refuses to run
against a dirty tree, and it needs `MINIMAX_API_KEY` in the environment.

## Donate

- UNHCR &mdash; https://www.unhcr.org
- MSF / Doctors Without Borders &mdash; https://www.msf.org
- International Committee of the Red Cross &mdash; https://www.icrc.org
