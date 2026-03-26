# vh1981_skills

Claude Code용 개발 워크플로우 스킬 플러그인입니다.

## Skills

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
plugins/worklog/
  .claude-plugin/
    plugin.json             # 플러그인 정의 (v1.2.0)
  skills/
    devlog/SKILL.md         # /devlog 스킬 (통합)
    worklog/SKILL.md        # /worklog 스킬
    prjdocs/SKILL.md        # /prjdocs 스킬
```

## 라이선스

MIT
