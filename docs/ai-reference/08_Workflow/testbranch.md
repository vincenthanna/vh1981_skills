---
name: testbranch
source: plusinsight/.claude/skills/testbranch/
type: claude-code-skill
---

# testbranch

라이브 PLUSINSIGHT 설치본에 브랜치 코드를 마운트하고 자동 검증을 실행하는 Claude Code 스킬.

## Overview

현재 브랜치의 코드 변경사항을 설치된 컴포넌트와 비교하여,
변경된 소스를 Docker 컨테이너에 volume-mount하고 인프라/데이터 파이프라인/브라우저 UI를 검증한다.
E2E 테스트의 핵심 게이트로, `/develop` 스킬에서 Docker 기반 테스트를 대체한다.

## Trigger

"test changes on the live system", "mount branch code", "verify on the installation",
"run testbranch", "try this on the live system" 등.
단위 테스트, 프로덕션 배포, Docker 이미지 빌드에는 사용하지 않음.

## Flag Reference

| 플래그 | 동작 |
|--------|------|
| (없음) | Full flow: snapshot → diff → update → verification |
| `--diff` | 버전 비교 테이블만 표시 |
| `--restore` | 저장된 스냅샷으로 복원 |
| `--mount-only` | 변경사항 적용, 검증 스킵 |
| `--qa-only` | 검증만 실행, 마운트 변경 없음 |
| `--no-qa` | 마운트 후 검증 스킵 |
| `--browser-only` | 브라우저 테스트만 실행 |
| `--no-browser` | 브라우저 테스트 스킵 |
| `--data-only` | ClickHouse + Redis 검증만 |
| `--status` | 현재 dev-mount 상태 표시 |
| `--dry-run` | 계획만 표시, 실행 안 함 |
| `--install-path` | 설치 경로 오버라이드 (기본: ~/plusinsight) |

## 사전조건 확인

1. **Docker 실행 확인**: `docker info`
2. **설치 경로 유효성**: `DevTestManager.validate_install_path()`
3. **브랜치 감지**: `git rev-parse --abbrev-ref HEAD`
4. **Playwright MCP** (프론트엔드 변경 시만): 브라우저 자동화 가용성 확인
5. **ECR 인증**: AWS ECR 레지스트리 접근 확인 (실패 시 경고 후 계속)
6. **버전 비교 테이블**: 설치 버전 vs 브랜치 버전 표시

## 기본 흐름 (플래그 없음)

### 단계 1-3: 스냅샷 & Diff

```python
from plusinsight_installer.core.snapshot import SnapshotManager
from plusinsight_installer.core.dev_test import DevTestManager
from plusinsight_installer.core.version_diff import VersionDiffEngine

snap = SnapshotManager(install_path=install_path)
snap.create()  # 또는 기존 스냅샷 로드

manager = DevTestManager(repo_root=repo_root, install_path=install_path)
components = manager.detect_changed_components(base_ref=base_ref)

engine = VersionDiffEngine(repo_root=repo_root, components=components)
diffs = engine.compute_diffs(snapshot_hashes=snap.load())
```

### 단계 4: 변경사항 분류

```python
from plusinsight_installer.core.update_dispatch import UpdateDispatcher
dispatcher = UpdateDispatcher(manager=manager)
classified = dispatcher.classify_changes(diffs=diffs)
```

### 단계 5: 업데이트 실행

1. 데이터 기록 서비스 중지
2. 인프라 서비스 업그레이드 (ClickHouse, Redis 등)
3. docker-compose.yml 템플릿에서 재생성
4. Schema migrator 실행
5. C++ 플러그인 빌드 (CPP 카테고리 변경 시)
6. Override YAML 생성 및 적용
7. 프론트엔드 빌드 (CODE/DEPS 카테고리 변경 시)
8. 서비스 재시작
9. TRT 엔진 동기화 (MODELS 카테고리 변경 시)
10. 아티팩트 내보내기

### 단계 6: 검증

#### 인프라 점검
- 컨테이너 상태 (docker compose ps)
- ERROR 레벨 로그 분석
- API 헬스 엔드포인트 확인

#### 데이터 파이프라인 점검
- ClickHouse: vision, vision_head, 집계 테이블, 매핑 테이블
- Redis: camera/roi 키, vision pub/sub
- D-Platform: 감지 상태, 재시작 안정성

#### 브라우저/UI 점검 (Playwright MCP)
- Minimap dots (Konva.js canvas 렌더링)
- Console Errors
- Network Errors
- Usertool page 렌더링

#### 맞춤 수정 검증
커밋 메시지와 diff를 분석하여 fix intent별 맞춤 검증:

| 시그널 | 검증 |
|--------|------|
| gender, GENDER_MALE | vision 테이블 GENDER_MALE 존재 확인 |
| occupancy, dwell | occupancy_realtime 최근 행 확인 |
| reid, tracking | mapping 테이블 확인 |
| clickhouse, migration | schema_migrator 로그 확인 |
| crash, malloc | d-platform 재시작 횟수 + 감지 활성 확인 |

### 단계 7-8: 리포트 & 자가 치유

```python
from plusinsight_installer.core.self_heal import SelfHealRunner
healer = SelfHealRunner(repo_root, install_path, report)
heal_report = healer.run()
```

Self-heal 4가지 검사:
1. **Registry Sync**: COMPONENT_REGISTRY vs docker-compose 일치성
2. **Verification Coverage**: 검증 누락 테이블/라우트 감지
3. **Benign Pattern Learning**: 반복 로그 패턴 학습
4. **SKILL.md Drift Detection**: 문서 vs 실제 코드 불일치 감지

## 서브 컴포넌트 변경 카테고리

| 카테고리 | 의미 | 파일 예시 |
|----------|------|-----------|
| `CPP` | C++ 소스 | `*.cpp`, `*.h`, `*.cu`, `Makefile` |
| `MODELS` | 모델 설정 | `model_id.yaml` |
| `PYTHON` | Python 소스 | `*.py` |
| `DOCKER` | Dockerfile | `Dockerfile*` |
| `DEPS` | 의존성 | `pyproject.toml`, `package.json` |
| `CODE` | 프론트엔드 | `*.ts`, `*.tsx`, `*.css` |
| `CYTHON` | Cython | `*.pyx`, `*.pxd` |

## 파일 안전성

`~/plusinsight`에서 수정 가능한 파일:
- `docker-compose.yml` (템플릿에서 재생성, 원본은 스냅샷 보존)
- `docker-compose.override.yml` (표준 Docker Compose 메커니즘)
- `.dev-test-snapshot/` (백업)
- `.env` (인프라 버전 키만)

기타 변경은 모두 override YAML의 volume mount로 적용 → `--restore` 항상 안전.

## 의존성

- Docker, docker-compose
- `plusinsight_installer` Python 패키지
- Playwright MCP (프론트엔드 변경 시)
- AWS ECR (C++ 플러그인 폴백용)
- ClickHouse client, Redis CLI
