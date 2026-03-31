---
name: release
source: plusinsight/.claude/skills/release/
type: claude-code-skill
---

# release

릴리스 브랜치에서 최종 릴리스를 발행하는 Claude Code 스킬.
PR 머지, git 태그, GitHub 릴리스 노트, 다음 릴리스 브랜치 설정까지 자동화한다.

## Overview

Minor(`release/X.Y`) 및 Patch(`release/X.Y.Z`) 릴리스를 지원한다.
릴리스 노트는 PM/Stakeholder용 한국어 섹션과 개발자용 기술 섹션으로 구분된다.
100개 초과 커밋의 대형 PR은 자동으로 분할 처리한다.

## Trigger

"create a release", "ship this version", "release v3.5.0", "finalize the release" 등.
RC 태깅에는 `/releasebranch` 사용. 배포, 롤백에는 사용하지 않음.

## 사전 요건

- Repository admin 권한 필수
- `release/X.Y` 또는 `release/X.Y.Z` 브랜치에서만 실행 가능

## 워크플로우

### 단계 0: 권한 & 브랜치 검증

```bash
# Admin 권한 확인
gh api repos/{owner}/{repo}/collaborators/$USER/permission --jq '.permission'

# 브랜치 패턴 확인: release/X.Y (minor) 또는 release/X.Y.Z (patch)
```

### 단계 1: 분석 & 시각화

- 릴리스 타입 판별 및 ASCII 다이어그램으로 워크플로우 시각화
- 100+ 커밋 시 분할 경고

### 단계 2-3: PR 머지

**대형 PR (>100 커밋):**
- 100개씩 임시 브랜치/PR 분할 → 순차 rebase merge → 원본 PR 닫기

**일반 PR (≤100 커밋):**
```bash
gh pr merge {pr_number} --rebase --delete-branch
```

### 단계 3.5: 필수 린팅

```bash
uv run pre-commit run --all-files
```

### 단계 4: 릴리스 생성

1. `pyproject.toml` 버전 동기화
2. `uv lock` 실행
3. `/commit`으로 버전 변경 커밋
4. `vX.Y.Z` 태그 생성 및 푸시
5. 릴리스 노트 생성
6. `gh release create` 실행

### 단계 5A: Minor 릴리스 후처리

```
release/3.4 완료 → v3.4.0 태그 → release/3.5 브랜치 생성 (v3.5.0-rc0)
```

### 단계 5B: Patch 릴리스 후처리

```
release/3.4.1 완료 → v3.4.1 태그 → release/3.5 를 새 main 위에 rebase
```

## 릴리스 노트 형식

```markdown
# vX.Y.Z

## 📋 For Product Managers & Stakeholders
### 🎯 Highlights
[비기술적 언어로 핵심 변경사항 요약]

### ✨ New Features
- [기능 설명 - 사용자 관점]

### 🐛 Bug Fixes
- [수정된 문제 - 이전 문제와 해결 내용]

### ⚠️ Cautions
- [주의사항 또는 "없음"]

## 🔧 For Developers
### ⚙️ Technical Changes
- [API 변경, 아키텍처 변경, breaking changes]

### 📦 Component Updates
- **d-platform**: vX.Y.Z - 변경 요약

### 📝 Migration Guide
- [업그레이드 시 필요 작업]

## 👥 Contributors
- @github_username
```

## 기여자 추출

```bash
# 릴리스 범위의 커밋에서만 추출 (gh pr list 사용 금지)
git shortlog -sn {previous_tag}..{new_tag}

# GitHub 유저네임 조회
gh api repos/{owner}/{repo}/commits/$commit --jq '.author.login'
```

## 규칙

- 모든 커밋은 `/commit` 스킬 사용 (raw git commit 금지)
- 사용자 확인 없이 자율 실행
- 릴리스 노트는 실제 코드 diff 기반 (커밋 메시지 아님)
- 릴리스 후 반드시 린팅 실행

## 의존성

- GitHub CLI (`gh`), admin 권한
- `/commit` 스킬
- `uv`, `pre-commit`
