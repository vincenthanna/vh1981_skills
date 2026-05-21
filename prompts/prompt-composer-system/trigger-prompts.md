# Trigger Prompts — 시스템 가동용 입력

> **무엇**: optimized-prompt-composer 시스템을 실제로 돌리기 위한 entry prompt 모음. *어떻게 시동을 거는가*만 다룬다(component 라이브러리는 별도).
> **용도**: composer를 step-by-step / compose-only auto / smoke-test 중 하나로 시동하거나, 이미 만든 prompt를 실행·평가할 때 복사해 쓸 입력을 고를 때 참조.
> **시리즈 위치**: composer 진입점(entry). 라이브러리 component가 아니라 시동 입력.
>
> **Changelog**:
> - v1.2 (2026-05-19): Compose / Execute / Evaluate **세션 분리를 invariant로 격상**. mode 재정의: A-2를 compose-only auto로 변경 (default), 기존 full-auto는 A-3 smoke-test로 강등. C-6 (execute-only) 신설.
> - v1.1 (2026-05-19): 방법 A에 `auto` 모드 추가 — *deprecated*, v1.2의 A-2/A-3로 분리됨.

---

## ⚠️ System Invariant — 반드시 읽기

**Prompt 생성과 실행은 다른 conversation에서 일어나야 한다.**

이유 (셋 다 독립적으로 정당화):

1. **Self-eval bias**: 같은 LLM이 자기 출력을 채점하면 점수가 1-2점 부풀려짐. Phase 7이 Phase 1-5와 같은 세션이면 신뢰 구간 오염.
2. **Context contamination**: composed prompt는 *fresh LLM이 이것만 보고 시작*한다는 가정으로 작성됨. 같은 세션에서 자기에게 던지면 Phase 1-5 컨텍스트가 role priming을 무효화.
3. **Tool 환경 불일치**: composed prompt가 가정한 tool (web_search 등)이 composer 세션에 없으면 "검색했다 치고" 식 simulation.

같은 세션 실행은 **smoke test 외에는 신뢰하지 말 것**. CLAUDE.md "System Invariants" 참조.

---

## 3개의 세션 단위

| 세션 | 역할 | Phase | 산출물 |
|---|---|---|---|
| **Compose** | rough request → optimized prompt | 1–5 | `composed prompt` (markdown artifact) |
| **Execute** | prompt → task 결과 | 6 | task output |
| **Evaluate** | output + spec.E → 점수 | 7 | 5축 점수 + 개선 권고 |

- Compose 세션은 독립 필수
- Execute와 Evaluate는 같은 세션 가능 (Composer와 분리되어 있으면 충분)

---

## 입력 형태 선택 가이드 (v1.2)

| 상황 | 추천 방법 |
|---|---|
| 학습 / 디버깅 / 새 task pattern 첫 시도 | **A-1** step-by-step |
| **정상 사용 (default)** | **A-2** compose-only auto |
| 시스템 데모만 / 결과 신뢰 X / smoke test | **A-3** full-auto (warning) |
| 이미 만든 prompt를 실행만 | **C-6** execute-only |
| 실행 결과를 평가만 | **C-7** evaluate-only |
| 단일 phase 격리 사용 | C-1/2/3/4/5 |
| 영구 skill 등록 | 방법 B (default: A-2 동작) |

---

## 방법 A — 1회용 사용 (3가지 모드)

### 절차
1. 새 conversation 시작 (또는 Claude Code 세션)
2. 컴포넌트 파일 위치 확인:
   - claude.ai라면: 핵심 md 파일을 attach 또는 paste
   - Claude Code라면: `prompts/prompt-composer-system/` 디렉터리에서 Read tool로 읽음
3. 아래 3개 모드 중 하나 선택해서 trigger paste (default: A-2)

### A-1. Step-by-step 모드

```
너는 지금부터 optimized-prompt-composer로 동작한다.
컴포넌트 파일들을 라이브러리로 사용해 (claude.ai: 첨부 / Claude Code: prompts/prompt-composer-system/).

[Rough request]
<여기에 실제 요청>

[실행 규칙 — step-by-step]
Phase 1부터 Phase 5까지 단계별로 진행하며 각 phase 종료 시 사용자 확인 대기.

1. Phase 1 (Intake): A-E 추출 후 모호 필드만 단답형 질문 max 3개. G1 통과 후 spec 보여주고 확인 대기.
2. Phase 2 (Routing): decision tree + routing log + selected components 표시 후 확인 대기.
3. Phase 3-4 (Context + Assembly): composed prompt를 markdown 코드블록으로 출력.
4. Phase 5 (Pre-validation): P1~P7 결과 표 형태.
5. 종료. Phase 6/7은 **별도 conversation에서** C-6/C-7 trigger로 진행.

규칙:
- 각 gate 통과/실패 명시.
- Bypass 적합 케이스면 권고 후 결정 대기.
- 컴포넌트 발췌는 §-숫자 ref 명시.
```

**언제 쓰나**: 처음 시도, 작동 방식 학습 중, 각 phase 결과를 검토하며 가고 싶을 때, high-stakes task로 매 단계 통제하고 싶을 때.

### A-2. Compose-only auto 모드 (default)

```
너는 지금부터 optimized-prompt-composer로 동작한다.
컴포넌트 파일들을 라이브러리로 사용해 (claude.ai: 첨부 / Claude Code: prompts/prompt-composer-system/).

[Rough request]
<여기에 실제 요청>

[실행 모드 — compose-only auto]
Phase 1 → 5를 중간 확인 없이 논스톱으로 진행하고, **Phase 5 종료 시 composed prompt artifact를 `.specs/<task-id>.composed.md`로 저장한 뒤 최종 산출물로 출력하고 종료**.
Phase 6 (실행)과 Phase 7 (평가)은 진행하지 않음.

다음 4가지 경우에만 멈추고 사용자 입력 대기:
(a) Phase 1: A-E 필드 추출 모호 시 보강 질문 (max 3개)
(b) Gate G1~G5 실패 시: 사유 보고 후 stop
(c) Phase 2: bypass 조건 충족 시: 권고 후 결정 대기
(d) Phase 4: 외부 자료 Read 필요 시 (Claude Code 환경)

형식:
- "## Phase N — <이름>" 헤더로 각 phase 시작
- Gate 결과 한 줄: "✓ G<N> 통과" 또는 "✗ G<N> 실패: <사유>"
- 컴포넌트 발췌는 §-숫자 ref 명시
- 모든 phase를 한 응답 안에 누적

최종 산출물 (Phase 5 통과 후):
1. composed prompt를 `.specs/<task-id>.composed.md` 파일로 **반드시 저장** (Claude Code: Write 도구 / claude.ai: 저장 위치 안내). 저장 실패 시 그 사실을 명시.
2. composed prompt를 별도 markdown 코드블록으로 강조 출력
3. 다음 단계 안내: "이 prompt(`.specs/<task-id>.composed.md`)를 새 conversation에서 실행하세요. 실행 결과를 평가하려면 trigger-prompts.md C-7 사용."

⚠️ 같은 세션에서 절대 Phase 6 (composed prompt 실행)을 진행하지 말 것. self-eval bias 및 context contamination 발생.
```

**언제 쓰나**: 정상적인 production 사용. prompt artifact를 만들어 별도 세션에서 실행할 때. **이게 default 모드.**

### A-3. Full-auto 모드 (smoke test only — ⚠️ 결과 신뢰 X)

```
너는 지금부터 optimized-prompt-composer로 동작한다.
컴포넌트 파일들을 라이브러리로 사용해.

[Rough request]
<여기에 실제 요청>

[실행 모드 — full-auto (smoke test)]
⚠️ 이 모드는 시스템 전체 흐름 데모/디버깅용입니다. 같은 세션에서 Phase 6 simulation + Phase 7 self-evaluation이 일어나므로 결과 신뢰도가 떨어집니다. Production 사용 금지.

Phase 1 → 7을 중간 확인 없이 진행, 한 응답에 누적.

같은 modal stop 조건 (a)-(d) 적용. Phase 6 실행은 *같은 세션의 같은 LLM이 composed prompt를 자기에게 던지는 형태로 simulate*.

Phase 7 출력 시 반드시 다음 경고 부착:
"⚠️ self-eval 점수입니다. 실제 평가는 fresh conversation에서 C-7 trigger로 재확인 권고."

spec.G == [IRREVERSIBLE] 또는 spec.J == High이면 이 모드 자체 거부하고 A-1/A-2 권고.
```

**언제 쓰나**:
- 시스템이 작동은 하는지 한눈에 보고 싶을 때
- 새 컴포넌트 추가 후 흐름이 깨지지 않았는지 smoke test
- **production 결과로 절대 사용 금지**

### 첫 응답 신호 (3 모드 공통)

```
## Phase 1 — Intake
자동 추출 결과:
A. Purpose: ...
...
```

이 형태로 시작하지 않으면 trigger 실패. 컴포넌트 파일 attach/read 가능 상태 확인.

---

## 방법 B — Claude Code skill로 영구 설치

### 설치 (1회만)

```bash
mkdir -p .claude/skills/prompt-composer/refs

cat > .claude/skills/prompt-composer/SKILL.md << 'FRONTMATTER'
---
name: prompt-composer
description: Rough request를 받아 prompt component library에서 적절한 것들을 선택·조합하여 optimized prompt artifact를 생성한다 (실행은 별도). 동일 task의 반복 / multi-topic 평가 / 외부 보고 대상 task에서 활성화. "이 작업을 위한 prompt 만들어줘", "여러 옵션 평가하고 싶어", "task 위한 component 조합해줘", "이 분석 prompt 최적화해줘" 같은 요청에 trigger.
---

FRONTMATTER

cat optimized-prompt-composer.md >> .claude/skills/prompt-composer/SKILL.md

cp task-spec-template.md prompt-component-router.md \
   context-injection-patterns.md prompt-evaluation-rubric.md \
   multi-agent-analysis-template.md agent-role-dictionary.md \
   .claude/skills/prompt-composer/refs/

cat >> .claude/skills/prompt-composer/SKILL.md << 'EOF'

---
## Reference files location
세부 컴포넌트는 `refs/`. Phase 진행 중 룰이 필요하면 해당 파일 Read.

## Default 실행 모드 (v1.2)
별도 지시 없으면 **compose-only auto** (trigger-prompts.md A-2):
- Phase 1→5 논스톱
- Phase 5 통과 후 composed prompt artifact 출력 후 종료
- Phase 6/7은 별도 conversation에서 진행 (사용자가 C-6/C-7 trigger로)

step-by-step 강제: trigger에 "step-by-step 모드" 명시
full-auto smoke test: trigger에 "smoke test 모드, 결과 신뢰 X" 명시

⚠️ Phase 6/7을 같은 세션에서 절대 자동 실행 금지 (CLAUDE.md System Invariants).
EOF
```

### 사용 — 자연어 trigger

```
이 작업을 위한 optimized prompt 만들어줘: <요청>          # default: compose-only auto
prompt-composer 돌려서 <요청>                              # default: compose-only auto
prompt-composer로 step-by-step 진행: <요청>                # A-1 강제
prompt-composer로 smoke test (low fidelity): <요청>        # A-3 강제
```

명시적 호출:
```
.claude/skills/prompt-composer 활성화해서 <요청>
```

### Skill이 작동하는지 확인
첫 응답이 "## Phase 1 — Intake" 형태로 시작하지 않으면 skill 자동 trigger 실패. `claude` CLI에서 `/skills list`로 등록 확인.

---

## 방법 C — 단일 phase / 단일 세션 사용

### C-1. Phase 1만 — Task Spec 추출 단독

```
[task-spec-template.md attach 또는 prompts/prompt-composer-system/task-spec-template.md Read]

위 template을 사용해 아래 rough request에서 Task Spec을 추출해.

규칙:
- A-E 필수 필드 무조건 채울 것. 추출 불가하면 단답형 질문 max 3개.
- F-J 권장 필드는 추출 가능하면 채우고 안 되면 생략.
- K-L은 explicit 신호 있을 때만.
- 마지막에 self-check(§5) 결과 표시.

[Rough request]
<요청>
```

### C-2. Phase 2만 — Routing 결정 단독

```
[router + 본인 spec attach/read]

위 router로 첨부 spec에 대한 routing 결정만 수행. Phase 3 이후 진행 금지.

출력:
1. Decision tree 통과 경로
2. Selected components list (version 포함)
3. Estimated cost (full vs 발췌)
4. Bypass 적합 여부 + 사유
5. Routing log (router §4 format)
```

### C-3. Phase 3만 — context injection plan

```
[context-injection-patterns.md + spec attach/read]

위 patterns로 첨부 spec에 대한 context injection plan을 작성.

출력:
- Context source 식별 (§1 7-source taxonomy 매핑)
- Source별 injection pattern 결정 (Header/Body/Reference/Memory)
- Redaction 필요 항목 + sanity check
- 최종 context manifest (§4 format)
```

### C-4. Phase 4만 — composed prompt 조립

```
[composer.md §6 + 결정된 components + context manifest attach/read]

위 §6 layout (§1~§7)을 따라 composed prompt 조립.

규칙:
- 각 component 발췌는 §-숫자 ref로 명시
- 전체 본문 복사 금지
- 최종 prompt를 markdown 코드블록 하나로 출력
```

### C-5. Phase 5만 — 사전 검증 (Pre-validation)

```
[prompt-evaluation-rubric.md + 검증할 composed prompt attach/read]

위 rubric의 사전 P1~P7 체크리스트로 첨부 prompt 평가.

출력:
| 항목 | 통과/실패 | 사유 | Fix 권고 |
|---|---|---|---|
| P1 ... | ... | ... | ... |

P1~P5 중 하나라도 실패면 사용 금지 권고. P6~P7은 warning.
```

### C-6. Phase 6 — 실행 (Execute, NEW in v1.2)

**별도 conversation에서** composed prompt를 실행하는 entry trigger. fresh context이므로 Composer 세션과 메모리/context 분리됨.

```
[composed prompt artifact를 paste 또는 attach]

위 prompt를 실행해. 별도 메타 코멘트나 phase 헤더 없이, prompt 자체의 instruction에 따라 task 결과만 출력.

산출물은 새 conversation에서 다시 평가할 수 있도록 markdown으로 정리.
```

**규칙**:
- 이 trigger는 Composer session과 **반드시 다른 conversation**에서 사용
- 결과를 받으면 평가 위해 C-7 trigger로 또 다른 (또는 같은) conversation에서 진행
- task에 필요한 tool (web_search, Read 등)은 미리 활성화

### C-7. Phase 7 — 사후 평가 (Evaluate)

```
[prompt-evaluation-rubric.md + spec.E (Success Criteria) + 실행 결과 attach]

위 rubric §3의 5축으로 실행 결과를 평가.

출력:
- 5축 점수 (Relevance / Evidence / Reasoning / Completeness / Actionability) 각 1-5
- 가장 약한 축 식별
- §4 improvement loop의 어느 component를 수정해야 하는지 mapping
- 다음 iteration 권고 (있다면)
```

**규칙**: 이 trigger는 **반드시 Composer session과 다른 conversation**에서 사용. Execute session과 같이 써도 무방하나 fresh conversation이 더 정확.

---

## Workflow 예시 (default path)

연희 님이 일반적으로 따를 흐름:

```
[conversation 1: Compose session]
  ↓ A-2 trigger paste
  ↓ Phase 1-5 자동 진행
  ↓ artifact를 .specs/<task-id>.composed.md 로 저장 (필수)
  ↓ composed prompt artifact 출력

[conversation 2: Execute session]
  ↓ 새 conversation 시작
  ↓ C-6 trigger + artifact paste
  ↓ task 결과 출력
  ↓ 결과를 .specs/<task-id>.result.md 로 저장

[conversation 3: Evaluate session (또는 conversation 2 이어서)]
  ↓ C-7 trigger + spec.E + 결과 paste
  ↓ 5축 점수 + 개선 권고

[iteration 필요 시]
  ↓ 점수 낮은 축 → 어느 component 수정할지 결정
  ↓ component 수정 후 conversation 1부터 재실행
```

---

## 모드 선택 결정 트리 (v1.2)

```
이번 task 처음 돌리는 패턴인가?
├─ Yes → A-1 step-by-step (학습 모드)
└─ No
    └─ spec.G == [IRREVERSIBLE] 또는 spec.J == High?
        ├─ Yes → A-1 step-by-step (high-stakes 통제)
        └─ No
            └─ 시스템이 작동만 하는지 보고 싶나? (production X)
                ├─ Yes → A-3 smoke-test (warning 모드)
                └─ No → A-2 compose-only auto (DEFAULT)
                          → C-6 execute (다른 conversation)
                          → C-7 evaluate (다른 conversation)
```

---

## 흔한 실수 방지 (v1.2)

### ❌ A-3 smoke-test 결과를 production에 사용
self-eval bias로 점수가 부풀려져 있음. 진짜 결과는 A-2 + C-6 + C-7 흐름으로.

### ❌ A-2에서 composed prompt를 같은 conversation에서 실행
"실행해" 같은 follow-up message를 같은 세션에서 보내면 본질적으로 A-3 smoke-test로 전락. 새 conversation 열 것.

### ❌ Composer 세션에서 C-6 trigger 호출
fresh context invariant 위반. C-6는 **반드시 새 conversation**에서.

### ❌ Trigger 메시지에 "Phase 1부터" 명시 빠뜨림
composer가 Phase 2부터 시작하려고 할 수 있음. A-1/A-2/A-3 trigger 형식 그대로 사용.

### ❌ 컴포넌트 파일 attach/read 누락
방법 A에서 7개 중 핵심 파일 (composer, task-spec, router, context, eval) 누락 시 phase 진행 막힘. multi-agent-template / agent-role-dictionary는 분석/결정 task에서 필수.

### ❌ Rough request에 compound goal
Phase 1 G1에서 차단. trigger 전에 두 task로 분리.

### ❌ Phase 4 출력을 다시 Phase 4에 넣음
composed prompt를 받고 그대로 composer에 다시 넣는 재귀는 의미 없음. C-6로 별도 conversation에서 실행.

---

## Quick reference (v1.2)

| 시점 | 가장 짧은 trigger |
|---|---|
| Default — compose only (A-2) | "너는 optimized-prompt-composer로 동작한다. compose-only auto, Phase 1→5만 진행. Rough request: <요청>" |
| 학습/디버깅 (A-1) | "너는 optimized-prompt-composer로 동작한다. step-by-step 모드. Rough request: <요청>" |
| Smoke test (A-3) | "너는 optimized-prompt-composer로 동작한다. full-auto smoke test (low fidelity). Rough request: <요청>" |
| Claude Code skill (방법 B, default A-2) | "이 작업을 위한 optimized prompt 만들어줘: <요청>" |
| Spec만 추출 (C-1) | "위 task-spec-template으로 A-E 추출. 모호하면 질문 3개. Rough request: <요청>" |
| Composed prompt 실행 (C-6) | "위 prompt 실행. task 결과만 출력." (별도 conversation) |
| 결과 평가 (C-7) | "위 rubric으로 첨부 결과 5축 점수 매기기." (별도 conversation) |
