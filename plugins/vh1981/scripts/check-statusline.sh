#!/bin/sh
# SessionStart self-repair for the devlog status line.
#
# `statusLine` lives in settings.json, not in the plugin manifest, so it does not
# travel with a plugin install and other installers (orca) overwrite it. Both
# failures are silent: the status line just stops rendering. This hook restores
# it at session start and reports only when it actually changed something.
#
# Repairs, in order:
#   1. $CLAUDE_DIR/statusline.sh missing or stale -> copy the version this plugin ships
#   2. settings.json statusLine not pointing at it -> rewrite that one key
#
# Opt out with VH1981_STATUSLINE_AUTOREPAIR=0.
# Never fails the session: every path exits 0.

# SessionStart delivers a JSON payload on stdin; drain it so nothing sees SIGPIPE.
cat >/dev/null 2>&1 || :

[ "${VH1981_STATUSLINE_AUTOREPAIR:-1}" = "0" ] && exit 0

SRC="${CLAUDE_PLUGIN_ROOT:-}/scripts/statusline.sh"
[ -f "$SRC" ] || exit 0

DEST_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
DEST="$DEST_DIR/statusline.sh"
SETTINGS="$DEST_DIR/settings.json"
WANT="/bin/sh '$DEST'"

# A quote in the path cannot be embedded in the command string safely.
case "$DEST" in *"'"*) exit 0 ;; esac

[ -d "$DEST_DIR" ] || exit 0

repaired=""

# --- 1. keep the installed script in sync with the one this plugin ships ---
if [ ! -f "$DEST" ] || ! cmp -s "$SRC" "$DEST"; then
  [ -f "$DEST" ] && cp -p "$DEST" "$DEST.bak-autorepair" 2>/dev/null
  if cp "$SRC" "$DEST" 2>/dev/null && chmod +x "$DEST" 2>/dev/null; then
    repaired="script"
  fi
fi

# --- 2. keep settings.json pointing at it --------------------------------
# Written to a temp file and renamed, so a concurrent session can never observe
# a half-written settings.json.
current=""
if [ -f "$SETTINGS" ] && command -v python3 >/dev/null 2>&1; then
  current=$(python3 -c "
import json,sys
try:
    d=json.load(open(sys.argv[1]))
    v=d.get('statusLine') or {}
    print(v.get('command','') if isinstance(v,dict) else '')
except Exception:
    print('')
" "$SETTINGS" 2>/dev/null)
fi

if [ "$current" != "$WANT" ]; then
  if command -v python3 >/dev/null 2>&1; then
    if python3 -c "
import json,os,sys,tempfile
settings, want = sys.argv[1], sys.argv[2]
try:
    data = json.load(open(settings)) if os.path.exists(settings) and os.path.getsize(settings) else {}
except Exception:
    sys.exit(1)
if not isinstance(data, dict):
    sys.exit(1)
if os.path.exists(settings):
    import shutil; shutil.copy2(settings, settings + '.bak-autorepair')
data['statusLine'] = {'type': 'command', 'command': want}
d = os.path.dirname(settings) or '.'
fd, tmp = tempfile.mkstemp(dir=d, prefix='.settings-', suffix='.json')
with os.fdopen(fd, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write('\n')
os.replace(tmp, settings)
" "$SETTINGS" "$WANT" 2>/dev/null; then
      repaired="${repaired:+$repaired+}settings"
    fi
  fi
fi

[ -n "$repaired" ] && printf 'vh1981: devlog status line repaired (%s). Restart the session to see it.\n' "$repaired"
exit 0
