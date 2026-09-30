#!/usr/bin/env bash
# Build the War365 dev server binary into ./bin/war365.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v go >/dev/null 2>&1; then
  echo "error: go not found in PATH" >&2
  exit 1
fi

mkdir -p bin
go build -o bin/war365 .
echo "built bin/war365"

# Hand the binary to the account the systemd unit runs as, so war365.service
# can execute it. Skipped when not root, or when the account does not exist
# (a dev machine that never ran the install steps). Override the account with
# WAR365_USER if you renamed it.
SVC_USER="${WAR365_USER:-war365}"
if [[ "$(id -u)" -eq 0 ]]; then
  if id "$SVC_USER" >/dev/null 2>&1; then
    # Non-fatal: the binary is already built, and a chown failure (root-squash
    # on a network mount, for example) should not fail the build. The unit
    # only needs read+execute, which root-owned 0755 already provides.
    if chown "$SVC_USER":"$SVC_USER" bin/war365; then
      echo "chowned bin/war365 to $SVC_USER:$SVC_USER"
    else
      echo "warning: chown to $SVC_USER failed; leaving bin/war365 as $(stat -c %U bin/war365 2>/dev/null || echo unknown)" >&2
    fi
  else
    echo "note: no '$SVC_USER' account on this box; leaving bin/war365 owned by root" >&2
  fi
else
  echo "note: not root; leaving bin/war365 owned by $(id -un)"
fi
