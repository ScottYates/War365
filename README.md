# War365

> "Folks, it's not WW3, no matter what anyone says. After WW2, we moved away from official release versions and switched to a mandatory lifetime subscription model with endless updates instead."
>
> &mdash; @ztwang87
>
> "War365, now with Copilot."
>
> &mdash; @tino.munic

A satirical single-page web site that riffs on the Microsoft 365 / Copilot meme by recasting real-world conflicts as if they were SaaS releases. The release history is the centrepiece: a fake git commit log that documents real events from 2022 to today, in the voice of an enterprise engineering team.

Nothing here is real. The conflicts it documents are. Please donate.

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
war365/
  index.html    # page structure
  styles.css    # Microsoft-365 marketing aesthetic
  commits.js    # fake release-history data
  app.js        # render + filter the log
  main.go       # dev server
  scripts/      # build, start, stop, restart, update (Linux)
  deploy/       # systemd unit (Linux)
```

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
sudo cp deploy/War365.logrotate /etc/logrotate.d/war365
sudo logrotate -d /etc/logrotate.d/war365   # dry run
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

The unit runs as `war365` with `ProtectSystem=strict` and friends, so it can
read the repo but not write to it. It has no `SystemCallFilter=` on purpose:
restrictive seccomp allowlists break the Go runtime, which needs a syscall set
that shifts between Go and kernel versions.

## Dev server scripts (Linux)

For long-running local use, the scripts wrap the Go server:

| Script | What it does |
| --- | --- |
| `scripts/build.sh` | Compiles `bin/war365`, chowns it to the service account |
| `scripts/start.sh` | Starts in background, writes `.war365.pid` / `.war365.log` |
| `scripts/stop.sh` | Stops by pid, escalates to `SIGKILL` after 5s |
| `scripts/restart.sh` | Stop, build, start |
| `scripts/update.sh` | `git pull --ff-only`, build, restart |

Set `WAR365_ADDR` to change the listen address (default `:8000`).

`build.sh` chowns `bin/war365` to the `war365` service account so the systemd
unit can execute it. That only happens when you build as root and the account
exists — on a dev box it just prints a note and leaves the binary alone. Set
`WAR365_USER` if you named the account something else.

```bash
./scripts/start.sh          # http://localhost:8000
tail -f .war365.log         # follow the log
./scripts/stop.sh
```

## Donate

- UNHCR &mdash; https://www.unhcr.org
- MSF / Doctors Without Borders &mdash; https://www.msf.org
- International Committee of the Red Cross &mdash; https://www.icrc.org