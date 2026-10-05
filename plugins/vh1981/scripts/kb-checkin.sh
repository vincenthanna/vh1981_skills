#!/bin/sh
# SessionStart: check this checkout in to the knowledge base, in the background.
#
# `kb.py checkin` registers the checkout (branch, devlog projects, last seen) and
# uploads the devlog projects it owns, so the KB's daily log can see work on
# machines the KB host cannot ssh into. It runs at most once per checkout per day,
# only on machines with a configured KB (`kb init` or VH1981_KB), and never
# overwrites or deletes: conflicts and deletions are skipped.
#
# Opt out with VH1981_KB_CHECKIN=0. Never blocks or fails the session.

cat >/dev/null 2>&1 || :
[ "${VH1981_KB_CHECKIN:-1}" = "0" ] && exit 0

KB="${CLAUDE_PLUGIN_ROOT:-}/skills/kb/scripts/kb.py"
[ -f "$KB" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$DIR" ] || exit 0

LOGDIR="${XDG_CACHE_HOME:-$HOME/.cache}/vh1981"
mkdir -p "$LOGDIR" 2>/dev/null || exit 0
LOG="$LOGDIR/kb-checkin.log"
# Keep the log small: it only records one line per checkout per day.
[ -f "$LOG" ] && [ "$(wc -c < "$LOG" 2>/dev/null || echo 0)" -gt 1048576 ] && : > "$LOG"

( cd "$DIR" && nohup python3 "$KB" checkin >>"$LOG" 2>&1 & ) >/dev/null 2>&1
exit 0
