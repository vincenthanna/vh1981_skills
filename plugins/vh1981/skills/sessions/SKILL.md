---
name: sessions
description: repo 에서 tmux 창마다 띄워 두었던 Claude 세션들을, tmux 나 서버가 죽은 뒤 같은 tmux 세션·창 이름·디렉터리로 다시 띄우고 각 창에서 그 대화를 이어 간다(claude --resume). vh1981 hook 이 세션마다 남긴 <repo>/.claude/sessions.md 와 기록을 읽어 목록, 상태(실행 중/중단/다른 머신), 최근 한 일 두 줄을 보여 주고 복구한다. 사용자는 그 repo 디렉터리에서 claude 를 새로 띄워 이 스킬을 부른다. Use when the user wants to see which Claude sessions were open in this repo, or to bring back sessions or tmux windows lost when tmux, the terminal or the host died. Trigger phrases include "sessions", "세션 목록", "세션 복구", "세션 되살려", "tmux 복구", "tmux 창 복구", "창 다시 띄워", "죽은 세션 살려", "restore sessions", "restore tmux". Do NOT use for resuming only the current conversation (claude --resume), for devlog work history (use vh1981:devlog), or for what is in progress across repos (use vh1981:kb status).
---

# sessions: tmux 창의 Claude 세션 되살리기

vh1981 플러그인의 `sessions.py` hook 은 세션 시작, prompt, 답을 마칠 때마다 그 repo 의 `.claude/sessions.md` 와 `.claude/sessions/<세션 id>.json` 을 고쳐 쓴다. 이 스킬은 그 기록으로 세션을 다시 띄운다. 사용자는 보통 tmux 나 서버가 죽은 뒤 그 repo 디렉터리에서 claude 를 새로 띄워 이 스킬을 부른다.

```
S="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sessions.py"
$S list                                   # 이 repo 의 세션, 상태, 최근 한 일
$S restore --dry-run [--only <id 앞부분|창 이름>,...] [--host <머신>]
$S restore [--only ...] [--host <머신>]   # tmux 창을 만들고 claude --resume 을 입력
```

디렉터리 인자를 생략하면 현재 작업 디렉터리가 속한 repo 최상위를 쓴다. 다른 repo 면 경로를 첫 인자로 준다.

## 할 일 고르기

| 요청 | 할 일 |
|---|---|
| 목록, 무슨 세션이 있었는지 | `list` 만 실행하고 보고한다. 복구하지 않는다 |
| 복구, 되살려, 다시 띄워 | 아래 "복구" 를 끝까지 한다. 복구 요청 자체가 승인이므로 따로 묻지 않는다 |
| 특정 창이나 세션만 | `--only` 에 창 이름이나 세션 id 앞부분을 쉼표로 이어 준다 |

## 복구

1. `$S list` 로 상태를 본다. 상태 뜻은 다음과 같다.
   - `실행 중`: 이 머신에서 그 claude 프로세스가 아직 살아 있다. 이 스킬을 부른 지금 세션도 여기에 나온다. 복구하지 않는다.
   - `중단`: 이 머신의 세션인데 프로세스가 없다. 복구 대상이다.
   - `다른 머신`: 다른 host 에서 띄운 세션이다. 기본으로는 복구하지 않는다.
2. 이 머신에 `중단` 이 없고 다른 머신 세션만 있으면, 그 머신이 죽어서 여기서 이어 가려는 것인지 사용자에게 묻는다. 그렇다고 하면 `--host <머신>` 을 붙인다. `/home` 이 NFS 라 대화 기록은 어느 머신에서나 이어진다.
3. `$S restore --dry-run ...` 으로 만들 창과 명령을 확인한 뒤 같은 인자로 `$S restore ...` 를 실행한다.
4. 띄운 결과를 확인한다. 몇 초 기다린 뒤 창마다 화면을 읽어, claude 가 대화를 불러왔는지 본다. `No conversation found` 같은 오류가 보이면 실패로 보고한다.
   ```bash
   tmux list-windows -t <tmux 세션> -F '#{window_index} #{window_name} #{pane_id} #{pane_current_path}'
   tmux capture-pane -p -t <pane_id> | tail -15
   ```
5. 보고한다. 되살린 창(tmux 세션:번호 이름, 디렉터리, 최근 한 일 한 줄), 건너뛴 세션과 이유, 실패한 것, 붙는 명령(`tmux attach -t <tmux 세션>`)을 쓴다.

## 알아 둘 것

- 복구는 원래 tmux 세션 이름, 창 번호, 창 이름, 디렉터리를 쓴다. 창 번호가 이미 차 있으면 뒤에 붙인다. tmux 정보가 없던 세션은 `claude-restore` 세션에 디렉터리 이름으로 창을 만든다.
- 되살린 claude 는 원래 실행 플래그(예: `--dangerously-skip-permissions`)를 그대로 받는다. `--resume`·`--continue`·처음 prompt 는 뺀다.
- 복구한 세션의 옛 기록은 지운다. 되살아난 세션이 hook 으로 새 기록을 쓴다.
- `.claude/sessions.md` 와 기록 파일은 손으로 고치지 않는다. hook 이 덮어쓴다.
- 목록에 `tmux 응답 없음` 이 나오면 그 세션의 hook 이 tmux 서버에 닿지 못한 것이다. `TMUX_TMPDIR` 가 NFS 홈 아래라 여러 머신이 같은 소켓 파일을 덮어쓸 때 생긴다. 사용자에게 알리고, 소켓을 머신마다 다른 곳(예: `/tmp`)에 두도록 권한다.
- `claude -p` 와 SDK 로 띄운 비대화형 세션(cron 포함)은 되살릴 창이 없어 기록하지 않는다. 지금 세션이 그런 실행이면 목록에 없는 것이 정상이다.
- 기록은 14일 동안 갱신이 없으면 지워진다. 기록이 아예 없으면 그 repo 에서 세션을 띄울 때 플러그인이 설치되어 있지 않았거나 `VH1981_SESSIONS=0` 이었던 것이다.
