#!/bin/sh
# Regression tests for the devlog status line, its installer, and the
# SessionStart self-repair hook.
#
#   ./scripts/tests/run.sh
#
# Every case here corresponds to a bug that actually shipped or a contract the
# hook depends on. Run on both Linux and macOS: the two worst bugs so far were
# BSD-vs-GNU differences that pass on one platform and fail on the other.
set -u

ROOT=$(CDPATH='' cd -- "$(dirname -- "$0")/../.." && pwd)
STATUSLINE="$ROOT/plugins/vh1981/scripts/statusline.sh"
INSTALLER="$ROOT/scripts/install-statusline.sh"
CHECKER="$ROOT/plugins/vh1981/scripts/check-statusline.sh"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT INT TERM
ESC=$(printf '\033')
FAILED=0
COUNT=0

pass() { COUNT=$((COUNT + 1)); printf 'ok   %s\n' "$1"; }
fail() { COUNT=$((COUNT + 1)); FAILED=1; printf 'FAIL %s\n       %s\n' "$1" "$2"; }

assert_contains() {
  case "$3" in
    *"$2"*) pass "$1" ;;
    *) fail "$1" "expected to contain [$2], got [$3]" ;;
  esac
}
assert_not_contains() {
  case "$3" in
    *"$2"*) fail "$1" "expected NOT to contain [$2], got [$3]" ;;
    *) pass "$1" ;;
  esac
}
assert_eq() { if [ "$2" = "$3" ]; then pass "$1"; else fail "$1" "want [$2], got [$3]"; fi; }

# Resolve a real binary without tripping over shell functions or aliases.
resolve() { env -i PATH=/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin which "$1" 2>/dev/null; }

# A PATH holding only the listed tools, used to simulate machines without jq
# or python3.
mkbin() {
  d=$1; shift
  mkdir -p "$d"
  for b in "$@"; do
    p=$(resolve "$b") || continue
    [ -n "$p" ] && ln -sf "$p" "$d/$b"
  done
}

render() { printf '%s' "$1" | env "PATH=$2" /bin/sh "$STATUSLINE" 2>&1 | sed "s/${ESC}\[[0-9;]*m//g"; }
payload() { printf '{"transcript_path":"%s","workspace":{"current_dir":"%s"},"model":{"display_name":"M"}}' "$1" "$2"; }

# ---------------------------------------------------------------- fixtures
REPO="$TMP/repo"
mkdir -p "$REPO/docs/devlog"
# A branch name only resolves once there is a commit; an empty repo reports HEAD.
( cd "$REPO" && git init -q . && git symbolic-ref HEAD refs/heads/main &&
  git -c user.email=t@example.com -c user.name=t commit -q --allow-empty -m init ) >/dev/null 2>&1
printf 'hinted' > "$REPO/docs/devlog/.active"

TRANSCRIPT="$TMP/transcript.jsonl"
cat > "$TRANSCRIPT" <<'EOF'
{"m":"SKILL.md excerpt: the marker is `[devlog/active: <project>]`"}
{"m":"result [devlog/active: first-project]"}
{"m":"result [devlog/active: winner]"}
EOF

# One line carrying two markers — this is what broke `grep -m1 -o`.
TWO_ON_ONE="$TMP/two-on-one.jsonl"
printf '%s\n' '{"m":"[devlog/active: alpha] then [devlog/active: beta]"}' > "$TWO_ON_ONE"

BIN_FULL=$PATH
mkbin "$TMP/bin_nojq" cat grep sed head tail tr basename dirname git
mkbin "$TMP/bin_none" cat grep sed head tail tr basename dirname git
PY=$(resolve python3)
[ -n "$PY" ] && ln -sf "$PY" "$TMP/bin_nojq/python3"

# GNU coreutils has no `tail -r`; reject it the way GNU does.
mkbin "$TMP/bin_gnutail" cat grep sed head tr basename dirname git jq python3
# shellcheck disable=SC2016  # deliberate literal: this is a printf format string
printf '#!/bin/sh\nfor a in "$@"; do [ "$a" = "-r" ] && { echo "tail: invalid option -- r" >&2; exit 1; }; done\nexec %s "$@"\n' "$(resolve tail)" > "$TMP/bin_gnutail/tail"
chmod +x "$TMP/bin_gnutail/tail"

echo "# statusline.sh"

out=$(render "$(payload "$TRANSCRIPT" "$REPO")" "$BIN_FULL")
assert_contains "transcript marker wins over .active" "📓 winner" "$out"
assert_not_contains "no ~ prefix when the marker resolved it" "📓 ~" "$out"
assert_contains "branch is shown" "⎇ main" "$out"
assert_contains "model is shown" "M" "$out"

assert_not_contains "SKILL.md <project> placeholder never matches" "<project>" "$out"
assert_not_contains "earlier marker loses to the later one" "first-project" "$out"

out=$(render "$(payload "" "$REPO")" "$BIN_FULL")
assert_contains ".active fallback is marked with ~" "📓 ~hinted" "$out"

rm -f "$REPO/docs/devlog/.active"
out=$(render "$(payload "" "$REPO")" "$BIN_FULL")
assert_contains "no marker and no .active renders a dash" "📓 -" "$out"
printf 'hinted' > "$REPO/docs/devlog/.active"

# Regression: BSD-only `tail -r` made this fall back to .active on Linux.
out=$(render "$(payload "$TRANSCRIPT" "$REPO")" "$TMP/bin_gnutail")
assert_contains "resolves the marker without 'tail -r'" "📓 winner" "$out"

# Regression: `grep -m1 -o` printed every match on the first matching line,
# producing a multi-line status bar.
out=$(render "$(payload "$TWO_ON_ONE" "$REPO")" "$BIN_FULL")
assert_eq "two markers on one line still render one line" "1" "$(printf '%s\n' "$out" | wc -l | tr -d ' ')"

out=$(render "$(payload "$TRANSCRIPT" "$REPO")" "$TMP/bin_nojq")
assert_contains "works without jq (python3 fallback)" "📓 winner" "$out"

out=$(render "$(payload "$TRANSCRIPT" "$REPO")" "$TMP/bin_none")
assert_contains "works without jq and python3 (sed fallback)" "📓 winner" "$out"

out=$(render "$(payload "" "$TMP")" "$BIN_FULL")
assert_not_contains "no branch segment outside a git repo" "⎇" "$out"

echo
echo "# install-statusline.sh"

FRESH="$TMP/cfg_fresh"
mkdir -p "$FRESH"
out=$(CLAUDE_DIR="$FRESH" /bin/sh "$INSTALLER" 2>&1)
assert_eq "fresh install succeeds" "0" "$?"
assert_contains "fresh install smoke-tests the result" "smoke test OK" "$out"
if [ -x "$FRESH/statusline.sh" ]; then pass "installed script is executable"
else fail "installed script is executable" "not executable"; fi

EXIST="$TMP/cfg_exist"
mkdir -p "$EXIST"
cat > "$EXIST/settings.json" <<'EOF'
{ "model": "opus", "permissions": { "allow": ["WebSearch"] },
  "statusLine": { "type": "command", "command": "/bin/sh '/orca/hijack.sh'" } }
EOF
CLAUDE_DIR="$EXIST" /bin/sh "$INSTALLER" >/dev/null 2>&1
keys=$(python3 -c "import json;print(','.join(sorted(json.load(open('$EXIST/settings.json')))))" 2>/dev/null)
assert_eq "installer preserves other settings keys" "model,permissions,statusLine" "$keys"
cmd=$(python3 -c "import json;print(json.load(open('$EXIST/settings.json'))['statusLine']['command'])" 2>/dev/null)
assert_eq "installer takes over a hijacked statusLine" "/bin/sh '$EXIST/statusline.sh'" "$cmd"

CLAUDE_DIR="$EXIST" /bin/sh "$INSTALLER" >/dev/null 2>&1
assert_eq "installer is idempotent" "0" "$?"

QUOTE="$TMP/cfg_it's"
mkdir -p "$QUOTE"
CLAUDE_DIR="$QUOTE" /bin/sh "$INSTALLER" >/dev/null 2>&1
assert_eq "installer refuses a path containing a quote" "1" "$?"
if [ -f "$QUOTE/settings.json" ]; then fail "refused install writes nothing" "settings.json was created"
else pass "refused install writes nothing"; fi

echo
echo "# check-statusline.sh (SessionStart self-repair)"

run_check() { printf '{}' | env "CLAUDE_PLUGIN_ROOT=$ROOT/plugins/vh1981" "CLAUDE_CONFIG_DIR=$1" ${2:+VH1981_STATUSLINE_AUTOREPAIR=$2} /bin/sh "$CHECKER" 2>&1; }

HOOKCFG="$TMP/cfg_hook"
mkdir -p "$HOOKCFG"
printf '{"model":"opus"}\n' > "$HOOKCFG/settings.json"

out=$(run_check "$HOOKCFG")
assert_contains "repairs a machine that never installed the script" "repaired" "$out"
if [ -f "$HOOKCFG/statusline.sh" ]; then pass "hook installs the script"
else fail "hook installs the script" "missing"; fi
cmd=$(python3 -c "import json;print(json.load(open('$HOOKCFG/settings.json'))['statusLine']['command'])" 2>/dev/null)
assert_eq "hook points settings at the installed script" "/bin/sh '$HOOKCFG/statusline.sh'" "$cmd"
assert_eq "hook preserves unrelated keys" "opus" "$(python3 -c "import json;print(json.load(open('$HOOKCFG/settings.json'))['model'])" 2>/dev/null)"

out=$(run_check "$HOOKCFG")
assert_eq "hook is silent when nothing needs repair" "" "$out"

python3 - "$HOOKCFG/settings.json" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p))
d['statusLine']={'type':'command','command':"/bin/sh '/orca/claude-statusline.sh'"}
json.dump(d, open(p,'w'), indent=2)
PY
out=$(run_check "$HOOKCFG")
assert_contains "hook takes statusLine back after orca hijacks it" "repaired" "$out"
cmd=$(python3 -c "import json;print(json.load(open('$HOOKCFG/settings.json'))['statusLine']['command'])" 2>/dev/null)
assert_eq "statusLine points back at our script" "/bin/sh '$HOOKCFG/statusline.sh'" "$cmd"

rm -f "$HOOKCFG/statusline.sh"
out=$(run_check "$HOOKCFG" 0)
assert_eq "VH1981_STATUSLINE_AUTOREPAIR=0 disables repair" "" "$out"
if [ -f "$HOOKCFG/statusline.sh" ]; then fail "opt-out really skips the copy" "script was reinstalled"
else pass "opt-out really skips the copy"; fi

out=$(printf '{}' | env "CLAUDE_PLUGIN_ROOT=/nonexistent" "CLAUDE_CONFIG_DIR=$HOOKCFG" /bin/sh "$CHECKER" 2>&1)
assert_eq "hook exits 0 when the plugin root is missing" "0" "$?"
assert_eq "hook stays quiet when the plugin root is missing" "" "$out"

echo
if [ "$FAILED" = "0" ]; then
  echo "all $COUNT checks passed"
else
  echo "FAILURES present ($COUNT checks run)"
fi
exit "$FAILED"
