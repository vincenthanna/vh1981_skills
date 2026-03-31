# vh1981_skills

Claude Code용 개발 워크플로우 스킬 플러그인입니다.

## Plugins

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

### prompts

`/plugin install prompts`로 설치합니다. 프롬프트 저장, 관리, 큐레이션 스킬 모음입니다.

**명령어:**

| 명령 | 설명 |
|------|------|
| `/save-prompt` | 대화에서 프롬프트를 추출하여 서버에 저장 |
| `/curate-prompts` | 저장된 프롬프트에서 재사용 가능한 템플릿 추출 |
| `/update-docs` | 코드 변경사항 기반 문서 자동 업데이트 |

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
/plugin install worklog
```

### 방법 2: 로컬 디렉토리에서 로드 (개발/테스트용)

```bash
git clone git@github.com:vincenthanna/vh1981_skills.git
claude --plugin-dir /path/to/vh1981_skills/plugins/worklog
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
    .claude-plugin/
      plugin.json           # 플러그인 정의 (v1.2.0)
    skills/
      devlog/SKILL.md       # /devlog 스킬 (통합)
      worklog/SKILL.md      # /worklog 스킬
      prjdocs/SKILL.md      # /prjdocs 스킬
  prompts/
    .claude-plugin/
      plugin.json           # 플러그인 정의 (v1.0.0)
    skills/
      save-prompt/SKILL.md  # /save-prompt 스킬
      curate-prompts/SKILL.md # /curate-prompts 스킬
      update-docs/SKILL.md  # /update-docs 스킬
docs/
  ai-reference/             # AI 참조 문서 (SDK, 튜토리얼 등)
```

## 라이선스

MIT
