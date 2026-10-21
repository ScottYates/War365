#!/usr/bin/env bash
# Install the War365 news scan on this machine.
#
# Run it as root, from a checkout of the repository:
#
#   sudo ./scripts/install-scan.sh
#
# It asks for your MiniMax API key and works out the rest. Every step is
# skipped if it is already done, so it is safe to re-run after a change.
#
# Options:
#   --key KEY    supply the key instead of prompting for it
#   --yes        never prompt; fail if there is no key to use
#   --repo DIR   where the checkout lives              (default /opt/War365)
#   -h, --help   this text
#
# Environment:
#   MINIMAX_API_KEY   the key, if you would rather not be asked
#   GITHUB_TOKEN      if set, the deploy key is added through the API
#   WAR365_REPO       same as --repo
#   WAR365_USER       the service account              (default war365)
#   WAR365_REPO_URL   where to clone from
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="${WAR365_REPO:-/opt/War365}"
CONF_DIR="${WAR365_CONF_DIR:-/etc/war365}"
STATE_DIR="${WAR365_STATE_DIR:-/var/lib/war365}"
SVC_USER="${WAR365_USER:-war365}"
ENV_FILE="$CONF_DIR/minimax.env"
KEY_FILE="$CONF_DIR/scan_key"
KNOWN_HOSTS="$CONF_DIR/known_hosts"
UNIT_NAME="war365-scan"
REPO_URL="${WAR365_REPO_URL:-https://github.com/ScottYates/War365.git}"
SSH_REMOTE="${WAR365_SSH_REMOTE:-git@github.com:ScottYates/War365.git}"
STEPS=9

KEY=""
ASSUME_YES=0

if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; DIM=$'\033[2m'; OFF=$'\033[0m'
else
  BOLD=""; DIM=""; OFF=""
fi

step()  { printf '\n%s==> [%s/%s] %s%s\n' "$BOLD" "$1" "$STEPS" "$2" "$OFF"; }
info()  { printf '    %s\n' "$*"; }
warn()  { printf '    %swarning:%s %s\n' "$DIM" "$OFF" "$*" >&2; }
die()   { printf 'error: %s\n' "$*" >&2; exit 1; }

usage() {
  sed -n '3,20p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --key)  KEY="${2:-}"; shift 2 ;;
    --yes)  ASSUME_YES=1; shift ;;
    --repo) REPO_DIR="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown option: %s\n\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

# --- 1 -----------------------------------------------------------------------

step 1 "Checking the machine"
[[ "$(id -u)" -eq 0 ]] || die "this has to run as root. Try: sudo $0"
info "running as root"
command -v git >/dev/null 2>&1 || die "git is not installed"
command -v ssh-keygen >/dev/null 2>&1 || die "openssh-client is not installed"
command -v systemctl >/dev/null 2>&1 || die "systemd is not installed"
info "git, ssh-keygen and systemctl are all present"

# --- 2 -----------------------------------------------------------------------

step 2 "The checkout"
if [[ ! -d "$REPO_DIR/.git" ]]; then
  info "cloning $REPO_URL into $REPO_DIR"
  git clone "$REPO_URL" "$REPO_DIR"
else
  info "using the checkout at $REPO_DIR"
fi
if [[ "$REPO_DIR" != "$SOURCE_DIR" ]]; then
  info "copying the install files from $SOURCE_DIR"
  install -d "$REPO_DIR/scripts" "$REPO_DIR/deploy"
  install -m 0755 "$SOURCE_DIR/scripts/scan.sh" "$REPO_DIR/scripts/scan.sh"
  install -m 0644 "$SOURCE_DIR/deploy/War365-scan.service" "$REPO_DIR/deploy/"
  install -m 0644 "$SOURCE_DIR/deploy/War365-scan.timer" "$REPO_DIR/deploy/"
  install -m 0644 "$SOURCE_DIR/deploy/war365-scan.env.example" "$REPO_DIR/deploy/"
fi
git config --global --add safe.directory "$REPO_DIR" 2>/dev/null || true

# --- 3 -----------------------------------------------------------------------

step 3 "The service account and directories"
if ! id "$SVC_USER" >/dev/null 2>&1; then
  useradd --system --no-create-home --shell /usr/sbin/nologin "$SVC_USER"
  info "created the $SVC_USER account"
else
  info "the $SVC_USER account already exists"
fi
install -d -m 0750 -o "$SVC_USER" -g "$SVC_USER" "$STATE_DIR"
install -d -m 0750 -o root -g "$SVC_USER" "$CONF_DIR"
chown -R "$SVC_USER":"$SVC_USER" "$REPO_DIR"
info "the checkout now belongs to $SVC_USER, so the scan can commit to it"

# --- 4 -----------------------------------------------------------------------

step 4 "The MiniMax API key"
KEY="${KEY:-${MINIMAX_API_KEY:-}}"
if [[ -z "$KEY" && -f "$ENV_FILE" ]]; then
  KEY="$(sed -n 's/^MINIMAX_API_KEY=//p' "$ENV_FILE" | head -1)"
  [[ -n "$KEY" ]] && info "found a key already in $ENV_FILE"
fi
if [[ -z "$KEY" ]]; then
  if [[ "$ASSUME_YES" -eq 1 ]]; then
    die "there is no key to use. Pass --key KEY or set MINIMAX_API_KEY."
  fi
  [[ -t 0 ]] || die "there is no terminal to prompt on. Pass --key KEY or set MINIMAX_API_KEY."
  echo
  info "Get a key from one of these:"
  info "  pay-as-you-go  https://platform.minimax.io/user-center/basic-information/interface-key"
  info "  M Plan seat    https://platform.minimax.io/user-center/payment/token-plan"
  echo
  read -rsp "Paste the MiniMax API key (input stays hidden): " KEY || die "no key entered"
  echo
  [[ -n "$KEY" ]] || die "no key entered"
  read -rp "Write this key to $ENV_FILE? [y/N] " confirm || true
  [[ "$confirm" =~ ^[Yy]$ ]] || die "aborted, nothing was written"
fi
# A newline or tab in the key would split the environment file into two
# directives, so take them out. A pasted key never legitimately has either.
KEY="${KEY//[$'\n\r\t']/}"
info "the key is ${#KEY} characters long"

# --- 5 -----------------------------------------------------------------------

step 5 "The environment file"
install -d -m 0750 -o root -g "$SVC_USER" "$CONF_DIR"
if [[ -f "$ENV_FILE" ]]; then
  info "updating the key in the existing $ENV_FILE"
  python3 - "$ENV_FILE" "$KEY" <<'PY'
import re, sys
path, key = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
text = re.sub(r"(?m)^MINIMAX_API_KEY=.*$", "MINIMAX_API_KEY=" + key, text)
open(path, "w", encoding="utf-8").write(text)
PY
else
  info "writing $ENV_FILE from the template"
  python3 - "$REPO_DIR/deploy/war365-scan.env.example" "$ENV_FILE" "$KEY" <<'PY'
import sys
src, dst, key = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(src, encoding="utf-8").read()
text = text.replace("MINIMAX_API_KEY=PASTE_YOUR_KEY_HERE", "MINIMAX_API_KEY=" + key)
open(dst, "w", encoding="utf-8").write(text)
PY
fi
chown root:"$SVC_USER" "$ENV_FILE"
chmod 0640 "$ENV_FILE"
info "the file is root-owned, group $SVC_USER, mode 0640. The key is never logged."

# --- 6 -----------------------------------------------------------------------

step 6 "The push key"
if [[ -f "$KEY_FILE" ]]; then
  info "reusing the existing $KEY_FILE"
else
  ssh-keygen -t ed25519 -N '' -f "$KEY_FILE" -C "war365-scan@$(hostname)" >/dev/null
  info "generated $KEY_FILE"
fi
chown root:"$SVC_USER" "$KEY_FILE"
chmod 0640 "$KEY_FILE"

if [[ ! -s "$KNOWN_HOSTS" ]]; then
  if ssh-keyscan github.com > "$KNOWN_HOSTS" 2>/dev/null; then
    info "recorded the github.com host key in $KNOWN_HOSTS"
  else
    warn "could not reach github.com. Run: ssh-keyscan github.com > $KNOWN_HOSTS"
  fi
fi
chown root:"$SVC_USER" "$KNOWN_HOSTS" 2>/dev/null || true
chmod 0644 "$KNOWN_HOSTS" 2>/dev/null || true

if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  info "GITHUB_TOKEN is set, adding the deploy key through the API"
  if python3 - "$KEY_FILE.pub" <<'PY'
import json, os, sys, urllib.request, urllib.error
pub = open(sys.argv[1], encoding="utf-8").read().strip()
body = json.dumps({"title": "war365-scan", "key": pub, "read_only": False}).encode()
req = urllib.request.Request(
    "https://api.github.com/repos/ScottYates/War365/keys",
    data=body,
    headers={
        "Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("    added deploy key", json.loads(resp.read())["id"])
except urllib.error.HTTPError as exc:
    print("    could not add the deploy key:", exc.code, file=sys.stderr)
    sys.exit(1)
PY
  then
    info "the deploy key is registered"
  else
    warn "the deploy key was not added through the API. Add it by hand, below."
  fi
else
  echo
  info "Add this public key to the repository, with WRITE access:"
  info "  repository > Settings > Deploy keys > Add deploy key"
  echo
  sed 's/^/    /' "$KEY_FILE.pub"
  echo
fi

if git -C "$REPO_DIR" remote get-url origin >/dev/null 2>&1; then
  CURRENT="$(git -C "$REPO_DIR" remote get-url origin)"
  if [[ "$CURRENT" != "$SSH_REMOTE" ]]; then
    git -C "$REPO_DIR" remote set-url origin "$SSH_REMOTE"
    info "origin now points at $SSH_REMOTE, so the push uses the deploy key"
  fi
fi

# The deploy key has to be usable by every git command in this repo, not
# just the ones the systemd unit runs with GIT_SSH_COMMAND in the
# environment. core.sshCommand is per-repository, so a plain "git pull" in
# the checkout works for any user, from any shell.
SSH_COMMAND="ssh -i $KEY_FILE -o IdentitiesOnly=yes -o UserKnownHostsFile=$KNOWN_HOSTS -o StrictHostKeyChecking=accept-new"
git -C "$REPO_DIR" config --local core.sshCommand "$SSH_COMMAND"
info "the deploy key is configured for this checkout, so git works from any shell"

# The pre-commit hook refuses a commit that would put a secret in the repo.
if [[ -f "$REPO_DIR/.githooks/pre-commit" ]]; then
  git -C "$REPO_DIR" config core.hooksPath .githooks
  if [[ -x "$REPO_DIR/.githooks/pre-commit" ]]; then
    info "the pre-commit secret check is enabled for this checkout"
  else
    warn "the pre-commit hook is not executable. Run: chmod +x $REPO_DIR/.githooks/pre-commit"
  fi
fi

# The checkout belongs to the service account, so git refuses to work in it
# for anyone else unless the directory is marked safe. The root account was
# already handled above; do the same for the user who ran this script.
if [[ -n "${SUDO_USER:-}" && "$SUDO_USER" != "root" ]]; then
  sudo -u "$SUDO_USER" git config --global --add safe.directory "$REPO_DIR" 2>/dev/null \
    || warn "could not mark $REPO_DIR safe for $SUDO_USER. Run: sudo -u $SUDO_USER git config --global --add safe.directory $REPO_DIR"
else
  info "the checkout is marked safe for root"
fi

# --- 7 -----------------------------------------------------------------------

step 7 "Python and Playwright"
command -v python3 >/dev/null 2>&1 || die "python3 is not installed. Try: apt-get install -y python3 python3-venv"
if [[ ! -x "$REPO_DIR/.venv/bin/python" ]]; then
  python3 -m venv "$REPO_DIR/.venv"
  info "created $REPO_DIR/.venv"
else
  info "reusing $REPO_DIR/.venv"
fi
"$REPO_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$REPO_DIR/.venv/bin/pip" install --quiet -r "$REPO_DIR/test/requirements.txt"
info "installed playwright"

# The browser is a separate download from the package that drives it, and it
# lands in a per-user cache. An install run as root puts it in /root/.cache,
# which the service account cannot read, so the browser goes in one fixed
# directory that the unit points at as well. The unit is the source of
# truth for the path: read it from there so the two cannot drift apart.
BROWSERS_DIR="$(sed -n 's/^Environment=PLAYWRIGHT_BROWSERS_PATH=//p' \
  "$REPO_DIR/deploy/War365-scan.service" | head -1)"
BROWSERS_DIR="${BROWSERS_DIR:-/var/lib/war365/browsers}"
install -d -m 0755 -o "$SVC_USER" -g "$SVC_USER" "$BROWSERS_DIR"
PLAYWRIGHT_BROWSERS_PATH="$BROWSERS_DIR" \
  "$REPO_DIR/.venv/bin/python" -m playwright install --with-deps chromium
chown -R "$SVC_USER":"$SVC_USER" "$BROWSERS_DIR"
info "installed chromium into $BROWSERS_DIR"

# An install the service cannot use is not an install. Prove the browser
# starts as the account the unit runs as, with that account's HOME, before
# the timer is ever enabled.
if ! sudo -u "$SVC_USER" env HOME="$STATE_DIR" PLAYWRIGHT_BROWSERS_PATH="$BROWSERS_DIR" \
     "$REPO_DIR/.venv/bin/python" "$REPO_DIR/tools/commitlog.py" doctor; then
  die "the browser does not start for $SVC_USER. The doctor above says why."
fi
info "the browser starts for $SVC_USER"

# And once more inside the unit's own sandbox, because that is where it
# actually has to run. The properties below are the ones the unit sets.
if command -v systemd-run >/dev/null 2>&1 && systemd-run --quiet --wait --pipe /bin/true 2>/dev/null; then
  if systemd-run --quiet --wait --pipe \
      --uid="$SVC_USER" --gid="$SVC_USER" \
      --setenv="HOME=$STATE_DIR" \
      --setenv="PLAYWRIGHT_BROWSERS_PATH=$BROWSERS_DIR" \
      --property="WorkingDirectory=$REPO_DIR" \
      --property=NoNewPrivileges=true \
      --property=PrivateTmp=true \
      --property=PrivateDevices=true \
      --property=ProtectSystem=strict \
      --property=ProtectHome=true \
      --property=ProtectKernelTunables=true \
      --property=ProtectKernelModules=true \
      --property=ProtectControlGroups=true \
      --property=RestrictSUIDSGID=true \
      --property=RestrictRealtime=true \
      --property=RestrictNamespaces=true \
      --property=LockPersonality=true \
      --property=SystemCallArchitectures=native \
      --property="ReadWritePaths=$REPO_DIR $STATE_DIR" \
      --property="RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6 AF_NETLINK" \
      "$REPO_DIR/.venv/bin/python" "$REPO_DIR/tools/commitlog.py" doctor; then
    info "the browser starts inside the unit's sandbox"
  else
    die "the browser does not start inside the unit's sandbox. The doctor above says why, and the unit would fail the same way."
  fi
else
  warn "systemd-run is not usable here, so the sandbox was not tested. Start the unit by hand and watch it: systemctl start $UNIT_NAME.service"
fi

# --- 8 -----------------------------------------------------------------------

step 8 "The systemd units"
install -m 0644 "$REPO_DIR/deploy/War365-scan.service" "/etc/systemd/system/$UNIT_NAME.service"
install -m 0644 "$REPO_DIR/deploy/War365-scan.timer"   "/etc/systemd/system/$UNIT_NAME.timer"
systemctl daemon-reload
info "installed $UNIT_NAME.service and $UNIT_NAME.timer"

# --- 9 -----------------------------------------------------------------------

step 9 "The timer"
systemctl enable --now "$UNIT_NAME.timer"
info "the timer is enabled and will fire daily at 07:00 America/Chicago"

echo
if systemctl list-unit-files war365.service 2>/dev/null | grep -q '^war365.service'; then
  info "the web server unit is installed as well"
else
  info "the web server unit is not installed yet. See the README for deploy/War365.service."
fi
echo
info "Run the scan once, by hand, before you trust the timer:"
info "  sudo systemctl start $UNIT_NAME.service"
info "  journalctl -u $UNIT_NAME -f"
echo
info "Git in this checkout, from any shell:"
info "  git -C $REPO_DIR pull"
info "  git -C $REPO_DIR status"
echo
info "Files:"
info "  $ENV_FILE   the key and the settings"
info "  $KEY_FILE   the push key"
info "  $STATE_DIR  the scratch directory and the last run log"
echo
info "Everything lives in:"
info "  $CONF_DIR   the configuration"
info "  $STATE_DIR  the state"
info "  $REPO_DIR   the checkout"
echo
