# Context Injection Patterns

> User / project / environment context를 composed prompt에 **안전하고 효과적으로** 주입하는 방법.
>
> 핵심 원칙: **right context, right place, redacted form.**
>
> **시리즈 위치**: composer Phase 3에서 호출. router가 활성화 결정 후 실제 주입 메커니즘 담당.

---

## 0. 왜 별도 component인가

Context 주입은 component selection(router)과 prompt composition(composer)에서 *직교*하는 관심사다:

- 같은 component 조합이라도 context가 다르면 다른 결과가 나온다.
- Context-only 변경(다른 프로젝트에서 같은 task)도 흔하다.
- **Context는 민감정보 redaction의 1차 방어선** — component는 보통 generic이지만 context는 user-specific이므로 leak risk가 여기서 발생한다.

세 가지를 분리해 관리하면 (a) component 재사용성↑, (b) redaction 누락 위험↓, (c) 메타 분석 용이.

---

## 1. Context source 분류

| Source | 예시 | Volatility | Redaction 필요? | 권장 pattern (§2) |
|---|---|---|---|---|
| **Project conventions** | CLAUDE.md, README, style guide | Low | No | Header inject |
| **Recent decisions** | 최근 PR, ADR, 결정서 | Medium | 부분 | Body / Reference |
| **Environment state** | 현재 commit, dependency, env vars | High | **Yes (env vars 등)** | Reference (path만) |
| **User preferences** | 톤, 언어, 형식 선호 | Low | No | Header inject |
| **Team / Org context** | 동료 이름, 역할, 의사결정 권한 | Medium | 부분 (개인정보) | Header / Body |
| **Memory (durable patterns)** | "X domain에서 Y 패턴" | Low | No | Body |
| **Run-specific state** | 이번 분석의 baseline, 이전 turn 결과 | High | Yes (있을 때) | Reference |

---

## 2. 주입 위치 — 4 patterns

### 2.1 Header inject (composed prompt 맨 위)

**적합**:
- Project conventions (수정 안 되는 규약)
- User preferences (응답 언어, 톤)
- Top-level identity (당신은 ___ 팀의 분석가)

**부적합**:
- 긴 reference doc (token 낭비)
- 자주 안 쓰일 context (noise)
- 자주 바뀌는 state

**예시**:
```markdown
당신은 DeepingSource 팀의 분석가로 일하고 있다.
- 응답 언어: 한국어 (특히 기술 용어는 영어 그대로)
- 분석 톤: 사실 기반, evidence tag 부착
- 프로젝트 컨벤션: `.analysis/<run-id>/`에 산출물 저장
```

### 2.2 Body inject (task instruction 사이에 삽입)

**적합**:
- 해당 step에만 필요한 context
- 도메인 hint (분석 시작 직전 주입)
- Memory의 durable pattern

**부적합**:
- 전체 conversation 유지되어야 할 정책 (→ Header)

**예시**:
```markdown
## 3. Topic 분석 단계

(아래 hint를 참고하라:)
- DeepStream 분석에서는 8.0과 9.0 사이 API 차이가 빈번한 gotcha다.
  9.0의 AI Agent 카테고리는 별도 검토 대상.

각 topic에 대해...
```

### 2.3 Reference (path만 전달, context 자체 미주입)

**적합**:
- 큰 baseline 파일 (multi-agent-template §3.2의 baseline_ref 패턴)
- 외부 docs / spec
- 변경 추적이 필요한 리소스

**장점**:
- Token 절약 (큰 파일을 매번 안 inject)
- Agent가 필요 시점에 fetch (lazy)
- 변경 추적 가능

**단점**:
- Agent가 안 읽고 hallucinate할 위험
- → **mitigation**: "파일을 읽지 못하면 즉시 abort, 분석 진행 금지" 룰 명시 (multi-agent template §3.1 C-016)

**예시**:
```markdown
## 5. Run-specific Context

다음 파일들이 disk에 있다. 분석 시작 전 반드시 읽어라.
읽지 못하면 즉시 abort:

- baseline: `.analysis/20260519-server-survey/baseline.md`
- prior decision: `.analysis/20260415-related/99_synthesis.md`
- project conventions: `./CLAUDE.md`
```

### 2.4 Memory / durable pattern reference

**적합**:
- 도메인별 best practice
- Gotcha (Anthropic Skills convention)
- 누적 학습 패턴

**부적합**:
- Run-specific 결론 (multi-agent template C-041 위반 — 새 분석을 anchoring한다)
- 검증 안 된 단편적 인상

**예시**:
```markdown
## Domain hints (durable patterns)
- 한국어 LLM 평가에서는 "한국어 품질"이 단일 metric이 아님 — 자연어/기술용어/존댓말로 분리.
- A100 40GB에서 30B-class 모델은 fp16 inference 한계가 있다. 양자화 옵션 고려 의무.
```

---

## 3. Redaction protocol (필수)

context를 prompt에 주입하기 **전**, 다음 redaction 적용:

| 유형 | 처리 |
|---|---|
| 비밀값 / 토큰 / credential | **완전 제거** — placeholder도 신중히 (실제 값 유추 단서 금지) |
| 환경 변수 | **이름만** 보존 (`DB_HOST=<redacted>` 또는 `DB_HOST 존재함`) |
| Endpoint URL | **존재 여부만** (도메인 유추 가능하면 host part도 제거) |
| 개인 식별 정보 | 동료 이름 보존 가능, 이메일/연락처/주소 제거 |
| 클라이언트 / 고객명 | 외부 보고용이면 redact, 내부 한정이면 그대로 |
| API key 형식 문자열 | 정규식 패턴 매칭 모두 제거 |

### 3.1 자동 검사 (composer Phase 5 직전)

```bash
# 흔한 secret 패턴 빠른 sanity check
grep -Eri '(AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{32}|ghp_[a-zA-Z0-9]{36}|api[_-]?key|password|secret|bearer)\s*[:=]\s*\S+' <composed_prompt>
```

1건이라도 hit → **재redact 후 재검사**, 통과 전 실행 금지.

### 3.2 Anthropic context 특수 처리

- 본 시스템 prompt 내용을 context로 주입하지 말 것 (system prompt는 user에 비공개)
- 다른 conversation의 context는 같은 user에게도 cross-injection 금지 (memory 메커니즘으로만)

---

## 4. Composed prompt 내 layout 권장

context는 다음 순서로 배치 (위→아래로 agent가 읽을 때 자연스럽게 context를 빌드):

```markdown
[1. Header — identity, language, tone, top-level constraints]
   ← Header-inject context

[2. Static project context — conventions, vocabulary]
   ← Header-inject context (수정 안 되는 것)

[3. Task spec — purpose, criteria, output format]
   ← spec에서 가져옴

[4. Activated components — from router]
   ← component 발췌

[5. Run-specific context — baseline ref, prior turn]
   ← Reference pattern (path만)

[6. Output specification — schema, length, gates]
   ← spec.B / spec.D / spec.E echo

[7. Routing log (참조용)]
```

**순서 logic**: project context 다음에 task가 와야 task가 project lens로 해석된다. 거꾸로 두면 task가 project context를 override하는 효과 발생.

---

## 5. Anti-patterns

- ❌ **가능한 모든 context를 일단 다 inject** — token cost + 무관 정보가 noise로 작용
- ❌ **민감정보를 "Claude는 안전하니까" 그대로 inject** — composed prompt가 다른 곳에 logged/exported될 수 있음
- ❌ **Memory의 run-specific 결론을 context로 inject** — 새 분석을 anchoring (multi-agent template C-021)
- ❌ **CLAUDE.md 전체를 매번 inject** — 변경 안 된 부분은 Reference로 충분
- ❌ **User preference를 자동 추론** — 명시되지 않은 선호는 안 적용. spec.D / spec.F에 적힌 것만.
- ❌ **Reference 패턴 쓰면서 "abort if unreadable" 룰 누락** — agent가 hallucinate한다
- ❌ **Header에 task-specific context** — 다른 turn에서 재사용 불가

---

## 6. Context manifest (composer가 작성)

Phase 3에서 다음 manifest를 작성 후 Phase 4 (Assembly)로 전달:

```markdown
## Context Manifest
| Source | Pattern | Redaction | Where in composed |
|---|---|---|---|
| CLAUDE.md | Header inject | No | §2 of composed |
| spec.F audience | Header inject | No | §1 |
| baseline.md | Reference | No | §5 - path only |
| env vars list | Reference | Yes (names only) | §5 |
| memory: 한국어 LLM 평가 gotcha | Body inject | No | §4.2 (해당 component 안) |
| prior PR #123 review comments | Body inject | 부분 (이메일 redact) | §3 |
```

이 manifest는 audit 가능해야 한다 — *왜* 그 context를 그 패턴으로 주입했는지 spec.E success criteria로 역추적 가능해야 함.

---

## 7. Lifecycle 노트

context는 시간이 지나면 stale된다:

- **3개월**: project conventions 재검토 (CLAUDE.md 변경 추적)
- **per-run**: run-specific context는 매번 새로 fetch
- **6개월**: memory durable pattern 재검토 (multi-agent template C-041 review cadence와 동일)

stale context를 inject하면 **silent failure** (composed prompt가 그럴듯해 보이지만 결과가 outdated)가 생긴다. composer의 Phase 5 pre-validation에서 last_modified 검증 권장.
