#!/usr/bin/env bash
# 보고서 사이트를 띄운다. 멱등이므로 여러 번 불러도 안전하다.
# @reboot cron 에 걸어두면 재부팅 후에도 복구된다.
#
#   serve_devlog.sh [문서루트] [포트]
#
# 생존 확인은 PID 파일 + 포트 리스닝이다. `pgrep -f` 는 이 스크립트 자신의
# 명령줄을 매치해서, 뜨지도 않은 서버를 "실행 중"이라고 보고한다. 실제로 당했다.
# Linux 와 macOS 모두에서 돈다: macOS 에는 setsid, ss, `hostname -I` 가 없다.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${1:-${REPORT_ROOT:-$PWD/docs/devlog}}"
PORT="${2:-${REPORT_PORT:-8800}}"
HOST="${REPORT_HOST:-0.0.0.0}"
PIDFILE="/tmp/serve_devlog.$PORT.pid"
LOG="/tmp/serve_devlog.$PORT.log"
PY="${PYTHON:-python3}"

listening() {
  if command -v ss >/dev/null 2>&1; then
    ss -ltn 2>/dev/null | grep -q "[:.]$PORT "
  elif command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1
  else
    "$PY" -c "import socket,sys;s=socket.socket();s.settimeout(1);sys.exit(s.connect_ex(('127.0.0.1',$PORT)))"
  fi
}

url() {
  if [ "$HOST" = "127.0.0.1" ]; then echo "http://127.0.0.1:$PORT/"; else echo "http://$(lan_ip):$PORT/"; fi
}

lan_ip() {
  local ip
  ip=$(hostname -I 2>/dev/null | awk '{print $1}')
  [ -n "$ip" ] || ip=$(ipconfig getifaddr en0 2>/dev/null)
  [ -n "$ip" ] || ip=$(ipconfig getifaddr en1 2>/dev/null)
  echo "${ip:-localhost}"
}

[ -d "$ROOT" ] || { echo "문서 루트가 없다: $ROOT"; exit 1; }
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null && listening; then
  echo "이미 실행 중 — $(url)  (pid $(cat "$PIDFILE"))"; exit 0
fi
if listening; then
  echo "포트 $PORT 를 다른 프로세스가 쓰고 있다 — 다른 포트를 넘겨라"; exit 1
fi

# setsid 가 있으면 세션을 분리하고, 없으면(macOS) nohup 만으로 띄운다.
DETACH=""; command -v setsid >/dev/null 2>&1 && DETACH="setsid"
$DETACH nohup "$PY" "$HERE/serve_devlog.py" --root "$ROOT" --port "$PORT" --host "$HOST" \
  >> "$LOG" 2>&1 < /dev/null &
echo $! > "$PIDFILE"
for _ in $(seq 1 20); do
  sleep 1
  if listening; then
    echo "서비스 중 — $(url)  (pid $(cat "$PIDFILE"), 로그 $LOG)"
    exit 0
  fi
  kill -0 "$(cat "$PIDFILE")" 2>/dev/null || break
done
echo "포트 $PORT 바인딩 실패 — $LOG 확인"; tail -5 "$LOG" 2>/dev/null; exit 1
