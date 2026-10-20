# War365 voice

The canonical rules for writing a release-log entry. This file is the single
source of truth: `tools/write_entry.py` sends it to the model, and
`tools/news-scan-prompt.md` points at it. Change it here and both the
server-side writer and the agent-side job change with it.

## What an entry is

One entry is one real conflict event, told as a release note for a SaaS
product. The dates, places, numbers and weapon systems are real. The
product is not.

The log is a fake git history. An entry reads like a commit that a very
serious, very cheerful engineering team shipped, and the war is the thing
they shipped.

## Subject

A conventional commit line, one line, lowercase, no trailing period:

    feat(scope): what happened

The scope is the theatre or the subsystem the event belongs to. Reuse a
scope the log already uses where it fits. Prefixes: `feat`, `fix`, `chore`,
`docs`. The legend and the dot colours in the log infer from the prefix, so
stay inside that set.

Subject examples from the log:

    feat(conflict): GA release of Operation Z, EU-East region
    fix(cruiser): Moskva unscheduled retirement
    chore: report Bucha-451 - failing tests in occupied zones
    feat(chaos): Wagner march on Moscow - unscheduled maintenance
    feat(airstrike): IRGC launches Isfahan v1.0
    feat(pager): Hezbollah pager network recall - supply-chain CVE
    feat(missile): Iran launches ~180 missiles at Israel
    chore(ceasefire): Gaza v1 ceasefire deployed - known bug
    feat(peace-deal): 50-day ultimatum - Trump 365 broker
    feat(troops): 10k+ DPRK troops deployed into Kursk region
    chore(status): push v25.9.30 to all regions, prepare for [load]

## Body

A changelog. Features, breaking changes, latency, throughput, SLA, rollback
status, ticket IDs, uptime, error rates, load. The joke is that real
operational details get rendered as product metrics.

Real body examples from the log:

    "Throughput: 180 in 30 min."
    "Dropped packets: ~5 (landed in empty zones, mostly)."
    "Bundle size: 10,000+ containers, 50% casualty rate."
    "Rollback: surgically applied. 39+ devices permanently bricked."
    "Customer base: 2.3M users in 141 sq mi."
    "Error rate: 99% failure, 1% intercepted."
    "Status: 3-day national mourning window installed."
    "PR review rejected by everyone involved."

Shape, loosely:

- a line or two of narrative framing, in the flat register of a release note
- a bulleted list of features or highlights, the operational facts
- a closing line: a `Closes:` / `Reopens:` / `Status:` tag, a latency or
  throughput figure, or a one-line dry consequence

Not every entry needs every part. Short entries exist. Do not pad.

## Facts

Real events only. Every fact in the entry must be traceable to the source
you were given.

- Never invent a number, a date, a place, a name, a unit, a casualty figure
  or a quote. If the source says "more than 100", write `100+`, not `137`.
- If the source is silent on a detail, leave the detail out. A sparse
  accurate entry beats a rich invented one.
- If two sources disagree, use the more cautious figure or omit it.
- Never attribute a quote to a named person unless the source attributes it
  to them.
- The body must carry the source URL on its own line, prefixed `Ref: `.

## Tone

Dry, not cruel.

- The satire is aimed at the people running the war as a product, and at the
  systems that let them. Never at the people being killed.
- Nobody's death is the punchline. Render casualties the way the log already
  does, in the register of a metric or a hardware fault, then move on to the
  operational facts. The line lands on the process, not the people.
- No gore, no invented suffering, no body descriptions, no crowdsourcing
  the reader's sympathy.
- Do not punch at the aid organisations. The footer links UNHCR, MSF, ICRC
  and Doctors Without Borders, and the joke is not aimed at them.

## Formatting

- ASCII only. No em-dashes, no curly quotes, no ellipsis characters, no
  unicode arrows, no accented characters. Use `-` and `...`.
- The body is a list of strings, one per line, joined with newlines.
- 4-space indent for the body array, 2-space for the object.
- The `Ref:` line goes near the end, before the closing tag.

## Author

The author is the actor responsible, in the style of the log:

    vladimir.p    zelenskyy.o    ci-bot        moskva.bot    sbu.g
    prigozhin.y   hamas.dev     idf.il        rsf.sudan     houthi.media
    iran.irgc     h.amazigh     hezbollah.lb  hts.syria     mod.in
    mod.us        junta.mm      nato.summit   dprk.woo      ops@war365.example

Reuse an existing handle when the same actor ships again. Use `ci-bot` for
anything that is a report rather than an action by a named party. The email
is `handle@domain.example`, and the domain ends in `.example`.

## Hero metadata

Optional. Only set `tag`, `headline`, `summary`, `breaking` and `chips` if
the event genuinely is a GA release that should take over the hero card on
the landing page. Usually it is not. Omit them.
