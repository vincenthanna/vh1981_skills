#!/bin/sh
# Regression tests for the devlog status line, its installer, and the two
# SessionStart hooks (status line self-repair, default guideline injection).
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
INJECTOR="$ROOT/plugins/vh1981/scripts/inject-guidelines.sh"

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
echo "# inject-guidelines.sh (SessionStart default guidelines)"

run_inject() { printf '{}' | env "CLAUDE_PLUGIN_ROOT=$1" ${2:+VH1981_GUIDELINES=$2} /bin/sh "$INJECTOR" 2>&1; }

out=$(run_inject "$ROOT/plugins/vh1981")
assert_contains "injects the guideline title" "# vh1981 기본 가이드라인" "$out"
assert_contains "points doc-style at this install's absolute path" "$ROOT/plugins/vh1981/guidelines/doc-style.md" "$out"
assert_not_contains "no placeholder survives substitution" "{{GUIDELINES_DIR}}" "$out"
# Every on-demand file core.md points at must ship with the plugin.
refs=$(printf '%s\n' "$out" | grep -o 'guidelines/[A-Za-z0-9._-]*\.md' | sort -u)
missing=""
for r in $refs; do
  [ -f "$ROOT/plugins/vh1981/$r" ] || missing="$missing $r"
done
assert_eq "every guideline file it names exists" "" "$missing"
assert_contains "names the ml-training guideline" "guidelines/ml-training.md" "$refs"
assert_contains "names the shell-pitfalls guideline" "guidelines/shell-pitfalls.md" "$refs"
assert_contains "names the mcp-connectors guideline" "guidelines/mcp-connectors.md" "$refs"

# Large hook output is moved to a file and only a preview reaches the context.
# Bytes over-count Korean text, so this is stricter than a character limit.
size=$(printf '%s' "$out" | wc -c | tr -d ' ')
if [ "$size" -lt 10000 ]; then pass "injected text stays under 10000 bytes ($size)"
else fail "injected text stays under 10000 bytes" "got $size"; fi

# sed replacement metacharacters in the install path must come through literally.
ODD="$TMP/plug&in|dir"
mkdir -p "$ODD/guidelines"
cp "$ROOT/plugins/vh1981/guidelines/core.md" "$ODD/guidelines/"
out=$(run_inject "$ODD")
assert_contains "install path with & and | is substituted literally" "$ODD/guidelines/doc-style.md" "$out"

out=$(run_inject "$ROOT/plugins/vh1981" 0)
assert_eq "VH1981_GUIDELINES=0 disables injection" "" "$out"

out=$(run_inject /nonexistent)
assert_eq "injector exits 0 when the plugin root is missing" "0" "$?"
assert_eq "injector stays quiet when the plugin root is missing" "" "$out"

echo
echo "# kb.py (devlog knowledge base)"

KBPY="$ROOT/plugins/vh1981/skills/kb/scripts/kb.py"
KBT="$TMP/kbt"
mkdir -p "$KBT"
kbr() { (cd "$1" && shift && python3 "$KBPY" --kb "$KBT/kb" "$@" 2>&1); }
mkproj() {
  d="$1/docs/devlog/proj"; mkdir -p "$d/history" "$d/data"
  printf -- '---\nkb:\n  status: active\n  tags: [reid]\n  summary: >-\n    line one\n    line two\n---\n# Proj\n\n## Remaining / Next (summary)\n- [Critical] fix leak\n- [Low] later\n' > "$d/README.md"
  echo "needle finding" > "$d/01_a.md"
  echo "historyonly" > "$d/history/01_h.md"
  echo x > "$d/data/img.jpg"
  printf '<img src="data:image/png;base64,AA">' > "$d/embed.html"
  printf '<p>plain</p>' > "$d/plain.html"
}
git init -q "$KBT/main" && git -C "$KBT/main" -c user.email=t@t -c user.name=t commit -q --allow-empty -m i
git -C "$KBT/main" remote add origin https://github.com/Org/repo.git
git -C "$KBT/main" worktree add -q "$KBT/wt" -b feat 2>/dev/null
git init -q "$KBT/clone" && git -C "$KBT/clone" -c user.email=t@t -c user.name=t commit -q --allow-empty -m i
git -C "$KBT/clone" remote add origin git@github.com:Org/repo.git
mkdir -p "$KBT/plain"
mkproj "$KBT/wt"; mkproj "$KBT/clone"; mkproj "$KBT/plain"
echo "different" > "$KBT/clone/docs/devlog/proj/01_a.md"

python3 "$KBPY" init "$KBT/kb" --no-save >/dev/null 2>&1
idn() { (cd "$1" && python3 "$KBPY" ident | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["name"],d["remote"],d["main_checkout"]==d["top"])'); }
assert_eq "https and git@ remotes name the same repo" "$(idn "$KBT/main" | cut -d' ' -f1-2)" "$(idn "$KBT/clone" | cut -d' ' -f1-2)"
assert_contains "a worktree resolves to its main checkout" "repo github.com/Org/repo False" "$(idn "$KBT/wt")"

out=$(kbr "$KBT/wt" upload proj)
assert_contains "first upload makes the checkout the owner" "[proj] ok  repos/repo/proj" "$out"
assert_eq "images are not uploaded" "" "$(ls "$KBT/kb/repos/repo/proj/data" 2>/dev/null | grep jpg)"
assert_eq "html with embedded images is not uploaded" "no" "$([ -f "$KBT/kb/repos/repo/proj/embed.html" ] && echo yes || echo no)"
assert_eq "plain html is uploaded" "yes" "$([ -f "$KBT/kb/repos/repo/proj/plain.html" ] && echo yes || echo no)"

out=$(kbr "$KBT/clone" upload proj; echo "rc=$?")
assert_contains "another checkout's diverged copy is a conflict" "[proj] conflict" "$out"
assert_contains "conflict lists the differing file" "내용 다름 1개: 01_a.md" "$out"
assert_contains "conflict exits non-zero" "rc=2" "$out"
assert_eq "conflict writes nothing" "needle finding" "$(cat "$KBT/kb/repos/repo/proj/01_a.md")"
assert_contains "NOW.md shows the diverged copy" "다른 사본" "$(cat "$KBT/kb/NOW.md")"
assert_contains "NOW.md carries Critical open items" "[Critical] fix leak" "$(cat "$KBT/kb/NOW.md")"
assert_not_contains "NOW.md drops Low items" "[Low] later" "$(cat "$KBT/kb/NOW.md")"
assert_contains "INDEX.md has the card summary" "line one line two" "$(cat "$KBT/kb/INDEX.md")"

out=$(kbr "$KBT/wt" search needle)
assert_contains "search finds body text" "repos/repo/proj/01_a.md:1: needle finding" "$out"
assert_not_contains "search skips history by default" "historyonly" "$(kbr "$KBT/wt" search historyonly)"
assert_contains "search --all includes history" "history/01_h.md" "$(kbr "$KBT/wt" search historyonly --all)"
assert_contains "cat refuses paths outside the KB tree" "unsafe path" "$(kbr "$KBT/wt" cat ../../etc/passwd)"

rm "$KBT/wt/docs/devlog/proj/plain.html"
out=$(kbr "$KBT/wt" upload proj; echo "rc=$?")
assert_contains "owner deletions wait for --yes" "needs-confirm" "$out"
assert_eq "nothing deleted before --yes" "yes" "$([ -f "$KBT/kb/repos/repo/proj/plain.html" ] && echo yes || echo no)"
kbr "$KBT/wt" upload proj --yes >/dev/null
assert_eq "--yes deletes the vanished file" "no" "$([ -f "$KBT/kb/repos/repo/proj/plain.html" ] && echo yes || echo no)"

out=$(kbr "$KBT/clone" upload proj --take-over --yes)
assert_contains "take-over reports the displaced files" "밀려난 파일" "$out"
assert_eq "take-over writes the new owner's content" "different" "$(cat "$KBT/kb/repos/repo/proj/01_a.md")"
reg=$(cat "$KBT/kb/registry/repos/repo.md")
assert_contains "previous owner is recorded as a copy" '"copies": [' "$reg"

out=$(kbr "$KBT/plain" upload proj; echo "rc=$?")
assert_contains "a checkout without origin must name a topic" "--topic" "$out"
out=$(kbr "$KBT/plain" upload proj --topic notes)
assert_contains "topic upload lands under topics/" "topics/notes/proj" "$out"

(kbr "$KBT/clone" upload proj --yes >/dev/null &) ; kbr "$KBT/clone" upload proj --yes >/dev/null; sleep 1
python3 -c "import json;json.load(open('$KBT/kb/.kb/manifest/repos/repo/proj.json'))" 2>/dev/null
assert_eq "concurrent uploads leave a valid manifest" "0" "$?"
assert_eq "no lock is left behind" "no" "$([ -d "$KBT/kb/.kb/lock" ] && echo yes || echo no)"

LP="$KBT/plain/docs/devlog/proj"
cat > "$LP/02_dated.md" <<'MD'
# Dated

### Finding 3: cache miss explained (2026-09-03)

- note: 2026-09-20 mentioned mid-sentence

## Progress

### Done
- 2026-09-02: measured baseline
- 2026-09-10: fixed the leak
- undated old item

### Remaining / Next
- [High] rerun eval (added 2026-09-05)
MD
printf '# h\n\n## Changes\n- 2026-09-04: edited config\n' > "$LP/history/02_h.md"
out=$(cd "$KBT/plain" && python3 "$KBPY" log --local --since 2026-09-01 --until 2026-09-05)
assert_contains "log picks a dated Done bullet" "done · 02_dated.md:10 · measured baseline" "$out"
assert_contains "log picks a dated Finding heading" "finding · 02_dated.md:3 · Finding 3: cache miss explained" "$out"
assert_contains "log picks a dated history bullet" "history · history/02_h.md:4 · edited config" "$out"
assert_contains "log picks an added Remaining item" "added · 02_dated.md:15" "$out"
assert_not_contains "log honours --until" "fixed the leak" "$out"
assert_not_contains "a mid-sentence date is not a work entry" "mid-sentence" "$(cd "$KBT/plain" && python3 "$KBPY" log --local)"
assert_contains "--loose takes mid-sentence dates too" "mention" "$(cd "$KBT/plain" && python3 "$KBPY" log --local --loose --since 2026-09-20)"
kbr "$KBT/plain" upload proj --topic notes --yes >/dev/null
assert_contains "log reads the whole KB without --local" "topics/notes/proj" "$(kbr "$KBT/plain" log --since 2026-09-10 --until 2026-09-10)"

where() { (cd "$KBT/plain" && env -u VH1981_KB -u VH1981_KB_DEFAULT HOME="$KBT/home" "$@" python3 "$KBPY" where --configured 2>&1; echo "rc=$?"); }
out=$(where)
assert_contains "built-in default is the ds35 KB" "ssh://yeonhui@192.168.100.135/home/yeonhui/kb  (출처: built-in default)" "$out"
assert_contains "built-in default alone is not 'configured'" "rc=1" "$out"
out=$(where VH1981_KB_DEFAULT=/srv/kb)
assert_contains "VH1981_KB_DEFAULT replaces the built-in default" "/srv/kb  (출처: built-in default)" "$out"
mkdir -p "$KBT/home/.config/vh1981" && printf '%s' "$KBT/kb" > "$KBT/home/.config/vh1981/kb"
out=$(where)
assert_contains "init's config file outranks the default" "rc=0" "$out"
out=$(where VH1981_KB=/elsewhere)
assert_contains "VH1981_KB outranks the config file" "/elsewhere  (출처: VH1981_KB)" "$out"
out=$(cd "$KBT/plain" && HOME="$KBT/home" python3 "$KBPY" --kb "ssh://nobody@unreachable.invalid$KBT/kb" where 2>&1)
assert_contains "an ssh location whose KB is on this machine is used locally" "이 머신의 로컬 경로" "$out"

if ssh -o BatchMode=yes -o ConnectTimeout=3 localhost true 2>/dev/null; then
  out=$( (cd "$KBT/wt" && python3 "$KBPY" --kb "ssh://localhost$KBT/kb" search needle 2>&1) )
  assert_contains "search works over ssh" "repos/repo/proj" "$out"
else
  echo "skip ssh transport (no passwordless ssh to localhost)"
fi

echo
if [ "$FAILED" = "0" ]; then
  echo "all $COUNT checks passed"
else
  echo "FAILURES present ($COUNT checks run)"
fi
exit "$FAILED"
