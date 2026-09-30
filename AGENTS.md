# War365

> "Folks, it's not WW3, no matter what anyone says. After WW2, we moved away from official release versions and switched to a mandatory lifetime subscription model with endless updates instead."
>
> &mdash; @ztwang87
>
> "War365, now with Copilot."
>
> &mdash; @tino.munic

A satirical single-page web site that riffs on the Microsoft 365 / Copilot meme by recasting real-world conflicts as if they were SaaS releases. The release history is the centrepiece: a fake git commit log that documents real events from 2022 to today, in the voice of an enterprise engineering team.

This project lives at `C:\Users\Scott\.mavis\agents\coder\workspace\war365\`. It is its own root — not a subdirectory of `email-notetoself`.

## Stack

Plain HTML, CSS, JavaScript. No framework, no build.

```
index.html    # page structure
styles.css    # Microsoft-365 marketing aesthetic
commits.js    # fake release-history data (25 commits)
app.js        # render + filter the log
main.go       # dev server (stdlib only, serves this directory)
scripts/      # Linux helpers: build, start, stop, restart, update
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
A failed chown is a warning, not a build failure — root-owned 0755 already
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

## Conventions

- Append new entries to `commits.js` (chronological order, newest at the end).
- Use conventional commit prefixes: `feat`, `fix`, `chore`, `docs`. The legend and dot colors in the commit log infer from the prefix.
- Real events only — keep the satire tethered to facts. Cite the real event in the body so future-me can verify.
- The footer links to UNHCR, MSF, ICRC and Doctors Without Borders. Keep those; the joke doesn't punch at the aid orgs.

## What is real, what isn't

Nothing on this page is real. The conflicts it documents are. Please donate.