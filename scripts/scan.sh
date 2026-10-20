#!/usr/bin/env bash
# Scan the news for release-log entries and ship them.
#
# The pipeline:
#   1. collect up to 20 candidate events from the public news feeds
#   2. have MiniMax score them for relevance to the release log
#   3. write the top 3 as entries, in the log's voice, grounded in the source
#   4. validate, insert, verify the site still renders
#   5. commit and push
#
# Nothing is added unless it clears the relevance bar, so a run that finds
# nothing worthy ships nothing and says so.
#
# Environment:
#   WAR365_PYTHON         python interpreter to use          (python3)
#   WAR365_SCAN_WORK      scratch directory for the run      (/var/lib/war365/scan)
#   WAR365_SCAN_TOP       how many entries a run may add    (3)
#   WAR365_SCAN_DAYS      how far back to look for events    (3)
#   WAR365_SCAN_MIN_SCORE score the top candidate must beat (60)
#   MINIMAX_API_KEY       the MiniMax credential             (required)
#
# The credential is expected in the environment, normally supplied by
# systemd from /etc/war365/minimax.env. See the README.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${WAR365_PYTHON:-python3}"
WORK="${WAR365_SCAN_WORK:-/var/lib/war365/scan}"
TOP="${WAR365_SCAN_TOP:-3}"
DAYS="${WAR365_SCAN_DAYS:-3}"
MIN_SCORE="${WAR365_SCAN_MIN_SCORE:-60}"

LOG=""

# UTF-8 mode, so the JSON reads below and the model output are decoded as
# UTF-8 whatever the locale is. Without it a cp1252 or POSIX locale turns a
# perfectly good candidates file into a UnicodeDecodeError.
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

say() {
  echo "$@"
  [[ -n "$LOG" ]] && echo "$@" >> "$LOG"
}

die() {
  echo "error: $*" >&2
  [[ -n "$LOG" ]] && echo "error: $*" >> "$LOG"
  exit 1
}

# --- 1. Preflight ------------------------------------------------------------
#
# The checks come before anything is created or changed, so a run that is
# going to refuse says so for the right reason.

if [[ -n "$(git status --porcelain)" ]]; then
  die "working tree has uncommitted changes; refusing to touch it"
fi

if [[ -z "${MINIMAX_API_KEY:-}" ]] && ! "$PYTHON" -c '
import sys
sys.path.insert(0, "tools")
from minimax_client import resolve_auth
try:
    resolve_auth()
except Exception:
    sys.exit(1)
' 2>/dev/null; then
  die "no MiniMax credential found. Set MINIMAX_API_KEY in the environment, or put it in /etc/war365/minimax.env."
fi

mkdir -p "$WORK"
LOG="$WORK/run.log"
: > "$LOG"

git pull --ff-only || die "git pull --ff-only failed; refusing to continue"

# --- 2. Collect --------------------------------------------------------------

say "collecting candidates from the feeds (last $DAYS days)"
"$PYTHON" tools/collect_candidates.py --days "$DAYS" --max 20 \
  --out "$WORK/candidates.json" || die "feed collection failed"

COUNT=$("$PYTHON" -c 'import json,sys; print(len(json.load(open(sys.argv[1], encoding="utf-8"))["candidates"]))' "$WORK/candidates.json")
say "collected $COUNT candidates"
if [[ "$COUNT" -eq 0 ]]; then
  say "no candidates in the window. Nothing to do."
  exit 0
fi

# --- 3. Rank -----------------------------------------------------------------

say "ranking with MiniMax"
"$PYTHON" tools/rank_candidates.py --file "$WORK/candidates.json" \
  --out "$WORK/ranking.json" --top "$TOP" || die "the ranker could not reach MiniMax"

BEST=$("$PYTHON" -c 'import json,sys; r=json.load(open(sys.argv[1], encoding="utf-8"))["ranking"]; print(r[0]["score"] if r else 0)' "$WORK/ranking.json")
if ! "$PYTHON" -c 'import sys; sys.exit(0 if float(sys.argv[1]) >= float(sys.argv[2]) else 1)' "$BEST" "$MIN_SCORE"; then
  say "top score $BEST is below the bar of $MIN_SCORE. Nothing ships today."
  exit 0
fi

mapfile -t PICKED < <("$PYTHON" -c '
import json,sys
sys.stdout.reconfigure(newline="\n")
ranking = json.load(open(sys.argv[1], encoding="utf-8"))["ranking"][:int(sys.argv[2])]
for s in ranking:
    print(s["id"].strip())
' "$WORK/ranking.json" "$TOP")

# Windows python writes CRLF, and command substitution keeps the carriage
# return. Strip it so the ids match the ones in the candidates file.
for i in "${!PICKED[@]}"; do
  PICKED[$i]="${PICKED[$i]//$'\r'/}"
done
say "selected: ${PICKED[*]}"

# --- 4. Write ----------------------------------------------------------------

rm -f "$WORK"/entry-*.json
for id in "${PICKED[@]}"; do
  say "writing an entry for $id"
  if ! "$PYTHON" tools/write_entry.py --candidates "$WORK/candidates.json" \
      --candidate "$id" --out "$WORK/entry-$id.json" >> "$LOG" 2>&1; then
    say "  could not write $id, skipping it"
    tail -4 "$LOG" | sed 's/^/    | /'
    rm -f "$WORK/entry-$id.json"
  fi
done

if ! compgen -G "$WORK/entry-*.json" > /dev/null; then
  say "no entries could be written. Nothing ships today."
  exit 0
fi

# --- 5. Insert, oldest first -------------------------------------------------

mapfile -t ENTRIES < <("$PYTHON" -c '
import glob, json, sys
sys.stdout.reconfigure(newline="\n")
rows = []
for path in glob.glob(sys.argv[1] + "/entry-*.json"):
    with open(path, encoding="utf-8") as fh:
        entry = json.load(fh)
    rows.append((entry.get("date", ""), path))
for _, path in sorted(rows):
    print(path)
' "$WORK")

for i in "${!ENTRIES[@]}"; do
  ENTRIES[$i]="${ENTRIES[$i]//$'\r'/}"
done

for entry_file in "${ENTRIES[@]}"; do
  "$PYTHON" tools/commitlog.py add --file "$entry_file" || die "refused $entry_file"
done

# --- 6. Verify ---------------------------------------------------------------

say "checking the log"
"$PYTHON" tools/commitlog.py check || die "the log failed the data check"

say "verifying the site still renders"
"$PYTHON" tools/commitlog.py verify || die "the site did not render cleanly"

# --- 7. Ship -----------------------------------------------------------------

if [[ -z "$(git status --porcelain commits.js)" ]]; then
  say "nothing changed in commits.js. Nothing to commit."
  exit 0
fi

COUNT_ADDED=$(ls -1 "$WORK"/entry-*.json 2>/dev/null | wc -l | tr -d ' ')
git add commits.js
git commit -m "feat(log): add ${COUNT_ADDED} release-log entries from the news scan"
git push
say "pushed $(git rev-parse --short HEAD)"
say "done: $COUNT_ADDED entries added"
