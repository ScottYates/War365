#!/usr/bin/env bash
# Start the War365 dev server in the background.
#
# Environment:
#   WAR365_ADDR   listen address (default :8000)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ADDR="${WAR365_ADDR:-:8000}"
BIN="$ROOT/bin/war365"
PIDFILE="$ROOT/.war365.pid"
LOGFILE="$ROOT/.war365.log"

if [[ -f "$PIDFILE" ]]; then
  pid="$(cat "$PIDFILE")"
  if kill -0 "$pid" 2>/dev/null; then
    echo "already running (pid $pid) on $ADDR"
    exit 0
  fi
  rm -f "$PIDFILE"
  echo "removed stale pidfile (pid $pid was gone)"
fi

# Build on demand so a clean checkout can just run start.sh.
if [[ ! -x "$BIN" ]]; then
  "$ROOT/scripts/build.sh"
fi

nohup "$BIN" -addr="$ADDR" >>"$LOGFILE" 2>&1 &
pid=$!
echo "$pid" > "$PIDFILE"

# Confirm it actually came up instead of exiting immediately (bad port, etc).
sleep 0.3
if ! kill -0 "$pid" 2>/dev/null; then
  rm -f "$PIDFILE"
  echo "error: server exited immediately. last log lines:" >&2
  tail -n 5 "$LOGFILE" >&2 || true
  exit 1
fi

echo "started (pid $pid) on $ADDR"
echo "  log:  $LOGFILE"
echo "  stop: scripts/stop.sh"
