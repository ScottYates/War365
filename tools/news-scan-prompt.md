# News scan procedure

This is the full procedure for the War365 news scan job. The scheduled task
carries only a short wrapper; this file is the procedure.

War365 documents real-world conflicts as if they were SaaS releases. The
centrepiece is `commits.js`: a fake git commit log where every entry
describes one real conflict event in the voice of an enterprise engineering
team. This job looks for the events worth a new entry, has MiniMax rank them
for relevance, writes the winners in voice, and ships them.

The pipeline is: collect up to 20 candidates, score them with MiniMax, write
the top 3, ship.

You are not writing the news. You are finding the events in this week's news
that the existing log would want to have shipped, and writing them the way
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

## 3. Collect up to 20 candidates

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

Collect **up to 20** candidates. Every candidate needs a real date, a real
source URL you actually opened, one or two sentences of what happened, and
the theatre it belongs to. Do not pad the list to hit 20. Twenty weak
candidates score worse than five good ones, because the scorer has to rank
them against each other.

You may look back further than 7 days if a story is still developing and has
not been logged. You may not log an event dated before the last entry in the
log: entries are appended newest last, so anything older is already out of
reach. `tools/commitlog.py add` will refuse it.

Write the candidates as JSON, **outside the repository** (use the system temp
directory; never write scratch files into the repo, the next run's dirty-tree
check will trip over them):

```json
{
  "candidates": [
    {
      "id": "c01",
      "date": "2026-10-15",
      "theatre": "Ukraine and Russia",
      "headline": "one line, the event as it would be titled",
      "summary": "one or two sentences, facts only, no judgement",
      "url": "https://the-source-you-actually-opened"
    }
  ]
}
```

Ids are `c01`, `c02`, and so on, unique within the file.

**Never write a URL you have not opened.** Never write a candidate you have
not seen in a source. If you cannot verify an event, it is not a candidate.
The scorer does not fact-check, and neither does the log. You are the only
thing standing between the release history and a plausible invention.

## 4. Score them with MiniMax

```
python tools/rank_candidates.py --file <candidates.json> --out <ranking.json>
```

The tool sends the candidates, the subjects already in the log, and the
rubric to MiniMax, and prints the ranking with the top 3 marked with a `*`.
The rubric is in the tool. It scores an event on whether it would earn a
line in a release history that reads like a git log of product launches: a
new theatre going GA, a ceasefire deployed or one collapsing, a regime
change, a first-of-kind strike, a record displacement figure, an attack on
critical infrastructure. A routine strike, a diplomatic statement, an aid
appeal and a general's opinion are patch notes, and patch notes score low.

The tool authenticates with the local MiniMax Code runtime, reading the
provider `baseURL` from the runtime config and the access token from the
runtime's auth store. Nothing is written to disk and no token is printed.

If it cannot reach MiniMax, **stop**. Report the error and add nothing. Do
not fall back to picking candidates by eye. The score is the point of the
step, and a run that skips it is not a run.

**The top 3 by score are the ones you write up.** Read the reasons, they
tell you what the scorer thought each event was, and they are worth
disagreeing with: if the top scorer picked a diplomatic statement and the
fourth pick is a genuine regime change, write the fourth. If the top score
is below 60, nothing cleared the bar and you add nothing. A run that adds
nothing is a healthy run, and several in a row are normal.

## 5. Write the entries

Match the existing voice exactly. Read the last five entries again if you are
unsure. The rules that matter:

- The subject is a conventional commit line: `feat(scope): what happened`,
  where the scope is the theatre or subsystem. Prefix from `feat`, `fix`,
  `chore`, `docs`. Reuse a scope the log already uses where it fits.
- The body is a changelog. Features, breaking changes, latency, throughput,
  SLA, rollback status, ticket IDs. The joke is that real operational details
  (dates, places, casualty counts, weapon systems) are rendered as product
  metrics. The existing entry for the October 2024 Iranian missile salvo
  reads: `Throughput: 180 in 30 min. Dropped packets: ~5 (landed in empty
  zones, mostly).`
- Real facts only, and only the ones your source states. Never invent a
  number, a date, a place, a name, or a quote. If your source says "more than
  100", write `100+`, not `137`. If two sources disagree on a number, use
  the more cautious one or leave the number out.
- The body must carry the source URL on its own line, prefixed `Ref: `. The
  tool refuses entries without one.
- ASCII only. No em-dashes, no curly quotes, no ellipsis characters, no
  unicode arrows. Use `-` and `...`.
- Dry, not cruel. The satire is aimed at the people running the war as a
  product and at the systems that let them. It is never aimed at the people
  being killed. No gore, no invented suffering, nobody's death as a
  punchline. Render casualties the way the log already does, in the
  register of a metric or a hardware fault, and then move on to the
  operational facts. The existing entries are about process, not about
  victims. Keep it that way.
- 4-space indent for the body array, 2-space for the object, matching the
  file.
- The author handle is the actor responsible, in the same style as the
  existing entries. Reuse an existing handle when the same actor ships
  again. Use `ci-bot` for anything that is a report rather than an action by
  a named party. Use a domain ending in `.example`.

Write each entry as JSON, outside the repository, in the same shape as the
candidates file but with the commit fields:

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

Only add `tag`, `headline`, `summary`, `breaking` and `chips` if the event
genuinely is a GA release that should take over the hero card on the landing
page. Usually it is not. Omit them.

Then insert each one:

```
python tools/commitlog.py add --file <path to the entry json>
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

- the ranking, top 3 first, with scores
- each event you added, its date, and its source URL
- the commit hash and the git commit id
- the exact verification commands you ran and their result
- the candidates you rejected and the one-line reason each failed the bar
- if you added nothing: say the bar was not met, and name the candidates you
  rejected

If the tree was dirty, the pull failed, or the scorer could not reach
MiniMax, say only that and what you found. Do not attempt a workaround.
