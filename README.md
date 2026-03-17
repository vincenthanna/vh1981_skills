# vh1981_skills

Claude Code용 개발 워크플로우 스킬 플러그인입니다.

## Skills

### worklog

세션 작업 기록을 `docs/history/<subject>/` 경로에 마크다운 파일로 관리합니다.

**명령어:**

| 명령 | 설명 |
|------|------|
| `/worklog create <subject>` | 새 작업 로그 생성 |
| `/worklog list` | 기존 작업 로그 목록 조회 |
| `/worklog select <subject>` | 작업 로그 선택 (활성화) |
| `/worklog update` | 활성 작업 로그에 진행 내용 추가 |

## 설치

### 방법 1: Git 저장소에서 설치

Claude Code 세션 안에서 다음 명령어를 실행합니다:

```
/plugin marketplace add git@github.com:vincenthanna/vh1981_skills.git
/plugin install vh1981_skills
```

### 방법 2: 로컬 디렉토리에서 로드 (개발/테스트용)

```bash
claude --plugin-dir /path/to/vh1981_skills
```

## 사용법

플러그인 설치 후, 네임스페이스를 포함하여 스킬을 호출합니다:

```
/vh1981_skills:worklog create my-project
/vh1981_skills:worklog list
/vh1981_skills:worklog select my-project
/vh1981_skills:worklog update
```

### 유용한 명령어

| 명령 | 설명 |
|------|------|
| `/plugin` | 플러그인 매니저 열기 (설치 확인) |
| `/reload-plugins` | 플러그인 변경 후 다시 로드 |

## 라이선스

MIT
