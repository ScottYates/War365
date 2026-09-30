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
```

## Run

Open `index.html` in any browser, or serve with `python -m http.server` from this directory.

## Deploy

Drop the directory on any static host.

## Conventions

- Append new entries to `commits.js` (chronological order, newest at the end).
- Use conventional commit prefixes: `feat`, `fix`, `chore`, `docs`. The legend and dot colors in the commit log infer from the prefix.
- Real events only — keep the satire tethered to facts. Cite the real event in the body so future-me can verify.
- The footer links to UNHCR, MSF, ICRC and Doctors Without Borders. Keep those; the joke doesn't punch at the aid orgs.

## What is real, what isn't

Nothing on this page is real. The conflicts it documents are. Please donate.