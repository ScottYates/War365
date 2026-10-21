#!/usr/bin/env python
"""Write settings into the scan's systemd environment file.

The file is read by systemd with EnvironmentFile, so it holds plain
KEY=VALUE lines and nothing else. This script sets the values it is given
and leaves every other line alone, so an operator's own settings survive a
re-run of the installer.

Usage:

    python scripts/write-scan-env.py --file /etc/war365/minimax.env \\
        --set MINIMAX_API_KEY=... --set PLAYWRIGHT_BROWSERS_PATH=/var/lib/war365/browsers

A value that is already in the file is replaced in place. A value that is
not there is appended. The file is never printed, because it holds the
MiniMax key.
"""

import argparse
import os
import re
import sys


def set_var(text, name, value):
    """Return text with name set to value, replacing or appending."""
    pattern = r"(?m)^" + re.escape(name) + r"=.*$"
    line = name + "=" + value
    if re.search(pattern, text):
        return re.sub(pattern, lambda _m: line, text)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + line + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--file", required=True, help="the environment file to write")
    ap.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="a setting to write. May be given more than once.",
    )
    ap.add_argument(
        "--print-names",
        action="store_true",
        help="list the keys in the file, not their values",
    )
    args = ap.parse_args()

    if args.print_names:
        if not os.path.exists(args.file):
            print("(no file)")
            return 0
        for line in open(args.file, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            print(line.split("=", 1)[0])
        return 0

    pairs = []
    for item in args.set:
        if "=" not in item:
            print(f"error: {item!r} is not KEY=VALUE", file=sys.stderr)
            return 2
        key, value = item.split("=", 1)
        pairs.append((key.strip(), value))

    text = ""
    if os.path.exists(args.file):
        text = open(args.file, encoding="utf-8").read()
    for key, value in pairs:
        text = set_var(text, key, value)

    tmp = args.file + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, args.file)
    print("wrote " + ", ".join(k for k, _ in pairs) + " to " + args.file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
