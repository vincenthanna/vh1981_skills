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

Claude Code 설정에서 플러그인으로 추가:

```
claude plugin add git@github.com:vincenthanna/vh1981_skills.git
```

## 라이선스

MIT
