#!/usr/bin/env bash
# Rebuild and restart the War365 dev server.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$HERE/stop.sh"
"$HERE/build.sh"
"$HERE/start.sh"
