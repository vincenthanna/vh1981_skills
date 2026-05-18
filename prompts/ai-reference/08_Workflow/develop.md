---
name: develop
source: plusinsight/.claude/skills/develop/
type: claude-code-skill
---

# develop

멀티 에이전트 합의(consensus) 기반 기능 개발을 오케스트레이션하는 Claude Code 스킬.

## Overview

TDD, 멀티 에이전트 합의, 자동화된 테스트를 결합한 완전한 기능 개발 워크플로우를 제공한다.
코드베이스 탐색부터 테스트 전략 수립, 구현, 검증까지 전 과정을 자동화한다.

## Trigger

사용자가 기능 구현, 버그 수정, 엔드포인트/컴포넌트/마이그레이션 추가, 리팩토링, Dockerfile 수정, 테스트 작성 등 **코드를 수정하는 모든 작업**을 요청할 때 트리거.
읽기 전용 작업(코드 설명, 파일 읽기, PR 리뷰)에는 사용하지 않음.

## Usage

```
/develop "Feature description or task to implement"
```

## 개발 원칙

### 1. 코딩 전 사고
가정을 명시적으로 밝히고, 불확실하면 질문. 여러 해석이 가능하면 제시.

### 2. 단순함 우선
요청된 것만 구현. 추측성 기능, 단일 사용 추상화, 불가능한 시나리오의 에러 핸들링 불필요.

### 3. 외과적 변경
변경할 부분만 수정. 인접 코드 "개선" 금지. 기존 스타일 유지.

### 4. 목표 지향 실행
작업을 검증 가능한 목표로 변환하고 검증될 때까지 반복.

## 워크플로우 단계

### 단계 1: 사전 요건 확인
- `ralph-loop` 스킬 가용성 확인
- `mgrep` (시맨틱 검색) 가용성 확인

### 단계 2: 코드베이스 탐색
- mgrep 가용 시: `deep-explore` 에이전트로 시맨틱 검색
- 미가용 시: `Explore` 에이전트 (thoroughness="very thorough") 폴백

### 단계 3: 테스트 전략 결정
- 테스트 유형 결정: 단위 / 통합 / Docker 기반
- `~/plusinsight` 존재 시: `/testbranch`를 유일한 E2E 테스트로 사용

### 단계 4: Ralph Loop 프롬프트 구성

4개 필수 헌법(Constitution):
1. **TDD**: 기능 코드에 반드시 테스트 동반
2. **Testbranch-First**: ~/plusinsight 존재 시 /testbranch가 유일한 E2E 게이트
3. **Commit Protocol**: 항상 /commit 스킬 사용
4. **Multi-Agent Consensus**: 모든 코드 변경에 5개 동일 에이전트 병렬 실행 → 합의 도출

### 단계 5: 사용자 확인
- Interactive 모드: 개발 계획 제시 및 확인 요청
- Headless 모드 (`claude -p`): 자동 스킵

### 단계 6: 개발 실행
`/ralph-loop:ralph-loop` 호출로 개발 실행

## 에이전트 참조

| 작업 | 에이전트 | 용도 |
|------|----------|------|
| 코드 탐색 (mgrep) | `deep-explore` | 시맨틱 검색 |
| 코드 탐색 (폴백) | `Explore` | 패턴 매칭 |
| Python 개발 | `python-pro` | Python, async 패턴 |
| FastAPI 개발 | `fastapi-pro` | API 엔드포인트, Pydantic |
| 프론트엔드 | `frontend-developer` | React, Next.js |
| DB | `database-architect` | 스키마 설계, 마이그레이션 |
| 테스트 | `test-automator` | 테스트 패턴, 픽스처 |
| 디버깅 | `debugger` | 에러 수정, 근본 원인 |

## 멀티 에이전트 합의 패턴

```
1. 적합한 에이전트 결정 (e.g., python-pro)
2. 동일 프롬프트로 5개 에이전트 병렬 실행
3. 5개 구현 수집
4. 리뷰 스킬로 각 구현 검토:
   - Python: /everything-claude-code:python-review
   - Non-Python: /everything-claude-code:code-review
5. 합의 솔루션만 구현
```

## 의존성

- `ralph-loop` 스킬 (필수)
- `mgrep` (선택, 시맨틱 검색용)
- `/commit`, `/testbranch` 스킬
- `/everything-claude-code` 리뷰 스킬
