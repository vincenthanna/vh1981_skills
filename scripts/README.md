# statusline.sh — devlog 상태줄

Claude Code 상태줄에 현재 세션의 devlog 프로젝트를 표시하는 스크립트입니다. `statusLine` 은
`settings.json` 레벨 설정이라 플러그인 매니페스트가 실어 나르지 못하고, orca 같은 다른 설치 스크립트가
덮어쓰기도 합니다. 두 경우 모두 에러 없이 상태줄만 조용히 사라지기 때문에, `vh1981` 플러그인이
SessionStart hook 으로 매 세션 자동 복구합니다. 수동 설치가 필요한 경우를 위해
`./scripts/install-statusline.sh` 도 남겨 두었습니다. macOS 와 Linux 양쪽에서 동작하며, 회귀 테스트는
`./scripts/tests/run.sh` 가 두 플랫폼 모두에서 검증합니다.

## 파일 배치

정본은 플러그인 안에 있고, repo 루트의 `scripts/statusline.sh` 는 그곳을 가리키는 symlink 입니다.
`prompts/agents` 가 `plugins/prompts-pack/agents` 를 가리키는 것과 같은 방향입니다.

```
plugins/vh1981/scripts/statusline.sh        # 정본. 플러그인이 실어 나름
plugins/vh1981/scripts/check-statusline.sh  # SessionStart 자동 복구
plugins/vh1981/hooks/hooks.json             # 위 스크립트를 SessionStart 에 등록
scripts/statusline.sh -> ../plugins/vh1981/scripts/statusline.sh
scripts/install-statusline.sh               # 수동 설치
scripts/tests/run.sh                        # 회귀 테스트
```

## 자동 복구

`vh1981` 플러그인이 설치되어 있으면 세션이 시작될 때마다 다음 두 가지를 확인하고 어긋난 것만 고칩니다.

| 확인 | 복구 |
|---|---|
| `~/.claude/statusline.sh` 가 없거나 플러그인이 실어 온 버전과 다름 | 플러그인 버전으로 복사 |
| `settings.json` 의 `statusLine` 이 그 파일을 가리키지 않음 | 해당 키만 다시 씀 |

고칠 것이 없으면 아무것도 출력하지 않습니다. 무언가 고쳤을 때만 한 줄을 남깁니다.

```
vh1981: devlog status line repaired (script+settings). Restart the session to see it.
```

`settings.json` 은 임시 파일에 쓴 뒤 rename 하므로, 여러 세션이 동시에 시작해도 반쯤 쓰인 파일이
보이지 않습니다. 다른 키는 보존하고 `statusLine` 만 교체하며, 덮어쓰기 전에
`settings.json.bak-autorepair` 로 백업합니다.

자동 복구를 끄려면 환경변수를 설정합니다.

```bash
export VH1981_STATUSLINE_AUTOREPAIR=0
```

## 수동 설치

플러그인 없이 스크립트만 쓰거나, 자동 복구 전에 즉시 적용하고 싶을 때 사용합니다.

```bash
./scripts/install-statusline.sh
```

설치 스크립트가 수행하는 일은 세 가지입니다. 먼저 `scripts/statusline.sh` 를 `~/.claude/statusline.sh`
로 복사합니다. 그다음 `~/.claude/settings.json` 의 `statusLine` 키를 갱신하며, 이때 나머지 키는 그대로
보존합니다. 마지막으로 합성 payload 를 흘려 넣어 상태줄이 정확히 한 줄을 출력하는지 확인하고, 아무것도
출력하지 않으면 실패로 처리합니다.

기존 파일은 덮어쓰기 전에 백업합니다.

```
~/.claude/statusline.sh.bak-<타임스탬프>
~/.claude/settings.json.bak-<타임스탬프>
```

설치 후에는 Claude Code 세션을 재시작해야 반영됩니다.

설치 위치를 바꾸려면 `CLAUDE_DIR` 를 지정합니다.

```bash
CLAUDE_DIR=/opt/claude-config ./scripts/install-statusline.sh
```

`settings.json` 을 편집하려면 python3 또는 jq 중 하나가 필요합니다. 둘 다 없으면 설치 스크립트는
직접 붙여 넣을 JSON 블록을 출력하고 종료합니다.

## 상태줄에 표시되는 것

```
vh1981_skills | ⎇ main | 📓 my-project | Opus 5
```

왼쪽부터 현재 디렉토리 이름, git 브랜치, devlog 프로젝트, 모델 표시 이름입니다. git 저장소가 아니면
브랜치 항목이 빠집니다. devlog 프로젝트를 찾지 못하면 `📓 -` 로 표시합니다.

## devlog 프로젝트 해석 순서

`devlog` SKILL.md 의 "Active Project" 규칙 중 앞 두 단계를 따릅니다.

| 순서 | 출처 | 표시 |
|---|---|---|
| 1 | 이 세션 transcript 의 마지막 `[devlog/active: <name>]` 마커 | `📓 name` |
| 2 | `<repo>/docs/devlog/.active` | `📓 ~name` |

마커를 우선하는 이유는 `.active` 가 동시에 실행 중인 다른 세션이 언제든 덮어쓸 수 있는 힌트이기
때문입니다. `.active` 에서 온 값에는 `~` 접두사를 붙여 이 세션이 직접 만든 값이 아님을 구분합니다.

SKILL.md 본문이 transcript 에 실려 들어가도 문제가 없습니다. 마커 패턴이 `[A-Za-z0-9._-]` 만
받으므로 문서 예시에 등장하는 `<project>` 같은 placeholder 는 매칭되지 않습니다.

## 이식성

원본 스크립트에는 macOS 에서만 동작하는 구문이 있었고, 아래와 같이 교체했습니다.

| 항목 | 이전 | 현재 |
|---|---|---|
| transcript 역방향 조회 | `tail -r` (BSD 전용) | `grep -o ... \| tail -n 1` |
| payload 파싱 | jq 필수 | jq → python3 → sed 순서로 폴백 |
| 설치 경로 | `/Users/<user>/...` 하드코딩 | `$HOME` 에서 유도 |

`tail -r` 은 GNU coreutils 에 없어서 Linux 에서 조용히 실패했고, 그러면 transcript 마커를 못 읽고
`.active` 폴백으로 떨어졌습니다. `grep -o | tail -n 1` 로 바꾸면서 한 줄에 마커가 여러 개 있을 때
상태줄이 두 줄로 깨지던 문제도 함께 없어졌습니다. 이전 구현은 `grep -m1 -o` 를 썼는데, `-m1` 은
매칭되는 줄 하나에서 멈추지만 `-o` 는 그 줄 안의 모든 매칭을 각각 출력하기 때문입니다.

## 테스트

`scripts/tests/run.sh` 가 상태줄, 설치 스크립트, 자동 복구 hook 을 검증합니다. 외부 의존성이 없고
`mktemp -d` 아래에서만 동작하므로 실제 `~/.claude` 를 건드리지 않습니다.

```bash
./scripts/tests/run.sh
```

각 케이스는 실제로 발생했던 버그이거나 hook 이 의존하는 계약입니다. 특히 두 건은 macOS 에서는
통과하고 Linux 에서만 깨졌던 것이라, `.github/workflows/statusline.yml` 이 `ubuntu-latest` 와
`macos-latest` 양쪽에서 이 스위트를 돌립니다. 같은 workflow 가 shellcheck 와 매니페스트 JSON 검증도
수행하며, hook 이 참조하는 파일이 플러그인 안에 실제로 있는지까지 확인합니다.

## orca 텔레메트리

`~/.orca/agent-hooks/claude-statusline.sh` 가 실행 가능한 상태로 존재하면 스크립트가 payload 를 그대로
넘깁니다. orca 는 stdout 에 아무것도 쓰지 않으므로 상태줄 표시에는 영향이 없습니다. 파일이 없으면
조용히 건너뜁니다.

orca 설치 스크립트가 `statusLine` 을 자기 것으로 되돌릴 수 있습니다. devlog 표시가 사라지면
`settings.json` 의 `statusLine.command` 가 orca 경로를 가리키는지 먼저 확인하십시오.

## 문제 해결

증상별로 원인이 다릅니다.

| 증상 | 원인 | 조치 |
|---|---|---|
| 상태줄 자체가 안 보임 | statusLine 커맨드가 stdout 에 아무것도 못 냄 | 아래 직접 실행으로 확인 |
| `📓 -` 로만 나옴 | 마커도 `.active` 도 없음 | 정상. devlog 명령을 실행하면 채워짐 |
| `📓 ~name` 이 계속 유지됨 | transcript 마커를 못 읽음 | Linux 에서 구버전을 쓰는지 확인 후 재설치 |
| 상태줄이 두 줄로 깨짐 | 구버전의 `grep -m1 -o` 버그 | 재설치 |
| 매 세션 "repaired" 가 반복됨 | 다른 도구가 `statusLine` 을 계속 되돌림 | 그 도구의 설치 스크립트를 확인 |

상태줄을 직접 실행해 확인하는 방법입니다.

```bash
printf '{"transcript_path":"","workspace":{"current_dir":"%s"},"model":{"display_name":"test"}}' "$PWD" \
  | /bin/sh ~/.claude/statusline.sh
```

한 줄이 출력되면 스크립트는 정상입니다. 그런데도 Claude Code 화면에 안 보이면 세션 재시작이
필요하거나 `settings.json` 의 `statusLine.command` 경로가 이 파일을 가리키지 않는 경우입니다.
