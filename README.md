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

`deploy/war365.service` is a ready-made systemd unit that runs the Go server
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
sudo cp deploy/war365.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now war365
```

Check on it:

```bash
systemctl status war365     # is it up
journalctl -u war365 -f     # follow the log
curl -s localhost:8000 | head -5
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

The unit runs as `war365` with `ProtectSystem=strict` and friends, so it can
read the repo but not write to it. It has no `SystemCallFilter=` on purpose:
restrictive seccomp allowlists break the Go runtime, which needs a syscall set
that shifts between Go and kernel versions.

## Dev server scripts (Linux)

For long-running local use, the scripts wrap the Go server:

| Script | What it does |
| --- | --- |
| `scripts/build.sh` | Compiles `bin/war365` |
| `scripts/start.sh` | Starts in background, writes `.war365.pid` / `.war365.log` |
| `scripts/stop.sh` | Stops by pid, escalates to `SIGKILL` after 5s |
| `scripts/restart.sh` | Stop, build, start |
| `scripts/update.sh` | `git pull --ff-only`, build, restart |

Set `WAR365_ADDR` to change the listen address (default `:8000`).

```bash
./scripts/start.sh          # http://localhost:8000
tail -f .war365.log         # follow the log
./scripts/stop.sh
```

## Donate

- UNHCR &mdash; https://www.unhcr.org
- MSF / Doctors Without Borders &mdash; https://www.msf.org
- International Committee of the Red Cross &mdash; https://www.icrc.org