# vh1981_skills

Claude Code용 개발 워크플로우 스킬 / 프롬프트 묶음입니다.

## 빠른 시작 — 다른 Claude Code 인스턴스에서 사용하기

이 레포의 prompts를 다른 Claude Code 인스턴스에서 쓰는 방법은 두 가지입니다.

**1) Plugin marketplace로 설치 (권장)**

Claude Code 세션 안에서:

```
/plugin marketplace add git@github.com:vincenthanna/vh1981_skills.git
/plugin install prompts-pack      # agents + commands 일괄 설치
/plugin install vh1981            # devlog / worklog / prjdocs skill
```

`prompts-pack` 설치 후:

- `prompts/agents/*.md`의 subagent들이 자동 등록되어 Agent 도구에서 호출 가능 (`debugger`, `code-reviewer`, `backend-architect` 등)
- `prompts/commands/*.md`의 slash command를 바로 사용 (`/bug-fix`, `/pr-audit`, `/verify`, `/analyze`, `/improve-prompt`, `/search-prompt`, `/write-report`)

**2) Clone 후 수동 참조**

플러그인 없이 파일만 참조하고 싶다면:

```bash
git clone git@github.com:vincenthanna/vh1981_skills.git ~/repos/vh1981_skills
```

- 프롬프트 본문에서 `@~/repos/vh1981_skills/prompts/baseline.md` 처럼 직접 첨부
- 또는 개별 agent를 사용자 레벨로 활성화:
  ```bash
  mkdir -p ~/.claude/agents
  ln -s ~/repos/vh1981_skills/plugins/prompts-pack/agents/debugger.md ~/.claude/agents/debugger.md
  ```
- AI 참고 문서 (`prompts/ai-reference/`, `prompts/baseline.md`, `prompts/commit_rules.md`, `prompts/translate_to_kr.md`, `prompts/code_visualization.md`)는 plugin에 포함되지 않으므로 이 방식으로 참조합니다.

## Plugins

### prompts-pack

`prompts/agents/`와 `prompts/commands/`를 하나의 플러그인으로 묶은 것입니다. 디렉토리 구조상 `plugins/prompts-pack/agents`, `plugins/prompts-pack/commands`가 원본이며, 호환을 위해 `prompts/agents`와 `prompts/commands`는 해당 위치로의 심볼릭 링크입니다.

포함된 agent (`/agents` 또는 Agent 도구로 호출):

`api-documenter`, `backend-architect`, `bash-pro`, `cloud-architect`, `code-reviewer`, `data-engineer`, `database-architect`, `database-optimizer`, `debugger`, `deployment-engineer`, `docs-architect`, `error-detective`, `fastapi-pro`, `frontend-developer`, `kubernetes-architect`, `observability-engineer`, `performance-engineer`, `python-pro`, `security-auditor`, `test-automator`, `typescript-pro`

포함된 slash command:

`/analyze`, `/bug-fix`, `/build_prompt`, `/fsd`, `/improve-prompt`, `/pr-audit`, `/search-prompt`, `/verify`, `/write-report`

`/build_prompt <요청사항>` — plugin에 포함된 `lib/prompt-composer-system/trigger.md` 본문을 그대로 실행하면서 `<요청사항>`을 `[Rough request]` 아래에 자동으로 붙입니다. 이 repo 안에서는 같은 파일을 `prompts/prompt-composer-system/trigger.md` 심볼릭 링크로도 볼 수 있습니다.

`/fsd <목표>` — Full Self-Development의 계획+인계 절반. 목표를 multi-agent로 조사·계획하고 격리된 git worktree + 자기완결적 handoff 문서를 만들어, 새 세션이 handoff만으로 개발→리뷰→검증→PR을 끝까지 실행할 수 있게 인계합니다 (구현은 하지 않음).

### vh1981

`/plugin install vh1981` 하나로 아래 3개 skill이 모두 설치됩니다.

### devlog (통합 스킬)

프로젝트 조사 문서와 작업 기록을 `docs/devlog/<project>/`에 통합 관리합니다. worklog + prjdocs의 통합 버전입니다.

**명령어:**

| 명령 | 설명 |
|------|------|
| `/devlog create <project>` | 새 프로젝트 생성 (조사 문서 + 작업 기록 디렉토리) |
| `/devlog list` | 프로젝트 목록 조회 |
| `/devlog select <project>` | 프로젝트 선택 (활성화) |
| `/devlog update` | 조사 문서 + 작업 기록 동시 갱신 |
| `/devlog update <instructions>` | 지시사항에 따라 조사 수행 후 갱신 |
| `/devlog upload [<project>] [--to <path>]` | 외부 knowledge-base repo로 프로젝트 복사 (target 경로는 `docs/devlog/.upload-target`에 자동 저장) |

**디렉토리 구조:**

```
docs/devlog/<project>/
  01_<topic>.md          ← 조사/분석 문서
  history/
    01_<topic>.md        ← 작업 기록
```

### worklog

세션 작업 기록을 `docs/history/<subject>/` 경로에 마크다운 파일로 관리합니다.

**명령어:**

| 명령 | 설명 |
|------|------|
| `/worklog create <subject>` | 새 작업 로그 생성 |
| `/worklog list` | 기존 작업 로그 목록 조회 |
| `/worklog select <subject>` | 작업 로그 선택 (활성화) |
| `/worklog update` | 활성 작업 로그에 진행 내용 추가 |

### prjdocs

프로젝트 주제에 대한 심층 조사 결과를 `docs/projects/<project>/` 경로에 구조화된 분석 보고서로 관리합니다.

**명령어:**

| 명령 | 설명 |
|------|------|
| `/prjdocs create <project>` | 새 프로젝트 문서 생성 |
| `/prjdocs select <project>` | 프로젝트 문서 선택 (활성화) |
| `/prjdocs update` | 활성 프로젝트에 조사 결과 추가 |
| `/prjdocs update <instructions>` | 지시사항에 따라 조사 수행 후 결과 추가 |

### md-tidy

markdown 파일 또는 디렉토리를 **보수적으로(최소 diff)** 정리합니다. 코드블록 내부는 건드리지 않고
공백·빈 줄을 정돈하고, 닫히지 않은 코드펜스·깨진 표·링크 등 깨진 문법을 고칩니다. 텍스트·코드·URL·수치
같은 내용은 바꾸지 않고 공백과 구문만 손봅니다.

**사용:**

| 입력 | 동작 |
|------|------|
| `/md-tidy <파일.md>` | 해당 파일 하나를 정리 |
| `/md-tidy <디렉토리>` | 하위까지 재귀로 모든 `*.md` 정리 |
| `/md-tidy` | 세션에서 방금 다룬 md 를 대상으로 (불분명하면 확인) |

공백/빈 줄 정리는 `plugins/vh1981/skills/md-tidy/scripts/normalize_whitespace.py`(결정론적·멱등)가,
깨진 문법 수정은 에이전트가 판단해 처리하며, 파일을 직접 수정한 뒤 파일별 변경 요약을 보고합니다.

## AI 참조 문서

`docs/ai-reference/` 경로에 AI가 참고할 수 있는 Claude SDK, 튜토리얼, 연구자료 등이 정리되어 있습니다.

| 디렉토리 | 설명 |
|----------|------|
| 01_SDK | Claude SDK 관련 문서 |
| 02_Product | Claude 제품 관련 문서 |
| 03_Tutorial | 튜토리얼 및 학습 자료 |
| 04_Research | 연구 자료 |
| 05_Integration | 통합 가이드 |
| 06_Extension | 확장 기능 문서 |
| 07_Agent | 에이전트 관련 문서 |
| 08_Workflow | 워크플로우 문서 |
| 09_Vertical | 수직 통합 사례 |
| 10_Safety | 안전성 관련 문서 |

## 상태줄 — devlog 프로젝트 표시

Claude Code 상태줄에 현재 세션의 devlog 프로젝트를 표시하는 스크립트입니다.

```
vh1981_skills | ⎇ main | 📓 my-project | Opus 5
```

`statusLine` 은 `settings.json` 레벨 설정이라 플러그인이 실어 나르지 못합니다. 플러그인을 설치해도
상태줄은 따라가지 않으므로, 사용하는 머신마다 아래를 한 번씩 실행해야 합니다.

```bash
./scripts/install-statusline.sh
```

설치 스크립트가 `~/.claude/statusline.sh` 로 복사하고, `~/.claude/settings.json` 의 `statusLine` 을
나머지 키를 보존한 채 갱신한 뒤, 상태줄이 실제로 한 줄을 출력하는지 확인합니다. 기존 파일은 백업합니다.
설치 후 세션 재시작이 필요합니다.

표시 규칙, 이식성 관련 사항, 문제 해결은 `scripts/README.md` 에 있습니다.

## 설치

### 방법 1: Marketplace에서 설치

Claude Code 세션 안에서 다음 명령어를 실행합니다:

```
/plugin marketplace add git@github.com:vincenthanna/vh1981_skills.git
/plugin install prompts-pack
/plugin install vh1981
```

### 방법 2: 로컬 디렉토리에서 로드 (개발/테스트용)

```bash
git clone git@github.com:vincenthanna/vh1981_skills.git
claude --plugin-dir /path/to/vh1981_skills/plugins/vh1981
claude --plugin-dir /path/to/vh1981_skills/plugins/prompts-pack
```

## 사용법

플러그인 설치 후 스킬을 호출합니다:

```
/worklog create my-project
/worklog list
/worklog select my-project
/worklog update

/prjdocs create cloud-mode
/prjdocs select cloud-mode
/prjdocs update "source_id 가드 분석"
```

### 유용한 명령어

| 명령 | 설명 |
|------|------|
| `/plugin` | 플러그인 매니저 열기 (설치 확인) |
| `/reload-plugins` | 플러그인 변경 후 다시 로드 |

## 디렉토리 구조

```
.claude-plugin/
  marketplace.json          # Marketplace 정의
plugins/
  vh1981/
    .claude-plugin/plugin.json   # name: vh1981 (plugin namespace)
    skills/
      devlog/SKILL.md       # /devlog 스킬 (통합)
      worklog/SKILL.md      # /worklog 스킬
      prjdocs/SKILL.md      # /prjdocs 스킬
  prompts-pack/
    .claude-plugin/plugin.json
    agents/                 # debugger, code-reviewer, ...
    commands/               # /bug-fix, /pr-audit, ...
prompts/
  agents -> ../plugins/prompts-pack/agents     # symlink
  commands -> ../plugins/prompts-pack/commands # symlink
  ai-reference/             # AI 참조 문서 (SDK, 튜토리얼 등)
  baseline.md               # 기본 작업 규칙
  commit_rules.md
  translate_to_kr.md
  code_visualization.md
scripts/
  statusline.sh             # devlog 상태줄 (플러그인 아님, 머신마다 설치)
  install-statusline.sh     # 위 스크립트 설치 + settings.json 등록
  README.md                 # 설치·표시 규칙·문제 해결
```

## 라이선스

MIT
