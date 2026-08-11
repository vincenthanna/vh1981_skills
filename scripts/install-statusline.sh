#!/bin/sh
# Install the devlog status line into the Claude Code config directory.
#
#   ./scripts/install-statusline.sh
#
# What it does:
#   1. copies scripts/statusline.sh    -> $CLAUDE_DIR/statusline.sh
#   2. registers it as `statusLine`    -> $CLAUDE_DIR/settings.json (other keys preserved)
#   3. smoke-tests the result and fails loudly if the status line prints nothing
#
# Existing files are backed up to <file>.bak-<timestamp> before being touched.
# Override the target directory with CLAUDE_DIR=/somewhere ./scripts/install-statusline.sh
set -eu

SRC_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
SRC="$SRC_DIR/statusline.sh"
DEST_DIR="${CLAUDE_DIR:-$HOME/.claude}"
DEST="$DEST_DIR/statusline.sh"
SETTINGS="$DEST_DIR/settings.json"
STAMP=$(date +%Y%m%d-%H%M%S)

die() { echo "install-statusline: $*" >&2; exit 1; }

[ -f "$SRC" ] || die "source not found: $SRC"

# The settings.json command embeds the path in single quotes, so a quote in the
# path would produce a broken shell command. Refuse rather than write garbage.
case "$DEST" in
  *"'"*) die "config path contains a single quote, which cannot be embedded safely: $DEST" ;;
esac

mkdir -p "$DEST_DIR"

# --- 1. copy the script -------------------------------------------------
if [ -f "$DEST" ] && ! cmp -s "$SRC" "$DEST"; then
  cp -p "$DEST" "$DEST.bak-$STAMP"
  echo "backed up existing script -> $DEST.bak-$STAMP"
fi
cp "$SRC" "$DEST"
chmod +x "$DEST"
echo "installed $DEST"

# --- 2. register statusLine in settings.json ----------------------------
if [ -f "$SETTINGS" ]; then
  cp -p "$SETTINGS" "$SETTINGS.bak-$STAMP"
  echo "backed up settings     -> $SETTINGS.bak-$STAMP"
fi

if command -v python3 >/dev/null 2>&1; then
  python3 - "$SETTINGS" "$DEST" <<'PY'
import json, pathlib, sys
settings_path, script_path = pathlib.Path(sys.argv[1]), sys.argv[2]
data = {}
if settings_path.exists():
    raw = settings_path.read_text()
    if raw.strip():
        data = json.loads(raw)
if not isinstance(data, dict):
    raise SystemExit("settings.json does not contain a JSON object")
data["statusLine"] = {"type": "command", "command": "/bin/sh '%s'" % script_path}
settings_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY
elif command -v jq >/dev/null 2>&1; then
  tmp=$(mktemp)
  if [ -s "$SETTINGS" ]; then cat "$SETTINGS"; else echo '{}'; fi |
    jq --arg cmd "/bin/sh '$DEST'" '.statusLine = {type: "command", command: $cmd}' > "$tmp"
  mv "$tmp" "$SETTINGS"
else
  die "need python3 or jq to edit settings.json; add this block to $SETTINGS by hand:
  \"statusLine\": { \"type\": \"command\", \"command\": \"/bin/sh '$DEST'\" }"
fi
echo "registered statusLine in $SETTINGS"

# --- 3. smoke test ------------------------------------------------------
payload=$(printf '{"transcript_path":"","workspace":{"current_dir":"%s"},"model":{"display_name":"install-check"}}' "$PWD")
out=$(printf '%s' "$payload" | /bin/sh "$DEST" 2>/dev/null) || die "status line exited non-zero"
[ -n "$out" ] || die "status line printed nothing; Claude Code would render no line at all"

lines=$(printf '%s\n' "$out" | wc -l | tr -d ' ')
[ "$lines" = "1" ] || die "status line printed $lines lines; it must print exactly 1"

echo "smoke test OK -> $out"
echo
echo "Restart your Claude Code session to pick up the new status line."
