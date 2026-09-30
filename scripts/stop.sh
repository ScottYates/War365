#!/usr/bin/env bash
# Stop the War365 dev server started by start.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIDFILE="$ROOT/.war365.pid"

if [[ ! -f "$PIDFILE" ]]; then
  echo "not running (no pidfile)"
  exit 0
fi

pid="$(cat "$PIDFILE")"

if ! kill -0 "$pid" 2>/dev/null; then
  rm -f "$PIDFILE"
  echo "not running (removed stale pidfile)"
  exit 0
fi

kill "$pid"

# Wait up to ~5s for a clean exit.
for _ in $(seq 1 50); do
  if ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$PIDFILE"
    echo "stopped (pid $pid)"
    exit 0
  fi
  sleep 0.1
done

# Still alive after 5s: escalate.
kill -9 "$pid" 2>/dev/null || true
rm -f "$PIDFILE"
echo "force-killed (pid $pid) after 5s"
