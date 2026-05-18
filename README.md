# vh1981_skills

Claude Code용 개발 워크플로우 스킬 / 프롬프트 묶음입니다.

## 빠른 시작 — 다른 Claude Code 인스턴스에서 사용하기

이 레포의 prompts를 다른 Claude Code 인스턴스에서 쓰는 방법은 두 가지입니다.

**1) Plugin marketplace로 설치 (권장)**

Claude Code 세션 안에서:

```
/plugin marketplace add git@github.com:vincenthanna/vh1981_skills.git
/plugin install prompts-pack      # agents + commands 일괄 설치
/plugin install worklog           # devlog / worklog / prjdocs skill
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

`/analyze`, `/bug-fix`, `/improve-prompt`, `/pr-audit`, `/search-prompt`, `/verify`, `/write-report`

### worklog

`/plugin install worklog` 하나로 아래 3개 skill이 모두 설치됩니다.

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

## 설치

### 방법 1: Marketplace에서 설치

Claude Code 세션 안에서 다음 명령어를 실행합니다:

```
/plugin marketplace add git@github.com:vincenthanna/vh1981_skills.git
/plugin install prompts-pack
/plugin install worklog
```

### 방법 2: 로컬 디렉토리에서 로드 (개발/테스트용)

```bash
git clone git@github.com:vincenthanna/vh1981_skills.git
claude --plugin-dir /path/to/vh1981_skills/plugins/worklog
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
  worklog/
    .claude-plugin/plugin.json
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
```

## 라이선스

MIT
