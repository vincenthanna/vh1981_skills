#!/usr/bin/env bash
# Install the daily / weekly log on the machine that holds the KB.
#
#   install.sh [KB_DIR]          # default: the local KB that `kb.py where` resolves to
#   install.sh --uninstall [KB_DIR]
#
# Idempotent. It copies the runner, kb.py and the report server into
# <kb>/.kb/bin and this skill into <kb>/.kb/kb-report (cron must not depend on
# the plugin cache path or version), records the claude binary to use, and
# replaces its own crontab lines (marked "# vh1981-kb-report"):
#
#   30 6 * * *   daily log for yesterday
#   0 22 * * 0   weekly log for the week ending that Sunday
#   @reboot      report server on port ${KB_REPORT_PORT:-8800}, root = KB
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUG="$(cd "$HERE/../../.." && pwd)"
MARK="# vh1981-kb-report"
PORT="${KB_REPORT_PORT:-8800}"

UNINSTALL=0
[ "${1:-}" = "--uninstall" ] && { UNINSTALL=1; shift; }

KB="${1:-}"
if [ -z "$KB" ]; then
  KB=$(python3 "$PLUG/skills/kb/scripts/kb.py" where | awk '{print $1}')
fi
case "$KB" in ssh://*) echo "KB 가 이 머신에 없다 ($KB). KB 가 있는 머신에서 실행한다"; exit 1 ;; esac
[ -f "$KB/KB.md" ] && [ -d "$KB/.kb" ] || { echo "KB 가 아니다: $KB"; exit 1; }
KB="$(cd "$KB" && pwd)"

current=$(crontab -l 2>/dev/null | grep -v "$MARK" || true)
if [ "$UNINSTALL" = 1 ]; then
  printf '%s\n' "$current" | sed '/^$/d' | crontab -
  echo "crontab 에서 kb-report 줄을 지웠다. 서버 중지: kill \"\$(cat /tmp/serve_devlog.$PORT.pid)\""
  exit 0
fi

# Pick a claude that supports skills. Some hosts carry a stale global npm install
# (1.x) ahead of the native one on PATH, so prefer ~/.local/bin and check the version.
CLAUDE="${KB_REPORT_CLAUDE:-}"
for c in "$CLAUDE" "$HOME/.local/bin/claude" "$(command -v claude 2>/dev/null || true)"; do
  [ -n "$c" ] && [ -x "$c" ] || continue
  v=$("$c" --version 2>/dev/null | awk '{print $1}')
  [ "${v%%.*}" -ge 2 ] 2>/dev/null && { CLAUDE="$c"; break; }
done
[ -x "${CLAUDE:-}" ] || { echo "버전 2 이상의 claude 를 찾지 못했다. KB_REPORT_CLAUDE=<경로> 로 지정한다"; exit 1; }

mkdir -p "$KB/.kb/bin" "$KB/.kb/logs" "$KB/reports/daily" "$KB/reports/weekly" "$KB/reports/.data"
cp "$PLUG/skills/kb/scripts/kb.py" "$KB/.kb/bin/kb.py"
cp "$PLUG/skills/techreport/scripts/serve_devlog.py" "$PLUG/skills/techreport/scripts/serve_devlog.sh" "$KB/.kb/bin/"
cp "$HERE/run.sh" "$KB/.kb/bin/kb-report-run.sh"
mkdir -p "$KB/.kb/kb-report/templates"
cp "$HERE/../SKILL.md" "$KB/.kb/kb-report/SKILL.md"
cp "$HERE/../templates/log.html" "$KB/.kb/kb-report/templates/log.html"
cp "$PLUG/guidelines/output-principles.md" "$KB/.kb/kb-report/output-principles.md"
chmod +x "$KB/.kb/bin/"*.sh "$KB/.kb/bin/kb.py"
printf '%s\n' "$CLAUDE" > "$KB/.kb/claude-path"

LOG="$KB/.kb/logs/kb-report.log"
{
  [ -n "$current" ] && printf '%s\n' "$current"
  echo "30 6 * * * $KB/.kb/bin/kb-report-run.sh daily >> $LOG 2>&1  $MARK daily"
  echo "0 22 * * 0 $KB/.kb/bin/kb-report-run.sh weekly >> $LOG 2>&1  $MARK weekly"
  echo "@reboot bash $KB/.kb/bin/serve_devlog.sh $KB $PORT >> $KB/.kb/logs/serve.log 2>&1  $MARK serve"
} | sed '/^$/d' | crontab -

bash "$KB/.kb/bin/serve_devlog.sh" "$KB" "$PORT" || true
echo
echo "설치 완료"
echo "  KB:      $KB"
echo "  claude:  $CLAUDE ($("$CLAUDE" --version 2>/dev/null | head -1))"
echo "  cron:    매일 06:30 daily(어제) · 일요일 22:00 weekly · 재부팅 시 서버"
echo "  로그:    $LOG"
echo "  수동 실행: $KB/.kb/bin/kb-report-run.sh daily [YYYY-MM-DD]"
