# News scan procedure

This is the full procedure for the War365 news scan job. The scheduled task
carries only a short wrapper; this file is the procedure.

War365 documents real-world conflicts as if they were SaaS releases. The
centrepiece is `commits.js`: a fake git commit log where every entry
describes one real conflict event in the voice of an enterprise engineering
team. This job looks for an event worth a new entry, appends it, verifies it,
and ships it.

You are not writing the news. You are finding the one event in this week's
news that the existing log would want to have shipped, and writing it the way
the existing entries are written.

## 1. Preflight

```
cd C:\Users\Scott\.mavis\agents\coder\workspace\war365
git status --short
```

If that prints anything, **stop**. Do not stash, do not reset, do not modify
anything, do not continue. Someone is working in this tree. Report which
paths are dirty and end.

```
git pull --ff-only origin master
```

If that fails, **stop** and report the error. Do not force, do not reset, do
not rebase. A local `master` that is ahead of `origin/master` means a human
has unpushed work. Leave it alone and say so.

## 2. Read before you write

```
python tools/commitlog.py list
python tools/commitlog.py check
```

Read the last five entries in `commits.js`. They are your voice reference and
your dedup list. Do not write a word before you have read them.

## 3. Find candidates

Use `web_search` to look for events from the last 7 days across the theatres
the log already tracks:

- Ukraine and Russia
- Gaza and Israel
- Lebanon and Hezbollah
- Iran
- Sudan
- Syria
- Myanmar
- Sahel
- Yemen
- Haiti
- Korea
- India and Pakistan

For every candidate you must have actually opened a source and have its URL.
A candidate you cannot source is not a candidate. Cross-check the date and the
facts against one source, and against two if the event is contested or if a
number in it matters. You may look further back than 7 days if a story is
still developing and has not been logged.

## 4. The bar

An event earns its place only if it is a discrete, datable, notable moment:

- a new theatre going GA, or a region carved out of another
- a ceasefire deployed, or one collapsing
- a regime or leadership change
- a first-of-kind strike or operation
- a record displacement or casualty figure
- an attack on supply chains, infrastructure, or dual-use hardware
- a peace deal signed, or a peace deal that collapses

These do **not** earn a place, however big: a routine strike, a diplomatic
statement, a change to the terms of a ceasefire, a general's opinion, an aid
appeal, a court ruling with no operational consequence, a "what if" scenario.
Those are patch notes. A release history that logs patch notes is a changelog
nobody reads.

Also reject anything already in the log, even worded differently. A second
entry for the same event is a bug, not a new release. Check the full list
from step 2, and grep `commits.js` for the event's key terms (place names,
weapon systems, organisations) before you commit to it.

**Add at most 3 entries this run.** The cap is a limit, not a quota. The log
holds 25 entries in four and a half years, about 5 a year, and a daily job
with a cap of 3 has a ceiling of 78. If you are finding three qualifying
events most days, you are lowering the bar. A run that adds nothing is a
healthy run, and several in a row are normal.

## 5. Write the entry

Match the existing voice exactly. Read the last five entries again if you are
unsure. The rules that matter:

- The subject is a conventional commit line: `feat(scope): what happened`,
  where the scope is the theatre or subsystem. Prefix from `feat`, `fix`,
  `chore`, `docs`.
- The body is a changelog. Features, breaking changes, latency, throughput,
  SLA, rollback status, ticket IDs. The joke is that real operational details
  (dates, places, casualty counts, weapon systems) are rendered as product
  metrics. The existing entry for the October 2024 Iranian missile salvo
  reads: `Throughput: 180 in 30 min. Dropped packets: ~5 (landed in empty
  zones, mostly).`
- Real facts only, and only the ones your source states. Never invent a
  number, a date, a place, a name, or a quote. If your source says "more than
  100", write `100+`, not `137`.
- The body must carry the source URL on its own line, prefixed `Ref: `. The
  tool refuses entries without one.
- ASCII only. No em-dashes, no curly quotes, no ellipsis characters, no
  unicode arrows. Use `-` and `...`.
- Dry, not cruel. The satire is aimed at the people running the war as a
  product and at the systems that let them. It is never aimed at the people
  being killed. No gore, no invented suffering, nobody's death as a
  punchline. The existing entries are about process, not about victims. Keep
  it that way.
- 4-space indent for the body array, 2-space for the object, matching the
  file.

Write the entry as JSON, **outside the repository** (use the system temp
directory; never write scratch files into the repo, the next run's dirty-tree
check will trip over them):

```json
{
  "hash": "7 lowercase hex chars, not already used",
  "date": "YYYY-MM-DD, the real date of the event",
  "author": "handle of the actor, e.g. mod.us, houthi.media, ci-bot",
  "authorEmail": "handle@domain.example",
  "subject": "feat(scope): literal description in product language",
  "body": ["line one", "", "Ref: https://..."]
}
```

The author handle should be the actor responsible, in the same style as the
existing entries. Use `ci-bot` for anything that is a report rather than an
action by a named party. Use a domain ending in `.example`, like the
existing entries.

Only add `tag`, `headline`, `summary`, `breaking` and `chips` if the event
genuinely is a GA release that should take over the hero card on the landing
page. Usually it is not. Omit them.

Then insert it:

```
python tools/commitlog.py add --file <path to the json>
```

The tool refuses bad input: wrong hash format, duplicate hash, duplicate
subject, a date earlier than the last entry, a date in the future, a subject
that is not a conventional commit, a body with no source URL, or any non-ASCII
character. If it refuses, fix the entry and run it again. Do not edit
`commits.js` by hand to get around it.

If you are adding more than one entry, add them oldest first so the log stays
in chronological order.

## 6. Verify

All three must pass:

```
python tools/commitlog.py check
python tools/commitlog.py verify
python test/verify.py --serve
```

`check` proves the data is well formed. `verify` proves the site still renders
the new entry with no console errors. `test/verify.py --serve` is the full
layout sweep across two engines and eleven viewports, and it is the project's
pre-commit gate. It is not optional.

If any of them fails, `git checkout -- commits.js` and report the failure. Do
not push a broken log.

## 7. Ship

```
git add commits.js
git commit -m "feat(log): <one line describing what was added>"
git push origin master
```

If the push fails, report it. Do not force-push and do not retry more than
once.

## 8. Report

End with:

- each event you added, its date, and its source URL
- the commit hash and the git commit id
- the exact verification commands you ran and their result
- the candidates you rejected and the one-line reason each failed the bar
- if you added nothing: say the bar was not met, and name the candidates you
  rejected

If the tree was dirty or the pull failed, say only that and what you found.
Do not attempt a workaround.
