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
- AI 참고 문서 (`prompts/ai-reference/`, `prompts/baseline.md`, `prompts/commit_rules.md`, `prompts/translate_to_kr.md`, `prompts/code_visualization.md`, `prompts/autorun.md`)는 plugin에 포함되지 않으므로 이 방식으로 참조합니다.

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

`/plugin install vh1981` 하나로 아래 skill이 모두 설치되고, [기본 가이드라인](#기본-가이드라인--모든-세션에-적용되는-규칙)이 모든 세션에 적용됩니다.

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
| `/devlog reorg rename <old> <new>` | 프로젝트 이름 변경 + 모든 cross-reference 치환 (`/devlog rename` 으로도 호출) |
| `/devlog reorg archive <path>` | 낡은 문서를 `_archived/` 로 격리하고 사유를 기록 (삭제는 하지 않음) |
| `/devlog reorg cleanup` | 구조적 위생 문제 점검 — 중복 `NN_`, 깨진 링크, 빈 파일. 제안만 하고 자동 실행하지 않음 |
| `/devlog reorg consolidate` | 쌓인 조사 문서의 내용 정리 + 압축 제안 — 중복 서술/중복 open item, 이미 해결된 open item, 뒤집힌 결론, 채택하지 않은 방법론의 상세를 `rejected/` 로 추출, 파일 분할/폴더링 임계. 제안만 하며 `history/` 는 읽지도 쓰지도 않음 (`/devlog consolidate` 으로도 호출) |
| `/devlog reorg readme` | README의 `<!-- AUTO-GENERATED -->` 영역 재생성 |
| `/devlog run <condition>` | 측정 run manifest 를 `runs/<condition>/` 에 등록 (실험 자체를 실행하지는 않음) |
| `/devlog compare <조건들>` | `comparisons/` 에 비교 리포트 생성·확장 |
| `/devlog log [--since <date>] [--until <date>]` | 기간 안에 날짜가 붙은 항목(Done, history, Finding)을 뽑아 그 기간에 한 일을 정리 |
| `/devlog upload [<project>] [--to <path>]` | knowledge base(KB)에 업로드. `vh1981:kb` 로 위임하며, KB가 설정돼 있으면 `/devlog update` 끝에 자동으로 올라감 |

**디렉토리 구조:**

```
docs/devlog/<project>/
  01_<topic>.md          ← 조사/분석 문서
  history/
    01_<topic>.md        ← 작업 기록
  rejected/
    01_<topic>.md        ← 채택하지 않은 방법론의 상세 (필요할 때만 읽음)
  _archived/             ← reorg archive 로 격리된 문서 + _log.md
```

조사 문서는 메인스트림 경로만 담고, 폐기·보류된 방법론의 상세는 `rejected/` 로
빠집니다. 조사 문서에는 한 줄 판정과 그 이유, 그리고 상세 문서 링크만 남습니다 —
이유까지 빼면 다음 사람이 같은 시도를 반복하므로 이유는 반드시 본문에 남깁니다.

### worklog (deprecated)

새 작업은 devlog 를 씁니다. `docs/history/` 를 이미 쓰는 repo 에서 `/worklog` 를 명시적으로 부를 때만 동작합니다.

세션 작업 기록을 `docs/history/<subject>/` 경로에 마크다운 파일로 관리합니다.

**명령어:**

| 명령 | 설명 |
|------|------|
| `/worklog create <subject>` | 새 작업 로그 생성 |
| `/worklog list` | 기존 작업 로그 목록 조회 |
| `/worklog select <subject>` | 작업 로그 선택 (활성화) |
| `/worklog update` | 활성 작업 로그에 진행 내용 추가 |

### prjdocs (deprecated)

새 작업은 devlog 를 씁니다. `docs/projects/` 를 이미 쓰는 repo 에서 `/prjdocs` 를 명시적으로 부를 때만 동작합니다.

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

### humanizer

바깥으로 보낼 글(Slack 메시지, PR 코멘트 답글과 본문, 이메일, 공지, 진행 보고)에서 AI 문체를 걷어내고
분량을 줄입니다. 33개 패턴 카탈로그와 비개발자용 진행 보고 모드를 담고 있으며, 질문 없이 최종본을 냅니다.
repo에 남는 markdown 문서는 대상이 아니며 `doc-style.md` 를 따릅니다.

| 입력 | 동작 |
|------|------|
| `/humanizer` + 붙여넣은 글 | 최종본과 가장 큰 변경 한 줄을 출력 |
| `/humanizer <파일>` | 파일의 산문만 고쳐 덮어쓰고 1~2줄로 보고 |
| 다른 작업의 Slack·PR 초안 | 초안을 내놓기 직전에 마지막 단계로 적용 |

패턴 카탈로그는 Wikipedia의 "Signs of AI writing"을 기반으로 한 MIT 라이선스 humanizer 3.1.0을 한국어로 옮긴 것입니다.

### kb

여러 repo와 머신의 devlog를 하나의 knowledge base(KB) 디렉토리에 모으고, 어느 세션에서나 업로드·검색·현황 조회를 합니다.
KB는 로컬 경로나 `ssh://user@host/abs/path` 이며, 원격에는 `python3` 3.8 이상만 있으면 됩니다(스크립트는 첫 호출 때 `<kb>/.kb/bin/` 에 복사됩니다).
주 독자는 AI이고, 사람은 `/kb` 명령으로 접근합니다.
KB 위치는 코드에 넣지 않습니다. 머신마다 `/kb init <위치>` 로 한 번 정하고(`~/.config/vh1981/kb`), 환경변수 `VH1981_KB` 나
명령의 `--kb <위치>` 로 바꿀 수 있습니다. 여러 머신이 함께 쓰는 기본값은 `VH1981_KB_DEFAULT` 에 둡니다.

| 명령 | 설명 |
|------|------|
| `/kb init <위치>` | KB를 만들고 이 머신의 기본 KB로 저장 (`~/.config/vh1981/kb`) |
| `/kb upload [<project>] [--all]` | devlog 프로젝트 업로드. repo별 `repos/<repo>/<project>`, origin 이 없으면 `--topic` 으로 `topics/<topic>/<project>` |
| `/kb search <질문>` | `INDEX.md` 로 후보를 고르고 본문을 grep 해 출처 경로와 함께 답함 |
| `/kb status` | `NOW.md`: 진행 중, 열린 Critical/High, 갈라진 사본, 멈춘 것 |
| `/kb register` | repo가 하는 일, 분야, checkout별 branch·하는 일·ssh 접속 방법 등록 |
| `/kb fetch <repo> [<project>]` | 등록된 checkout에 직접 접속해 최신 devlog 읽기 |
| `/kb log --since <날짜> --until <날짜>` | 모든 repo·머신에 걸쳐 기간 안에 한 일을 날짜순으로 뽑기 |
| `/kb check`, `/kb survey <dir>` | KB 점검, 작업 디렉토리들의 갈라진 사본 비교 |

같은 프로젝트가 여러 worktree나 clone에 갈라진 사본으로 있을 수 있어, 프로젝트마다 소유 checkout 하나만 KB에 쓰고
다른 사본은 차이를 보고만 합니다(`--take-over` 로 소유자 변경). repo는 정규화한 origin URL과 `git --git-common-dir` 로
식별하므로 https/`git@` 표기 차이와 worktree 가 한 repo로 묶입니다. 512KB 이하 텍스트와 이미지가 내장되지 않은 HTML만 올리고,
이미지·`npy`·압축 파일은 올리지 않습니다. 프로젝트 카드는 devlog `README.md` 의 `kb:` frontmatter 입니다.
devlog에 새로 넣는 Done, history 항목은 `- YYYY-MM-DD: ...`, 새 Finding 헤딩은 `(YYYY-MM-DD)` 로 끝나도록 날짜를 붙입니다. `log` 가 이 날짜로 기간을 거릅니다.
설계 근거는 `docs/projects/knowledge-base/01_spec-and-plan.md` 에 있습니다.

### kb-report

KB가 있는 머신의 cron이 KB 디렉토리에서 headless claude로 이 스킬을 실행해, 등록된 모든 repo·디렉토리에서 어제 한 일을 모아 단일 HTML **daily log** 를 만듭니다.
일요일 22:00에는 그 주의 **weekly log** 를 만듭니다. 두 로그는 KB를 루트로 하는 웹 서버(`http://<KB 머신>:8800/`)에 최신순으로 올라갑니다.

| 명령 | 설명 |
|------|------|
| `/kb-report daily [YYYY-MM-DD]` | 그날(기본: 어제)의 daily log 생성 |
| `/kb-report weekly [YYYY-MM-DD]` | 그날로 끝나는 7일의 weekly log 생성 |
| `/kb-report install` | KB 머신에 cron(06:30 daily, 일 22:00 weekly, 재부팅 시 서버)과 실행 파일 설치 |
| `/kb-report status` | 최근 실행 로그와 최신 로그 페이지 |

수집은 `kb.py collect` 가 합니다. KB 머신에서 ssh로 들어갈 수 있는 checkout은 그 자리에서(live), 들어갈 수 없는 checkout(노트북 등)은
세션 시작 때 자동 checkin이 올린 KB 사본으로 읽습니다. cron의 claude는 `kb.py`, 서버 스크립트, Read/Write/Edit/Glob/Grep만 쓸 수 있습니다.

### techreport

조사·측정 결과를 그 분야를 모르는 사람도 혼자 읽을 수 있는 단일 HTML 기술 보고서로 만들고, 주제별 색인 웹서버에 올립니다.
보고서에는 0장 비유와 그 비유의 한계, 용어집과 마우스 팝업, 인라인 SVG 그림과 설명용 애니메이션, arXiv 로 제목을 확인한 논문 인용,
재현 실패까지 남기는 검증 기록이 들어갑니다. 외부 이미지와 CDN 은 쓰지 않습니다.

| 항목 | 내용 |
|------|------|
| 저장 위치 | 활성 devlog 프로젝트의 `docs/devlog/<project>/NN_<slug>.html` |
| 서버 | 보고서를 만들면 `scripts/serve_devlog.sh docs/devlog` 로 자동 기동 (기본 `0.0.0.0:8800`, 이미 떠 있으면 그대로) |
| 이 머신에서만 보기 | `REPORT_HOST=127.0.0.1` 을 붙여 기동 |
| 중지 | `kill "$(cat /tmp/serve_devlog.8800.pid)"` |

서버는 시작할 때 만든 `.html` 허용 목록으로만 응답하므로, 요청 경로가 파일 시스템에 닿지 않습니다.
이미지가 내장된 보고서는 기본으로 잠기고 `--include-personal` 로만 열립니다. 템플릿은 `templates/report.html`,
넘기기 전 검사 목록은 `reference/checklist.md` 에 있습니다.

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

## 기본 가이드라인 — 모든 세션에 적용되는 규칙

`vh1981` 플러그인을 설치하면 세션이 시작될 때마다 기본 작업 규칙, 문서 작성 규칙, 모델 학습 규칙이 컨텍스트에 들어갑니다.
사용자나 프로젝트의 `CLAUDE.md`, 또는 사용자의 직접 지시와 충돌하면 그쪽이 우선합니다.
규칙의 정본은 이 repo 의 `plugins/vh1981/guidelines/` 이며, 고친 뒤에는 플러그인 버전을 올려야 설치된
머신이 새 규칙을 받습니다.

플러그인 루트의 `CLAUDE.md` 는 로드되지 않고, 플러그인 `settings.json` 은 `agent` 와
`subagentStatusLine` 키만 받습니다. 그래서 SessionStart hook 이 규칙을 stdout 으로 출력해 컨텍스트에
넣습니다. matcher 를 두지 않았으므로 startup, resume, `/clear`, compact 때마다 다시 주입됩니다.

| 파일 | 역할 |
|---|---|
| `plugins/vh1981/guidelines/core.md` | 매 세션 주입되는 규칙 본문. 맨 위의 우선순위와 "정책 지도"가 주제마다 정본 문서 하나를 정하고, 다른 문서는 정본을 가리키기만 합니다 |
| `plugins/vh1981/guidelines/doc-style.md` | 문서를 작성할 때만 읽는 상세 규칙 |
| `plugins/vh1981/guidelines/ml-training.md` | 모델 학습을 다룰 때만 읽는 체크포인트·재개 규칙 |
| `plugins/vh1981/guidelines/japanese-notation.md` | 일본어를 적을 때 읽는 한글 발음 표기 규칙 |
| `plugins/vh1981/guidelines/output-principles.md` | 보고서·문서·설명의 기본 원칙: 쉬운 기술 문체(ASD-STE100의 약 80%)와 이미지·그래프·차트·애니메이션 기본 사용 |
| `plugins/vh1981/guidelines/references/karpathy-understanding-llm-outputs.md` | 위 원칙의 근거: Karpathy 글(2026-10-02) 번역과 관련 실험·자료 |
| `plugins/vh1981/guidelines/shell-pitfalls.md` | worktree, ssh·docker, gh, subagent를 다룰 때 읽는 조용한 실패 함정 모음 |
| `plugins/vh1981/guidelines/mcp-connectors.md` | claude.ai 커넥터(Notion 등) 연결이 404로 실패할 때 읽는 우회 절차 |
| `plugins/vh1981/scripts/inject-guidelines.sh` | `core.md` 를 출력하는 SessionStart hook |
| `plugins/vh1981/scripts/kb-checkin.sh` | 세션 시작 때 백그라운드로 KB에 checkin 하는 SessionStart hook (`VH1981_KB_CHECKIN=0` 으로 끔) |

`core.md` 는 매 세션 컨텍스트를 차지하므로 짧게 유지합니다. hook 출력이 크면 파일로 빠지고 미리보기만
컨텍스트에 들어갑니다. 긴 내용은 `doc-style.md` 처럼 별도 파일로 두고 `core.md` 에서
`{{GUIDELINES_DIR}}/<파일>` 로 가리키면, hook 이 이 자리표시자를 설치 경로로 바꿉니다.
`./scripts/tests/run.sh` 는 주입 텍스트가 10000 bytes 미만인지 검사합니다.

주입을 끄려면 환경변수를 설정합니다.

```bash
export VH1981_GUIDELINES=0
```

주입된 규칙이 subagent 에도 전달되는지는 확인하지 않았습니다(미검증).

## 상태줄 — devlog 프로젝트 표시

Claude Code 상태줄에 현재 세션의 devlog 프로젝트를 표시하는 스크립트입니다.

```
vh1981_skills | ⎇ main | 📓 my-project | Opus 5
```

`statusLine` 은 `settings.json` 레벨 설정이라 플러그인 매니페스트가 실어 나르지 못하고, orca 같은
다른 설치 스크립트가 덮어쓰기도 합니다. 두 경우 모두 에러 없이 상태줄만 조용히 사라집니다.

`vh1981` 플러그인이 설치되어 있으면 **따로 할 일이 없습니다.** SessionStart hook 이 매 세션마다
스크립트와 `settings.json` 을 확인해 어긋난 것만 고치고, 고칠 것이 없으면 아무것도 출력하지 않습니다.
자동 복구를 끄려면 `VH1981_STATUSLINE_AUTOREPAIR=0` 을 설정합니다.

플러그인 없이 스크립트만 쓰거나 즉시 적용하고 싶으면 수동 설치도 됩니다.

```bash
./scripts/install-statusline.sh
```

표시 규칙, 자동 복구 동작, 이식성 관련 사항, 문제 해결은 `scripts/README.md` 에 있습니다.

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
    hooks/hooks.json        # SessionStart 가이드라인 주입 + 상태줄 자동 복구
    guidelines/
      core.md               # 매 세션 주입되는 기본 규칙 (정본)
      doc-style.md          # 문서 작성 상세 규칙 (필요할 때 Read)
      ml-training.md        # 모델 학습 체크포인트·재개 규칙 (필요할 때 Read)
      japanese-notation.md  # 일본어 한글 발음 표기 규칙 (필요할 때 Read)
      shell-pitfalls.md     # 셸·도구 실전 함정 (필요할 때 Read)
      output-principles.md  # 보고서·문서 기본 원칙: 쉬운 문체 + 시각 자료 (필요할 때 Read)
      references/           # 원칙의 근거 자료 (Karpathy 글 번역 등)
      mcp-connectors.md     # MCP 커넥터 연결 실패 우회 (필요할 때 Read)
    scripts/
      inject-guidelines.sh  # core.md 주입 스크립트
      statusline.sh         # devlog 상태줄 (정본)
      check-statusline.sh   # 자동 복구 스크립트
    skills/
      devlog/SKILL.md       # /devlog 스킬 (통합)
      worklog/SKILL.md      # /worklog 스킬
      prjdocs/SKILL.md      # /prjdocs 스킬
      humanizer/            # /humanizer 스킬 (SKILL.md + references/patterns.md)
      techreport/           # /techreport 스킬 (템플릿, 검사 목록, 보고서 서버)
      kb/                   # /kb 스킬 (kb.py 클라이언트·store, KB.md 템플릿)
      kb-report/            # /kb-report 스킬 (daily·weekly log, cron 설치)
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
  statusline.sh -> ../plugins/vh1981/scripts/statusline.sh   # symlink
  install-statusline.sh     # 수동 설치 + settings.json 등록
  tests/run.sh              # 상태줄·설치·자동복구·가이드라인 주입 회귀 테스트
  README.md                 # 설치·표시 규칙·자동 복구·문제 해결
.github/workflows/
  statusline.yml            # ubuntu + macos 매트릭스, shellcheck, 매니페스트 검증
```

## 라이선스

MIT
