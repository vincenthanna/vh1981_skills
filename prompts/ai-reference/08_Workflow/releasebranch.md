---
name: releasebranch
source: plusinsight/.claude/skills/releasebranch/
type: claude-code-skill
---

# releasebranch

릴리스 및 기능 브랜치에 RC(Release Candidate) 태그를 생성하는 Claude Code 스킬.

## Overview

릴리스 브랜치(`release/X.Y`)에서는 `vX.Y.Z-rcN` 형식,
기능 브랜치에서는 `vX.Y.Z-JIRA-XXXX-rcN` 형식의 RC 태그를 자동 생성한다.
기존 RC 태그를 확인하여 번호를 자동 증가시킨다.

## Trigger

"tag an RC", "create a release candidate", "cut an RC", "cut a new RC" 등.
최종 릴리스에는 `/release` 스킬 사용. 태그 조회/삭제에는 사용하지 않음.

## 태그 형식

| 브랜치 유형 | 태그 형식 | 예시 |
|-------------|-----------|------|
| Release (`release/3.0`) | `vX.Y.Z-rcN` | `v3.0.0-rc1` |
| Feature (`PII-1234-new-feature`) | `vX.Y.Z-JIRA-XXXX-rcN` | `v3.0.0-PII-1234-rc1` |

## 워크플로우

### 단계 1: 브랜치 검증

- main 브랜치에서는 실행 불가
- Release 브랜치: 직접 사용
- Feature 브랜치: PR base → upstream → merge-base 순으로 타겟 릴리스 브랜치 탐지

### 단계 2: 버전 추출

```bash
# release/X.Y → vX.Y.0
# release/X.Y.Z → vX.Y.Z
```

### 단계 3: JIRA 태그 (기능 브랜치만)

브랜치 이름 → 커밋 메시지 순으로 JIRA 태그(`PII-1234`) 추출.
없으면 에러.

### 단계 4: RC 번호 결정

```bash
git fetch --tags -q
git tag -l "${tag_pattern}*" | sort -V | tail -1
# 가장 높은 rcN에서 +1
```

### 단계 5: 태그 생성 & 푸시

```bash
git tag -a "$new_tag" -m "$tag_message"
git push origin "$new_tag"
```

## 예시

```bash
# Release branch, first RC
# branch: release/3.0 → v3.0.0-rc1

# Release branch, subsequent RC
# branch: release/2.5, existing: v2.5.0-rc1, v2.5.0-rc2 → v2.5.0-rc3

# Feature branch with JIRA in name
# branch: PII-1234-new-feature, base: release/3.0 → v3.0.0-PII-1234-rc1

# Feature branch with JIRA in commits
# branch: feature/awesome-update, base: release/3.0.1
# commit: [PII-5678] Add new feature → v3.0.1-PII-5678-rc1
```

## 에러 처리

- main 브랜치에서 실행 시 에러
- Feature 브랜치가 릴리스 브랜치를 타겟하지 않을 시 에러
- 릴리스 브랜치 이름에서 버전 파싱 실패 시 에러
- Feature 브랜치에 JIRA 태그 없을 시 에러

## 의존성

- Git, GitHub CLI (`gh`)
- JIRA 태그 컨벤션 (`PII-XXXX`)
