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
```

## Deploy

Drop the directory on any static host. That's it.

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