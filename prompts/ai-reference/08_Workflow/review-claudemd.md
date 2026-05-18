---
name: review-claudemd
source: plusinsight/.claude/skills/review-claudemd/
type: claude-code-skill
---

# review-claudemd

Claude Code 대화 히스토리를 분석하여 CLAUDE.md 파일과 `.claude/rules/`를 자동 개선하는 스킬.

## Overview

최근 15-20개 대화 세션을 분석하여 위반된 규칙, 누락된 규칙, 중복 규칙, 불필요한 규칙을 식별한다.
Blind 테스트로 규칙의 실제 필요성을 검증하고, 자동으로 편집을 적용한다.

## Trigger

"review CLAUDE.md", "update Claude instructions", "improve Claude configuration",
"audit .claude/rules", "optimize context token usage", "clean up the rules",
"review recent sessions for improvements" 등.

## 5단계 워크플로우

### 단계 1: 대화 히스토리 추출

```bash
# 프로젝트 대화 디렉토리 탐색
PROJECT_PATH=$(pwd | sed 's|/|-|g' | sed 's|^-||')
CONVO_DIR=~/.claude/projects/-${PROJECT_PATH}

# 최근 15-20개 대화를 텍스트로 추출
for f in $(ls -t "$CONVO_DIR"/*.jsonl | head -20); do
  jq -r '...' "$f" > "$SCRATCH/${basename_f}.txt"
done
```

### 단계 2: 대화 분석 (병렬 Sonnet 서브에이전트)

대화 파일을 크기별로 배치:
- Large (>100KB): 1-2개/에이전트
- Medium (10-100KB): 3-5개/에이전트
- Small (<10KB): 5-10개/에이전트

각 서브에이전트가 분석하는 항목:
1. **VIOLATED RULES**: 존재하지만 위반된 규칙
2. **MISSING RULES (LOCAL)**: 프로젝트 특화 패턴 → local CLAUDE.md
3. **MISSING RULES (GLOBAL)**: 범용 패턴 → ~/.claude/CLAUDE.md
4. **OUTDATED RULES**: 더 이상 관련 없는 항목
5. **DUPLICATED RULES**: 통합 대상

### 단계 3: 중복 테스트 (블라인드 Haiku 서브에이전트)

CLAUDE.md 내용을 **보지 않은** 에이전트에게 구체적 시나리오를 제시하여
Claude가 기본적으로 따르는 행동인지 테스트.

**테스트 대상**: 행동 기본값 규칙만 (도구 선호, 코딩 스타일, 커밋 형식 등)
**스킵 대상**: 프로젝트 특화 값 (env vars, 포트, 파일 경로, 아키텍처 결정 등)

```
Scenario: Python 프로젝트에 requests를 설치해야 합니다.
Question: 어떤 명령어를 사용하시겠습니까?

Expected rule: "use uv, never pip"
```

결과 분류:

| 결과 | 의미 | 조치 |
|------|------|------|
| **REDUNDANT** | 에이전트가 기본적으로 따름 | 제거 후보 |
| **NECESSARY** | 에이전트가 다르게 행동 | 유지 |
| **REVIEW** | 대략 맞지만 세부 누락 | 재작성 고려 |

### 단계 4: 결과 통합

Phase 2 + Phase 3 결과를 통합 리포트로:
1. Violated rules (강화 필요)
2. Suggested additions - LOCAL
3. Suggested additions - GLOBAL
4. Outdated rules (제거)
5. Redundant rules (컨텍스트 토큰 절약)
6. Duplicated rules (통합)

### 단계 5: 변경 적용

리포트 제시 후 자동 적용:
- Redundant → 제거
- Violated → 문구 강화, 예시 추가
- New patterns → 적절한 파일에 추가
- Outdated → 제거/업데이트
- Duplicated → 한 위치로 통합

## 출력

변경된 모든 파일과 변경 내용 요약 출력.
스크래치 디렉토리 정리:

```bash
rm -rf "$SCRATCH"
```

## 의존성

- Claude Code 대화 히스토리 (`~/.claude/projects/`)
- `jq` (JSON 처리)
- Sonnet/Haiku 서브에이전트
