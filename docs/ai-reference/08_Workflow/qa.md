---
name: qa
source: plusinsight/.claude/skills/qa/
type: claude-code-skill
---

# qa

RC(Release Candidate) 태그의 빌드-설치-배포를 검증하는 루프형 Claude Code 스킬.

## Overview

가장 최근 RC 태그가 빌드되고, 설치되고, 정상 운영되는지 end-to-end로 검증한다.
어떤 단계에서든 실패하면 진단 → 수정 → 새 RC 태그 → 처음부터 재시작하는 루프를 반복한다.

## Trigger

"verify an RC build", "run QA on a release candidate", "check if RC CI passed",
"validate deployment health", "did the build pass", "check the RC" 등.
릴리스 생성, 브랜치 컷, 프로덕션 배포에는 사용하지 않음.

## 검증 루프

### 단계 1: RC 태그 탐색

`deployment-engineer` 서브에이전트 사용:

```bash
git tag --sort=-creatordate | grep -E 'rc[0-9]+' | head -5
```

- 최신 RC 태그 저장 (e.g., `v3.3.2-PII-1610-rc0`)
- `.github/workflows/`의 워크플로우 분석

### 단계 2: GitHub Actions 검증

- `gh run list --branch <tag>`로 워크플로우 실행 확인
- 모든 워크플로우가 `conclusion: success` 완료 확인
- installer/NAS 업로드 워크플로우 완료 확인

### 단계 3: 빌드 설치

```bash
VERSION="<discovered-version>"
SETUP_NOCHECK=1 bash /qa/pi-installer/pi-installer-${VERSION}.run \
  --keep --target /qa/pi-installer/pi-installer-${VERSION}

cd /qa/pi-installer/pi-installer-${VERSION}/installer
bash setup.sh --upgrade
```

### 단계 4: 배포 상태 검증

```bash
# Credentials from installer .env
source ~/plusinsight/installer/.env

# ClickHouse: vision table data flow
clickhouse-client ... -q "SELECT count() FROM vision WHERE timestamp > now() - INTERVAL 5 MINUTE"

# ClickHouse: raw table data flow
clickhouse-client ... -q "SELECT count() FROM raw WHERE timestamp > now() - INTERVAL 5 MINUTE"

# Container health
docker compose ps --format 'table {{.Name}}\t{{.Status}}'

# Service logs
for svc in mediaserver dplatform dashboard-postprocessor; do
  docker compose logs --tail 50 "$svc"
done
```

### 실패 루프

모든 단계에서 실패 시:
1. `gh run view <run-id> --log-failed`로 실패 로그 확인
2. `debugger` 서브에이전트로 진단 및 수정
3. `/commit`으로 수정 커밋
4. `/releasebranch`로 새 RC 태그 생성
5. Phase 1부터 재시작

## 성공 기준

5가지 모두 충족 시 RC 검증 완료:

1. RC 태그의 모든 GitHub Actions 워크플로우 성공
2. Installer 업그레이드 에러 없이 완료
3. `vision` 및 `raw` 테이블에 최근 5분 데이터 존재 (count > 0)
4. 모든 critical 컨테이너 `Up` 상태 (superset 제외)
5. 서비스 로그에 critical 에러(FATAL, unhandled exception) 없음

## 에이전트 참조

| Phase | 에이전트 | 용도 |
|-------|----------|------|
| Discovery | `deployment-engineer` | 태그 목록, 워크플로우 분석 |
| GitHub Actions | `deployment-engineer` | CI/CD 상태 확인 |
| Failure Analysis | `debugger` | 근본 원인 분석, 코드 수정 |
| Installation | (Bash 직접 실행) | 인스톨러 추출 및 업그레이드 |
| Health Check | (Bash 직접 실행) | ClickHouse 쿼리, 컨테이너 상태, 로그 |

## 규칙

- 최대 3회 반복 후 사용자에게 에스컬레이션
- 단계 간 확인 요청 없이 자율 실행
- 항상 `/commit`으로 코드 수정, `/releasebranch`로 RC 태그 생성

## 의존성

- GitHub CLI (`gh`)
- Docker, ClickHouse
- `/commit`, `/releasebranch` 스킬
