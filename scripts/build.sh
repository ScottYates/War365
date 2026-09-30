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
