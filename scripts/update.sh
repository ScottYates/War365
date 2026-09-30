#!/usr/bin/env bash
# Pull the latest changes, rebuild, and restart the War365 dev server.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree has uncommitted changes; commit or stash first" >&2
  exit 1
fi

git pull --ff-only
"$ROOT/scripts/build.sh"
"$ROOT/scripts/restart.sh"
