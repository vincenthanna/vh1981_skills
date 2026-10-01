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

# SessionStart delivers a JSON payload on stdin; drain it so nothing sees SIGPIPE.
cat >/dev/null 2>&1 || :

[ "${VH1981_GUIDELINES:-1}" = "0" ] && exit 0

DIR="${CLAUDE_PLUGIN_ROOT:-}/guidelines"
[ -f "$DIR/core.md" ] || exit 0

# Escape the sed replacement: backslash, the & back-reference and the | delimiter.
esc=$(printf '%s' "$DIR" | sed 's/[\\&|]/\\&/g')
sed "s|{{GUIDELINES_DIR}}|$esc|g" "$DIR/core.md" 2>/dev/null
exit 0
