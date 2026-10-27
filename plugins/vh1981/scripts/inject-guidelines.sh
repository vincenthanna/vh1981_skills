#!/bin/sh
# SessionStart: inject the vh1981 default guidelines into every session.
#
# A plugin cannot change session policy through files alone: a CLAUDE.md at the
# plugin root is not loaded, and the plugin settings.json accepts only `agent`
# and `subagentStatusLine`. SessionStart stdout is added to the context, so this
# hook is how installing the plugin sets the defaults. hooks.json gives it no
# matcher, so it re-runs on startup/resume/clear/compact and the rules survive
# /clear and compaction.
#
# guidelines/core.md is printed every session and must stay small: large hook
# output is saved to a file and only a preview reaches the context. Longer
# material (doc-style.md) is read on demand; core.md names it through
# {{GUIDELINES_DIR}}, replaced here with this install's absolute path.
#
# Opt out with VH1981_GUIDELINES=0.
# Never fails the session: every path exits 0.

# SessionStart delivers a JSON payload on stdin; read all of it so nothing sees
# SIGPIPE, and keep it for the session id.
payload=$(cat 2>/dev/null) || :

[ "${VH1981_GUIDELINES:-1}" = "0" ] && exit 0

DIR="${CLAUDE_PLUGIN_ROOT:-}/guidelines"
[ -f "$DIR/core.md" ] || exit 0

# Escape the sed replacement: backslash, the & back-reference and the | delimiter.
esc=$(printf '%s' "$DIR" | sed 's/[\\&|]/\\&/g')
sed "s|{{GUIDELINES_DIR}}|$esc|g" "$DIR/core.md" 2>/dev/null || exit 0

# Mark the session as injected. A run cancelled by the hook timeout never gets
# here, and prompt-hook.py re-injects on the next prompt when the marker is
# missing. The path must match state_dir() in prompt-hook.py.
sid=$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([A-Za-z0-9-]*\)".*/\1/p' | head -n 1)
if [ -n "$sid" ]; then
  state="${VH1981_STATE_DIR:-${TMPDIR:-/tmp}/vh1981-$(id -u)}"
  if mkdir -p "$state/injected" 2>/dev/null && [ -O "$state" ]; then
    chmod 700 "$state" 2>/dev/null
    : > "$state/injected/$sid" 2>/dev/null
  fi
fi
exit 0
