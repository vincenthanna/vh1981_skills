#!/bin/sh
# Claude Code status line — shows the devlog project active in THIS session.
#
# Portable across macOS (BSD userland) and Linux (GNU coreutils):
#   - no `tail -r` / `tac`  : the last marker is found with grep + `tail -n1`
#   - no hard jq dependency : falls back to python3, then to a grep/sed parse
#   - no hardcoded $HOME    : every path is derived from $HOME at runtime
#
# Resolution order (mirrors devlog SKILL.md "Active Project"):
#   1. the last `[devlog/active: <name>]` marker printed in this session's
#      transcript  -> per-session truth, unaffected by concurrent sessions
#   2. <repo>/docs/devlog/.active                -> repo-wide resume hint,
#      shown with a `~` prefix because another session may have written it
#
# stdin: the status-line JSON payload from Claude Code.

payload=$(cat)

# Keep the orca telemetry status line working (it writes nothing to stdout).
orca="$HOME/.orca/agent-hooks/claude-statusline.sh"
if [ -f "$orca" ] && [ -r "$orca" ] && [ -x "$orca" ]; then
  printf '%s' "$payload" | /bin/sh "$orca" >/dev/null 2>&1 || :
fi

# --- parse the payload --------------------------------------------------
transcript=""
cwd=""
model=""

if command -v jq >/dev/null 2>&1; then
  eval "$(printf '%s' "$payload" | jq -r '
      @sh "transcript=\(.transcript_path // "")",
      @sh "cwd=\(.workspace.current_dir // .cwd // "")",
      @sh "model=\(.model.display_name // "")"
    ' 2>/dev/null)" 2>/dev/null || :
fi

if [ -z "$cwd" ] && command -v python3 >/dev/null 2>&1; then
  eval "$(printf '%s' "$payload" | python3 -c '
import json, shlex, sys
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
if not isinstance(d, dict):
    d = {}
ws = d.get("workspace") or {}
md = d.get("model") or {}
if not isinstance(ws, dict):
    ws = {}
if not isinstance(md, dict):
    md = {}
def emit(name, value):
    print("%s=%s" % (name, shlex.quote(value if isinstance(value, str) else "")))
emit("transcript", d.get("transcript_path") or "")
emit("cwd", ws.get("current_dir") or d.get("cwd") or "")
emit("model", md.get("display_name") or "")
' 2>/dev/null)" 2>/dev/null || :
fi

# Last resort: no jq, no python3 — pull the two fields we can get with sed.
if [ -z "$cwd" ]; then
  transcript=$(printf '%s' "$payload" |
    sed -n 's/.*"transcript_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' |
    head -n 1)
  cwd=$(printf '%s' "$payload" |
    sed -n 's/.*"current_dir"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' |
    head -n 1)
  model=$(printf '%s' "$payload" |
    sed -n 's/.*"display_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' |
    head -n 1)
fi

[ -n "$cwd" ] || cwd=$PWD

# --- devlog project -----------------------------------------------------
# `[A-Za-z0-9._-]` never matches the `<project>` placeholders that appear in
# SKILL.md excerpts inside the transcript, so only real project names match.
# grep scans forward and `tail -n1` keeps the LAST hit, which avoids the
# BSD-only `tail -r` and the GNU-only `tac`.
devlog=""
hint=""
if [ -n "$transcript" ] && [ -r "$transcript" ]; then
  devlog=$(grep -o '\[devlog/active: [A-Za-z0-9._][A-Za-z0-9._-]*' "$transcript" 2>/dev/null |
    tail -n 1 |
    sed 's/^.*: //')
fi
if [ -z "$devlog" ]; then
  root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || root=$cwd
  if [ -r "$root/docs/devlog/.active" ]; then
    devlog=$(head -n1 "$root/docs/devlog/.active" 2>/dev/null | tr -d '\r\n')
    [ -n "$devlog" ] && hint="~"
  fi
fi

# --- render -------------------------------------------------------------
DIM='\033[2m'
CYAN='\033[36m'
RESET='\033[0m'
sep="${DIM} | ${RESET}"

out=$(basename "$cwd")
branch=$(git -C "$cwd" rev-parse --abbrev-ref HEAD 2>/dev/null)
[ -n "$branch" ] && out="${out}${sep}⎇ ${branch}"
if [ -n "$devlog" ]; then
  out="${out}${sep}${CYAN}📓 ${hint}${devlog}${RESET}"
else
  out="${out}${sep}${DIM}📓 -${RESET}"
fi
[ -n "$model" ] && out="${out}${sep}${DIM}${model}${RESET}"

printf '%b\n' "$out"
