---
name: commit
source: plusinsight/.claude/skills/commit/
type: claude-code-skill
---

# commit

Conventional Commits 형식의 원자적(atomic) git 커밋을 자동 생성하는 Claude Code 스킬.

## Overview

코드 변경사항을 분석하여 목적별로 분리된 원자적 커밋을 생성한다.
Pre-commit 린팅, 선택적 스테이징, JIRA 태깅을 포함한 완전한 커밋 워크플로우를 자동화한다.

## Trigger

사용자가 "commit", "save changes", "check in code", "save my work" 등 커밋 관련 요청을 할 때 자동 트리거.
읽기 전용 git 명령(log, status, diff), push/pull, undo(revert, reset)에는 트리거하지 않음.

## 워크플로우

### 1. 사전 점검

- 변경사항 없으면 중단
- `main`/`master` 브랜치에서는 커밋 차단

### 2. Pre-commit 린팅

```bash
uv run pre-commit run --all-files
```

- 프론트엔드 파일 변경 시 manual stage 훅도 실행
- 자동 수정된 파일은 재스테이징, 수동 수정이 필요한 경우 직접 수정 후 재실행
- 린팅 통과 전까지 커밋 진행 불가

### 3. 원자적 커밋 계획

변경사항을 목적별로 분리:
- Feature 코드 ↔ 테스트
- Bug fix ↔ 리팩토링
- 문서 ↔ 구현
- 의존성 업데이트 ↔ 사용 코드
- CI/빌드 설정 ↔ 애플리케이션 코드

### 4. 커밋 타입

| 브랜치 | 타입 |
|--------|------|
| `release/*` | 항상 `hotfix` |
| 기타 | `feat` / `fix` / `refactor` / `docs` / `style` / `perf` / `test` / `build` / `ci` / `chore` |

### 5. 커밋 메시지 형식

```
[<JIRA-TAG>] <type>(<optional-scope>): <imperative-description>
```

Example:
```
[PII-2062] fix(postprocessor): resolve memory leak in cluster adapter
```

### 6. 푸시 & 확인

```bash
git push origin <branch>
git log --oneline -5
```

## 규칙

- "Generated with Claude Code", "Co-Authored-By: Claude", 이모지 금지
- `git add -A`, `git add .`, `git add --all` 사용 금지
- `-i` (interactive) 플래그 사용 금지
- Pre-commit 훅 실패 시 `--amend` 대신 새 커밋 생성
- HEREDOC으로 커밋 메시지 포맷팅

## 의존성

- `uv` (Python 패키지 매니저)
- `pre-commit` (린팅 프레임워크)
- Git, JIRA 태그 컨벤션
