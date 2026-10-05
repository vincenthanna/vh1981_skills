#!/usr/bin/env bash
# Cron entry point for the knowledge-base daily / weekly log.
# install.sh copies this file to <kb>/.kb/bin/kb-report-run.sh.
#
#   kb-report-run.sh daily  [YYYY-MM-DD]   # default: yesterday
#   kb-report-run.sh weekly [YYYY-MM-DD]   # week ending that day; default: today
#
# It makes sure the report server is up, then runs headless claude in the KB
# directory with only the tools the kb-report skill needs. Writes outside the
# KB directory are refused (acceptEdits applies only to the working directory).
set -uo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KB="$(cd "$HERE/../.." && pwd)"
MODE="${1:-daily}"
PORT="${KB_REPORT_PORT:-8800}"
CLAUDE="${KB_REPORT_CLAUDE:-$(cat "$KB/.kb/claude-path" 2>/dev/null)}"
ts() { date '+%Y-%m-%d %H:%M:%S'; }
day() { date -d "$1" +%F 2>/dev/null || date -j -v"$2" +%F; }

[ -x "$CLAUDE" ] || { echo "$(ts) FAIL claude not executable: '$CLAUDE' (rerun install.sh)"; exit 1; }

case "$MODE" in
  daily)  D="${2:-$(day yesterday -1d)}"; OUT="$KB/reports/daily/$D.html"; ARGS="daily $D" ;;
  weekly) D="${2:-$(date +%F)}"; ARGS="weekly $D"; OUT="" ;;
  *) echo "usage: $0 daily|weekly [YYYY-MM-DD]"; exit 2 ;;
esac

# install.sh copies the skill next to the KB, so a run does not depend on which
# plugin version this host has installed. Point claude at that copy explicitly.
SKILL="${KB_REPORT_SKILL:-$KB/.kb/kb-report/SKILL.md}"
[ -f "$SKILL" ] || { echo "$(ts) FAIL skill copy missing: $SKILL (rerun install.sh)"; exit 1; }

bash "$HERE/serve_devlog.sh" "$KB" "$PORT" >/dev/null 2>&1 || echo "$(ts) WARN report server did not start"

cd "$KB" || exit 1
TO=""; command -v timeout >/dev/null 2>&1 && TO="timeout 1800"
echo "$(ts) START $ARGS (skill $SKILL)"
$TO "$CLAUDE" -p "kb-report 스킬을 실행한다: $ARGS
스킬 본문은 $SKILL 이다. Read로 읽고 그대로 따른다. 스킬의 '<이 skill 디렉토리>' 는 $(dirname "$SKILL") 다.
이 실행은 cron이 띄운 무인 실행이다. 질문하지 말고 끝까지 진행한다." \
  --allowedTools "Bash(python3 $KB/.kb/bin/kb.py:*)" "Bash(bash $KB/.kb/bin/serve_devlog.sh:*)" \
                 "Read" "Write" "Edit" "Glob" "Grep" \
  --permission-mode acceptEdits
rc=$?
if [ "$MODE" = "weekly" ]; then
  OUT=$(ls -1t "$KB"/reports/weekly/*.html 2>/dev/null | head -1)
fi
if [ "$rc" -eq 0 ] && [ -n "$OUT" ] && [ -f "$OUT" ] && [ "$(find "$OUT" -mmin -60 2>/dev/null)" ]; then
  echo "$(ts) OK $ARGS -> $OUT"
else
  echo "$(ts) FAIL $ARGS (claude exit $rc, output ${OUT:-none})"
  exit 1
fi
